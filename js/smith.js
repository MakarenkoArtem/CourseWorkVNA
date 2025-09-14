const canvas = document.getElementById('smith');
const ctx = canvas.getContext('2d');
const w = canvas.width;
const h = canvas.height;
const r = 250; // радиус круга
const cx = w/2;
const cy = h/2;

// Нарисовать единичный круг
ctx.beginPath();
ctx.arc(cx, cy, r, 0, 2*Math.PI);
ctx.strokeStyle = 'black';
ctx.lineWidth = 2;
ctx.stroke();

// Нарисовать несколько кругов постоянного сопротивления (пример)
const resistances = [0.2, 0.5, 1, 2, 5]; // нормированные
resistances.forEach(R => {
    const rad = r * R/(R+1); // формула для Смита
    ctx.beginPath();
    ctx.arc(cx + r*R/(R+1), cy, rad, 0, 2*Math.PI);
    ctx.strokeStyle = 'blue';
    ctx.stroke();
});

// Нарисовать окружности реактивности (пример)
const reactances = [0.2, 0.5, 1, 2, 5];
reactances.forEach(X => {
    const rad = r / (X+1); // примерная формула
    ctx.beginPath();
    ctx.arc(cx, cy + rad, r - rad, 0, 2*Math.PI);
    ctx.strokeStyle = 'red';
    ctx.stroke();
});
