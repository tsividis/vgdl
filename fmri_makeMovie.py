# create movie after fmri_empaReplay has been run, to show regressors & theory plotted on top of actual game play

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
from vgdl.core import fMRI_screensize
from IPython import embed
from vgdl.main_agent import Agent
import cPickle, cloudpickle
import os
import argparse
import glob
import vgdl.core
import utils

import pygame

# USAGE: python fmri_makeMovie.py [subj_id] [run_id*] [block_id*] [instance_id*] [play_id*]
#        python fmri_makeMovie.py [subj_id] [game_name]
#        python fmri_makeMovie.py [subj_id] [run_id] [game_name]
# * - optional
# copied from fmri_empaReplay.py


client = utils.get_mongo_client()

if 'omchil' in socket.gethostname() or 'ncfood' in socket.gethostname() or 'ncflogin' in socket.gethostname():
    # local on my Mac, or on a login / VDI node
    videosDir = 'videos'
    imagesDir = 'images'
else:
    # cluster
    videosDir = os.path.join(os.environ.get('MY_LAB'), 'VGDL', 'videos')
    imagesDir = os.path.join(os.environ.get('MY_LAB'), 'VGDL', 'images')

print('fmri_makeMovie dirs: ', videosDir, imagesDir)

db = client['heroku_7lzprs54']

def get_video_name(play, use_renders):
    video_name = 'fmri_makeMovie_s={}_r={}_b={}_i={}_p={}_{}{}'.format(
        play['subj_id'], play['run_id'], play['block_id'], play['instance_id'], play['play_id'], game['name'],
        '_render' if use_renders else '')
    return video_name

def get_subj_game_videos_dir(videosDir, subj_id, play):
    return os.path.join(videosDir, 'makeMovie', 'subj_'+str(subj_id), play['game_name'])
    
def get_subj_game_images_dir(imagesDir, subj_id, play, video_name):
    return os.path.join(imagesDir, 'makeMovie', 'subj_'+str(subj_id), play['game_name'], video_name)

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    assert False

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--subj-id', required=True)
    parser.add_argument('--run-id', default=None)
    parser.add_argument('--block-id', default=None)
    parser.add_argument('--instance-id', default=None)
    parser.add_argument('--play-id', default=None)
    parser.add_argument('--game-name', default=None)
    parser.add_argument('--make-images', default=True, help='Whether to generate images')
    parser.add_argument('--make-movie', default=True, help='Whether to generate a movie')
    parser.add_argument('--show-symbols', default=False, help='Whether to display the sprite symbols inside the boxes like the subjects saw them')
    parser.add_argument('--use-renders', default=True, help='Whether to render each screen as a 80x60 image, for e.g. DQN or PCA')
    parser.add_argument('--default-colors', default=True, help='Whether to use the default colors for each game (e.g. for EMPA, DQN, PCA), or the ones that the subject saw')
    parser.add_argument('--headless', default=False, help='Whether to actually display the screen (otherwise, weird things happen)')

    config = parser.parse_args()
    print(config)

    subj_id = config.subj_id
    show_symbols = config.show_symbols
    use_renders = config.use_renders
    default_colors = config.default_colors
    make_images = config.make_images
    make_movie = config.make_movie
    headless = config.headless

    # construct query
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

    # get plays
    plays = db.plays.find(query, {'_id': 1}).sort('start_time')
    pks = []
    for play in plays:
        pks.append(play['_id'])
    del plays # close cursor, o/w screws things up

    print('Running fmri_makeMovie with query:')
    print(query)

    # TODO dedupe with fmri_empaReplay

    all_pairs = {}
    all_regressors = {}
    all_movie_names = {}

    # Hack: we need to change the block size for the earlier subject, since the block sizes were smaller and the sprite coordinates were correspondingly different
    if int(subj_id) <= 11:
        vgdl.core.BLOCK_SIZE = 20
    
    for pk in pks:
        # find play
        query = {'_id': pk}
        play = db.plays.find_one(query)
        assert play['subj_id'] == subj_id

        subj = db.subjects.find_one({'subj_id': subj_id})
        game = subj['games'][play['game_id']]
        game_str = game['descs'][play['desc_id']]
        level_str = game['levels'][play['level_id']]
        assert game_str == play['game_str']
        assert level_str == play['level_str']
        assert game['name'] == play['game_name']

        print('Making video for subj %s, run %d, block %d, instance %d, play %d: %s (%s), desc %d, level %d' % (play['subj_id'], play['run_id'], play['block_id'], play['instance_id'], play['play_id'], game['name'], game['fake_name'], play['desc_id'], play['level_id']))

        # get regressors
        q = {'play_key': play['_id']}
        print(q)
        print(db.empa_regressors.count(q))
        #assert db.empa_regressors.count(q) == 1, 'Too many regressors!' 
        regs = db.empa_regressors.find(q).sort('ts', -1)
        reg = None
        for reg in regs:
            break # just take the latest one

        video_name = get_video_name(play, use_renders) 
        print('video_name = ', video_name)

        ls = glob.glob(os.path.join('videos', video_name + '*')) # TODO coupling with startPlaybackGame() video saving logic
        if len(ls) > 0:
            print( '....found video files with prefix; skipping this one')
            print(ls)
            continue

        # load theories from disk
        with open(reg['regressors']['theory_filename'], 'r') as f:
            reg['regressors']['theory'] = cloudpickle.load(f)

        # hack to fix interaction_change_flag TODO undo once we re-run it
        #for i in range(1, len(reg['regressors']['interaction_change_flag'])):
        #    prev_theory = reg['regressors']['theory'][i-1][0]
        #    curr_theory = reg['regressors']['theory'][i][0]
        #    interactionSetEqual = all(any(i1==i2 for i2 in prev_theory.interactionSet) for i1 in curr_theory.interactionSet)

        #    #if reg['regressors']['interaction_change_flag'][i][0]:
        #        #print 'w000000t interaction_change_flag!'
        #        #embed()
        #    reg['regressors']['interaction_change_flag'][i][0] = not interactionSetEqual
        '''
        reg['regressors'] = None # -- uncomment this and comment the lines above to run locally
        '''

        # get states
        zstates = play['zstates']
        states = core.VGDLParser.decompress(zstates)
        states = states['states'] # dummy dict

        zkeystates = play['zkeystates']
        keystates = core.VGDLParser.decompress(zkeystates)
        keystates = keystates['keystates'] # dummy dict

        # optionally remove symbols
        # see setFullState()
        if not show_symbols:
            for fs in states:
                for key, ss in fs['objects'].iteritems():
                    for ID, attrs in ss.iteritems():
                        attrs['symbol'] = None

        # output directories
        subj_game_videos_dir = get_subj_game_videos_dir(videosDir, subj_id, play)
        subj_game_images_dir = get_subj_game_images_dir(imagesDir, subj_id, play, video_name)
        if not os.path.exists(subj_game_videos_dir):
            os.makedirs(subj_game_videos_dir)
        if not os.path.exists(subj_game_images_dir):
            os.makedirs(subj_game_images_dir)

        # in lieu of makeMovie() from main_agent.py
        # use default colors (not the ones the subject saw) b/c that's what EMPA sees
        core.VGDLParser.playGame(play['game_str'], play['level_str'], states, \
            headless=headless, persist_movie=make_movie, make_images=True, make_movie=None, movie_dir=subj_game_videos_dir, images_dir=subj_game_images_dir,
            padding=0, regressors=reg['regressors'], screensize=fMRI_screensize, video_name=video_name, default_colors=default_colors, 
            use_renders=use_renders) # make_movie doesn't do anything right now

    print('done!')
