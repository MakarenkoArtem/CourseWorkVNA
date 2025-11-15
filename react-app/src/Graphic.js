import {GraphData} from './GraphData.js'

function range(start, end, step = 1) {
  return Array.from({ length: Math.ceil((end - start) / step) }, (_, i) => start + i * step);
}

export class Graphic{
    constructor(graphData){
        if (!(graphData instanceof GraphData)) {
            throw new TypeError("Ожидается GraphData");
        }

        Plotly.newPlot(graphData.divId, graphData.data, {});
        changeScale(graphData);
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
        Plotly.relayout(graphData.divId, layout);
    }
}


var trace1 = {
  x: {range: [0, graph.data.lenght()]},
  y: [4, 5, 6],
  type: 'scatter'
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