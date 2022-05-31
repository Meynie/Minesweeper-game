import tkinter as tk


class MyButton(tk.Button):

    def __init__(self, master, x, y, number=0, *args, **kwargs):
        super(MyButton, self).__init__(master, width=3, font='Calibri 15 bold', *args, **kwargs)
        self.x = x
        self.y = y
        self.number = number
        self.is_mine = False
        self.count_mine = 0
        self.is_open = False
        self.count_flag = 0

    def __repr__(self):
        return f'MyButton x={self.x} y={self.y} num={self.number} {self.is_mine}'
