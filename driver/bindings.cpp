#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/complex.h>  // Для std::complex<double>
#include "VNAKitDevice.h"

namespace py = pybind11;

PYBIND11_MODULE(vnakit_py, m) {
    m.doc() = "Python bindings for VNAKitDevice";

    // === Экспорт всех структур VNAKit (без изменений) ===

    py::class_<VNAKit_Complex>(m, "Complex")
        .def(py::init<>())
        .def_readwrite("real", &VNAKit_Complex::real)
        .def_readwrite("imag", &VNAKit_Complex::imag)
        .def("__repr__", [](const VNAKit_Complex& c) {
            return "Complex(" + std::to_string(c.real) + ", " + std::to_string(c.imag) + ")";
        });

    py::class_<VNAKit_FrequencyRange>(m, "FrequencyRange")
        .def(py::init<>())
        .def_readwrite("freq_start_mhz", &VNAKit_FrequencyRange::freqStartMHz)
        .def_readwrite("freq_stop_mhz", &VNAKit_FrequencyRange::freqStopMHz)
        .def_readwrite("num_freq_points", &VNAKit_FrequencyRange::numFreqPoints);

    py::class_<VNAKit_RecordingSettings>(m, "RecordingSettings")
        .def(py::init<>())
        .def_readwrite("freq_range", &VNAKit_RecordingSettings::freqRange)
        .def_readwrite("rbw_khz", &VNAKit_RecordingSettings::rbw_khz)
        .def_readwrite("output_power_dbm", &VNAKit_RecordingSettings::outputPower_dbm)
        .def_readwrite("txtr", &VNAKit_RecordingSettings::txtr)
        .def_readwrite("mode", &VNAKit_RecordingSettings::mode);

    py::class_<VNAKit_FrequencyLimits>(m, "FrequencyLimits")
        .def(py::init<>())
        .def_readonly("min_mhz", &VNAKit_FrequencyLimits::min_MHz)
        .def_readonly("max_mhz", &VNAKit_FrequencyLimits::max_MHz)
        .def_readonly("step_mhz", &VNAKit_FrequencyLimits::step_MHz)
        .def_readonly("n_points_min", &VNAKit_FrequencyLimits::nPointsMin)
        .def_readonly("n_points_max", &VNAKit_FrequencyLimits::nPointsMax);

    py::class_<VNAKit_PowerLimits>(m, "PowerLimits")
        .def(py::init<>())
        .def_readonly("min_dbm", &VNAKit_PowerLimits::min_dbm)
        .def_readonly("max_dbm", &VNAKit_PowerLimits::max_dbm)
        .def_readonly("step_dbm", &VNAKit_PowerLimits::step_dbm);

    py::class_<VNAKit_RbwLimits>(m, "RbwLimits")
        .def(py::init<>())
        .def_readonly("min_khz", &VNAKit_RbwLimits::min_KHz)
        .def_readonly("max_khz", &VNAKit_RbwLimits::max_KHz)
        .def_readonly("step_khz", &VNAKit_RbwLimits::step_KHz);

    py::class_<VNAKit_RecordingResult>(m, "RecordingResult")
        .def(py::init<>())
        .def_readwrite("n_rx_tr", &VNAKit_RecordingResult::nRxTr)
        .def_readwrite("n_frequencies_measured", &VNAKit_RecordingResult::nFrequenciesMeasured);

    // === НОВАЯ СТРУКТУРА: VNAData ===
    py::class_<VNAData>(m, "VNAData")
        .def(py::init<>())
        .def_readonly("frequency", &VNAData::frequency)
        .def_readonly("a0", &VNAData::a0)
        .def_readonly("a3", &VNAData::a3)
        .def_readonly("b0_3", &VNAData::b0_3)
        .def_readonly("b0_6", &VNAData::b0_6)
        .def_readonly("b3_3", &VNAData::b3_3)
        .def_readonly("b3_6", &VNAData::b3_6);

    // === Основной класс: VNAKitDevice ===
    py::class_<VNAKitDevice>(m, "VNAKitDevice")
        .def(py::init<const std::string&>(), py::arg("config_path"))
        .def("init", &VNAKitDevice::init,
             py::call_guard<py::gil_scoped_release>())
        .def("shutdown", &VNAKitDevice::shutdown)
        .def("set_config_file", &VNAKitDevice::setConfigFile, py::arg("path"))
        .def("apply_settings", &VNAKitDevice::applySettings,
             py::call_guard<py::gil_scoped_release>())
        .def("validate_settings", &VNAKitDevice::validateSettings)
        .def("get_settings", &VNAKitDevice::getSettings,
             py::return_value_policy::reference_internal)
        .def("set_settings", &VNAKitDevice::setSettings, py::arg("settings"))
        .def("get_frequency_vector_mhz", &VNAKitDevice::getFrequencyVectorMHz)
        .def("get_result", &VNAKitDevice::getResult,
             py::call_guard<py::gil_scoped_release>())
        .def("frequency_limits", &VNAKitDevice::frequencyLimits)
        .def("power_limits", &VNAKitDevice::powerLimits)
        // Обратите внимание: lastError теперь НЕ статический и требует аргумент!
        .def_static("last_error", [](VNAKIT_RESULT result) {
            return VNAKitDevice::lastError(result);
        });

    // Обработка исключений
    py::register_exception_translator([](std::exception_ptr p) {
        try {
            if (p) std::rethrow_exception(p);
        } catch (const std::runtime_error& e) {
            PyErr_SetString(PyExc_RuntimeError, e.what());
        }
    });
}