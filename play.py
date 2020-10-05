# the main entry point for the fMRI experiment
# starts given session (run) for given subject
#
from pymongo import MongoClient
import pprint
import random
from datetime import datetime
import time

# USAGE: python fmri_play.py [subj_id] [run_id]
# * - optional

# see db_api.py

#assert False, ' don''t -- it will mess up the current stuff in the db'

import json
import sys
import csv
from collections import defaultdict
from vgdl import core
from IPython import embed

from pygame.locals import K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT


keyboard_remap = {ord('h'): K_LEFT, ord('k'): K_DOWN, ord(','): K_RIGHT, ord('u'): K_UP}
scanner_remap = {ord('1'): K_LEFT, ord('3'): K_DOWN, ord('4'): K_RIGHT, ord('2'): K_UP, ord('0'): K_SPACE}

# USAGE: python fmri_play.py [subj_id] [run_id]

client = MongoClient('localhost', 27017)
db = client['heroku_7lzprs54']




if __name__ == '__main__':
    game_name = sys.argv[1]
    level_id = int(sys.argv[2])

    game = db.games.find_one({'name': game_name})

    from vgdl.core import VGDLParser

    game_str = game['descs'][0]
    level_str = game['levels'][level_id]

    wins, scores = VGDLParser.playGame(game_str, level_str)

    print 'wins ', wins
    print 'scores ', scores
