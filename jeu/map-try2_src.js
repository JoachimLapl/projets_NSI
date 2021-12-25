// @ts-check

import { Vector, Point, Droite } from './math_utils.js';
import { Wall, MAP, Wheel } from './map_utils2.js';

const svg = document.querySelector('svg')

// const map = new MAP(new Array(100).fill(0).map(e=>new Array(100).fill(0).map(e=>Number(Math.random()>.5)).join('')).join(','), 20, svg);
const map = new MAP('00000,20000,12000,11011,11111', 20, svg);
const wheel = new Wheel([50, 50], 5);
wheel.vector = [0, 45]
const drt = new Droite.Point_Vector(wheel.pos, wheel.vector)
map.addWheel(wheel)
map.draw();
wheel.display();
drt.homothetia(1 / map.l)
map.drawLineLine(drt)
wheel.update()
const drt2 = new Droite.Point_Vector([0, 0], [1, 1])
const drt3 = new Droite.Point_Vector([0, 0], [1, 0])
const drt4 = new Droite.Point_Vector([0, 0], [0, 1])
// map.drawLineLine(drt2)
// map.drawLineLine(drt3)
// map.drawLineLine(drt4)
drt2.translate(10,10)
drt3.translate(10,10)
drt4.translate(10,10)
drt2.draw(map.svg, [-50, -50, 50, 50])
drt3.draw(map.svg, [-50, -50, 50, 50])
drt4.draw(map.svg, [-50, -50, 50, 50])
drt2.homothetia(3)
drt3.homothetia(3)
drt4.homothetia(3)
drt2.draw(map.svg, [-50, -50, 50, 50])
drt3.draw(map.svg, [-50, -50, 50, 50])
drt4.draw(map.svg, [-50, -50, 50, 50])

const drt5 = MAP.WALL[.25][2][0].line
const drt6 = MAP.WALL[.25][7][0].line

drt5.translate(0,0)
drt6.translate(0,1)

console.log(drt5,drt6)