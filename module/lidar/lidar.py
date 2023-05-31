from sympy import geometry
import zenoh
from pycdr import cdr
from pycdr.types import int8, int32, uint16, uint32, float32, sequence, array
import json
import math
from matplotlib import pyplot as plt
import numpy as np
import time

@cdr
class Time:
    sec: uint32
    nsec: uint32

@cdr
class Header:
    stamp: Time
    frame_id: str

@cdr
class LaserScan:
    stamp_sec: uint32
    stamp_nsec: uint32
    frame_id: str
    angle_min: float32
    angle_max: float32
    angle_increment: float32
    time_increment: float32
    scan_time: float32
    range_min: float32
    range_max: float32
    ranges: array[float32, 360]
    intensities: array[float32, 360]


class Map :
    def __init__(self, x_size, y_size) -> None:
        self.x_size = x_size
        self.y_size = y_size


class DraftMap :
    points = [] 
    def __init__(self, x_size, y_size) -> None:
        self.x_size = x_size
        self.y_size = y_size
    
    def draw(self, x, y) -> None:
        self.points.append(geometry.Point2D(x,y))
    
    def show(self) :
        plt.scatter([point.x for point in self.points], [point.y for point in self.points])
        plt.show()

class Lidar :
    angles = []

    def __init__(self, angles : list, draft_map : DraftMap, threshold : float = 10) -> None:
        self.angles = angles
        self.threshold = threshold
        self.draft_map = draft_map

    def handle(self, sample) :
        # print("Scanning")
        # print('[DEBUG] Received frame: {}'.format(sample.key_expr))
        scan = LaserScan.deserialize(sample.payload)
        for (angle, distance, intensity) in zip(self.angles, scan.ranges, scan.intensities) :
            #print(angle, self.bot.get_angle(), self.bot.get_pos())
            if intensity > self.threshold :
                self.draft_map.draw(math.cos(angle + self.bot.get_angle())*distance + self.bot.get_pos()[0], math.sin(angle + self.bot.get_angle()) * distance + self.bot.get_pos()[1])
        #self.draft_map.show()
        print("Top")




