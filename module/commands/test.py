import sys
import numpy
from time import sleep
from math import cos,sin
from datetime import datetime
import argparse
import curses
import zenoh
import json
from pycdr import cdr
from pycdr.types import int8, int32, uint32, float64






goal = (x,y)
cleaned_map=clean_map(map.discrete())
path = astar(map.discrete(),bot.position,goal)
moves = [path[i+1]-path[i] for i in range(len(path)-1)]

bot.move_path(moves)


