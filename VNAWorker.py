from datetime import datetime, timedelta
from threading import Thread
from time import sleep
from VNATask import VNATask

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
DECALIBRATION = 7
DEVICE_SETTINGS = 10


def taskLoop(worker):
    while worker.isRunning:
        worker.tasks.sort(reverse=True)
        if worker.curTask.inProcess():
            if len(worker.tasks) and worker.tasks[0].priority > worker.curTask.priority:
                worker.tasks.append(worker.curTask)
                worker.curTask = worker.tasks.pop(0)
                print("Берем более приоритетную задачу:", worker.curTask.title)
                print("Задачи в очереди:", ", ".join([i.title for i in worker.tasks]))
            worker.curTask.func()
        else:
            if len(worker.tasks):
                worker.curTask = worker.tasks.pop(0)
                print("Берем задачу:", worker.curTask.title)
                print("Задачи в очереди:", ", ".join([i.title for i in worker.tasks]))
            else:
                sleep(0.5)
    worker.isRunning = 1


class VNAWorker:
    def __init__(self):
        self.isInit = False
        self.thread = None
        self.isRunning = 1
        self.calibration = UNCALIBRATED
        self.DeviceVNA = None
        self.CalibrationVNA = VNACalibration()
        self.tasks = []
        self.curTask = VNATask(int, priority=-1, title="Заглушка")
        self.MATCH, self.KZ, self.HH, self.BOLT, self.MATCH_DUAL = None, None, None, None, None
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
        self.tasks.append(VNATask(lambda: self.__setSettingsTask(settings), priority=DEVICE_SETTINGS, repeat=1,
                                  title="Установка настроек"))

    def __getResultTask(self, DATA):
        measurData = self.DeviceVNA.get_result()
        sMatr = Smatrixs()
        # TODO проверить калибровки
        self.CalibrationVNA.load_measurement_data(measurData)
        self.CalibrationVNA.calculate_uncalibrated_s()
        if self.calibration == UNCALIBRATED:
            self.CalibrationVNA.get_uncalibrated_s(measurData, sMatr)
        elif self.calibration == ONE_PORT:
            # TODO проверить калибровки
            if self.settings.txtr == 3:
                self.CalibrationVNA.apply_port_one_err()
            else:
                self.CalibrationVNA.apply_port_two_err()
            self.CalibrationVNA.write_calibrated_s("onePort.csv")
            sMatr = self.CalibrationVNA.get_calibrated_s()
        elif self.calibration == DUAL_PORT:
            # TODO проверить калибровки
            self.CalibrationVNA.apply_12term_errors()
            self.CalibrationVNA.write_calibrated_s("dualPort.csv")
            sMatr = self.CalibrationVNA.get_calibrated_s()
        DATA.frequency = sMatr.frequency
        DATA.S11 = list(map(abs, sMatr.S11))
        DATA.S12 = list(map(abs, sMatr.S12))
        DATA.S21 = list(map(abs, sMatr.S21))
        DATA.S22 = list(map(abs, sMatr.S22))

    def getResult(self, DATA: Smatrixs, seconds=300):
        self.stopGettingMeasurment()
        self.tasks.append(VNATask(lambda: self.__getResultTask(DATA), priority=GETTING_DATA,
                                  timeEnd=datetime.now() + timedelta(seconds=seconds), title="Получение значений"))

    def stopGettingMeasurment(self):
        if self.curTask is not None and self.curTask.priority == GETTING_DATA:
            self.curTask.timeEnd = datetime.now()
            self.curTask.repeat = 0
        self.tasks = [task for task in self.tasks if task.priority != GETTING_DATA]
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

    def setMatchDual(self, data):
        self.MATCH_DUAL = data

    def setBolt(self, data):
        self.BOLT = data

    def takeHH(self, setVal):  # передаем в списке переменную которую поменять в результате
        self.tasks.append(
            VNATask(func=lambda: self.__getCalibrationTask(self.setHH, setVal), repeat=1,
                    priority=MEASURE_FOR_CALIBRATION, title="Измерение ХХ"))

    def takeKZ(self, setVal):  # передаем в списке переменную которую поменять в результате
        self.tasks.append(
            VNATask(func=lambda: self.__getCalibrationTask(self.setKZ, setVal), repeat=1,
                    priority=MEASURE_FOR_CALIBRATION, title="Измерение  КЗ"))

    def takeMatch(self, setVal):  # передаем в списке переменную которую поменять в результате
        self.tasks.append(
            VNATask(func=lambda: self.__getCalibrationTask(self.setMatch, setVal), repeat=1,
                    priority=MEASURE_FOR_CALIBRATION, title="Измерение Нагрузка"))

    def takeBolt(self, setVal):  # передаем в списке переменную которую поменять в результате
        self.tasks.append(
            VNATask(func=lambda: self.__getCalibrationTask(self.setBolt, setVal), repeat=1,
                    priority=MEASURE_FOR_CALIBRATION, title="Измерение Болт"))

    def takeMatchDual(self, setVal):  # передаем в списке переменную которую поменять в результате
        self.tasks.append(
            VNATask(func=lambda: self.__getCalibrationTask(self.setMatchDual, setVal), repeat=1,
                    priority=MEASURE_FOR_CALIBRATION, title="Измерение Нагрузка"))

    def __onePortCalibration(self):
        if None in [self.HH, self.KZ, self.MATCH]:
            return
        self.CalibrationVNA.load_measurement_data(self.DeviceVNA.get_result())
        # TODO проверить калибровки
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
        self.tasks.append(VNATask(func=lambda: self.__onePortCalibration(), repeat=1, priority=CALIBRATION,
                                  title="Однопортовая калибровка"))
        return True

    def __dualPortCalibration(self):
        if None in [self.HH, self.KZ, self.BOLT, self.MATCH]:
            return
        self.CalibrationVNA.load_measurement_data(self.DeviceVNA.get_result())
        self.CalibrationVNA.load_port_one_calibration_standart_data(Open=self.HH, Short=self.KZ, Match=self.MATCH)
        self.CalibrationVNA.load_port_two_calibration_standart_data(Open=self.HH, Short=self.KZ, Match=self.MATCH)
        self.CalibrationVNA.load_thru_standart_data(thruData=self.BOLT)
        if self.MATCH_DUAL is not None:
            self.CalibrationVNA.load_two_match_standart_data(self.MATCH_DUAL)
        self.CalibrationVNA.calculate_uncalibrated_s()
        self.CalibrationVNA.interpolate_standarts()
        # TODO проверить калибровки
        self.CalibrationVNA.calc_12term_err()
        self.CalibrationVNA.apply_12term_errors()
        self.calibration = DUAL_PORT

    def dualPortCalibration(self):
        self.tasks.append(VNATask(func=lambda: self.__dualPortCalibration(), repeat=1, priority=CALIBRATION,
                                  title="Двухпортовая калибровка"))
        return True

    def __decalibrateTask(self):
        self.calibration = UNCALIBRATED
        self.MATCH, self.KZ, self.HH, self.BOLT, self.MATCH_DUAL = None, None, None, None, None
        self.tasks = [task for task in self.tasks if task.priority != CALIBRATION]

    def decalibrate(self):
        self.tasks.append(VNATask(func=lambda: self.__decalibrateTask(), repeat=1, priority=DECALIBRATION,
                                  title="Декалибровка"))

    def run(self):
        if self.thread is not None:
            self.isRunning = 0
            self.thread.join()
        self.thread = Thread(target=taskLoop, args=(self,), daemon=True)
        self.thread.start()
