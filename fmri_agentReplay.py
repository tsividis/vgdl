import pprint
import argparse
import random
from datetime import datetime
import time

import json
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

# USAGE: python fmri_agentReplay.py [agent_name] [subj_id] [run_id*] [block_id*] [instance_id*] [play_id*]
#        python fmri_agentReplay.py [agent_name] [subj_id] [game_name]
#        python fmri_agentReplay.py [agent_name] [subj_id] [run_id] [game_name]
# * - optional
# copied from fmri_agentPlay.py


show_symbols = False  # optionally do not show symbols, for DQN; It's important, since there are no symbols during training

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

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
    #client = MongoClient('holy2a05207.rc.fas.harvard.edu', 27017)

if not os.path.exists(theoriesDir):
    os.makedirs(theoriesDir)
if not os.path.exists(layersDir):
    os.makedirs(layersDir)

db = client['heroku_7lzprs54']

def fix_states(states, game, subj_id, play):
    # Chelsea's color mess up fix
    # change avatar color to default color
    if subj_id not in ['12', '13', '14', '15', '16', '17']:
        return
    assert play['game_str'] == game['descs'][play['desc_id']]
    if game['name'] == 'vgfmri4_chase':
        assert 'MovingAvatar color=GREEN' in game['descs'][play['desc_id']]
        game['descs'][play['desc_id']] = game['descs'][play['desc_id']].replace('MovingAvatar color=GREEN', 'MovingAvatar color=DARKBLUE')
        avatar_color = 'GREEN'
    elif game['name'] == 'vgfmri4_bait':
        assert 'MovingAvatar color=YELLOW' in game['descs'][play['desc_id']]
        game['descs'][play['desc_id']] = game['descs'][play['desc_id']].replace('MovingAvatar color=YELLOW', 'MovingAvatar color=DARKBLUE')
        avatar_color = 'YELLOW'
    else:
        return
    play['game_str'] = game['descs'][play['desc_id']]
    print 'Fixing states for ', subj_id, ' ', game['name'], ' - ', avatar_color

    for i in range(len(states)):
        state = states[i]
        for effect in state['effectListByColor']:
            if effect[1] == avatar_color:
                effect[1] = 'DARKBLUE'
            if effect[2] == avatar_color:
                effect[2] = 'DARKBLUE'
        for key, s in state['objects']['avatar'].iteritems():
            s['colorName'] = 'DARKBLUE'
            s['color'] = [255, 82, 82]
        if avatar_color in str(state):
            print 'found avatar color in state'
            embed()




