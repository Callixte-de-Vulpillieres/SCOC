import sys
import time
import csv
import random
from datetime import datetime
import argparse
import json
import zenoh
from zenoh import Reliability, Sample, Encoding

# --- Command line argument parsing --- --- --- --- --- ---
parser = argparse.ArgumentParser(
    prog='lobby',
    description='Hide & Seek lobby')
parser.add_argument("bots",
                    type=argparse.FileType("r"),
                    help="CSV file describing position of each bot",
                    )

parser.add_argument("x_max",
                    type=int,
                    )

parser.add_argument("y_max",
                    type=int,
                    )

parser.add_argument("duration",
                    type=int,
                    )

parser.add_argument('--connect', '-e', dest='connect',
                    metavar='ENDPOINT',
                    action='append',
                    type=str,
                    help='Endpoints to connect to.')

args = parser.parse_args()
conf = zenoh.Config()
conf.insert_json5(zenoh.config.MODE_KEY, json.dumps("client"))
conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(args.connect))
key = "lobby"

bots_CSV = csv.DictReader(args.bots)
bots=[]
for bot in bots_CSV :
    if "x" in bot and "y" in bot and "angle" in bot and "id" in bot :
        bots.append({"id" : bot["id"], "x" : int(bot["x"]), "y" : int(bot["y"]), "angle" : float(bot["angle"]), "x_max" : int(args.x_max), "y_max" : int(args.y_max)})
    else :
        parser.error("invalid CSV file")
bots_presents = set()
mouses = {}
cat = None

# initiate logging
zenoh.init_logger()

print("Opening session...")
session = zenoh.open(conf)

def listener_lobby(sample: Sample):
    global bots, mouses, cat
    #if sample.encoding == Encoding.APP_JSON :
    message = json.loads(sample.payload.decode())
    if message["type"] == "bot" :
        bots_presents.add(message["id"])
    if message["type"] == "mouse" :
        mouses.add(message["id"])
    if message["type"] == "cat" :
        cat = message["id"]

sub = session.declare_subscriber(key, listener_lobby, reliability=Reliability.RELIABLE())

print("Waiting for all bots and controllers to connect...")
while len(mouses) + 1 != len(bots) or len(bots_presents) != len(bots) or cat is None :
    time.sleep(1)

sub.undeclare()

print("All participants connected !")
bots_presents = list(bots_presents)
mouses = list(mouses)
random.shuffle(bots)
cat_bot = bots.pop()

# Declare cat
pub = session.declare_publisher("bot/"+cat_bot["id"]+"/handshake")
pub.put(cat)
pub.undeclare()
pub = session.declare_publisher("controller/" + cat + "/handshake")
jsn = json.dumps(cat_bot)
pub.put(jsn.encode())
pub.undeclare()

for i in range(len(bots)) :
    pub = session.declare_publisher("bot/" + bots[i]["id"] + "/handshake")
    pub.put(mouses[i]["id"])
    pub.undeclare()
    pub = session.declare_publisher("controller/" + mouses[i]["id"] + "/handshake")
    jsn = json.dumps(bots[i])
    pub.put(jsn.encode())
    pub.undeclare()


pub = session.declare_publisher("controller")
time.sleep(5)
print("Beginning of hiding phase for " + str(args.duration) + " seconds")
pub.put(args.duration)
pub.put("Hiding phase")
time.sleep(args.duration)

losers = []
def listener_game(sample: Sample) :
    global losers
    losers.add(sample.payload)
    print("Robot " + sample.payload + " has been found")
sub = session.declare_subscriber(key, listener_game, reliability=Reliability.RELIABLE())
print("Seeking phase")
deb = time.time()
pub.put("Seeking phase")


while len(losers) != len(bots) :
    time.sleep(1)
print("Bot " + cat_bot["id"] + "has won in " + time.time() - deb)
print("Bot " + losers[-1] + "has won !")

pub.undeclare()
sub.undeclare()
session.close()