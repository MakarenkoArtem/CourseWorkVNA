export class SettingsVNA {
    constructor(strSettings = "") {
        // Дефолтные значения
        this.id = 0;
        this.minFrequency = 9000;
        this.maxFrequency = 10500;
        this.countPoints = 51;

        // Если передана строка, обновляем значения
        if (strSettings && strSettings.length) {
            this.update(strSettings);
        }
    }

    update(strSettings) {
        let settings;
        try {
            settings = JSON.parse(strSettings);
        } catch (e) {
            console.error("Invalid JSON:", strSettings);
            return false;
        }
        this.id = settings.id ?? this.id;
        this.minFrequency = settings.minFrequency ?? this.minFrequency;
        this.maxFrequency = settings.maxFrequency ?? this.maxFrequency;
        this.countPoints = settings.countPoints ?? this.countPoints;
        return true;
    }
}
