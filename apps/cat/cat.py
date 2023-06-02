
import time
import cv2
from qrcode_scanner import *
from module.commands import controller as cmd
from cmd import Controller
from module.hiding import hiding
from random import randrange
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

def moving(bot: Controller, map,position,stp,horizon,max_retry=10):
    """
    bot: Objet de la classe controller
    map: carte discète des murs
    position : [x,y] position du robot
    stp: nombre de cases dont le robot se déplace avant de refaire un scan
    max_rety: nombre de retry si le chemin n'est pas accessible
    """
    pas=min(stp, horizon)
    x,y=position
    for i in range(max_retry):
        a,b= randrange(max(0,x-pas),min(a,min(x+pas))),randrange(max(0,y-pas),min(a,y+pas))
        if hiding.find_path(map,position,[a,b]) !=None:
            bot.move_path(hiding.find_path(map,position,[a,b])[:pas])
            break
    return None

def turn_around(bot: Controller, angle ):
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
        moving(self, map )

session.close()
zenoh.shutdown()

