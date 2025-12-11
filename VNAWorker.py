from datetime import datetime, timedelta
from threading import Thread
from time import sleep
from VNAEvent import VNAEvent

DEBUG = False
if DEBUG:
    print("ЗАПУЩЕН ЭМУЛЯТОР ВЕКТОРНИКА")
    from driver.build.vnakit_py import VNACalibration, RecordingSettings, VNAData, Smatrixs
    from emulator import VNAKitDevice
else:
    from driver.build.vnakit_py import *

OK = 0
UNCALIBRATED = 0
ONE_PORT = 1
DUAL_PORT = 2
CalibrationVNA = VNACalibration()
GETTING_DATA = 0
CALIBRATION = 5
MEASURE_FOR_CALIBRATION = 6
DEVICE_SETTINGS = 10


def eventLoop(worker):
    while worker.status:
        worker.events.sort(reverse=True)
        if worker.curEvent.inProcess():
            if len(worker.events) and worker.events[0].priority > worker.curEvent.priority:
                worker.events.append(worker.curEvent)
                worker.curEvent = worker.events.pop(0)
                print("Берем более приоритетную задачу:", worker.curEvent.title)
                print("Задачи в очереди:", ", ".join([i.title for i in worker.events]))
            worker.curEvent.func()
        else:
            if len(worker.events):
                worker.curEvent = worker.events.pop(0)
                print("Берем задачу:", worker.curEvent.title)
                print("Задачи в очереди:", ", ".join([i.title for i in worker.events]))
            else:
                sleep(0.5)
    worker.status = 1


