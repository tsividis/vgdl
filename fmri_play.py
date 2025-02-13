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
import utils

from pygame.locals import K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT

experiment_mode = "meg" # "fmri", "meg" or "test"
keyboard_remap = {
    "fmri": {ord('h'): K_LEFT, ord('k'): K_DOWN, ord(','): K_RIGHT, ord('u'): K_UP},
    "meg": None,
    "test": None
}
scanner_remap = {
    "fmri": {ord('1'): K_LEFT, ord('3'): K_DOWN, ord('4'): K_RIGHT, ord('2'): K_UP, ord('0'): K_SPACE},
    "meg": None,
    "test": None
}

client = utils.get_mongo_client()

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

game_names_old = [
    "vgfmri3_sokoban",
    "vgfmri3_chase",
    "vgfmri3_helper",
    "vgfmri3_bait",
    "vgfmri3_lemmings",
    "vgfmri3_plaqueAttack",
    "vgfmri3_zelda"
#    "vgfmri3_aliens",
#    "vgfmri3_sokoban",
#    "vgfmri3_avoidgeorge",
#    "vgfmri3_butterflies",
#    "vgfmri3_jaws",
#    "vgfmri3_zelda"
]

game_names = [
    "vgfmri4_sokoban",
    "vgfmri4_chase",
    "vgfmri4_helper",
    "vgfmri4_bait",
    "vgfmri4_lemmings",
    #"vgfmri4_plaqueAttack",
    "vgfmri4_zelda",
#    "vgfmri4_aliens",
#    "vgfmri4_sokoban",
    "vgfmri4_avoidgeorge",
#    "vgfmri4_butterflies",
#    "vgfmri4_jaws",
#    "vgfmri4_zelda"
]

#real_names = [
#    "Chase",
#    "Helper",
#    "Sokoban",
#    "Aliens",
#    "Avoid George",
#    "Bait",
#    "Butterflies",
#    "Jaws",
#    "Lemmings",
#    "Plaque Attack",
#    "Zombies",
#    "Zelda"
#]

fake_names = [
    "Archeplan",
    "Questtide",
    "Fuseville",
    "Prime Origin",
    "Dreams of Origins",
    "Giants of Solitude",
    "Deception Eagle"
]
#Defeat of Logic
#Dreamside
#Defflight
#Archeblast
#Sacred Kingdom
#Immortal Reaver
#Embers and Hazard
#Archeplan
#Defmania
#Blasterland
#Ebon Sect
#Alterblaze
#Fuseville
#Master Spyre
#Scarletspace
#Aeon and Whispers
#Everkin
#Questtide
#Chronoline
#Prime Origin
#Dreams of Origins
#Giants of Solitude
#Deception Eagle
#Survival and Tomorrow
#Ghosttale
#Lightdroid
#Datastar

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
#    range(947,972),
#    range(9015,9039),
#    range(10675,10700),
#    range(10675,10700), # TODO new!
#    range(10675,10700), # TODO new!
]
#alphabets = [
#    [947, 947, 969, 968, 969, 968],
#    [947, 947, 969, 968, 969, 968],
#    [947, 947, 969, 968, 969, 968],
#]

bg_colors = [
    (0,0,0),
    (80,0,0),
    (0,80,0),
    (0,0,80),
    (80,80,0),
    (80,0,80),
    (0,80,80)
]


assert(len(game_names) == len(fake_names))
assert(len(alphabets) == len(game_names))
assert(len(bg_colors) == len(game_names))

# run has blocks
# each block is the same game, diff levels
# block has instances
# each instance is the same level
# instances have plays of the same level, repeated until timeout

# total TRs = 283 TRs = 566 seconds

nruns = 6 # = 6 per subject: 0 = practice, last one = post-training
prerun_interval = 10 # = 10 sec, how long for scanner to settle
postrun_interval = 10 # = 10 sec, how long for HRF to settle
nblocks = 3 # = 3 per run
ninstances = 3 # = 3 per block
duration = 60 # TODO vs. timeout in game rules! = 60 instance duration (sec) 
interplay_interval = 2 # = 2 sec, how long to hold last screen
interblock_interval = 2 # = 2 sec, how long to show game name


