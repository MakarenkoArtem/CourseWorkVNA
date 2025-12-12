const CALIBRATED=0
const UNCORRECTED_CALIBRATION=3
const CALIBRATING=4
const UNCALIBRATED=5
const classNames = {
[CALIBRATED]:'btn btn-success',
[UNCORRECTED_CALIBRATION]:'btn btn-warning',
[CALIBRATING]:'btn btn-info',
[UNCALIBRATED]:'btn btn-danger'
}
export function updateButtons(settings) {
    // Маппинг ID кнопок к соответствующим ключам в объекте settings
    const buttonsMap = {
        'HH': 'calib_HH',
        'KZ': 'calib_KZ',
        'Match': 'calib_Match',
        'Bolt': 'calib_Bolt',
        'MatchDual': 'calib_Match_Dual',
    };
    console.debug(settings)
    for (const [buttonId, settingKey] of Object.entries(buttonsMap)) {
        let button = document.getElementById(buttonId);
        if (button) { // Проверяем, существует ли кнопка
            console.debug(`Checking ${settingKey}: ${settings[settingKey]}`);
            let loader = document.getElementById(`loader-${buttonId}`);
            let newVal = classNames[settings[settingKey]];
            button.className = newVal;
            // Устанавливаем класс кнопки в зависимости от значения настройки
            if (settings[settingKey]!=CALIBRATING && loader.style.display != 'none'){
                loader.style.display = 'none'
            }
        } else {
            console.debug(`Button with ID ${buttonId} not found`);
        }
    }
}

export async function calibration(buttonId, client){
    let button = document.getElementById(buttonId);
    const loader = document.getElementById(`loader-${buttonId}`);
    const buttonText = document.getElementById(`text-${buttonId}`);
    loader.style.display = 'inline-block'; // Показать спиннер
    button.className = classNames[CALIBRATING]

    try {
        const result = await client.getJSON(`/${buttonId}`)
        console.log(`Response from /${buttonId}:`, result);
    } catch (error) {
        console.error("Error sending request to:", error);
    }
}
window.calibration = calibration;