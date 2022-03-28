// @ts-check

function tuple(a) {
    return Object.freeze(a)
}

class Vector {
    static add(v, u) { return v.map((e, i) => e + u[i]) }
    static subtract(v, u) { return v.map((e, i) => e - u[i]) }
    static multiply(v, n) { return v.map(e => e * n) }
    constructor(...d) {
        d.forEach((e, i) => this[i] = e);
        this.length = d.length;
    }
    map(callback = (x, i) => x) {
        const r = new Vector();
        for (let i = 0; i < this.length; i++) r[i] = callback(this[i], i);
        r.length = this.length;
        return r;
    }
    array(callback = (x, i) => x) {
        const r = [];
        for (let i = 0; i < this.length; i++) r[i] = callback(this[i], i)
        return r
    }
    multiply(n) { return this.map(a => a * n) }
    add(v) { return this.map((a, i) => a + v[i]) }
    subtract(v) { return this.map((a, i) => a - v[i]) }
    isOpposite(v) { return new Array(this.length).fill(0).map((_, i) => (this[i] + v[i]) ** 2).reduce((s, p) => s + p) < this[this instanceof Vector ? 'array' : 'map'](e => e ** 2).reduce((s, p) => s + p) + v[v instanceof Vector ? 'array' : 'map'](e => e ** 2).reduce((s, p) => s + p) }
    static getNorm = v => Math.hypot(v[0], v[1]);
    static setToNorm = (v, s) => (s /= Vector.getNorm(v), v.map(e => e * s));
}

class Point extends Vector {
    static distance(p, q) {
        return Math.hypot(p[0] - q[0], p[1] - q[1])
    }
    distance(p) { // returns the distance between this point and another point
        return Math.hypot(this[0] - p[0], this[1] - p[1])
    }
    droite(point) { return new Droite.Point_Vector(this, [this[0] - point[0], this[1] - point[1]]) }
    translate = this.add;
    draw(svgElement) {
        svgElement.insertAdjacentHTML('beforeend', `<circle cx=${this[0] * 20 - 50} cy=${this[1] * 20 - 50} r=1 />`)
    }
}

