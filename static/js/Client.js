 import {WSResponse} from './WSResponse.js';

export class Client {
    constructor(address, settings) {
        this.address = address;
        this.settings = settings;
    }

    async getSettings(message="settings"){
        return this.getJSON("/api/settings", message);
    }

    async updateSettings(message="settings"){
        return this.settings.updateSettings(this.getSettings(message));
    }

    async getSParams(path="/api/get_data"){
        const data = await this.getJSON(path);
        return new WSResponse(data);
    }
    async getJSON(path, message="") {
        const response = await fetch(this.address+path, {method: "GET"})
        if(response.ok){
            return await response.json();
        }
        throw new Error(`HTTP error ${response.status}`);
    }

   /*async getData(message="") {
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
    }*/
}

/*
export async function getSParamWS(client, message="") {
    const data = await client.getData(message);
    console.log("typeof data:", typeof data,
            "instanceof ArrayBuffer:", data instanceof ArrayBuffer,
            "constructor:", data.constructor.name);
    let resp = new WSResponse(data);
    console.log(`Done S11=${resp.sParams[0][0]}`);
    return resp;
}*/
