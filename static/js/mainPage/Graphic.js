import {GraphData} from './GraphData.js'

function range(start, end, step = 1) {
  return Array.from({ length: Math.ceil((end - start) / step) }, (_, i) => start + i * step);
}

export class Graphic{
    constructor(data){
        if (!(data instanceof GraphData)) {
            throw new TypeError("Ожидается GraphData");
        }
        const layout = {
            margin: { l: 0, r: 0, t: 0, b: 0 }, // левый, правый, верхний, нижний
            autosize: true,                           // авто размер
            // optional: чтобы график растягивался на всю ширину/высоту div
        };
        const data = [{
            y: data.data, // Используем массив y
            mode: "lines",
            line: { color: 'orange' },
            type: 'scatter'
        }];
        Plotly.newPlot(data.divId, data, layout);
        changeScale(graphData);
    }
    /*
    changeScale(data){
        if (!(data instanceof GraphData)) {
            throw new TypeError("Ожидается GraphData");
        }
        var layout = {
            x: range(data.start, data.finish, (data.finish-data.start)/data.data.lenght),
            y: {range: [data.bottom, data.top]},
            type: 'scatter',
  line: {color: 'blue'}}
        };

        Plotly.relayout(graphData.divId, layout);
    }*/
}