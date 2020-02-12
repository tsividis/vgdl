from pymongo import MongoClient
import pprint
import random
from datetime import datetime
import time

# see db_api.py

assert False, ' don''t -- it will mess up the current stuff in the db'

import json
import sys
import csv
from collections import defaultdict
from vgdl import core
from IPython import embed

# USAGE: python fmri_play.py [subj_id] [run_id]

client = MongoClient('localhost', 27017)
db = client['heroku_7lzprs54']


# > db.games.find({'name': /vgfmri3.*/}, {'name': 1})
#game_names = [
#    "vgfmri3_aliens",
#    "vgfmri3_avoidgeorge",
#    "vgfmri3_bait",
#    "vgfmri3_butterflies",
#    "vgfmri3_chase",
#    "vgfmri3_helper",
#    "vgfmri3_jaws",
#    "vgfmri3_lemmings",
#    "vgfmri3_plaqueAttack",
#    "vgfmri3_sokoban",
#    "vgfmri3_survivezombies",
#    "vgfmri3_zelda"
#]
#
#
#def duplicate_games():
#    assert False, "CAREFUL! don't do it. backup db first" 
#
#    for i in range(len(game_names)):
#        game = db.games.find_one({'name': game_names[i]})
#        del game['_id']
#        game['name'] = game['name'].replace('2', '3')
#        print game['name']
#        db.games.insert(game)
#

game_names = [
    "vgfmri3_chase",
    "vgfmri3_helper",
    "vgfmri3_sokoban",
]

fake_names = [
    "The Sharp",
    "anoshusao",
    "w t f adwgggggg"
]

# unicode ranges for each game -- see https://freefontsdownload.net/free-segoeuisymbol-font-135679.htm
# and https://en.wikipedia.org/wiki/Geometric_Shapes
alphabets = [
    range(9631,9642) + range(9644,9652), 
    range(9660,9662) + range(9664,9666) + range(9670,9691), 
    range(9703,9724),
    range(9552,9559) + range(9568,9580),
    range(9451,9471),
    range(8926,8951),
    range(8853,8875),
    range(947,972),
    range(9015,9039),
    range(10675,10700),
]
#alphabets = [
#    [947, 947, 969, 968, 969, 968],
#    [947, 947, 969, 968, 969, 968],
#    [947, 947, 969, 968, 969, 968],
#]


assert(len(game_names) == len(fake_names))
#assert(len(alphabets) == len(game_names))

# run has blocks
# each block is the same game, diff levels
# block has instances
# each instance is the same level
# instances have plays of the same level, repeated until timeout

nruns = 3 # per subject
prerun_interval = 1 # sec, how long for scanner to settle
postrun_interval = 1 # sec, how long for HRF to settle
nblocks = 1 # per run
ninstances = 1 # per block
duration = 20 # instance duration (sec)
interplay_interval = 2 # sec, how long to hold last screen
interblock_interval = 2 # sec, how long to show game name

def gen_runs(games):
    runs = []
    for r in range(nruns):
        run = {
            'run_id': r,
            'prerun_interval': prerun_interval,
            'postrun_interval': postrun_interval
        }
        blocks = []
        for b in range(nblocks):
            g = random.randint(0, len(games) - 1) # TODO actual 
            g = 2
            block = {
                'block_id': b,
                'game_id': g,
                'game': games[g],
                'interblock_interval': interblock_interval
            }
            instances = []
            for i in range(ninstances):
                instance = {
                    'instance_id': i,
                    'desc_id': 0,
                    'level_id': i, # TODO actual
                    'duration': duration,
                    'interplay_interval': interplay_interval
                }
                instances.append(instance)

            block['instances'] = instances
            blocks.append(block)

        run['blocks'] = blocks
        runs.append(run)

    return runs


def get_games(fakes, alphs):
    games = []
    for i in range(len(game_names)):
        game = db.games.find_one({'name': game_names[i]})
        game['fake_name'] = fakes[i]
        game['alphabet'] = alphs[i]
        games.append(game)

    return games

def gen_subj(subj_id):
    seed = random.randint(1, 100000000) # beware of bday paradox
    fakes = list(fake_names)
    random.shuffle(fakes)
    alphs = list(alphabets)
    random.shuffle(alphs)
    for i in range(len(alphs)):
        random.shuffle(alphs[i])
        print alphs[i]
    games = get_games(fakes, alphs)
    runs = gen_runs(games)
    subj = {
        'subj_id': subj_id,
        'dt': datetime.now(),
        'ts': time.time(),
        'seed': seed,
        'games': games,
        'runs': runs
    }
    return subj


def get_subj(subj_id):
    cnt = db.subjects.count_documents({'subj_id': subj_id})
    assert cnt == 0 or cnt == 1

    if cnt == 0:
        print 'Creating subject...'
        subj = gen_subj(subj_id)
        db.subjects.insert(subj)

    subj = db.subjects.find_one({'subj_id': subj_id})

    return subj

if __name__ == '__main__':
    subj_id = sys.argv[1]
    run_id = int(sys.argv[2])

    subj = get_subj(subj_id)

    run_length = prerun_interval + postrun_interval + nblocks * interblock_interval + nblocks * ninstances * duration
    print 'run length = ', run_length, 's = ', run_length/60.0, 'min = ', run_length/2.0, 'TRs'

    from vgdl.core import VGDLParser
    #VGDLParser.fMRI_showAlphabets(alphabets)
    VGDLParser.fMRI_playRun(subj, run_id, db, subj['seed'])
