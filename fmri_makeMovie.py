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
from IPython import embed
from vgdl.main_agent import Agent
import cPickle, cloudpickle

import pygame

# USAGE: python fmri_makeMovie.py [subj_id] [run_id*] [block_id*] [instance_id*] [play_id*]
#        python fmri_makeMovie.py [subj_id] [game_name]
#        python fmri_makeMovie.py [subj_id] [run_id] [game_name]
# * - optional
# copied from fmri_empaReplay.py

if 'omchil' in socket.gethostname():
    # local 
    client = MongoClient('localhost', 27017)
else:
    # cluster
    client = MongoClient('holy7c22306.rc.fas.harvard.edu', 27017)


db = client['heroku_7lzprs54']

fMRI_screensize = (800,580) # TODO dedupe momchil

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

    print 'Running fmri_makeMovie with query:'
    print query

    # TODO dedupe with fmri_empaReplay

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

        print 'Making video for subj %s, run %d, block %d, instance %d, play %d: %s (%s), desc %d, level %d' % (play['subj_id'], play['run_id'], play['block_id'], play['instance_id'], play['play_id'], game['name'], game['fake_name'], play['desc_id'], play['level_id'])

        # get regressors
        q = {'play_key': play['_id']}
        print q
        print db.regressors.count(q)
        assert db.regressors.count(q) == 1, 'Too many regressors!'
        reg = db.regressors.find_one(q)

        # load theories from disk
        with open(reg['regressors']['theory_filename'], 'r') as f:
            reg['regressors']['theory'] = cloudpickle.load(f)

        # get states
        zstates = play['zstates']
        states = core.VGDLParser.decompress(zstates)
        states = states['states'] # dummy dict

        zkeystates = play['zkeystates']
        keystates = core.VGDLParser.decompress(zkeystates)
        keystates = keystates['keystates'] # dummy dict

        video_name = 'real_s={}_r={}_b={}_i={}_p={}_{}'.format(play['subj_id'], play['run_id'], play['block_id'], play['instance_id'], play['play_id'], game['name'])
        print 'video_name = ', video_name

        # in lieu of makeMovie() from main_agent.py
        # use default colors (not the ones the subject saw) b/c that's what EMPA sees
        core.VGDLParser.playGame(play['game_str'], play['level_str'], states, \
            headless=False, persist_movie=True, make_images=True, make_movie=True, movie_dir="videos/"+game['name'], padding=10, regressors=reg['regressors'], screensize=fMRI_screensize, video_name=video_name, default_colors=True)


