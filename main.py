from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ListProperty
from kivy.clock import Clock
from math import sin, cos, tan
from random import randint
import numpy as np

'''
TODO:
  + rewrite existing code using numpy instead of python arrays
  + init fields using numpy broadcast vectorization
  + add second type of agent
  + play / impl. killing and spreading
  + write abstract agent class
  - write helper detection functions for neighboring agents
'''


class Field(BoxLayout):
    r = NumericProperty(1)
    g = NumericProperty(1)
    b = NumericProperty(1)


class Agent(Widget):
    energy = 0
    row = 0
    col = 0
    color = ListProperty([0, 0, 0, 1])

    def __init__(self, row, col, **kwargs):
        super(Agent, self).__init__(**kwargs)
        self.row = row
        self.col = col

    def random_move(self, world_rows, world_cols):
        self.row += randint(-1, 1)
        self.col += randint(-1, 1)
        # wrap axes - simulate torus world
        if self.row >= world_rows:
            self.row = 0
        elif self.row < 0:
            self.row += world_rows
        if self.col >= world_cols:
            self.col = 0
        elif self.col < 0:
            self.col += world_cols


class Zombie(Agent):
    color = ListProperty([0, 1, 0, 1])


class Human(Agent):
    color = ListProperty([0.9, 0.8, 0.6, 1])


class MtxCanvas(GridLayout):
    fields = None
    zombies = None
    humans = None

    def agents(self):
        return np.concatenate([self.zombies, self.humans])

    def init_base(self, dim=(5, 5), zombie_num=1, human_num=5):
        self.rows = dim[0]
        self.cols = dim[1]
        self.spacing = 1

        self.fields = np.array([[Field() for _ in range(self.cols)] for _ in range(self.rows)])
        for field in self.fields.flat:
            self.add_widget(field)

        self.zombies = np.array([Zombie(randint(0, self.rows-1), randint(0, self.cols-1)) for _ in range(zombie_num)])
        for zombie in self.zombies.flat:
            self.fields[zombie.row, zombie.col].add_widget(zombie)

        self.humans = np.array([Human(randint(0, self.rows - 1), randint(0, self.cols - 1)) for _ in range(human_num)])
        for human in self.humans.flat:
            self.fields[human.row, human.col].add_widget(human)

    def update(self, dt):
        # some logic for moving agents

        dead_zombies = []
        for z1 in self.zombies:
            for z2 in self.zombies:
                if z1 is not z2:
                    if z1.row == z2.row and z1.col == z2.col:
                        self.fields[z1.row, z1.col].remove_widget(z1)
                        self.fields[z1.row, z1.col].remove_widget(z2)
                        dead_zombies.append(z1)
                        dead_zombies.append(z2)
        dead_zombies = np.array(dead_zombies)
        self.zombies = np.setdiff1d(self.zombies, dead_zombies)

        ex_humans = []
        new_zombies = []
        for z in self.zombies:
            for h in self.humans:
                if z.row == h.row and z.col == h.col:
                    if randint(0, 9) < 5:
                        ex_humans.append(h)
                        new_zombie = Zombie(z.row, z.col)
                        new_zombies.append(new_zombie)
                        self.fields[z.row, z.col].remove_widget(h)
                        self.fields[z.row, z.col].add_widget(new_zombie)  # new zombie is born

        ex_humans = np.array(ex_humans)
        self.humans = np.setdiff1d(self.humans, ex_humans)
        self.zombies = np.concatenate((self.zombies, new_zombies))

        # move agents
        for a in self.agents():
            self.fields[a.row, a.col].remove_widget(a)
            a.random_move(self.rows, self.cols)
            self.fields[a.row, a.col].add_widget(a)


class MtxApp(App):
    def build(self):
        mtx = MtxCanvas()
        mtx.init_base(dim=(30, 30), zombie_num=10, human_num=100)
        Clock.schedule_interval(mtx.update, 1.0 / 40.0)
        return mtx

if __name__ == '__main__':
    MtxApp().run()
