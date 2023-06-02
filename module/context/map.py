from matplotlib import pyplot as plt
from sympy import geometry
import numpy as np

class DraftMap :
    points = []
    step : float
    def __init__(self, x_size, y_size, step) -> None:
        self.x_size = x_size
        self.y_size = y_size
        self.points = np.zeros((self.x_size, self.y_size))
        self.step = step
        self.shape = (x_size, y_size)
    
    def draw(self, x, y, posx, posy) -> None:
        discrete_x = int(x/self.step)
        discrete_y = int(y/self.step)
        try :
            self.points[discrete_x+posx,discrete_y+posy] = 1
        except :
            pass
    
    def show(self) :
        plt.matshow(self.points)
        plt.show()
    