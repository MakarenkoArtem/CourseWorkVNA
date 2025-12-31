#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/complex.h>  // Для std::complex<double>
#include "VNAKitDevice.h"
#include "VNACalibration.h"

using namespace pybind11::literals;
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
        .def_readwrite("frequency", &VNAData::frequency)
        .def_readwrite("a0", &VNAData::a0)
        .def_readwrite("a3", &VNAData::a3)
        .def_readwrite("b0_3", &VNAData::b0_3)
        .def_readwrite("b0_6", &VNAData::b0_6)
        .def_readwrite("b3_3", &VNAData::b3_3)
        .def_readwrite("b3_6", &VNAData::b3_6);

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

    py::class_<Smatrixs>(m, "Smatrixs")
    .def(py::init<>())
    .def_readwrite("frequency", &Smatrixs::frequency)
    .def_readwrite("S11", &Smatrixs::S11)
    .def_readwrite("S12", &Smatrixs::S12)
    .def_readwrite("S21", &Smatrixs::S21)
    .def_readwrite("S22", &Smatrixs::S22)
    .def("to_dict", [](const Smatrixs& s) {
        py::dict d;
        d["frequency"] = s.frequency;
        d["S11"] = s.S11;
        d["S12"] = s.S12;
        d["S21"] = s.S21;
        d["S22"] = s.S22;
        return d;
    });


// === НОВАЯ СТРУКТУРА: OSMstandart ===
py::class_<OSMstandart>(m, "OSMstandart")
    .def(py::init<>())
    .def_readwrite("frequency", &OSMstandart::frequency)
    .def_readwrite("S", &OSMstandart::S);

// === Структура флагов ===
py::class_<flags>(m, "CalibrationFlags")
    .def(py::init<>())
    .def_readonly("full_measurement_data_got", &flags::full_measurement_data_got)
    .def_readonly("measurement_data_side3_got", &flags::measurement_data_side3_got)
    .def_readonly("measurement_data_side6_got", &flags::measurement_data_side6_got)
    .def_readonly("firstP_standart_data_got", &flags::firstP_standart_data_got)
    .def_readonly("secondP_standart_data_got", &flags::secondP_standart_data_got)
    .def_readonly("thru_standart_got", &flags::thru_standart_got)
    .def_readonly("match2_standart_got", &flags::match2_standart_got)
    .def_readonly("firstP_standart_interpolated", &flags::firstP_standart_interpolated)
    .def_readonly("secondP_standart_interpolated", &flags::secondP_standart_interpolated)
    .def_readonly("thru_standart_interpolated", &flags::thru_standart_interpolated)
    .def_readonly("match2_standart_interpolated", &flags::match2_standart_interpolated)
    .def_readonly("uncalibrates_S_calculated", &flags::uncalibrates_S_calculated)
    .def_readonly("port_one_errors_calculated", &flags::port_one_errors_calculated)
    .def_readonly("port_two_errors_calculated", &flags::port_two_errors_calculated)
    .def_readonly("error_12term_calculated", &flags::error_12term_calculated)
    .def_readonly("S11_calibrated", &flags::S11_calibrated)
    .def_readonly("S22_calibrated", &flags::S22_calibrated)
    .def_readonly("Smatrix_calibrated", &flags::Smatrix_calibrated);

// === Основные структуры ошибок ===
py::class_<singlePortE>(m, "SinglePortError")
    .def(py::init<>())
    .def_readwrite("ef00", &singlePortE::ef00)
    .def_readwrite("ef11", &singlePortE::ef11)
    .def_readwrite("det_ef", &singlePortE::detEf);

py::class_<fullErrModel>(m, "FullErrorModel")
    .def(py::init<>())
    // Однопортовые по 1-му порту
    .def_readwrite("ef00", &fullErrModel::ef00)
    .def_readwrite("ef11", &fullErrModel::ef11)
    .def_readwrite("ef10_01", &fullErrModel::ef10_01)
    // По 2-му порту
    .def_readwrite("er33", &fullErrModel::er33)
    .def_readwrite("er22", &fullErrModel::er22)
    .def_readwrite("er23_32", &fullErrModel::er23_32)
    // Утечки
    .def_readwrite("ef30", &fullErrModel::ef30)
    .def_readwrite("er03", &fullErrModel::er03)
    // Двупортовые
    .def_readwrite("ef22", &fullErrModel::ef22)
    .def_readwrite("ef10_32", &fullErrModel::ef10_32)
    .def_readwrite("er11", &fullErrModel::er11)
    .def_readwrite("er23_01", &fullErrModel::er23_01);

