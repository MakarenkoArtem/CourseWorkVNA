#ifndef VNAKIT_H
#define VNAKIT_H

#ifdef __cplusplus
extern "C" {
#endif


#if defined(_WIN32) || defined(_WIN64)
  #define VNAKIT_API __declspec(dllimport)
#else
  #define VNAKIT_API extern
#endif


typedef int VNAKIT_RESULT;

#define VNAKIT_RES_SUCCESS 0
#define VNAKIT_RES_USERERR__NOT_INITIALIZED 1
#define VNAKIT_RES_USERERR__NO_SETTINGS_APPLIED 2
#define VNAKIT_RES_USERERR__NO_RECORDING 3
#define VNAKIT_RES_INPUTERR__OUT_OF_RANGE 4
#define VNAKIT_RES_INPUTERR__INVALID_SETTINGS 5
#define VNAKIT_RES_INPUTERR__BAD_RESULT_SIZE 6
#define VNAKIT_RES_INSTRUMENT_NOT_FOUND 7
#define VNAKIT_RES_DEVICE_ERROR 8
#define VNAKIT_RES_INIT_FAILED 9
#define VNAKIT_RES_BAD_CONFIG 10
#define VNAKIT_RES_GENERAL_ERROR 11


#define VNAKIT_MODE_ONE_PORT   0
#define VNAKIT_MODE_TWO_PORTS  1

#define VNAKIT_OUTFORMAT_MAT   0
#define VNAKIT_OUTFORMAT_CSV   1


typedef struct {
    double freqStartMHz;
    double freqStopMHz;
    int numFreqPoints;
} VNAKit_FrequencyRange;

typedef struct {
    VNAKit_FrequencyRange freqRange;
    double rbw_khz;
    double outputPower_dbm;
    int txtr;
    int mode;
} VNAKit_RecordingSettings;

typedef struct {
    double min_MHz;
    double max_MHz;
    double step_MHz;
    int nPointsMin;
    int nPointsMax;
} VNAKit_FrequencyLimits;

typedef struct {
    double min_dbm;
    double max_dbm;
    double step_dbm;
} VNAKit_PowerLimits;

typedef struct {
    double min_KHz;
    double max_KHz;
    double step_KHz;
} VNAKit_RbwLimits;

typedef struct {
    double real;
    double imag;
} VNAKit_Complex;

typedef struct {
    VNAKit_Complex **resultBuffer;
    int nRxTr;
    int nFrequenciesMeasured;
} VNAKit_RecordingResult;


VNAKIT_API VNAKIT_RESULT VNAKit_Init(void);
VNAKIT_API VNAKIT_RESULT VNAKit_Shutdown(void);

VNAKIT_API VNAKIT_RESULT VNAKit_SetConfigFile(const char *path);
VNAKIT_API VNAKIT_RESULT VNAKit_EnableLog(void);
VNAKIT_API VNAKIT_RESULT VNAKit_ClearConfigOverrides(void);
VNAKIT_API VNAKIT_RESULT VNAKit_OverrideConfigParams(void);

VNAKIT_API VNAKIT_RESULT VNAKit_ApplySettings(const VNAKit_RecordingSettings settings);
VNAKIT_API VNAKIT_RESULT VNAKit_ValidateSettings(const VNAKit_RecordingSettings settings);

VNAKIT_API VNAKIT_RESULT VNAKit_Record(void);
VNAKIT_API VNAKIT_RESULT VNAKit_WriteRecording(const char *output_dir, int format);

VNAKIT_API VNAKIT_RESULT VNAKit_EnterStandbyMode(void);

VNAKIT_API VNAKIT_RESULT VNAKit_InitResultStructure(VNAKit_RecordingResult *res, int nFreqs);
VNAKIT_API VNAKIT_RESULT VNAKit_GetRecordingResult(VNAKit_RecordingResult *res);
VNAKIT_API VNAKIT_RESULT VNAKit_GetResult_NoStruct(void *buffer);
VNAKIT_API VNAKIT_RESULT VNAKit_FreeResultStructure(VNAKit_RecordingResult *res);

VNAKIT_API VNAKIT_RESULT VNAKit_GetFreqVectorSizeDouble(int *size);
VNAKIT_API VNAKIT_RESULT VNAKit_GetFreqVector_MHz(int size, double *outBuffer);

VNAKIT_API VNAKit_FrequencyLimits VNAKit_GetFrequencyLimits(void);
VNAKIT_API VNAKIT_RESULT VNAKit_GetActualRBW_KHz(double *outVal);
VNAKIT_API VNAKit_PowerLimits VNAKit_GetPowerLimits(void);
VNAKIT_API VNAKit_RbwLimits VNAKit_GetRbwLimits(void);
VNAKIT_API int VNAKit_nMaxPoints_ForRbw(double rbw_KHz);
VNAKIT_API double VNAKit_MinRbwKhz_ForNPoints(int nPoints);

VNAKIT_API const char* VNAKit_GetLastErrString(void);

#ifdef __cplusplus
}
#endif

