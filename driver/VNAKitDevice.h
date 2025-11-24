#ifndef VNAKITDEVICE_H
#define VNAKITDEVICE_H

#include <iostream>
#include "VNAKit.h"
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
    explicit VNAKitDevice(const std::string& path);
    ~VNAKitDevice() = default;
    void init();
    void shutdown();
    void setConfigFile(const std::string& path);
    void applySettings();
    void validateSettings();
    VNAKit_RecordingSettings& getSettings();
    void setSettings(const VNAKit_RecordingSettings s);
    std::vector<double> getFrequencyVectorMHz();
    Measurement getResult();
    VNAKit_FrequencyLimits frequencyLimits() const;
    VNAKit_PowerLimits powerLimits() const;
    static std::string lastError(VNAKIT_RESULT result);

private:
    void check(VNAKIT_RESULT result, const std::string& where);
    void record();
};


#endif //VNAKITDEVICE_H