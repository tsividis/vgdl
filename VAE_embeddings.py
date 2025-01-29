# from https://github.com/yl3508/heroku_vgdl/tree/master/HRR_Analysis

# generate kernels for Gaussian process regression from VAE from human replay, generated with images_pca.py
# optionally also generate representational dissimilarity matrices for RSA
# optionally also generate the unique theory sequences and also the corresponding holographic reduced representations, for fiddling around in Matlab 

import numpy as np
import math
import os 
import csv
import cv2
import scipy.stats
import scipy.io
import sklearn.metrics.pairwise as k
from IPython import embed
import time
from pprint import pprint
import logging, sys
import argparse
import cPickle, cloudpickle
from HRR import gen_subject_kernels, gen_subject_kernels_multisigma
import utils
import socket
import images_pca
from pymongo import MongoClient
#from fmri_makeMovie import imagesDir, get_video_name, get_subj_game_images_dir
from fmri_agentReplay import imagesDir
from vgdl import core
from IPython import embed

# ### Helper functions


logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

#logging.disable(logging.CRITICAL)
logging.disable(logging.ERROR)

client = utils.get_mongo_client()

# Cedric: To make the code work in the same way as before when executed on the
# server, change the string 'harvard' below to match the server hostname
if 'harvard' not in socket.gethostname():
    # local 
    matDir = 'mat'
else:
    # Cannon 
    matDir = os.path.join(os.environ.get('MY_LAB'), 'VGDL', 'mat')
    print(matDir)
    # NCF cluster
    #client = MongoClient('holy7c22108.rc.fas.harvard.edu', 27017)


db = client['heroku_7lzprs54']

# get squence of VAE embeddings for a given subject
# copied and adapted from gen_subject_DQN_layers 
#
def gen_subject_VAE_embeddings(subj_id, normalize=False):
    subj_id = str(subj_id)

    import socket
    from pymongo import MongoClient
    from collections import defaultdict
    from vgdl import core
    from vgdl.core import keyPresses as keyNames
    from IPython import embed
    import cPickle, cloudpickle

    import pygame

    db = client['heroku_7lzprs54']

    subj = db.subjects.find_one({'subj_id': subj_id})

    # get plays
    query = {'subj_id': subj_id, 'run_id': {'$lt': 7}}
    plays = db.plays.find(query, {'_id': 1}).sort('start_time')
    pks = []
    for play in plays:
        pks.append(play['_id'])
    del plays # close cursor, o/w screws things up

    # notice that here we only have a single "sample", unlike in HRRs
    embeddings = []

    ts = []
    run_id = []
    play_key = []
    frame = []
    block_ons_idx = []
    block_offs_idx = []

    then0 = time.time()

    last_block_id = None

    for pk in pks:

        then = time.time()

        query = {'_id': pk}
        play = db.plays.find_one(query)
        assert play['subj_id'] == subj_id

        game = subj['games'][play['game_id']]
        print('gen_subject_VAE: subj %s, run %d, block %d, instance %d, play %d: %s (%s), desc %d, level %d' % (play['subj_id'], play['run_id'], play['block_id'], play['instance_id'], play['play_id'], game['name'], game['fake_name'], play['desc_id'], play['level_id']))

        # get regressors
        q = {'play_key': play['_id']}
        print q
        print db.regressors.count(q)
        assert db.regressors.count(q) <= 1, 'Too many regressors!' 
        if db.regressors.count(q) == 0:
            print 'skipping (e.g. Sokoban)'
            continue

        if last_block_id != play['block_id']:
            if last_block_id is not None:
                block_offs_idx.append(len(ts))
            block_ons_idx.append(len(ts))
            last_block_id = play['block_id']

        # get states
        zstates = play['zstates']
        states = core.VGDLParser.decompress(zstates)
        states = states['states'] # dummy dict

        print('loading play time: ', (time.time() - then))

        # get directory where the frames are
        # based on fmri_agentReplay.py DQN replay
        video_name = 'fmri_agentReplay_{}_s={}_r={}_b={}_i={}_p={}_{}'.format('DQN', play['subj_id'], 
            play['run_id'], play['block_id'], play['instance_id'], play['play_id'], game['name'])
        subj_game_images_dir = os.path.join(imagesDir, 'DQN', 'subj_'+str(subj_id), game['name'])

        then = time.time()

        # loop over layers
        for i in range(1, len(states) - 1):
            # load and preprocess image for frame
            #image_filename = core.VGDLParser.get_image_filename(i)
            #image_filename = os.path.join(subj_game_images_dir, image_filename)
            # tight coupling with dqn_agent.py saveImage
            image_filename = os.path.join(subj_game_images_dir, video_name + '_step=' + str(i) + '.png')
            image_filename = image_filename.replace('DQN', 'VAE').replace('png', 'pkl') # se images_vae_inference.py
            image_filename = image_filename.replace('/n/holystore01/LABS/gershman_lab/Users/mtomov13/', '/n/holyscratch01/LABS/gershman_lab/Users/mtomov13/')

            # load precomputed embedding buy images_vae_inference.py
            with open(image_filename, 'rb') as f:
                d = cloudpickle.load(f)
            embedding = d['embedding']

            # potentially normalize
            if normalize == 2:
                embedding = scipy.stats.zscore(embedding)
            elif normalize == 1:
                embedding = embedding / np.sqrt(np.sum(np.square(embedding)))
            elif normalize == 0:
                pass
            else:
                assert False, 'bad normalize'

            embeddings.append(embedding)

            # insert frame identifiers
            frame.append(i)
            ts.append(states[i]['ts'] - play['run_start_ts'])
            play_key.append(str(play['_id']))
            run_id.append(play['run_id'])

        print('pca frames time: ', (time.time() - then))
        

    block_offs_idx.append(len(ts))

    print('total time: ', (time.time() - then0))

    return embeddings, ts, run_id, play_key, frame, block_ons_idx, block_offs_idx




