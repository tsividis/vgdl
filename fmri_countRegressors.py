# make sure there is a regressor object for each play object

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
import os
import glob

import pygame

# USAGE: python fmri_makeMovie.py [subj_id]
# * - optional
# copied from fmri_makeMovie.py

# from core.py
def dispTheory(theory):
    text = theory.display(as_string=True)
    lines = text.split('\n')
    lines = [l.strip() for l in lines if l.strip()]
    l = []
    for i in range(len(lines)):
        if 'generic: True' in lines[i]:
            continue
        if lines[i][-1] == ':':
            lines[i] = '-------- ' + lines[i]
        l.append(lines[i])
    text = '\n'.join(l)
    return text

if 'omchil' in socket.gethostname() or 'ncfood' in socket.gethostname() or 'ncflogin' in socket.gethostname():
    # local on my Mac, or on a login / VDI node
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

games = ['vgfmri3_chase', 'vgfmri3_helper', 'vgfmri3_bait', 'vgfmri3_lemmings', 'vgfmri3_plaqueAttack', 'vgfmri3_zelda']

if __name__ == '__main__':
    subj_id = sys.argv[1]

    query = {'subj_id': subj_id, 'run_id': {'$lt': 7}}

    ff = open('fmri_countRegressors.txt', 'w')

    for game in games:
        query['game_name'] = game

        ff.write('\n\n\n\n --------------------------------------- ' + game + ' ----------------------- \n\n\n\n')

        nplays = db.plays.count(query)
        #nregs = db.regressors.count(query)
        nregs = db.regressors_cannon_spriteEvery20.count(query)

        print query
        print nplays, ' vs. ', nregs
        if nplays != nregs:
            print '----------------------------------- !!!!!! MISMATCH!!!'

        plays = db.plays.find(query).sort('start_time')
        for play in plays:
            q = {'play_key': play['_id']}
            #cnt = db.regressors.count(q)
            cnt = db.regressors_cannon_spriteEvery20.count(q)
            if cnt != 1:
                print '         wrong # of regressors for ', play['run_id'], play['block_id'], play['instance_id'], play['play_id'], ' = ', cnt

            '''
            reg = db.regressors.find_one(q)

            # load theories from disk
            with open(reg['regressors']['theory_filename'], 'r') as f:
                reg['regressors']['theory'] = cloudpickle.load(f)

            s = dispTheory(reg['regressors']['theory'][0][0])
            ff.write(s)
            ff.write('\n\n ------ new play: ------- ' + str(play['_id']))
            print '\n\n ------ new play: ------- ' + str(play['_id'])
            print s
            '''
