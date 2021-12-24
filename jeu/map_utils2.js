// @ts-check

import { Vector, Point, Droite } from './math_utils.js';

function tuple(a) {
    return Object.freeze(a)
}

class Wall {
    constructor(p, v) {
        this.line = new Droite(v[0], v[1], -(v[0] * p[0] + v[1] * p[1]))
        const hypot = Math.hypot(...v)
        this.p = p;
        this.vector = tuple(v.map(e => e / hypot))
    }
    draw(svgElement) {
        const i1 = this.line.intersection([0, -1, 0]) || this.line.intersection([1, 0, 0])
        const i2 = this.line.intersection([0, -1, 1]) || this.line.intersection([1, 0, -1])
        const j1 = Vector.add(i1, this.vector.map(e => -e * 5))
        const j2 = Vector.add(i2, this.vector.map(e => -e * 5))
        svgElement.insertAdjacentHTML('beforeend', `<path d="M ${j1[0]},${j1[1]} L ${i1[0]},${i1[1]} L ${i2[0]},${i2[1]} L ${j2[0]},${j2[1]}" />`)
    }
    static AutoConstructed = class {
        constructor(constructedwall) {
            for (let i in constructedwall) {
                this[i] = constructedwall[i]
            }
        }
    }
    clone() { return new Wall.AutoConstructed(this) }
}