class Droite {
    static Point_Vector = class extends Droite {
        constructor(p, v) { super(v[1], -v[0], v[0] * p[1] - v[1] * p[0]) }
    }
    static sin(h, a) {
        // o.add(a) === h.multiply(k)
        // o[0]+a[0] === k*h[0]
        // o[1]+a[1] === k*h[1] 
        // o[0]**2+o[1]**2 + a[0]**2+a[1]**2 === k**2(h[0]**2+h[1]**2)

    }
    constructor(a, b, c) { // ax + by + c = 0
        // if (!(a || b)) throw Error('Impossible to make a line with the first two coefficients equal to 0')
        this[0] = a
        this[1] = b
        this[2] = c
    }
    intersection(l) {
        // ax  + by  + c  = 0
        // a'x + b'y + c' = 0  
        // (ab' - a'b)x + b'c - bc' = 0
        // x = (bc'-b'c)/(ab'-a'b)
        // (a'b - ab')y + a'c - ac' = 0
        // y = (ac'-a'c)/(a'b-ab')
        if (this[0] * l[1] !== l[0] * this[1]) {
            const x = (this[1] * l[2] - l[1] * this[2]) / (this[0] * l[1] - l[0] * this[1]);
            const y = (this[0] * l[2] - l[0] * this[2]) / (l[0] * this[1] - this[0] * l[1]);
            return new Point(x, y);
        }
    }
    PV_intersection(P, v) {
        const b = this[0] * v[0] + this[1] * v[1];
        if (b) {
            const a = v[1] * P[0] - v[0] * P[1];
            return new Point(
                (a * this[1] - this[2] * v[0]) / b,
                (-a * this[0] - this[2] * v[1]) / b
            )
        }
    }
    closest(point) {
        const [a2, b2, ab] = [this[0] ** 2, this[1] ** 2, this[0] * this[1]];
        return new Point(
            (b2 * point[0] - ab * point[1] - this[0] * this[2]) / (a2 + b2),
            (a2 * point[1] - ab * point[0] - this[1] * this[2]) / (a2 + b2)
        )
    }
    translate(right = 0, down = 0) {
        this[2] -= right * this[0] + down * this[1]
    }
    homothetia(k) { this[2] *= k }
    draw(svgElement, view = [0, 0, 1, 1]) {
        console.log(this)
        const i = [
            this.intersection([0, -1, view[0]]),
            this.intersection([1, 0, -view[1]]),
            this.intersection([0, -1, view[2]]),
            this.intersection([1, 0, -view[3]])]
            .filter(e => e && e[0] >= view[0] && e[1] >= view[1] && e[0] <= view[2] && e[1] <= view[3]);
        console.log(i)
        i.length && svgElement.insertAdjacentHTML('beforeend', `<line x1=${i[0][0]} y1=${i[0][1]} x2=${i[1][0]} y2=${i[1][1]} />`)
    }
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
        const j1 = i1.add(this.vector.map(e => -e * 5))
        const j2 = i2.add(this.vector.map(e => -e * 5))
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
        /*0000*/[],
        /*0001*/[[[0, .5], [.5, 1], [0, 1]]],
        /*0010*/[[[.5, 1], [1, .5], [1, 1]]],
        /*0011*/[[[0, .5], [1, .5], [1, 1], [0, 1]]],
        /*0100*/[[[1, .5], [.5, 0], [1, 0]]],
        /*0101*/[[[1, .5], [.5, 0], [1, 0]], [[0, .5], [.5, 1], [0, 1]]],
        /*0110*/[[[.5, 0], [1, 0], [1, 1], [.5, 1]]],
        /*0111*/[[[0, .5], [.5, 0], [1, 0], [1, 1], [0, 1]]],
        /*1000*/[[[0, 0], [.5, 0], [0, .5]]],
        /*1001*/[[[0, 0], [.5, 0], [.5, 1], [0, 1]]],
        /*1010*/[[[0, 0], [.5, 0], [0, .5]], [[.5, 1], [1, .5], [1, 1]]],
        /*1011*/[[[0, 0], [.5, 0], [1, .5], [1, 1], [0, 1]]],
        /*1100*/[[[0, 0], [1, 0], [1, .5], [0, .5]]],
        /*1101*/[[[0, 0], [1, 0], [1, .5], [.5, 1], [0, 1]]],
        /*1110*/[[[0, 0], [1, 0], [1, 1], [.5, 1], [0, .5]]],
        /*1111*/[[[0, 0], [1, 0], [1, 1], [0, 1]]]
    ]
    static WALL = {};
    static add_WALL(r) {
        return MAP.WALL[r] || (MAP.WALL[r] = [
            /*0000*/[],
            /*0001*/[new Wall([0, .5 - r], [1, -1])],
            /*0010*/[new Wall([1, .5 - r], [-1, -1])],
            /*0011*/[new Wall([0, .5 - r], [0, -1])],
            /*0100*/[new Wall([1, .5 + r], [-1, 1])],
            /*0101*/[new Wall([1, .5 + r], [-1, 1]), new Wall([0, .5 - r], [1, -1])],
            /*0110*/[new Wall([.5 - r, 0], [-1, 0])],
            /*0111*/[new Wall([0, .5 - r], [-1, -1])],
            /*1000*/[new Wall([0, .5 + r], [1, 1])],
            /*1001*/[new Wall([.5 + r, 0], [1, 0])],
            /*1010*/[new Wall([0, .5 + r], [1, 1]), new Wall([1, .5 - r], [-1, -1])],
            /*1011*/[new Wall([.5 + r, 0], [1, -1])],
            /*1100*/[new Wall([0, .5 + r], [0, 1])],
            /*1101*/[new Wall([1, .5 + r], [1, 1])],
            /*1110*/[new Wall([0, .5 + r], [-1, 1])],
            /*1111*/[]
        ])
    }
    static types = [
        // [slippery: number]
        [0], // basic groud: not slippery at all
        [.75]   // ice: very slippery
    ];
    constructor(string, l, svg) {
        this.l = l
        this.matrix = [];
        string.split(',').map((e, i) => {
            this.matrix[i] = [];
            for (let c in e)
                this.matrix[i][Number(c)] = Number(e[c])
        });
        console.log(this.matrix)
        this.mat_d = [this.matrix[0].length, this.matrix.length];
        this.wheels = [];
        this.relative = new Point(50, 50);
        this.view = [new Vector(-50, -50), new Vector(50, 50)];
        this.svg = svg;
        svg.setAttribute('viewBox', `${this.view[0][0]} ${this.view[0][1]} ${this.view[1][0] - this.view[0][0]} ${this.view[1][1] - this.view[0][1]}`)
    }
    addWheel(wheel) {
        MAP.add_WALL(wheel.r / this.l);
        wheel.map = this;
        this.wheels.push(wheel)
    }
    draw() {
        const [minX, minY] = this.findPointCase(this.relative.translate(this.view[0])).map(e => Math.max(0, e));
        const [maxX, maxY] = this.findPointCase(this.relative.translate(this.view[1])).map((e, i) => Math.min(e + 1, this.mat_d[i] - 1));
        console.log(minX, minY, maxX, maxY)
        var str = '';
        for (let y = minY; y < maxY; y++) {
            for (let x = minX; x < maxX; x++) {
                const [i, j, k, l] = [this.matrix[y][x], this.matrix[y][x + 1], this.matrix[y + 1][x + 1], this.matrix[y + 1][x]]
                const marching_square = MAP.marching_squares[i * 8 + j * 4 + k * 2 + l]
                // console.log(marching_square, i * 8 + j * 4 + k * 2 + l, i, j, k, l)
                marching_square.forEach(points => {
                    points.forEach((point, index) => {
                        str += (index === 0 ? ' M ' : ' L ') + ((point[0] + x) * this.l - this.relative[0]) + ',' + ((point[1] + y) * this.l - this.relative[1]);
                    })
                })
            }
        }
        this.svg.innerHTML = `<path d="${str}" />`;
    }
    findPointCase(p) {
        // On prend un point et on renvoie la case de la map sur laquelle se trouve ce point
        return p instanceof Vector ? p.array(e => Math.floor(e / this.l)) : p.map(e => Math.floor(e / this.l))
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
            console.log(p1, p2)
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
        console.log(point, i, j, radius);
        const bl = [this.matrix[i][j], this.matrix[i][j + 1], this.matrix[i + 1][j + 1], this.matrix[i + 1][j]];
        const walls = [];
        for (let k = 1; k < MAP.types.length + 1; k++) {
            if (!bl.every(e => e !== k)) {
                const [a, b, c, d] = bl.map(e => Number(e && e <= k));
                console.log(bl, [a, b, c, d], a * 8 + b * 4 + c * 2 + d)
                console.log(MAP.WALL[radius], MAP.WALL[radius][a * 8 + b * 4 + c * 2 + d])
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
    drawCircle([x, y], r, c = "#000") {
        this.svg.insertAdjacentHTML('beforeend', `<circle cx=${x - this.relative[0]} cy=${y - this.relative[1]} r=${r} fill=${c} />`)
    }
    drawLine([x1, y1], [x2, y2], w, c = "#000") {
        this.svg.insertAdjacentHTML('beforeend', `<line x1=${x1 - this.relative[0]} x2=${x2 - this.relative[0]} y1=${y1 - this.relative[1]} y2=${y2 - this.relative[1]} stroke-width=${w} stroke=${c} />`)
    }
}

class Wheel {
    constructor(pos, r) {
        this.pos = pos;
        this.r = r;
        this.vector = new Vector(0, 0)
        this.weight = new Vector(0, 1);
        this.map = undefined;
    }
    update() {
        var point = this.pos;
        var vector = this.vector;
        var size = Vector.getNorm(this.vector);
        var Size = size;
        const map = this.map;
        var index = 0;
        while (true && index < 4) {
            console.log(point, vector)
            const cases = map.vectorCases(point, vector).filter(c => this.map.withinMap(c));
            const droite = new Droite.Point_Vector(Vector.multiply(point, 1 / this.map.l), vector);
            var mur;
            console.log(cases)
            for (let cas of cases) {
                console.groupCollapsed(cas)
                var murs = this.map.readMatrixCase(cas, this.r)
                console.log(murs)
                murs = murs.filter(mur => vector.isOpposite(mur.vector))
                console.log(murs)
                murs.forEach(mur => {
                    // console.log(Vector.add(Vector.multiply(mur.p, this.map.l),[-50,-50]),)
                    new Droite.Point_Vector(Vector.add(Vector.multiply(mur.p, this.map.l),[0,0]), [-mur.vector[1], mur.vector[0]]).draw(this.map.svg, [-50, -50, 50, 50])
                })

                murs = murs.map(mur => [mur, droite.intersection(mur.line)])
                console.log(murs)

                murs.forEach(mur => {
                    mur[1].draw(this.map.svg)
                })
                murs = murs.filter(mur => this.map.withinCase(mur[1], cas))
                console.log(murs)
                murs = murs.map(mur => [...mur, Point.distance(Vector.multiply(point, 1 / this.map.l), mur[1])])
                murs = murs.sort((mur1, mur2) => mur1[2] - mur2[2]);
                console.log(murs)
                console.groupEnd()
                if (murs.length === 1) {
                    mur = murs[0];
                    break;
                }
                index++;
            }
            console.log('mur', mur)
            if (!mur) break;
            console.log(mur)
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
            this.map.svg.insertAdjacentHTML('beforeend', `<line x1=${R[0] - 50} y1=${R[1] - 50} x2=${R[0] - 50 + vector[0]} y2=${R[1] - 50 + vector[1]} style="stroke:#00f;stroke-width:.4" />`)
            // changer la varibale`vector` en fonction du vecteur du`mur` et de la distance où se trouve le point issu de la translation de`point` par le vecteur`vector` partant du point`nouveau_point`
            point = R;
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