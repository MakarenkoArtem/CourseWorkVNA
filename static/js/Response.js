export class Response{
    constructor(data){
        this.sParams = Array.from({ length: 2 }, () =>
                Array.from({ length: 2 }, () => 0
                )
            );
        this.sParams[0][0] = data.S11;
        this.sParams[0][1] = data.S12;
        this.sParams[1][0] = data.S21;
        this.sParams[1][1] = data.S22;
    }
}