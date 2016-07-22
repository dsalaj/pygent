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
  - init fields using numpy broadcast vectorization
  - write helper detection functions for neighboring agents
  - add second type of agent
  - play / impl. killing and spreading
  - write abstract agent class
'''
# class PongPaddle(Widget):
#     score = NumericProperty(0)
# 
#     def bounce_ball(self, ball):
#         if self.collide_widget(ball):
#             vx, vy = ball.velocity
#             offset = (ball.center_y - self.center_y) / (self.height / 2)
#             bounced = Vector(-1 * vx, vy)
#             vel = bounced * 1.1
#             if vel[0] > 20:
#               vel[0] = 22
#             elif vel[0] < -20:
#               vel[0] = -22
#             print vel
#             ball.velocity = vel.x, vel.y + offset
 
 
# class PongBall(Widget):
#     velocity_x = NumericProperty(0)
#     velocity_y = NumericProperty(0)
#     velocity = ReferenceListProperty(velocity_x, velocity_y)
# 
#     def move(self):
#         self.pos = Vector(*self.velocity) + self.pos

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
    # col = 3
    # row = 5
    # ball = ObjectProperty(None)
    # player1 = ObjectProperty(None)
    # player2 = ObjectProperty(None)

    def init_base(self, dim=(5, 5), zombie_num=1):
        self.rows = dim[0]
        self.cols = dim[1]
        self.spacing = 1
        fields = []
        for row in range(0, self.rows):
            row_content = []
            for col in range(0, self.cols):
                field = Field()
                row_content.append(field)
                self.add_widget(field)
            fields.append(row_content)

        temp_zombies = []
        for zombie_idx in range(0, zombie_num):
            zombie = Zombie(randint(0, self.rows-1), randint(0, self.cols-1))
            temp_zombies.append(zombie)
            fields[zombie.row][zombie.col].add_widget(zombie)

        self.fields_np = np.array(fields)
        self.zombies = np.array(temp_zombies)
        
        # self.add_widget(grid)

    # def serve_ball(self, vel=(4, 0)):
    #     self.ball.center = self.center
    #     self.ball.velocity = vel

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
                zombie.row *= -1
            if zombie.col >= self.cols:
                zombie.col = 0
            elif zombie.col < 0:
                zombie.col *= -1                
            try:      
                self.fields_np[zombie.row, zombie.col].add_widget(zombie)
            except IndexError as e:
                print "zombie.row", zombie.row
                print "zombie.col", zombie.col
                raise e

        # TODO: detect multiple zombies on one field

        # self.ball.move()

        # #bounce of paddles
        # self.player1.bounce_ball(self.ball)
        # self.player2.bounce_ball(self.ball)

        # #bounce ball off bottom or top
        # if (self.ball.y < self.y) or (self.ball.top > self.top):
        #     self.ball.velocity_y *= -1

        # #went of to a side to score point?
        # if self.ball.x < self.x:
        #     self.player2.score += 1
        #     self.serve_ball(vel=(4, 0))
        # if self.ball.x > self.width:
        #     self.player1.score += 1
        #     self.serve_ball(vel=(-4, 0))

    # def on_touch_move(self, touch):
    #     if touch.x < self.width / 3:
    #         self.player1.center_y = touch.y
    #     if touch.x > self.width - self.width / 3:
    #         self.player2.center_y = touch.y


class MtxApp(App):
    def build(self):
        mtx = MtxCanvas()
        mtx.init_base(dim=(15,15), zombie_num=5)
        Clock.schedule_interval(mtx.update, 1.0 / 20.0)
        return mtx


if __name__ == '__main__':
    MtxApp().run()
