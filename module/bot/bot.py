from sympy import geometry
import zenoh
import json
from zenoh import Encoding
import time
from zenoh import Sample
import sys
import os


ROUTER_ADDRESS = ['tcp/192.168.13.1:7447']
ZTURTLE_PATH = "/home/pi/zenoh-demos/turtlebot3/zdrive-python/zdrive.py"
ZLIDAR_PATH = ""

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
        self.cmd_subscriber_key = "bot/{}/cmd_vel".format(uid)
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
        handshake_controller = self.session.declare_subscriber("controller/" + self.uid + "/peer/handshake", self.handshake_controller_handler)
        while not self.controller_connected :
            print("[INFO] Reaching controller")
            controller_waiting_room.put(self.uid)
            time.sleep(1)
            
        controller_waiting_room.delete()
        handshake_controller.undeclare()
        
        ## Run zturtle, cam is at bot/id/cams/0
        print("[INFO] Starting Zturtle")
        os.system("python3 {} -k {} -e {} -a {} -l {}".format(ZTURTLE_PATH, self.cmd_subsciber_key, ROUTER_ADDRESS, self.angular_vel, self.linear_vel))

        ## Run zlidar
        print("[INFO] Starting zlidar")
        lidar_publisher_key = "bot/{}/lidar".format(self.uid)
        os.system("sh {} -e {} -k {}".format(ZLIDAR_PATH, ROUTER_ADDRESS, lidar_publisher_key))

        # Init subscribers
        cmd = zenoh

    def handshake_lobby_handler(self, sample : Sample) :
        self.controller = sample.payload.decode()
        self.lobby_connected = True
        print("[INFO] Connected ! Assigned to controller {}".format(self.controller))

    def handshake_controller_handler(self, sample : Sample) :
        try :
            response = json.load(sample.payload)
            self.angular_vel = response["angular_vel"]
            self.linear_vel = response["linear_vel"]
            self.controller_connected = True
            print("[INFO] Successfully connected to controller {}".format(self.controller))
        except :
            print("[ERROR] {}".format(response))
            sys.exit(1)

    ## Getters
    def get_pos(self) -> geometry.Point2D :
        return self.position

    def get_angle(self) -> float :
        return self.angle
    
    
if __name__ == "__main__" :
    bot = Bot("1")