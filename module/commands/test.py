import sys
from time import sleep
from math import cos,sin
from datetime import datetime
import argparse
import curses
import zenoh
import json
from pycdr import cdr
from pycdr.types import int8, int32, uint32, float64
from astar import *

class Vector3:
    x: float64
    y: float64
    z: float64

class Twist:
    linear: Vector3
    angular: Vector3

class Time:
    sec: int32
    nanosec: uint32

class Log:
    stamp: Time
    level: int8
    name: str
    msg: str
    file: str
    function: str
    line: uint32

class bot:
    position: Vector3
    orientation: float64

    def __init__(self,start_coord,angle):
        bot.position = start_coord
        bot.orientation = angle

    def move(self,direction,length):
        currentAngle = self.orientation()
        pub_twist((direction - currentAngle) * angular_scale, 0.0)
        pub_twist(0.0, length * linear_scale)
        self.position.x=self.position.x + length * cos(direction)
        self.position.y=self.position.y + length * sin(direction)


    def getposition(self):
        return self.position()

    def move_path(self,path):
        for el in path:
            self.move(el[0],el[1])
            sleep(1000)


def pub_twist(linear, angular):
    print("Pub twist: {} - {}".format(linear, angular))
    t = Twist(linear=Vector3(x=linear, y=0.0, z=0.0),
                angular=Vector3(x=0.0, y=0.0, z=angular))
    session.put("", t.serialize())

goal = (x,y)

path = astar(map.discrete(),bot.position,goal)
moves = [path[i+1]-path[i] for i in range(len(path)-1)]

bot.move_path(moves)


