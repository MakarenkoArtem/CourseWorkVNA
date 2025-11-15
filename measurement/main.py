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
        vnakit.FrequencyRange(4125.0, 6000.0, 51),  # 51 точка, от 4125 до 6000 МГц
        140.0,  # Полоса пропускания (RBW) в КГц
        -24.0,  # Выходная мощность (дБм)
        6,  # txtr — от 1 до 6
        vnakit.VNAKIT_MODE_ONE_PORT #VNAKIT_MODE_TWO_PORTS  # Режим двухпортного измерения
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
    print("FREQUENCIES:")
    print(actual_freqs)
    print("------")
    with open("open.csv", "w") as file:
        recording = vnakit.GetRecordingResult()
        res = [recording[4][i]/recording[5][i] for i in range(len(recording[1]))]
        for txtr in [1, 2, 3, 4, 5, 6]:
            file.write(str(txtr) + ": " + str(recording[txtr]))
            file.write("\n")
        file.write(" ".join([str(i) for i in res]))
        file.write("\n")
        file.write(" ".join([str(abs(i)) for i in res]))
        file.write("\n")
