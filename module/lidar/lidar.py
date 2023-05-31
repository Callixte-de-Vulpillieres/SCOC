from sympy import geometry
import zenoh
from pycdr import cdr
from pycdr.types import int8, int32, uint16, uint32, float32, sequence, array
import json
import math
from matplotlib import pyplot as plt
import numpy as np
import time
import sys

# sys.path.insert(0,'..')
# from commands.controller import Controller

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

    def __init__(self, dim : tuple, threshold : float = 10) -> None:
        self.angles = np.linspace(-math.pi/2, 3*math.pi/2 - 2*math.pi/360, 360)
        self.threshold = threshold
        self.draft_map = DraftMap()

    def handle(self, sample) :
        # print("Scanning")
        # print('[DEBUG] Received frame: {}'.format(sample.key_expr))
        scan = LaserScan.deserialize(sample.payload)
        for (angle, distance, intensity) in zip(self.angles, scan.ranges, scan.intensities) :
            if intensity > self.threshold :
                self.draft_map.draw(math.cos(angle + self.parent.get_angle())*distance + self.parent.get_x() , math.sin(angle + self.parent.get_angle()) * distance + self.parent.get_y())
        #self.draft_map.show()




