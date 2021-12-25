// @ts-check

function sumArray(array, callback = x => x) {
    var S = 0;
    for (let i of array)
        S += callback(i);
    return S
}

class Vector {
    static add(v, u) { return v.map((e, i) => e + u[i]) }
    static subtract(v, u) { return v.map((e, i) => e - u[i]) }
    static multiply(v, n) { return v.map(e => e * n) }
    static isOpposite(v, u) { return sumArray(Vector.add(v, u), x => x ** 2) < sumArray(v, x => x ** 2) + sumArray(u, x => x ** 2) }
    static getNorm = v => Math.hypot(v[0], v[1]);
    static setToNorm = (v, s) => (s /= Vector.getNorm(v), v.map(e => e * s));
    static draw(v, p, svgElement, stroke = "#000", strokeWidth = 1) { svgElement.insertAdjacentHTML('beforeend', `<path d="m ${p[0]},${p[1]} l ${v[0]},${v[1]}" stroke=${stroke} stroke-width=${strokeWidth} marker-end=url(#arrow) />`) }
}

class Point extends Vector {
    static distance(p, q) { return Math.hypot(p[0] - q[0], p[1] - q[1]) }
    static translate = Vector.add;
    static draw(p, svgElement) { svgElement.insertAdjacentHTML('beforeend', `<circle cx=${p[0] * 20 - 50} cy=${p[1] * 20 - 50} r=1 />`) }
}

class Droite {
    static Point_Vector = class extends Droite { constructor(p, v) { super(v[1], -v[0], v[0] * p[1] - v[1] * p[0]) } }
    static Point_Point = class extends Droite {
        constructor(p, q) { super(q[1] - p[1], p[0] - q[0], q[0] * p[1] - q[1] * p[0]) }
    }
    constructor(a, b, c) { this[0] = a; this[1] = b; this[2] = c }
    intersection(l) {
        const [a, b] = [this[0] * l[1], l[0] * this[1]];
        if (a !== b) {
            const x = (this[1] * l[2] - l[1] * this[2]) / (a - b);
            const y = (this[0] * l[2] - l[0] * this[2]) / (b - a);
            return [x, y];
        }
    }
    PV_intersection(P, v) {
        const b = this[0] * v[0] + this[1] * v[1];
        if (b) {
            const a = v[1] * P[0] - v[0] * P[1];
            return [
                (a * this[1] - this[2] * v[0]) / b,
                (-a * this[0] - this[2] * v[1]) / b
            ]
        }
    }
    closest(point) {
        const [a2, b2, ab] = [this[0] ** 2, this[1] ** 2, this[0] * this[1]];
        return [
            (b2 * point[0] - ab * point[1] - this[0] * this[2]) / (a2 + b2),
            (a2 * point[1] - ab * point[0] - this[1] * this[2]) / (a2 + b2)
        ]
    }
    translate(right = 0, down = 0) { this[2] -= right * this[0] + down * this[1] }
    homothetia(k) { this[2] *= k }
    draw(svgElement, view = [0, 0, 1, 1]) {
        const i = [
            this.intersection([0, -1, view[0]]),
            this.intersection([1, 0, -view[1]]),
            this.intersection([0, -1, view[2]]),
            this.intersection([1, 0, -view[3]])
        ].filter(e => e && e[0] >= view[0] && e[1] >= view[1] && e[0] <= view[2] && e[1] <= view[3]);
        const d = i.filter((e, j) => {
            for (let k = 0; k < j; k++)
                if (i[k][0] === e[0] && i[k][1] === e[1])
                    return false
            return true
        });
        console.log(d)
        i.length === 2 && svgElement.insertAdjacentHTML('beforeend', `<line x1=${i[0][0]} y1=${i[0][1]} x2=${i[1][0]} y2=${i[1][1]} />`)
    }
}

export { Vector, Point, Droite }