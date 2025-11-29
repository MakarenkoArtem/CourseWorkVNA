import asyncio
import json
from queue import Queue
from emulator import VNAData
import websockets
import psutil
import struct


class Smatrixs:
    def __init__(self, N):
        self.frequency = [0.0] * N
        self.S11 = [0.0] * N
        self.S12 = [0.0] * N
        self.S21 = [0.0] * N
        self.S22 = [0.0] * N


def get_uncalibrated_s(data: VNAData) -> Smatrixs:
    N = len(data.frequency)
    res = Smatrixs(N)

    for i in range(N):
        # Check for division by zero
        if abs(data.a0[i]) < 1e-15:
            print(f"Warning: a0[{i}] is close to zero! freq = {data.frequency[i]}")
            res.S11[i] = 0.0
            res.S21[i] = 0.0
        else:
            res.S11[i] = data.b0_3[i] / data.a0[i]
            res.S21[i] = data.b3_3[i] / data.a0[i]

        if abs(data.a3[i]) < 1e-15:
            print(f"Warning: a3[{i}] is close to zero! freq = {data.frequency[i]}")
            res.S12[i] = 0.0
            res.S22[i] = 0.0
        else:
            res.S12[i] = data.b0_6[i] / data.a3[i]
            res.S22[i] = data.b3_6[i] / data.a3[i]

    return res


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
    global dataCpu, settings
    loop = asyncio.get_running_loop()  # Получаем текущий цикл событий
    while True:
        if not events.empty():
            event = events.get()
            print(event)
            match event.get('event', None):
                case 'settings':
                    delta = event['countPoints'] - settings['countPoints']
                    if delta > 0:
                        dataCpu = [0] * 4 * delta + dataCpu
                    elif delta < 0:
                        dataCpu = dataCpu[:-delta + 4]
                    settings = {key: value for key, value in event.items() if key != 'event'}
                case 'getData':
                    func = event['func']
                    data = event['data']
                    result = await loop.run_in_executor(None, func, data)
                    data = get_uncalibrated_s(result)
                    print("!!!!", result)
                    print(data)
                    dataCpu = [abs(value) for values in zip(data.S11, data.S12, data.S21, data.S22) for value in values]
                    print(dataCpu)
        '''dataCpu[:-4] = dataCpu[4:]
        updateList = [0] * 4
        for i in range(4):
            updateList[i] = psutil.cpu_percent(interval=0.005)
            await asyncio.sleep(0)  # отдаём управление циклу событий
        dataCpu[-4:] = updateList'''
        await asyncio.sleep(0)  # отдаём управление циклу событий


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
