from pymongo import MongoClient
import pprint
import random
from datetime import datetime
import argparse
import time

import json
import sys
import csv
import os
import socket
import utils
from collections import defaultdict
from vgdl import agent_utils, core
from IPython import embed
from vgdl.EMPA import Agent
from vgdl.random_agent import RandomAgent
from vgdl.dqn_agent import DQNAgent
from vgdl.environment import Environment
from vgdl.hyperparameters import hyperparameter_sets
import vgdl.core
import pandas as pd

FMRI_STEPS_PER_LEVEL = 60 * 20  # momchil: fMRI max steps per instance (i.e. until end of level) = 60 s x 20 fps

# USAGE: python fmri_empaPlay.py [agent_name] [subj_id] [run_id] [block_id] [instance_id*] [play_id*]
# * - optional
# copied from fmri_replay.py

# TODO dedupe with fmri_empaReplay.py

client = utils.get_mongo_client()

if 'omchil' in socket.gethostname():
    # local 
    theoriesDir = 'theories'
    layersDir = 'layers'
    imagesDir = 'images'
    videosDir = 'videos'
else:
    # Cannon 
    theoriesDir = os.path.join(os.environ.get('MY_SCRATCH'), 'VGDL', 'theories')
    layersDir = os.path.join(os.environ.get('MY_SCRATCH'), 'VGDL', 'layers')
    videosDir = os.path.join(os.environ.get('MY_LAB'), 'VGDL', 'videos')
    imagesDir = os.path.join(os.environ.get('MY_LAB'), 'VGDL', 'images')
    print theoriesDir, layersDir, videosDir, imagesDir
    # NCF cluster
    #client = MongoClient('holy7c22211.rc.fas.harvard.edu', 27017)

if not os.path.exists(theoriesDir):
    os.makedirs(theoriesDir)
if not os.path.exists(layersDir):
    os.makedirs(layersDir)

db = client['heroku_7lzprs54']

vgdl.core.BLOCK_SIZE = 20  # for subjects 1..11, the block_size was 20; then it was 35

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--agent-name', required=True)
    parser.add_argument('--subj-id', required=True)
    parser.add_argument('--run-id', default=None)
    parser.add_argument('--block-id', default=None)
    parser.add_argument('--instance-id', default=None)
    #parser.add_argument('--play-id', default=None)
    parser.add_argument('--game-name', default=None)
    parser.add_argument('--tag', default='')
    parser.add_argument('--steps-per-level', default=FMRI_STEPS_PER_LEVEL)
    parser.add_argument('--insert', action='store_true', default=False)

    config = parser.parse_args()
    print(config)

    agent_name = config.agent_name
    subj_id = config.subj_id

    query = {'subj_id': subj_id}

    if config.run_id is not None:
        query['run_id'] = int(config.run_id)
    else:
        query['run_id'] = { '$gt': 0, '$lt': 7 }
    if config.block_id is not None:
        query['block_id'] = int(config.block_id)
    if config.instance_id is not None:
        query['instance_id'] = int(config.instance_id)
    #if config.play_id is not None:
    #    query['play_id'] = int(config.play_id)
    query['play_id'] = 0 # for generative play, only pass one play per instance, and then the agent can potentially play multiple plays
    if config.game_name is not None:
        query['game_name'] = config.game_name

    plays = db.plays.find(query)

    all_pairs = {}
    all_movie_names = {}

    for play in plays:
        subj = db.subjects.find_one({'subj_id': subj_id})
        game = subj['games'][play['game_id']]
        if subj_id in ['12', '13', '14', '15', '16', '17']:
            # Chelsea's color mess up fix
            # use game description from games collection
            count = db.games.count_documents({'name': game['name']})
            assert count == 1
            game_from_db = db.games.find_one({'name': game['name']})
            game['descs'] = game_from_db['descs']
            print 'Using colors from the games collection'
        game_str = game['descs'][play['desc_id']]
        level_str = game['levels'][play['level_id']]
        if subj_id not in ['12', '13', '14', '15', '16', '17']:
            assert game_str == play['game_str']
        assert level_str == play['level_str']

        print 'EMPA playing subj %s, run %d, block %d, instance %d, play %d: %s (%s), desc %d, level %d' % (play['subj_id'], play['run_id'], play['block_id'], play['instance_id'], play['play_id'], game['name'], game['fake_name'], play['desc_id'], play['level_id'])

        if game['name'] not in all_pairs:
            all_pairs[game['name']] = [] 
            all_movie_names[game['name']] = [] 

        video_name = 'fmri_empaPlay_{}_s={}_r={}_b={}_i={}_p={}_{}'.format(agent_name, play['subj_id'], 
            play['run_id'], play['block_id'], play['instance_id'], play['play_id'], game['name'])
        print 'video_name = ', video_name

        # this is the money that gets passed to playCurriculum
        reset_finalTimeStepList = play['instance_id'] == 0 and play['play_id'] == 0 # reset finalTimeStepList before every block -- balance between psychological plausibility and practicality (i.e. avoiding OOM in plaqueAttack)
        all_pairs[game['name']].append((game_str, play['level_str'], video_name, reset_finalTimeStepList, play['level_id'])) # TODO momchil OOM? 

        movie_name = game['name'] + '_lev=' + str(play['level_id']) + '_' + str(play['play_id'])
        all_movie_names[game['name']].append(movie_name)


    # for each game, play all instances as part of one curriculum
    # allows within-game transfer but no cross-game transfer
    #
    for game_name, level_game_pairs in all_pairs.iteritems():
        print 'Playing game ', game_name, ': ', len(level_game_pairs), ' instances'

        movie_names = all_movie_names[game_name]
        assert len(movie_names) == len(level_game_pairs)

        task_ID = 'subj={}'.format(subj_id) # This is crucial to make sure the curriculum is subject-specific
        subj_game_videos_dir = os.path.join(videosDir, 'DQN', 'subj_'+str(subj_id), game_name)
        subj_game_images_dir = os.path.join(imagesDir, 'DQN', 'subj_'+str(subj_id), game_name)


        # create agent
        if agent_name == 'EMPA':
            # defaults from load_games.py 
            # python -m vgdl.load_games --game_name tiny_zelda
            agent = Agent('full', game_name, hyperparameter_sets=hyperparameter_sets, hyperparameter_index='short-term', 
                metacontroller_index=0, IW_k=1, extra_atom_allowed=True, task_ID=task_ID)
        elif agent_name == 'Random':
            agent = RandomAgent(game_name)
        elif agent_name == 'DQN':
            agent = DQNAgent(game_name, (vgdl.core.render_screensize[0], vgdl.core.render_screensize[1], 3),
                make_videos=True, movie_names=movie_names, videos_dir=subj_game_videos_dir, 
                images_dir=subj_game_images_dir, task_ID=task_ID)
        else:
            assert False, 'Invalid agent name ' + agent_name

        # play
        # TODO momchil CAREFUL with saved curricula! might reload old agent; figure out how to deal with it
        environment = Environment(game_name, agent, task_ID=task_ID, produce_printout=False)
        curriculumResults = environment.playCurriculum(level_game_pairs=level_game_pairs, make_movie=False, heatmap=False, steps_per_level=int(config.steps_per_level))

        # optionally insert into Mongo
        if config.insert:
            res = {
                'subj_id': subj_id,
                'game_name': game_name,
                'agent_name': agent_name,
                'tag': config.tag,
                'dt': datetime.now(),
                'ts': time.time(),
                'results': curriculumResults,
            }
            db.sim_results.insert_one(res)
