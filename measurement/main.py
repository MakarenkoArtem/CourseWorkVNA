import vnakit

if __name__ == '__main__':
    vnakit.Init()

    # Применение настроек
    vnaSettings = vnakit.RecordingSettings(
        vnakit.FrequencyRange(500.0, 6000.0, 1001),  # 51 точка, от 4125 до 6000 МГц
        2.0,  # Полоса пропускания (RBW) в КГц
        -10.0,  # Выходная мощность (дБм)
        6,  # txtr — от 1 до 6
        vnakit.VNAKIT_MODE_TWO_PORTS  # VNAKIT_MODE_TWO_PORTS  # Режим двухпортного измерения
    )

    vnakit.ApplySettings(vnaSettings)

    # Запись несколько раз
    for i in range(10):
        vnakit.Record()

    actual_freqs = vnakit.GetFreqVector_MHz()
    with open("3db6.csv", "w") as file:
        recording = vnakit.GetRecordingResult()
        print(recording)
        res = [recording[4][i] / recording[5][i] for i in range(len(recording[1]))]
        for i in range(len(actual_freqs)):
            file.write(str(actual_freqs[i]).ljust(5, ' '))
            for txtr in [1, 2, 3, 4, 5, 6]:
                file.write(str(recording[txtr][i].real).rjust(25, ' '))
                file.write(str(recording[txtr][i].imag).rjust(25, ' '))
            file.write("\n")