#endif // VNAKIT_H

#ifndef VNAKITDEVICE_H
#define VNAKITDEVICE_H



#include <vector>
#include <string>
#include <stdexcept>


struct Measurement{
    std::vector<VNAKit_Complex> a0;
    std::vector<VNAKit_Complex> a3;
    std::vector<VNAKit_Complex> b0;
    std::vector<VNAKit_Complex> b3;
    double startFreq;
    double stopFreq;
    int mode;
};

class VNAKitDevice {
     VNAKit_RecordingSettings settings;
public:
    VNAKitDevice();
    ~VNAKitDevice();
    void setConfigFile(const std::string& path);
    void applySettings();
    VNAKit_RecordingSettings& getSettings();
    void setSettings(const VNAKit_RecordingSettings s);
    std::vector<double> getFrequencyVectorMHz();
    Measurement getResult();
    VNAKit_FrequencyLimits frequencyLimits() const;
    VNAKit_PowerLimits powerLimits() const;
    static std::string lastError();
private:
    void check(VNAKIT_RESULT result, const std::string& where);
    void record();
};


#endif //VNAKITDEVICE_H


#include <iostream>
#include <algorithm>

VNAKitDevice::VNAKitDevice() {
  std::cout<<VNAKit_Init();
    if (VNAKit_Init() != VNAKIT_RES_SUCCESS)
        throw std::runtime_error("VNAKit_Init failed");
}

VNAKitDevice::~VNAKitDevice() {
    VNAKit_Shutdown();
}

void VNAKitDevice::setConfigFile(const std::string& path) {
    check(VNAKit_SetConfigFile(path.c_str()), "SetConfigFile");
}

void VNAKitDevice::applySettings() {
    check(VNAKit_ValidateSettings(settings), "ValidateSettings");
    check(VNAKit_ApplySettings(settings), "ApplySettings");
}

VNAKit_RecordingSettings& VNAKitDevice::getSettings(){
    return settings;
}

void VNAKitDevice::setSettings(const VNAKit_RecordingSettings s){
    settings = s;
}

void VNAKitDevice::record() {
    check(VNAKit_Record(), "Record");
}

std::vector<double> VNAKitDevice::getFrequencyVectorMHz() {
    int size = 0;
    check(VNAKit_GetFreqVectorSizeDouble(&size), "GetFreqVectorSizeDouble");
    std::vector<double> freqs(size);
    check(VNAKit_GetFreqVector_MHz(size, freqs.data()), "GetFreqVector_MHz");
    return freqs;
}

