from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty
from kivy.clock import Clock
from math import sin, cos, tan
from random import randint
import numpy as np

'''
TODO:
  + rewrite existing code using numpy instead of python arrays
  + init fields using numpy broadcast vectorization
  - write helper detection functions for neighboring agents
  - add second type of agent
  - play / impl. killing and spreading
  - write abstract agent class
'''


class Field(BoxLayout):
    r = NumericProperty(1)
    g = NumericProperty(1)
    b = NumericProperty(1)


class Zombie(Widget):
    energy = 0
    row = 0
    col = 0

    def __init__(self, row, col, **kwargs):
        super(Zombie, self).__init__(**kwargs)
        self.row = row
        self.col = col


class MtxCanvas(GridLayout):
    time = 0.0
    fields_np = None
    zombies = None

    def init_base(self, dim=(5, 5), zombie_num=1):
        self.rows = dim[0]
        self.cols = dim[1]
        self.spacing = 1

        self.fields_np = np.array([[Field() for _ in range(self.cols)] for _ in range(self.rows)])
        for field in self.fields_np.flat:
            self.add_widget(field)
        # self.fields_np = np.reshape(self.fields_np, newshape=(self.rows, self.cols))

        self.zombies = np.array([Zombie(randint(0, self.rows-1), randint(0, self.cols-1)) for _ in range(zombie_num)])
        for zombie in self.zombies.flat:
            self.fields_np[zombie.row, zombie.col].add_widget(zombie)

    def update(self, dt):
        # some logic for moving agents

        self.fields_np[1, 1].r = sin(self.time)
        self.fields_np[3, 2].g = cos(self.time)
        self.fields_np[2, 4].b = tan(self.time)
        self.time += dt

        # move zombies
        for zombie in self.zombies:        
            self.fields_np[zombie.row, zombie.col].remove_widget(zombie)
            zombie.row += randint(-1, 1)
            zombie.col += randint(-1, 1)
            if zombie.row >= self.rows:
                zombie.row = 0
            elif zombie.row < 0:
                zombie.row += self.rows
            if zombie.col >= self.cols:
                zombie.col = 0
            elif zombie.col < 0:
                zombie.col += self.cols
            try:      
                self.fields_np[zombie.row, zombie.col].add_widget(zombie)
            except IndexError as e:
                print "zombie.row", zombie.row
                print "zombie.col", zombie.col
                raise e

        # TODO: detect multiple zombies on one field


class MtxApp(App):
    def build(self):
        mtx = MtxCanvas()
        mtx.init_base(dim=(15,15), zombie_num=5)
        Clock.schedule_interval(mtx.update, 1.0 / 10.0)
        return mtx


if __name__ == '__main__':
    MtxApp().run()