class MAP {
    static marching_squares = [
        [],
        [[[0, .5], [.5, 1], [0, 1]]],
        [[[.5, 1], [1, .5], [1, 1]]],
        [[[0, .5], [1, .5], [1, 1], [0, 1]]],
        [[[1, .5], [.5, 0], [1, 0]]],
        [[[1, .5], [.5, 0], [1, 0]], [[0, .5], [.5, 1], [0, 1]]],
        [[[.5, 0], [1, 0], [1, 1], [.5, 1]]],
        [[[0, .5], [.5, 0], [1, 0], [1, 1], [0, 1]]],
        [[[0, 0], [.5, 0], [0, .5]]],
        [[[0, 0], [.5, 0], [.5, 1], [0, 1]]],
        [[[0, 0], [.5, 0], [0, .5]], [[.5, 1], [1, .5], [1, 1]]],
        [[[0, 0], [.5, 0], [1, .5], [1, 1], [0, 1]]],
        [[[0, 0], [1, 0], [1, .5], [0, .5]]],
        [[[0, 0], [1, 0], [1, .5], [.5, 1], [0, 1]]],
        [[[0, 0], [1, 0], [1, 1], [.5, 1], [0, .5]]],
        [[[0, 0], [1, 0], [1, 1], [0, 1]]]
    ]
    static WALL = {};
    static add_WALL(r) {
        return MAP.WALL[r] || (MAP.WALL[r] = [
            [],
            [new Wall([0, .5 - r], [1, -1])],
            [new Wall([1, .5 - r], [-1, -1])],
            [new Wall([0, .5 - r], [0, -1])],
            [new Wall([1, .5 + r], [-1, 1])],
            [new Wall([1, .5 + r], [-1, 1]), new Wall([0, .5 - r], [1, -1])],
            [new Wall([.5 - r, 0], [-1, 0])],
            [new Wall([0, .5 - r], [-1, -1])],
            [new Wall([0, .5 + r], [1, 1])],
            [new Wall([.5 + r, 0], [1, 0])],
            [new Wall([0, .5 + r], [1, 1]), new Wall([1, .5 - r], [-1, -1])],
            [new Wall([.5 + r, 0], [1, -1])],
            [new Wall([0, .5 + r], [0, 1])],
            [new Wall([1, .5 + r], [1, 1])],
            [new Wall([0, .5 + r], [-1, 1])],
            []
        ])
    }
    static types = [
        // [slippery: number]
        [0, '#888'], // basic groud: not slippery at all, grey
        [.75, '#0ff']   // ice: very slippery, cyan (just a test)
    ];
    constructor(string, l, svg, view = [[-50, -50], [50, 50]]) {
        this.l = l
        this.matrix = [];
        string.split(',').map((e, i) => { this.matrix[i] = []; for (let c in e) this.matrix[i][Number(c)] = Number(e[c]) });
        console.log(this.matrix)
        this.mat_d = [this.matrix[0].length, this.matrix.length];
        this.wheels = [];
        this.relative = [50, 50];
        this.view = view;
        this.svg = svg;
        svg.setAttribute('viewBox', `${this.view[0][0]} ${this.view[0][1]} ${this.view[1][0] - this.view[0][0]} ${this.view[1][1] - this.view[0][1]}`)
    }
    addWheel(wheel) {
        MAP.add_WALL(wheel.r / this.l);
        wheel.map = this;
        this.wheels.push(wheel)
    }
    draw() {
        const [minX, minY] = this.findPointCase(Point.translate(this.relative, this.view[0])).map(e => Math.max(0, e));
        const [maxX, maxY] = this.findPointCase(Point.translate(this.relative, this.view[1])).map((e, i) => Math.min(e + 1, this.mat_d[i] - 1));
        var strs = new Array(MAP.types.length).fill('');
        for (let y = minY; y < maxY; y++) {
            for (let x = minX; x < maxX; x++) {
                const bl = [this.matrix[y][x], this.matrix[y][x + 1], this.matrix[y + 1][x + 1], this.matrix[y + 1][x]];
                for (let k = 1; k < MAP.types.length + 1; k++) {
                    if (!bl.every(e => e !== k)) {
                        const [a, b, c, d] = bl.map(e => Number(e && e <= k));
                        const path = MAP.marching_squares[a * 8 + b * 4 + c * 2 + d];
                        path.forEach(points => {
                            points.forEach((point, index) => {
                                strs[k - 1] += (index === 0 ? ' M ' : ' L ') + ((point[0] + x) * this.l - this.relative[0]) + ',' + ((point[1] + y) * this.l - this.relative[1])
                            })
                        })
                    }
                }
            }
        }
        console.log(strs)
        strs.forEach((str, i) => {
            this.svg.innerHTML = `<path d="${str}" fill="${MAP.types[i][1]}" />` + this.svg.innerHTML;
        })
    }
    findPointCase(p) {
        return p.map(e => Math.floor(e / this.l));
    }
    vectorCases(point, vector) {
        // On prend un point et un vecteur puis on renvoie toutes les cases de la map par lesquelles passe le vecteur partant du point
        var [p1, p2] = [point, Vector.add(point, vector)].map(e => this.findPointCase(e));
        const r = [];
        const drt = new Droite.Point_Vector(Vector.multiply(point, 1 / this.l), Vector.multiply(vector, 1 / this.l));
        if (p1[0] === p2[0]) {
            const index = p1[1] > p2[1] ? -1 : 1;
            for (let i = p1[1]; i !== p2[1] + index; i += index)
                r.push([p1[0], i])
            return r
        }
        if (p1[1] === p2[1]) {
            const index = p1[0] > p2[0] ? -1 : 1;
            for (let i = p1[0]; i !== p2[0] + index; i += index)
                r.push([i, p1[1]])
            return r
        }
        // if (p1[0] === p2[0] && p1[1] === p2[1]) return [[p1[0], p1[1]]]
        if (Math.abs(p1[0] - p2[0]) > Math.abs(p1[1] - p2[1])) {
            if (vector[0] < 0) { [p1, p2] = [p2, p1] }
            // console.log(p1, p2)
            var offsetX = p1[0];
            const index = p1[1] > p2[1] ? -1 : 1;
            for (let y = p1[1]; y !== p2[1] + index; y += index) {
                const nX = Math.floor(new Droite(0, 1, -y - index).intersection(drt)[0]);
                // console.log(offsetX, nX, "1", new Droite(0, 1, -y - index).intersection(drt)[0]);
                for (let x = offsetX; x !== nX + 1 && x !== p2[0] + 1; x++) {
                    // console.log(x, y);
                    r.push([x, y])
                }
                offsetX = nX;
            }
            return vector[0] < 0 ? r.reverse() : r
        } else {
            if (vector[1] < 0) { [p1, p2] = [p2, p1] }
            // console.log(p1, p2)
            var offsetY = p1[1];
            const index = p1[0] > p2[0] ? -1 : 1;
            for (let x = p1[0]; x !== p2[0] + index; x += index) {
                const nY = Math.floor(new Droite(1, 0, -x - (index === 1 ? index : 0)).intersection(drt)[1]);
                // console.log(offsetY, nY, "1", new Droite(1, 0, -x - index).intersection(drt)[0]);
                for (let y = offsetY; y !== nY + 1 && y !== p2[1] + 1; y++) {
                    // console.log(x, y);
                    r.push([x, y])
                }
                offsetY = nY;
            }
            return vector[1] < 0 ? r.reverse() : r
        }
    }
    readMatrixCase(point, radius) {
        radius /= this.l
        const i = point[1], j = point[0];
        // console.log(point, i, j, radius);
        const bl = [this.matrix[i][j], this.matrix[i][j + 1], this.matrix[i + 1][j + 1], this.matrix[i + 1][j]];
        const walls = [];
        for (let k = 1; k < MAP.types.length + 1; k++) {
            if (!bl.every(e => e !== k)) {
                const [a, b, c, d] = bl.map(e => Number(e && e <= k));
                // console.log(bl, [a, b, c, d], a * 8 + b * 4 + c * 2 + d)
                // console.log(MAP.WALL[radius], MAP.WALL[radius][a * 8 + b * 4 + c * 2 + d])
                const addwalls = MAP.WALL[radius][a * 8 + b * 4 + c * 2 + d];
                addwalls.forEach(wall => {
                    wall = wall.clone();
                    wall.line.translate(i, j);
                    wall.type = k - 1;
                    walls.push(wall);
                })
            }
        }
        return walls
    }
    withinCase(point, cas) {
        return point[0] >= cas[0] && point[0] <= cas[0] + 1 && point[1] >= cas[1] && point[1] <= cas[1] + 1
    }
    withinMap(cas) {
        return cas[0] > -1 && cas[0] < this.mat_d[0] - 1 && cas[1] > -1 && cas[1] < this.mat_d[0] - 1
    }
    drawCircle([x, y], r = 1, c = "#000") {
        this.svg.insertAdjacentHTML('beforeend', `<circle cx=${x - this.relative[0]} cy=${y - this.relative[1]} r=${r} fill=${c} />`)
    }
    drawLine([x1, y1], [x2, y2], w, c = "#000") {
        this.svg.insertAdjacentHTML('beforeend', `<line x1=${x1 - this.relative[0]} x2=${x2 - this.relative[0]} y1=${y1 - this.relative[1]} y2=${y2 - this.relative[1]} stroke-width=${w} stroke=${c} />`)
    }
    drawLineLine(l, t = [0, 0]) {
        new Droite(
            l[0],
            l[1],
            l[2] * this.l + (t[0] * this.l - this.relative[0]) * l[1] + (t[1] * this.l - this.relative[1]) * l[0]
        ).draw(this.svg, [...this.view[0], ...this.view[1]])
    }
}

