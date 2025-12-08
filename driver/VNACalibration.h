#ifndef VNACALIBRATION_H
#define VNACALIBRATION_H

#include <iostream>
#include <fstream>
#include <vector>
#include <complex>
#include <string>
#include <sstream>
#include <algorithm>
#include <iomanip>
#include "VNAKitDevice.h"

using std::vector;
using std::complex;
using std::string;
using std::ifstream;
using std::ofstream;
using std::cout;
using std::cerr;
using std::endl;
using std::stringstream;
using std::stod;
using std::size_t;
using std::min;
using std::setw;
using std::fixed;
using std::setprecision;
using std::exception;
/*
struct VNAData {
    std::vector<double> frequency;
    std::vector<std::complex<double>> a0;  // Port 2
    std::vector<std::complex<double>> a3;  // Port 5
    std::vector<std::complex<double>> b0_3;  // Port 1 (transmission from 3)
    std::vector<std::complex<double>> b0_6;  // Port 1 (transmission from 6)
    std::vector<std::complex<double>> b3_3;  // Port 4 (transmission from 3)
    std::vector<std::complex<double>> b3_6;  // Port 4 (transmission from 6)
};*/

struct Smatrixs {
    std::vector<double> frequency;
    std::vector<std::complex<double>> S11;
    std::vector<std::complex<double>> S12;
    std::vector<std::complex<double>> S21;
    std::vector<std::complex<double>> S22;
};

struct flags {
    bool full_measurement_data_got = false,
        measurement_data_side3_got = false,
        measurement_data_side6_got = false,
        firstP_standart_data_got = false,
        secondP_standart_data_got = false,
        thru_standart_got = false,
        match2_standart_got = false,
        firstP_standart_interpolated = false,
        secondP_standart_interpolated = false,
        thru_standart_interpolated = false,
        match2_standart_interpolated = false,
        uncalibrates_S_calculated = false,
        port_one_errors_calculated = false,
        port_two_errors_calculated = false,
        error_12term_calculated = false,
        S11_calibrated = false,
        S22_calibrated = false,
        Smatrix_calibrated = false;
};

struct OSMstandart {
    std::vector<double> frequency;
    std::vector<std::complex<double>> S;
};

struct singlePortE {std::complex<double> ef00, ef11, detEf;};

    struct fullErrModel {
        //однопортовые по 1ому порту
        std::complex<double> ef00, ef11, ef10_01;
        //по 2ому порту
        std::complex<double> er33, er22, er23_32;

        //утечки
        std::complex<double> ef30, er03;

        //остальные двупортовые, вычисляемые по 1ому порту
        std::complex<double> ef22, ef10_32;
        //вычисляемые по 2ому порту
        std::complex<double> er11, er23_01;
    };


class VNACalibration {
private:
    // Измеренные данные
    VNAData rawData;
    Smatrixs uncalibratedS;
    Smatrixs calibratedS;
    //вспомогательные
    std::vector<double> calibrationFrequencies;
    int N = 0; //количество точек

    //предполагаем, что все стандарты сняты на одном диапазоне с одинаковым шагом
    VNAData OpenRaw, ShortRaw, MatchRaw;

    OSMstandart openStandartp1, openStandartp2;
    OSMstandart shortStandartp1, shortStandartp2;
    OSMstandart matchStandartp1, matchStandartp2;

    Smatrixs thruStandart;
    Smatrixs twoMatchStandart;

    std::vector<double> FrequenciesOfStandart;

    //стандарты, интерполированные на нужные частоты
    std::vector<std::complex<double>> openLInterpP1, openLInterpP2;
    std::vector<std::complex<double>> shortLInterpP1, shortLInterpP2;
    std::vector<std::complex<double>> matchLInterpP1, matchLInterpP2;
    Smatrixs thruLInterp;
    Smatrixs Match2LInterp;

    // Компоненты ошибок
    //однопортовые ошибки - аналогично для второго порта будет er33, er22, detEr
    //на каждую частоту однопортовые ошибки
    std::vector<singlePortE> firstPortE;
    std::vector<singlePortE> secondPortE;

    //полная модель ошибок (на каждую частоту)
    std::vector<fullErrModel> full12termErrors;

    struct flags status;

public:
    // Конструктор
    VNACalibration() : N(0) {};

    //получить статус экзмепляра калибровки
    struct flags get_status();

    // Загрузка измеренных данных и данный стандартов
    void loadMeasurementData(const VNAData& data);

    void loadPortOneCalibrationStandartData(const VNAData& Open, const VNAData& Short, const VNAData& Match);

    void loadPortTwoCalibrationStandartData(const VNAData& Open, const VNAData& Short, const VNAData& Match);

    void loadThruStandartData(const VNAData& thruData);

    void loadTwoMatchStandartData(const VNAData& match2Data);


    //загрузки с файлов
    void loadMeasurementDataSide3FromFile(const std::string& filename);
    void loadMeasurementDataSide6FromFile(const std::string& filename);

    void readDataSide3FromFile(const std::string& filename, VNAData& result);

    void readDataSide6FromFile(const std::string& filename, VNAData& result);
    void loadPortOneCalibrationStandartsFromFile(const std::string& openFile, const std::string& shortFile,
                                         const std::string& matchFile);
    void loadPortTwoCalibrationStandartsFromFile(const std::string& openFile, const std::string& shortFile,
                                     const std::string& matchFile);
    void loadThruStandart(const std::string& thruFile3, const std::string& thruFile6);
    void load2matchStandart(const std::string& match2File3, const std::string& match2File6);
    // Линейная интерполяция
    std::complex<double> linearInterpolate(std::vector<double>& Xarr, std::vector<std::complex<double>>& Yarr, int index, double arg);
    int getInterpIndex(std::vector<double>& ConstStepArr, double point);
    void interpolateStandarts();
    // Пересчет сырых данных в S-параметры
    Smatrixs getUncalibratedS(const VNAData& Data, Smatrixs& res);
    void calculateUncalibratedS();
    //получаем однопортовые компоненты ошибок
    void CalcPortOneErr();
    void CalcPortTwoErr();
    // Получаем двухпортовые компоненты ошибок
    void Calc12termErr();
    // Применить ошибки (откалибровать)
    void ApplyPortOneErr();
    void ApplyPortTwoErr();
    void Apply12termErrors();
    // Сохранение/загрузка коэффициентов ошибок
    void saveErrorTerms(const std::string& filename);
    void loadErrorTerms(const std::string& filename);
    void saveErrorTermsToDB();
    void loadErrorTermsFromDB();
    // Вывод результатов
    void writeCalibratedS(const std::string& filename);
    // тут всегда возвращается полная матрица - надо бы помнить какая калибровка
    Smatrixs getCalibratedS();
    // Вспомогательные методы
    std::vector<double> getCalibrationFrequencies() const;
    void debugCheck(int number);
};


#endif //VNACALIBRATION_H
