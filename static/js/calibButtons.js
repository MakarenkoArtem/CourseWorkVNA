
export function updateButtons(settings) {
    // Маппинг ID кнопок к соответствующим ключам в объекте settings
    const buttonsMap = {
        'HH': 'calib_HH',
        'KZ': 'calib_KZ',
        'Match': 'calib_Match',
        'Bolt': 'calib_Bolt'
    };
    console.debug(settings)
    for (const [buttonId, settingKey] of Object.entries(buttonsMap)) {
        let button = document.getElementById(buttonId);
        if (button) { // Проверяем, существует ли кнопка
            console.debug(`Checking ${settingKey}: ${settings[settingKey]}`);
            let newVal = settings[settingKey] == 1 ? 'btn btn-danger' : 'btn btn-success';
            // Устанавливаем класс кнопки в зависимости от значения настройки
            if (button.className != newVal){
                button.className = newVal;
                let loader = document.getElementById(`loader-${buttonId}`);
                loader.style.display = 'none'
            }
        } else {
            console.error(`Button with ID ${buttonId} not found`);
        }
    }
}

export async function calibration(buttonId, client){
    const loader = document.getElementById(`loader-${buttonId}`);
    const buttonText = document.getElementById(`text-${buttonId}`);
    loader.style.display = 'inline-block'; // Показать спиннер

    try {
        const result = await client.getJSON(`/${buttonId}`)
        console.log(`Response from /${buttonId}:`, result);
    } catch (error) {
        console.error("Error sending request to:", error);
    }
}
window.calibration = calibration;