# from https://github.com/yl3508/heroku_vgdl/tree/master/HRR_Analysis

# generate kernels for Gaussian process regression from DQN layers from human replay (fmri_agentReplay.py)
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
from HRR import gen_subject_kernels, gen_subject_kernels_multisigma
import utils
import socket
from pymongo import MongoClient
from fmri_agentReplay import layersDir

# ### Helper functions


logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

#logging.disable(logging.CRITICAL)
logging.disable(logging.ERROR)

client = utils.get_mongo_client()

if 'omchil' in socket.gethostname():
    # local 
    matDir = 'mat'
else:
    # Cannon 
    matDir = os.path.join(os.environ.get('MY_LAB'), 'VGDL', 'mat')
    print layersDir, matDir
    # NCF cluster
    #client = MongoClient('holy2a05207.rc.fas.harvard.edu', 27017)


db = client['heroku_7lzprs54']

# get squence of DQN layer activations for a given subject
# copied and adapted from gen_subject_HRRs
#
def gen_subject_DQN_layers(subj_id, normalize=False):
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

    # regressor name (as defined in dqn_agent.py; see LAYER_TO_LAYER_NAME and save_hidden_layer_output) -> sequence of layer activations
    # notice that here we only have a single "sample", unlike in HRRs
    layers = {
        'layer_conv1_output': [],
        'layer_conv2_output': [],
        'layer_conv3_output': [],
        'layer_linear1_output': [],
        'layer_linear2_output': [],
    }
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
        print 'gen_subject_DQN_layers: subj %s, run %d, block %d, instance %d, play %d: %s (%s), desc %d, level %d' % (play['subj_id'], play['run_id'], play['block_id'], play['instance_id'], play['play_id'], game['name'], game['fake_name'], play['desc_id'], play['level_id'])

        # get regressors
        q = {'play_key': play['_id']}
        print q
        print db.dqn_regressors.count(q)
        assert db.dqn_regressors.count(q) <= 1, 'Too many regressors!' 
        if db.dqn_regressors.count(q) == 0:
            print 'skipping (e.g. Sokoban)'
            continue
        regs = db.dqn_regressors.find(q).sort('ts', -1)
        reg = None
        for reg in regs:
            break # just take the latest one

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

        # loop over layers
        num_frames = None
        for regressor_name in layers.keys():

            then = time.time()

            # load layers from disk
            assert regressor_name in reg['regressors']
            with open(reg['regressors'][regressor_name + '_filename'], 'r') as f:
                reg['regressors'][regressor_name] = cloudpickle.load(f)

            # sanity check that all layers have the same number of frames
            if num_frames is None:
                num_frames = len(reg['regressors'][regressor_name])
            else:
                assert num_frames == len(reg['regressors'][regressor_name])

            # insert layer for each time step
            for i in range(0, len(reg['regressors'][regressor_name])):
                layer = reg['regressors'][regressor_name][i][0].flatten()

                if normalize:
                    layer = layer / np.sqrt(np.sum(np.square(layer)))

                layers[regressor_name].append(layer)

                if regressor_name == layers.keys()[0]:
                    # only insert these for one layer, since this should be identical across layers
                    # we sanity check this using num_frames
                    frame.append(reg['regressors'][regressor_name][i][1])
                    ts.append(reg['regressors'][regressor_name][i][2] - play['run_start_ts'])
                    play_key.append(str(play['_id']))
                    run_id.append(play['run_id'])

            print 'layer', regressor_name, ' time: ', (time.time() - then)
        

    block_offs_idx.append(len(ts))

    print 'total time: ', (time.time() - then0)

    return layers, ts, run_id, play_key, frame, block_ons_idx, block_offs_idx




