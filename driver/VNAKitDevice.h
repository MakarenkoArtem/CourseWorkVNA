#ifndef VNAKITDEVICE_H
#define VNAKITDEVICE_H

#include "VNAKit.h"
#include "TreadSafeQueue.h"
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
     std::shared_ptr<ThreadSafeQueue<Measurement>> queue_;
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
    void setQueue(std::shared_ptr<ThreadSafeQueue<Measurement>> q);
private:
    void check(VNAKIT_RESULT result, const std::string& where);
    void record();
};


#endif //VNAKITDEVICE_H
