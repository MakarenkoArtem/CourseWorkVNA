import vnakit

if __name__ == '__main__':
    vnakit.Init()
    # Применение настроек
    vnaSettings = vnakit.RecordingSettings(
        vnakit.FrequencyRange(500.0, 6000.0, 1001), # 1001 точка, от 500 до 6000 МГц
        10.0,  # Полоса пропускания (RBW) в КГц
        -10.0,  # Выходная мощность (дБм)
        6,  # txtr — от 1 до 6
        vnakit.VNAKIT_MODE_TWO_PORTS  # Режим двухпортного измерения
    )

    vnakit.ApplySettings(vnaSettings) # применение настроек
    vnakit.Record()                   # получение измерений

    actual_freqs = vnakit.GetFreqVector_MHz()
    with open("cal.csv", "w") as file: # запись измерений в файл
        recording = vnakit.GetRecordingResult()
        for i in range(len(actual_freqs)):
            file.write(str(actual_freqs[i]).ljust(5, ' '))
            for txtr in [1, 2, 3, 4, 5, 6]:
                file.write(str(recording[txtr][i].real).rjust(25, ' '))
                file.write(str(recording[txtr][i].imag).rjust(25, ' '))
            file.write("\n")







