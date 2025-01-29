# extract Avatar interactions for artificial agents
# similar to fmri_avatar_interactions.py

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
    parser.add_argument('--agent-name', required=True)
    parser.add_argument('--tag', default=None)

    config = parser.parse_args()
    print(config)

    agent_name = config.agent_name
    subj_id = config.subj_id
    tag = config.tag

    if tag is not None:
        query = {'subj_id': subj_id, 'agent_name': agent_name, 'tag': tag}
    else:
        query = {'subj_id': subj_id, 'agent_name': agent_name}
    print 'Running fmri_agent_avatar_interactions.py with query:'
    print query
    ress = db.sim_results.find(query, {'_id': 1}).sort('ts')

    ks = []
    for res in ress:
        ks.append(res['_id'])
    del ress

    # TODO deduplicate with fmri_avatar_interactions.py
    agent_names = []
    subj_ids = []
    game_names = []
    levels = []
    timestamps = []
    frames = []
    object_types = []
    outcomes = []

    for k in ks:
        res = db.sim_results.find_one({'_id': k})

        for sim_play in res['results']:

            zstates = sim_play['zstates']
            states = core.VGDLParser.decompress(zstates)
            states = states['states'] # dummy dict

            print sim_play['agent'], sim_play['game_name'], sim_play['level']

            for t in range(len(states)):
                state = states[t]

                acf = False
                for eff in state['effectListByClass']:
                    if 'avatar' == eff[1] or 'avatar' == eff[2]:
                        agent_names.append(agent_name)
                        subj_ids.append(int(subj_id))
                        game_names.append(sim_play['game_name'])
                        levels.append(sim_play['level'])
                        timestamps.append(state['ts'])
                        frames.append(t)
                        object_types.append(eff[2] if 'avatar' == eff[1] else eff[1])
                        outcomes.append(eff[0])
                        print eff

                #break

        #break

    filename = os.path.join(matDir, 'fmri_agent_avatar_interactions_subj=%s_agent=%s_tag=%s.mat' % (subj_id, agent_name, tag))
    d = {
        'tag': tag,
        'agent_names': agent_names,
        'subj_ids': subj_ids,
        'game_names': game_names,
        'levels': levels,
        'timestamps': timestamps,
        'frames': frames,
        'object_types': object_types,
        'outcomes': outcomes
    }
    scipy.io.savemat(filename, d)
