import {Client} from '../Client.js'
import {GraphicSParams} from './GraphicSParams.js'
import {GraphData} from './GraphData.js'
import {Response} from './Response.js'
import {SettingsVNA} from './SettingsVNA.js'


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
            if (isChanged){
                console.debug("Update settings: ", settings)
                graphics.updateScales()
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