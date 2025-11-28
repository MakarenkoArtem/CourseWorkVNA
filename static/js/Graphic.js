import {GraphData} from './GraphData.js'

function range(start, end, step = 1) {
  return Array.from({ length: Math.ceil((end - start) / step) }, (_, i) => start + i * step);
}

export class Graphic{
    constructor(graphData){
        if (!(graphData instanceof GraphData)) {
            throw new TypeError("Ожидается GraphData");
        }
        // задаём layout
        const layout = {
            margin: { l: 0, r: 0, t: 0, b: 0 }, // левый, правый, верхний, нижний
            autosize: true,                           // авто размер
            // optional: чтобы график растягивался на всю ширину/высоту div
            width: document.getElementById(graphData.divId).clientWidth,
            height: document.getElementById(graphData.divId).clientHeight
        };
        const data = [{
            y: graphData.data, // Используем массив y
            mode: "lines",
            line: { color: 'orange' },
            type: 'scatter'
        }];
        Plotly.newPlot(graphData.divId, data, layout);
        changeScale(graphData);
    }
    changeScale(graphData){
        if (!(graphData instanceof GraphData)) {
            throw new TypeError("Ожидается GraphData");
        }
        var layout = {
            x: range(graphData.start, graphData.finish, (graphData.finish-graphData.start)/graphData.data.lenght),
            y: {range: [graphData.bottom, graphData.top]},
            type: 'scatter',
  line: {color: 'blue'}}
        };

        Plotly.relayout(graphData.divId, layout);
    }
}


var trace1 = {
  x: {range: [0, graph.data.lenght()]},
  y: [4, 5, 6],
  type: 'scatter',
  line: {color: 'red'}
};


var trace2 = {
  x: [20, 30, 40],
  y: [50, 60, 70],
  xaxis: 'x2',
  yaxis: 'y2',
  type: 'scatter'
};


var trace3 = {
  x: [300, 400, 500],
  y: [600, 700, 800],
  xaxis: 'x3',
  yaxis: 'y3',
  type: 'scatter'
};


var trace4 = {
  x: [4000, 5000, 6000],
  y: [7000, 8000, 9000],
  xaxis: 'x4',
  yaxis: 'y4',
  type: 'scatter'
};

var data = [trace1, trace2, trace3, trace4];

var layout = {
  grid: {rows: 2, columns: 2, pattern: 'independent'},
};

Plotly.newPlot('myDiv', data, layout);