from sympy import geometry
import zenoh
import json
from zenoh import Encoding
import time
from zenoh import Sample
import sys
import os
import numpy

import math

ROUTER_ADDRESS = ['tcp/192.168.13.1:7447']
ZTURTLE_PATH = "/home/pi/zenoh-demos/turtlebot3/zturtle-python"
ZLIDAR_PATH = "/home/pi/zenoh-demos/turtlebot3/zlidar-rust/target/release/zlidar"

class Bot :
    cmd_key : str
    lidar_cmd : str
    uid : str
    lobby_connected : bool
    controller : str
    session : zenoh.Session
    angular_vel : str
    linear_vel : str


    def __init__(self, uid : str) -> None:
        self.cmd_subscriber_key = "bot/{}".format(uid)
        self.lobby_connected = False
        self.controller_connected = False
        self.controller = ""
        self.uid = uid

        # Init conf
        zenoh.init_logger()
        conf = zenoh.Config()

        ## Config connection
        conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(ROUTER_ADDRESS))

        ## Init session
        self.session = zenoh.open(conf)

        ## Join lobby
        lobby = self.session.declare_publisher("lobby")
        handshake_lobby = self.session.declare_subscriber("bot/" + self.uid + "/handshake", self.handshake_lobby_handler)

        ## Generate id card
        id_card = {"id" : self.uid, "type" : "bot"}
        id_card_json = json.dumps(id_card, indent=4)

        ## Send heartbeat until response of lobby
        while not self.lobby_connected :
            print("[INFO] Reaching lobby")
            lobby.put(id_card_json.encode())
            time.sleep(1)
        lobby.delete()

        ## Connect to controller
        controller_waiting_room = self.session.declare_publisher("controller/" + self.controller)
        handshake_controller = self.session.declare_subscriber("controller/" + self.controller + "/peer/handshake", self.handshake_controller_handler)
        while not self.controller_connected :
            print("[INFO] Reaching controller")
            controller_waiting_room.put(self.uid)
            time.sleep(1)
        
        handshake_controller.undeclare()
        controller_waiting_room.delete()
        
        
        ## Run zturtle, cam is at bot/id/cams/0
        print("[INFO] Starting Zturtle")
        print("[INFO] Listening on prefix {}".format(self.cmd_subscriber_key))
        os.system("python3 {}/zturtle.py -p {} -e {}/endpoints.json & ".format(ZTURTLE_PATH, self.cmd_subscriber_key, ZTURTLE_PATH))

        ## Run zlidar
        print("[INFO] Starting zlidar")
        lidar_publisher_key = "bot/{}/lidar".format(self.uid)
        os.system(" /home/pi/zenoh-demos/turtlebot3/zlidar-rust/target/release/zlidar -e tcp/192.168.13.1:7447 -k bot/{}/lidar".format(self.uid))

        # Init subscribers
        cmd = zenoh

    def handshake_lobby_handler(self, sample : Sample) :
        self.controller = sample.payload.decode()
        self.lobby_connected = True
        print("[INFO] Connected ! Assigned to controller {}".format(self.controller))

    def handshake_controller_handler(self, sample : Sample) :
        print("a")
        try :
            response = json.loads(sample.payload.decode())
            self.angular_vel = response["angular_vel"]
            self.linear_vel = response["linear_vel"]
            self.controller_connected = True
            print("[INFO] Successfully connected to controller {}".format(self.controller))
        except :
            print("[ERROR] {}".format(sample.payload.decode()))
            sys.exit(1)

    ## Getters
    def get_pos(self) -> geometry.Point2D :
        return self.position

    def get_angle(self) -> float :
        return self.angle
    
    

    
if __name__ == "__main__" :
    bot = Bot("1")