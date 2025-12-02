import numpy as np
from dataclasses import dataclass
from typing import List



@dataclass
class Smatrixs:
    frequency: List[float]
    S11: List[complex]
    S12: List[complex]
    S21: List[complex]
    S22: List[complex]


@dataclass
class MagnitudeResponse:
    frequency: List[float]
    S11_mag: List[float]
    S12_mag: List[float]
    S21_mag: List[float]
    S22_mag: List[float]


@dataclass
class PhaseResponse:
    frequency: List[float]
    S11_phase: List[float]
    S12_phase: List[float]
    S21_phase: List[float]
    S22_phase: List[float]



def get_uncalibrated_s(data) -> Smatrixs:
    n = len(data.frequency)

    S11 = [0j] * n
    S12 = [0j] * n
    S21 = [0j] * n
    S22 = [0j] * n

    for i in range(n):
        if abs(data.a0[i]) < 1e-15:
            print(f"Внимание: a0[{i}] близко к нулю! freq = {data.frequency[i]} МГц")
            S11[i] = 0j
            S21[i] = 0j
        else:
            S11[i] = data.b0_3[i] / data.a0[i]
            S21[i] = data.b3_3[i] / data.a0[i]

        if abs(data.a3[i]) < 1e-15:
            print(f"Внимание: a3[{i}] близко к нулю! freq = {data.frequency[i]} МГц")
            S12[i] = 0j
            S22[i] = 0j
        else:
            S12[i] = data.b0_6[i] / data.a3[i]
            S22[i] = data.b3_6[i] / data.a3[i]

    return Smatrixs(
        frequency=data.frequency.copy(),
        S11=S11,
        S12=S12,
        S21=S21,
        S22=S22
    )


def calculate_magnitude_response(s_params: Smatrixs) -> MagnitudeResponse:
    return MagnitudeResponse(
        frequency=s_params.frequency.copy(),
        S11_mag=[abs(s) for s in s_params.S11],
        S12_mag=[abs(s) for s in s_params.S12],
        S21_mag=[abs(s) for s in s_params.S21],
        S22_mag=[abs(s) for s in s_params.S22]
    )


def calculate_phase_response(s_params: Smatrixs) -> PhaseResponse:
    return PhaseResponse(
        frequency=s_params.frequency.copy(),
        S11_phase=[np.angle(s) for s in s_params.S11],
        S12_phase=[np.angle(s) for s in s_params.S12],
        S21_phase=[np.angle(s) for s in s_params.S21],
        S22_phase=[np.angle(s) for s in s_params.S22]
    )


def magnitude_to_db(mag_response: MagnitudeResponse) -> MagnitudeResponse:
    def mag_to_db(mag):
        return 20 * np.log10(max(mag, 1e-15))

    return MagnitudeResponse(
        frequency=mag_response.frequency.copy(),
        S11_mag=[mag_to_db(m) for m in mag_response.S11_mag],
        S12_mag=[mag_to_db(m) for m in mag_response.S12_mag],
        S21_mag=[mag_to_db(m) for m in mag_response.S21_mag],
        S22_mag=[mag_to_db(m) for m in mag_response.S22_mag]
    )


def phase_to_degrees(phase_response: PhaseResponse) -> PhaseResponse:
    RAD_TO_DEG = 180.0 / np.pi
    return PhaseResponse(
        frequency=phase_response.frequency.copy(),
        S11_phase=[p * RAD_TO_DEG for p in phase_response.S11_phase],
        S12_phase=[p * RAD_TO_DEG for p in phase_response.S12_phase],
        S21_phase=[p * RAD_TO_DEG for p in phase_response.S21_phase],
        S22_phase=[p * RAD_TO_DEG for p in phase_response.S22_phase]
    )