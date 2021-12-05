const assert = (e, s) => !e && (() => { throw new Error(`Asertion Error:\n${s.replace(/\;/g, '\n')}`) })();

class Game {
    constructor(useTag = 'canvas', parentElement = document.body) {
        Object.defineProperties(Object.prototype, {
            isElement: {
                get: function () { try { return this instanceof Element } catch { return this && typeof this === 'object' && this.nodeType === 1 && typeof this.style === 'object' && typeof this.ownerDocument === 'object' } }
            }
        });
        const use = ['canvas', 'svg'].includes(useTag) ? useTag : 'canvas';
        const gamedisplay_element = document.createElement(use);
        const gamedisplay_parent = parentElement.isElement ? parentElement : document.body;
        gamedisplay_parent.appendChild(gamedisplay_element);
        gamedisplay_element.classList.add('gamedisplay_element');
    }
    Component = class GameComponent {
        constructor(x = 0, y = 0, width = 0, height = 0) {
            this.x = x;
            this.y = y;
            this.width = width;
            this.height = height;
        }
    }
    Image = class GameImage extends this.Component {
        constructor(x, y, width, height, href) {
            super(x, y, width, height);
        }
    }
}

class Vector {
    constructor(...s) {
        this.data = s;
        this.dimension = s.length;
    }
    multiply(n) { assert(typeof n === 'number', 'we can only multiply a vector with a number'); return new Vector(this.data.map(e => e * n)) }
    divide(n) { assert(typeof n === 'number', 'we can only divide a vector with a number'); return new Vector(this.data.map(e => e / n)) }
    add(v) { assert([Vector, Matrix].every(e => v instanceof e), 'we can only add two vectors together'); return new Vector(this.data.map((e, i) => e + (v.data?.[i] || 0))) }
    subtract(v) { assert([Vector, Matrix].every(e => v instanceof e), 'we can only subtract a vector from another vector'); return new Vector(this.data.map((e, i) => e - (v.data?.[i] || 0))) }
}

class Matrix {
    constructor(s) {
        assert(s && s instanceof Array && s.length > 0 && s[0] instanceof Array && s[0].length > 0, "you must enter an array containing arrays which aren't empty to create a matrix");
        this.data = s;
        this.Isize = s.length;
        this.Jsize = s[0].length;
    }
    static Rotation = class extends Matrix {
        constructor(angle, dimension, typeangle) {
            assert(angle )
            this.data = [];
            for (let i = 0; i < dimension; i++) {
                this.data[i] = [];
                for (let j = 0; j < dimension; j++) {

                }
            }
        }
    }
}