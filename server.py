from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import psutil
import socket
import time
from fastapi.middleware.cors import CORSMiddleware


def get_local_ip():
    # создаём UDP-сокет и "подключаемся" к внешнему адресу
    # (фактически соединения не будет, нужно только чтобы ОС выбрала интерфейс)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 8.8.8.8 — это Google DNS, можно указать любой внешний IP
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

print("Мой локальный IP:", get_local_ip())

app = FastAPI()

# Разрешаем запросы с любых источников
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # или ["http://localhost:5173"] для конкретного фронтенда
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
templates = Jinja2Templates(directory="react-app")
app.mount("/react-app", StaticFiles(directory="react-app"), name="react-app")
app.mount("/react-app/lib", StaticFiles(directory="react-app/lib"), name="lib")

'''
@app.get("/api/time")
def read_root():
    return {"value":time.time()%60}

@app.get("/api/cpu")
def read_root():
    return {"value": psutil.cpu_percent(interval=1)}
'''
@app.get("/settings", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("settingsPage.html", {"request": request})

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("mainPage.html", {"request": request})
    return FileResponse("react-app/mainPage.html",
                        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        })

@app.get("/api/websocket")
def read_root():
    return {"host": "127.0.0.1", "port": 8765, "protocol":"websocket"}

#uvicorn server:app --port 8000