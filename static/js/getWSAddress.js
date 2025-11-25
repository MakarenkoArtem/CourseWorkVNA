/*export class Server{
    constructor(address, websocketHost, websocketPort){
        this.address = address;
        this.websocketHost = websocketHost;
        this.websocketPort = websocketPort;
    }
    async function getWSAddress() {
        if (this.websocketHost!=null && this.websocketPort!=null){return [this.websocketHost, this.websocketPort];}
        const response = await fetch(this.address, {method: "GET"})

        if(response.ok){
            const data = await response.json();
            if (typeof data.host === 'string' && typeof data.port === 'number') {
                this.websocketHost = data.host;
                this.websocketPort = data.port;
                return [data.host, data.port];
            }
            throw new Error(`Data is not correct`)
            }
        throw new Error(`HTTP error ${response.status}`);
    }
}*/

export async function getWSAddress(address, websocketHost, websocketPort) {
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

export async function getCurrentTime(address, websocketHost, websocketPort) {
        if (websocketHost==null || websocketPort==null){
        throw new Error(`HTTP doesn not know host/port`);}
        const response = await fetch(address, {method: "GET"})

        if(response.ok){
            const data = await response.json();
            if (typeof data.remainingTime === 'number') {
                return data.remainingTime;
            }
            throw new Error(`Data is not correct`)
            }
        throw new Error(`HTTP error ${response.status}`);
    }