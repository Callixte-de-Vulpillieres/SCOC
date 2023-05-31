import sys
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
        self.position.y=self.position.y + length * cos(direction)


    def getposition(self):
        return self.position()

    def move_path(self,path):
        for el in path:
            self.move(el[0],el[1])



parser = argparse.ArgumentParser(
    prog='ros2-teleop',
    description='zenoh ros2 teleop example')
parser.add_argument('--mode', '-m', dest='mode',
                    choices=['peer', 'client'],
                    type=str,
                    help='The zenoh session mode.')
parser.add_argument('--connect', '-e', dest='connect',
                    metavar='ENDPOINT',
                    action='append',
                    type=str,
                    help='zenoh endpoints to connect to.')
parser.add_argument('--listen', '-l', dest='listen',
                    metavar='ENDPOINT',
                    action='append',
                    type=str,
                    help='zenoh endpoints to listen on.')
parser.add_argument('--config', '-c', dest='config',
                    metavar='FILE',
                    type=str,
                    help='A configuration file.')
parser.add_argument('--cmd_vel', dest='cmd_vel',
                    default='rt/turtle1/cmd_vel',
                    type=str,
                    help='The "cmd_vel" ROS2 topic.')
parser.add_argument('--rosout', dest='rosout',
                    default='rt/rosout',
                    type=str,
                    help='The "rosout" ROS2 topic.')
parser.add_argument('--angular_scale', '-a', dest='angular_scale',
                    default='2.0',
                    type=float,
                    help='The angular scale.')
parser.add_argument('--linear_scale', '-x', dest='linear_scale',
                    default='2.0',
                    type=float,
                    help='The linear scale.')

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

goal = (x,y)

path = astar(map.discrete(),bot.position,goal)
moves = [path[i+1]-path[i] for i in range(len(path)-1)]

bot.move_path(moves)


