# post-processing of data to extract quantities for convenient analysis

from pymongo import MongoClient
import pprint
import random
from datetime import datetime
import time

import json
import sys
import uuid
import csv
import socket
import numpy as np
from collections import defaultdict
from vgdl import core
from vgdl.core import VGDLParser, fMRI_screensize
from vgdl.core import keyPresses as keyNames
from IPython import embed
from vgdl.main_agent import Agent
import cPickle, cloudpickle
import utils
from vgdl.theory_template import TimeoutRule, SpriteCounterRule, MultiSpriteCounterRule, NoveltyRule, generateTheoryFromGame
from fmri_agentReplay import chelsea_fix_states_avatar_only
from sprite_valence import sprite_valences

import pygame

# USAGE: python fmri_playsPostproc.py.py [subj_id] [run_id*] [block_id*] [instance_id*] [play_id*]
#        python fmri_playsPostproc.py.py [subj_id] [game_name]
#        python fmri_playsPostproc.py.py [subj_id] [run_id] [game_name]
# * - optional
# copied from fmri_makeMovie.py

client = utils.get_mongo_client()

db = client['heroku_7lzprs54']



def playsPostprocApproachAvoid(subj_id):
    query = {'subj_id': subj_id}

    if int(subj_id) <= 11:
        games = ['vgfmri3_chase', 'vgfmri3_helper', 'vgfmri3_bait', 'vgfmri3_lemmings', 'vgfmri3_plaqueAttack', 'vgfmri3_zelda']
    else:
        games = ['vgfmri4_chase', 'vgfmri4_helper', 'vgfmri4_bait', 'vgfmri4_lemmings', 'vgfmri4_avoidgeorge', 'vgfmri4_zelda']

    # Do it game by game, so we know what the last theory was from the previous play
    for game in games:
        query['game_name'] = game

        plays = db.plays.find(query, no_cursor_timeout=True).sort('start_time')

        print 'Running fmri_approachAvoid.py with query:'
        print query

        # TODO dedupe with fmri_empaReplay

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
            assert game['name'] == play['game_name']
            game_name = game['name']

            print 'Computing approach_avoid for subj %s, run %d, block %d, instance %d, play %d: %s (%s), desc %d, level %d' % (play['subj_id'], play['run_id'], play['block_id'], play['instance_id'], play['play_id'], game['name'], game['fake_name'], play['desc_id'], play['level_id'])

            q = {'play_key': play['_id']}
            print q
            print db.approach_avoid.count(q)
            if db.approach_avoid.count(q) > 0:
                print '..........skipping: already computed '
                assert False, "this messes up last_theory_from_previous_play...." # TODO fix
                continue

            # get states
            zstates = play['zstates']
            states = core.VGDLParser.decompress(zstates)
            states = states['states'] # dummy dict

            zkeystates = play['zkeystates']
            keystates = core.VGDLParser.decompress(zkeystates)
            keystates = keystates['keystates'] # dummy dict

            # Fix game & state colors for subjects 12..32  ...
            chelsea_fix_states_avatar_only(states, game, subj_id, play)

            # create object to hold play postprocessing data
            # similar to regressors (see fmri_empaReplay.py)
            approach_avoid = {
                'play_key': play['_id'],
                'subj_id': play['subj_id'],
                'run_id': play['run_id'],
                'block_id': play['block_id'],
                'instance_id': play['instance_id'],
                'play_id': play['play_id'],
                'game_name': play['game_name'],
                'level_id': play['level_id'],
                'type': 'fmri_approachAvoid'
            }

            state_timestamps = []
            # initialize effects_by_valence
            effects_by_valence = {}
            for valance in sprite_valences[game_name].keys():
                effects_by_valence[valance] = {}
                for sprite_class in sprite_valences[game_name][valence].keys():
                    effects_by_valence[valance][sprite_class] = []

            assert(len(states) == len(keystates))
            for t in range(len(states)):
                state = states[t]
                state_timestamps.append(state['ts'])

                touched_sprites = set()
                for eff in state['effectListByClass']:
                    if 'avatar' == eff[1]:
                        touched_sprites.add(eff[2])
                    elif 'avatar' == eff[2]:
                        touched_sprites.add(eff[1])

            if len(touched_sprites)>0:
                embed()
                snaohe

            print('touched sprites', touched_sprites)
            for valance in sprite_valences[game_name].keys():
                for sprite_class in sprite_valences[game_name][valence].keys():
                    is_touched = sprite_class in touched_sprites
                    effects_by_valence[valance][sprite_class].append(is_touched)



            approach_avoid['state_timestamps'] = state_timestamps
            approach_avoid['effects_by_valence'] = effects_by_valence
            approach_avoid['approach_avoid_ts'] = time.time() # for sanity checks
            approach_avoid['approach_avoid_dts'] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S") # for sanity checks

            # Insert into database
            #

            db.approach_avoid.insert_one(approach_avoid)

        plays.close()
        
    print 'done!'



if __name__ == '__main__':
    subj_id = sys.argv[1]

    playsPostprocApproachAvoid(subj_id)
