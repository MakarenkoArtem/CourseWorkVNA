from datetime import datetime, timedelta
from threading import Thread
from time import sleep
from VNAEvent import VNAEvent
from driver.build.vnakit_py import *

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
                print("Берем более приоритетную задачу")
            worker.curEvent.func()
        else:
            if len(worker.events):
                worker.event = worker.events.pop(0)
                print("TAKE EVENT:", worker.curEvent.__dict__)
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
        self.curEvent = None
        self.MATCH, self.KZ, self.HH, self.BOLT = None, None, None, None

    def init(self, settings: RecordingSettings):
        self.DeviceVNA = VNAKitDevice(config_path="driver/vnakit.conf")
        self.DeviceVNA.init()
        self.setSettings(settings)

    def __setSettingsTask(self, settings: RecordingSettings):
        self.DeviceVNA.set_settings(settings)
        self.DeviceVNA.apply_settings()
        self.isInit = True

    def setSettings(self, settings: RecordingSettings):
        self.events.append(VNAEvent(lambda: self.__setSettingsTask(settings), priority=DEVICE_SETTINGS, repeat=1))

    def __getResultTask(self, DATA):
        measurData = self.DeviceVNA.get_result()
        sMatr = Smatrixs()
        self.CalibrationVNA.load_measurement_data(measurData)
        if self.calibration == UNCALIBRATED:
            self.CalibrationVNA.calculate_uncalibrated_s()
            self.CalibrationVNA.get_uncalibrated_s(measurData, sMatr)
        elif self.calibration == ONE_PORT:
            self.CalibrationVNA.interpolate_standarts()
            self.CalibrationVNA.calc_port_one_err()
            self.CalibrationVNA.apply_port_one_err()
            sMatr = self.CalibrationVNA.get_calibrated_s()
        DATA.frequency = sMatr.frequency
        DATA.S11 = list(map(abs, sMatr.S11))
        DATA.S12 = list(map(abs, sMatr.S12))
        DATA.S21 = list(map(abs, sMatr.S21))
        DATA.S22 = list(map(abs, sMatr.S22))
        print("DATA:", DATA.__dict__)

    def getResult(self, DATA: VNAData, seconds=300):
        self.stopGettingMeasurment()
        self.events.append(VNAEvent(lambda: self.__getResultTask(DATA), priority=GETTING_DATA,
                                    timeEnd=datetime.now() + timedelta(seconds=seconds)))

    def stopGettingMeasurment(self):
        if self.curEvent is not None and self.curEvent.priority == GETTING_DATA:
            self.curEvent.timeEnd = datetime.now()
            self.curEvent.repeat = 0
        self.events = [event for event in self.events if self.events.priority != GETTING_DATA]
        return True

    def __getCalibrationTask(self, data):
        newData = self.DeviceVNA.get_result()
        data.frequency = newData.frequency
        data.a0 = newData.a0
        data.b0_3 = newData.b0_3
        data.b3_3 = newData.b3_3
        data.a3 = newData.a3
        data.b0_6 = newData.b0_6
        data.b3_6 = newData.b3_6
        return 1

    def takeHH(self):
        self.events.append(
            VNAEvent(func=lambda: self.__getCalibrationTask(self.HH), repeat=1, priority=MEASURE_FOR_CALIBRATION))

    def takeKZ(self):
        self.events.append(
            VNAEvent(func=lambda: self.__getCalibrationTask(self.KZ), repeat=1, priority=MEASURE_FOR_CALIBRATION))

    def takeMatch(self):
        self.events.append(
            VNAEvent(func=lambda: self.__getCalibrationTask(self.MATCH), repeat=1, priority=MEASURE_FOR_CALIBRATION))

    def takeBolt(self):
        self.events.append(
            VNAEvent(func=lambda: self.__getCalibrationTask(self.BOLT), repeat=1, priority=MEASURE_FOR_CALIBRATION))

    def __onePortCalibration(self):
        self.CalibrationVNA.load_port_one_calibration_standart_data(Open=self.HH, Short=self.KZ, Match=self.MATCH)
        self.CalibrationVNA.interpolate_standarts()
        self.CalibrationVNA.calc_port_one_err()
        self.CalibrationVNA.apply_port_one_err()

    def onePortCalibration(self):
        if None in [self.HH, self.KZ, self.MATCH]:
            return False
        self.events.append(VNAEvent(func=lambda: self.__onePortCalibration(), repeat=1, priority=CALIBRATION))
        return True

    def dualPortCalibration(self):
        if None in [self.HH, self.KZ, self.MATCH, self.BOLT]:
            return False
        # self.events.append(VNAEvent(func=lambda: self.__dualPortCalibration(), repeat=1, priority=CALIBRATION))
        return True

    def run(self):
        if self.thread is not None:
            self.status = 0
            self.thread.join()
        self.thread = Thread(target=eventLoop, args=(self,), daemon=True)
        self.thread.start()


'''
def VNAWorker(events):
    CalibrationVNA = VNACalibration()
    DATA = processing.Smatrixs(frequency=[], S11=[], S12=[], S21=[], S22=[])

    DeviceVNA = VNAKitDevice(config_path="driver/vnakit.conf")
    DeviceVNA.init()
    DeviceVNA.set_settings(SETTINGS.toRecordingSettings())
    DeviceVNA.apply_settings()

    event = VNAEvent(int)
    while 1:
        events.sort(reverse=True)
        if event.inProcess():
            if len(events) and events[0].priority > event.priority:
                events.append(event)
                event = events.pop(0)
                print("Берем более приоритетную задачу")
            event.func()
        else:
            if len(events):
                event = events.pop(0)
                print("TAKE EVENT:", event.__dict__)
            else:
                time.sleep(0.5)
'''
