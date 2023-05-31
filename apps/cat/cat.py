
import time
import cv2
import sys
import os 

# setting path
qrcode_recognition_path = os.path.abspath('../../module/bot-recognition/qrcode_recognition')
commands_path = os.path.abspath('../../module/commands')
sys.path.append(qrcode_recognition_path)
sys.path.append(commands_path)

from qrcode_scanner import *

searching = True
bots_found = []
nb_bots = 5

cam = cv2.VideoCapture(0)
cam.set(3, 640)
cam.set(4, 480)
fps = 10

start_time = time.time()
searching_time = 5

def move():
    print("moving")

while searching:
    # scan les qrcodes
    success, res = recognition(cam)
    if success:
        for bot in res:
            if bot not in bots_found:
                bots_found.append(bot)
                #send to lobby:
                
                if len(bots_found) >= nb_bots:
                    searching = False
                    print("I win!")
                    cam.release()
    time.sleep(1/fps)
    print(bots_found)
    
    #se bouger le cul
    if time.time()> start_time + searching_time:
        start_time = time.time()
        move()
        

