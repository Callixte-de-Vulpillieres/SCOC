from matplotlib import pyplot as plt
from sympy import geometry
import numpy as np

class DraftMap :
    points = []
    step : float
    def __init__(self, x_size, y_size) -> None:
        self.x_size = x_size
        self.y_size = y_size
        self.points = np.ndarray((self.x_size, self.y_size))
    
    def draw(self, x, y) -> None:
        discrete_x = int(x*self.step)
        discrete_y = int(y*self.step)
        self.points[discrete_x,discrete_y] = 1
    
    def show(self) :
        plt.plot(self.points)
        plt.show()
    