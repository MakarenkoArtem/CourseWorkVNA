import asyncio
import json
from queue import Queue

import websockets
import psutil
import struct

settings = {"id": 0, "minFrequency": 0, "maxFrequency": 200, "countPoints": 201}
dataCpu = [0] * settings["countPoints"] * 4


async def unknownPath(websocket):
    await websocket.send("Exist variables: " + ", ".join(data.keys()))


async def cpuData(websocket, message=None):
    data = struct.pack("i", 200)
    for i in dataCpu:
        data += struct.pack("f", i)
    await websocket.send(data)


async def sendSettings(websocket, message=None):
    await websocket.send(json.dumps(settings))


async def setSettings(websocket, message=None):
    global settings
    data = json.loads(message)
    print(data)
    for key in data.keys():
        if key in settings and type(settings[key]) == type(data[key]):
            settings[key] = data[key]
    await sendSettings(websocket)


async def sData(websocket, message=None):
    data = struct.pack("i", settings['id'])
    for i in dataCpu:
        data += struct.pack("f", i)
    await websocket.send(data)


data = {"cpu": cpuData, "S": sData, "settings": sendSettings, "setSettings": setSettings}


# Обработчик соединения
async def echo(websocket):
    try:
        async for message in websocket:
            cmd, *args = message.split(maxsplit=1)
            if cmd in data:
                print(f"Получено(команда): {message}")
                payload = args[0] if args else ""
                await data[cmd](websocket, payload)
            else:
                print(f"Получено(не команда): {message}")
                await unknownPath(websocket)
    except websockets.exceptions.ConnectionClosedError:
        print('Close')


async def cycle(events: Queue):
    global dataCpu
    loop = asyncio.get_running_loop()  # Получаем текущий цикл событий
    while True:
        if not events.empty():
            print("??????????")
            event = events.get()
            func = event['func']
            data = event['data']
            result = await loop.run_in_executor(None, func, data)
            print("!!!!", result)
        dataCpu[:-4] = dataCpu[4:]
        updateList = [0] * 4
        for i in range(4):
            updateList[i] = psutil.cpu_percent(interval=0.005)
            await asyncio.sleep(0)  # отдаём управление циклу событий
        dataCpu[-4:] = updateList


# Запуск сервера на localhost:8765
async def server(events):
    async with websockets.serve(echo, "localhost", 8765):
        print("Сервер запущен на ws://localhost:8765")
        # Запускаем обе задачи параллельно
        await asyncio.gather(
            cycle(events),
            asyncio.Future(),  # чтобы сервер не завершился
        )


def main(events: Queue):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(server(events))


if __name__ == "__main__":
    main(Queue())
# python3 serverWS.py
