import {checkWSClient, getWSClient, getSParamWS, WSClient} from '../wsClient.js'
import {SettingsVNA} from '../SettingsVNA.js'

async function getAddress(address, websocketHost, websocketPort) {
    if (websocketHost!=null && websocketPort!=null){return [websocketHost, websocketPort];}
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

const form = document.getElementById('numsForm');
    const out = document.getElementById('out');
    const clearBtn = document.getElementById('clearBtn');

    function showError(id, text) {
      document.getElementById(id).textContent = text || '';
    }

    function validateIntegerNonNeg(val) {
      if (val === null || val === '') return 'Обязательно для заполнения';
      // Проверяем число и целое неотрицательное
      const n = Number(val);
      if (!Number.isFinite(n) || !Number.isInteger(n)) return 'Должно быть целым числом';
      if (n < 0) return 'Должно быть неотрицательным';
      return '';
    }

    form.addEventListener('submit', async (ev) => {
      ev.preventDefault();

      // Сброс ошибок
      showError('errA', '');
      showError('errB', '');
      showError('errC', '');
      out.hidden = true;

      const aVal = form.elements['a'].value.trim();
      const bVal = form.elements['b'].value.trim();
      const cVal = form.elements['c'].value.trim();

      const errA = validateIntegerNonNeg(aVal);
      const errB = validateIntegerNonNeg(bVal);
      const errC = validateIntegerNonNeg(cVal);

      let hasError = false;
      if (errA) { showError('errA', errA); hasError = true; }
      if (errB) { showError('errB', errB); hasError = true; }
      if (errC) { showError('errC', errC); hasError = true; }

      if (hasError) return;

      // Преобразуем в числа и используем
      const a = Number(aVal);
      const b = Number(bVal);
      const c = Number(cVal);

      out.hidden = false;
      out.textContent = `Введено: A=${a}, B=${b}, C=${c}`;
      // Здесь можно отправить на сервер или дальше обработать
      const settings = new SettingsVNA();
      let websocketHost, websocketPort
      [websocketHost, websocketPort] =
                await getAddress(`http://${location.hostname}:8000/api/websocket`, websocketHost, websocketPort);

      const client = await WSClient.create(`ws://${websocketHost}:${websocketPort}`, settings);
      client.setSettings({"id": 101, "minFrequency": a, "maxFrequency": b, "countPoints": c})
      window.location.assign("/");
    });

    clearBtn.addEventListener('click', () => {
      form.reset();
      showError('errA', ''); showError('errB', ''); showError('errC', '');
      out.hidden = true;
    });