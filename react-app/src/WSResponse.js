export class WSResponse{
    constructor(bytes, settings){
            if (!(bytes instanceof ArrayBuffer)) {
                console.debug(`Пришел не ArrayBuffer: ${bytes}`)
                throw new TypeError("Ожидается ArrayBuffer");
            }

            console.debug(settings)
            const view = new DataView(bytes);
            const id = view.getInt32(0, true);
            if (settings!= null && id != settings.id){
                console.debug("Local id settings:", settings.id, " server id settings:", id);
                throw new TypeError("Настройки не совпадают с настройками на сервере");
            }
            if (bytes.byteLength < 4 + settings.countPoints * 2 * 2 * 4) {
                throw new Error(`Недостаточно данных в буфере(${bytes.byteLength}/${4+settings.countPoints * 2 * 2 * 4} байт)`);
            }

            this.sParams = Array.from({ length: 2 }, () =>
                Array.from({ length: 2 }, () =>
                    Array(settings.countPoints).fill(0)
                )
            );

            let offset;
            for (let i = 0; i < 2; i++) {
                for (let j = 0; j < 2; j++) {
                    for (let k = 0; k < settings.countPoints; k++) {
                        offset = 4+k*16+i*8+j*4;
                        this.sParams[i][j][k] = view.getFloat32(offset, true);
                    }
                }
            }
    }
}