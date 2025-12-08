#include "VNAKitDevice.h"


VNAKitDevice::VNAKitDevice(const std::string& path) {
	check(VNAKit_SetConfigFile(path.c_str()), "SetConfigFile");
}

void VNAKitDevice::shutdown() {
	check(VNAKit_Shutdown(), "VNAKit_Shutdown");
}

void VNAKitDevice::init(){
	check(VNAKit_Init(), "VNAKit_Init");
}

void VNAKitDevice::setConfigFile(const std::string& path) {
    check(VNAKit_SetConfigFile(path.c_str()), "SetConfigFile");
}

void VNAKitDevice::validateSettings() {
	check(VNAKit_ValidateSettings(settings), "VNAKit_VerifyConfig");
}

void VNAKitDevice::applySettings() {
    check(VNAKit_ApplySettings(settings), "ApplySettings");
}

VNAKit_RecordingSettings& VNAKitDevice::getSettings(){
    return settings;
}

void VNAKitDevice::setSettings(const VNAKit_RecordingSettings s){
  	if (settings.freqRange.freqStartMHz != s.freqRange.freqStartMHz && settings.freqRange.freqStopMHz != s.freqRange.freqStopMHz
      && settings.freqRange.numFreqPoints != s.freqRange.numFreqPoints
      && settings.rbw_khz != s.rbw_khz && settings.outputPower_dbm != s.outputPower_dbm
      && settings.txtr != s.txtr && settings.mode != s.mode)
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

VNAData VNAKitDevice::getResult() {
	record();
    VNAData measurement{};
    VNAKit_RecordingSettings currSettings = getSettings();
    auto nFreqs = currSettings.freqRange.numFreqPoints;
    VNAKit_RecordingResult result{};
    VNAKit_InitResultStructure(&result, nFreqs);
    check(VNAKit_GetRecordingResult(&result), "GetRecordingResult");
    if (currSettings.mode == VNAKIT_MODE_ONE_PORT){
    	if (currSettings.txtr == 3){
    		copyVNAComplexToComplexVector(measurement.a0, result.resultBuffer[1], nFreqs);
            copyVNAComplexToComplexVector(measurement.b0_3, result.resultBuffer[0], nFreqs);
            copyVNAComplexToComplexVector(measurement.b3_3, result.resultBuffer[3], nFreqs);
            std::fill(measurement.a3.begin(), measurement.a3.begin() + nFreqs, 1);
            std::fill(measurement.b3_6.begin(), measurement.b3_6.begin() + nFreqs, 1);
            std::fill(measurement.b0_6.begin(), measurement.b0_6.begin() + nFreqs, 1);
    	}
    	else{
          	copyVNAComplexToComplexVector(measurement.a3, result.resultBuffer[4], nFreqs);
    		copyVNAComplexToComplexVector(measurement.b0_6, result.resultBuffer[0], nFreqs);
            copyVNAComplexToComplexVector(measurement.b3_6, result.resultBuffer[3], nFreqs);
            std::fill(measurement.a0.begin(), measurement.a3.begin() + nFreqs, 1);
            std::fill(measurement.b0_3.begin(), measurement.b0_3.begin() + nFreqs, 1);
            std::fill(measurement.b3_3.begin(), measurement.b3_3.begin() + nFreqs, 1);
    	}
    }
	else{
    	if (currSettings.txtr == 3){
    		copyVNAComplexToComplexVector(measurement.a0, result.resultBuffer[1], nFreqs);
            copyVNAComplexToComplexVector(measurement.b0_3, result.resultBuffer[0], nFreqs);
            copyVNAComplexToComplexVector(measurement.b3_3, result.resultBuffer[3], nFreqs);
			currSettings.txtr = 6;
            setSettings(currSettings);
            record();
    		VNAKit_InitResultStructure(&result, nFreqs);
    		check(VNAKit_GetRecordingResult(&result), "GetRecordingResult");
            copyVNAComplexToComplexVector(measurement.a3, result.resultBuffer[4], nFreqs);
    		copyVNAComplexToComplexVector(measurement.b0_6, result.resultBuffer[0], nFreqs);
            copyVNAComplexToComplexVector(measurement.b3_6, result.resultBuffer[3], nFreqs);
    	}
        else{
        	copyVNAComplexToComplexVector(measurement.a3, result.resultBuffer[4], nFreqs);
    		copyVNAComplexToComplexVector(measurement.b0_6, result.resultBuffer[0], nFreqs);
            copyVNAComplexToComplexVector(measurement.b3_6, result.resultBuffer[3], nFreqs);
            currSettings.txtr = 3;
            setSettings(currSettings);
            record();
    		VNAKit_InitResultStructure(&result, nFreqs);
    		check(VNAKit_GetRecordingResult(&result), "GetRecordingResult");
            copyVNAComplexToComplexVector(measurement.a0, result.resultBuffer[1], nFreqs);
            copyVNAComplexToComplexVector(measurement.b0_3, result.resultBuffer[0], nFreqs);
            copyVNAComplexToComplexVector(measurement.b3_3, result.resultBuffer[3], nFreqs);
        }
    }
    measurement.frequency.resize(nFreqs);
    VNAKit_GetFreqVector_MHz(nFreqs, measurement.frequency.data());
    return measurement;
}

VNAKit_FrequencyLimits VNAKitDevice::frequencyLimits() const {
    return VNAKit_GetFrequencyLimits();
}

VNAKit_PowerLimits VNAKitDevice::powerLimits() const {
    return VNAKit_GetPowerLimits();
}

std::string VNAKitDevice::lastError(VNAKIT_RESULT result) {
    std::string err = VNAKit_GetLastErrString();
    if (err == "(none)"){
        switch (result){
          case VNAKIT_RES_USERERR__NOT_INITIALIZED:
            err = "Not initialized";
            break;
          case VNAKIT_RES_USERERR__NO_SETTINGS_APPLIED:
            err = "No settings applied";
           	break;
          case VNAKIT_RES_USERERR__NO_RECORDING:
            err = "No recording";
            break;
          case VNAKIT_RES_INPUTERR__OUT_OF_RANGE:
            err = "Input out of range";
            break;
          case VNAKIT_RES_INPUTERR__INVALID_SETTINGS:
            err = "Invalid settings";
            break;
          case VNAKIT_RES_INPUTERR__BAD_RESULT_SIZE:
            err = "Bad result size";
            break;
          case VNAKIT_RES_INSTRUMENT_NOT_FOUND:
            err = "Instruction not found";
            break;
          case VNAKIT_RES_DEVICE_ERROR:
            err = "Device error";
            break;
          case VNAKIT_RES_INIT_FAILED:
            err = "Init failed";
            break;
          case VNAKIT_RES_BAD_CONFIG:
            err = "Bad configuration";
            break;
          case VNAKIT_RES_GENERAL_ERROR:
            err = "General error";
            break;
        }
        err += " " + std::to_string(result);
    }
    return err;
}

void VNAKitDevice::check(VNAKIT_RESULT result, const std::string& where) {
    if (result != VNAKIT_RES_SUCCESS) {
    	throw std::runtime_error(lastError(result) + " (in func " + where + ")");
    }
}

void VNAKitDevice::copyVNAComplexToComplexVector(
    std::vector<std::complex<double>>& output,
    const VNAKit_Complex* input,
    size_t count
) {
    if (input == nullptr) {
        output.clear();
        return;
    }

    output.resize(count);
    std::transform(
        input,
        input + count,
        output.begin(),
        [](const VNAKit_Complex& c) {
            return std::complex<double>(c.real, c.imag);
        }
    );
}