//import React from 'react'
//import * as ReactDOMClient from 'react-dom/client'
//import './index.css'
import {checkWSClient, getWSClient, getSParamWS, WSClient} from './wsClient.js'
import {GraphicSParams} from './GraphicSParams.js'
import {GraphData} from './GraphData.js'
import {WSResponse} from './WSResponse.js'
import {SettingsVNA} from './SettingsVNA.js'

function sleep(ms){
    return new Promise(resolve=>setTimeout(resolve, ms));
}

async function getAddress(address, websocketHost, websocketPort) {
    if (websocketHost!=null && websocketPort!=null){return [websocketHost, websocketPort];}
    const response = await fetch(address, {method: "GET"})

    if(response.ok){
        const data = await response.json();
        if (typeof data.host === 'string' && typeof data.port === 'number') {
            return [data.host, data.port];
        }
        throw new Error(`Data is not correct`)
        }
    throw new Error(`HTTP error ${response.status}`);
}

let timeOut = 100;
let websocketHost = null;
let websocketPort = null;
let client = null;
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
                await getAddress(`http://${location.hostname}:8000/api/websocket`, websocketHost, websocketPort);

                client = await WSClient.create(`ws://${websocketHost}:${websocketPort}`, settings);
                timeOut = 100;
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