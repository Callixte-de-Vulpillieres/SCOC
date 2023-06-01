from sympy import geometry
import zenoh
from pycdr import cdr
from pycdr.types import int8, int32, uint16, uint32, float32, sequence, array
import json
import math
from matplotlib import pyplot as plt
import numpy as np
import time
from ..bestHidingPlace import best_hiding_place
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
    def __init__(self, x_size, y_size,step,seuil) -> None:
        self.x_size = x_size
        self.y_size = y_size
        self.step= step
        self.seuil=seuil
    def discrete(self) -> None:
        res=np.array([[0]*self.x_size for i in range(self.y_size)])
        for point in map:
            res[int(point[0]//self.step),int(point[1]//self.step)]+=1
        return (2*res//self.seuil).astype(bool)

class DraftMap :
    points = [] 
    def __init__(self, x_size, y_size) -> None:
        self.x_size = x_size
        self.y_size = y_size
    
    def draw(self, x, y) -> None:
        self.points.append(geometry.Point2D(x,y))
    
    def ___repr__ (self) :
        plt.scatter([point.x for point in self.points], [point.y for point in self.points])
        plt.show()

class Bot :
    angle = 0
    position = (0,0)
    hiding_places=[]
    def __init__(self) -> None:
        pass

    def get_pos(self) -> geometry.Point2D :
        return self.position

    def get_angle(self) -> float :
        return self.angle
    
    def get_hiding_places(self) -> list:
        return self.hiding_places


class Lidar :
    angles = []
    lidar_subscriber_key : str = ""

    def __init__(self, key : str, angles : list, parent_bot : Bot, draft_map : DraftMap, threshold : float = 10) -> None:
        self.lidar_subscriber_key = key
        self.angles = angles
        self.bot = parent_bot
        self.threshold = threshold
        self.draft_map = draft_map
    
    def start(self, z : zenoh.Session) :
        print("[INFO] Creating Subscriber on '{}'...".format(self.lidar_subscriber_key))
        global a
        a = z.declare_subscriber(self.lidar_subscriber_key, self.handle)

    def handle(self, sample) :
        #print("Scanning")
        # print('[DEBUG] Received frame: {}'.format(sample.key_expr))
        scan = LaserScan.deserialize(sample.payload)
        for (angle, distance, intensity) in zip(self.angles, scan.ranges, scan.intensities) :
            #print(angle, self.bot.get_angle(), self.bot.get_pos())
            if intensity > self.threshold :
                self.draft_map.draw(math.cos(angle + self.bot.get_angle())*distance + self.bot.get_pos()[0], math.sin(angle + self.bot.get_angle()) * distance + self.bot.get_pos()[1])
        #self.draft_map.show()
        print("Top")

## Init session
print("[INFO] Opening zenoh session...")
zenoh.init_logger()
conf = zenoh.Config()
## Config connection
conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(['tcp/192.168.13.1:7447']))
z = zenoh.open(conf)


## Create Lidar
print("[INFO] Creating new LIDAR instance...")
lidar = Lidar("rt/turtle1/lidar", np.linspace(-math.pi/2, 3*math.pi/2 - 2*math.pi/360, 360), Bot(), DraftMap(100,100), 1024)
lidar.start(z)



