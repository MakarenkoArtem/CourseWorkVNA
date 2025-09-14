function getPoint(title) {
    return new Promise((resolve, reject) => {
        fetch(`${location.origin}/api/${title}`, {method: "GET"})
            .then(response => response.json())  // парсим JSON
            .then(data => {
                console.log(data);
                resolve(data['value']);
            })
            .catch(err => {
                console.error("Ошибка:", err)
                reject(err);
            });
    })
}
/*
function addPoint() {
    t += 0.1;
    y.shift(); // удаляем старую точку
    y.push(Math.sin(t)); // добавляем новую точку (сигнал)
    Plotly.update("scope1", {y: [y]}, {}, [0]);
}
*/
const N = 200; // количество точек на экране
let t = 0;
let y = Array(N).fill(0); // стартовые точки
/*
Plotly.newPlot("scope", [{
    y: y,
    mode: "lines",
    line: {color: "lime"}
}], {
    title: "Загруженность процессора",
    xaxis: {range: [0, N]},
    yaxis: {range: [0, 110]}
});

function connection() {
    return new Promise((resolve, reject) => {
        fetch("${location.origin}/connection", {method: "GET"})
            .then(response => response.json())  // парсим JSON
            .then(data => {
                resolve(data);
            })
            .catch(err => {
                reject(err);
            });
    })
}
*/
//while (1) {

//}

async function main() {
    try {
        let result = await getPoint("data");
        console.log('Получено: result =', result);

        t += 0.1;
        y.shift(); // удаляем старую точку
        y.push(result); // добавляем новую точку (сигнал)
        Plotly.update("cpu", {y: [y]}, {}, [0]);
    } catch (err) {
        console.error("Ошибка:", err)
    }
}

//const intervalId = setInterval(main, 50); // обновление каждые 50 мс
/*while(1) {
    main();
}*/


async function updateData(title) {
    try {
        let result = await getPoint(title);
        console.log('Получено: result =', result);
        dictData[title].shift(); // удаляем старую точку
        dictData[title].push(result); // добавляем новую точку (сигнал)
        Plotly.update(title, {y: [dictData[title]]}, {}, [0]);
    } catch (err) {
        console.error("Ошибка:", err)
    }
}

let dictData = {};

function start() {
    const divs = document.querySelectorAll('div[data-role="graph"]');
    const types = ["cpu", "time"]
    divs.forEach(div => {
        if (types.includes(div.id)) {
            if (!(div.id in dictData)) {
                dictData[div.id] = Array(N).fill(0);
                Plotly.newPlot(div.id, [{
                    y: dictData[div.id],
                    mode: "lines",
                    line: {color: "lime"}
                }], {
                    title: div.id,
                    xaxis: {range: [0, N]},
                    yaxis: {range: [0, 110]}
                });
            }
            updateData(div.id);
        }
    })
}

const interval = setInterval(start, 50); // обновление каждые 50 мс
