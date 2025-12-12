from VNAWorker import UNCALIBRATED
from driver.build.vnakit_py import RecordingSettings, FrequencyRange


def get_nested_attr(obj, attr):
    for part in attr.split('.'):
        obj = getattr(obj, part)
    return obj


def set_nested_attr(obj, attr, value):
    parts = attr.split('.')
    for part in parts[:-1]:
        obj = getattr(obj, part)
    setattr(obj, parts[-1], value)


def cpyData(source, obj, mapp):
    for source_key, target_key in mapp.items():
        try:
            value = get_nested_attr(source, source_key)
            set_nested_attr(obj, target_key, value)
        except AttributeError as e:
            print(f"Error accessing attribute '{source_key}': {e}")


CALIBRATED = 0
UNCORRECTED_CALIBRATION = 3
CALIBRATING = 4
UNCALIBRATED = 5


class SettingsModel:
    def __init__(self, author_id=-1):
        self.id = -1
        self.author_id = author_id
        self.freq_start_mhz = 500
        self.freq_stop_mhz = 6000
        self.num_freq_points = 1001
        self.rbw_khz = 2
        self.output_power_dbm = -10
        self.txtr = 3
        self.mode = 0
        self.calib_HH = UNCALIBRATED
        self.calib_KZ = UNCALIBRATED
        self.calib_Match = UNCALIBRATED
        self.calib_Bolt = UNCALIBRATED
        self.calib_Match_Dual = UNCALIBRATED

    def fromDB(self, dbSettings):
        mapp = {'id': 'id', 'author_id': 'author_id', 'freq_start_mhz': 'freq_start_mhz',
                'freq_stop_mhz': 'freq_stop_mhz', 'num_freq_points': 'num_freq_points', 'rbw_khz': 'rbw_khz',
                'output_power_dbm': 'output_power_dbm', 'txtr': 'txtr', 'mode': 'mode'}
        cpyData(source=dbSettings, obj=self, mapp=mapp)
        return self

    def toDB(self, dbSettings):
        mapp = {'author_id': 'author_id', 'freq_start_mhz': 'freq_start_mhz',
                'freq_stop_mhz': 'freq_stop_mhz', 'num_freq_points': 'num_freq_points', 'rbw_khz': 'rbw_khz',
                'output_power_dbm': 'output_power_dbm', 'txtr': 'txtr', 'mode': 'mode'}
        cpyData(source=self, obj=dbSettings, mapp=mapp)
        return dbSettings

    def toRecordingSettings(self):
        recordSettings = RecordingSettings()
        recordSettings.freq_range = FrequencyRange()
        mapp = {'freq_start_mhz': 'freq_start_mhz', 'freq_stop_mhz': 'freq_stop_mhz',
                'num_freq_points': 'num_freq_points'}
        cpyData(source=self, obj=recordSettings.freq_range, mapp=mapp)

        mapp = {'rbw_khz': 'rbw_khz', 'output_power_dbm': 'output_power_dbm', 'txtr': 'txtr', 'mode': 'mode'}
        cpyData(source=self, obj=recordSettings, mapp=mapp)
        return recordSettings

    def fromForm(self, form):
        mapp = {'freq_start_mhz.data': 'freq_start_mhz', 'freq_stop_mhz.data': 'freq_stop_mhz',
                'num_freq_points.data': 'num_freq_points', 'rbw_khz.data': 'rbw_khz',
                'output_power_dbm.data': 'output_power_dbm', 'txtr.data': 'txtr', 'mode.data': 'mode'}
        cpyData(source=form, obj=self, mapp=mapp)
        self.txtr = int(form.txtr.data)
        self.mode = int(form.mode.data)
        return self

    def toForm(self, form):
        mapp = {'freq_start_mhz': 'freq_start_mhz.data', 'freq_stop_mhz': 'freq_stop_mhz.data',
                'num_freq_points': 'num_freq_points.data', 'rbw_khz': 'rbw_khz.data',
                'output_power_dbm': 'output_power_dbm.data', 'txtr': 'txtr.data', 'mode': 'mode.data'}
        cpyData(source=self, obj=form, mapp=mapp)
        form.txtr.data = str(form.txtr.data)
        form.mode.data = str(form.mode.data)
        return form

    def toDict(self):
        return self.__dict__
