import { Client } from './Client.js'
import { GraphicSParams } from './GraphicSParams.js'
import { GraphData } from './GraphData.js'
import { SettingsVNA } from './SettingsVNA.js'

// --- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ---
let timeOut = 100; // ← исправляет ReferenceError
const settings = new SettingsVNA();
let client = new Client(`http://${location.hostname}:${location.port}`, settings);

// --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function formatTime(time) {
    const formattedMinutes = String(Math.floor(time / 60)).padStart(2, '0');
    const formattedSeconds = String(time % 60).padStart(2, '0');
    return `${formattedMinutes}:${formattedSeconds}`;
}

function updateBar(time) {
    try {
        let btn = document.getElementById("btn-settings");
        if (time > -1) {
            document.getElementById("settingsIcon").src = "/src/control.png";
            let text = 'Устройство доступно';
            if (time > 0) {
                text = formatTime(time);
            }
            document.getElementById("btn-settings-text").textContent = text;
            btn.onclick = () => window.location.href = "/settings";
        } else {
            document.getElementById("settingsIcon").src = "/src/disconnect.png";
            document.getElementById("btn-settings-text").textContent = 'Управление у другого пользователя';
            btn.onclick = () => null;
        }
    } catch (error) {
        console.debug(error);
    }
}

// --- ОСНОВНОЙ ЦИКЛ ЗАГРУЗКИ ДАННЫХ ---
async function loop() {
    let graphics = new GraphicSParams(settings,
        [[new GraphData("S11", "S11"), new GraphData("S12", "S12")],
        [new GraphData("S21", "S21"), new GraphData("S22", "S22")]]
    );
    while (1) {
        try {
            let time = (await client.getJSON("/api/time_user")).remainingTime;
            timeOut = 5000;
            console.log("TIME:", time);
            updateBar(time);
            let change = settings.update(await client.getSettings());
            if (change) {
                console.debug("Update settings: ", settings);
                graphics.updateScales();
            }
            let data = await client.getSParams();
            graphics.takeResponse(data);
            await sleep(timeOut);
            console.debug("restart");
        } catch (error) {
            console.log("Timeout:", timeOut);
            console.error(error);
            await sleep(timeOut);
            timeOut = Math.min(30000, timeOut * 2);
        }
    }
}

// --- ЗАПУСК ЦИКЛА ---
loop();

// === ОБРАБОТЧИК ПКМ: ТОЧКА ПОД КУРСОРОМ + ПРАВИЛЬНЫЕ КООРДИНАТЫ ===
function attachContextMenuToGraphs() {
    document.querySelectorAll('[data-role="graph"]').forEach(graph => {
        if (!graph.dataset.contextMenuHandled) {
            graph.addEventListener('contextmenu', (e) => {
                e.preventDefault();

                const rect = graph.getBoundingClientRect();
                const xRel = e.clientX - rect.left;
                const yRel = e.clientY - rect.top;

                // Получаем layout
                const layout = graph.layout;
                if (!layout || !layout.xaxis || !layout.yaxis) {
                    console.warn("Layout не доступен");
                    return;
                }

                const xaxis = layout.xaxis;
                const yaxis = layout.yaxis;

                // --- ВЫЧИСЛЯЕМ РЕАЛЬНЫЕ КООРДИНАТЫ ---
                const xData = xaxis.range[0] + (xRel / rect.width) * (xaxis.range[1] - xaxis.range[0]);
                const yData = yaxis.range[1] - (yRel / rect.height) * (yaxis.range[1] - yaxis.range[0]);

                // --- СОЗДАЁМ ТОЧКУ ПОД КУРСОРОМ ---
                const point = document.createElement('div');
                point.className = 'plotly-click-point';
                point.style.cssText = `
                    position: absolute;
                    width: 10px;
                    height: 10px;
                    background: red;
                    border-radius: 50%;
                    transform: translate(-50%, -50%);
                    pointer-events: none;
                    left: ${xRel}px;
                    top: ${yRel}px;
                    z-index: 10;
                `;
                graph.appendChild(point);

                // --- СОЗДАЁМ ПОДПИСЬ С РЕАЛЬНЫМИ КООРДИНАТАМИ ---
                const coord = document.createElement('div');
                coord.className = 'plotly-click-coord';
                coord.textContent = `(${xData.toFixed(2)}, ${yData.toFixed(2)})`;
                coord.style.cssText = `
                    position: absolute;
                    background: rgba(0,0,0,0.9);
                    color: white;
                    padding: 2px 6px;
                    font-size: 12px;
                    border-radius: 4px;
                    pointer-events: none;
                    white-space: nowrap;
                    left: ${xRel + 12}px;
                    top: ${yRel - 20}px;
                    z-index: 11;
                `;
                graph.appendChild(coord);

                // Удаляем через 5 сек
                setTimeout(() => {
                    point.remove();
                    coord.remove();
                }, 5000);
            });
            graph.dataset.contextMenuHandled = "true";
        }
    });
}

attachContextMenuToGraphs();
setInterval(attachContextMenuToGraphs, 2000);