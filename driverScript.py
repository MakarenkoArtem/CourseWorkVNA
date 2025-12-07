from driver.build.vnakit_py import *

dev = VNAKitDevice(config_path="driver/vnakit.conf")
dev.init()
set = RecordingSettings()
set.freq_range = FrequencyRange()
set.freq_range.freq_start_mhz = 500
set.freq_range.freq_stop_mhz = 6000
set.freq_range.num_freq_points = 1001
set.mode = 1
set.output_power_dbm = -10
set.rbw_khz = 2
set.txtr = 3
print(dev.set_settings(set))
print(dev.validate_settings())
print(dev.apply_settings())
obj = dev.get_result()

fields = {
    name: getattr(obj, name)
    for name in dir(obj)
    if not name.startswith("__") and not callable(getattr(obj, name))
}

print(fields)
dev.shutdown()


class VNADevice(VNAKitDevice):
    def __init__(self, config_path):
        self.super(config_path)
        self.init()

    def getMeasur(self, recSettings: RecordingSettings):
        self.set_settings(recSettings)
        self.validate_settings()
        self.apply_settings()
        return self.get_result()
