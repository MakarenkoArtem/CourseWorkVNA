import time
import numpy as np
from typing import List
from driver.build.vnakit_py import *


def _generate_thousandth_signal(n_points: int) -> List[complex]:
    real = np.random.uniform(-0.01, 0.01, n_points)
    imag = np.random.uniform(-0.01, 0.01, n_points)
    return [complex(r, i) for r, i in zip(real, imag)]


def generate_vna_data(settings: RecordingSettings) -> VNAData:
    n_freqs = settings.freq_range.num_freq_points
    freqs = np.linspace(
        settings.freq_range.freq_start_mhz,
        settings.freq_range.freq_stop_mhz,
        n_freqs
    ).tolist()

    zero_vec = [0j] * n_freqs
    data = VNAData()
    data.frequency = freqs
    data.a0 = zero_vec.copy()
    data.a3 = zero_vec.copy()
    data.b0_3 = zero_vec.copy()
    data.b0_6 = zero_vec.copy()
    data.b3_3 = zero_vec.copy()
    data.b3_6 = zero_vec.copy()

    time.sleep(4)

    if settings.mode == 0:
        if settings.txtr == 3:
            data.a0 = _generate_thousandth_signal(n_freqs)
            data.b0_3 = _generate_thousandth_signal(n_freqs)
            data.b3_3 = _generate_thousandth_signal(n_freqs)
            data.a3 = [1.0 + 0j] * n_freqs
            data.b0_6 = [1.0 + 0j] * n_freqs
            data.b3_6 = [1.0 + 0j] * n_freqs

        else:
            data.a3 = _generate_thousandth_signal(n_freqs)
            data.b0_6 = _generate_thousandth_signal(n_freqs)
            data.b3_6 = _generate_thousandth_signal(n_freqs)
            data.a0 = [1.0 + 0j] * n_freqs
            data.b0_3 = [1.0 + 0j] * n_freqs
            data.b3_3 = [1.0 + 0j] * n_freqs

    else:
        if settings.txtr == 3:
            data.a0 = _generate_thousandth_signal(n_freqs)
            data.b0_3 = _generate_thousandth_signal(n_freqs)
            data.b3_3 = _generate_thousandth_signal(n_freqs)
            data.a3 = _generate_thousandth_signal(n_freqs)
            data.b0_6 = _generate_thousandth_signal(n_freqs)
            data.b3_6 = _generate_thousandth_signal(n_freqs)

        else:
            data.a3 = _generate_thousandth_signal(n_freqs)
            data.b0_6 = _generate_thousandth_signal(n_freqs)
            data.b3_6 = _generate_thousandth_signal(n_freqs)

            data.a0 = _generate_thousandth_signal(n_freqs)
            data.b0_3 = _generate_thousandth_signal(n_freqs)
            data.b3_3 = _generate_thousandth_signal(n_freqs)

    return data


class VNAKitDevice:
    def __init__(self, config_path):
        self.settings = RecordingSettings()
        pass

    def init(self):
        pass

    def set_settings(self, settings):
        self.settings = settings

    def apply_settings(self):
        pass

    def get_result(self):
        return generate_vna_data(self.settings)
