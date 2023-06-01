from matplotlib import pyplot as plt
from sympy import geometry

class DraftMap :
    points = [] 
    def __init__(self, x_size, y_size) -> None:
        self.x_size = x_size
        self.y_size = y_size
    
    def draw(self, x, y) -> None:
        self.points.append(geometry.Point2D(x,y))
    
    def show(self) :
        plt.scatter([point.x for point in self.points], [point.y for point in self.points])
        plt.show()
    