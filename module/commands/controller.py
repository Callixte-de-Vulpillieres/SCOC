import zenoh
import json
from zenoh import Session
from zenoh import Encoding
from zenoh import Sample
import time
import sys
sys.path.insert(0, '..')
from module.lidar.lidar import Lidar


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

    lobby_connected : bool = False
    bound : bool = False
    session : Session
    uid : str
    bot : str

    lidar : Lidar

    def __init__(self, uid : str) -> None:
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
        handshake_lobby = self.session.declare_subscriber("controller/" + self.uid + "/handshake", self.handshake_lobby_handler)

        ## Generate id card
        id_card = {"id" : self.uid, "type" : "controller"}
        id_card_json = json.dumps(id_card, indent=4)

        ## Send heartbeat until response of lobby
        while not self.lobby_connected :
            lobby.put(id_card_json, Encoding.APP_JSON)
            time.sleep(1)
        lobby.delete()

        ## Wait for bot connection
        print("[INFO] Waiting for bot connection")
        bot_waiting_room = self.session.declare_subscriber("controller/{}".format(self.uid), self.bot_connection_handler)

    
    def listen(self) :
        print("[INFO] Starting subscribers")
        lobby_instruction_subscriber = self.session.declare_subscriber("controller", self.handle_instruction)
        self.lidar = Lidar(DIM)
        ## Lidar handles lidar subscriber, directly generates map
        lidar_subscriber = self.session.declare_subscriber("bot/{}/lidar".format(self.bot), self.lidar.handle)
    
    ## Handlers
    def handle_instruction(self, sample : Sample) :
        pass


    ## Protocol methods
    def handshake_lobby_handler(self, sample : Sample) :
        if sample.encoding == Encoding.TEXT_PLAIN :
            self.bot = sample.payload.decode()
            self.lobby_connected = True
            print("[INFO] Connected ! Assigned to bot {}".format(self.controller))

    def bot_connection_handler(self, sample: Sample) :
        if sample.payload.decode() == self.bot :
            print("[INFO] Connection requested from {}".format(self.bot))
            handshake_bot = self.session.declare_publisher("controller/{}/handshake".format(self.uid))
            payload = json.dumps(CONFIG, indent=4)
            handshake_bot.put(payload, Encoding.APP_JSON)
            print("[INFO] Config sent to {}".format(self.bot))
            handshake_bot.delete()
            print("[INFO] Ready to start !")

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