# copy of HRR.gen_and_save_subject_kernels_batched but for DQN
def gen_and_save_subject_kernels(subj_id):

    normalize = True

    sigma_w = 1; # This is effectively a constant scaling factor of the kernel K, which gets canceled out in the posterior mean equation and gets absorbed in the noise variance (see equation 2.23 in Rasmussen's GP book)

    # get sequences of DQN layer activations
    layers, ts, run_id, play_key, frame, block_ons_idx, block_offs_idx = gen_subject_DQN_layers(subj_id, normalize)

    # generate GP kernels
    layer_kernels = dict()
    layer_Xx = dict()
    layer_sf = dict()
    for regressor_name, layer_sequence in layers.iteritems():
        # note that we are reusing the HRR kernel code which expects several samples; here we create a single sample
        layer_kernels[regressor_name], r_id, layer_Xx[regressor_name], layer_sf[regressor_name] = \
            gen_subject_kernels(subj_id, [layer_sequence], ts, run_id, block_ons_idx, block_offs_idx, sigma_w)
        layer_kernels[regressor_name] = layer_kernels[regressor_name][0] # single sample

    # save kernels
    #
    kernel_filename = os.path.join(matDir, 'DQN_subject_kernel_subj=%s_sigma_w=%.3f_norm=%d.mat' % (subj_id, sigma_w, normalize))

    d = {regressor_name + '_kernel': kernel for regressor_name, kernel in layer_kernels.iteritems()}
    d.update({regressor_name + '_Xx': Xx for regressor_name, Xx in layer_Xx.iteritems()}) 
    #d.update({regressor_name + '_sf': sf for regressor_name, sf in layer_sf.iteritems()}) - there are too big
    d.update({
        'r_id': r_id,
        'ts': ts,
        'block_ons_idx': block_ons_idx,
        'block_offs_idx': block_offs_idx,
        'sigma_w': sigma_w,
        'subj_id': subj_id,
    })

    scipy.io.savemat(kernel_filename, d)


# copy of gen_and_save_subject_kernels but for multiple sigma_w's
# notice that this might not be necessary - sigma_w is a constant factor that gets absorbed in the noise variance (see equation 2.23 in the GP book)
def gen_and_save_subject_kernels_multisigma(subj_id):

    normalize = True

    sigma_ws = np.logspace(-10, 10) # grid search the parameter space

    # get sequences of DQN layer activations
    layers, ts, run_id, play_key, frame, block_ons_idx, block_offs_idx = gen_subject_DQN_layers(subj_id, normalize)

    # generate GP kernels
    layer_kernelss = dict()
    layer_Xx = dict()
    layer_sf = dict()
    for regressor_name, layer_sequence in layers.iteritems():
        # note that we are reusing the HRR kernel code which expects several samples; here we create a single sample
        layer_kernelss[regressor_name], r_id, layer_Xx[regressor_name], layer_sf[regressor_name] = \
            gen_subject_kernels_multisigma(subj_id, [layer_sequence], ts, run_id, block_ons_idx, block_offs_idx, sigma_ws)

    for i in range(len(sigma_ws)):
        sigma_w = sigma_ws[i]

        # save kernels
        #
        kernel_filename = os.path.join(matDir, 'DQN_subject_kernel_subj=%s_sigma_w=%.3e_norm=%d.mat' % (subj_id, sigma_w, normalize))

        d = {regressor_name + '_kernel': kernel for regressor_name, kernel in layer_kernelss[i][0].iteritems()}
        d.update({regressor_name + '_Xx': Xx for regressor_name, Xx in layer_Xx.iteritems()}) 
        #d.update({regressor_name + '_sf': sf for regressor_name, sf in layer_sf.iteritems()}) - there are too big
        d.update({
            'normalize': normalize,
            'r_id': r_id,
            'ts': ts,
            'block_ons_idx': block_ons_idx,
            'block_offs_idx': block_offs_idx,
            'sigma_w': sigma_w,
            'subj_id': subj_id,
        })

        scipy.io.savemat(kernel_filename, d)


if __name__ == '__main__':
    subj_id = int(sys.argv[1])

    gen_and_save_subject_kernels(subj_id)
    #gen_and_save_subject_kernels_multisigma(subj_id)

    print 'Done'