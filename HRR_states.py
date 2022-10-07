# from https://github.com/yl3508/heroku_vgdl/tree/master/HRR_Analysis

# embed EMPA theory sequences from human replay into holographic reduced representations (HRRs), (fmri_agentReplay.py)
# generate kernels for Gaussian process regression
# optionally also generate representational dissimilarity matrices for RSA
# optionally also generate the unique theory sequences and also the corresponding holographic reduced representations, for fiddling around in Matlab 

import numpy as np
import math
import os 
import csv
import scipy.stats
import scipy.io
import sklearn.metrics.pairwise as k
from IPython import embed
import time
from pprint import pprint
import logging, sys
import cPickle, cloudpickle
import utils

import socket
from pymongo import MongoClient
from collections import defaultdict
from vgdl import core
import argparse
from vgdl.core import VGDLParser, fMRI_screensize
from vgdl.core import keyPresses as keyNames
from IPython import embed
from vgdl.EMPA import Agent
import cPickle, cloudpickle
from vgdl.environment import Environment
from vgdl.hyperparameters import hyperparameter_sets
from vgdl.theory_template import TimeStep, Theory, Game, writeTheoryToTxt, generateSymbolDict
#from fmri_agentReplay import theoriesDir

import pygame

from HRR import *  # TODO

# get squence of HRRs for subject's inferred theories
#
def gen_subject_HRRs__state(subj_id, K=10, N=10, E=0.05, nsamples=100, normalize=False):
    subj_id = str(subj_id)

    db = client['heroku_7lzprs54']

    subj = db.subjects.find_one({'subj_id': subj_id})

    # get plays
    query = {'subj_id': subj_id, 'run_id': {'$gt': 0, '$lt': 7}}
    plays = db.plays.find(query, {'_id': 1}).sort('start_time')
    pks = []
    for play in plays:
        pks.append(play['_id'])
    del plays # close cursor, o/w screws things up

    # "subject" embeddings: have multiple (nsamples), for robustness
    samples = [SubjectHRR(K, N, E) for _ in range(nsamples)]
   
    state_HRRs = [[] for _ in range(nsamples)] 
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
        projection = {'subj_id': 1, 'run_id': 1, 'block_id': 1, 'instance_id': 1, 'play_id': 1, 'game_id': 1, '_id': 1, 
                'desc_id': 1, 'level_id': 1, 'game_str': 1, 'level_str': 1, 'run_start_ts': 1, 'zstates': 1}
        play = db.plays.find_one(query, projection)
        assert play['subj_id'] == subj_id

        game = subj['games'][play['game_id']]
        print 'gen_subject_HRRs: subj %s, run %d, block %d, instance %d, play %d: %s (%s), desc %d, level %d' % (play['subj_id'], play['run_id'], play['block_id'], play['instance_id'], play['play_id'], game['name'], game['fake_name'], play['desc_id'], play['level_id'])


        if last_block_id != play['block_id']:
            if last_block_id is not None:
                block_offs_idx.append(len(ts))
            block_ons_idx.append(len(ts))
            last_block_id = play['block_id']

        # get states
        zstates = play['zstates']
        states = core.VGDLParser.decompress(zstates)
        states = states['states'] # dummy dict

        print 'loading play time: ', (time.time() - then)

        then = time.time()

        for i in range(0, len(states)):
            state = states[i]

            if len(state['effectListByColor']) == 0:
                continue

            for j in range(nsamples):
                state_HRR = samples[j].embedState(state, normalize)
                state_HRRs[j].append(state_HRR)

            frame.append(i)
            ts.append(state['ts'] - play['run_start_ts'])
            play_key.append(str(play['_id']))
            run_id.append(play['run_id'])

        print 'HRR time: ', (time.time() - then)

        #break # TODO !!!!!!!! rm


    block_offs_idx.append(len(ts))

    print 'total time: ', (time.time() - then0)

    return state_HRRs, ts, run_id, play_key, frame, block_ons_idx, block_offs_idx

def gen_and_save_subject_kernels_batched__states(subj_id, K=10, N=10, E=0.05, nsamples=1, batch_size=1, normalize=True):

    # copy of gen_and_save_subject_kernels_batched  but for state features

    # generate HRRs and kernels in batches, b/c of OOM (HRRs are too big)
    # batches is better than 1 by 1 b/c of overhead of querying mongo
    #
    sigma_w = 1; # This is effectively a constant scaling factor of the kernel K, which gets canceled out in the posterior mean equation and gets absorbed in the noise variance (see equation 2.23 in Rasmussen's GP book)

    kernel_filename = os.path.join(matDir, 'HRR_states_subject_kernel_subj=%s_K=%d_N=%d_E=%.3f_nsamples=%d_sigma_w=%.3f_norm=%d.mat' % (subj_id, K, N, E, nsamples, sigma_w, normalize))
    print 'filename', kernel_filename

    assert nsamples % batch_size == 0

    all_state_kernels = []

    for batch in range(nsamples / batch_size):
        print 'BATCH ', batch

        state_HRRs, ts, run_id, play_key, frame, block_ons_idx, block_offs_idx = gen_subject_HRRs__state(subj_id, K, N, E, batch_size, normalize)

        state_kernels, r_id, state_Xx, state_sf = gen_subject_kernels(subj_id, state_HRRs, ts, run_id, block_ons_idx, block_offs_idx, sigma_w)

        all_state_kernels.append(state_kernels)

    state_kernels = np.concatenate(all_state_kernels, axis=0)

    state_kernel = np.mean(state_kernels, axis=0)

    state_kernel_std = np.std(state_kernels, axis=0)

    # save kernels
    #
    d = {
        'state_kernel': state_kernel,
        'state_kernel_std': state_kernel_std,
        #'state_kernels': state_kernels, # -- too much memory
        'state_Xx': state_Xx,
        #'state_sf': state_sf, # -- too much memory
        'r_id': r_id,
        'ts': ts,
        'block_ons_idx': block_ons_idx,
        'block_offs_idx': block_offs_idx,
        'K': K,
        'N': N,
        'E': E,
        'normalize': normalize,
        'sigma_w': sigma_w,
        'nsamples': nsamples,
        'subj_id': subj_id,
    }

    scipy.io.savemat(kernel_filename, d)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--subj-id', required=True)
    parser.add_argument('--K', default=10, help='the maximum number of terms to be combined')
    parser.add_argument('--N', default=10, help='the number of atomic values in the language')
    parser.add_argument('--E', default=0.05, help='the probability of error')
    parser.add_argument('--nsamples', default=100, help='number of HRR samples; must be a multiple of batch_size')
    parser.add_argument('--batch-size', default=10, help='batch size')
    parser.add_argument('--normalize', default=1, help='whether/how to normalize the HRRs (0 = no, 2 = Z score, 1 = unit vector')
    parser.add_argument('--type', default='kernel')
    parser.add_argument('--dist', default='correlation')
    parser.add_argument('--glmodel', default=24)
    parser.add_argument('--agg', default='avg')

    config = parser.parse_args()
    print(config)

    subj_id = int(config.subj_id)
    K = int(config.K)
    N = int(config.N)
    E = float(config.E)
    nsamples = int(config.nsamples)
    batch_size = int(config.batch_size)
    normalize = int(config.normalize)
    dist = config.dist
    glmodel = int(config.glmodel)
    agg = config.agg

    if config.type == 'kernel':
        gen_and_save_subject_kernels_batched__states(subj_id, K, N, E, nsamples, batch_size, normalize)
    #gen_and_save_subject_kernels_batched_multisigma(subj_id)

    print 'Done'
