from PIL import Image
import numpy as np
import importlib
import pygame
import pickle
import os

from vgdl.rlenvironmentnonstatic import createRLInputGameFromStrings
from pygame.locals import K_SPACE

# Game parameters
filename = "examples.gridphysics.chase"
game_name, level_name = "game", "level"

# Import game and level
mod = importlib.import_module(filename)

game = getattr(mod, game_name)
level = getattr(mod, level_name)

def downsample(array, coords, delta=65):
    y, x = coords
    # Make sure we get a point in the middle of the block for color
    # representation (important in the case of rounded edges)
    x += delta/2
    y += delta/2

    pixel00 = array[x-delta, y-delta]
    pixel01 = array[x, y-delta]
    pixel02 = array[x+delta, y-delta]

    pixel10 = array[x-delta, y]
    pixel11 = array[x, y]
    pixel12 = array[x+delta, y]

    pixel20 = array[x-delta, y+delta]
    pixel21 = array[x, y+delta]
    pixel22 = array[x+delta, y+delta]

    return np.array([[pixel00, pixel01, pixel02],
                    [pixel10, pixel11, pixel12],
                    [pixel20, pixel21, pixel22]])


def createPatch(coords, counter, game_name, level_name, effect_name):
    import datetime

    fn_1 = "../vgdl_data/%s/%s/tmp%05d.png" % (game_name, level_name,
                                               counter - 1)
    fn_2 = "../vgdl_data/%s/%s/tmp%05d.png" % (game_name, level_name, counter)

    cropped_img1 = downsample(np.array(Image.open(fn_1)), coords, delta=32)
    cropped_img2 = downsample(np.array(Image.open(fn_2)), coords, delta=32)

    # Check if directory exists, and if not, create it
    if not os.path.exists("../vgdl_data/%s/%s/%s" %
                          (game_name, level_name, effect_name)):
        os.makedirs("../vgdl_data/%s/%s/%s" %
                    (game_name, level_name, effect_name))

    # Use clock to create unique filename
    pickle.dump([np.array([cropped_img1, cropped_img2]), effect_name],
                open('../vgdl_data/%s/%s/%s/%d.pickle' %
                     (game_name, level_name, effect_name,
                      datetime.datetime.now().microsecond), 'wb'))


def generateData(game_str, level_str, game_name, level_name, n_actions=100):
    """ Tests image recording functionalities """
    rleCreateFunc = lambda: createRLInputGameFromStrings(game_str, level_str)
    rle = rleCreateFunc()
    rle.visualize = True
    pygame.init()
    # Initialize keystate for games with orientation
    rle._game.keystate = pygame.key.get_pressed()
    rle.reset()
    for counter in range(n_actions):
        # Choose an action uniformly
        actionset = [(1,0), (0,1), (-1,0), (0,-1)]
        if np.random.rand() < .3:
            keystate = list(rle._game.keystate)
            keystate[K_SPACE] = 1
            rle._game.keystate = tuple(keystate)
        action = actionset[np.random.randint(len(actionset))]
        res = rle.step(action)

        # Update gamescreen and save to file
        rle._game._drawAll()

        # Check if directory exists, and if not, create it
        if not os.path.exists("../vgdl_data/%s/%s" % (filename, level_name)):
            os.makedirs("../vgdl_data/%s/%s" % (filename, level_name))

        fn = "../vgdl_data/%s/%s/tmp%05d.png" % (filename, level_name, counter)
        pygame.image.save(rle._game.screen, fn)

        # Detect whether an interaction has happened
        effects = res['effectList']
        if effects:
            for effect in effects:
                # Do not handle stepBack interactions for the moment
                if counter > 1:
                    # Try to set coordinates to first object's position
                    # If that fails (first object was killed), use the second
                    # one
                    try:
                        coords = previous_objects[effect[1]]['position']
                    except KeyError:
                        coords = previous_objects[effect[2]]['position']

                    # If downsampling fetches an index beyond the gamescreen,
                    # pass
                    try:
                        createPatch(coords, counter, filename, level_name,
                                    effect[0])
                    except IndexError:
                        pass

        keystate = list(rle._game.keystate)
        keystate[K_SPACE] = 0
        rle._game.keystate = tuple(keystate)

        previous_objects = rle._game.getObjects()

for _ in range(10):
    generateData(game, level, filename, level_name, n_actions=100)
