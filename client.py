import socket
import pygame
import math
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import time as t


def scroll(event):
    global color
    color = combo.get()
    style.configure("TCombobox", fieldbackground=color, background="white")


def login():
    global name
    name = row.get()
    if name and color:
        root.destroy()
        root.quit()
    else:
        tk.messagebox.showerror("Ошибка", "Ты не выбрал цвет или не ввёл имя!")


def find(info: str):
    global buffer
    first = None
    for num, sign in enumerate(info):
        if sign == "<":
            first = num
        if sign == ">" and first is not None:
            second = num
            rezult = info[first + 1: second]
            return rezult
    if buffer < 10000000:
        buffer = int(buffer * 1.5)
    return ""


def draw(data: list[str]):
    for num, sing in enumerate(data):
        data = sing.split(" ")
        x = CC[0] + int(data[0])
        y = CC[1] + int(data[1])
        size = int(data[2])
        color = data[3]
        pygame.draw.circle(screen, color, (x, y), size)
        if len(data) > 4:
            draw_text(x, y, size // 2, data[4], "black")


def draw_text(x, y, size, txt, color):
    s = pygame.font.Font(None, size)
    text = s.render(txt, True, color)
    rect = text.get_rect(center=(x, y))
    screen.blit(text, rect)


root = tk.Tk()
root.title("логин")
root.geometry("300x200")

name = " "
color = ""

style = ttk.Style()
style.theme_use("default")
name_label = tk.Label(root, text="Введи свой никнейм:")
name_label.pack()
row = tk.Entry(root, width=30, justify="center")
row.pack()
color_label = tk.Label(root, text="Выбери цвет:")
color_label.pack()
colors = ['Maroon', 'DarkRed', 'FireBrick', 'Red', 'Salmon', 'Tomato', 'Coral', 'OrangeRed', 'Chocolate', 'SandyBrown',
          'DarkOrange', 'Orange', 'DarkGoldenrod', 'Goldenrod', 'Gold', 'Olive', 'Yellow', 'YellowGreen', 'GreenYellow',
          'Chartreuse', 'LawnGreen', 'Green', 'Lime', 'SpringGreen', 'MediumSpringGreen', 'Turquoise',
          'LightSeaGreen', 'MediumTurquoise', 'Teal', 'DarkCyan', 'Aqua', 'Cyan', 'DeepSkyBlue',
          'DodgerBlue', 'RoyalBlue', 'Navy', 'DarkBlue', 'MediumBlue']
buffer = 1024

combo = ttk.Combobox(root, values=colors, textvariable=color)
combo.bind("<<ComboboxSelected>>", scroll)
combo.pack()
name_btn = tk.Button(root, text="Зайти в игру", command=login)
name_btn.pack()
root.mainloop()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Настраиваем сокет
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Отключаем пакетирование
sock.connect(("localhost", 10000))
sock.send(("color:<" + name + "," + color + ">").encode())
pygame.init()

WIDTH = 800
HEIGHT = 600
CC = (WIDTH // 2, HEIGHT // 2)
old = (0, 0)
radius = 50

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Бактерии")

run = True


class Grid:
    def __init__(self, screen, color):
        self.screen = screen
        self.color = color
        self.x = 0
        self.y = 0
        self.start_size = 200
        self.size = self.start_size

    def update(self, list: list[int]):
        x, y, k = list
        self.size = self.start_size // k
        self.x = -self.size + (-x) % self.size
        self.y = -self.size + (-y) % self.size

    def render(self):
        for x in range(WIDTH // self.size + 2):
            pygame.draw.line(self.screen, self.color, (self.x + x * self.size, 0), (self.x + x * self.size, HEIGHT), 1)
        for y in range(HEIGHT // self.size + 2):
            pygame.draw.line(self.screen, self.color, (0, self.y + y * self.size), (WIDTH, self.y + y * self.size), 1)


grid = Grid(screen, "seashell4")

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if pygame.mouse.get_focused():
            pos = pygame.mouse.get_pos()
            vector = pos[0] - CC[0], pos[1] - CC[1]
            lenv = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
            vector = vector[0] / lenv, vector[1] / lenv
            if lenv <= radius:
                vector = 0, 0
            if vector != old:
                old = vector
                msg = f"<{vector[0]},{vector[1]}>"
                try:
                    sock.send(msg.encode())
                except:
                    run = False
                    break
    if not run:
        break
    data = sock.recv(buffer).decode()
    data = find(data).split(",")
    print("Получил", data)
    screen.fill("gray")
    if data != [""]:
        par = list(map(int, data[0].split(" ")))
        radius = par[0]
        grid.update(par[1:])
        grid.render()
        draw(data[1:])
    pygame.draw.circle(screen, color, CC, radius)
    draw_text(CC[0], CC[1], radius // 2, name, "gray")
    pygame.display.update()

screen.fill("black")
draw_text(CC[0], CC[1], 100, "YOU DEAD", "red")
pygame.display.update()
t.sleep(5)

pygame.quit()
