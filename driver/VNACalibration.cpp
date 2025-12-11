#include "VNACalibration.h"

    //получить статус экзмепляра калибровки
    flags VNACalibration::get_status() {
        return status;
    }

    // Загрузка измеренных данных и данный стандартов
    void VNACalibration::loadMeasurementData(const VNAData& data)
    {
        rawData = data;
        
        N = rawData.frequency.size();
        calibrationFrequencies = rawData.frequency;
        status.full_measurement_data_got = true;
    }

    void VNACalibration::loadPortOneCalibrationStandartData(const VNAData& Open, const VNAData& Short, const VNAData& Match)
    {
        OpenRaw.frequency = Open.frequency; OpenRaw.a0 = Open.a0; OpenRaw.b0_3 = Open.b0_3; OpenRaw.b3_3 = Open.b3_3;
        ShortRaw.frequency = Short.frequency; ShortRaw.a0 = Short.a0; ShortRaw.b0_3 = Short.b0_3; ShortRaw.b3_3 = Short.b3_3;
        MatchRaw.frequency = Match.frequency; MatchRaw.a0 = Match.a0; MatchRaw.b0_3 = Match.b0_3; MatchRaw.b3_3 = Match.b3_3;

        openStandartp1 = OSMstandart();
        shortStandartp1 = OSMstandart();
        matchStandartp1 = OSMstandart();
        
        int Nstd = OpenRaw.frequency.size();
        //по нормальному проверку на одинаковость файлов по длине, но нее
        for (int i = 0; i < Nstd; i++)
        {
            openStandartp1.frequency.push_back(OpenRaw.frequency[i]);
            shortStandartp1.frequency.push_back(ShortRaw.frequency[i]);
            matchStandartp1.frequency.push_back(MatchRaw.frequency[i]);

            openStandartp1.S.push_back(OpenRaw.b0_3[i] / OpenRaw.a0[i]);
            shortStandartp1.S.push_back(ShortRaw.b0_3[i] / ShortRaw.a0[i]);
            matchStandartp1.S.push_back(MatchRaw.b0_3[i] / MatchRaw.a0[i]);

            FrequenciesOfStandart.push_back(OpenRaw.frequency[i]);
        }

        status.firstP_standart_data_got = true;
    }

    void VNACalibration::loadPortTwoCalibrationStandartData(const VNAData& Open, const VNAData& Short, const VNAData& Match) {

        if (Open.frequency.size() != Short.frequency.size() || Open.frequency.size() != Match.frequency.size()) {
            std::cerr << "нессответствует размер массивов" << std::endl;
            return;
        }
    
        VNAData OpenRaw6, ShortRaw6, MatchRaw6;
        OpenRaw6.frequency = Open.frequency;
        OpenRaw6.a3 = Open.a3;
        OpenRaw6.b3_6 = Open.b3_6;
    
        ShortRaw6.frequency = Short.frequency;
        ShortRaw6.a3 = Short.a3;
        ShortRaw6.b3_6 = Short.b3_6;
        
        MatchRaw6.frequency = Match.frequency;
        MatchRaw6.a3 = Match.a3;
        MatchRaw6.b3_6 = Match.b3_6;
    
        openStandartp2 = OSMstandart{};
        shortStandartp2 = OSMstandart{};
        matchStandartp2 = OSMstandart{};
    
        size_t Nstd = Open.frequency.size();
        for (size_t i = 0; i < Nstd; ++i) {
            openStandartp2.frequency.push_back(OpenRaw6.frequency[i]);
            shortStandartp2.frequency.push_back(ShortRaw6.frequency[i]);
            matchStandartp2.frequency.push_back(MatchRaw6.frequency[i]);
        
            openStandartp2.S.push_back(OpenRaw6.b3_6[i] / OpenRaw6.a3[i]);
            shortStandartp2.S.push_back(ShortRaw6.b3_6[i] / ShortRaw6.a3[i]);
            matchStandartp2.S.push_back(MatchRaw6.b3_6[i] / MatchRaw6.a3[i]);
        
            if (FrequenciesOfStandart.empty()) {
                FrequenciesOfStandart.push_back(OpenRaw6.frequency[i]);
            }
        }
        status.secondP_standart_data_got = true;
    }

    void VNACalibration::loadThruStandartData(const VNAData& thruData) {
        if (!status.full_measurement_data_got) {
            std::cerr << "Measurement data not loaded! Call loadMeasurementData() first." << std::endl;
            return;
        }
    
        getUncalibratedS(thruData, thruStandart);
        status.thru_standart_got = true;
    }

    void VNACalibration::loadTwoMatchStandartData(const VNAData& match2Data) {
        if (!status.full_measurement_data_got) {
            std::cerr << "Measurement data not loaded! Call loadMeasurementData() first." << std::endl;
            return;
        }
    
        getUncalibratedS(match2Data, twoMatchStandart);
        status.match2_standart_got = true;
    }


    //загрузки с файлов
    void VNACalibration::loadMeasurementDataSide3FromFile(const std::string& filename)
    {
        std::ifstream file(filename);
        std::string line;
        
        rawData.frequency.clear();
        rawData.a0.clear();
        rawData.b0_3.clear();
        rawData.b3_3.clear();
    
        // Читаем все строки и находим первую с числовыми данными
        std::vector<std::string> lines;
        while (getline(file, line)) {
            lines.push_back(line);
        }
        file.close(); // Закрываем файл здесь

        bool dataStarted = false;
    
        for (const auto& currentLine : lines) {
            if (currentLine.empty()) continue;
        
            if (!dataStarted) {
                // Пропускаем комментарии и заголовки
                if (currentLine[0] == '#') continue;
                if (currentLine.find("FREQUENCY") != std::string::npos) continue;
            
                // Проверяем, начинается ли строка с числа (возможно с минусом или точкой)
                if (isdigit(currentLine[0]) || currentLine[0] == '-' || currentLine[0] == '.') {
                    dataStarted = true;
                } else {
                    continue; // Пропускаем не-числовые строки до начала данных
                }
            }
        
            // Парсим строку с данными
            if (dataStarted) {
                std::stringstream ss(currentLine);
                std::vector<double> values;
                double value;
            
                while (ss >> value) {
                    values.push_back(value);
                }
            
                if (values.size() >= 11) {
                    rawData.frequency.push_back(values[0]);
                    rawData.b0_3.push_back({values[1], values[2]});
                    rawData.a0.push_back({values[3], values[4]});
                    rawData.b3_3.push_back({values[7], values[8]});
                }
            }
        }
        N = rawData.frequency.size();
        calibrationFrequencies = rawData.frequency;
        status.measurement_data_side3_got = true;
        if (status.measurement_data_side3_got && status.measurement_data_side6_got) status.full_measurement_data_got = true;
    }

    void VNACalibration::loadMeasurementDataSide6FromFile(const std::string& filename)
    {
        double firstfr = rawData.frequency[0], lastfr = rawData.frequency.back();

        std::ifstream file(filename);
        std::string line;
        
        rawData.frequency.clear();
        rawData.a3.clear();
        rawData.b0_6.clear();
        rawData.b3_6.clear();
    
        // Читаем все строки и находим первую с числовыми данными
        std::vector<std::string> lines;
        while (getline(file, line)) {
            lines.push_back(line);
        }
        file.close(); // Закрываем файл здесь

        bool dataStarted = false;
    
        for (const auto& currentLine : lines) {
            if (currentLine.empty()) continue;
        
            if (!dataStarted) {
                // Пропускаем комментарии и заголовки
                if (currentLine[0] == '#') continue;
                if (currentLine.find("FREQUENCY") != std::string::npos) continue;
            
                // Проверяем, начинается ли строка с числа (возможно с минусом или точкой)
                if (isdigit(currentLine[0]) || currentLine[0] == '-' || currentLine[0] == '.') {
                    dataStarted = true;
                } else {
                    continue; // Пропускаем не-числовые строки до начала данных
                }
            }
        
            // Парсим строку с данными
            if (dataStarted) {
                std::stringstream ss(currentLine);
                std::vector<double> values;
                double value;
            
                while (ss >> value) {
                    values.push_back(value);
                }
            
                if (values.size() >= 11) {
                    rawData.frequency.push_back(values[0]);
                    rawData.b0_6.push_back({values[1], values[2]});
                    rawData.b3_6.push_back({values[7], values[8]});
                    rawData.a3.push_back({values[9], values[10]});
                }
            }
        }

        int M = rawData.frequency.size();
        if ((N != 0 && M != N) || (rawData.frequency[0] != firstfr) || (rawData.frequency.back() != lastfr))
        {
            std::cerr << "несоответствие файлов";
            return;
        }

        status.measurement_data_side6_got = true;
        calibrationFrequencies = rawData.frequency;
        if (status.measurement_data_side3_got && status.measurement_data_side6_got) status.full_measurement_data_got = true;
    }
    


    void VNACalibration::readDataSide3FromFile(const std::string& filename, VNAData& result)
    {
        std::ifstream file(filename);
        std::string line;
        
        result.frequency.clear();
        result.a0.clear();
        result.b0_3.clear();
        result.b3_3.clear();
    
        // Читаем все строки и находим первую с числовыми данными
        std::vector<std::string> lines;
        while (getline(file, line)) {
            lines.push_back(line);
        }
        file.close(); // Закрываем файл здесь

        bool dataStarted = false;
    
        for (const auto& currentLine : lines) {
            if (currentLine.empty()) continue;
        
            if (!dataStarted) {
                // Пропускаем комментарии и заголовки
                if (currentLine[0] == '#') continue;
                if (currentLine.find("FREQUENCY") != std::string::npos) continue;
            
                // Проверяем, начинается ли строка с числа (возможно с минусом или точкой)
                if (isdigit(currentLine[0]) || currentLine[0] == '-' || currentLine[0] == '.') {
                    dataStarted = true;
                } else {
                    continue; // Пропускаем не-числовые строки до начала данных
                }
            }
        
            // Парсим строку с данными
            if (dataStarted) {
                std::stringstream ss(currentLine);
                std::vector<double> values;
                double value;
            
                while (ss >> value) {
                    values.push_back(value);
                }
            
                if (values.size() >= 11) {
                    result.frequency.push_back(values[0]);
                    result.b0_3.push_back({values[1], values[2]});
                    result.a0.push_back({values[3], values[4]});
                    result.b3_3.push_back({values[7], values[8]});
                }
            }
        }
    }

    void VNACalibration::readDataSide6FromFile(const std::string& filename, VNAData& result)
    {
        ifstream file(filename);
        string line;  
        
        result.frequency.clear();
        result.a3.clear();
        result.b0_6.clear();
        result.b3_6.clear();
    
        // Читаем все строки и находим первую с числовыми данными
        vector<string> lines;
        while (getline(file, line)) {
            lines.push_back(line);
        }
        file.close(); // Закрываем файл здесь

        bool dataStarted = false;
    
        for (const auto& currentLine : lines) {
            if (currentLine.empty()) continue;
        
            if (!dataStarted) {
                // Пропускаем комментарии и заголовки
                if (currentLine[0] == '#') continue;
                if (currentLine.find("FREQUENCY") != string::npos) continue;
            
                // Проверяем, начинается ли строка с числа (возможно с минусом или точкой)
                if (isdigit(currentLine[0]) || currentLine[0] == '-' || currentLine[0] == '.') {
                    dataStarted = true;
                } else {
                    continue; // Пропускаем не-числовые строки до начала данных
                }
            }
        
            // Парсим строку с данными
            if (dataStarted) {
                stringstream ss(currentLine);
                vector<double> values;
                double value;
            
                while (ss >> value) {
                    values.push_back(value);
                }
            
                if (values.size() >= 11) {
                    result.frequency.push_back(values[0]);
                    result.b0_6.push_back({values[1], values[2]});
                    result.a3.push_back({values[9], values[10]});
                    result.b3_6.push_back({values[7], values[8]});
                }
            }
        }
    }



    void VNACalibration::loadPortOneCalibrationStandartsFromFile(const string& openFile, const string& shortFile,
                                         const string& matchFile)
    {
        readDataSide3FromFile(openFile, OpenRaw);
        readDataSide3FromFile(shortFile, ShortRaw);
        readDataSide3FromFile(matchFile, MatchRaw);

        openStandartp1 = OSMstandart();
        shortStandartp1 = OSMstandart();
        matchStandartp1 = OSMstandart();
        
        int Nstd = OpenRaw.frequency.size();
        //по нормальному проверку на одинаковость файлов по длине, но нее
        for (int i = 0; i < Nstd; i++)
        {
            openStandartp1.frequency.push_back(OpenRaw.frequency[i]);
            shortStandartp1.frequency.push_back(ShortRaw.frequency[i]);
            matchStandartp1.frequency.push_back(MatchRaw.frequency[i]);

            openStandartp1.S.push_back(OpenRaw.b0_3[i] / OpenRaw.a0[i]);          
            shortStandartp1.S.push_back(ShortRaw.b0_3[i] / ShortRaw.a0[i]);
            matchStandartp1.S.push_back(MatchRaw.b0_3[i] / MatchRaw.a0[i]);

            FrequenciesOfStandart.push_back(OpenRaw.frequency[i]);
        }

        status.firstP_standart_data_got = true;
    }
    
    void VNACalibration::loadPortTwoCalibrationStandartsFromFile(const string& openFile, const string& shortFile,
                                     const string& matchFile)
    {
        VNAData OpenRaw6, ShortRaw6, MatchRaw6;

        readDataSide6FromFile(openFile, OpenRaw6);
        readDataSide6FromFile(shortFile, ShortRaw6);
        readDataSide6FromFile(matchFile, MatchRaw6);

        openStandartp2 = OSMstandart();
        shortStandartp2 = OSMstandart();
        matchStandartp2 = OSMstandart();
    
        int Nstd = OpenRaw6.frequency.size();
        if (Nstd != openStandartp1.frequency.size()) {
            cerr << "файлы несоответсвенные" << endl; 
            return;
        }

        for (int i = 0; i < Nstd; i++)
        {
            openStandartp2.frequency.push_back(OpenRaw6.frequency[i]);
            shortStandartp2.frequency.push_back(ShortRaw6.frequency[i]);
            matchStandartp2.frequency.push_back(MatchRaw6.frequency[i]);

            // ЗДЕСЬ ИЗМЕНЕНИЕ: используем правильные измерения для порта 6
            openStandartp2.S.push_back(OpenRaw6.b3_6[i] / OpenRaw6.a3[i]);          
            shortStandartp2.S.push_back(ShortRaw6.b3_6[i] / ShortRaw6.a3[i]);
            matchStandartp2.S.push_back(MatchRaw6.b3_6[i] / MatchRaw6.a3[i]);

            if (FrequenciesOfStandart.size() == 0) 
                FrequenciesOfStandart.push_back(OpenRaw6.frequency[i]);
        }

        status.secondP_standart_data_got = true;
    }


    void VNACalibration::loadThruStandart(const string& thruFile3, const string& thruFile6)
    {
        VNAData rawThru;
        readDataSide3FromFile(thruFile3,rawThru);
        readDataSide6FromFile(thruFile6,rawThru);

        getUncalibratedS(rawThru, thruStandart);

        status.thru_standart_got = true;
    }

    void VNACalibration::load2matchStandart(const string& match2File3, const string& match2File6)
    {
        VNAData rawmatch2;
        readDataSide3FromFile(match2File3,rawmatch2);
        readDataSide6FromFile(match2File6,rawmatch2);

        getUncalibratedS(rawmatch2, twoMatchStandart);

        status.match2_standart_got = true;
    }


    // Линейная интерполяция
    complex<double> VNACalibration::linearInterpolate(vector<double>& Xarr, vector<complex<double>>& Yarr, int index, double arg)
    {
        complex<double> x1 = Xarr[index-1], x2 = Xarr[index];
        complex<double> y1 = Yarr[index-1], y2 = Yarr[index];
        return (y2 - y1) / (x2 - x1) * arg + (y1*x2 - y2*x1) / (x2 - x1);
    }

    int VNACalibration::getInterpIndex(vector<double>& ConstStepArr, double point)
    {
        if (ConstStepArr.empty()) {
            cerr << "Ошибка: пустой массив частот!" << endl;
            return -1;
        }
    
        // Для строго равномерного массива
        double start = ConstStepArr[0];
        double step = ConstStepArr[1] - ConstStepArr[0];
    
        // Рассчитываем индекс
        int index = static_cast<int>((point - start) / step) + 1;
    
        // Проверка границ
        if (index <= 0) return 1;
        if (index >= ConstStepArr.size()) return ConstStepArr.size() - 1;
        
        return index;
    }

    void VNACalibration::interpolateStandarts()
    {
        int index;

        if (status.firstP_standart_data_got){
            openLInterpP1.resize(N);
            shortLInterpP1.resize(N);
            matchLInterpP1.resize(N);

            for (int i = 0; i < N; i++)
            {
                index = getInterpIndex(FrequenciesOfStandart,calibrationFrequencies[i]);

                openLInterpP1[i] = linearInterpolate(FrequenciesOfStandart, openStandartp1.S, index, calibrationFrequencies[i]);
                shortLInterpP1[i] = linearInterpolate(FrequenciesOfStandart, shortStandartp1.S, index, calibrationFrequencies[i]);
                matchLInterpP1[i] = linearInterpolate(FrequenciesOfStandart, matchStandartp1.S, index, calibrationFrequencies[i]);

                status.firstP_standart_interpolated = true;
            }
        }

        if (status.secondP_standart_data_got){
            openLInterpP2.resize(N);
            shortLInterpP2.resize(N);
            matchLInterpP2.resize(N);

            for (int i = 0; i < N; i++)
            {
                index = getInterpIndex(FrequenciesOfStandart,calibrationFrequencies[i]);

                openLInterpP2[i] = linearInterpolate(FrequenciesOfStandart, openStandartp2.S, index, calibrationFrequencies[i]);
                shortLInterpP2[i] = linearInterpolate(FrequenciesOfStandart, shortStandartp2.S, index, calibrationFrequencies[i]);
                matchLInterpP2[i] = linearInterpolate(FrequenciesOfStandart, matchStandartp2.S, index, calibrationFrequencies[i]);

                status.secondP_standart_interpolated = true;
            }
        }

        if (status.thru_standart_got){
            thruLInterp.S11.resize(N);
            thruLInterp.S12.resize(N);
            thruLInterp.S21.resize(N);
            thruLInterp.S22.resize(N);

            for (int i = 0; i < N; i++)
            {
                index = getInterpIndex(FrequenciesOfStandart,calibrationFrequencies[i]);

                thruLInterp.S11[i] = linearInterpolate(FrequenciesOfStandart, thruStandart.S11, index, calibrationFrequencies[i]);
                thruLInterp.S12[i] = linearInterpolate(FrequenciesOfStandart, thruStandart.S12, index, calibrationFrequencies[i]);
                thruLInterp.S21[i] = linearInterpolate(FrequenciesOfStandart, thruStandart.S21, index, calibrationFrequencies[i]);
                thruLInterp.S22[i] = linearInterpolate(FrequenciesOfStandart, thruStandart.S22, index, calibrationFrequencies[i]);

                status.thru_standart_interpolated = true;
            }
        }

        if (status.match2_standart_got){
            Match2LInterp.S11.resize(N);
            Match2LInterp.S12.resize(N);
            Match2LInterp.S21.resize(N);
            Match2LInterp.S22.resize(N);
        
            for (int i = 0; i < N; i++)
            {
                index = getInterpIndex(FrequenciesOfStandart,calibrationFrequencies[i]);

                Match2LInterp.S11[i] = linearInterpolate(FrequenciesOfStandart, thruStandart.S11, index, calibrationFrequencies[i]);
                Match2LInterp.S12[i] = linearInterpolate(FrequenciesOfStandart, thruStandart.S12, index, calibrationFrequencies[i]);
                Match2LInterp.S21[i] = linearInterpolate(FrequenciesOfStandart, thruStandart.S21, index, calibrationFrequencies[i]);
                Match2LInterp.S22[i] = linearInterpolate(FrequenciesOfStandart, thruStandart.S22, index, calibrationFrequencies[i]);

                status.match2_standart_interpolated = true;
            }
        }
    }
    

    // Пересчет сырых данных в S-параметры
    Smatrixs VNACalibration::getUncalibratedS(const VNAData& Data, Smatrixs& res)
    {
        loadMeasurementData(Data);
        res.frequency.resize(N);
        res.S11.resize(N);
        res.S12.resize(N);
        res.S21.resize(N);
        res.S22.resize(N);

        for (int i = 0; i < N; i++)
        {
            res.frequency[i]=Data.frequency[i];
            // Проверка деления на ноль
            if (std::abs(Data.a0[i]) < 1e-15) {
                cerr << "Внимание: a0[" << i << "] близко к нулю! freq = " << Data.frequency[i] << endl;
                res.S11[i] = 0.0;
                res.S21[i] = 0.0;
            } else {
                res.S11[i] = Data.b0_3[i] / Data.a0[i];
                res.S21[i] = Data.b3_3[i] / Data.a0[i];
            }
        
            if (std::abs(Data.a3[i]) < 1e-15) {
                cerr << "Внимание: a3[" << i << "] близко к нулю! freq = " << Data.frequency[i] << endl;
                res.S12[i] = 0.0;
                res.S22[i] = 0.0;
            } else {
                res.S12[i] = Data.b0_6[i] / Data.a3[i];
                res.S22[i] = Data.b3_6[i] / Data.a3[i];
            }
        }
        return res;
    }

    void VNACalibration::calculateUncalibratedS()
    {
        getUncalibratedS(rawData, uncalibratedS); 

        status.uncalibrates_S_calculated = true;
    }

    //получаем однопортовые компоненты ошибок
    void VNACalibration::CalcPortOneErr()
    {
        firstPortE.resize(N);
        complex<double> g1, g2, g3, m1, m2, m3, znam;
        for (int i = 0; i < N; i++)
        {
            g1 = {1.0,0.0}, g2 = {-1.0, 0.0}, g3 = {0.0, 0.0}; //заглушка!!
            m1 = openLInterpP1[i], m2 = shortLInterpP1[i], m3 = matchLInterpP1[i];

            znam = (g2*g3*m3) - (g1*g3*m3) - (g2*g3*m2) + (g1*g2*m2) + (g1*g3*m1) - (g1*g2*m1);

            firstPortE[i].ef00 = (1.0 / znam) * (-((g1*g3-g1*g2)*m2+(g1*g2-g2*g3)*m1)*m3 - (g2-g1)*g3*m1*m2);
            firstPortE[i].ef11 = (1.0 / znam) * ((g2 - g1)*m3 - (g3 - g1) * m2 + (g3 - g2) * m1);
            firstPortE[i].detEf = (1.0 / znam) * (-((g3 -g2)*m2 + (g1 - g3) * m1) * m3 - (g2 - g1) * m1 * m2);
        }

        status.port_one_errors_calculated = true;
    }

    void VNACalibration::CalcPortTwoErr()
    {
        secondPortE.resize(N);
        complex<double> g1, g2, g3, m1, m2, m3, znam;
        for (int i = 0; i < N; i++)
        {
            g1 = {1.0,0.0}, g2 = {-1.0, 0.0}, g3 = {0.0, 0.0}; //заглушка!!
            m1 = openLInterpP2[i], m2 = shortLInterpP2[i], m3 = matchLInterpP2[i];

            znam = (g2*g3*m3) - (g1*g3*m3) - (g2*g3*m2) + (g1*g2*m2) + (g1*g3*m1) - (g1*g2*m1);

            secondPortE[i].ef00 = (1.0 / znam) * (-((g1*g3-g1*g2)*m2+(g1*g2-g2*g3)*m1)*m3 - (g2-g1)*g3*m1*m2);
            secondPortE[i].ef11 = (1.0 / znam) * ((g2 - g1)*m3 - (g3 - g1) * m2 + (g3 - g2) * m1);
            secondPortE[i].detEf = (1.0 / znam) * (-((g3 -g2)*m2 + (g1 - g3) * m1) * m3 - (g2 - g1) * m1 * m2);
        }

        status.port_two_errors_calculated = true;
    }

    // Получаем двухпортовые компоненты ошибок 
    void VNACalibration::Calc12termErr()
    {
        if ((!status.firstP_standart_interpolated) || (!status.secondP_standart_interpolated) || (!status.thru_standart_interpolated))
        {
            cerr << "для вычисления 12-ти компонентной модели ошибок недостаточно данных, либо не проведена интерполяция" << endl;
            return;
        }
        
        full12termErrors.resize(N);

        //однопортовые ошибки первого порта
        if (status.port_one_errors_calculated)
        {
            for (size_t i = 0; i < N; i++)
            {
                full12termErrors[i].ef00 = firstPortE[i].ef00;
                full12termErrors[i].ef11 = firstPortE[i].ef11;
                full12termErrors[i].ef10_01 = (firstPortE[i].ef00 * firstPortE[i].ef11) - firstPortE[i].detEf;
            }
        }
        else {
            complex<double> g1, g2, g3, m1, m2, m3, znam, det;
            for (int i = 0; i < N; i++)
            {
                g1 = {1.0,0.0}, g2 = {-1.0, 0.0}, g3 = {0.0, 0.0}; //заглушка!!
                m1 = openStandartp1.S[i], m2 = shortStandartp1.S[i], m3 = matchStandartp1.S[i];

                znam = (g2*g3*m3) - (g1*g3*m3) - (g2*g3*m2) + (g1*g2*m2) + (g1*g3*m1) - (g1*g2*m1);

                full12termErrors[i].ef00 = (1.0 / znam) * (-((g1*g3-g1*g2)*m2+(g1*g2-g2*g3)*m1)*m3 - (g2-g1)*g3*m1*m2);
                full12termErrors[i].ef11 = (1.0 / znam) * ((g2 - g1)*m3 - (g3 - g1) * m2 + (g3 - g2) * m1);
                det = (1.0 / znam) * (-((g3 -g2)*m2 + (g1 - g3) * m1) * m3 - (g2 - g1) * m1 * m2);
                full12termErrors[i].ef10_01 = (full12termErrors[i].ef00 * full12termErrors[i].ef11) - det;
            }
        }
        //однопортовые ошибки второго порта
        if (status.port_two_errors_calculated)
        {
            for (size_t i = 0; i < N; i++)
            {
                full12termErrors[i].er33 = secondPortE[i].ef00;
                full12termErrors[i].er22 = secondPortE[i].ef11;
                full12termErrors[i].er23_32 = (secondPortE[i].ef00 * secondPortE[i].ef11) - secondPortE[i].detEf;
            }
        }
        else {
            complex<double> g1, g2, g3, m1, m2, m3, znam, det;
            for (int i = 0; i < N; i++)
            {
                g1 = {1.0,0.0}, g2 = {-1.0, 0.0}, g3 = {0.0, 0.0}; //заглушка!!
                m1 = openStandartp2.S[i], m2 = shortStandartp2.S[i], m3 = matchStandartp2.S[i];

                znam = (g2*g3*m3) - (g1*g3*m3) - (g2*g3*m2) + (g1*g2*m2) + (g1*g3*m1) - (g1*g2*m1);

                full12termErrors[i].er33 = (1.0 / znam) * (-((g1*g3-g1*g2)*m2+(g1*g2-g2*g3)*m1)*m3 - (g2-g1)*g3*m1*m2);
                full12termErrors[i].er22 = (1.0 / znam) * ((g2 - g1)*m3 - (g3 - g1) * m2 + (g3 - g2) * m1);
                det = (1.0 / znam) * (-((g3 -g2)*m2 + (g1 - g3) * m1) * m3 - (g2 - g1) * m1 * m2);
                full12termErrors[i].er23_32 = (full12termErrors[i].er33 * full12termErrors[i].er22) - det;
            }
        }
        //утечки
        if (status.match2_standart_interpolated){
            for (int i = 0; i < N; i++)
            {
                full12termErrors[i].ef30 = Match2LInterp.S21[i];
                full12termErrors[i].er03 = Match2LInterp.S12[i];  
            }}
        //двупортовые остальные - на основании стандарта передачи
        for (int i = 0; i < N; i++)
        {
            //обозначим переменные для удобства
            complex<double> S11m = thruLInterp.S11[i], 
                            S21m = thruLInterp.S21[i], 
                            S12m = thruLInterp.S12[i], 
                            S22m = thruLInterp.S22[i], 

                            S11 = {0.0, 0.0},
                            S22 = {0.0, 0.0},
                            S12 = {1.0, 0.0},
                            S21 = {1.0, 0.0},
                            detS = {-1.0, 0.0},

                            ef10_01 = full12termErrors[i].ef10_01, 
                            ef00 = full12termErrors[i].ef00,
                            ef11 = full12termErrors[i].ef11,
                            er23_32 = full12termErrors[i].er23_32, 
                            er33 = full12termErrors[i].er33,
                            er22 = full12termErrors[i].er22,
                            ef30 = full12termErrors[i].ef30,
                            er03 = full12termErrors[i].er03,

                            ef22, ef10_32, er11, er23_01;
            //в прямом направлении
            ef22 = (ef10_01 * S11 - (S11m - ef00) * (1.0 - ef11 * S11)) / ((S11m - ef00) * (ef11 * detS - S22) + ef10_01 * detS);
            ef10_32 = (1.0 / S21) * (S21m - ef30) * (1.0 - ef11 * S11 - ef22 * S22 + ef11 * ef22 * detS);
            //в обратном
            er11 = (er23_32 * S22 - (S22m - er33) * (1.0 - er22 * S22)) / ((S22m - er33) * (er22 * detS - S11) + er23_32 * detS);
            er23_01 = (1.0 / S12) * (S12m - er03) * (1.0 - er11 * S11 - er22 * S22 + er11 * er22 * detS);

            full12termErrors[i].ef22 = ef22;
            full12termErrors[i].ef10_32 = ef10_32;
            full12termErrors[i].er11 = er11;
            full12termErrors[i].er23_01 = er23_01;
        }

        status.error_12term_calculated = true;
    }
    
    // Применить ошибки (откалибровать)
    void VNACalibration::ApplyPortOneErr()
    {
        calibratedS.frequency.resize(N);
        calibratedS.S11.clear();
        for (int i = 0; i < N; i++)
        {
            calibratedS.frequency[i]=rawData.frequency[i];
            complex<double> Gm = uncalibratedS.S11[i];
            calibratedS.S11.push_back((Gm - firstPortE[i].ef00) / (Gm * firstPortE[i].ef11 - firstPortE[i].detEf));
        }

        status.S11_calibrated = true;
    }
    
    void VNACalibration::ApplyPortTwoErr()
    {
        calibratedS.frequency.resize(N);
        calibratedS.S22.clear();
        for (int i = 0; i < N; i++)
        {
            calibratedS.frequency[i]=rawData.frequency[i];
            complex<double> Gm = uncalibratedS.S22[i];
            calibratedS.S22.push_back((Gm - secondPortE[i].ef00) / (Gm * secondPortE[i].ef11 - secondPortE[i].detEf));
        }

        status.S22_calibrated = true;
    }
    
    void VNACalibration::Apply12termErrors()
    {
        if (!status.error_12term_calculated)
        {
            cerr << "не посчитанны ошибки";
            return;
        }

        calibratedS.frequency.resize(N);
        calibratedS.S11.resize(N);
        calibratedS.S12.resize(N);
        calibratedS.S21.resize(N);
        calibratedS.S22.resize(N);

        complex<double> D;
        for (int i = 0; i < N; i++)
        {
            calibratedS.frequency[i]=rawData.frequency[i];
            complex<double> S11m = uncalibratedS.S11[i], 
                            S21m = uncalibratedS.S21[i], 
                            S12m = uncalibratedS.S12[i], 
                            S22m = uncalibratedS.S22[i], 

                            ef10_01 = full12termErrors[i].ef10_01, 
                            ef00 = full12termErrors[i].ef00,
                            ef11 = full12termErrors[i].ef11,

                            ef22 = full12termErrors[i].ef22,
                            ef10_32 = full12termErrors[i].ef10_32,
                            ef30 = full12termErrors[i].ef30,

                            er23_32 = full12termErrors[i].er23_32, 
                            er33 = full12termErrors[i].er33,
                            er22 = full12termErrors[i].er22,

                            er11 = full12termErrors[i].er11,
                            er23_01 = full12termErrors[i].er23_01,
                            er03 = full12termErrors[i].er03,
                            D;

            D = (1.0 + ((S11m - ef00) / ef10_01) * ef11) * (1.0 + ((S22m - er33) / er23_32) * er22) - ((S21m - ef30) / ef10_32) * ((S12m - er03) / (er23_01)) * ef22 * er11;

            calibratedS.S11[i] = (((S11m - ef00) / (ef10_01)) * (1.0 + ((S22m - er33) / (er23_32)) * er22) - ef22 * ((S21m - ef30) / (ef10_32)) * ((S12m - er03) / (er23_01))) / D;
            calibratedS.S21[i] = (((S21m - ef30) / (ef10_32)) * (1.0 + ((S22m - er33) / (er23_32)) * (er22 - ef22))) / D;
            calibratedS.S12[i] = (((S12m - er03) / (er23_01)) * (1.0 + ((S11m - ef00) / (ef10_01)) * (ef11 - er11))) / D;
            calibratedS.S22[i] = (((S22m - er33) / (er23_32)) * (1.0 + ((S11m - ef00) / (ef10_01)) * ef11) - er11 * ((S21m - ef30) / (ef10_32)) * ((S12m - er03) / (er23_01))) / D;
        }

        status.Smatrix_calibrated = true;
    }



    // Вывод результатов
    void VNACalibration::writeCalibratedS(const string& filename)
    {
        ofstream file(filename, std::ios::trunc);
        if (!file.is_open()) {
            cout << "Не удалось открыть файл: " << filename << endl;
            return;
        }
    
        file << fixed << setprecision(15);
    
        for (size_t i = 0; i < N; ++i) {
            file << setprecision(1) << rawData.frequency[i] << "      ";

            double realPart;
            double imagPart;

            //записать всё
            if (status.Smatrix_calibrated)
            {
                realPart = calibratedS.S11[i].real();
                imagPart = calibratedS.S11[i].imag();
        
                if (imagPart >= 0) {
                    if (realPart >= 0.0) file << " ";
                    file << setprecision(15) << realPart << "    " << imagPart  << "       ";
                } else {
                    file << setprecision(15)<< realPart << "   -" << -imagPart  << "       ";
                }

                realPart = calibratedS.S21[i].real();
                imagPart = calibratedS.S21[i].imag();
        
                if (imagPart >= 0) {
                    if (realPart >= 0.0) file << " ";
                    file << setprecision(15) << realPart << "    " << imagPart  << "       ";
                } else {
                    file << setprecision(15)<< realPart << "   -" << -imagPart  << "       ";
                }

                realPart = calibratedS.S12[i].real();
                imagPart = calibratedS.S12[i].imag();
        
                if (imagPart >= 0) {
                    if (realPart >= 0.0) file << " ";
                    file << setprecision(15) << realPart << "    " << imagPart  << "       ";
                } else {
                    file << setprecision(15)<< realPart << "   -" << -imagPart  << "       ";
                }

                realPart = calibratedS.S22[i].real();
                imagPart = calibratedS.S22[i].imag();
        
                if (imagPart >= 0) {
                    if (realPart >= 0.0) file << " ";
                    file << setprecision(15) << realPart << "    " << imagPart  << "       ";
                } else {
                    file << setprecision(15)<< realPart << "   -" << -imagPart  << "       ";
                }
            }

            //записать однопортовую по первому порту
            if (status.S11_calibrated && (!status.Smatrix_calibrated))
            {
                realPart = calibratedS.S11[i].real();
                imagPart = calibratedS.S11[i].imag();
        
                if (imagPart >= 0) {
                    if (realPart >= 0.0) file << " ";
                    file << setprecision(15) << realPart << "    " << imagPart;
                } else {
                    file << setprecision(15)<< realPart << "   -" << -imagPart;
                }
            }

            //записать однопортовую по первому порту
            if (status.S22_calibrated && (!status.Smatrix_calibrated))
            {
                realPart = calibratedS.S22[i].real();
                imagPart = calibratedS.S22[i].imag();
        
                if (imagPart >= 0) {
                    file  << "         " << setprecision(15) << realPart << "     " << imagPart;
                } else {
                    file  << "         " << setprecision(15)<< realPart << "    -" << -imagPart;
                }
            }

            if (i < N - 1) {
                file << endl;
            }
        }
        file << endl << endl;
    
        file.close();
    }
    // тут всегда возвращается полная матрица - надо бы помнить какая калибровка
    Smatrixs VNACalibration::getCalibratedS(){
        if (!status.Smatrix_calibrated && !status.S11_calibrated && !status.S22_calibrated) {
            //throw std::runtime_error("S-параметры не откалиброваны");
            cerr << "S-параметры не откалиброваны" << endl;
        }
        return calibratedS;
    }

    // Вспомогательные методы
    vector<double> VNACalibration::getCalibrationFrequencies() const { return calibrationFrequencies; }

    void VNACalibration::debugCheck(int number) {
        cout << "_________________________________________________________" << endl;
        cout << "отладчик номер" << number << endl;
        cout << "Размеры векторов (сырые данные):" << endl;
        cout << "a0: " << rawData.a0.size() << endl;
        cout << "a3: " << rawData.a3.size() << endl;
        cout << "b0_3: " << rawData.b0_3.size() << endl;
        cout << "b3_3: " << rawData.b3_3.size() << endl;
        cout << "b0_6: " << rawData.b0_6.size() << endl;
        cout << "b3_6: " << rawData.b3_6.size() << endl;
        cout << endl;
    
        /* // Проверим первые несколько значений
        for (int i = 0; i < min(5, N); i++) {
            cout << "Точка " << i << ":" << endl;
            cout << "  a0 = " << rawData.a0[i] << endl;
            cout << "  a3 = " << rawData.a3[i] << endl;
            cout << "  b0_3 = " << rawData.b0_3[i] << endl;
            cout << "  b3_3 = " << rawData.b3_3[i] << endl;
        } */

        cout << "Размеры стандартов первого порта:" << endl;
        cout << "O: " << openStandartp1.S.size() << endl;
        cout << "S: " << shortStandartp1.S.size() << endl;
        cout << "M: " << matchStandartp1.S.size() << endl;
        for (int i = 0; i < min(5, N); i++) {
            cout << "Точка " << i << ": ";
            cout << "Open=" << openStandartp1.S[i] << " ";
            cout << "Short=" << shortStandartp1.S[i] << " ";
            cout << "Match=" << matchStandartp1.S[i] << endl;
        }
        cout << "Размеры стандартов второго порта:" << endl;
        cout << "O: " << openStandartp2.S.size() << endl;
        cout << "S: " << shortStandartp2.S.size() << endl;
        cout << "M: " << matchStandartp2.S.size() << endl;
        cout << "Значения стандартов второго порта:" << endl;
        for (int i = 0; i < min(5, (int)openStandartp2.S.size()); i++) {
            cout << "Точка " << i << ": ";
            cout << "Open=" << openStandartp2.S[i] << " ";
            cout << "Short=" << shortStandartp2.S[i] << " ";
            cout << "Match=" << matchStandartp2.S[i] << endl;
        }
        cout << endl;

        cout << "проверяем неоткалиброванные S" << endl;
        cout << "количество частот: " << uncalibratedS.frequency.size() << endl;
        cout << "количество S11: " << uncalibratedS.S11.size() << endl;
        cout << "количество S12: " << uncalibratedS.S12.size() << endl;
        cout << "количество S21: " << uncalibratedS.S21.size() << endl;
        cout << "количество S22: " << uncalibratedS.S22.size() << endl;
        for (int i = 0; i < min(5, N); i++) {
            cout << "Точка " << i << ":  ";
            cout << "  S11 = " << uncalibratedS.S11[i] << ",  ";
            cout << "  S12 = " << uncalibratedS.S12[i] << ",  ";
            cout << "  S21 = " << uncalibratedS.S21[i] << ",  ";
            cout << "  S22 = " << uncalibratedS.S22[i] << ",  " << endl;
        }
        cout << endl;
    
        cout << "компоненты ошибки" << endl;
        cout << "количество по первому порту: " << firstPortE.size() << endl;
        cout << "количество по второму порту: " << secondPortE.size() << endl;
        for (int i = 0; i < min(5, (int)firstPortE.size()); i++) {
            cout << "Точка " << i << ":  ";
            cout << "  ef00 = " << firstPortE[i].ef00 << ",  ";
            cout << "  ef11 = " << firstPortE[i].ef11 << ",  ";
            cout << "  detEf = " << firstPortE[i].detEf << ",  "<< endl;
        }
        
        for (int i = 0; i < min(5, (int)secondPortE.size()); i++) {
            cout << "Точка " << i << ":  ";
            cout << "  er00 = " << secondPortE[i].ef00 << ",  ";
            cout << "  er11 = " << secondPortE[i].ef11 << ",  ";
            cout << "  detEr = " << secondPortE[i].detEf << ",  "<< endl;
        }
        cout << endl;

        cout << "проверяем откалиброванные S" << endl;
        cout << "количество частот: " << calibratedS.frequency.size() << endl;
        cout << "количество S11: " << calibratedS.S11.size() << endl;
        cout << "количество S12: " << calibratedS.S12.size() << endl;
        cout << "количество S21: " << calibratedS.S21.size() << endl;
        cout << "количество S22: " << calibratedS.S22.size() << endl;
        for (int i = 0; i < min(5, N); i++) {
            cout << "Точка " << i << ":  ";
            cout << "  S11 = " << calibratedS.S11[i] << ",  ";
            cout << "  S12 = " << calibratedS.S12[i] << ",  ";
            cout << "  S21 = " << calibratedS.S21[i] << ",  ";
            cout << "  S22 = " << calibratedS.S22[i] << ",  " << endl;
        }

        cout << "_________________________________________________________" << endl;
        cout << endl;
        cout << endl;
    }
