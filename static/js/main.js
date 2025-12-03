import {Client} from './Client.js'
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

let timeOut = 1000;
const settings = new SettingsVNA();
let client = new Client(`http://${location.hostname}:${location.port}`,settings);
async function loop() {
    let graphics = new GraphicSParams(settings,
                                      [[new GraphData("S11", "S11"), new GraphData("S12", "S12")],
                                      [new GraphData("S21", "S21"), new GraphData("S22", "S22")]]);
    while (1){
        try{
            console.log("client:", client);
            let time = await client.getRemainingTime();
            timeOut = 5000
            console.log("TIME:", time)
            updateBar(time)
            let isChanged = settings.update(await client.getSettings())
            if (isChanged){
                console.debug("Update settings: ", settings)
                graphics.updateScales()
            }
            let data = await client.getSParams();
            graphics.takeResponse(data)
            await client.delay(timeOut);
            console.log(client)
        }catch(error){
            console.log("Timeout:", timeOut);
            console.error(error)
            await client.delay(timeOut);
            client.timeOut = Math.min(30000, client.timeOut*2);
        }
    }
}

loop();