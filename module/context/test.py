import zenoh
import sys
sys.path.insert(0,'..')
from lidar.lidar import Lidar
import json
import time

class Parent :
    def __init__(self) -> None:
        pass

    def get_angle(self) :
        return 0
    
    def get_x(self) :
        return 100
    
    def get_y(self) : 
        return 100
    

ROUTER_ADDRESS = ['tcp/192.168.13.1:7447']

l = Lidar((200,200),Parent(), 0.01, 1024)

conf = zenoh.Config()
conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(ROUTER_ADDRESS))
session = zenoh.open(conf)

a = session.declare_subscriber("rt/turtle1/lidar", l.handle)
time.sleep(3)

l.draft_map.show()
