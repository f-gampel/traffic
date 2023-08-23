import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches
from math import inf
from matplotlib.animation import FuncAnimation
from functools import partial

dt = 1/30
n_lanes = 2
road_length = 1000

def overlap(a, b):
    return (min(a[1], b[1]) - max(a[0], b[0])) > 0

def x_dist(v1, v2):
    return min(abs(v1.front() - v2.x),
               abs(v2.front() - v1.x))

def same_lane(v1, v2):
    return v1.lane == v2.lane

def vehicle_close(v1, v2):
    d = v2.x - v1.front()
    return same_lane(v1, v2) and d <= v1.v_x*1.8 and d>0

def lane_free(vehicles, l, interval):
    if l >= n_lanes or l<0:
        return False
        
    for v in vehicles.values():
        if v.lane == l:
            if overlap(interval, [v.x, v.front()]):
                return False
    return True

def next_car(v0, vehicles):
    vf = v0.front()
    res = v0
    d_min = inf
    for v in vehicles.values():
        d = v.x - vf 
        if same_lane(v0, v) and d>0:
            if d<d_min:
                res, d_min = v, d
    return res, d_min
        
            

class Car:
    def __init__(self, x, y, v_x, lane=0, length=4.5, v_max = 30):
        self.x = x
        self.y = y
        self.length = length
        self.width = 1.5
        
        self.v_x = v_x
        self.acceleration = 0
        self.v_max = v_max
        self.lane = lane
        
        self.drawing = matplotlib.patches.Rectangle((self.x, self.y), self.length, self.width)
        self.infotxt = ax.text(self.x, self.y, f'{self.v_x:.3f} \n {self.v_max} \n {self.acceleration}')

    def front(self):
        return self.x+self.length
    
    def check_road(self, vehicles):
        if lane_free(vehicles, self.lane-1, [self.x-self.v_x*1.8, self.front()+self.v_x*1.8]):
            self.change_lane(-1)
        
        n_car, dist = next_car(self, vehicles)
        
        if dist < self.v_x*1.8:
            
            if lane_free(vehicles, self.lane+1, [self.x-self.v_x*1.8, self.front()+self.v_x*1.8]) and (self.v_max-self.v_x)>3:
                self.change_lane(1)
            else:
                self.acceleration = -8

        if dist >= self.v_x*1.8 and dist < self.v_x*2.0:
            if lane_free(vehicles, self.lane+1, [self.x-self.v_x*1.8, self.front()+self.v_x*1.8]) and (self.v_max-self.v_x)>3:
                self.change_lane(1)
            else:
                self.acceleration = 0

        if dist >= self.v_x*2.0:
            self.acceleration = 3
    
    def update(self, vehicles):
        self.check_road(vehicles)
        self.v_x += self.acceleration * dt 
        
        if self.v_x >= self.v_max:
            self.v_x = self.v_max

        if self.v_x <= 0:
            self.v_x = 0
        
        self.x += self.v_x * dt
        self.drawing.set_xy((self.x, self.y))
        self.infotxt.set_x(self.x)
        self.infotxt.set_y(self.y)
        self.infotxt.set_text(f'{self.v_x:.3f} \n {self.v_max} \n {self.acceleration}')

    def change_lane(self, direction):
        self.lane += direction
        self.y += direction * 3.5


vehicles = {}
fig, ax = plt.subplots(figsize=(20,6), tight_layout=True)
vehicles[0] = Car(x=60, y=0.5, v_x=0, v_max=20)
vehicles[1] = Car(x=0,  y=0.5, v_x=0, v_max=30)
vehicles[2] = Car(x=30, y=0.5, v_x=0, v_max=25)

def init():
    ax.set_xlim(0, road_length)
    ax.set_ylim(0, 10)
    for v in vehicles.values():
        ax.add_patch(v.drawing)
    return [v.drawing for v in vehicles.values()]+[v.infotxt for v in vehicles.values()]

def update(frame):
    to_delete = []
    for id, v in vehicles.items():
        
        vehicles_to_check = vehicles.copy()
        vehicles_to_check.pop(id)
        v.update(vehicles_to_check)
        
        if v.x > 1000:
            to_delete.append(id)
            
    for id in to_delete:
        vehicles.pop(id)
            
    return [v.drawing for v in vehicles.values()]+[v.infotxt for v in vehicles.values()]


ani = FuncAnimation(fig, update, frames=np.linspace(0, 2*np.pi, 128),
                    interval=33.3, init_func=init, blit=True)

plt.show()