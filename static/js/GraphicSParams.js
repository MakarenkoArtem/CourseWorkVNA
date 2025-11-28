import {GraphData} from './GraphData.js'
import {WSResponse} from './WSResponse.js'

function range(start, end, step = 1) {
  return Array.from({ length: Math.ceil((end - start) / step) }, (_, i) => start + i * step);
}

export class GraphicSParams{
    constructor(sGraphics){
        if (!Array.isArray(sGraphics) || !sGraphics[0].every(item => item instanceof GraphData)) {
            throw new TypeError("Ожидается GraphData");
        }
        this.graphics=sGraphics;
        console.log(this.graphics);
        this.initPlots();
    }
     async initPlots() {
        for (let i = 0; i < 2; ++i) {
            for (let j = 0; j < 2; ++j) {

                console.log("График создан:", i, j);
                let g = this.graphics[i][j];
                console.log("Создаём график:", g.divId);

                await Plotly.newPlot(g.divId, [{
                    y: Array(200).fill(0),
                    mode: "lines",
                    line: { color: "blue" }
                }], {
                    title: g.title,
                }, { responsive: true });

                console.log("График создан:", g.divId);
                this.changeScale(g);
                console.log("Масштаб изменён:", g.divId);
            }
        }
    }

    changeScale(graphData){
        if (!(graphData instanceof GraphData)) {
            throw new TypeError("Ожидается GraphData");
        }

        var layout = {
            x: range(graphData.start, graphData.finish, (graphData.finish-graphData.start)/graphData.data.lenght),
            y: {range: [graphData.bottom, graphData.top]},
            type: 'scatter'
        };
        Plotly.relayout(document.getElementById(graphData.divId), {
            'xaxis.range': [graphData.start, graphData.finish],
            'yaxis.range': [graphData.bottom, graphData.top]
        });
        /*Plotly.relayout(document.getElementById(graphData.divId), layout)
            .then(() => console.log(`Масштаб обновлён: ${graphData.divId}`))
            .catch(err => console.error(`Ошибка relayout для ${graphData.divId}:`, err));*/
    }

    updateScale(graphData){
    const minF =graphData.settings.minFrequency
    const maxF = graphData.settings.maxFrequency
    const countPoints = graphData.settings.countPoints
    const step = (maxF - minF) / countPoints;
    const xValues = [];
    for(let v = minF; v <= maxF; v += step){
        xValues.push(v);
    }
        var layout = {
            x: range(minF, maxF, step),
            y: {range: [graphData.bottom, graphData.top]},
            type: 'scatter'
        };
        /*Plotly.relayout(document.getElementById(graphData.divId), {
            'xaxis.range': [minF, maxF],
            'yaxis.range': [graphData.bottom, graphData.top]
        });*/

        Plotly.update(
        document.getElementById(graphData.divId),
        { x: [xValues], y: [graphData.data] }, // x и y одновременно
        {
            'xaxis.range': [minF, maxF],
            'yaxis.range': [graphData.bottom, graphData.top]
        }
    );
    }
   takeResponse(resp){
        if (!(resp instanceof WSResponse)) {
            throw new TypeError("Ожидается WSResponse");
        }
        this.updateScale(this.graphics[0][0]);
        this.updateScale(this.graphics[0][1]);
        this.updateScale(this.graphics[1][0]);
        this.updateScale(this.graphics[1][1]);

        this.graphics[0][0].data=resp.sParams[0][0];
        this.graphics[0][1].data=resp.sParams[0][1];
        this.graphics[1][0].data=resp.sParams[1][0];
        this.graphics[1][1].data=resp.sParams[1][1];
        Plotly.update(this.graphics[0][0].divId,
        {y: [this.graphics[0][0].data]}, {}, [0]);
        Plotly.update(this.graphics[0][1].divId,
        {y: [this.graphics[0][1].data]}, {}, [0]);
        Plotly.update(this.graphics[1][0].divId,
        {y: [this.graphics[1][0].data]}, {}, [0]);
        Plotly.update(this.graphics[1][1].divId,
        {y: [this.graphics[1][1].data]}, {}, [0]);
   }
}