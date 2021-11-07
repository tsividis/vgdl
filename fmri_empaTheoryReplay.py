# TODO dedupe with fmri_empaReplay.py
# run planner on state/action and theory replay, for computing likelihood of behavior

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
from bson.objectid import ObjectId

import pygame

# USAGE: python fmri_empaTheoryReplay.py [subj_id] [run_id*] [block_id*] [instance_id*] [play_id*] [game_name*] [theory_seq_filename]
#        python fmri_empaTheoryReplay.py [subj_id] [game_name] [theory_seq_filename]
#        python fmri_empaTheoryReplay.py [subj_id] [run_id] [game_name] [theory_seq_filename]
# * - optional
# copied from fmri_empaPlay.py
#
# EXAMPLE: rm savedCurricula/*; python fmri_empaTheoryReplay.py 1 1 0 0 0 vgfmri3_chase ../../matlab/VGDL_fMRI/mat/decode_gp_CV_subj\=1_test.mat


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


if 'omchil' in socket.gethostname():
    # local 
    client = MongoClient('localhost', 27017)
    theoriesDir = 'theories'
else:
    # cluster
    client = MongoClient('holy7c22103.rc.fas.harvard.edu', 27017)
    theoriesDir = os.path.join(os.environ.get('MY_LAB'), 'VGDL', 'theories')
    # NCF cluster
    #client = MongoClient('holy7c22103.rc.fas.harvard.edu', 27017)
print theoriesDir

