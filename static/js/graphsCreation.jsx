import Plotly from "plotly.js-dist"

function getSettings(graph:GraphData){
    if (graph.host==null || graph.port==null){return false;}
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

function createGraph(titleDiv:Element, graph:GraphData){
    if(titleDiv == null || xFinish<=xStart || yBottom>=yTop || document.getElementById(title)){return false}
    const plot = Plotly.newPlot(title, [{
        y: graph.data,
        mode: "lines",
        line: {color: "lime"}
    }], {
        title: title,
        xaxis: {range: [0, graph.data.lenght()]},
        yaxis: {range: [0,100]}
    });
    return plot;
}

function show(graph:GraphData){
    if(plot == null){
        getSettings();
        createGraph(document.getElementById(graph.title), graph);

    }
}