// === ОСНОВНОЙ КЛАСС ===
py::class_<VNACalibration>(m, "VNACalibration")
    .def(py::init<>())

    // Загрузка данных (из памяти)
    .def("load_measurement_data", &VNACalibration::loadMeasurementData, py::arg("data"))
    .def("load_port_one_calibration_standart_data", &VNACalibration::loadPortOneCalibrationStandartData,
         py::arg("Open"), py::arg("Short"), py::arg("Match"))
    .def("load_port_two_calibration_standart_data", &VNACalibration::loadPortTwoCalibrationStandartData,
         py::arg("Open"), py::arg("Short"), py::arg("Match"))
    .def("load_thru_standart_data", &VNACalibration::loadThruStandartData, py::arg("thruData"))
    .def("load_two_match_standart_data", &VNACalibration::loadTwoMatchStandartData, py::arg("match2Data"))

    // Загрузка данных (из файлов)
    .def("load_measurement_data_side3_from_file", &VNACalibration::loadMeasurementDataSide3FromFile, py::arg("filename"))
    .def("load_measurement_data_side6_from_file", &VNACalibration::loadMeasurementDataSide6FromFile, py::arg("filename"))
    .def("load_port_one_calibration_standarts_from_file", &VNACalibration::loadPortOneCalibrationStandartsFromFile,
         py::arg("openFile"), py::arg("shortFile"), py::arg("matchFile"))
    .def("load_port_two_calibration_standarts_from_file", &VNACalibration::loadPortTwoCalibrationStandartsFromFile,
         py::arg("openFile"), py::arg("shortFile"), py::arg("matchFile"))
    .def("load_thru_standart", &VNACalibration::loadThruStandart,
         py::arg("thruFile3"), py::arg("thruFile6"))
    .def("load_2match_standart", &VNACalibration::load2matchStandart,
         py::arg("match2File3"), py::arg("match2File6"))

    // Внутренние методы загрузки (публичные версии)
    .def("get_data_side3_from_file", &VNACalibration::readDataSide3FromFile,
         py::arg("filename"), py::arg("result"))
    .def("get_data_side6_from_file", &VNACalibration::readDataSide6FromFile,
         py::arg("filename"), py::arg("result"))

    // Обработка данных
    .def("interpolate_standarts", &VNACalibration::interpolateStandarts)
    .def("calculate_uncalibrated_s", &VNACalibration::calculateUncalibratedS)
    .def("calc_port_one_err", &VNACalibration::CalcPortOneErr)
    .def("calc_port_two_err", &VNACalibration::CalcPortTwoErr)
    .def("calc_12term_err", &VNACalibration::Calc12termErr)
    .def("apply_port_one_err", &VNACalibration::ApplyPortOneErr)
    .def("apply_port_two_err", &VNACalibration::ApplyPortTwoErr)
    .def("apply_12term_errors", &VNACalibration::Apply12termErrors)
    .def("get_interp_index", &VNACalibration::getInterpIndex,
        py::arg("ConstStepArr"), py::arg("point"))
	.def("linearInterpolate", &VNACalibration::linearInterpolate,
         py::arg("Xarr"), py::arg("Yarr"), py::arg("index"), py::arg("arg"))
    // Управление состоянием
    .def("get_status", &VNACalibration::get_status)

    // Результаты
    .def("write_calibrated_s", &VNACalibration::writeCalibratedS, py::arg("filename"))
    .def("get_calibrated_s", &VNACalibration::getCalibratedS)
    .def("get_calibration_frequencies", &VNACalibration::getCalibrationFrequencies)
    .def("get_uncalibrated_s", &VNACalibration::getUncalibratedS,
     py::arg("data"), py::arg("res"))

    // Отладка
    .def("debug_check", &VNACalibration::debugCheck, py::arg("number"));
}