Measurement VNAKitDevice::getResult() {
    Measurement measurement{};
    int nFreqs = 0;
    check(VNAKit_GetFreqVectorSizeDouble(&nFreqs), "GetFreqVectorSizeDouble");
    VNAKit_RecordingSettings currSettings = getSettings();
    record();
    VNAKit_RecordingResult result{};
    check(VNAKit_InitResultStructure(&result, nFreqs), "InitResultStructure");
    check(VNAKit_GetRecordingResult(&result), "GetRecordingResult");
   	if (currSettings.txtr == 3){
    	measurement.a0.assign(result.resultBuffer[1], result.resultBuffer[1] + nFreqs);
    	measurement.b0.assign(result.resultBuffer[0], result.resultBuffer[0] + nFreqs);
    }
    else{
    	measurement.a3.assign(result.resultBuffer[4], result.resultBuffer[4] + nFreqs);
    	measurement.b3.assign(result.resultBuffer[3], result.resultBuffer[3] + nFreqs);
    }
    if (currSettings.mode == 1) {
      if (currSettings.txtr == 3)
    		currSettings.txtr = 6;
      else
        	currSettings.txtr = 3;
    	setSettings(currSettings);
    	record();
    	check(VNAKit_InitResultStructure(&result, nFreqs), "InitResultStructure");
    	check(VNAKit_GetRecordingResult(&result), "GetRecordingResult");
   		if (currSettings.txtr == 3){
    		measurement.a0.assign(result.resultBuffer[1], result.resultBuffer[1] + nFreqs);
    		measurement.b0.assign(result.resultBuffer[0], result.resultBuffer[0] + nFreqs);
    	}
    	else{
    		measurement.a3.assign(result.resultBuffer[4], result.resultBuffer[4] + nFreqs);
    		measurement.b3.assign(result.resultBuffer[3], result.resultBuffer[3] + nFreqs);
    	}
    	VNAKit_FreeResultStructure(&result);
    }
    measurement.startFreq = currSettings.freqRange.freqStartMHz;
    measurement.stopFreq = currSettings.freqRange.freqStopMHz;
    measurement.mode = currSettings.mode;
    return measurement;
}

VNAKit_FrequencyLimits VNAKitDevice::frequencyLimits() const {
    return VNAKit_GetFrequencyLimits();
}

VNAKit_PowerLimits VNAKitDevice::powerLimits() const {
    return VNAKit_GetPowerLimits();
}

std::string VNAKitDevice::lastError() {
    const char* err = VNAKit_GetLastErrString();
    return err ? std::string(err) : "Unknown error";
}

void VNAKitDevice::check(VNAKIT_RESULT result, const std::string& where) {
    if (result != VNAKIT_RES_SUCCESS)
        throw std::runtime_error("Error: " + where);
}


// main.cpp

#include <iostream>
#include <thread>
#include <memory>

int main() {
    try {
        // Создание экземпляра устройства
        VNAKitDevice vna;

        vna.setConfigFile("vnakit.conf");
        // Получение текущих настроек
        auto settings = vna.getSettings();

        // Настройка диапазона частот (в МГц)
        settings.freqRange.freqStartMHz = 100.0;   // Начальная частота
        settings.freqRange.freqStopMHz = 2000.0;   // Конечная частота
        settings.freqRange.numFreqPoints = 101;          // Количество точек

        // Режим измерения: 0 — одиночный, 1 — дифференциальный (если поддерживается)
        settings.mode = 0;

        // TXTR: 3 или 6 — зависит от конфигурации портов (см. документацию VNAKit)
        settings.txtr = 3;

        // Применение настроек
        vna.setSettings(settings);
        vna.applySettings();

        // Выполнение измерения
        Measurement result = vna.getResult();

        // Вывод информации
        std::cout << "Измерение выполнено:\n";
        std::cout << "  Диапазон частот: " << result.startFreq << " – " << result.stopFreq << " МГц\n";
        std::cout << "  Режим: " << result.mode << "\n";
        std::cout << "  Длина вектора a0: " << result.a0.size() << "\n";
        std::cout << "  Длина вектора b0: " << result.b0.size() << "\n";
        std::cout << "  Длина вектора a3: " << result.a3.size() << "\n";
        std::cout << "  Длина вектора b3: " << result.b3.size() << "\n";

        // Пример вывода первых значений (если есть)
        if (!result.a0.empty()) {
            std::cout << "  Первое значение a0: " << result.a0[0].real << "\n";
        }
        if (!result.b0.empty()) {
            std::cout << "  Первое значение b0: " << result.b0[0].real << "\n";
        }

    } catch (const std::exception& e) {
        std::cerr << "Ошибка: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}

