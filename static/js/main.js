import {Client} from './Client.js'
import {GraphicSParams} from './GraphicSParams.js'
import {GraphData} from './GraphData.js'
import {WSResponse} from './WSResponse.js'
import {SettingsVNA} from './SettingsVNA.js'

function sleep(ms){
    return new Promise(resolve=>setTimeout(resolve, ms));
}

function formatTime(time) {
    const formattedMinutes = String(Math.floor(time / 60)).padStart(2, '0');
    const formattedSeconds = String(time % 60).padStart(2, '0');
    return `${formattedMinutes}:${formattedSeconds}`;
}
function updateBar(time){
    try{
        let btn = document.getElementById("btn-settings")
        if(time>-1){
            document.getElementById("settingsIcon").src = "/src/control.png"
            let text='Устройсво доступно';
            if (time>0){
                text=formatTime(time)
            }
            document.getElementById("btn-settings-text").textContent = text
            btn.onclick = () => window.location.href = "/settings";
        }else{
            document.getElementById("settingsIcon").src = "/src/disconnect.png"
            document.getElementById("btn-settings-text").textContent = 'Управление у другого пользователя'
            btn.onclick = () => null;
        }
    }catch(error){
        console.debug(error)
    }
}

let timeOut = 100;
const settings = new SettingsVNA();
let client = new Client(`http://${location.hostname}:${location.port}`,settings);
async function loop() {
    let graphics = new GraphicSParams(settings,
                                      [[new GraphData("S11", "S11"), new GraphData("S12", "S12")],
                                      [new GraphData("S21", "S21"), new GraphData("S22", "S22")]]);
    while (1){
        try{
            let time = (await client.getJSON("/api/time_user")).remainingTime;
            timeOut = 5000
            console.log("TIME:", time)
            updateBar(time)
            let change = settings.update(await client.getSettings())
            if (change){
                console.debug("Update settings: ", settings)
                graphics.updateScales()
            }
            let data = await client.getSParams();
            graphics.takeResponse(data)
            await sleep(timeOut);
            console.debug("restart");
        }catch(error){
            console.log("Timeout:", timeOut);
            console.error(error)
            await sleep(timeOut);
            timeOut = Math.min(30000, timeOut*2);
        }
    }
}

loop();
//npm run dev