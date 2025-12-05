import {Client} from '../Client.js'
import {SettingsVNA} from '../SettingsVNA.js'


function formatTime(time) {
    const formattedMinutes = String(Math.floor(time / 60)).padStart(2, '0');
    const formattedSeconds = String(time % 60).padStart(2, '0');
    return `${formattedMinutes}:${formattedSeconds}`;
}

function updateBar(time){
    try{
        let btn = document.getElementById("btn-settings")
        if(time>-1){
            document.getElementById("settingsIcon").src = "/static/img/control.png"
            let text='Устройсво доступно';
            if (time>0){
                text=formatTime(time)
            }
            document.getElementById("btn-settings-text").textContent = text
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

function updateButtons(settings) {
    // Маппинг ID кнопок к соответствующим ключам в объекте settings
    const buttonsMap = {
        'HH': 'calib_HH',
        'KZ': 'calib_KZ',
        'Match': 'calib_Match',
        'Bolt': 'calib_Bolt'
    };

    for (const [buttonId, settingKey] of Object.entries(buttonsMap)) {
        let button = document.getElementById(buttonId);
        if (button) { // Проверяем, существует ли кнопка
            console.log(`Checking ${settingKey}: ${settings[settingKey]}`);
            let newVal = settings[settingKey] == 1 ? 'btn btn-danger' : 'btn btn-primary';
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

const settings = new SettingsVNA();
let client = new Client(`http://${location.hostname}:${location.port}`,settings);
async function loop() {
    while (1){
        try{
            let time = await client.getRemainingTime()
            console.log("TIME:", time)
            updateBar(time)
            console.log(await client.getSettings());
            let isChanged = settings.update(await client.getSettings())
            updateButtons(await client.getSettings())
            if (isChanged){
                console.debug("Update settings: ", settings)
            }
            let data = await client.getSParams()
            await client.delay()
        }catch(error){
            console.error(error)
            await client.delay(10000);
        }
    }
}

loop();


async function calibration(buttonId){
    const loader = document.getElementById(`loader-${buttonId}`);
    const buttonText = document.getElementById(`text-${buttonId}`);
    loader.style.display = 'inline-block'; // Показать спиннер

    try {
        const result = await client.getJSON(`/${buttonId}`)
        console.log(`Response from /${buttonId}:`, result);
    } catch (error) {
        console.error("Error sending request to /HH:", error);
    }
}
window.calibration = calibration;