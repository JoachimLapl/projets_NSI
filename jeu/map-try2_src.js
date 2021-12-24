// @ts-check

import { Vector, Point, Droite } from './math_utils.js';
import { Wall, MAP, Wheel } from './map_utils2.js';

const svg = document.querySelector('svg')

// const map = new MAP(new Array(100).fill(0).map(e=>new Array(100).fill(0).map(e=>Number(Math.random()>.5)).join('')).join(','), 20, svg);
const map = new MAP('00000,00000,10000,11011,11111', 20, svg);
const wheel = new Wheel([50, 50], 5);
wheel.vector = [0, 45]
const drt = new Droite.Point_Vector(Vector.add(wheel.pos, [-50, -50]), wheel.vector)
map.addWheel(wheel)
map.draw();
wheel.display();
drt.draw(svg, [-50, -50, 50, 50])
wheel.update()