# run after fmri_empaTheoryReplay.py to actually get the plans in convenient form
# for computing the likelihood and fitting the parameters in MATLAB

# EX: python fmri_empaLik.py 1

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
from collections import defaultdict
from vgdl import core
from vgdl.core import VGDLParser, fMRI_screensize
from vgdl.core import keyPresses as keyNames
from IPython import embed
from vgdl.main_agent import Agent
import scipy.stats
import scipy.io
import cPickle, cloudpickle
import os

import pygame


if 'omchil' in socket.gethostname() or 'ncfood' in socket.gethostname() or 'ncflogin' in socket.gethostname():
    # local on my Mac, or on a login / VDI node
    client = MongoClient('localhost', 27017)
    matDir = 'mat'
    pickleDir = 'pickle'
else:
    # cluster
    client = MongoClient('holy7c22107.rc.fas.harvard.edu', 27017)
    matDir = os.path.join(os.environ.get('MY_SCRATCH'), 'VGDL', 'mat')
    pickleDir = os.path.join(os.environ.get('MY_SCRATCH'), 'VGDL', 'pickle')

db = client['heroku_7lzprs54']



if __name__ == '__main__':
    subj_id = sys.argv[1]
    game_name = sys.argv[2]

    # get plays
    query = {'subj_id': subj_id, 'game_name': game_name, 'run_id': {'$lt': 7, '$gt': 0}}

    plays = db.plays.find(query, {'_id': 1}).sort('start_time')
    pks = []
    for play in plays:
        pks.append(play['_id'])
    del plays # close cursor, o/w screws things up

    
    behavior = []
    predictions = []
    
    # for each play
    for pk in pks:

        then = time.time()

        query = {'_id': pk}
        play = db.plays.find_one(query)
        assert play['subj_id'] == subj_id

        # get states
        zstates = play['zstates']
        states = core.VGDLParser.decompress(zstates)
        states = states['states'] # dummy dict

        zkeystates = play['zkeystates']
        keystates = core.VGDLParser.decompress(zkeystates)
        keystates = keystates['keystates'] # dummy dict

        #
        # open plans as saved by fmri_empaReplay.py i.e. the original theory sequence
        #

        '''
        # get regressors
        q = {'play_key': play['_id']}
        print q
        print db.regressors.count(q)
        assert db.regressors.count(q) <= 1, 'Too many regressors!' 
        if db.regressors.count(q) == 0:
            print 'skipping'
            continue
        regs = db.regressors.find(q).sort('ts', -1)
        reg = None
        for reg in regs:
            break # just take the latest one

        #if 'plans_filename' not in reg['regressors'].keys():
        #    continue

        # get plans
        with open(reg['regressors']['plans_filename'], 'r') as f:
            reg['regressors']['plans'] = cloudpickle.load(f)

        plans = reg['regressors']['plans']
        avatar_collisions = reg['regressors']['avatar_collisions']
        '''

        #
        # open plans as saved by fmri_empaTheoryReplay.py which replays custom theory sequences
        #

        # get plans
        q = {'play_key': play['_id']}
        print q
        print db.plans.count(q) # TODO plans
        assert db.plans.count(q) <= 1, 'Too many plans!' 
        if db.plans.count(q) == 0:
            print 'skipping'
            continue
        plans = db.plans.find(q).sort('ts', -1)
        plan = None
        for plan in plans:
            break # just take the latest one

        # actually load plans from disk
        with open(plan['plans_filename'], 'r') as f:
            plan['plans'] = cloudpickle.load(f)

        plans = plan['plans'] # all plans for each frame
        avatar_collisions = plan['avatar_collisions']




        assert len(plans) == len(avatar_collisions)
        assert len(plans) == len(states) - 2 # TODO we skip first and last one in EMPA.py

        # extract predicted avatar-sprite interactions, based on EMPA plans
        #     and actual avatar-sprite interactions
        # assumes subject replans next interaction immediately after current interaction
        #
        subject_interactions = [] # each avatar-sprite interaction
        EMPA_predictions = [] # predicted interaction
        last_EMPA_prediction = [] # EMPA prediction about current interaction = first nonempty prediction after (or at) last interaction


        s_all = []
        e_all = []

        for i in range(len(plans)):

            # get subject avatar collisions
            #
            subject_interaction = avatar_collisions[i][0]['by_color']

            # get EMPA avatar collisions
            #
            if len(plans[i][0]) == 0:
                # no planning at this frame
                EMPA_prediction = []

            else:

                p = sorted(plans[i][0], key = lambda x: (-x['win'], -x['intrinsic_reward']) ) # all plans at current frame, sorted from best to worst

                best_plan = p[0]
                assert not best_plan['win'] or best_plan['terminal']

                # for each future time step in the plan
                EMPA_prediction = []
                for j in range(len(best_plan['effectListByColorSeq'])):
                    # iterate over effects
                    for eff in best_plan['effectListByColorSeq'][j]:
                        if 'DARKBLUE' == eff[1]:
                            EMPA_prediction.append(eff[2])
                        elif 'DARKBLUE' == eff[2]:
                            EMPA_prediction.append(eff[1])

                    if len(EMPA_prediction) > 0:
                        # first interaction with avatar in plan already logged
                        break

            s_all.append(subject_interaction)
            e_all.append(EMPA_prediction)
            
            if len(subject_interaction) > 0:
                subject_interactions.append(subject_interaction) # current subject avatar-object interaction(s)
                EMPA_predictions.append(last_EMPA_prediction) # first (nonempty) prediction after last interaction
                last_EMPA_prediction = []

            if len(EMPA_prediction) > 0 and len(last_EMPA_prediction) == 0:
                last_EMPA_prediction = EMPA_prediction


        print subject_interactions
        print EMPA_predictions

        behavior.extend(subject_interactions)
        predictions.extend(EMPA_predictions)



    pks = [str(pk) for pk in pks]
    data = {
        'behavior': behavior,
        'predictions': predictions,
        'subj_id': subj_id,
        'game_name': game_name,
        'pks': pks 
    }

    filename = os.path.join(pickleDir, 'fmri_empaLik_orig_' + subj_id + '_' + game_name + '.pickle')
    print filename
    with open(filename, 'wb') as f:
        cloudpickle.dump(data, f)


    filename = os.path.join(matDir, 'fmri_empaLik_orig_' + subj_id + '_' + game_name + '.mat')
    print filename
    scipy.io.savemat(filename, data)
