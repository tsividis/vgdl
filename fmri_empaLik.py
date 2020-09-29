# run after fmri_empaTheoryReplay.py to actually get the plans in convenient form
# for computing the likelihood and fitting the parameters in MATLAB

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
import cPickle, cloudpickle

import pygame


if 'omchil' in socket.gethostname() or 'ncfood' in socket.gethostname() or 'ncflogin' in socket.gethostname():
    # local on my Mac, or on a login / VDI node
    client = MongoClient('localhost', 27017)
else:
    # cluster
    client = MongoClient('holy7c22306.rc.fas.harvard.edu', 27017)

db = client['heroku_7lzprs54']



if __name__ == '__main__':
    subj_id = sys.argv[1]

    # get plays
    query = {'subj_id': subj_id, 'run_id': {'$lt': 7, '$gt': 0}}

    plays = db.plays.find(query, {'_id': 1}).sort('start_time')
    pks = []
    for play in plays:
        pks.append(play['_id'])
    del plays # close cursor, o/w screws things up

    
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

        # get regressors
        '''
        q = {'play_key': play['_id']}
        print q
        print db.regressors_plans_test.count(q)
        assert db.regressors_plans_test.count(q) <= 1, 'Too many regressors!' 
        if db.regressors_plans_test.count(q) == 0:
            print 'skipping (e.g. Sokoban)'
            continue
        regs = db.regressors_plans_test.find(q).sort('ts', -1)
        reg = None
        for reg in regs:
            break # just take the latest one

        # get plans
        with open(reg['regressors']['plans_filename'], 'r') as f:
            reg['regressors']['plans'] = cloudpickle.load(f)

        plans = reg['regressors']['plans']
        avatar_collisions = regs['regressors']['avatar_collisions']

        '''

        # get plans
        q = {'play_key': play['_id']}
        print q
        print db.plans.count(q) # TODO plans
        assert db.plans.count(q) <= 1, 'Too many plans!' 
        if db.plans.count(q) == 0:
            print 'skipping (e.g. Sokoban)'
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
        #
        EMPA_interactions = [None] # we have no prediction for first interaction TODO fix
        subject_interactions = []
        for i in range(len(plans)):

            # get subject avatar collision
            #
            subj_ac = avatar_collisions[i][0] 

            if len(subj_ac) == 0:
                continue

            # get EMPA avatar collisions
            #
            if len(plans[i][0]) == 0:
                # no planning at this frame
                EMPA_ac = []

            else:

                p = sorted(plans[i][0], key = lambda x: (-x['win'], -x['intrinsic_reward']) ) # all plans at current frame, sorted from best to worst

                best_plan = p[0]
                assert not best_plan['win'] or best_plan['terminal']

                # for each future time step in the plan
                EMPA_ac = []
                for j in range(len(best_plan['effectListByClassSeq'])):
                    # iterate over effects
                    for eff in best_plan['effectListByClassSeq'][j]:
                        if 'avatar' == eff[1]:
                            EMPA_ac.append(eff[2])
                        elif 'avatar' == eff[2]:
                            EMPA_ac.append(eff[1])

                    if len(EMPA_ac) > 0:
                        # first interaction with avatar in plan already logged
                        break

            subject_interactions.append(subj_ac)
            EMPA_interactions.append(EMPA_ac)

        embed()
