#ifndef VNAKITDEVICE_H
#define VNAKITDEVICE_H

#include "VNAKit.h"
#include <vector>
#include <string>
#include <complex>
#include <algorithm>
#include <stdexcept>


struct VNAData {
    std::vector<double> frequency;
    std::vector<std::complex<double>> a0;  // Port 2
    std::vector<std::complex<double>> a3;  // Port 5
    std::vector<std::complex<double>> b0_3;  // Port 1 (transmission from 3)
    std::vector<std::complex<double>> b0_6;  // Port 1 (transmission from 6)
    std::vector<std::complex<double>> b3_3;  // Port 4 (transmission from 3)
    std::vector<std::complex<double>> b3_6;  // Port 4 (transmission from 6)
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
    VNAData getResult();
    VNAKit_FrequencyLimits frequencyLimits() const;
    VNAKit_PowerLimits powerLimits() const;
    static std::string lastError(VNAKIT_RESULT result);
private:
    void check(VNAKIT_RESULT result, const std::string& where);
    void record();
    void copyVNAComplexToComplexVector(
        std::vector<std::complex<double>>& output,
        const VNAKit_Complex* input,
        size_t count
        );
};


#endif //VNAKITDEVICE_H