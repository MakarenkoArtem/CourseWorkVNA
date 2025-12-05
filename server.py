import asyncio
import datetime
import os
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
from threading import Thread

from flask import Flask, request, jsonify, send_from_directory, render_template, redirect
from flask_cors import CORS
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from werkzeug.security import check_password_hash

import emulator
import processing
from SettingsModel import SettingsModel
from data import db_session
from data.settings import Setting
from data.users import User
from forms.measure import MeasureForm
from forms.user import RegisterForm, EntryForm

activeSession = {}
SETTINGS = SettingsModel()
events = Queue()
app = Flask(
    __name__,
    # template_folder="react-app",  # Jinja2 HTML
    # static_folder=None  # Статику подключаем вручную ниже
)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "key")  # нужен для CSRF и сессий
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(days=1)
login_manager = LoginManager()
login_manager.init_app(app)
# задаёт страницу, на которую перенаправит неавторизованных пользователей при срабатывании @login_required
login_manager.login_view = '/'

CORS(app)  # как allow_origins=["*"] в FastAPI


# Static mounts (как app.mount в FastAPI)
@app.route('/lib/<path:path>')
def send_lib(path):
    return send_from_directory('static/lib', path)


# ------------------------  TEMPLATES  ---------------------------
@app.route("/main")
@app.route("/main/<int:id>")
def home(idMeasure=None):
    name = ''
    try:
        id = current_user.id
        name = current_user.email
    except AttributeError:
        id = 0
    return render_template("mainPage.html", id=id, name=name, idMeasure=idMeasure)


def fillSettingsForm(form, settings):
    if settings is not None:
        form.freq_start_mhz.data = settings.freq_start_mhz
        form.freq_stop_mhz.data = settings.freq_stop_mhz
        form.num_freq_points.data = settings.num_freq_points
        form.rbw_khz.data = settings.rbw_khz
        form.output_power_dbm.data = settings.output_power_dbm
        form.txtr.data = settings.txtr
        form.mode.data = settings.mode
    return form


def to_Settings(form, settings):
    settings.freq_start_mhz = form.freq_start_mhz.data
    settings.freq_stop_mhz = form.freq_stop_mhz.data
    settings.num_freq_points = form.num_freq_points.data
    settings.rbw_khz = form.rbw_khz.data
    settings.output_power_dbm = form.output_power_dbm.data
    settings.txtr = int(form.txtr.data)
    settings.mode = int(form.mode.data)
    return settings


background_loop = asyncio.new_event_loop()


def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


t = Thread(target=start_background_loop, args=(background_loop,), daemon=True)
t.start()


@app.route("/settings", methods=['GET', 'POST'])
@login_required
def settings():  # форма для регистрации
    if cur_user().get_json()['remainingTime'] == -1:  # устройство занято другим пользователем
        redirect("/main")
    global activeSession, executor, SETTINGS
    activeSession = {'user': current_user.id, 'time': datetime.datetime.now() + datetime.timedelta(minutes=5)}
    form = MeasureForm()
    db_sess = db_session.create_session()
    settings = db_sess.query(Setting).filter(Setting.author_id == current_user.id).first()
    if settings is None:
        settings = Setting(author_id=current_user.id)
        db_sess.add(settings)
    if form.validate_on_submit():
        newSettings = SettingsModel().fromForm(form)
        db_sess.commit()
        if 'measure' in request.form:
            if activeSession['user'] == current_user.id:
                SETTINGS = newSettings
                print(SETTINGS.__dict__)
                background_loop.call_soon_threadsafe(
                    asyncio.create_task, newData(emulator.generate_vna_data, emulator.RecordingSettings(
                        freq_range=emulator.FrequencyRange(SETTINGS.freq_start_mhz, SETTINGS.freq_stop_mhz,
                                                           SETTINGS.num_freq_points),
                        rbw_khz=SETTINGS.rbw_khz, output_power_dbm=SETTINGS.output_power_dbm, txtr=SETTINGS.txtr,
                        mode=SETTINGS.mode)))
                db_sess.close()
            return redirect(f'/main')
        elif 'calibrate' in request.form:
            # vnakit.calibrate(settings)
            pass
    db_sess.close()
    fillSettingsForm(form, settings)
    return render_template('settingsPage.html', form=form, name=current_user.email, id=current_user.id)


DATA = None

async def newData(func, *args):
    global DATA, activeSession
    while activeSession != {}:
        DATA = processing.get_uncalibrated_s(func(*args))
        DATA.S11 = list(map(abs, DATA.S11))
        DATA.S12 = list(map(abs, DATA.S12))
        DATA.S21 = list(map(abs, DATA.S21))
        DATA.S22 = list(map(abs, DATA.S22))
        print("!!!!", DATA.__dict__)


# ------------------------  API LOGIC  ---------------------------
@app.get("/api/get_data")
def get_data():
    global DATA
    if DATA is None:
        return {}
    return jsonify(DATA.__dict__)


@app.get("/api/time_user")
def cur_user():
    global activeSession
    if activeSession == {} or current_user is None:
        return jsonify({"remainingTime": 0})  # если remainingTime 0 устройство свободно, если -1 у другого пользователя
    delta = (activeSession['time'] - datetime.datetime.now()).total_seconds() // 60
    if delta < 0:
        activeSession = {}
        return jsonify({"remainingTime": 0})
    if activeSession['user'] != current_user.id:
        return jsonify({"remainingTime": -1})
    return jsonify({"remainingTime": delta})


@app.get("/api/settings")
def get_settings():
    global SETTINGS
    return SETTINGS.toJSON()


@app.get("/api/userSettings")
def get_user_settings():
    return jsonify({"status": "not implemented"})


@app.get("/api/currentSettings")
def current_settings():
    # TODO — вернуть настройки векторника
    return jsonify({"status": "not implemented"})


@app.get("/api/activeUser")
def active_user():
    # TODO — вернуть активного пользователя
    return jsonify({"userId": -1, "nameUser": None})


@app.get("/api/websocket")
def websocket_info():
    return jsonify({"host": "127.0.0.1", "port": 8765, "protocol": "websocket"})


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():  # форма для регистрации
    form = RegisterForm()
    if form.validate_on_submit():
        if not form.passIsCorrect():
            return render_template('register.html', form=form, message="Пароли не совпадают", id=0)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', form=form, message="Такой пользователь уже есть", id=0)
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db_sess.add(user)
        curUser = db_sess.query(User).filter(
            User.email == form.email.data and check_password_hash(User.hashed_password, form.password.data)).first()
        if curUser is not None:
            login_user(curUser, remember=True)
        db_sess.commit()
        db_sess.close()
        return redirect('/main')
    return render_template('register.html', title='Регистрация', form=form, id=0)


@app.route('/')
def choice():  # выбор входа или регистрации
    return render_template("choice.html")


@app.route('/login', methods=['GET', 'POST'])
def login():  # форма для входа
    form = EntryForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        curUser = db_sess.query(User).filter(
            User.email == form.email.data and check_password_hash(User.hashed_password, form.password.data)).first()
        if curUser is None:
            db_sess.close()
            return render_template('login.html', form=form, message="Такой пользователь не найден")
        login_user(curUser, remember=True)
        db_sess.close()
        return redirect('/main')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    global activeSession
    if activeSession.get('user', None) == current_user.id:
        activeSession = {}
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/VNAData.db")
    app.run(host="0.0.0.0", port=8000, debug=True, use_reloader=False)


if __name__ == "__main__":
    main()
