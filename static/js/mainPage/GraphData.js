export class GraphData{
    constructor(divId, title, settings, countPoints=500, plot=null){
        this.divId = divId;
        this.title = title;
        this.settings = settings;
        this.data = Array(countPoints).fill(0);

        this.start = 0;
        this.finish = 200;
        this.bottom = -60;
        this.top = 2;
    }
}