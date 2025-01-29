# extract Avatar interactions
# note that this omits collisions that are not interactions in the game rules

import pprint
import argparse
import random
from datetime import datetime
import time

import json
import scipy.stats
import scipy.io
import sys
import uuid
import csv
import os
import socket
import glob
from collections import defaultdict
from vgdl import core
from IPython import embed
from vgdl.EMPA import Agent
import cPickle, cloudpickle
from vgdl.random_agent import RandomAgent
from vgdl.dqn_agent import DQNAgent
from vgdl.environment import Environment
import vgdl.core
from vgdl.hyperparameters import hyperparameter_sets
import utils
import string

import pygame
from fmri_agentReplay import fix_states

client = utils.get_mongo_client()
db = client['heroku_7lzprs54']

# Cedric: To make the code work in the same way as before when executed on the
# server, change the string 'harvard' below to match the server hostname
if ('harvard' not in socket.gethostname()) or 'ncfood' in socket.gethostname() or 'ncflogin' in socket.gethostname():
    # local on my Mac, or on a login / VDI node
    matDir = 'mat'
else:
    # cluster
    matDir = os.path.join(os.environ.get('MY_LAB'), 'VGDL', 'mat')
    print matDir

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--subj-id', required=True)

    config = parser.parse_args()
    print(config)

    #agent_name = config.agent_name
    subj_id = config.subj_id

    query = {'subj_id': subj_id}
    print 'Running fmri_avatar_interactions.py with query:'
    print query
    plays = db.plays.find(query, {'_id': 1}).sort('start_time')

    # TODO dedupe with fmri_agentPlay

    pks = []
    for play in plays:
        pks.append(play['_id'])
    del plays

    subj_ids = []
    game_names = []
    run_ids = []
    block_ids = []
    instance_ids = []
    play_ids = []
    levels = []
    timestamps = []
    frames = []
    object_types = []
    outcomes = []

    for pk in pks:
        q = {'_id': pk}

        play = db.plays.find_one(q)
        subj = db.subjects.find_one({'subj_id': subj_id})
        game = subj['games'][play['game_id']]
        game_str = game['descs'][play['desc_id']]
        level_str = game['levels'][play['level_id']]
        assert game_str == play['game_str']
        assert level_str == play['level_str']
        assert game['name'] == play['game_name']

        zstates = play['zstates']
        states = core.VGDLParser.decompress(zstates)
        states = states['states'] # dummy dict
        fix_states(states, game, subj_id, play)

        print play['_id'], play['run_id'], play['block_id'], play['instance_id'], play['play_id']

        for t in range(len(states)):
            state = states[t]

            for eff in state['effectListByClass']:
                if 'avatar' == eff[1] or 'avatar' == eff[2]:
                    subj_ids.append(int(subj_id))
                    game_names.append(play['game_name'])
                    run_ids.append(play['run_id'])
                    block_ids.append(play['block_id'])
                    instance_ids.append(play['instance_id'])
                    play_ids.append(play['play_id'])
                    levels.append(play['level_id'] + 1)
                    timestamps.append(state['ts'] - play['run_start_ts'])
                    frames.append(t)
                    object_types.append(eff[2] if 'avatar' == eff[1] else eff[1])
                    outcomes.append(eff[0])
                    print eff


    filename = os.path.join(matDir, 'fmri_avatar_interactions_subj=%s.mat' % (subj_id))
    d = {
        'subj_ids': subj_ids,
        'game_names': game_names,
        'run_ids': run_ids,
        'block_ids': block_ids,
        'instance_ids': instance_ids,
        'play_ids': play_ids,
        'levels': levels,
        'timestamps': timestamps,
        'frames': frames,
        'object_types': object_types,
        'outcomes': outcomes
    }
    scipy.io.savemat(filename, d)
