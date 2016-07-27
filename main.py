from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty
from kivy.clock import Clock
from random import randint, random
import numpy as np


class TorusWorld(np.ndarray):
    def __new__(cls, input_array, info=None):
        return np.asarray(input_array).view(cls)

    def __array_finalize__(self, obj):
        if obj is None: return

    @property
    def rows(self):
        return self.shape[0]

    @property
    def cols(self):
        return self.shape[1]

    def field(self, row, col):
        return self[row % self.rows, col % self.cols]


class Field(BoxLayout):
    color = ListProperty([1, 1, 1, 1])


class Agent(Widget):
    energy = 0
    row = 0
    col = 0
    color = ListProperty([0, 0, 0, 1])

    def __init__(self, row, col, **kwargs):
        super(Agent, self).__init__(**kwargs)
        self.row = row
        self.col = col

    def random_move(self, world):
        # move to random unoccupied neighboring field
        new_row = self.row + randint(-1, 1)
        new_col = self.col + randint(-1, 1)
        if len(world.field(new_row, new_col).children) > 0:
            self.random_move(world)
        else:  # FIXME: refactor - world should normalise the values, not the agent
            self.row = new_row % world.rows
            self.col = new_col % world.cols

    def neighboring_agents(self, world):
        neighbors = world.field(self.row - 1, self.col - 1).children +\
                    world.field(self.row - 1, self.col).children +\
                    world.field(self.row - 1, self.col + 1).children +\
                    world.field(self.row, self.col - 1).children +\
                    world.field(self.row, self.col + 1).children +\
                    world.field(self.row + 1, self.col - 1).children +\
                    world.field(self.row + 1, self.col).children +\
                    world.field(self.row + 1, self.col + 1).children
        return neighbors


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

        self.fields = TorusWorld([[Field() for _ in range(self.cols)] for _ in range(self.rows)])
        for field in self.fields.flat:
            self.add_widget(field)

        self.zombies = np.array([Zombie(randint(0, self.rows-1), randint(0, self.cols-1)) for _ in range(zombie_num)])
        for zombie in self.zombies.flat:
            self.fields[zombie.row, zombie.col].add_widget(zombie)

        self.humans = np.array([Human(randint(0, self.rows - 1), randint(0, self.cols - 1)) for _ in range(human_num)])
        for human in self.humans.flat:
            self.fields[human.row, human.col].add_widget(human)

    def update(self, dt):
        # move agents
        for a in self.agents():
            self.fields[a.row, a.col].remove_widget(a)
            a.random_move(self.fields)
            self.fields[a.row, a.col].add_widget(a)

        # conflict
        dead_humans = []
        dead_zombies = []
        for zombie in self.zombies:
            for neighbor in zombie.neighboring_agents(self.fields):
                if type(neighbor) is Human:
                    if random() > 0.77:  # conversion threshold
                        dead_humans.append(neighbor)
                    else:
                        dead_zombies.append(zombie)
                        self.fields[zombie.row, zombie.col].remove_widget(zombie)
                        break  # after the zombie has been killed, he can not infect further victims
        self.zombies = np.setdiff1d(self.zombies, np.array(dead_zombies))
        zombabies = []
        for human in dead_humans:
            self.fields[human.row, human.col].remove_widget(human)
            zombaby = Zombie(human.row, human.col)
            zombabies.append(zombaby)
            self.fields[human.row, human.col].add_widget(zombaby)
        dead_humans = np.array(dead_humans)
        self.humans = np.setdiff1d(self.humans, dead_humans)
        self.zombies = np.concatenate((self.zombies, zombabies))

        if len(self.zombies) == 0 or len(self.humans) == 0:
            if len(self.zombies) == 0:
                print "HUMANS WON!"
            else:
                print "ZOMBIES WON!"
            exit(0)


class MtxApp(App):
    def build(self):
        mtx = MtxCanvas()
        mtx.init_base(dim=(30, 30), zombie_num=20, human_num=15)
        Clock.schedule_interval(mtx.update, 1.0 / 60.0)
        return mtx

if __name__ == '__main__':
    MtxApp().run()
