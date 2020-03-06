from pymongo import MongoClient
import pprint
import random
from datetime import datetime

import json
import sys
import uuid
import csv
from collections import defaultdict
from vgdl import core
from IPython import embed
from vgdl.main_agent import Agent

import pygame

# USAGE: python fmri_empaPlay.py [subj_id] [run_id] [block_id] [instance_id*] [play_id*]
# * - optional
# copied from fmri_empaPlay.py

# from load_games.py TODO dedupe
hyperparameter_sets = [
    {'idx'           : 0,
     'short_horizon' : False,
     'first_order_horizon': True,
     'sprite_first_alpha': 10000,
     'sprite_second_alpha': 100,
     'sprite_negative_mult': .1,
     'multisprite_first_alpha': 10000,
     'multisprite_second_alpha': 100,
     'novelty_first_alpha': 5000,
     'novelty_second_alpha': 50,
     },
    {'idx'           : 1,
     'short_horizon' : False,
     'first_order_horizon': False,
     'sprite_first_alpha': 10000,
     'sprite_second_alpha': 100,
     'sprite_negative_mult': 10.,
     'multisprite_first_alpha': 10000,
     'multisprite_second_alpha': 100,
     'novelty_first_alpha': 5000,
     'novelty_second_alpha': 50,
     },
    {'idx'           : 2,
     'short_horizon' : False,
     'first_order_horizon': False,
     'sprite_first_alpha': 10000,
     'sprite_second_alpha': 100,
     'sprite_negative_mult': .1,
     'multisprite_first_alpha': 10000,
     'multisprite_second_alpha': 100,
     'novelty_first_alpha': 5000,
     'novelty_second_alpha': 50,
     },
    {'idx'           : 3,
     'short_horizon' : True,
     'first_order_horizon': True,
     'sprite_first_alpha': 10000,
     'sprite_second_alpha': 100,
     'sprite_negative_mult': 10, #normally .1
     'multisprite_first_alpha': 10000,
     'multisprite_second_alpha': 100,
     'novelty_first_alpha': 5000,
     'novelty_second_alpha': 50,
     },
    {'idx'           : 4,
     'short_horizon' : True,
     'first_order_horizon': True,
     'sprite_first_alpha': 10000,
     'sprite_second_alpha': 100,
     'sprite_negative_mult': .1, #normally .1
     'multisprite_first_alpha': 10000,
     'multisprite_second_alpha': 100,
     'novelty_first_alpha': 5000,
     'novelty_second_alpha': 10,
     }
]

client = MongoClient('localhost', 27017)
db = client['heroku_7lzprs54']

if __name__ == '__main__':
    subj_id = sys.argv[1]

    query = {'subj_id': subj_id}

    if len(sys.argv) > 2:
        query['run_id'] = int(sys.argv[2])
    if len(sys.argv) > 3:
        query['block_id'] = int(sys.argv[3])
    if len(sys.argv) > 4:
        query['instance_id'] = int(sys.argv[4])
    if len(sys.argv) > 5:
        query['play_id'] = int(sys.argv[5])

    # TODO momchil make sure ordered
    plays = db.plays.find(query)

    # TODO dedupe with fmri_empaPlay

    all_pairs = {}
    all_regressors = {}
    all_movie_names = {}

    for play in plays:
        subj = db.subjects.find_one({'subj_id': subj_id})
        game = subj['games'][play['game_id']]
        game_str = game['descs'][play['desc_id']]
        level_str = game['levels'][play['level_id']]
        assert game_str == play['game_str']
        assert level_str == play['level_str']

        print 'EMPA playing subj %s, run %d, block %d, instance %d, play %d: %s (%s), desc %d, level %d' % (play['subj_id'], play['run_id'], play['block_id'], play['instance_id'], play['play_id'], game['name'], game['fake_name'], play['desc_id'], play['level_id'])

        zstates = play['zstates']
        states = core.VGDLParser.decompress(zstates)
        states = states['states'] # dummy dict

        zkeystates = play['zkeystates']
        keystates = core.VGDLParser.decompress(zkeystates)
        keystates = keystates['keystates'] # dummy dict

        if game['name'] not in all_pairs:
            all_pairs[game['name']] = [] 
            all_regressors[game['name']] = [] 
            all_movie_names[game['name']] = [] 
        all_pairs[game['name']].append((play['game_str'], play['level_str'], states, keystates)) # TODO momchil OOM? 

        # pre-populate regressors object for each play with identifier info
        # extract the regressors later in Agent
        reg = {
            'play_key': play['_id'],
            'subj_id': play['subj_id'],
            'run_id': play['run_id'],
            'block_id': play['block_id'],
            'instance_id': play['instance_id'],
            'play_id': play['play_id'],
            'game_name': play['game_name'],
            'level_id': play['level_id'],
            'type': 'fmri_empaReplay'
        }
        all_regressors[game['name']].append(reg)

        movie_name = game['name'] + '_lev=' + str(play['level_id']) + '_' + str(play['play_id'])
        all_movie_names[game['name']].append(movie_name)

    # for each game, play all instances as part of one curriculum
    # allows within-game transfer but no cross-game transfer
    # TODO note this assumes we simulate the entire subject at once
    #
    for game_name, level_game_pairs in all_pairs.iteritems():
        print 'Playing game ', game_name, ': ', len(level_game_pairs), ' instances'

        regs = all_regressors[game_name] 
        assert len(regs) == len(level_game_pairs)

        movie_names = all_movie_names[game_name]
        assert len(movie_names) == len(level_game_pairs)

        # defaults from load_games.py 
        # python -m vgdl.load_games --game_name tiny_zelda
        agent = Agent('full', game_name, hyperparameter_sets=hyperparameter_sets, hyperparameter_index=3, metacontroller_index=0, IW_k=1, extra_atom_allowed=True, task_ID='0')

        agent.record_fMRIRegressors = True
        curriculumRegressors = agent.playCurriculum(level_game_pairs=level_game_pairs, make_movie=True, heatmap=False, playback=True, movie_names=movie_names)
        assert len(curriculumRegressors) == len(regs)

        for i in range(len(curriculumRegressors)): # for each play
            reg = regs[i]
            reg['regressors'] = curriculumRegressors[i]
            reg['regressors']['theory'] = [] # TODO momchil W T F FIXME ASAP
            db.regressors.insert_one(reg)