if not os.path.exists(theoriesDir):
    os.makedirs(theoriesDir)

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

    assert len(sys.argv) > 3
    if len(sys.argv) > 3:
        if is_int(sys.argv[2]):
            query['run_id'] = int(sys.argv[2])
        else:
            assert len(sys.argv) == 4
            query['game_name'] = sys.argv[2]
            theory_seq_filename = sys.argv[3] # e.g. ../../matlab/VGDL_fMRI/decode_gp_CV_HRR_subj=1_minint=300_2.mat
    if len(sys.argv) > 4:
        if is_int(sys.argv[3]):
            query['block_id'] = int(sys.argv[3])
        else:
            assert len(sys.argv) == 5
            query['game_name'] = sys.argv[3]
            theory_seq_filename = sys.argv[4]
    if len(sys.argv) > 5:
        if is_int(sys.argv[4]):
            query['instance_id'] = int(sys.argv[4])
        else:
            assert len(sys.argv) == 6
            query['game_name'] = sys.argv[4]
            theory_seq_filename = sys.argv[5]
    if len(sys.argv) > 6:
        if is_int(sys.argv[5]):
            query['play_id'] = int(sys.argv[5])
        else:
            assert len(sys.argv) == 7
            query['game_name'] = sys.argv[5]
            theory_seq_filename = sys.argv[6]
    if len(sys.argv) > 7:
        query['game_name'] = sys.argv[6]
        theory_seq_filename = sys.argv[7]

    plays = db.plays.find(query).sort('start_time')

    print 'Running fmri_empaTheoryReplay with query:'
    print query
    print 'theory_seq_filename', theory_seq_filename

    # TODO dedupe with fmri_empaPlay

    all_pairs = {}
    all_plans = {}
    all_movie_names = {}

    # get theory sequence as filename (for all plays for subject)
    import h5py
    with h5py.File(theory_seq_filename, 'r') as f: # make sure to save with -v7.3, otherwise doesn't work...
        # passed from HRR.py, gen_and_save_subject_unique_HRRs
        maskfile = u''.join(unichr(c) for c in f['maskfile'])
        unique_theories_filename = u''.join(unichr(c) for c in f['unique_theories_filename'])

        theory_id_seq = []
        #for i in range(len(f['theory_id_seq_best'])):
        #    theory_id_seq.append(f['theory_id_seq_best'][i][0])
        for i in range(len(f['theory_id_seq_orig'])):
            theory_id_seq.append(f['theory_id_seq_orig'][i][0])

        gameStrings = f['gameStrings']

        '''
        play_key_seq = []
        for i in range(len(f['play_key_seq'][0])):
            print i
            play_key_seq.append(ObjectId(u''.join(unichr(c) for c in f[f['play_key_seq'][0][i]])))
        '''
        # TODO !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1
        #actually load 
        #fuck NCF
        with open('fuck_ncf.pickle', 'r') as ff:
            play_key_seq = cloudpickle.load(ff)

        with open(unique_theories_filename, 'r') as ff:
            theories = cloudpickle.load(ff)


    for play in plays:
        subj = db.subjects.find_one({'subj_id': subj_id})
        game = subj['games'][play['game_id']]
        game_str = game['descs'][play['desc_id']]
        level_str = game['levels'][play['level_id']]
        assert game_str == play['game_str']
        assert level_str == play['level_str']
        assert game['name'] == play['game_name']

        print 'EMPA playing subj %s, run %d, block %d, instance %d, play %d: %s (%s), desc %d, level %d' % (play['subj_id'], play['run_id'], play['block_id'], play['instance_id'], play['play_id'], game['name'], game['fake_name'], play['desc_id'], play['level_id'])

        # ensure plans weren't already generated
        q = {'play_key': play['_id'], 'theory_seq_filename': theory_seq_filename}
        count = db.plans.count(q)
        print q, count
        # this is so that we can resume from the last savedCurriculum e.g. after a crash
        #if count > 0:
        #    print '........................................... found plans; skipping................................'
        #    continue

        # get regressors, for sanity checks 
        regs = db.regressors.find({'play_key': play['_id']}).sort('ts', -1)
        reg = None
        for reg in regs:
            break # just take the latest one

        # get theory sequence for given play
        theory = []
        assert len(play_key_seq) == len(theory_id_seq)
        for i in range(len(theory_id_seq)):
            if play_key_seq[i] == play['_id']:
                theory.append(theories[theory_id_seq[i]])

        assert len(theory) == len(reg['regressors']['theory_change_flag'])

        # get states
        zstates = play['zstates']
        states = core.VGDLParser.decompress(zstates)
        states = states['states'] # dummy dict
        
        zkeystates = play['zkeystates']
        keystates = core.VGDLParser.decompress(zkeystates)
        keystates = keystates['keystates'] # dummy dict
        
        if game['name'] not in all_pairs:
            all_pairs[game['name']] = [] 
            all_plans[game['name']] = [] 
            all_movie_names[game['name']] = [] 

        video_name = 's={}_r={}_b={}_i={}_p={}_{}'.format(play['subj_id'], play['run_id'], play['block_id'], play['instance_id'], play['play_id'], game['name'])
        print 'video_name = ', video_name

        # this is the money that gets passed to playCurriculum
        reset_finalTimeStepList = play['instance_id'] == 0 and play['play_id'] == 0 # reset finalTimeStepList before every block -- balance between psychological plausibility and practicality (i.e. avoiding OOM in plaqueAttack)
        level_game = (play['game_str'], play['level_str'], states, keystates, video_name, reset_finalTimeStepList, theory, play['level_id'] + 1)
        all_pairs[game['name']].append(level_game) # TODO momchil OOM? 

        # pre-populate plans object for each play with identifier info
        # extract the plans later in Agent
        plan = {
            'play_key': play['_id'],
            'theory_seq_filename': theory_seq_filename,
            'theory_id_seq': theory_id_seq,
            'play_key_seq': play_key_seq,
            'subj_id': play['subj_id'],
            'run_id': play['run_id'],
            'block_id': play['block_id'],
            'instance_id': play['instance_id'],
            'play_id': play['play_id'],
            'game_name': play['game_name'],
            'level_id': play['level_id'],
            'type': 'fmri_empaReplay',
            'plan_ts': time.time(), # for sanity checks
            'plan_dts': datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), # for sanity checks
            'maskfile': maskfile,
        }
        all_plans[game['name']].append(plan)

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

        plans = all_plans[game_name] 
        assert len(plans) == len(level_game_pairs)

        movie_names = all_movie_names[game_name]
        assert len(movie_names) == len(level_game_pairs)

        # defaults from load_games.py 
        # python -m vgdl.load_games --game_name tiny_zelda
        task_ID = 'subj={}'.format(subj_id)
        agent = Agent('full', game_name, hyperparameter_sets=hyperparameter_sets, hyperparameter_index='short-term', metacontroller_index=0, IW_k=1, extra_atom_allowed=True, task_ID=task_ID)
        agent.record_fMRIRegressors = True
        agent.theory_playback = True

        environment = Environment(game_name, agent, task_ID=task_ID, produce_printout=False)
        curriculumRegressors = environment.playCurriculum(level_game_pairs=level_game_pairs, make_movie=False, heatmap=False, playback=True, movie_names=movie_names, theory_playback=True)
        assert len(curriculumRegressors) == len(plans)

        for i in range(len(curriculumRegressors)): # for each play
            plan = plans[i]

            # prepare plans for insert into Mongo
            # only take stuff relevant for planning
            plan['plans'] = curriculumRegressors[i]['plans']
            plan['avatar_collisions'] = curriculumRegressors[i]['avatar_collisions']
            plan['dt'] = datetime.now()
            plan['ts'] = time.time()

            # serialize plans
            tmp = os.path.split(theory_seq_filename)[-1]
            filename = os.path.join(theoriesDir, 'plans_' + str(plan['play_key']) + '_'+ tmp + '_' + str(plan['ts'])) + '.pickle'
            with open(filename, 'wb') as f:
                cloudpickle.dump(plan['plans'], f)
            plan['plans_filename'] = filename
            plan['plans'] = [] # remove from plans object

            # insert plans into mongo
            db.plans.insert_one(plan)

    if didSomething:
        print 'Completed!'
    else:
        print 'Nothing to do...'

    end = time.time()
    print 'time end: ', datetime.now()
    print 'time elapsed: ', (end - start), ' s'
