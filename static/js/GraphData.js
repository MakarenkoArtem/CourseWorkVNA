export class GraphData{
    constructor(divId, title, host, port, settings, countPoints=500, plot=null){
        this.divId = divId;
        this.title = title;
        this.host = host;
        this.port = port;
        this.settings = settings;
        this.data = Array(countPoints).fill(0);

        this.start = 0;
        this.finish = 200;
        this.bottom = 0;
        this.top = 100;
    }
}