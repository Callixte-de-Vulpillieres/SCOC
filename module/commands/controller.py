import zenoh
import json
from zenoh import Session
from zenoh import Encoding
from zenoh import Sample
import time
import sys
sys.path.insert(0, '..')
import lidar
from lidar.lidar import Lidar


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

    lidar : lidar.lidar.Lidar
    info : dict = {}

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
        self.lidar = Lidar((self.x_max, self.y_max))
        ## Lidar handles lidar subscriber, directly generates map
        lidar_subscriber = self.session.declare_subscriber("bot/{}/lidar".format(self.bot), self.lidar.handle)
        while True :
            time.sleep(1)

    ## Handlers
    def handle_instruction(self, sample : Sample) :
        message = sample.payload.decode()
        if self.ins_count == 0 :
            self.info["duration"] = message
            print(self.info["duration"])
            self.ins_count += 1
        if message == "Hiding phase" :
            print("[INFO] Starting")
        


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

    ## Commands
    def move_to(self, x : float, y : float) :
        pass

    ## Treatements


    ## Getters
    def get_x(self) -> float :
        return self.slave_x
    
    def get_y(self) -> float :
        return self.slave_y
    
    def get_angle(self) -> float :
        return self.slave_angle

if __name__ == "__main__" :
    c = Controller("mouse", "mouse")
    
