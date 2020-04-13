import copy
import os
import platform
import time

import pygame
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import numpy as np


def char_to_pixels(text, path='arialbd.ttf', fontsize=14):
    """
    Based on https://stackoverflow.com/a/27753869/190597 (jsheperd)
    """
    font = ImageFont.truetype(path, fontsize)
    w, h = font.getsize(text)
    h *= 2
    image = Image.new('L', (w, h), 1)
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text, font=font)
    arr = np.asarray(image)
    arr = np.where(arr, 0, 1)
    arr = arr[(arr != 0).any(axis=1)]
    return arr


def display(arr, arr_prot=np.array([])):
    if arr_prot.size == 0:
        result = np.where(arr, '░', ' ')
    else:
        result = np.where(arr_prot, (np.where(arr, '▒', '▓')), (np.where(arr, '░', ' ')))
    str = '\n'.join([''.join(row) for row in result])
    print(str, end="\r", flush=True)


def alive(arr, coord):
    neigbours = 0
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if not (i == 0 and j == 0):
                x, y = coord[0] + i, coord[1] + j
                if x >= arr.shape[0]:
                    x = 0
                if y >= arr.shape[1]:
                    y = 0
                neigbours += 1 if arr[x][y] > 0 else 0
    return ((neigbours == 2 or neigbours == 3) and arr[coord[0]][coord[1]] > 0) or (
            neigbours == 3 and arr[coord[0]][coord[1]] == 0)


def game_of_life_step(arr):
    arr_tmp = copy.deepcopy(arr)
    for x in range(arr.shape[0]):
        for y in range(arr.shape[1]):
            if alive(arr, (x, y)):
                arr_tmp[x][y] += 1
            else:
                arr_tmp[x][y] = 0
    return arr_tmp


def split_list(a_list):
    half = len(a_list) // 2
    return a_list[:half], a_list[half:]


def generate_array():
    timestamp_tmp = time.strftime(time_str)
    time_arr_tmp = np.zeros((max_height, max_width))
    for c in str(timestamp_tmp):
        height_array = np.zeros((max_height - char_dict[c].shape[0], char_dict[c].shape[1]))
        width_array = np.split(np.zeros((max_height, max_width - char_dict[c].shape[1])), 2)
        try:
            char_dict[c] = np.concatenate((height_array, char_dict[c]))
        except:
            pass

        try:
            char_dict[c] = np.concatenate((width_array[0], char_dict[c]), axis=1)
            char_dict[c] = np.concatenate((char_dict[c], width_array[1]), axis=1)
        except:
            pass

        time_arr_tmp = np.concatenate((time_arr_tmp, char_dict[c]), axis=1)
    return np.pad(time_arr_tmp, padding), timestamp_tmp


def font_select():
    fonts = []
    for filename in os.listdir("./fonts"):
        fonts.append("./fonts/" + filename)

    print("")
    i = 1
    for font in fonts:
        print(str(i) + " " + str(font))
        i += 1

    while True:
        conf_select = int(
            input("Choose a previous configuration or create a new one(" + str(1) + "-" + str(i - 1) + "):"))
        if conf_select >= 1 or conf_select < i:
            return fonts[conf_select - 1]
        else:
            print("[ERROR] Selected Number is out of range")


def create_char_dict(char_arr, font_path, fontsize):
    tmp_dict = {}
    for c in char_arr:
        arr = char_to_pixels(
            c,
            path=font_path,
            fontsize=fontsize)
        tmp_dict[c] = arr
    return tmp_dict


def x_zoom(x):
    for _ in range(zoom_factor):
        x = pygame.transform.scale2x(x)
    return x


font = font_select()
char_dict = create_char_dict("0123456789.:Uhr ", font, 25)
time_str = '%H:%M Uhr'
zoom_factor = 3
ticks_per_seconds = 30
transition_frames = 5
padding = 10

max_height = 0
max_width = 0
for num in char_dict.values():
    max_height = int(num.shape[0] if num.shape[0] > max_height else max_height)
    max_width = int(num.shape[1] if num.shape[1] > max_width else max_width)

time_arr, timestamp = generate_array()
arr_step = copy.deepcopy(time_arr)

pygame.init()
display = pygame.display.set_mode([2**zoom_factor * x for x in arr_step.shape[::-1]])
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if time.strftime(time_str) != timestamp:
        time_arr, timestamp = generate_array()
        if arr_step.size != 0:
            arr_step = arr_step + time_arr
            arr_step = np.where(arr_step, 1, 0)
        else:
            arr_step = copy.deepcopy(time_arr)
    last_step = copy.deepcopy(arr_step)
    arr_step = game_of_life_step(arr_step)

    surf_step = pygame.surfarray.make_surface(arr_step.T)
    surf_last_step = pygame.surfarray.make_surface(last_step.T)
    surf_background = pygame.surfarray.make_surface(arr_step.T)
    surf_time = pygame.surfarray.make_surface(time_arr.T)

    surf_time.set_colorkey(pygame.Color(0, 0, 0))
    surf_step.set_colorkey(pygame.Color(0, 0, 0))
    surf_last_step.set_colorkey(pygame.Color(0, 0, 0))

    surf_background.fill(pygame.Color(192, 192, 192))

    surf_time.set_alpha(125)
    for alpha in range(0, 101, int(100/transition_frames)):
        surf_step.set_alpha(alpha*2.55)
        surf_last_step.set_alpha((100 - alpha)*2.55)
        display.blits(((x_zoom(surf_background), (0, 0), None),
                       ((x_zoom(surf_step)), (0, 0), None),
                       ((x_zoom(surf_last_step)), (0, 0), None),
                       ((x_zoom(surf_time)), (0, 0), None)))
        pygame.display.update()

    time.sleep(1/ticks_per_seconds)
