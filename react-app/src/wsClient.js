 import {WSResponse} from './WSResponse.js';

export class WSClient {
    constructor(address, settings) {
        this.socket = new WebSocket(address);
        this.settings = settings;
        console.debug(settings, this.settings);
    }

    static async create(address, settings) {
        return new Promise((resolve, reject) => {
            const client = new WSClient(address, settings);

            client.socket.onopen = () => {
                console.log("WebSocket открыт");
                resolve(client);
            };

            client.socket.onerror = (err) => {
                reject(err);
            };

            client.socket.onclose = () => {
                console.log("WebSocket закрыт");
                resolve(null);
            };
        });
    }

    async setSettings(data) {
    const responseData = await this.getData("setSettings " + JSON.stringify(data));
    return this.settings.updateSettings(responseData);
    }

    async getSettings(message="settings"){
        this.socket.binaryType = "string";
        return this.getData(message);
    }

    async updateSettings(message="settings"){
        return this.settings.updateSettings(this.getSettings(message));
    }

    async getSParams(message="S"){
        this.socket.binaryType = "arraybuffer";
        const data = await this.getData(message);
        console.debug(data, this.settings);
        return await new WSResponse(data, this.settings);

    }

   async getData(message="") {
        return new Promise((resolve, reject) => {
            const handler = (event) => {
                console.debug("removeEventListener");
                this.socket.removeEventListener("message", handler);
                resolve(event.data);
            };
            this.socket.addEventListener("message", handler);
            this.socket.send(message);
        });
    }
    isSocketOpen() {
        return this.socket !== null && this.socket.readyState === WebSocket.OPEN;
    }
    close() {
        if (this.socket) {
            this.socket.close();
        }
    }
}

 export function checkWSClient(client){
     if (client instanceof WSClient &&
         (client.socket.readyState == WebSocket.CONNECTING || client.socket.readyState == WebSocket.OPEN)){
             return client;
     }
     return null;
 }

 export function getWSClient(address, settings){
     return new Promise((resolve, reject) => {
        const client = new WSClient(address, settings);

        client.socket.onopen = () => {
            console.log("WebSocket открыт");
            resolve(client);
        };

        client.socket.onerror = (err) => {
            reject(err);
        };

        client.socket.onclose = () => {
            console.log("WebSocket закрыт");
        };
    });
}


export async function getSParamWS(client, message="") {
    const data = await client.getData(message);
    console.log("typeof data:", typeof data,
            "instanceof ArrayBuffer:", data instanceof ArrayBuffer,
            "constructor:", data.constructor.name);
    let resp = new WSResponse(data);
    console.log(`Done S11=${resp.sParams[0][0]}`);
    return resp;
}
