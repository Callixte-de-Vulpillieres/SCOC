import zenoh
from ..lidar.lidar import Lidar
import json
import time

ROUTER_ADDRESS = ['tcp/192.168.13.1:7447']

l = Lidar((100,100), 1024)

conf = zenoh.Config()
conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(ROUTER_ADDRESS))
session = zenoh.open(conf)

a = session.declare_subscriber("rt/turtle1/lidar", l.handle)
time.sleep(3)

l.draft_map.show()
