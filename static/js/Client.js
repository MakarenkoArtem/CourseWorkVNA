import { Response } from './Response..js';

export class Client {
    constructor(address, settings) {
        this.timeout = 5000;
        this.address = address;
        this.settings = settings;
    }

    async getSettings(message = "settings") {
        return this.getJSON("/api/settings", message);
    }

    async updateSettings(message = "settings") {
        return this.settings.updateSettings(this.getSettings(message));
    }

    async getRemainingTime(path = "/api/time_user") {
        return (await this.getJSON(path)).remainingTime
    }

    async getSParams(path = "/api/get_data") {
        const data = await this.getJSON(path);
        return new Response(data);
    }
    async getJSON(path, message = "") {
        const response = await fetch(this.address + path, { method: "GET" })
        if (response.ok) {
            return await response.json();
        }
        throw new Error(`HTTP error ${response.status}`);
    }
    async delay(ms = this.timeout) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}