class VNAWorker:
    def __init__(self):
        self.isInit = False
        self.thread = None
        self.status = 1
        self.calibration = UNCALIBRATED
        self.DeviceVNA = None
        self.CalibrationVNA = VNACalibration()
        self.events = []
        self.curEvent = VNAEvent(int, priority=-1, title="Заглушка")
        self.MATCH, self.KZ, self.HH, self.BOLT = None, None, None, None
        self.settings = RecordingSettings()

    def init(self, settings: RecordingSettings):
        self.settings = settings
        self.DeviceVNA = VNAKitDevice(config_path="driver/vnakit.conf")
        self.DeviceVNA.init()
        self.setSettings(settings)

    def __setSettingsTask(self, settings: RecordingSettings):
        self.DeviceVNA.set_settings(settings)
        self.DeviceVNA.apply_settings()
        self.isInit = True
        self.settings = settings

    def setSettings(self, settings: RecordingSettings):
        self.events.append(VNAEvent(lambda: self.__setSettingsTask(settings), priority=DEVICE_SETTINGS, repeat=1,
                                    title="Установка настроек"))

    def __getResultTask(self, DATA):
        measurData = self.DeviceVNA.get_result()
        sMatr = Smatrixs()
        #TODO проверить калибровки
        self.CalibrationVNA.load_measurement_data(measurData)
        self.CalibrationVNA.calculate_uncalibrated_s()
        if self.calibration == UNCALIBRATED:
            self.CalibrationVNA.get_uncalibrated_s(measurData, sMatr)
        elif self.calibration == ONE_PORT:
            #TODO проверить калибровки
            if self.settings.txtr == 3:
                self.CalibrationVNA.apply_port_one_err()
            else:
                self.CalibrationVNA.apply_port_two_err()
            self.CalibrationVNA.write_calibrated_s("onePort.csv")
            sMatr = self.CalibrationVNA.get_calibrated_s()
        elif self.calibration == DUAL_PORT:
            #TODO проверить калибровки
            self.CalibrationVNA.apply_12term_errors()
            self.CalibrationVNA.write_calibrated_s("dualPort.csv")
            sMatr = self.CalibrationVNA.get_calibrated_s()
        DATA.frequency = sMatr.frequency
        DATA.S11 = list(map(abs, sMatr.S11))
        DATA.S12 = list(map(abs, sMatr.S12))
        DATA.S21 = list(map(abs, sMatr.S21))
        DATA.S22 = list(map(abs, sMatr.S22))

    def getResult(self, DATA: VNAData, seconds=300):
        self.stopGettingMeasurment()
        self.events.append(VNAEvent(lambda: self.__getResultTask(DATA), priority=GETTING_DATA,
                                    timeEnd=datetime.now() + timedelta(seconds=seconds), title="Получение значений"))

    def stopGettingMeasurment(self):
        if self.curEvent is not None and self.curEvent.priority == GETTING_DATA:
            self.curEvent.timeEnd = datetime.now()
            self.curEvent.repeat = 0
        self.events = [event for event in self.events if event.priority != GETTING_DATA]
        return True

    def __getCalibrationTask(self, setData, setVal):
        setData(self.DeviceVNA.get_result())
        setVal(OK)
        return 1

    def setHH(self, data):
        self.HH = data

    def setKZ(self, data):
        self.KZ = data

    def setMatch(self, data):
        self.MATCH = data

    def setBolt(self, data):
        self.BOLT = data

    def takeHH(self, setVal):  # передаем в списке переменную которую поменять в результате
        self.events.append(
            VNAEvent(func=lambda: self.__getCalibrationTask(self.setHH, setVal), repeat=1,
                     priority=MEASURE_FOR_CALIBRATION, title="Измерение ХХ"))

    def takeKZ(self, setVal):  # передаем в списке переменную которую поменять в результате
        self.events.append(
            VNAEvent(func=lambda: self.__getCalibrationTask(self.setKZ, setVal), repeat=1,
                     priority=MEASURE_FOR_CALIBRATION, title="Измерение  КЗ"))

    def takeMatch(self, setVal):  # передаем в списке переменную которую поменять в результате
        self.events.append(
            VNAEvent(func=lambda: self.__getCalibrationTask(self.setMatch, setVal), repeat=1,
                     priority=MEASURE_FOR_CALIBRATION, title="Измерение Нагрузка"))

    def takeBolt(self, setVal):  # передаем в списке переменную которую поменять в результате
        self.events.append(
            VNAEvent(func=lambda: self.__getCalibrationTask(self.setBolt, setVal), repeat=1,
                     priority=MEASURE_FOR_CALIBRATION, title="Измерение Болт"))

    def __onePortCalibration(self):
        if None in [self.HH, self.KZ, self.MATCH]:
            return
        #TODO проверить калибровки
        if self.settings.txtr == 3:
            self.CalibrationVNA.load_port_one_calibration_standart_data(Open=self.HH, Short=self.KZ, Match=self.MATCH)
            self.CalibrationVNA.calculate_uncalibrated_s()
            self.CalibrationVNA.interpolate_standarts()
            self.CalibrationVNA.calc_port_one_err()
            self.CalibrationVNA.apply_port_one_err()
        else:
            self.CalibrationVNA.load_port_two_calibration_standart_data(Open=self.HH, Short=self.KZ, Match=self.MATCH)
            self.CalibrationVNA.calculate_uncalibrated_s()
            self.CalibrationVNA.interpolate_standarts()
            self.CalibrationVNA.calc_port_two_err()
            self.CalibrationVNA.apply_port_two_err()
        self.calibration = ONE_PORT

    def onePortCalibration(self):
        self.events.append(VNAEvent(func=lambda: self.__onePortCalibration(), repeat=1, priority=CALIBRATION,
                                    title="Однопортовая каллибровка"))
        return True

    def __dualPortCalibration(self):
        if None in [self.HH, self.KZ, self.MATCH, self.BOLT]:
            return
        self.CalibrationVNA.load_port_one_calibration_standart_data(Open=self.HH, Short=self.KZ, Match=self.MATCH)
        self.CalibrationVNA.load_port_two_calibration_standart_data(Open=self.HH, Short=self.KZ, Match=self.MATCH)
        self.CalibrationVNA.load_thru_standart_data(thruData=self.BOLT)
        self.CalibrationVNA.calculate_uncalibrated_s()
        self.CalibrationVNA.interpolate_standarts()
        #TODO проверить калибровки
        self.CalibrationVNA.calc_12term_err()
        self.CalibrationVNA.apply_12term_errors()
        self.calibration = DUAL_PORT

    def dualPortCalibration(self):
        self.events.append(VNAEvent(func=lambda: self.__dualPortCalibration(), repeat=1, priority=CALIBRATION,
                                    title="Двупортовая каллибровка"))
        return True

    def run(self):
        if self.thread is not None:
            self.status = 0
            self.thread.join()
        self.thread = Thread(target=eventLoop, args=(self,), daemon=True)
        self.thread.start()
