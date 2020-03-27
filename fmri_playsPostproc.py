# post-processing of data to extract quantities for convenient analysis

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
from vgdl.core import keyPresses as keyNames
from IPython import embed
from vgdl.main_agent import Agent
import cPickle, cloudpickle

import pygame

# USAGE: python fmri_playsPostproc.py.py [subj_id] [run_id*] [block_id*] [instance_id*] [play_id*]
#        python fmri_playsPostproc.py.py [subj_id] [game_name]
#        python fmri_playsPostproc.py.py [subj_id] [run_id] [game_name]
# * - optional
# copied from fmri_makeMovie.py

if 'omchil' in socket.gethostname() or 'ncfood' in socket.gethostname() or 'ncflogin' in socket.gethostname():
    # local on my Mac, or on a login / VDI node
    client = MongoClient('localhost', 27017)
else:
    # cluster
    client = MongoClient('holy7c22306.rc.fas.harvard.edu', 27017)


db = client['heroku_7lzprs54']

fMRI_screensize = (800,580) # TODO dedupe momchil

def print_keystates(keystates):
    ts0 = keystates[1]['ts']
    for t in range(len(keystates)):
        if t == 0:
            continue
        keystate = keystates[t]['keystate']
        kk = []
        for key in range(len(keystate)):
            if keystate[key]:
                kk.append(key)
        print str(t) + ' -- ' + str(keystates[t]['ts'] - ts0) + ': ' + str(kk)



def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    assert False


def playsPostproc(subj_id):
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

    print 'Running fmri_playsPostproc.py with query:'
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

        print 'Computing plays_post for subj %s, run %d, block %d, instance %d, play %d: %s (%s), desc %d, level %d' % (play['subj_id'], play['run_id'], play['block_id'], play['instance_id'], play['play_id'], game['name'], game['fake_name'], play['desc_id'], play['level_id'])

        q = {'play_key': play['_id']}
        print q
        print db.plays_post.count(q)
        #assert db.plays_post.count(q) == 0, 'Too many regressors!'
        if db.plays_post.count(q) > 0:
            print '..........skipping: already computed'
            assert db.plays_post.count(q) == 1, 'Too many regressors!'
            continue

        # get states
        zstates = play['zstates']
        states = core.VGDLParser.decompress(zstates)
        states = states['states'] # dummy dict

        zkeystates = play['zkeystates']
        keystates = core.VGDLParser.decompress(zkeystates)
        keystates = keystates['keystates'] # dummy dict

        # create object to hold play postprocessing data
        # similar to regressors (see fmri_empaReplay.py)
        play_post = {
            'play_key': play['_id'],
            'subj_id': play['subj_id'],
            'run_id': play['run_id'],
            'block_id': play['block_id'],
            'instance_id': play['instance_id'],
            'play_id': play['play_id'],
            'game_name': play['game_name'],
            'level_id': play['level_id'],
            'type': 'fmri_playsPostproc'
        }

        # extract keypresses similar to keyholds, etc already recorded in plays (see startGame() in core.py)
        # also extract duplicates of keyholds, etc based on key presses
        # the purpose is to:
        # 1) sanity check key presses against keydowns, etc. recorded during game play (they're different pygame events)
        # 2) generate keyholds boxcars for subj #1 when we still didn't have proper keyhold logging

        keypresses = {}
        keyups = {}
        keydowns = {}
        keyholds = {} # boxcars starting at keydown and ending at keyup
        for _, k in keyNames.iteritems():
            keypresses[k] = []
            keyups[k] = []
            keydowns[k] = []
            keyholds[k] = []

        # compute keypresses first
        # b/c of fMRI continuoun pressing shenanighans, those are the ones that actally resulted in movement, so confounded with visual
        # highly advised not to use
        #
        for t in range(len(keystates)): # for each state / pygame frame
            if keystates[t] is None:
                assert t == 0  # first one is blank
                continue

            keystate = keystates[t]['keystate']
            for key in range(len(keystate)): # for each key (potentially pressed) TODO only iterate over relevant keys
                if key not in keyNames.keys():
                    continue
                k = keyNames[key] # assumes fMRI_remap was used; see startGame() in core.py

                # update keypresses
                if keystate[key]:
                    keypresses[k].append(keystates[t]['ts'])


        #print '---------- BEFORE:'
        #print_keystates(keystates)

    
        # now, extend every key press into the next 0.15 s frames...
        # b/c fMRI continuous key press chicanery in startGame(), we end up with gaps in the logged keys
        # i.e. there are lots of frames when a key was being held but nothing was logged, so we can't reconstruct keyholds properly...
        # only an issue for subject 1 really
        for t in reversed(range(len(keystates))): # for each state / pygame frame
            if keystates[t] is None:
                assert t == 0  # first one is blank
                continue

            keystate = keystates[t]['keystate']
            for key in range(len(keystate)): # for each key (potentially pressed) TODO only iterate over relevant keys
                if key not in keyNames.keys():
                    continue

                if not keystate[key]:
                    tp = t - 1
                    while tp > 0 and keystates[t]['ts'] - keystates[tp]['ts'] <= 0.15:
                        if keystates[tp]['keystate'][key]:
                            keystates[t]['keystate'][key] = True
                            break
                        tp -= 1


        #print '\n\n\n\n ----------- AFTER:'
        #print_keystates(keystates)


        # compute keyholds based on the repeated keypresses
        # makes it more accurate (see GLM 1)
        # all of this is b/c we screwed up subj #1 ...
        #
        for t in range(len(keystates)): # for each state / pygame frame
            if keystates[t] is None:
                assert t == 0  # first one is blank
                continue

            keystate = keystates[t]['keystate']
            last_keystate = keystates[t - 1]['keystate'] if t - 1 > 0 else None 

            for key in range(len(keystate)): # for each key (potentially pressed) TODO only iterate over relevant keys
                if key not in keyNames.keys():
                    continue
                k = keyNames[key] # assumes fMRI_remap was used; see startGame() in core.py

                # update keypresses
                if keystate[key]:
                    keypresses[k].append(keystates[t]['ts'])

                if keystate[key] and (last_keystate is None or not last_keystate[key]):
                    # key just got pressed
                    # timestamp between frames, unless it's the first frame
                    ts = keystates[t]['ts'] if t - 1 == 0 else (keystates[t]['ts'] + keystates[t - 1]['ts']) / 2.0
                    keydowns[k].append(ts)

                if not keystate[key] and last_keystate is not None and last_keystate[key]:
                    # key was pressed but is now released
                    offset = (keystates[t]['ts'] + keystates[t - 1]['ts']) / 2.0
                    keyups[k].append(offset)
                    onset = keydowns[k][-1]
                    keyholds[k].append((onset, offset - onset))


        # from logLastKeyup() in startGame()
        for k in keydowns.keys():
            if len(keyups[k]) < len(keydowns[k]):
                if len(keyups[k]) + 1 != len(keydowns[k]):
                    print 'inconsistent keyups vs. keydowns'
                    embed()
                    assert False
                offset = keystates[-1]['ts'] + 1e-6 # so we don't accidentally get negative keyhold durations 
                keyups[k].append(offset)
                onset = keydowns[k][-1]
                keyholds[k].append((onset, offset - onset))

        play_post['keypresses'] = keypresses
        play_post['keyholds'] = keyholds
        play_post['keyups'] = keyups
        play_post['keydowns'] = keydowns

        db.plays_post.insert_one(play_post)




if __name__ == '__main__':
    subj_id = sys.argv[1]

    playsPostproc(subj_id)
    #for s in range(4,9):
    #    playsPostproc(str(s))
