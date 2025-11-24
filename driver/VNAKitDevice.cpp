#include "VNAKitDevice.h"
#include <iostream>
#include <algorithm>


VNAKitDevice::VNAKitDevice() {
    VNAKit_SetConfigFile("./vnakit.conf");

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

void VNAKitDevice::setQueue(std::shared_ptr<ThreadSafeQueue<Measurement>> q) {
	queue_ = std::move(q);
}

