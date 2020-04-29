from pymongo import MongoClient
import pprint
import random
from datetime import datetime
import time

import json
import sys
import uuid
import csv
import os
import socket
from collections import defaultdict
from vgdl import core
from IPython import embed
from vgdl.EMPA import Agent
import cPickle, cloudpickle
from vgdl.environment import Environment
from vgdl.hyperparameters import hyperparameter_sets

import pygame

# USAGE: python fmri_empaReplay.py [subj_id] [run_id*] [block_id*] [instance_id*] [play_id*]
#        python fmri_empaReplay.py [subj_id] [game_name]
#        python fmri_empaReplay.py [subj_id] [run_id] [game_name]
# * - optional
# copied from fmri_empaPlay.py


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


if 'omchil' in socket.gethostname():
    # local 
    client = MongoClient('localhost', 27017)
else:
    # cluster
    client = MongoClient('holy7c22306.rc.fas.harvard.edu', 27017)

db = client['heroku_7lzprs54']

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    assert False

if __name__ == '__main__':
    subj_id = sys.argv[1]

    query = {'subj_id': subj_id}

    if len(sys.argv) > 2:
        if is_int(sys.argv[2]):
            query['run_id'] = int(sys.argv[2])
        else:
            assert len(sys.argv) == 3
            query['game_name'] = sys.argv[2]
    if len(sys.argv) > 3:
        if is_int(sys.argv[3]):
            query['block_id'] = int(sys.argv[3])
        else:
            assert len(sys.argv) == 4
            query['game_name'] = sys.argv[3]
    if len(sys.argv) > 4:
        if is_int(sys.argv[4]):
            query['instance_id'] = int(sys.argv[4])
        else:
            assert len(sys.argv) == 5
            query['game_name'] = sys.argv[4]
    if len(sys.argv) > 5:
        if is_int(sys.argv[5]):
            query['play_id'] = int(sys.argv[5])
        else:
            assert len(sys.argv) == 6
            query['game_name'] = sys.argv[5]
    if len(sys.argv) > 6:
        query['game_name'] = sys.argv[6]

    plays = db.plays.find(query).sort('start_time')

    print 'Running fmri_empaReplay with query:'
    print query

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
        assert game['name'] == play['game_name']

        print 'EMPA playing subj %s, run %d, block %d, instance %d, play %d: %s (%s), desc %d, level %d' % (play['subj_id'], play['run_id'], play['block_id'], play['instance_id'], play['play_id'], game['name'], game['fake_name'], play['desc_id'], play['level_id'])

        q = {'play_key': play['_id']}
        count = db.regressors.count(q)
        print q, count
        # this is so that we can resume from the last savedCurriculum e.g. after a crash
        if count > 0:
            print '........................................... found regressors; skipping................................'
            continue


	# get states
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

        video_name = 's={}_r={}_b={}_i={}_p={}_{}'.format(play['subj_id'], play['run_id'], play['block_id'], play['instance_id'], play['play_id'], game['name'])
        print 'video_name = ', video_name

        # this is the money that gets passed to playCurriculum
        all_pairs[game['name']].append((play['game_str'], play['level_str'], states, keystates, video_name)) # TODO momchil OOM? 

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
    didSomething = False

    start = time.time()
    print 'time start: ', datetime.now()

    for game_name, level_game_pairs in all_pairs.iteritems():
        didSomething = True

        print 'Playing game ', game_name, ': ', len(level_game_pairs), ' instances'

        regs = all_regressors[game_name] 
        assert len(regs) == len(level_game_pairs)

        movie_names = all_movie_names[game_name]
        assert len(movie_names) == len(level_game_pairs)

        # defaults from load_games.py 
        # python -m vgdl.load_games --game_name tiny_zelda
        task_ID = 'subj={}'.format(subj_id)
        agent = Agent('full', game_name, hyperparameter_sets=hyperparameter_sets, hyperparameter_index='short-term', metacontroller_index=0, IW_k=1, extra_atom_allowed=True, task_ID=task_ID)
        agent.record_fMRIRegressors = True

        environment = Environment(game_name, agent, task_ID=task_ID, produce_printout=False)
        curriculumRegressors = environment.playCurriculum(level_game_pairs=level_game_pairs, make_movie=False, heatmap=False, playback=True, movie_names=movie_names)
        assert len(curriculumRegressors) == len(regs)

        for i in range(len(curriculumRegressors)): # for each play
            reg = regs[i]

            # prepare regressors for insert into Mongo
            reg['regressors'] = curriculumRegressors[i]
            reg['dt'] = datetime.now()
            reg['ts'] = time.time()

            # special care for theory which does not serialize into BSON for Mongo
            # use cloudpickle instead & save on disk TODO find better option

            theoriesDir = 'theories'
            if theoriesDir not in os.listdir('.'):
                os.makedirs(theoriesDir)

            filename = os.path.join(theoriesDir, 'theory_' + str(reg['play_key']) + '_' + str(reg['ts'])) + '.pickle'
            with open(filename, 'wb') as f:
                cloudpickle.dump(reg['regressors']['theory'], f)

            reg['regressors']['theory_filename'] = filename # remove from regressor object
            reg['regressors']['theory'] = [] # remove from regressor object


            db.regressors.insert_one(reg)

    if didSomething:
        print 'Completed!'
    else:
        print 'Nothing to do...'

    end = time.time()
    print 'time end: ', datetime.now()
    print 'time elapsed: ', (end - start), ' s'
