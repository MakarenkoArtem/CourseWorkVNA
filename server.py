import datetime
import os
from queue import Queue

from flask import Flask, request, jsonify, send_from_directory, render_template, redirect
from flask_cors import CORS
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from werkzeug.security import check_password_hash

from data import db_session
from data.settings import Setting
from data.users import User
from forms.measure import MeasureForm
from forms.user import RegisterForm, EntryForm
import emulator

activeSession = None
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
@app.route('/src/<path:path>')
def send_src(path):
    return send_from_directory('react-app/src', path)


@app.route('/lib/<path:path>')
def send_lib(path):
    return send_from_directory('react-app/lib', path)


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
        form.minFreq.data = settings.freq_start_mhz
        form.maxFreq.data = settings.freq_stop_mhz
        form.pointCnt.data = settings.num_freq_points
        form.rbw.data = settings.rbw_khz
        form.dbm.data = settings.output_power_dbm
        form.txtr.data = settings.txtr
        form.mode.data = settings.mode
    return form


@app.route("/settings", methods=['GET', 'POST'])
@login_required
def settings():  # форма для регистрации
    if cur_user().get_json()['remainingTime']==-1:
        redirect("/main")
    form = MeasureForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        settings = db_sess.query(Setting).filter(Setting.author_id == current_user.id).first()
        if settings is None:
            settings = Setting(author_id=current_user.id)
            db_sess.add(settings)
        settings.freq_start_mhz = form.minFreq.data
        settings.freq_stop_mhz = form.maxFreq.data
        settings.num_freq_points = form.pointCnt.data
        settings.rbw_khz = form.rbw.data
        settings.output_power_dbm = form.dbm.data
        settings.txtr = int(form.txtr.data)
        settings.mode = int(form.mode.data)
        db_sess.commit()

        if 'measure' in request.form:
            global activeSession
            if activeSession is None:
                events.put(
                    {"event":"settings", "id": settings.id, "minFrequency": settings.freq_start_mhz, "maxFrequency": settings.freq_stop_mhz,
                     "countPoints": settings.num_freq_points})

                events.put({"event":"getData",'func': emulator.generate_vna_data, 'data': emulator.RecordingSettings(
                    freq_range=emulator.FrequencyRange(settings.freq_start_mhz, settings.freq_stop_mhz,
                                                       settings.num_freq_points),
                    rbw_khz=settings.rbw_khz, output_power_dbm=settings.output_power_dbm, txtr=settings.txtr,
                    mode=settings.mode
                )})
                activeSession = {'id': current_user.id,
                                 'time': datetime.datetime.now() + datetime.timedelta(minutes=5)}
            return redirect(f'/main')
        elif 'calibrate' in request.form:
            # vnakit.calibrate(settings)
            pass

    db_sess = db_session.create_session()
    settings = db_sess.query(Setting).filter(Setting.author_id == current_user.id).first()
    fillSettingsForm(form, settings)
    return render_template('settingsPage.html', title='Регистрация', form=form, name=current_user.email,
                           id=current_user.id)


# ------------------------  API LOGIC  ---------------------------




@app.get("/api/time_user")
def cur_user():
    global activeSession
    print("/api/time_user", activeSession)
    if activeSession is None or current_user is None:
        return jsonify({"remainingTime": 0}) #если remainingTime 0 устройство свободно, если -1 у другого пользователя
    delta = (activeSession['time'] - datetime.datetime.now()).total_seconds() // 60
    if delta < 0:
        activeSession = None
        return jsonify({"remainingTime": 0})
    if activeSession['id'] != current_user.id:
        return jsonify({"remainingTime": -1})
    return jsonify({"remainingTime": delta})


@app.get("/api/userSettings/<int:id>")
def get_user_settings(id):
    # TODO — вернуть настройки пользователя
    return jsonify({"status": "not implemented"})


@app.put("/api/userSettings/<int:id>")
def update_user_settings(id):
    data = request.get_json()  # аналог request.json() в FastAPI
    # TODO — обновить настройки пользователя
    return jsonify({"status": "not implemented", "received": data})


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
@login_required
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
        db_sess.commit()
        login_user(user, remember=True)
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form, id=0)


@app.route('/')
def choice():  # выбор входа или регистрации
    return render_template("choice.html")


@app.route('/entry', methods=['GET', 'POST'])
def entry():  # форма для входа
    form = EntryForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        curUser = None
        for user in db_sess.query(User).all():
            if user.email == form.email.data and check_password_hash(user.hashed_password, form.password.data):
                curUser = user
                break
        if curUser is None:
            return render_template('entry.html', form=form, message="Такой пользователь не найден")
        login_user(curUser, remember=True)
        return redirect('/main')
    return render_template('entry.html', form=form)


@app.route('/logout')
@login_required
def logout():
    global activeSession
    if activeSession is not None and activeSession['id'] == current_user.id:
        activeSession = None
    logout_user()
    return redirect("/")


def main():
    db_session.global_init("db/VNAData.db")
    app.run(host="0.0.0.0", port=8000, debug=True, use_reloader=False)


if __name__ == "__main__":
    main()
