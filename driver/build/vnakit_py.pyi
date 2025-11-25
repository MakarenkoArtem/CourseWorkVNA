# Stub file for vnakit_py.so
# Provides type hints for IDEs (PyCharm, VSCode)

from typing import List, Tuple, Optional


class Complex:
    real: float
    imag: float

    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...


class FrequencyRange:
    freq_start_mhz: float
    freq_stop_mhz: float
    num_freq_points: int

    def __init__(self) -> None: ...


class RecordingSettings:
    freq_range: FrequencyRange
    rbw_khz: float
    output_power_dbm: float
    txtr: int
    mode: int

    def __init__(self) -> None: ...


class FrequencyLimits:
    min_mhz: float
    max_mhz: float
    step_mhz: float
    n_points_min: int
    n_points_max: int

    def __init__(self) -> None: ...


class PowerLimits:
    min_dbm: float
    max_dbm: float
    step_dbm: float

    def __init__(self) -> None: ...


class RbwLimits:
    min_khz: float
    max_khz: float
    step_khz: float

    def __init__(self) -> None: ...


class RecordingResult:
    n_rx_tr: int
    n_frequencies_measured: int

    def __init__(self) -> None: ...


class Measurement:
    start_freq: float
    stop_freq: float
    mode: int

    # Lists of [real, imag]
    @property
    def a0(self) -> List[List[float]]: ...
    @property
    def a3(self) -> List[List[float]]: ...
    @property
    def b0(self) -> List[List[float]]: ...
    @property
    def b3(self) -> List[List[float]]: ...

    def __init__(self) -> None: ...


class VNAKitDevice:
    def __init__(self, config_path: str) -> None: ...

    # Device lifecycle
    def init(self) -> None: ...
    def shutdown(self) -> None: ...

    # Config file management
    def set_config_file(self, path: str) -> None: ...

    # Settings
    def apply_settings(self) -> None: ...
    def validate_settings(self) -> None: ...
    def get_settings(self) -> RecordingSettings: ...
    def set_settings(self, settings: RecordingSettings) -> None: ...

    # Measurement utilities
    def get_frequency_vector_mhz(self) -> List[float]: ...
    def get_result(self) -> Measurement: ...

    # Limits
    def frequency_limits(self) -> FrequencyLimits: ...
    def power_limits(self) -> PowerLimits: ...

    @staticmethod
    def last_error() -> str: ...
