
from qrcode_scanner import *
from commands import *
import sys

# setting path
sys.path.append('.../module/bot-recognition/qrcode_recognition')
sys.path.append('.../module/commands')


searching = True
nb_bots_found = 0
nb_bots = 1

map = commands.getmap()  # ??


while searching:
    # cherche un point au hazrd dans les zones dispos
    # se dirige vers cette zone

    # cherche un bot
    res, bot = scan_environment()
    if res == True:
        bot_found(bot)

# play victory sound


def scan_environment():
    # se tourne pour voir s'il y a des robots dans la zone


def scan_ligne():
    # se deplace jusqu'a l'obstacle le plus proche a gauche / a droite


def bot_found():
    # reconnait le robot
    # envoie l id au lobby?
