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

