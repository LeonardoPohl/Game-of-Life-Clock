import copy
import datetime
import string
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


num_dict = {}
font_dict = {
    'LiberationSerif-Bold.ttf': '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf',
    'Ubuntu-R.ttf': '/usr/share/fonts/truetype/ubuntu/Ubuntu-R.ttf',
    'NotoSerifCJK-Regular.ttc': '/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc'
}
time_str = '%H.%M Uhr'
for c in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.', ':', 'U', 'h', 'r', ' ', 'H', 'i', 'M', 'a', 'e']:
    arr = char_to_pixels(
        c,
        path=font_dict['Ubuntu-R.ttf'],
        fontsize=100)
    num_dict[c] = arr

max_height = 0
for num in num_dict.values():
    max_height = int(num.shape[0] if num.shape[0] > max_height else max_height)

timestamp = time.strftime(time_str)
time_arr = np.array([0 for i in range(max_height)])
time_arr = time_arr.reshape((max_height, 1))

for c in str(timestamp):
    tmp_arr = np.array(
        [[0 for i in range(num_dict[c].shape[1])] for j in range(max_height - num_dict[c].shape[0])])
    try:
        num_dict[c] = np.concatenate((tmp_arr, num_dict[c]))
    except:
        pass
    time_arr = np.concatenate((time_arr, num_dict[c]), axis=1)
    time_arr = np.concatenate((time_arr, np.array([[0] for x in range(max_height)])), axis=1)
time_arr = np.pad(time_arr, 5)
arr_step = copy.deepcopy(time_arr)

pygame.init()
display = pygame.display.set_mode(arr_step.shape)
surf = pygame.surfarray.make_surface(arr_step)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    print(
        '______________________________________________________________________________________________________________')
    time.sleep(1)

    if time.strftime(time_str) != timestamp:
        timestamp = time.strftime(time_str)
        time_arr = np.array([0 for i in range(max_height)])
        time_arr = time_arr.reshape((max_height, 1))

        for c in str(timestamp):
            tmp_arr = np.array(
                [[0 for i in range(num_dict[c].shape[1])] for j in range(max_height - num_dict[c].shape[0])])
            try:
                num_dict[c] = np.concatenate((tmp_arr, num_dict[c]))
            except:
                pass
            time_arr = np.concatenate((time_arr, num_dict[c]), axis=1)
            time_arr = np.concatenate((time_arr, np.array([[0] for x in range(max_height)])), axis=1)
        time_arr = np.pad(time_arr, 5)
        if arr_step.size != 0:
            arr_step = arr_step + time_arr
            arr_step = np.where(arr_step, 1, 0)
        else:
            arr_step = copy.deepcopy(time_arr)

        display(arr_step)

    arr_step = game_of_life_step(arr_step)
    for row in arr_step:
        pass  # print(row)
    #display(arr_step, time_arr)

    surf = pygame.surfarray.make_surface(arr_step)
    display.blit(surf, (0, 0))
    pygame.display.update()
#timestamp = None
#arr_step = np.array([])
#time_arr = np.array([])

while True:
    print(
        '______________________________________________________________________________________________________________')
    time.sleep(1)

    if time.strftime(time_str) != timestamp:
        timestamp = time.strftime(time_str)
        time_arr = np.array([0 for i in range(max_height)])
        time_arr = time_arr.reshape((max_height, 1))

        for c in str(timestamp):
            tmp_arr = np.array(
                [[0 for i in range(num_dict[c].shape[1])] for j in range(max_height - num_dict[c].shape[0])])
            try:
                num_dict[c] = np.concatenate((tmp_arr, num_dict[c]))
            except:
                pass
            time_arr = np.concatenate((time_arr, num_dict[c]), axis=1)
            time_arr = np.concatenate((time_arr, np.array([[0] for x in range(max_height)])), axis=1)
        time_arr = np.pad(time_arr, 5)
        if arr_step.size != 0:
            arr_step = arr_step + time_arr
            arr_step = np.where(arr_step, 1, 0)
        else:
            arr_step = copy.deepcopy(time_arr)

        display(arr_step)

    arr_step = game_of_life_step(arr_step)
    for row in arr_step:
        pass#print(row)
    display(arr_step, time_arr)

'''

timestamp = "Hi Marie"
time_arr = np.array([0 for i in range(max_height)])
time_arr = time_arr.reshape((max_height, 1))

for c in str(timestamp):
    # if c != '.':
    #    time_arr = np.concatenate((time_arr, num_dict[c]), axis=1)
    # else:
    tmp_arr = np.array(
        [[0 for i in range(num_dict[c].shape[1])] for j in range(max_height - num_dict[c].shape[0])])
    try:
        num_dict[c] = np.concatenate((tmp_arr, num_dict[c]))
    except:
        pass

    time_arr = np.concatenate((time_arr, num_dict[c]), axis=1)
    time_arr = np.concatenate((time_arr, np.array([[0] for x in range(max_height)])), axis=1)
time_arr = np.pad(time_arr, 5)
arr_step = copy.deepcopy(time_arr)

while True:
    print(
        '_______________________________________________________'
        '_______________________________________________________')
    time.sleep(0.5)

    arr_step = game_of_life_step(arr_step)

    display(arr_step, time_arr)
'''
