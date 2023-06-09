import zenoh
import json
from zenoh import Session
from zenoh import Encoding
from zenoh import Sample
import time
import sys
sys.path.insert(0, '..')
from module.lidar.lidar import Lidar
import math
from pycdr import cdr
from pycdr.types import int8, int32, uint32, float64
from module.hiding.hiding import decidemove
import numpy
import cv2
import os
from PIL import Image
# setting path for qrcode recognition
qrcode_recognition_path = os.path.abspath('../../module/recognition/qrcode_recognition')
commands_path = os.path.abspath('../../module/commands')
sys.path.append(qrcode_recognition_path)
sys.path.append(commands_path)
from qrcode_scanner import *
from module.commands import *
import module.hiding.hiding

ROUTER_ADDRESS = ['tcp/192.168.13.1:7447']
CONFIG = {
    "angular_vel" : 0,
    "linear_vel" : 0,
}
DIM = (100,100)

class Controller :
    ## Variables corresponding to bot position
    slave_x : float = 0
    slave_y : float = 0
    slave_angle : float = 0

    x_max : float
    y_max : float

    lobby_connected : bool = False
    bound : bool = False
    session : Session
    uid : str
    bot : str

    cmd_pub : zenoh.Publisher

    lidar : Lidar
    info : dict = {}

    elapsed : float
    duration : float
    start : float

    score : list
    to_scan : bool = False

    searching : bool = False
    bots_found : list = []

    cat_publisher_key : str = "lobby"
    cat_publisher : zenoh.Publisher

    def __init__(self, uid : str, role : str) -> None:
        self.uid = uid
        self.type = role

        # Init conf
        zenoh.init_logger()
        conf = zenoh.Config()

        ## Config connection
        conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(ROUTER_ADDRESS))

        ## Init session
        self.session = zenoh.open(conf)

        ## Join lobby
        lobby = self.session.declare_publisher("lobby")
        handshake_lobby = self.session.declare_subscriber("controller/" + self.uid + "/handshake", self.handshake_lobby_handler)

        ## Generate id card
        id_card = {"id" : self.uid, "type" : self.type}
        id_card_json = json.dumps(id_card, indent=4)

        ## Send heartbeat until response of lobby
        while not self.lobby_connected :
            print("[INFO] Reaching lobby")
            lobby.put(id_card_json.encode())
            time.sleep(1)
        lobby.delete()
        handshake_lobby.undeclare()

        ## Wait for bot connection
        print("[INFO] Waiting for bot connection")
        bot_waiting_room = self.session.declare_subscriber("controller/{}".format(self.uid), self.bot_connection_handler)
        while not self.bound :
            pass
        bot_waiting_room.undeclare()

        self.listen()
    
    def listen(self) :
        print("[INFO] Starting subscribers")
        self.ins_count = 0
        lobby_instruction_subscriber = self.session.declare_subscriber("controller", self.handle_instruction)
        self.lidar = Lidar((200,200), self)
        ## Lidar handles lidar subscriber, directly generates map
        lidar_subscriber = self.session.declare_subscriber("bot/{}/lidar".format(self.bot), self.lidar.handle)
        while True :
            time.sleep(1)

    ## Handlers
    def handle_instruction(self, sample : Sample) :
        message = sample.payload.decode()
        if self.ins_count == 0 :
            self.info["duration"] = message
            self.duration = float(message)
            self.start = time.time()
            self.ins_count += 1
        if message == "Hiding phase" :
            print("[INFO] Starting")
            if self.type == "mouse" :
                self.mouse()
        
            

    ## Protocol methods
    def handshake_lobby_handler(self, sample : Sample) :
        data = json.loads(sample.payload.decode())
        self.bot = data["id"]
        self.x_max = data["x_max"]
        self.y_max = data["y_max"]
        self.slave_angle = data["angle"]
        self.lobby_connected = True
        print("[INFO] Connected ! Assigned to bot {}".format(self.bot))

    def bot_connection_handler(self, sample: Sample) :
        if sample.payload.decode() == self.bot :
            print("[INFO] Connection requested from {}".format(self.bot))
            handshake_bot = self.session.declare_publisher("controller/{}/peer/handshake".format(self.uid))
            data = json.dumps(CONFIG, indent=4)
            handshake_bot.put(data.encode())
            print("[INFO] Config sent to {}".format(self.bot))
            handshake_bot.undeclare()
            print("[INFO] Ready to start !")
            self.bound = True

    ## Move commands
    def move(self,direction,length):
        self.angular_vel = 200
        self.linear_vel = 20
        currentAngle = self.get_angle()
        pub_twist((direction - currentAngle) * self.angular_vel, 0.0,self.session, self.cmd_pub.key_expr)
        time.sleep(1)
        pub_twist(0.0, length*self.linear_vel , self.session, self.cmd_pub.key_expr)
        print("[INFO] Publishing twist on {}".format(self.cmd_pub.key_expr))
        self.slave_x=self.slave_x + length * math.cos(direction)
        self.slave_y=self.slave_y + length * math.sin(direction)
        self.slave_angle = (self.slave_angle + 360)%360

    def move_path(self,path):
        for i,el in enumerate(path[:-1]):
            print(path[i+1][0] - path[i][0])
            match path[i+1][0] - path[i][0] :
                case 1 :
                    match path[i+1][1] - path[i][1] :
                        case 1 :
                            self.move(0, 1)
                        case 0 :
                            self.move(0,-1)
                        case -1 :
                            self.move(-1,1)
                case -1 :
                    match path[i+1][1] - path[i][1] :
                        case 1 :
                            self.move(1,1)
                        case 0 :
                            self.move(-1,1)
                        case -1 :
                            self.move(-1,1)

                case 0 :
                    match path[i+1][1] - path[i][1] :
                        case 1 :
                            self.move(1,1)
                        case 0 :
                            self.move(-1,1)
                        case -1 :
                            self.move(-1,1)
            time.sleep(1)

    ## Treatements
    def mouse(self) :
        self.cmd_pub = self.session.declare_publisher("bot/{}/cmd_vel".format(self.bot))
        print("[INFO] Test froward move...")
        self.move(0,1)
        self.elapsed = time.time() - self.start
        self.score = []
        print("[INFO] Moving")
        i = 0
        self.to_scan =True
        time.sleep(1)
        img = Image.fromarray(self.lidar.draft_map.points)
        new_p = img.convert('RGB')
        new_p.save("init.jpeg")
        self.to_scan= False
        while self.elapsed < self.duration :
            self.to_scan = False
            print("[INFO] Beginning scan")
            next_moves = decidemove(self.elapsed, 0.9, 120, (self.get_x(), self.get_y()),20,self.lidar.draft_map.points, 1, 150, self.score, 10,5,1,10)
            print("[INFO] Scan ended")
            print("[INFO] Next moves", next_moves)
            print("’[INFO] Publishing on {}".format(self.cmd_pub.key_expr))
            self.move_path(next_moves)
            self.to_scan = True 
            img = Image.fromarray(self.lidar.draft_map.points)
            new_p = img.convert('RGB')
            new_p.save("{}.jpeg".format(i))
            i += 1


    def cat(self) :
        self.cat_publisher = self.session.declare_publisher(self.cat_publisher_key)
        cam = self.session.declare_subscriber("bot/{}/cam".format(self.cmd_pub),self.camera_handler)
        print("[INFO] Starting cat mode")
        while self.searching :
            # Scan and turn around
            for i in range(36) :
                self.move(10, 0)

            self.cat_move()
        
        print("[INFO] Exiting")

    def camera_handler(self, sample):
        npImage = numpy.frombuffer(bytes(sample.value.payload), dtype=numpy.uint8)
        matImage = cv2.imdecode(npImage, 1)
            # scan les qrcodes
        success, res = recognition(matImage)
        if success:
            for bot in res:
                if bot not in self.bots_found:
                    self.bots_found.append(bot)
                    #send to lobby:
                    self.cat_publisher.put(str(bot))
                    if len(self.bots_found) >= 2:
                        self.searching = False
                        print("[INFO] Found every robot")
            

    def moving(self):
        """
        bot: Objet de la classe controller
        map: carte discète des murs
        position : [x,y] position du robot
        stp: nombre de cases dont le robot se déplace avant de refaire un scan
        max_rety: nombre de retry si le chemin n'est pas accessible
        """
        map = self.lidar.draft_map
        position = (self.get_x(), self.get_y())
        stp = 40
        horizon = 40
        max_retry = 10
        pas=min(stp, horizon)
        x,y=position
        for i in range(max_retry):
            a,b= numpy.randrange(max(0,x-pas),min(a,min(x+pas))),numpy.randrange(max(0,y-pas),min(a,y+pas))
            if hiding.find_path(map,position,[a,b]) !=None:
                self.move_path(hiding.find_path(map,position,[a,b])[:pas])
                break
        return None

    ## Getters
    def get_x(self) -> float :
        return self.slave_x
    
    def get_y(self) -> float :
        return self.slave_y
    
    def get_angle(self) -> float :
        return self.slave_angle

@cdr
class Vector3:
    x: float64
    y: float64
    z: float64
@cdr
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

def clean_map(map,size):
    position_next=[[(i,j) for i in range(-size,size)] for j in range(-size,size)]
    position_next=position_next.flatten()
    n,m=map.shape()
    map2=numpy.array(n,m)
    for i in range(n):
        for j in range(m):
            value=0
            for el in position_next:
                k,l=(i,j)+el
                if 0<=k<=n and 0<=l<=m and map2[i,j]!=1 and map[k,l]:
                    map2[i,j]=1



def pub_twist(angular, linear, session : zenoh.Session, key  :str):
    print("Pub twist: {} - {}".format(linear, angular))
    t = Twist(linear=Vector3(x=linear, y=0.0, z=0.0),
                angular=Vector3(x=0.0, y=0.0, z=angular))
    session.put(key,t.serialize())  


if __name__ == "__main__" :
    c = Controller("mouse", "mouse")
    