class Wheel {
    constructor(pos, r) {
        this.pos = pos;
        this.r = r;
        this.vector = [0, 0]
        this.weight = [0, 1];
        this.map = undefined;
    }
    update() {
        var point = this.pos;
        var vector = this.vector;
        Vector.draw(vector, point, this.map.svg)
        var size = Vector.getNorm(this.vector);
        var Size = size;
        const map = this.map;
        var index = 0;
        while (true && index < 3) {
            console.groupCollapsed(index.toString());
            console.log(point, vector)
            const cases = map.vectorCases(point, vector).filter(c => this.map.withinMap(c));
            const droite = new Droite.Point_Vector(Vector.multiply(point, 1 / this.map.l), vector);
            var mur = undefined;
            console.log(cases)
            for (let cas of cases) {
                console.groupCollapsed(cas)
                var murs = this.map.readMatrixCase(cas, this.r)
                console.log(murs)
                murs = murs.filter(mur => Vector.isOpposite(vector, mur.vector))
                murs = murs.map(mur=>mur.line.translate(...cas))
                console.log(murs)
                murs.forEach(mur => {
                    // console.log(Vector.add(Vector.multiply(mur.p, this.map.l),[-50,-50]),)
                    this.map.drawLineLine(mur.line, cas)
                    // new Droite.Point_Vector(Vector.add(Vector.multiply(mur.p, this.map.l), [0, 0]), [-mur.vector[1], mur.vector[0]]).draw(this.map.svg, [-50, -50, 50, 50])
                })

                murs = murs.map(mur => [mur, droite.intersection(mur.line)])
                // console.log(murs)

                // murs.forEach(mur => {
                //     Point.draw(mur[1], this.map.svg)
                // })
                murs = murs.filter(mur => this.map.withinCase(mur[1], cas))
                console.log(murs)
                murs = murs.map(mur => [...mur, Point.distance(Vector.multiply(point, 1 / this.map.l), mur[1])])
                murs = murs.sort((mur1, mur2) => mur1[2] - mur2[2]);
                // console.log(murs)
                console.groupEnd()
                if (murs.length === 1) {
                    mur = murs[0];
                    break;
                }
            }
            if (!mur) break;
            console.log('mur', mur)
            const R = Vector.multiply(mur[1], this.map.l);
            const Q = Vector.multiply(mur[0].line.closest(point), this.map.l);
            const PR = mur[2] * this.map.l;//Point.distance(point, R);
            const QR = Point.distance(R, Q);                 // # merci Thalès
            const v_QR = Vector.subtract(R, Q);
            console.log('R', R)
            console.log('Q', Q)
            console.log('PR', PR)
            console.log('QR', QR)
            console.log('v_QR', v_QR)

            const sin = QR / PR;
            Size *= sin;
            console.log(size)
            size = (size - PR) * sin;
            console.log('size', size)
            vector = Vector.setToNorm(v_QR, size);
            Vector.draw(vector, Point.translate(R, [-50, -50]), this.map.svg, "#00f", .4)
            // this.map.svg.insertAdjacentHTML('beforeend', `<line x1=${R[0] - 50} y1=${R[1] - 50} x2=${R[0] - 50 + vector[0]} y2=${R[1] - 50 + vector[1]} style="stroke:#00f;stroke-width:.4" />`)
            // changer la varibale`vector` en fonction du vecteur du`mur` et de la distance où se trouve le point issu de la translation de`point` par le vecteur`vector` partant du point`nouveau_point`
            point = R;
            this.map.drawCircle(point)
            console.groupEnd()
            index++;
            // break; // to be removed later
            debugger;
        }
        this.pos = Vector.add(point, vector);
        this.vector = Vector.setToNorm(vector, Size);
        this.vector = Vector.add(this.vector, this.weight);
        this.vector = Vector.multiply(this.vector, .99);
    }
    display() {
        this.map?.drawCircle?.(this.pos, this.r, "#f00")
    }
    drawVec() {
        this.map?.drawLine?.(this.pos, Vector.add(this.pos, this.vector), this.r / 10, "#ff0")
    }
}

export { Wall, MAP, Wheel }