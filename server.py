from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS

app = Flask(
    __name__,
    template_folder="react-app",  # Jinja2 HTML
    static_folder=None  # Статику подключаем вручную ниже
)

CORS(app)  # как allow_origins=["*"] в FastAPI


# Static mounts (как app.mount в FastAPI)
@app.route('/src/<path:path>')
def send_src(path):
    return send_from_directory('react-app/src', path)


@app.route('/lib/<path:path>')
def send_lib(path):
    return send_from_directory('react-app/lib', path)


# ------------------------  TEMPLATES  ---------------------------

@app.route("/")
def home():
    return render_template("mainPage.html")


@app.route("/settings")
def settings():
    return render_template("settingsPage.html")


# ------------------------  API LOGIC  ---------------------------

CURRENT_USER = 5
remaining_time = 150


@app.get("/api/time_user/<int:id>")
def cur_user(id):
    if id == CURRENT_USER:
        return jsonify({"remainingTime": remaining_time})
    return jsonify({"remainingTime": -1})


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


# ------------------------  ENTRY POINT  --------------------------

if __name__ == "__main__":
    host = "0.0.0.0"
    print("Мой локальный IP:", host)
    app.run(host, port=8000, debug=True)
