#include "VNAKitDevice.h"
#include <iostream>

int main() {
    try {
        VNAKitDevice vna("./vnakit.conf");

        vna.init();

        auto settings = vna.getSettings();

        // Настройка диапазона частот (в МГц)
        settings.freqRange.freqStartMHz = 500.0;   // Начальная частота
        settings.freqRange.freqStopMHz = 1000.0;   // Конечная частота
        settings.freqRange.numFreqPoints = 1001;          // Количество точек
        settings.rbw_khz = 2;
        settings.outputPower_dbm = -10.0;

        // Режим измерения: 0 — одиночный, 1 — дифференциальный (если поддерживается)
        settings.mode = VNAKIT_MODE_TWO_PORTS;

        // TXTR: 3 или 6 — зависит от конфигурации портов (см. документацию VNAKit)
        settings.txtr = 3;

        // Применение настроек
        vna.setSettings(settings);
        vna.validateSettings();
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