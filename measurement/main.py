import argparse
import vnakit


def ParseArguments():
    """Парсинг аргументов командной строки."""
    parser = argparse.ArgumentParser(description='Test VNAKit.py, Python wrapper for VNAKit')
    parser.add_argument('--output_dir', required=True, dest='OUTPUT_DIR', help="Path to write output")
    return parser.parse_args()


if __name__ == '__main__':
    #args = ParseArguments()
    vnakit.Init()

    # Применение настроек
    vnaSettings = vnakit.RecordingSettings(
        vnakit.FrequencyRange(500.0, 6000.0, 51),  # 51 точка, от 4125 до 6000 МГц
        1.0,  # Полоса пропускания (RBW) в КГц
        -10.0,  # Выходная мощность (дБм)
        6,  # txtr — от 1 до 6
        vnakit.VNAKIT_MODE_TWO_PORTS #VNAKIT_MODE_TWO_PORTS  # Режим двухпортного измерения
    )

    vnakit.ApplySettings(vnaSettings)

    #vnakit.Record()  # первое измерение
    #vnakit.WriteRecording(args.OUTPUT_DIR, vnakit.VNAKIT_OUTFORMAT_CSV)  # запись в CSV файл

    #vnakit.Record()  # второе измерение
    #vnakit.WriteRecording(args.OUTPUT_DIR, vnakit.VNAKIT_OUTFORMAT_MAT)  # запись в MAT файл

    # Изменение настроек
    vnaSettings.txtr = 6
    vnaSettings.mode = vnakit.VNAKIT_MODE_ONE_PORT
    vnakit.ApplySettings(vnaSettings)

    # Запись несколько раз
    for i in range(10):
        vnakit.Record()

    actual_freqs = vnakit.GetFreqVector_MHz()
    with open("3db6.csv", "w") as file:
        recording = vnakit.GetRecordingResult()
        print(recording)
        res = [recording[4][i]/recording[5][i] for i in range(len(recording[1]))]
        #file.write(' '.join(map(str, actual_freqs)))
        #print(' '.join(map(str, actual_freqs)))
        for i in range(len(actual_freqs)):
            file.write(str(actual_freqs[i]).ljust(5, ' '))
            for txtr in [1, 2, 3, 4, 5, 6]:
                file.write(str(recording[txtr][i].real).rjust(25, ' '))
                file.write(str(recording[txtr][i].imag).rjust(25, ' '))
            file.write("\n")
        file.write(" ".join([str(i) for i in res]))
        file.write("\n")
        file.write(" ".join([str(abs(i)) for i in res]))
        file.write("\n")
