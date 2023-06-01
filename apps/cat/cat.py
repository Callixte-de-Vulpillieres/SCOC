
import time
import cv2
import sys
import os 
from math import pi
from zenoh import Zenoh, ZenohSession

# setting path
qrcode_recognition_path = os.path.abspath('../../module/bot-recognition/qrcode_recognition')
commands_path = os.path.abspath('../../module/commands')
sys.path.append(qrcode_recognition_path)
sys.path.append(commands_path)

from qrcode_scanner import *

searching = True
bots_found = []
nb_bots = 2

cam = cv2.VideoCapture(0)
cam.set(3, 640)
cam.set(4, 480)
fps = 20

start_time = time.time()
looking_time = 0.5
nb  = 0
angle = pi/4




zenoh = Zenoh()
session = zenoh.open()
publisher = session.declare_publisher("/lobby")

def move():
    print("moving")

def turn_around(angle ):
    print("turning",angle)

while searching:
    # scan les qrcodes
    success, res = recognition(cam)
    if success:
        for bot in res:
            if bot not in bots_found:
                bots_found.append(bot)
                #send to lobby:
                publisher.write(str(bot))
                if len(bots_found) >= nb_bots:
                    searching = False
                    print("I win!")
                    cam.release()
    time.sleep(1/fps)
    print(bots_found)
    
    #tourner chaque "looking_time" secondes
    if time.time()> start_time + looking_time:
        start_time = time.time()
        turn_around(angle)
        nb += 1
    
    #se bouger le cul apres avoir fait le tour
    if nb*angle >= 2*pi:
        nb = 0
        move()
        
session.close()
zenoh.shutdown()
