import threading
import time
from datetime import datetime
from data.measurement_data import MeasurementData
from data.calibration_standards import CalibrationStandard

# Константы для состояний калибровки
CALIBRATED = 0
UNCALIBRATED = 0
ONE_PORT = 1
DUAL_PORT = 2

# Для debug-режима
DEBUG = True

if DEBUG:
    print("ЗАПУЩЕН ЭМУЛЯТОР ВЕКТОРНИКА")
    from driver.build.vnakit_py import (
        VNACalibration,
        RecordingSettings,
        VNAData,
        Smatrixs,
    )
    from emulator import VNAKitDevice
else:
    from driver.build.vnakit_py import *

# Константы для состояний
OK = 0
UNCALIBRATED = 0
ONE_PORT = 1
DUAL_PORT = 2

# Инициализация калибровки
CalibrationVNA = VNACalibration()

# Константы для задач
GETTING_DATA = 0
CALIBRATION = 5
MEASURE_FOR_CALIBRATION = 6
DEVICE_SETTINGS = 10


class VNAWorker:
    def __init__(self):
        self.isInit = False
        self.thread = None
        self.status = 1
        self.calibration = UNCALIBRATED
        self.DeviceVNA = None
        self.CalibrationVNA = VNACalibration()
        self.events = []
        self.curEvent = None  # Будет инициализирован позже
        self.MATCH = None
        self.KZ = None
        self.HH = None
        self.BOLT = None
        self.MATCH_DUAL = None
        self.settings = None

    def init(self, settings):
        self.settings = settings
        if DEBUG:
            self.DeviceVNA = VNAKitDevice(config_path="driver/vnakit.conf")
            self.DeviceVNA.init()
        self.setSettings(settings)

    def setSettings(self, settings):
        if DEBUG:
            self.DeviceVNA.set_settings(settings)
            self.DeviceVNA.apply_settings()
        self.isInit = True
        self.settings = settings

    def getResult(self, DATA, seconds=300):
        # В debug-режиме используем эмуляцию
        if DEBUG:
            # Имитация получения данных
            try:
                # Здесь будет реальный вызов, если включен режим
                measurData = self.DeviceVNA.get_result()
                sMatr = Smatrixs()

                # Применяем калибровку
                self.CalibrationVNA.load_measurement_data(measurData)
                self.CalibrationVNA.calculate_uncalibrated_s()

                if self.calibration == UNCALIBRATED:
                    self.CalibrationVNA.get_uncalibrated_s(measurData, sMatr)
                elif self.calibration == ONE_PORT:
                    if self.settings.txtr == 3:
                        self.CalibrationVNA.apply_port_one_err()
                    else:
                        self.CalibrationVNA.apply_port_two_err()
                    self.CalibrationVNA.write_calibrated_s("onePort.csv")
                    sMatr = self.CalibrationVNA.get_calibrated_s()
                elif self.calibration == DUAL_PORT:
                    self.CalibrationVNA.apply_12term_errors()
                    self.CalibrationVNA.write_calibrated_s("dualPort.csv")
                    sMatr = self.CalibrationVNA.get_calibrated_s()

                DATA.frequency = sMatr.frequency
                DATA.S11 = list(map(abs, sMatr.S11))
                DATA.S12 = list(map(abs, sMatr.S12))
                DATA.S21 = list(map(abs, sMatr.S21))
                DATA.S22 = list(map(abs, sMatr.S22))

            except Exception as e:
                print(f"Ошибка получения результата: {e}")
        else:
            # Реальный код для продакшена
            pass

    def save_measurement_to_db(
        self,
        author_id,
        measurement_name,
        frequency_data,
        s11_data,
        s12_data,
        s21_data,
        s22_data,
    ):
        """Сохранить измерения в БД"""
        try:
            # Используем глобальный db_session или создаем новый
            from data import (
                db_session,
            )  # Импорт внутри функции чтобы избежать циклических зависимостей

            db_sess = db_session.create_session()
            measurement = MeasurementData.create_calibrated_measurement(
                db_sess,
                author_id,
                measurement_name,
                frequency_data,
                s11_data,
                s12_data,
                s21_data,
                s22_data,
            )
            db_sess.close()
            return measurement
        except Exception as e:
            print(f"Ошибка сохранения измерений в БД: {e}")
            return None

    def save_calibration_standard_to_db(
        self, author_id, standard_type, port, measurement_name, frequency_data, raw_data
    ):
        """Сохранить калибровочный стандарт в БД"""
        try:
            # Используем глобальный db_session или создаем новый
            from data import (
                db_session,
            )  # Импорт внутри функции чтобы избежать циклических зависимостей

            db_sess = db_session.create_session()
            standard = CalibrationStandard.create_standard(
                db_sess,
                author_id,
                standard_type,
                port,
                measurement_name,
                frequency_data,
                raw_data,
            )
            db_sess.close()
            return standard
        except Exception as e:
            print(f"Ошибка сохранения калибровочного стандарта в БД: {e}")
            return None

    def run(self):
        """Запуск worker'а в отдельном потоке"""
        if self.thread is not None:
            self.status = 0
            self.thread.join()
        self.thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.thread.start()

    def _worker_loop(self):
        """Основной цикл worker'а"""
        while self.status:
            time.sleep(1)

    def stop(self):
        """Остановка worker'а"""
        self.status = 0
        if self.thread:
            self.thread.join()