def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    assert False

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--agent-name', required=True)
    parser.add_argument('--subj-id', required=True)
    parser.add_argument('--run-id', default=None)
    parser.add_argument('--block-id', default=None)
    parser.add_argument('--instance-id', default=None)
    parser.add_argument('--play-id', default=None)
    parser.add_argument('--game-name', default=None)

    config = parser.parse_args()
    print(config)

    agent_name = config.agent_name
    subj_id = config.subj_id

    query = {'subj_id': subj_id}
    if config.run_id is not None:
        query['run_id'] = int(config.run_id)
    if config.block_id is not None:
        query['block_id'] = int(config.block_id)
    if config.instance_id is not None:
        query['instance_id'] = int(config.instance_id)
    if config.play_id is not None:
        query['play_id'] = int(config.play_id)
    if config.game_name is not None:
        query['game_name'] = config.game_name

    plays = db.plays.find(query).sort('start_time')

    print 'Running fmri_agentReplay with query:'
    print query

    # TODO dedupe with fmri_agentPlay

    all_pairs = {}
    all_regressors = {}
    all_movie_names = {}

    # Hack: we need to change the block size for the earlier subject, since the block sizes were smaller and the sprite coordinates were correspondingly different
    if int(subj_id) <= 11:
        vgdl.core.BLOCK_SIZE = 20
    
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
        #count = db.regressors_cannon_spriteEvery20.count(q)
        if agent_name == 'EMPA':
            count = db.regressors.count(q)
        elif agent_name == 'DQN':
            count = db.dqn_regressors.count(q)
        else:
            assert False, 'Invalid agent name ' + agent_name
        print q, count

        # this is so that we can resume from the last savedCurriculum e.g. after a crash
        if count > 0:
            print '........................................... found regressors; skipping................................'
            continue


	    # get states
        zstates = play['zstates']
        states = core.VGDLParser.decompress(zstates)
        states = states['states'] # dummy dict
        fix_states(states, game, subj_id, play)

        zkeystates = play['zkeystates']
        keystates = core.VGDLParser.decompress(zkeystates)
        keystates = keystates['keystates'] # dummy dict

        # optionally remove symbols, for DQN/PCA/etc
        # see setFullState()
        if not show_symbols:
            for fs in states:
                for key, ss in fs['objects'].iteritems():
                    for ID, attrs in ss.iteritems():
                        attrs['symbol'] = None

        #embed()
        #continue

        if game['name'] not in all_pairs:
            all_pairs[game['name']] = [] 
            all_regressors[game['name']] = [] 
            all_movie_names[game['name']] = [] 

        video_name = 'fmri_agentReplay_{}_s={}_r={}_b={}_i={}_p={}_{}'.format(agent_name, play['subj_id'], 
            play['run_id'], play['block_id'], play['instance_id'], play['play_id'], game['name'])
        print 'video_name = ', video_name

        # this is the money that gets passed to playCurriculum
        reset_finalTimeStepList = play['instance_id'] == 0 and play['play_id'] == 0 # reset finalTimeStepList before every block -- balance between psychological plausibility and practicality (i.e. avoiding OOM in plaqueAttack)
        all_pairs[game['name']].append((play['game_str'], play['level_str'], states, keystates, video_name, reset_finalTimeStepList)) # TODO momchil OOM? 

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
            'type': 'fmri_agentReplay',
            'reg_ts': time.time(), # for sanity checks
            'reg_dts': datetime.now().strftime("%m/%d/%Y, %H:%M:%S") # for sanity checks
        }
        all_regressors[game['name']].append(reg)
        all_movie_names[game['name']].append(video_name)


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

        task_ID = 'subj={}'.format(subj_id) # This is crucial to make sure the curriculum is subject-specific
        subj_game_videos_dir = os.path.join(videosDir, 'DQN', 'subj_'+str(subj_id), game_name)
        subj_game_images_dir = os.path.join(imagesDir, 'DQN', 'subj_'+str(subj_id), game_name)

        # create agent
        if agent_name == 'EMPA':
            # defaults from load_games.py 
            # python -m vgdl.load_games --game_name tiny_zelda
            agent = Agent('full', game_name, hyperparameter_sets=hyperparameter_sets, hyperparameter_index='short-term', 
                metacontroller_index=0, IW_k=1, extra_atom_allowed=True, task_ID=task_ID)
        elif agent_name == 'DQN':
            # render videos based on the DQN inputs, as a sanity check
            agent = DQNAgent(game_name, (vgdl.core.render_screensize[0], vgdl.core.render_screensize[1], 3),
                make_videos=True, movie_names=movie_names, videos_dir=subj_game_videos_dir, 
                images_dir=subj_game_images_dir, task_ID=task_ID)
        else:
            assert False, 'Invalid agent name ' + agent_name

        # fMRI mode
        agent.record_fMRIRegressors = True

        environment = Environment(game_name, agent, task_ID=task_ID, produce_printout=False)
        curriculumRegressors = environment.playCurriculum(
            level_game_pairs=level_game_pairs, make_movie=False, heatmap=False, playback=True)
        assert len(curriculumRegressors) == len(regs)

        for i in range(len(curriculumRegressors)): # for each play
            reg = regs[i]

            # prepare regressors for insert into Mongo
            reg['regressors'] = curriculumRegressors[i]
            reg['dt'] = datetime.now()
            reg['ts'] = time.time()

            # special care for theory which does not serialize into BSON for Mongo
            # use cloudpickle instead & save on disk TODO find better option

            if agent_name == 'EMPA':
                # serialize theory sequence
                filename = os.path.join(theoriesDir, 'theory_' + str(reg['play_key']) + '_' + str(reg['ts'])) + '.pickle'
                with open(filename, 'wb') as f:
                    cloudpickle.dump(reg['regressors']['theory'], f)
                reg['regressors']['theory_filename'] = filename
                reg['regressors']['theory'] = [] # remove from regressor object

                # serialize time steps (used to calculate likelihood) 
                for j in range(len(reg['regressors']['newTimeStep'])):
                    reg['regressors']['newTimeStep'][j][0].rle = None # delete RLE's before saving; they're huge and we don't need them for computing likelihoods
                filename = os.path.join(theoriesDir, 'newTimeStep_' + str(reg['play_key']) + '_' + str(reg['ts'])) + '.pickle'
                with open(filename, 'wb') as f:
                    cloudpickle.dump(reg['regressors']['newTimeStep'], f)
                reg['regressors']['newTimeStep_filename'] = filename
                reg['regressors']['newTimeStep'] = [] # remove from regressor object

                # serialize plans
                filename = os.path.join(theoriesDir, 'plans_' + str(reg['play_key']) + '_' + str(reg['ts'])) + '.pickle'
                with open(filename, 'wb') as f:
                    cloudpickle.dump(reg['regressors']['plans'], f)
                reg['regressors']['plans_filename'] = filename
                reg['regressors']['plans'] = [] # remove from regressor object

                # same deal with sprite distribution
                # TODO too big -- risks running out of disk space; shelve for now
                #
                #filename = os.path.join(theoriesDir, 'sprite_distr_' + str(reg['play_key']) + '_' + str(reg['ts'])) + '.pickle'
                #with open(filename, 'wb') as f:
                #    cloudpickle.dump(reg['regressors']['sprite_distr'], f)
                #reg['regressors']['sprite_distr_filename'] = filename
                #reg['regressors']['sprite_distr'] = [] # remove from regressor object

                # insert regressor into mongo
                #db.regressors_cannon_spriteEvery20.insert_one(reg)
                db.regressors.insert_one(reg)

            elif agent_name == 'DQN':

                # serialize layer sequences
                for regressor_name in reg['regressors'].keys():
                    if regressor_name.startswith('layer_'):
                        filename = os.path.join(layersDir, regressor_name + '_' + str(reg['play_key']) + '_' + str(reg['ts'])) + '.pickle'
                        with open(filename, 'wb') as f:
                            cloudpickle.dump(reg['regressors'][regressor_name], f)
                        reg['regressors'][regressor_name + '_filename'] = filename
                        reg['regressors'][regressor_name] = [] # remove from regressor object

                db.dqn_regressors.insert_one(reg)

            else:
                assert False, 'Invalid agent name ' + agent_name

    if didSomething:
        print 'Completed!'
    else:
        print 'Nothing to do...'

    end = time.time()
    print 'time end: ', datetime.now()
    print 'time elapsed: ', (end - start), ' s'
