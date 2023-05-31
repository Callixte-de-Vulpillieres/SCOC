import sys
from math import cos,sin
from datetime import datetime
import argparse
import curses
import zenoh
import json
from pycdr import cdr
from pycdr.types import int8, int32, uint32, float64
from astar.py import *

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




args = parser.parse_args()
conf = zenoh.config_from_file(args.config) if args.config is not None else zenoh.Config()
if args.mode is not None:
    conf.insert_json5(zenoh.config.MODE_KEY, json.dumps(args.mode))
if args.connect is not None:
    conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(args.connect))
if args.listen is not None:
    conf.insert_json5(zenoh.config.LISTEN_KEY, json.dumps(args.listen))
cmd_vel = args.cmd_vel
rosout = args.rosout
angular_scale = args.angular_scale
linear_scale = args.linear_scale

zenoh.init_logger()

print("Openning session...")
session = zenoh.open(conf)

print("Subscriber on '{}'...".format(rosout))

def rosout_callback(sample):
    log = Log.deserialize(sample.payload)
    print('[{}.{}] [{}]: {}'.format(log.stamp.sec,
                                    log.stamp.nanosec, log.name, log.msg))

sub = session.declare_subscriber(rosout, rosout_callback)

def pub_twist(linear, angular):
    print("Pub twist: {} - {}".format(linear, angular))
    t = Twist(linear=Vector3(x=linear, y=0.0, z=0.0),
                angular=Vector3(x=0.0, y=0.0, z=angular))
    session.put(cmd_vel, t.serialize())


def move(self,direction,length):
    currentAngle=self.orientation()
    pub_twist((direction - currrentAngle) * angular_scale, 0.0)
    pub_twist(0.0, length * linear_scale)
    self.position.x=self.position.x + length * cos(direction)
    self.position.y=self.position.y + length * cos(direction)


def getposition(self):
    return self.position()