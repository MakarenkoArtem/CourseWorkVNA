const CALIBRATED=0
const UNCORRECTED_CALIBRATION=3
const CALIBRATING=4
const UNCALIBRATED=5
const classNames = {
[CALIBRATED]:'btn btn-success',
[UNCORRECTED_CALIBRATION]:'btn btn-warning',
[CALIBRATING]:'btn btn-warning',//'btn btn-info',
[UNCALIBRATED]:'btn btn-danger'
}

function formatTime(time) {
    const formattedMinutes = String(Math.floor(time / 60)).padStart(2, '0');
    const formattedSeconds = String(time % 60).padStart(2, '0');
    return `${formattedMinutes}:${formattedSeconds}`;
}

export function updateBar(time){
    try{
        let btn = document.getElementById("btn-settings")
        if(time>-1){
            document.getElementById("settingsIcon").src = "/static/img/control.png"
            let text='Устройсво доступно';
            if (time>0){
                text=formatTime(time)
            }
            document.getElementById("calib_dropdown").disabled= time<=0;
            document.getElementById("btn-settings-text").textContent = text;
            btn.onclick = () => window.location.href = "/settings";
        }else{
            document.getElementById("settingsIcon").src = "/static/img/disconnect.png"
            document.getElementById("btn-settings-text").textContent = 'Управление у другого пользователя'
            btn.onclick = () => null;
        }
    }catch(error){
        console.debug(error)
    }
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

export async function decalibration(client){
    try {
        const result = await client.getJSON(`/decalibrate`)
        console.log(`Response from /decalibrate`, result);
    } catch (error) {
        console.error("Error sending request to:", error);
    }
}

export async function deactivate(client){
    try {
        const result = await client.getJSON(`/deactivate`)
        console.log(`Response from /deactivate`, result);
    } catch (error) {
        console.error("Error sending request to:", error);
    }
}

window.calibration = calibration;
window.decalibration = decalibration;
window.deactivate = deactivate;