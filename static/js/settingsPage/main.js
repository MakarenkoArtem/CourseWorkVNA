import {Client} from '../Client.js'
import {SettingsVNA} from '../SettingsVNA.js'
import {updateButtons,calibration, decalibration, updateBar} from '../calibButtons.js'



const settings = new SettingsVNA();
let client = new Client(`http://${location.hostname}:${location.port}`,settings);
async function loop() {
    while (1){
        try{
            let time = await client.getRemainingTime()
            updateBar(time)
            let isChanged = settings.update(await client.getSettings())
            updateButtons(await client.getSettings())
            if (isChanged){
                console.debug("Update settings: ", settings)
            }
            let data = await client.getSParams()
            await client.delay()
        }catch(error){
            console.error(error)
            await client.delay(10000);
        }
    }
}

loop();
window.client = client;
window.calibration = calibration;