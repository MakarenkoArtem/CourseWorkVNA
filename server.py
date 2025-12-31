import logging
import os
import subprocess
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, jsonify, send_from_directory, render_template, redirect
from flask_cors import CORS
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from werkzeug.security import check_password_hash

from SettingsModel import *
from VNAWorker import VNAWorker
from data import db_session
from data.settings import Setting
from data.users import User
from driver.build.vnakit_py import *
from forms.measure import MeasureForm
from forms.user import RegisterForm, EntryForm


def check_active_user(func):
    """
    Декоратор: разрешает вызов если
      - activeSession пустой (устройство свободно), или
      - activeSession['user'] == current_user.id
    Иначе возвращает {"error": "..."} с кодом 403.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        global activeSession

        # если пользователь не авторизован — 401
        if current_user.is_anonymous:
            return jsonify({"error": "unauthenticated"}), 401

        # Если activeSession пустой/None — устройство свободно -> разрешаем
        if not activeSession:
            return func(*args, **kwargs)

        try:
            session_user = int(activeSession.get("user"))
        except Exception:
            return jsonify({"error": "invalid activeSession format"}), 500

        if session_user == int(current_user.id):
            return func(*args, **kwargs)
        return jsonify({
            "error": "device_in_use",
            "message": "Устройство сейчас используется другим пользователем",
            "userId": session_user
        }), 403

    return wrapper


SETTINGS = SettingsModel()
VNA_WORKER = VNAWorker()
VNA_WORKER.init(SETTINGS.toRecordingSettings())
CalibrationVNA = VNACalibration()
DATA = Smatrixs()
DATA.frequency = []
DATA.S11 = []
DATA.S12 = []
DATA.S21 = []
DATA.S22 = []
activeSession = {}

app = Flask(__name__, )
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "key")  # нужен для CSRF и сессий
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=1)
login_manager = LoginManager()
login_manager.init_app(app)
# задаёт страницу, на которую перенаправит неавторизованных пользователей при срабатывании @login_required
login_manager.login_view = '/'

CORS(app)  # как allow_origins=["*"] в FastAPI


@app.route('/lib/<path:path>')
def send_lib(path):
    return send_from_directory('static/lib', path)


@app.errorhandler(500)
def not_found(error):
    try:
        id = current_user.id
    except AttributeError:
        id = 0
    return render_template("500.html", id=id)


@app.errorhandler(404)
def not_found(error):
    try:
        id = current_user.id
    except AttributeError:
        id = 0
    return render_template("404.html", id=id)


# ------------------------  TEMPLATES  ---------------------------
@app.route("/main")
@app.route("/main/<int:id>")
def home(idMeasure=None):
    try:
        id, name = current_user.id, current_user.email
    except AttributeError:
        id, name = 0, ''
    return render_template("mainPage.html", id=id, name=name, idMeasure=idMeasure, dualPort=SETTINGS.mode)


def updateSettingsDb(settingsMdl):
    res = False
    db_sess = db_session.create_session()
    settingsDB = db_sess.query(Setting).filter(Setting.author_id == settingsMdl.author_id).first()
    if settingsDB is not None:
        settingsMdl.toDB(settingsDB)
        db_sess.commit()
        res = True
    db_sess.close()
    return res


def getSettingsMdlFromDB(author_id):
    db_sess = db_session.create_session()
    settingsDB = db_sess.query(Setting).filter(Setting.author_id == author_id).first()
    if settingsDB is None:
        settingsDB = SettingsModel(author_id=current_user.id).toDB(Setting())
        db_sess.add(settingsDB)
        db_sess.commit()
    settingsMdl = SettingsModel().fromDB(settingsDB)
    db_sess.close()
    return settingsMdl


@app.route("/settings", methods=['GET', 'POST'])
@login_required
def settings():  # форма для регистрации
    if cur_user().get_json()['remainingTime'] == -1:  # устройство занято другим пользователем
        return redirect("/main")
    global activeSession, SETTINGS, DATA
    form = MeasureForm()
    settingsMdl = getSettingsMdlFromDB(current_user.id)
    if form.validate_on_submit():
        activeSession = {'user': current_user.id, 'time': datetime.now() + timedelta(minutes=form.delay.data)}
        SETTINGS.author_id = current_user.id
        if SETTINGS.mode != int(form.mode.data) or SETTINGS.txtr != int(form.txtr.data):
            VNA_WORKER.decalibrate()
            SETTINGS.decalibrated()
        SETTINGS.fromForm(form)
        updateSettingsDb(SETTINGS)
        VNA_WORKER.setSettings(SETTINGS.toRecordingSettings())
        VNA_WORKER.getResult(DATA, seconds=form.delay.data * 60)
        return redirect(f'/main')
    settingsMdl.toForm(form)
    return render_template('settingsPage.html', form=form, name=current_user.email, id=current_user.id,
                           dualPort=SETTINGS.mode)


# ------------------------  API LOGIC  ---------------------------
@app.get("/api/get_data")
def get_data():
    global DATA
    if DATA is None:
        return {}
    return jsonify({
        "frequency": DATA.frequency,
        "S11": [abs(x) for x in DATA.S11],
        "S12": [abs(x) for x in DATA.S12],
        "S21": [abs(x) for x in DATA.S21],
        "S22": [abs(x) for x in DATA.S22],
    })


@app.get("/api/time_user")
def cur_user():
    global activeSession
    if activeSession == {} or current_user.is_anonymous:
        return jsonify({"remainingTime": 0})
    delta = ((activeSession['time'] - datetime.now()).total_seconds() + 59) // 60
    if delta < 0:
        activeSession = {}
        return jsonify({"remainingTime": 0})
    if activeSession['user'] != current_user.id:
        return jsonify({"remainingTime": -1})
    return jsonify({"remainingTime": delta})


@app.get("/api/settings")
def get_settings():
    global SETTINGS
    return jsonify(SETTINGS.toDict())


def calibration(DeviceVNA, data):
    newData = DeviceVNA.get_result()
    data.frequency = newData.frequency
    data.a0 = newData.a0
    data.b0_3 = newData.b0_3
    data.b3_3 = newData.b3_3
    data.a3 = newData.a3
    data.b0_6 = newData.b0_6
    data.b3_6 = newData.b3_6
    return 1


def setHH(value):
    SETTINGS.calib_HH = value


@app.get("/HH")
@check_active_user
def calib_HH():
    SETTINGS.calib_HH = CALIBRATING
    VNA_WORKER.takeHH(setHH)
    if SETTINGS.mode == 0:
        VNA_WORKER.onePortCalibration()
    else:
        VNA_WORKER.dualPortCalibration()
    return jsonify('In process')


def setKZ(value):
    SETTINGS.calib_KZ = value


@app.get("/KZ")
@check_active_user
def calib_KZ():
    SETTINGS.calib_KZ = CALIBRATING
    VNA_WORKER.takeKZ(setKZ)
    if SETTINGS.mode == 0:
        VNA_WORKER.onePortCalibration()
    else:
        VNA_WORKER.dualPortCalibration()
    return jsonify('In process')


def setMatch(value):
    SETTINGS.calib_Match = value


@app.get("/Match")
@check_active_user
def calib_Match():
    SETTINGS.calib_Match = CALIBRATING
    VNA_WORKER.takeMatch(setMatch)
    if SETTINGS.mode == 0:
        VNA_WORKER.onePortCalibration()
    else:
        VNA_WORKER.dualPortCalibration()
    return jsonify('In process')


def setMatchDual(value):
    SETTINGS.calib_Match_Dual = value


@app.get("/MatchDual")
@check_active_user
def calib_Match_Dual():
    SETTINGS.calib_Match_Dual = CALIBRATING
    if SETTINGS.mode == 0:
        return jsonify('Set one port calibration')
    VNA_WORKER.takeMatch(setMatchDual)
    VNA_WORKER.dualPortCalibration()
    return jsonify('In process')


def setBolt(value):
    SETTINGS.calib_Bolt = value


@app.get("/Bolt")
@check_active_user
def calib_Bolt():
    if SETTINGS.mode == 0:
        return jsonify('Set one port calibration')
    VNA_WORKER.takeBolt(setBolt)
    VNA_WORKER.dualPortCalibration()
    return jsonify('In process')


@app.get("/deactivate")
@check_active_user
def deactivate():
    global activeSession
    activeSession = {}
    return jsonify({'data': 'OK'})


@app.get("/decalibrate")
@check_active_user
def decalibrate():
    VNA_WORKER.decalibrate()
    SETTINGS.calib_KZ = UNCALIBRATED
    SETTINGS.calib_HH = UNCALIBRATED
    SETTINGS.calib_Match = UNCALIBRATED
    SETTINGS.calib_Bolt = UNCALIBRATED
    SETTINGS.calib_Match_Dual = UNCALIBRATED
    return jsonify({'data': 'OK'})


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():  # форма для регистрации
    if current_user.is_authenticated:  # переадресация авторизованных пользователей
        return redirect("/main")
    form = RegisterForm()
    if form.validate_on_submit():
        if not form.passIsCorrect():
            return render_template('register.html', form=form, message="Пароли не совпадают", id=-247)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first() is not None:
            db_sess.close()
            return render_template('register.html', form=form, message="Такой пользователь уже есть", id=-247)
        db_sess.add(User(email=form.email.data).set_password(form.password.data))
        curUser = db_sess.query(User).filter(
            User.email == form.email.data and check_password_hash(User.hashed_password, form.password.data)).first()
        if curUser is not None:
            login_user(curUser, remember=True)
        db_sess.commit()
        db_sess.close()
        return redirect('/main')
    return render_template('register.html', title='Регистрация', form=form, id=-247)


@app.route('/')
def choice():  # выбор входа или регистрации
    if current_user.is_authenticated:  # устройство занято другим пользователем
        return redirect("/main")
    return render_template("choice.html", id=-247)


@app.route('/login', methods=['GET', 'POST'])
def login():  # форма для входа
    if current_user.is_authenticated:  # устройство занято другим пользователем
        return redirect("/main")
    form = EntryForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        curUser = db_sess.query(User).filter(
            User.email == form.email.data and check_password_hash(User.hashed_password, form.password.data)).first()
        if curUser is None:
            db_sess.close()
            return render_template('login.html', form=form, message="Такой пользователь не найден", id=-247)
        login_user(curUser, remember=True)
        db_sess.close()
        return redirect('/main')
    return render_template('login.html', form=form, id=-247)


@app.route('/logout')
@login_required
def logout():
    global activeSession
    if activeSession.get('user', None) == current_user.id:
        activeSession = {}
    logout_user()
    return redirect("/")


def main():
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.WARNING)
    port = 8000
    result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
    print("IP адреса:", *[f'\nhttp://{i}:{port}' for i in result.stdout.strip().split()])
    db_session.global_init("db/VNAData.db")
    VNA_WORKER.run()
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)


if __name__ == "__main__":
    main()
