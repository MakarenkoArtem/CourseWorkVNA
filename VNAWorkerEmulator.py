from datetime import datetime, timedelta
from threading import Thread
from time import sleep
from VNAEvent import VNAEvent
from driver.build.vnakit_py import *
from emulator import generate_vna_data

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
        # print(worker.curEvent.title, [i.title for i in worker.events])
        if worker.curEvent.inProcess():
            if len(worker.events) and worker.events[0].priority > worker.curEvent.priority:
                worker.events.append(worker.curEvent)
                worker.curEvent = worker.events.pop(0)
                print("Берем более приоритетную задачу", worker.curEvent.title)
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

SETTINGS=RecordingSettings()
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


    def init(self, settings: RecordingSettings):
        pass

    def __setSettingsTask(self, settings: RecordingSettings):
        global SETTINGS
        SETTINGS=settings
        self.isInit = True

    def setSettings(self, settings: RecordingSettings):
        self.events.append(VNAEvent(lambda: self.__setSettingsTask(settings), priority=DEVICE_SETTINGS, repeat=1,
                                    title="Установка настроек"))

    def __getResultTask(self, DATA):
        global SETTINGS
        measurData = generate_vna_data(SETTINGS)
        sMatr = Smatrixs()
        self.CalibrationVNA.load_measurement_data(measurData)
        if self.calibration == UNCALIBRATED:
            self.CalibrationVNA.calculate_uncalibrated_s()
            self.CalibrationVNA.get_uncalibrated_s(measurData, sMatr)
        elif self.calibration == ONE_PORT:
            self.CalibrationVNA.interpolate_standarts()
            self.CalibrationVNA.calc_port_one_err()
            self.CalibrationVNA.apply_port_one_err()
            d = Smatrixs()
            self.CalibrationVNA.get_uncalibrated_s(measurData, d)
            self.CalibrationVNA.calculate_uncalibrated_s()
            sMatr = self.CalibrationVNA.get_calibrated_s()
            # sMatr = d
            sMatr.frequency = DATA.frequency
        elif self.calibration == DUAL_PORT:
            self.CalibrationVNA.interpolate_standarts()
            self.CalibrationVNA.calc_port_two_err()
            self.CalibrationVNA.apply_port_two_err()
            self.CalibrationVNA.calculate_uncalibrated_s()
            d = Smatrixs()
            self.CalibrationVNA.get_uncalibrated_s(measurData, d)
            sMatr = self.CalibrationVNA.get_calibrated_s()
            # sMatr = d
            sMatr.frequency = DATA.frequency
        DATA.frequency = sMatr.frequency
        DATA.S11 = list(map(abs, sMatr.S11))
        DATA.S12 = list(map(abs, sMatr.S12))
        DATA.S21 = list(map(abs, sMatr.S21))
        DATA.S22 = list(map(abs, sMatr.S22))
        # print("DATA:", DATA.__dict__)

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
        global SETTINGS
        setData(SETTINGS)
        '''data.frequency = newData.frequency
        data.a0 = newData.a0
        data.b0_3 = newData.b0_3
        data.b3_3 = newData.b3_3
        data.a3 = newData.a3
        data.b0_6 = newData.b0_6
        data.b3_6 = newData.b3_6'''
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
        self.CalibrationVNA.load_port_one_calibration_standart_data(Open=self.HH, Short=self.KZ, Match=self.MATCH)
        self.CalibrationVNA.calculate_uncalibrated_s()
        self.CalibrationVNA.interpolate_standarts()
        self.CalibrationVNA.calc_port_one_err()
        self.CalibrationVNA.apply_port_one_err()
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
        if True:
            self.CalibrationVNA.calculate_uncalibrated_s()
            self.CalibrationVNA.interpolate_standarts()
            self.CalibrationVNA.calc_port_two_err()
            self.CalibrationVNA.apply_port_two_err()
            self.calibration = DUAL_PORT
        else:
            self.CalibrationVNA.load_thru_standart_data(self.BOLT)
            self.CalibrationVNA.calculate_uncalibrated_s()
            self.CalibrationVNA.interpolate_standarts()
            self.CalibrationVNA.calc_12term_err()
            self.CalibrationVNA.apply_12term_errors()

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
