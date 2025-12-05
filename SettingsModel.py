def get_nested_attr(obj, attr):
    """Retrieve a nested attribute from an object."""
    for part in attr.split('.'):
        obj = getattr(obj, part)
    return obj


def cpyData(obj, source, mapp):
    for source_key, target_key in mapp.items():
        try:
            value = get_nested_attr(source, source_key)
            setattr(obj, target_key, value)
        except AttributeError as e:
            print(f"Error accessing attribute '{source_key}': {e}")


class SettingsModel:
    def __init__(self, author_id=-1):
        self.id = -1
        self.author_id = author_id
        self.freq_start_mhz = 100
        self.freq_stop_mhz = 1000
        self.num_freq_points = 100
        self.rbw_khz = 1
        self.output_power_dbm = -3
        self.txtr = 3
        self.mode = 0
        self.calib_HH = 1
        self.calib_KZ = 1
        self.calib_Match = 1
        self.calib_Bolt = 1

    def fromDB(self, dbSettings):
        mapp = {'id': 'id', 'author_id': 'author_id', 'freq_start_mhz': 'freq_start_mhz',
                'freq_stop_mhz': 'freq_stop_mhz', 'num_freq_points': 'num_freq_points', 'rbw_khz': 'rbw_khz',
                'output_power_dbm': 'output_power_dbm', 'txtr': 'txtr', 'mode': 'mode'}
        cpyData(self, dbSettings, mapp)
        return self

    def fromForm(self, form):
        mapp = {'freq_start_mhz.data': 'freq_start_mhz', 'freq_stop_mhz.data': 'freq_stop_mhz',
                'num_freq_points.data': 'num_freq_points', 'rbw_khz.data': 'rbw_khz',
                'output_power_dbm.data': 'output_power_dbm', 'txtr.data': 'txtr', 'mode.data': 'mode'}
        cpyData(self, form, mapp)
        self.txtr = int(self.txtr)
        self.mode = int(self.mode)
        return self

    def toDB(self, dbSettings):
        mapp = {'author_id': 'author_id', 'freq_start_mhz': 'freq_start_mhz',
                'freq_stop_mhz': 'freq_stop_mhz', 'num_freq_points': 'num_freq_points', 'rbw_khz': 'rbw_khz',
                'output_power_dbm': 'output_power_dbm', 'txtr': 'txtr', 'mode': 'mode'}
        cpyData(dbSettings, self, mapp)
        return dbSettings

    def toDict(self):
        return self.__dict__
