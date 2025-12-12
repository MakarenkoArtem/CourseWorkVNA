import {Client} from '../Client.js'
import {Response} from '../Response.js'
import {SettingsVNA} from '../SettingsVNA.js'
import {GraphicSParams} from './GraphicSParams.js'
import {GraphData} from './GraphData.js'
import {updateButtons, calibration, decalibration} from '../calibButtons.js'

// --- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ---
const settings = new SettingsVNA();
let client = new Client(`http://${location.hostname}:${location.port}`,settings);


function formatTime(time) {
    const formattedMinutes = String(Math.floor(time / 60)).padStart(2, '0');
    const formattedSeconds = String(time % 60).padStart(2, '0');
    return `${formattedMinutes}:${formattedSeconds}`;
}

function updateBar(time){
    try{
        let btn = document.getElementById("btn-settings")
        if(time>-1){
            document.getElementById("settingsIcon").src = "/static/img/control.png"
            let text='Устройсво доступно';
            if (time>0){
                text=formatTime(time)
            }
            document.getElementById("btn-settings-text").textContent = text;
            btn.onclick = () => window.location.href = "/settings";
        }else{
            document.getElementById("settingsIcon").src = "/static/img/disconnect.png"
            document.getElementById("btn-settings-text").textContent = 'Управление у другого пользователя'
            btn.onclick = () => null;
        }
    }catch(error){
        console.debug(error)
    }
}

// --- ОСНОВНОЙ ЦИКЛ ЗАГРУЗКИ ДАННЫХ ---
async function loop() {
    let graphics = new GraphicSParams(settings,
                                      [[new GraphData("S11", "S11"), new GraphData("S12", "S12")],
                                      [new GraphData("S21", "S21"), new GraphData("S22", "S22")]]);
    while (1){
        try{
            let time = await client.getRemainingTime()
            updateBar(time)
            let isChanged = settings.update(await client.getSettings())
            updateButtons(await client.getSettings())
            if (isChanged){
                console.debug("Update settings: ", settings)
                graphics.updateScales()
            }
            let data = await client.getSParams()
            graphics.takeResponse(data)
            await client.delay()
        }catch(error){
            console.error(error)
            await client.delay(10000);
        }
    }
}

// --- ЗАПУСК ЦИКЛА ---
loop();
window.client = client;
window.calibration = calibration;

// === ОБРАБОТЧИК ПКМ ДЛЯ ВСЕХ ГРАФИКОВ ===
function attachContextMenuToGraphs() {
    document.querySelectorAll('[data-role="graph"]').forEach(graph => {
        if (!graph.dataset.contextMenuHandled) {
            graph.addEventListener('contextmenu', async (e) => {
                e.preventDefault();

                const fullLayout = graph._fullLayout;
                if (!fullLayout) {
                    console.warn("График ещё не проинициализирован");
                    return;
                }

                const xaxis = fullLayout.xaxis;
                const yaxis = fullLayout.yaxis;

                // Проверяем, что оси инициализированы
                if (!xaxis || !yaxis || xaxis._length === undefined || yaxis._length === undefined) {
                    console.warn("Оси графика не готовы");
                    return;
                }

                // Получаем смещения и размеры области графика (plot area)
                const plotLeft = xaxis._offset;
                const plotTop = yaxis._offset;
                const plotWidth = xaxis._length;
                const plotHeight = yaxis._length;

                // Позиция курсора относительно контейнера графика
                const rect = graph.getBoundingClientRect();
                const xRel = e.clientX - rect.left;
                const yRel = e.clientY - rect.top;

                // Проверяем, попадает ли клик в plot area
                if (xRel < plotLeft || xRel > plotLeft + plotWidth ||
                    yRel < plotTop || yRel > plotTop + plotHeight) {
                    return; // Игнорируем клик вне графика
                }

                // Преобразуем пиксели → данные
                const xFraction = (xRel - plotLeft) / plotWidth;
                const yFraction = 1 - (yRel - plotTop) / plotHeight; // y идёт сверху вниз

                const xMin = xaxis.range[0];
                const xMax = xaxis.range[1];
                const yMin = yaxis.range[0];
                const yMax = yaxis.range[1];

                const xData = xMin + xFraction * (xMax - xMin);
                const yData = yMin + yFraction * (yMax - yMin);

                // Добавляем точку
                await Plotly.addTraces(graph, {
                    x: [xData],
                    y: [yData],
                    mode: 'markers',
                    marker: { size: 10, color: 'red' },
                    showlegend: false,
                    name: 'click-point'
                });

                // Подпись
                const coord = document.createElement('div');
                coord.className = 'plotly-click-coord';
                coord.textContent = `(${xData.toFixed(2)}, ${yData.toFixed(2)})`;
                coord.style.cssText = `
                    position: absolute;
                    background: rgba(0,0,0,0.8);
                    color: white;
                    padding: 2px 6px;
                    font-size: 12px;
                    border-radius: 4px;
                    pointer-events: none;
                    white-space: nowrap;
                    left: ${e.clientX - rect.left + 12}px;
                    top: ${e.clientY - rect.top - 20}px;
                    z-index: 10;
                `;
                graph.appendChild(coord);

                setTimeout(() => {
                    if (coord.parentNode === graph) coord.remove();
                }, 3000);
            });

            graph.dataset.contextMenuHandled = "true";
        }
    });
}

// Запускаем сразу и повторяем, если графики рисуются асинхронно
attachContextMenuToGraphs();
setInterval(attachContextMenuToGraphs, 2000);