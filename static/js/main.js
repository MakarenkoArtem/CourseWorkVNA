import {checkWSClient, getWSClient, getSParamWS, WSClient} from './wsClient.js'
import {GraphicSParams} from './GraphicSParams.js'
import {GraphData} from './GraphData.js'
import {WSResponse} from './WSResponse.js'
import {SettingsVNA} from './SettingsVNA.js'
import {getWSAddress, getCurrentTime} from './getWSAddress.js'

function sleep(ms){
    return new Promise(resolve=>setTimeout(resolve, ms));
}

let timeOut = 100;
let websocketHost = null;
let websocketPort = null;
let client = null;
let CURRENT_USER = 5;
const settings = new SettingsVNA();
async function loop() {
    let graphics = new GraphicSParams([
        [new GraphData("S11", "S11", websocketHost,websocketPort, settings),
        new GraphData("S12", "S12", websocketHost,websocketPort, settings)],
        [new GraphData("S21", "S21", websocketHost,websocketPort, settings),
        new GraphData("S22", "S22", websocketHost,websocketPort, settings)]]);
    while (1){
        try{
            if(checkWSClient(client) == null){
                [websocketHost, websocketPort] =
                await getWSAddress(`http://${location.hostname}:8000/api/websocket`, websocketHost, websocketPort);

                timeOut = 100;
                let time = await getCurrentTime(`http://${location.hostname}:8000/api/time_user`, websocketHost, websocketPort);
                console.log("TIME:", time)
                try{
                    let btn = document.getElementById("btn-settings")
                    if(time>-1){
                        document.getElementById("settingsIcon").src = "/src/control.png"
                        let text='Устройсво доступно';
                        if (time>0){
                            text=`${Math.floor(time/60)}:${time%60}`
                        }
                        document.getElementById("btn-settings-text").textContent = text
                        btn.onclick = () => window.location.href = "/settings";
                    }else{
                        document.getElementById("settingsIcon").src = "/src/disconnect.png"
                        document.getElementById("btn-settings-text").textContent = 'Управление у другого пользователя'
                        btn.onclick = () => null;
                    }
                }catch(error){
                    console.log(error)
                }
                client = await WSClient.create(`ws://${websocketHost}:${websocketPort}`, settings);

            }

            console.debug("Update settings: ", settings.update(await client.getSettings()))

            while(client.isSocketOpen()){
                let resp = await client.getSParams();
                console.log("Получено через WS:", resp);
                graphics.takeResponse(resp);
                timeOut = 50;
                await sleep(timeOut);
            }
            client = null
            console.debug("restart");
        }catch(error){
            console.log("Timeout:", timeOut);
            console.error(error)
            await sleep(timeOut);
            timeOut = Math.min(30000, timeOut*2);
            websocketHost = null;
            websocketPort = null;
            if(client!=null){
                client.close();
                client = null;
            }
        }
    }
}

loop();
//npm run dev