# copy of HRR.gen_and_save_subject_kernels_batched but for DQN
def gen_and_save_subject_kernels(subj_id, normalize):

    sigma_w = 1; # This is effectively a constant scaling factor of the kernel K, which gets canceled out in the posterior mean equation and gets absorbed in the noise variance (see equation 2.23 in Rasmussen's GP book)

    # get sequences of VAE layer activations
    embeddings, ts, run_id, play_key, frame, block_ons_idx, block_offs_idx = gen_subject_VAE_embeddings(subj_id, normalize)

    # generate GP kernels
        # note that we are reusing the HRR kernel code which expects several samples; here we create a single sample
    embedding_kernel, r_id, embedding_Xx, embedding_sf = \
        gen_subject_kernels(subj_id, [embeddings], ts, run_id, block_ons_idx, block_offs_idx, sigma_w)
    embedding_kernel= embedding_kernel[0] # single sample

    # save kernels
    #
    kernel_filename = os.path.join(matDir, 'VAE_e1k_subject_kernel_subj=%s_sigma_w=%.3f_norm=%d.mat' % (subj_id, sigma_w, normalize))
    print('kernel_filename', kernel_filename)

    d = {
        'embeddings': embeddings,
        'embedding_kernel': embedding_kernel,
        'embedding_Xx': embedding_Xx,
       # 'embedding_sf': embedding_sf,  # -- too much memory
        'r_id': r_id,
        'ts': ts,
        'block_ons_idx': block_ons_idx,
        'block_offs_idx': block_offs_idx,
        'normalize': normalize,
        'sigma_w': sigma_w,
        'subj_id': subj_id,
    }

    scipy.io.savemat(kernel_filename, d)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--subj-id', required=True)
    parser.add_argument('--normalize', default=1, help='whether/how to normalize the HRRs (0 = no, 2 = Z score, 1 = unit vector')

    config = parser.parse_args()
    print(config)

    subj_id = int(config.subj_id)
    normalize = int(config.normalize)

    gen_and_save_subject_kernels(subj_id, normalize)

    print('Done')
