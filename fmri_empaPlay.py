from pymongo import MongoClient
import pprint
import random
from datetime import datetime

import json
import sys
import csv
from collections import defaultdict
from vgdl import core
from IPython import embed
from vgdl.EMPA import Agent
from vgdl.environment import Environment
from vgdl.hyperparameters import hyperparameter_sets
import vgdl.core

# USAGE: python fmri_empaPlay.py [subj_id] [run_id] [block_id] [instance_id*] [play_id*]
# * - optional
# copied from fmri_replay.py

# TODO dedupe with fmri_empaReplay.py

client = MongoClient('localhost', 27017)
db = client['heroku_7lzprs54']

vgdl.core.BLOCK_SIZE = 20  # for subjects 1..11, the block_size was 20; then it was 35

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

        if game['name'] not in all_pairs:
            all_pairs[game['name']] = [] 
            all_regressors[game['name']] = [] 
            all_movie_names[game['name']] = [] 

        video_name = 'fmri_empaPlay_s={}_r={}_b={}_i={}_p={}_{}'.format(play['subj_id'], play['run_id'], play['block_id'], play['instance_id'], play['play_id'], game['name'])
        print 'video_name = ', video_name

        # this is the money that gets passed to playCurriculum
        reset_finalTimeStepList = play['instance_id'] == 0 and play['play_id'] == 0 # reset finalTimeStepList before every block -- balance between psychological plausibility and practicality (i.e. avoiding OOM in plaqueAttack)
        all_pairs[game['name']].append((play['game_str'], play['level_str'], video_name, reset_finalTimeStepList)) # TODO momchil OOM? 

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
            'type': 'fmri_empaPlay'
        }
        all_regressors[game['name']].append(reg)

        movie_name = game['name'] + '_lev=' + str(play['level_id']) + '_' + str(play['play_id'])
        all_movie_names[game['name']].append(movie_name)


    # for each game, play all instances as part of one curriculum
    # allows within-game transfer but no cross-game transfer
    #
    for game_name, level_game_pairs in all_pairs.iteritems():
        print 'Playing game ', game_name, ': ', len(level_game_pairs), ' instances'

        regs = all_regressors[game_name] 
        assert len(regs) == len(level_game_pairs)

        movie_names = all_movie_names[game_name]
        assert len(movie_names) == len(level_game_pairs)

        # defaults from load_games.py 
        # python -m vgdl.load_games --game_name tiny_zelda
        task_ID = '0'
        agent = Agent('full', game_name, hyperparameter_sets=hyperparameter_sets, hyperparameter_index='short-term', metacontroller_index=0, IW_k=1, extra_atom_allowed=True, task_ID=task_ID)

        # TODO momchil CAREFUL with saved curricula! might reload old agent; figure out how to deal with it
        environment = Environment(game_name, agent, task_ID=task_ID, produce_printout=True)
        environment.playCurriculum(level_game_pairs=level_game_pairs, make_movie=True, heatmap=False, movie_names=movie_names)
