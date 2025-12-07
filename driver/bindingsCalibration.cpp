// bindings.cpp (фрагмент для VNACalibration)

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/complex.h>
#include "VNAKitDevice.h"
#include "VNACalibration.h"

namespace py = pybind11;

PYBIND11_MODULE(vnakit_calibretion, m) {
// Экспорт всех структур (включая OSMstandart!)
py::class_<VNAData>(m, "VNAData")
    .def(py::init<>())
    .def_readwrite("frequency", &VNAData::frequency)
    .def_readwrite("a0", &VNAData::a0)
    .def_readwrite("a3", &VNAData::a3)
    .def_readwrite("b0_3", &VNAData::b0_3)
    .def_readwrite("b0_6", &VNAData::b0_6)
    .def_readwrite("b3_3", &VNAData::b3_3)
    .def_readwrite("b3_6", &VNAData::b3_6);

py::class_<Smatrixs>(m, "Smatrixs")
    .def(py::init<>())
    .def_readwrite("frequency", &Smatrixs::frequency)
    .def_readwrite("S11", &Smatrixs::S11)
    .def_readwrite("S12", &Smatrixs::S12)
    .def_readwrite("S21", &Smatrixs::S21)
    .def_readwrite("S22", &Smatrixs::S22);

// === НОВАЯ СТРУКТУРА: OSMstandart ===
py::class_<VNACalibration::OSMstandart>(m, "OSMstandart")
    .def(py::init<>())
    .def_readwrite("frequency", &VNACalibration::OSMstandart::frequency)
    .def_readwrite("S", &VNACalibration::OSMstandart::S);

// === Структура флагов ===
py::class_<VNACalibration::flags>(m, "CalibrationFlags")
    .def(py::init<>())
    .def_readonly("full_measurement_data_got", &VNACalibration::flags::full_measurement_data_got)
    .def_readonly("measurement_data_side3_got", &VNACalibration::flags::measurement_data_side3_got)
    .def_readonly("measurement_data_side6_got", &VNACalibration::flags::measurement_data_side6_got)
    .def_readonly("firstP_standart_data_got", &VNACalibration::flags::firstP_standart_data_got)
    .def_readonly("secondP_standart_data_got", &VNACalibration::flags::secondP_standart_data_got)
    .def_readonly("thru_standart_got", &VNACalibration::flags::thru_standart_got)
    .def_readonly("match2_standart_got", &VNACalibration::flags::match2_standart_got)
    .def_readonly("firstP_standart_interpolated", &VNACalibration::flags::firstP_standart_interpolated)
    .def_readonly("secondP_standart_interpolated", &VNACalibration::flags::secondP_standart_interpolated)
    .def_readonly("thru_standart_interpolated", &VNACalibration::flags::thru_standart_interpolated)
    .def_readonly("match2_standart_interpolated", &VNACalibration::flags::match2_standart_interpolated)
    .def_readonly("uncalibrates_S_calculated", &VNACalibration::flags::uncalibrates_S_calculated)
    .def_readonly("port_one_errors_calculated", &VNACalibration::flags::port_one_errors_calculated)
    .def_readonly("port_two_errors_calculated", &VNACalibration::flags::port_two_errors_calculated)
    .def_readonly("error_12term_calculated", &VNACalibration::flags::error_12term_calculated)
    .def_readonly("S11_calibrated", &VNACalibration::flags::S11_calibrated)
    .def_readonly("S22_calibrated", &VNACalibration::flags::S22_calibrated)
    .def_readonly("Smatrix_calibrated", &VNACalibration::flags::Smatrix_calibrated);

// === Основные структуры ошибок ===
py::class_<VNACalibration::singlePortE>(m, "SinglePortError")
    .def(py::init<>())
    .def_readwrite("ef00", &VNACalibration::singlePortE::ef00)
    .def_readwrite("ef11", &VNACalibration::singlePortE::ef11)
    .def_readwrite("det_ef", &VNACalibration::singlePortE::detEf);

py::class_<VNACalibration::fullErrModel>(m, "FullErrorModel")
    .def(py::init<>())
    // Однопортовые по 1-му порту
    .def_readwrite("ef00", &VNACalibration::fullErrModel::ef00)
    .def_readwrite("ef11", &VNACalibration::fullErrModel::ef11)
    .def_readwrite("ef10_01", &VNACalibration::fullErrModel::ef10_01)
    // По 2-му порту
    .def_readwrite("er33", &VNACalibration::fullErrModel::er33)
    .def_readwrite("er22", &VNACalibration::fullErrModel::er22)
    .def_readwrite("er23_32", &VNACalibration::fullErrModel::er23_32)
    // Утечки
    .def_readwrite("ef30", &VNACalibration::fullErrModel::ef30)
    .def_readwrite("er03", &VNACalibration::fullErrModel::er03)
    // Двупортовые
    .def_readwrite("ef22", &VNACalibration::fullErrModel::ef22)
    .def_readwrite("ef10_32", &VNACalibration::fullErrModel::ef10_32)
    .def_readwrite("er11", &VNACalibration::fullErrModel::er11)
    .def_readwrite("er23_01", &VNACalibration::fullErrModel::er23_01);

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

    // Управление состоянием
    .def("get_status", &VNACalibration::get_status)

    // Результаты
    .def("write_calibrated_s", &VNACalibration::writeCalibratedS, py::arg("filename"))
    .def("get_calibrated_s", &VNACalibration::getCalibratedS)
    .def("get_calibration_frequencies", &VNACalibration::getCalibrationFrequencies)

    // Отладка
    .def("debug_check", &VNACalibration::debugCheck, py::arg("number"));
}