def gen_runs_for_actual_experiment(games):
    #
    # === Experimental structure ===
    #
    # - 'Level'/'Instance': One level of a game constitutes 60s of playtime. The
    #   level is played on repeat: every time the player loses or wins, the
    #   level is reset and the player plays it again. Hence, multiple plays
    #   (episodes) of the same level can occur. The level uniquely identifies
    #   the initial state of the game.
    # - 'Block': A set of 3 instances (levels) of one game played contiguously,
    #   lasting about 3 min.
    # - 'Run': A set of 3 blocks played continuously in the scanner, lasting 566
    #   s (9 min 26 s). There are 6 scanner runs, meaning that the scanner
    #   session takes about 1h without taking breaks into account.
    #
    # Outside the scanner, in addition to the 6 scanner runs, there is one
    # practice run before going in the scanner, which contains only one block
    # and is always playing Sokoban, and one post-scan evaluation run, during
    # which the player plays level 10-11-12 of all 6 games played in the
    # scanner.

    # First run (run#1) - Practice behavioral run:
    # Play level 1-2-3 of Sokoban (which is  not part of the 6 games played in
    # the scanner)
    run_game_ids  = []
    run_game_ids.append([0]) # run 0 is practice, and is always sokoban

    # Data partition 1
    # First two scanner runs (run #2&3):
    # Play level 1-2-3 of each of the 6 games, in 2 runs. The 6 games are played
    # in a random order.
    gs = range(1,7)
    random.shuffle(gs)
    run_game_ids.append(gs[0:3])
    run_game_ids.append(gs[3:6])
    
    # Data partition 2
    # Next two scanner runs (run #4&5):
    # Play level 4-5-6 of each of the 6 games, in 2 runs. The 6 games are played
    # in a random order.
    random.shuffle(gs)
    run_game_ids.append(gs[0:3])
    run_game_ids.append(gs[3:6])

    # Data partition 3
    # Last two scanner runs (run #6&7):
    # Play level 7-8-9 of each of the 6 games, in 2 runs. The 6 games are played
    # in a random order.
    random.shuffle(gs)
    run_game_ids.append(gs[0:3])
    run_game_ids.append(gs[3:6])

    # Last run (run #8) - Post-scan evaluation run:
    # Play level 10-11-12 of each of the 6 games in one run.
    random.shuffle(gs) # last run is post-scan evaluation
    run_game_ids.append(gs)

    next_level_id = [0] * 7

    runs = []
    print run_game_ids
    for r in range(len(run_game_ids)):
        run = {
            'run_id': r,
            'prerun_interval': prerun_interval,
            'postrun_interval': postrun_interval
        }
        blocks = []
        for b in range(len(run_game_ids[r])):
            g = run_game_ids[r][b] 
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
                    'level_id': next_level_id[g],
                    'duration': duration,
                    'interplay_interval': interplay_interval
                }
                next_level_id[g] += 1
                instances.append(instance)

            block['instances'] = instances
            blocks.append(block)

        run['blocks'] = blocks
        runs.append(run)

    return runs


def gen_runs(games):
    runs = []
    for r in range(nruns):
        run = {
            'run_id': r,
            'prerun_interval': prerun_interval,
            'postrun_interval': postrun_interval
        }
        blocks = []
        # Cedric's change: Randomize and vary the games played in each block,
        # instead of always playing the same game as was done in original code.
        block_game_indices = range(len(games))
        random.shuffle(block_game_indices)
        for b in range(nblocks):
            g = block_game_indices[b]
            # g = random.randint(0, len(games) - 1) # TODO actual 
            # g = b + 1 # TODO 
            # g = 6
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
                    'level_id': i,# i, # TODO actual
                    'duration': duration,
                    'interplay_interval': interplay_interval
                }
                instances.append(instance)

            block['instances'] = instances
            blocks.append(block)

        run['blocks'] = blocks
        runs.append(run)

    return runs


def get_games(fakes, alphs, colors):
    games = []
    for i in range(len(game_names)):
        game = db.games.find_one({'name': game_names[i]})
        game['fake_name'] = fakes[i]
        game['alphabet'] = alphs[i]
        game['bg_color'] = colors[i]
        games.append(game)

    return games

def gen_subj(subj_id):
    seed = random.randint(1, 100000000) # beware of bday paradox

    fakes = list(fake_names)
    if (experiment_mode.lower() == "fmri" or experiment_mode.lower() == "meg"):
        random.shuffle(fakes)

    alphs = list(alphabets)
    random.shuffle(alphs)
    for i in range(len(alphs)):
        random.shuffle(alphs[i])
        print alphs[i]

    colors = list(bg_colors[1:])
    random.shuffle(colors)
    colors = [bg_colors[0]] + colors
    print colors

    games = get_games(fakes, alphs, colors)

    if (experiment_mode.lower() == "fmri" or experiment_mode.lower() == "meg"):
        runs = gen_runs_for_actual_experiment(games)
    else:
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

    assert subj_id > 10 # safeguard so we don't overwrite the precious subject 0

    subj = get_subj(subj_id)

    run_length = prerun_interval + postrun_interval + nblocks * interblock_interval + nblocks * ninstances * duration
    print 'run length = ', run_length, 's = ', run_length/60.0, 'min = ', run_length/2.0, 'TRs'

    if (experiment_mode.lower() == "fmri" or experiment_mode.lower() == "meg"):
        if run_id == 0 or run_id == 7: # TODO hardcoded
            remap_keys = keyboard_remap[experiment_mode.lower()]
        else:
            remap_keys = scanner_remap[experiment_mode.lower()]
    else:
        remap_keys = None 

    from vgdl.core import VGDLParser
    #VGDLParser.fMRI_showAlphabets(alphabets)
    do_meg_triggers = experiment_mode.lower() == "meg"
    wins, scores, best_instance_scores = VGDLParser.fMRI_playRun(subj, run_id, db,
        subj['seed'], remap_keys=remap_keys, do_meg_triggers=do_meg_triggers)

    print 'wins ', wins
    print 'scores ', scores
    print 'best_instance_scores ', best_instance_scores 

    """
    w = []
    s = []
    for i in range(len(wins)):
        if wins[i] is not None: # exclude timeouts
            w.append(wins[i])
            s.append(scores[i])

    print 'no timeouts'
    print 'w ', w
    print 's ', s

    i = random.randint(0, len(w)-1)
    print i
   
    if w[i]:
        money = 5 + s[i]
    else:
        money = 0
    print 'money for run', run_id, '= $', money
    """
    i = random.randint(0, len(best_instance_scores)-1)
    money = best_instance_scores[i]
    print 'money for run', run_id, '= $', money, '   from instance ', i

    i = random.randint(1, 7)
    print 'for bonus, pick run ', i
