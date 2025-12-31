export class SettingsVNA {
    constructor() {
        this.id = 0;
        this.minFrequency = 9000;
        this.maxFrequency = 10500;
        this.countPoints = 51;
    }

    update(settings) {
        let change = (settings.id != this.id || settings.freq_start_mhz != this.minFrequency
           ||  settings.freq_stop_mhz != this.maxFrequency || settings.num_freq_points != this.countPoints)
        this.id = settings.id ?? this.id;
        this.minFrequency = settings.freq_start_mhz ?? this.minFrequency;
        this.maxFrequency = settings.freq_stop_mhz ?? this.maxFrequency;
        this.countPoints = settings.num_freq_points ?? this.countPoints;
        return change;
    }
}
