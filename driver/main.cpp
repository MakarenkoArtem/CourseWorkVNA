// main.cpp
#include "VNAKitDevice.h"
#include <iostream>
#include <thread>
#include <memory>

int main() {
    try {
        // Создание экземпляра устройства
        VNAKitDevice vna;
        // Получение текущих настроек
            VNAKit_RecordingSettings settings{};
    settings.freqRange.freqStartMHz = 4125.0;
    settings.freqRange.freqStopMHz = 6000.0;
    settings.freqRange.numFreqPoints = 51;
    settings.rbw_khz = 140.0;
    settings.outputPower_dbm = -24.0;
    settings.txtr = 6;
    settings.mode = VNAKIT_MODE_ONE_PORT;


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
