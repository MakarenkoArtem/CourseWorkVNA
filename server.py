from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import psutil
import socket
import time

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
templates = Jinja2Templates(directory=".")
app.mount("/js", StaticFiles(directory="js"), name="js")

@app.get("/api/time")
def read_root():
    return {"value":time.time()%60}

@app.get("/api/cpu")
def read_root():
    return {"value": psutil.cpu_percent(interval=1)}

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

