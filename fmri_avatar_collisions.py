# extract Avatar collisions
# see also fmri_avatar_interactions.py

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

def get_overlapping_objects(objects, x, y):
    object_types = []
    key = u'(%d, %d)' % (x, y)
    for object_type, object_instances in objects.iteritems():
        if key in object_instances.keys():
            object_types.append(object_type)
    return object_types

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--subj-id', required=True)

    config = parser.parse_args()
    print(config)

    #agent_name = config.agent_name
    subj_id = config.subj_id

    query = {'subj_id': subj_id}
    print 'Running fmri_avatar_collisions.py with query:'
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

            avatar = state['objects']['avatar']
            if len(avatar.keys()) == 0:
                # Avatar is dead
                continue 
            avatar = avatar[avatar.keys()[0]]

            dirs = [[0, 0], [1, 0], [-1, 0], [0, 1], [0, -1]]
            for d in dirs:
                new_x = avatar['x'] + avatar['rect']['size'][0] * d[0]
                new_y = avatar['y'] + avatar['rect']['size'][1] * d[1]

                overlapping_objects = get_overlapping_objects(state['objects'], new_x, new_y)
                for object_type in overlapping_objects:
                    if object_type == 'avatar':
                        continue
                    #print avatar, new_x, new_y, object_type
                    #embed()

                    subj_ids.append(int(subj_id))
                    game_names.append(play['game_name'])
                    run_ids.append(play['run_id'])
                    block_ids.append(play['block_id'])
                    instance_ids.append(play['instance_id'])
                    play_ids.append(play['play_id'])
                    levels.append(play['level_id'] + 1)
                    timestamps.append(state['ts'] - play['run_start_ts'])
                    frames.append(t)
                    object_types.append(object_type)

                    print t, object_type

    filename = os.path.join(matDir, 'fmri_avatar_collisions_subj=%s.mat' % (subj_id))
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
    }
    scipy.io.savemat(filename, d)
