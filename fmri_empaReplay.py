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
    run_id = int(sys.argv[2])

    query = {'subj_id': subj_id, 'run_id': run_id}

    if len(sys.argv) > 3:
        query['block_id'] = int(sys.argv[3])
    if len(sys.argv) > 4:
        query['instance_id'] = int(sys.argv[4])
    if len(sys.argv) > 5:
        query['play_id'] = int(sys.argv[5])

    plays = db.plays.find(query)

    all_pairs = {}

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

        new_states = states[0:5] # TODO momchil undo
        for i,state in enumerate(states[5:]):
            if len(state['effectList']) > 0 or state['key']:
                new_states.append(state)

        del new_states[6:-6]

        if game['name'] not in all_pairs:
            all_pairs[game['name']] = [] 
        all_pairs[game['name']].append([play['game_str'], play['level_str'], new_states]) # TODO OOM? momchil rm new_states

        #core.VGDLParser.fMRI_replayGame(play['game_str'], play['level_str'], new_states) working
        core.VGDLParser.playGame(play['game_str'], play['level_str'], new_states, \
            persist_movie=True, make_images=True, make_movie=True, movie_dir="videos", padding=10) 

        '''
        game_str = play['game_str']
        map_str = play['level_str']
        g = core.VGDLParser().parseGame(game_str)
        g.uiud = uuid.uuid4()
        g.buildLevel(map_str)
        g.playback_states = new_states
        g.startPlaybackGame(headless=False, persist_movie=True, make_images=True, make_movie=True, movie_dir='videos', padding=10, gameName='', parameter_string='')
        sys.exit(0)
        ''' # don't work

        '''
        black = (0,0,0)
        white = (255,255,255)

        pygame.init()
        clock = pygame.time.Clock()

        fMRI_screensize = (1200,900)
        fMRI_screen = pygame.display.set_mode(fMRI_screensize)

        fMRI_bg = pygame.Surface(fMRI_screensize)
        fMRI_bg.fill(black)
        fMRI_screen.blit(fMRI_bg, (0, 0))
        fMRI_screensize = (1200,900)

        game_str = play['game_str']
        map_str = play['level_str']
        g = core.VGDLParser().parseGame(game_str)
        g.uiud = uuid.uuid4()
        g.buildLevel(map_str)
        g.playback_states = new_states
        g.startPlaybackGame(headless=False, persist_movie=True, make_images=True, make_movie=True, movie_dir='videos', padding=10, gameName='', parameter_string='', deoffset=True)
        '''
        #sys.exit(0)


    # for each game, play all instances as part of one curriculum
    # allows within-game transfer but no cross-game transfer
    #
    for game_name, level_game_pairs in all_pairs.iteritems():
        print 'Playing game ', game_name, ': ', len(level_game_pairs), ' instances'

        # defaults from load_games.py 
        # python -m vgdl.load_games --game_name tiny_zelda
        agent = Agent('full', game_name, hyperparameter_sets=hyperparameter_sets, hyperparameter_index=3, metacontroller_index=0, IW_k=1, extra_atom_allowed=True, task_ID='0')

        agent.record_fMRIRegressors = True
        agent.playCurriculum(level_game_pairs=level_game_pairs, make_movie=True, heatmap=False, playback=True)
