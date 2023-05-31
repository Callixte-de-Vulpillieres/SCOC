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

parser.add_argument('--connect', '-e', dest='connect',
                    metavar='ENDPOINT',
                    action='append',
                    type=str,
                    help='Endpoints to connect to.')

args = parser.parse_args()
conf = zenoh.Config.from_file(zenoh.Config())
conf.insert_json5(zenoh.config.MODE_KEY, json.dumps("client"))
conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(args.connect))
key = "lobby"

bots = csv.DictReader(args.bots)
bots_presents = {}

mouses = {}
cat = None

# initiate logging
zenoh.init_logger()

print("Opening session...")
session = zenoh.open(conf)

def listener(sample: Sample):
    global bots, mouses, cat
    if sample.encoding == Encoding.APP_JSON :
        message = json.load(sample.payload)
        if message["type"] == "bot" :
            bots_presents.add(message["id"])
        if message["type"] == "mouse" :
            mouses.add(message["id"])
        if message["type"] == "cat" :
            cat = message["id"]

sub = session.declare_subscriber(key, listener, reliability=Reliability.RELIABLE())

print("Waiting for all bots and controllers to connect...")
while len(mouses) + 1 != len(bots) and len(bots_presents) != len(bots) and cat is not None :
    time.sleep(1)

print("All participants connected !")
bots_presents = list(bots_presents)
mouses = list(mouses)
random.shuffle(bots)
cat_bot = bots.pop()

# Declare cat
pub = session.declare_publisher("bot/"+cat_bot["id"]+"/handshake")
pub.put(cat,Encoding.TEXT_PLAIN)
pub.undeclare()
pub = session.declare_publisher("controller/" + cat + "/handshake")
jsn = json.dump(cat_bot)
pub.put(jsn,Encoding.APP_JSON)
pub.undeclare()

for i in range(bots) :
    pub = session.declare_publisher("bot/" + bots[i]["id"] + "/handshake")
    pub.put(mouses[i]["id"],Encoding.TEXT_PLAIN)
    pub.undeclare()
    pub = session.declare_publisher("controller/" + mouses[i]["id"] + "/handshake")
    jsn = json.dump(bots[i])
    pub.put(jsn,Encoding.APP_JSON)
    pub.undeclare()

pub = session.declare_publisher("controller")
pub.put("Starting game !")




sub.undeclare()
session.close()