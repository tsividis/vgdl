# from https://github.com/yl3508/heroku_vgdl/tree/master/HRR_Analysis

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

# ### Helper functions

# In[5]:

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

#logging.disable(logging.CRITICAL)
logging.disable(logging.ERROR)


def dim(K, N, E):
    '''
    K: the maximum number of terms to be combined
    N: the number of atomic values in the language
    E: the probability of error
    '''
    D = round(3.16*(K-0.25)*(math.log(N)-3*math.log(E)))
    return D


# In[6]:


def vector_init(dim):
    '''
    initialize a vector of specific length with the constraint of a mean of zero and a variance of 1/n
    '''
    a = np.random.normal(loc=0.0, scale=1/math.sqrt(float(dim)), size=(length))
    return a


# In[7]:


def vector_product(v0, v1, axis=0):
    '''
    Return vector perpendicular to vectors.
    '''
    return np.cross(v0, v1, axis=axis) 


# In[8]:


def encode(a, b):
    '''
    Computes the circular convolution of the (real-valued) vectors a and b.
    '''
    v1 = np.fft.fft(a)
    v2 = np.fft.fft(b)
    return np.fft.ifft(np.multiply(v1, v2)).real


# In[9]:


def decode(a, b):
    '''
    Computes the circular correlation (inverse convolution) of the real-valued
    vector a with b.
    '''
    v1 = np.fft.fft(a)
    v2 = np.fft.fft(b)
    return np.fft.ifft(np.multiply(v1.conj(), v2)).real


# In[10]:


def hammingSim(a, b):
    '''
    Computes the normalized Hamming similarity between binary vectors a and b.
    '''
    h = float(numpy.sum((a > 0) * (b > 0))) / float(numpy.sum((a > 0) + (b > 0)))
    return h


# In[11]:


def euclidean_distance(a,b):
    '''
    Return the Euclidean distance between vectors a and b.
    '''
    return numpy.sum((a - b)**2.0)**0.5


# In[12]:


def normalize(a):
    '''
    Normalize a vector to length 1.
    '''
    return a / numpy.sum(a**2.0)**0.5


# In[13]:


def prev_embedding_initializations(dim):  
    '''
    previous method for initializing embedding vectors: it identifies a set of orthonormal vectors through singular value decomposition
    '''
    X = np.random.normal(loc=0.0, scale=1/math.sqrt(dim), size=(dim, dim))
    U, _, Vt = np.linalg.svd(X, full_matrices=False)
    np.allclose(np.dot(Vt, Vt.T), np.eye(Vt.shape[0]))
    W = Vt.reshape((dim, dim))
    reference = W[0]
    return W


# In[14]:


def embedding_initializations(N, dim):  
    '''
    initialize a list of vectors where values are independent drawn from N(0, 1/N)
    '''
    X = np.random.normal(loc=0.0, scale=1/math.sqrt(dim), size=(N, dim))
    return X


# ### Process description files

# In[15]:


def gameDescFromFile(filename):

    f = open(fileName, 'r')
    lines = f.readlines()
    f.close()

    return getGameDescriptionFromLines(lines)


# pass e.g. gameString.replace('\t', '    ').split('\n')
# as returned by writeTheoryToTxt
#
def getGameDescriptionFromLines(lines):

    #pprint(lines)
        
    # index of the first line in the sprite set
    spriteIdx = None
    # index of the first line in the interaction set
    interactionIdx = None
    # index of the first line in the termination
    terminationIdx = None

    for idx, row in enumerate(lines):
        if row.split() == []:
            continue
        if row.split()[0] == 'SpriteSet':
            spriteIdx = idx + 1
        if row.split()[0] == 'InteractionSet':
            interactionIdx = idx + 1
        if row.split()[0] == 'TerminationSet':
            terminationIdx = idx + 1

    nonSpriteSet = ['TerminationSet', 'InteractionSet', 'LevelMapping']
    nonInteractionSet = ['TerminationSet', 'SpriteSet', 'LevelMapping']
    nonTerminationSet = ['InteractionSet', 'SpriteSet', 'LevelMapping']
    
    spriteSet = []
    interactionSet = []
    terminationSet = []

    # store information of the sprite set
    for row in lines[spriteIdx:]:
        
        # reaches an empty line
        if row.split() == []:
            continue
            
        # reaches the end of the sprite set
        if row.split()[0] in nonSpriteSet:
            break
            
        # still inside the sprite set
        tokens = row.split()
        sprite_info = {}

        if len(tokens) < 3:
            logging.error('NO SPRITE TYPE' + str(tokens)) # TODO zelda enemy sprite; assert false for theories
            continue
        
        sprite_info["name"] = tokens[0]
        sprite_info["type"] = tokens[2]
        
        for token in tokens[2:]:
            if "=" in token:
                field, value = token.split("=")
                # cooldown, spawnCooldown, speed, total, prob, limit
                # orientation, color eliminated
                # momchil TODO: brain might care about color, even in theory region
                if field in ['color', 'singleton', 'cons', 'rotateInPlace', 'autotling', 'frameRate', 'portal', 'total']:
                    continue
                if field == "speed":
                    if float(value) < 0.5:
                        value = "slow"
                    else:
                        value = "fast"
                if field == "cooldown":
                    if float(value) < 4:
                        value = "slow"
                    else:
                        value = "fast"
                if field == "limit":
                    if float(value) < 6:
                        value = "few"
                    else:
                        value = "many"
                if field == "spawnCooldown":
                    if float(value) < 10:
                        value = "few"
                    else:
                        value = "many"
                if field == "prob":
                    if float(value) < 0.03:
                        value = "slow"
                    else:
                        value = "fast"
                if field == 'stype':
                    sprite_info[field + "_" + tokens[2]] = value
                else:
                    sprite_info[field] = value
        spriteSet.append(sprite_info)

    # stores information of the interaction set
    for row in lines[interactionIdx:]:
        
        # if empty line
        if row.split() == []:
            continue
        
        # if the present line is commented out
        if row.split()[0][0] == "#":
            continue
        
        # reaches the end of the interaction set
        if row.split()[0] in nonInteractionSet:
            break
        
        # ignores the interaction of "nothing"
        if row.split()[3] == "nothing":
            continue
            
        if row.split()[3] == "stepBack":
            continue
            
        tokens = row.split()
        agent = tokens[1]
        patient = tokens[0]
        interaction = tokens[3]
        parameters = {}
        
        if len(tokens) > 4:
            for token in tokens[4:]:
                if "#" in token:
                    continue
                else:
                    field, value = token.split("=")
                    
                    if field == "limit":
                        if float(value) < 0:
                            value = "negative"
                        else:
                            value = "positive"
                    elif field == "value":
                        if float(value) < 0:
                            value = "negative"
                        else:
                            value = "positive"
                    
                    if field == "stype":
                        parameters[field + "_" + interaction] = value
                    else:
                        parameters[field] = value
        
        if agent == "EOS" or patient == "EOS":
            logging.error("there shouldn't be EOS") # TODO momchil
            continue
            
        # distinguish roles of the same type across interactions
        interaction_info = {"agent_" + str(interaction): agent, "patient_" + str(interaction): patient, "interaction": interaction, "parameters": parameters}
        interactionSet.append(interaction_info)

    # stores information of the termination set
    for row in lines[terminationIdx:]:
        
        # if empty line
        if row.split() == []:
            continue
        
        # if the present line is commented out
        if row.split()[0][0] == "#":
            continue
        
        # reaches the end of the termination set
        if row.split()[0] in nonTerminationSet:
            break
        
        tokens = row.split()
        termination_type = None
        stype_obj = None
        outcome = None
        
        for i, token in enumerate(tokens):
            if i == 0:
                termination_type = token
                continue
            info = token.split("=")
            if info[0] == 'stype':
                stype_obj = info[1]
            elif info[0] == 'win':
                outcome = info[1]
            elif termination_type == "Timeout" and info[0] == "limit":
                continue
                
        # distinguish roles of the same type across interactions
        if stype_obj is not None:
            termination_info = {"termination_type": termination_type, "stype" + "_" + termination_type: stype_obj, "outcome": outcome}
            terminationSet.append(termination_info)
        else:
            termination_info = {"termination_type": termination_type, "outcome": outcome}
            terminationSet.append(termination_info)
            
    gameDesc = {"sprites": spriteSet, "interactions": interactionSet, "terminations": terminationSet}
    return gameDesc



# a sample of HRR embeddings
# as if it's a single "subject"
#
class SubjectHRR(object):

    # K: the maximum number of terms to be combined
    # N: the number of atomic values in the language
    # E: the probability of error
    def __init__(self, K, N, E):
        self.D = int(math.ceil(dim(K, N, E)))
        self.embeddings = {}

    def genEmbedding(self):
        return np.random.normal(loc=0.0, scale=1.0/math.sqrt(self.D), size=(self.D))

    def embedToken(self, token):
        if token not in self.embeddings.keys():
            self.embeddings[token] = self.genEmbedding()
            logging.debug('                                        generating ' + token) #, ': ', self.embeddings[token]
        return self.embeddings[token]

    def embedGame(self, gameDesc, normalize):
        
        pprint(gameDesc)

        game_HRR = np.zeros(self.D)
        spriteSet_HRR = np.zeros(self.D)
        interactionSet_HRR = np.zeros(self.D)
        terminationSet_HRR = np.zeros(self.D)

        sprite_set = gameDesc['sprites']
        interaction_set = gameDesc['interactions']
        termination_set = gameDesc['terminations']
    
        sprite_embeddings = {}

        logging.debug('...sprites')
        
        # first embed non-stype sprites: base vectors should have an expected length of 1
        for sprite_info in sprite_set:
            sprite_name = sprite_info['name']
            sprite_embedding = np.zeros(self.D)
            s = False
            for field in sprite_info.keys():
                if 'stype' in field:
                    s = True
            logging.debug('    :: ' + sprite_name)
            if s:
                continue
            else:
                for field, val in sprite_info.iteritems():
                    if field == 'name':
                        continue
                    else:
                        logging.debug('          + ' + field + ' * ' + val)
                        feature_embedding = encode(self.embedToken(field), self.embedToken(val))
                        sprite_embedding = np.add(sprite_embedding, feature_embedding)
            sprite_embedding = sprite_embedding / np.sqrt(np.sum(np.square(sprite_embedding))) # unit length TODO legit? see X.E in Plate 1995
            sprite_embeddings[sprite_name] = sprite_embedding
            
        logging.debug('...more sprites')

        # then let's deal with stype sprites whose stype arguments are already embedded: base vectors should have an expected length of 1
        moreRemaining = True
        it = 0
        while moreRemaining:

            it += 1 
            if it == 100:
                # TODO happens rarely, e.g. for subj 3; just ignore for now.. TODO FIXME
                logging.error('RECURSIVE SPRITE STYPES! ignoring...')
                break

            moreRemaining = False
        
            for sprite_info in sprite_set:
                sprite_name = sprite_info['name']
                sprite_embedding = np.zeros(self.D)
                logging.debug('    :: ' + sprite_name)
                if sprite_name in sprite_embeddings.keys():
                    continue
                s = None
                for field in sprite_info.keys():
                    if 'stype' in field:
                        assert s is None # can't have 2 stypes
                        s = field
                stype = sprite_info[s]
                if stype == sprite_name:
                    # self-referential / recursive stype
                    # handle by special casing TODO hack
                    #
                    sprite_info[s] = 'recursive'
                if stype not in sprite_embeddings.keys() and stype != 'recursive':
                    moreRemaining = True
                    continue
                else:
                    for field, val in sprite_info.iteritems():
                        if field == 'name':
                            continue
                        elif 'stype' in field and val != 'recursive':
                            logging.debug('             + ' + field + ' * sprite ' + val)
                            feature_embedding = encode(self.embedToken(field), sprite_embeddings[val])
                            sprite_embedding = np.add(sprite_embedding, feature_embedding)
                        else:
                            logging.debug('             + ' + field + ' * ' + val)
                            feature_embedding = encode(self.embedToken(field), self.embedToken(val))
                            sprite_embedding = np.add(sprite_embedding, feature_embedding)
                sprite_embedding = sprite_embedding / np.sqrt(np.sum(np.square(sprite_embedding))) # unit length TODO legit? see X.E in Plate 1995
                sprite_embeddings[sprite_name] = sprite_embedding
        
        for sprite in sprite_embeddings:
            spriteSet_HRR = np.add(spriteSet_HRR, sprite_embeddings[sprite])
        
        logging.debug('...interactions')

        for interaction_info in interaction_set:
            interaction_embedding = np.zeros(self.D)

            logging.debug(interaction_info)

            for field, val in interaction_info.iteritems():
                if field is not "parameters":
                    #if field not in embeddings or (interaction_info[field] not in embeddings and interaction_info[field] not in sprite_embeddings):
                    #    print("{}, {}".format(field, interaction_info[field]))
                    if 'agent' in field or 'patient' in field:
                        logging.debug('             + ' + field + ' * sprite ' + val)
                        if val not in sprite_embeddings:
                            logging.error('NO SUCH SPRITE ' + val) # TODO helper rand & missile; add assert for theories
                            continue
                        embedding = encode(self.embedToken(field), sprite_embeddings[val])
                        interaction_embedding = np.add(interaction_embedding, embedding)
                    else:
                        logging.debug('             + ' + field + ' * ' + val)
                        embedding = encode(self.embedToken(field), self.embedToken(val))
                        interaction_embedding = np.add(interaction_embedding, embedding)
                else:
                    for subfield in val:
                        if val[subfield] in sprite_embeddings.keys():
                            logging.debug('             + ' + field + ' * sprite ' + val[subfield])
                            if val[subfield] not in sprite_embeddings:
                                print 'NO SUCH SPRITE ', val[subfield] # TODO add assert for theories
                                continue
                            embedding = encode(self.embedToken(subfield), sprite_embeddings[val[subfield]])
                            interaction_embedding = np.add(interaction_embedding, embedding)
                        else:
                            logging.debug('             + ' + field + ' * ' + val[subfield])
                            embedding = encode(self.embedToken(subfield), self.embedToken(val[subfield]))
                            interaction_embedding = np.add(interaction_embedding, embedding)
            interactionSet_HRR = np.add(interactionSet_HRR, interaction_embedding)

        logging.debug('...terminations')
        
        for termination_info in termination_set:
            termination_embedding = np.zeros(self.D)
            for field, val in termination_info.iteritems():
                if 'stype' in field:
                    logging.debug('             + ' + field + ' * sprite ' + val)
                    if val not in sprite_embeddings:
                        logging.error('NO SUCH SPRITE ' + val) # TODO add assert for theories
                        continue
                    embedding = encode(self.embedToken(field), sprite_embeddings[val])
                    termination_embedding = np.add(termination_embedding, embedding)
                else:
                    logging.debug('             + ' + field + ' * ' + val)
                    embedding = encode(self.embedToken(field), self.embedToken(val))
                    termination_embedding = np.add(termination_embedding, embedding)
            terminationSet_HRR = np.add(terminationSet_HRR, termination_embedding)

        if normalize:
            # see X.E in Plate 1995
            spriteSet_HRR = spriteSet_HRR / np.sqrt(np.sum(np.square(spriteSet_HRR)))
            interactionSet_HRR = interactionSet_HRR / np.sqrt(np.sum(np.square(interactionSet_HRR)))
            terminationSet_HRR = terminationSet_HRR / np.sqrt(np.sum(np.square(terminationSet_HRR)))

        game_HRR = np.add(game_HRR, spriteSet_HRR)
        game_HRR = np.add(game_HRR, interactionSet_HRR)
        game_HRR = np.add(game_HRR, terminationSet_HRR)
                
        return game_HRR, spriteSet_HRR, interactionSet_HRR, terminationSet_HRR



    def embedTheory(self, theory):

        theory_HRR = np.zeros(self.D)
        spriteSet_HRR = np.zeros(self.D)
        interactionSet_HRR = np.zeros(self.D)
        terminationSet_HRR = np.zeros(self.D)

        sprite_embeddings = {}

        logging.debug('...terminations')

        for terminationRule in theory.terminationSet:
            if terminationRule.ruleType in ['TimeoutRule']:
                pass
        



def sanity(dist='correlation'):

    nsamples = 100
    K = 10
    N = 10
    E = 0.05

    rm, game_names, rs = gen_ground_truth_RDMs(K, N, E, nsamples, dist, shuffle=False)
    rsem = np.std(rs, axis=0) / math.sqrt(nsamples)

    _, _, null_rs = gen_ground_truth_RDMs(K, N, E, nsamples, dist, shuffle=True)
    
    ng = len(game_names)

    # compute Spearman rank correlations for every other pair of subjects
    # to make sure they are consistent
    #
    rhos = []
    null_rhos = []
    ix = np.triu_indices(ng, 1)
    for i in range(0,nsamples,2):
        rho = scipy.stats.spearmanr(rs[i,ix[0],ix[1]], rs[i+1,ix[0],ix[1]]).correlation
        rhos.append(rho)

        null_rho = scipy.stats.spearmanr(null_rs[i,ix[0],ix[1]], rs[i+1,ix[0],ix[1]]).correlation
        null_rhos.append(null_rho)

    rm = np.mean(rs, axis=0)
    rsem = np.std(rs, axis=0) / math.sqrt(nsamples)

    return rm, rsem, rs, null_rs, rhos, null_rhos, game_names



# generate many RDMs from random "subjects" i.e. embeddings
# also generate null distribution for sanity checking
#
def gen_ground_truth_RDMs(K=10, N=10, E=0.05, nsamples=100, dist='correlation', shuffle=False):

    from pymongo import MongoClient

    client = MongoClient('localhost', 27017)
    db = client['heroku_7lzprs54']

    # coupled with neurosynth_rsa_HRR.m
    game_names = [
        "vgfmri3_chase",
        "vgfmri3_helper",
        "vgfmri3_bait",
        "vgfmri3_lemmings",
        "vgfmri3_plaqueAttack",
        "vgfmri3_zelda"
    ]

    games = []
    for i in range(len(game_names)):
        game = db.games.find_one({'name': game_names[i]})
        games.append(game)
    ng = len(games)

    game_RDMs = np.zeros((nsamples, ng, ng))
    sprite_RDMs = np.zeros((nsamples, ng, ng))
    interaction_RDMs = np.zeros((nsamples, ng, ng))
    termination_RDMs = np.zeros((nsamples, ng, ng))

    for i in range(nsamples):
        #logging.info('iter ' + str(i)) 
        print i

        subj = SubjectHRR(K, N, E)
        
        game_HRR = np.zeros((len(games), subj.D))
        sprite_HRR = np.zeros((len(games), subj.D))
        interaction_HRR = np.zeros((len(games), subj.D))
        termination_HRR = np.zeros((len(games), subj.D))
        for j in range(ng):
            game = games[j]

            logging.debug(' ---------------' + game_names[j])

            lines = game['descs'][0].replace('\t', '    ').split('\n')
            desc = getGameDescriptionFromLines(lines)
            
            game_HRR[j,:], sprite_HRR[j,:], interaction_HRR[j,:], termination_HRR[j,:] = subj.embedGame(desc, normalize=False)

        if shuffle:
            np.random.shuffle(game_HRR) # null distr

        if dist == 'correlation':
            game_RDM = 1 - np.corrcoef(game_HRR)
            sprite_RDM = 1 - np.corrcoef(sprite_HRR)
            interaction_RDM = 1 - np.corrcoef(interaction_HRR)
            termination_RDM = 1 - np.corrcoef(termination_HRR)
        elif dist == 'cosine':
            game_RDM = 1 - k.cosine_similarity(game_HRR)
            sprite_RDM = 1 - k.cosine_similarity(sprite_HRR)
            interaction_RDM = 1 - k.cosine_similarity(interaction_HRR)
            termination_RDM = 1 - k.cosine_similarity(termination_HRR)
        elif dist == 'euclidean':
            game_RDM = k.euclidean_distances(game_HRR)
            sprite_RDM = k.euclidean_distances(sprite_HRR)
            interaction_RDM = k.euclidean_distances(interaction_HRR)
            termination_RDM = k.euclidean_distances(termination_HRR)
        else: 
            assert False, 'invalid distance metric'

        game_RDMs[i,:,:] = game_RDM
        sprite_RDMs[i,:,:] = sprite_RDM
        interaction_RDMs[i,:,:] = interaction_RDM
        termination_RDMs[i,:,:] = termination_RDM

    game_RDM = np.mean(game_RDMs, axis=0)
    sprite_RDM = np.mean(sprite_RDMs, axis=0)
    interaction_RDM = np.mean(interaction_RDMs, axis=0)
    termination_RDM = np.mean(termination_RDMs, axis=0)

    return game_RDM, sprite_RDM, interaction_RDM, termination_RDM, game_names




# export ground truth HRR RDMs to matlab
#
def gen_and_export_RDMs_to_matlab(K, N, E, nsamples, dist):

    filename='mat/HRR_groundtruth_RDM_K=%d_N=%d_E=%.3f_nsamples=%d_dist=%s.mat' % (K, N, E, nsamples, dist)

    game_RDM, sprite_RDM, interaction_RDM, termination_RDM, game_names = gen_ground_truth_RDMs(K, N, E, nsamples, dist)

    g = np.zeros((len(game_names),), dtype=np.object)
    g[:] = game_names

    scipy.io.savemat(filename, {'game_RDM': game_RDM, 'sprite_RDM': sprite_RDM, 'interaction_RDM': interaction_RDM, 'termination_RDM': termination_RDM, 'game_names': game_names})



# helper to read multi from matlab (must have created it first with ccnl_check_multi)
#
def get_onsets_and_durs_from_beta_series_GLM(glmodel, subj_id, run_id):
    filename = 'mat/vgdl_create_multi_glm%d_subj%d_run%d.mat' % (glmodel, subj_id, run_id)
    
    import h5py

    onsets = []
    durations = []
    with h5py.File(filename, 'r') as f: # make sure to save with -v7.3, otherwise doesn't work...
        
        n = len(f['multi']['onsets'][()])
        for i in range(n):
            onsets.append(f[f['multi']['onsets'][i][0]][()][0][0])
            durations.append(f[f['multi']['durations'][i][0]][()][0][0])

    return onsets, durations

# get squence of unique HRRs for subject's inferred theories
# faster, and also used for decoding (we pass those to MATLAB which recombines them, convolves with the HRF, computes the kernels, and fits the GP in the same loop)
# copy of gen_subject_HRRs
#
def gen_subject_unique_HRRs(subj_id, K=10, N=10, E=0.05, nsamples=100, normalize=False):
    subj_id = str(subj_id)

    import socket
    from pymongo import MongoClient
    from collections import defaultdict
    from vgdl import core
    from vgdl.core import VGDLParser, fMRI_screensize
    from vgdl.core import keyPresses as keyNames
    from IPython import embed
    from vgdl.EMPA import Agent
    import cPickle, cloudpickle
    from vgdl.environment import Environment
    from vgdl.hyperparameters import hyperparameter_sets
    from vgdl.theory_template import TimeStep, Theory, Game, writeTheoryToTxt, generateSymbolDict

    import pygame

    if 'omchil' in socket.gethostname() or 'ncfood' in socket.gethostname() or 'ncflogin' in socket.gethostname():
        # local on my Mac, or on a login / VDI node
        client = MongoClient('localhost', 27017)
    else:
        # cluster
        client = MongoClient('holy2a05207.rc.fas.harvard.edu', 27017)

    db = client['heroku_7lzprs54']

    subj = db.subjects.find_one({'subj_id': subj_id})

    # get plays
    query = {'subj_id': subj_id, 'run_id': {'$lt': 7}}
    plays = db.plays.find(query, {'_id': 1}).sort('start_time')
    pks = []
    for play in plays:
        pks.append(play['_id'])
    del plays # close cursor, o/w screws things up

    # "subject" embeddings: have multiple (nsamples), for robustness
    samples = [SubjectHRR(K, N, E) for _ in range(nsamples)]
   
    theory_HRRs = [[] for _ in range(nsamples)] 
    sprite_HRRs = [[] for _ in range(nsamples)] 
    interaction_HRRs = [[] for _ in range(nsamples)]
    termination_HRRs = [[] for _ in range(nsamples)] 
    ts = []
    run_id = []
    play_key = []
    frame = []
    block_ons_idx = []
    block_offs_idx = []
    game_names = []

    then0 = time.time()

    last_block_id = None

    gameStrings = []  # theories as strings
    gameString_to_id = dict()  # reverse mapping for gameStrings 
    theories = []
    theory_id_seq = []

    for pk in pks:

        then = time.time()

        query = {'_id': pk}
        play = db.plays.find_one(query)
        assert play['subj_id'] == subj_id

        game = subj['games'][play['game_id']]
        print 'gen_subject_HRRs: subj %s, run %d, block %d, instance %d, play %d: %s (%s), desc %d, level %d' % (play['subj_id'], play['run_id'], play['block_id'], play['instance_id'], play['play_id'], game['name'], game['fake_name'], play['desc_id'], play['level_id'])

        # get regressors
        q = {'play_key': play['_id']}
        print q
        print db.regressors.count(q)
        assert db.regressors.count(q) <= 1, 'Too many regressors!' 
        if db.regressors.count(q) == 0:
            print 'skipping (e.g. Sokoban)'
            continue
        regs = db.regressors.find(q).sort('ts', -1)
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

        # load theories from disk
        with open(reg['regressors']['theory_filename'], 'r') as f:
            reg['regressors']['theory'] = cloudpickle.load(f)

        # create temporary environment just to convert theory to VGDL description
        # roughly main steps from:
        # - fmri_empaRepaly.py
        # - vgdl/environment.py: playCurriculum.py
        # - vgdl/environment.py: playEpisode.py
        # - vgdl/EMPA.py: initializeHypotheses and initializeVrle
        game_name = game['name']
        task_ID = 'subj={}'.format(subj_id)
        agent = Agent('full', game_name, hyperparameter_sets=hyperparameter_sets, hyperparameter_index='short-term', metacontroller_index=0, IW_k=1, extra_atom_allowed=True, task_ID=task_ID)
        environment = Environment(game_name, agent, task_ID=task_ID, produce_printout=False)
        environment.gameString = play['game_str']
        environment.levelString = play['level_str']
        environment.playback_states = None
        environment.playback_keystates = None
        environment.initializeEnvironment()
        symbolDict = generateSymbolDict(environment.environment)

        print 'loading play time: ', (time.time() - then)

        then = time.time()

        for i in range(0, len(reg['regressors']['theory'])):
            theory = reg['regressors']['theory'][i][0]

            # convert theory to VGDL description
            gameString, _, _ = writeTheoryToTxt(environment.environment, theory, symbolDict, "./theory_files/{}_{}.py_auto_HRR".format(agent.gameFilename, task_ID))

            if gameString not in gameString_to_id.keys():
                # previously unseen theory

                gameLines = gameString.replace('\t', '    ').split('\n')
                gameDesc = getGameDescriptionFromLines(gameLines)

                # save it
                gameString_to_id[gameString] = len(gameString_to_id)
                gameStrings.append(gameString)
                theories.append(theory)

                # note each new row = unique theory, not frame
                for j in range(nsamples):
                    theory_HRR, sprite_HRR, interaction_HRR, termination_HRR = samples[j].embedGame(gameDesc, normalize)
                    theory_HRRs[j].append(theory_HRR)
                    sprite_HRRs[j].append(sprite_HRR)
                    interaction_HRRs[j].append(interaction_HRR)
                    termination_HRRs[j].append(termination_HRR)

            theory_id = gameString_to_id[gameString]
            assert gameStrings[theory_id] == gameString

            theory_id_seq.append(theory_id)
            frame.append(reg['regressors']['theory'][i][1])
            ts.append(reg['regressors']['theory'][i][2] - play['run_start_ts'])
            play_key.append(str(play['_id']))
            run_id.append(play['run_id'])
            game_names.append(game_name)

        print 'HRR time: ', (time.time() - then)

    block_offs_idx.append(len(ts))

    print 'total time: ', (time.time() - then0)

    return theory_id_seq, gameString_to_id, gameStrings, theories, theory_HRRs, sprite_HRRs, interaction_HRRs, termination_HRRs, ts, run_id, play_key, frame, block_ons_idx, block_offs_idx, game_names



# get squence of HRRs for subject's inferred theories
#
def gen_subject_HRRs(subj_id, K=10, N=10, E=0.05, nsamples=100, normalize=False):
    subj_id = str(subj_id)

    import socket
    from pymongo import MongoClient
    from collections import defaultdict
    from vgdl import core
    from vgdl.core import VGDLParser, fMRI_screensize
    from vgdl.core import keyPresses as keyNames
    from IPython import embed
    from vgdl.EMPA import Agent
    import cPickle, cloudpickle
    from vgdl.environment import Environment
    from vgdl.hyperparameters import hyperparameter_sets
    from vgdl.theory_template import TimeStep, Theory, Game, writeTheoryToTxt, generateSymbolDict

    import pygame

    if 'omchil' in socket.gethostname() or 'ncfood' in socket.gethostname() or 'ncflogin' in socket.gethostname():
        # local on my Mac, or on a login / VDI node
        client = MongoClient('localhost', 27017)
    else:
        # cluster
        client = MongoClient('holy2a05207.rc.fas.harvard.edu', 27017)

    db = client['heroku_7lzprs54']

    subj = db.subjects.find_one({'subj_id': subj_id})

    # get plays
    query = {'subj_id': subj_id, 'run_id': {'$lt': 7}}
    plays = db.plays.find(query, {'_id': 1}).sort('start_time')
    pks = []
    for play in plays:
        pks.append(play['_id'])
    del plays # close cursor, o/w screws things up

    # "subject" embeddings: have multiple (nsamples), for robustness
    samples = [SubjectHRR(K, N, E) for _ in range(nsamples)]
   
    theory_HRRs = [[] for _ in range(nsamples)] 
    sprite_HRRs = [[] for _ in range(nsamples)] 
    interaction_HRRs = [[] for _ in range(nsamples)]
    termination_HRRs = [[] for _ in range(nsamples)] 
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
        print 'gen_subject_HRRs: subj %s, run %d, block %d, instance %d, play %d: %s (%s), desc %d, level %d' % (play['subj_id'], play['run_id'], play['block_id'], play['instance_id'], play['play_id'], game['name'], game['fake_name'], play['desc_id'], play['level_id'])

        # get regressors
        q = {'play_key': play['_id']}
        print q
        print db.regressors.count(q)
        assert db.regressors.count(q) <= 1, 'Too many regressors!' 
        if db.regressors.count(q) == 0:
            print 'skipping (e.g. Sokoban)'
            continue
        regs = db.regressors.find(q).sort('ts', -1)
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

        # load theories from disk
        with open(reg['regressors']['theory_filename'], 'r') as f:
            reg['regressors']['theory'] = cloudpickle.load(f)

        # create temporary environment just to convert theory to VGDL description
        # roughly main steps from:
        # - fmri_empaRepaly.py
        # - vgdl/environment.py: playCurriculum.py
        # - vgdl/environment.py: playEpisode.py
        # - vgdl/EMPA.py: initializeHypotheses and initializeVrle
        game_name = game['name']
        task_ID = 'subj={}'.format(subj_id)
        agent = Agent('full', game_name, hyperparameter_sets=hyperparameter_sets, hyperparameter_index='short-term', metacontroller_index=0, IW_k=1, extra_atom_allowed=True, task_ID=task_ID)
        environment = Environment(game_name, agent, task_ID=task_ID, produce_printout=False)
        environment.gameString = play['game_str']
        environment.levelString = play['level_str']
        environment.playback_states = None
        environment.playback_keystates = None
        environment.initializeEnvironment()
        symbolDict = generateSymbolDict(environment.environment)

        print 'loading play time: ', (time.time() - then)

        then = time.time()

        for i in range(0, len(reg['regressors']['theory'])):
            theory = reg['regressors']['theory'][i][0]

            # convert theory to VGDL description
            gameString, _, _ = writeTheoryToTxt(environment.environment, theory, symbolDict, "./theory_files/{}_{}.py_auto_HRR".format(agent.gameFilename, task_ID))
            gameLines = gameString.replace('\t', '    ').split('\n')

            gameDesc = getGameDescriptionFromLines(gameLines)

            for j in range(nsamples):
                theory_HRR, sprite_HRR, interaction_HRR, termination_HRR = samples[j].embedGame(gameDesc, normalize)
                theory_HRRs[j].append(theory_HRR)
                sprite_HRRs[j].append(sprite_HRR)
                interaction_HRRs[j].append(interaction_HRR)
                termination_HRRs[j].append(termination_HRR)

            frame.append(reg['regressors']['theory'][i][1])
            ts.append(reg['regressors']['theory'][i][2] - play['run_start_ts'])
            play_key.append(str(play['_id']))
            run_id.append(play['run_id'])

        print 'HRR time: ', (time.time() - then)


    block_offs_idx.append(len(ts))

    print 'total time: ', (time.time() - then0)

    return theory_HRRs, sprite_HRRs, interaction_HRRs, termination_HRRs, ts, run_id, play_key, frame, block_ons_idx, block_offs_idx


# aggregate single sample HRRs in range
#
def aggregate_HRRs(HRRs, st, en, agg):

    if agg == 'avg':
        HRR = np.zeros(HRRs[st].shape)
        for i in range(st,en):
            HRR = np.add(HRR, HRRs[i])
        HRR = HRR / (en - st)

    elif agg == 'last':
        HRR = HRR[en - 1]

    else:
        assert False, 'invalid aggregate'

    return HRR


# convolve single sample HRR timecourses with HRF 
# logic from spm_get_ons.m and spm_Volterra.m, as used in spm_fMRI_design.m
#
def convolve_HRRs(HRRs, ts, run_id, block_ons_idx, block_offs_idx):

    assert len(block_ons_idx) == len(block_offs_idx)

    # convert to proper 2D array, rows = frames, columns = features
    HRRs = np.concatenate([np.reshape(HRR, (1,len(HRR))) for HRR in HRRs], axis=0)

    filename = 'mat/SPM73.mat' # any single-subject SPM.mat (glmOutput/model1/subj1/), make sure to re-save with -v7.3

    import h5py

    with h5py.File(filename, 'r') as f:
        nruns = len(f['SPM']['nscan'])
        assert nruns == 6

    Xx = []
    r_id = [] 
    Xsf = []

    for s in range(nruns): # from spm_fMRI_design.m

        which = np.array(run_id) == s + 1

        with h5py.File(filename, 'r') as f:
            # from spm_get_ons.m
            #
            k = int(f['SPM']['nscan'][s][0])
            assert k == 283 # # of TRs

            T = int(f['SPM']['xBF']['T'][0][0])
            assert T == 16 # resolution: # of time points per TR

            dt = f['SPM']['xBF']['dt'][0][0]
            assert dt == 0.1250 # resolution: # of seconds per time point (T * dt = 2 s = TR)

            UNITS = u''.join(unichr(c) for c in f['SPM']['xBF']['UNITS'])
            assert UNITS == 'secs'
            TR = 1 # not actual TR, b/c units of dt are in seconds

            bf = f['SPM']['xBF']['bf'][()]
            bf = np.reshape(bf, bf.shape[1]) # make 1-D
            assert bf.shape[0] == 257

        # calculate durations separately for each play, because we assume consecituve frames within play
        # and need to take special care for the last frame
        # update: don't do it; assume theory lingers between plays
        #dur = np.array([])
        #for i in range(len(block_ons_idx)):
        #    st = block_ons_idx[i]
        #    en = block_offs_idx[i] # + 1

        #    if run_id[st] != s + 1: 
        #        continue

        #    print st, en
        #    d = np.array(ts[st+1:en]) - np.array(ts[st:en-1])
        #    d = np.append(d, np.mean(d)) # average duration for last frame (see get_regressors.m)
        #    dur = np.append(dur, d)

        # from spm_get_ons.m
        #
        ons = np.array(ts)[which]
        #dur = ons[1:] - ons[:-1]
        #dur = np.append(dur, np.mean(dur)) # average duration for last frame (see get_regressors.m)
        u = HRRs[which,:]
        ton = np.round(ons*TR/dt).astype(int) + 33 # 32 bin offset
        toff = ton[1:]
        toff = np.append(toff, ton[-1] + T) # 1 s duration for last one, to match other between-block / level durations TODO more rigorous
        sf = np.zeros((k*T + 128, u.shape[1]))

        assert np.all(ton >= 0)
        assert np.all(ton < sf.shape[0])
        assert np.all(toff >= 0)
        assert np.all(toff < sf.shape[0])

        for j in range(len(ton)):
            sf[ton[j],:] += u[j,:]
            sf[toff[j],:] -= u[j,:]

        Xsf.append(sf) # for sanity checks

        sf = np.cumsum(sf, axis=0)
        sf = sf[0:k*T + 32]  # 32 bin offset

        # from spm_Volterra.m
        #
        X = np.zeros(sf.shape)
        for i in range(sf.shape[1]):
            x = sf[:,i]
            d = range(x.shape[0])
            x = np.convolve(x, bf)
            x = x[d]
            X[:,i] = x

        # from spm_fMRI_design.m
        #
        with h5py.File(filename, 'r') as f:
            fMRI_T = int(f['SPM']['xBF']['T'][0][0])
            fMRI_T0 = int(f['SPM']['xBF']['T0'][0][0])

        # resample regressors at acquisition times (32 bin offset)
        assert k == 283
        idx = np.array(range(k)) * fMRI_T + fMRI_T0 + 32
        X = X[idx - 1, :]

        Xx.append(X)
        r_id.append(np.array([s+1]*X.shape[0]))

    Xx = np.concatenate(Xx, axis=0)
    assert Xx.shape[0] == k * nruns
    assert Xx.shape[1] == HRRs.shape[1]

    Xsf = np.concatenate(Xsf, axis=0)

    r_id = np.concatenate(r_id, axis=0)

    return Xx, r_id, Xsf



# generate kernel from output of convolve_HRRs, after gen_subject_HRRs
#
def gen_subject_kernels(subj_id, HRRs, ts, run_id, block_ons_idx, block_offs_idx, sigma_w):

    nsamples = len(HRRs)

    Ks = []

    for j in range(nsamples):
        
        Xx, r_id, sf = convolve_HRRs(HRRs[j], ts, run_id, block_ons_idx, block_offs_idx)
        Sigma_w = np.identity(Xx.shape[1]) * sigma_w # Sigma_p in Rasmussen, Eq. 2.4

        K = np.matmul(np.matmul(Xx, Sigma_w), np.transpose(Xx)) # K in Rasmussen, Eq. 2.12

        Ks.append(K)

    Ks = [K.reshape((1, K.shape[0], K.shape[1])) for K in Ks]
    Ks = np.concatenate(Ks, axis=0)

    return Ks, r_id, Xx, sf


# generate RDMs from output of gen_subject_HRRs
#
def gen_subject_RDMs(subj_id, theory_HRRs, sprite_HRRs, interaction_HRRs, termination_HRRs, ts, run_id, dist='correlation', agg='avg', glmodel=24, shuffle=False):

    assert len(theory_HRRs[0]) == len(sprite_HRRs[0])
    assert len(theory_HRRs[0]) == len(interaction_HRRs[0])
    assert len(theory_HRRs[0]) == len(termination_HRRs[0])
    assert len(theory_HRRs[0]) == len(ts)
    assert len(theory_HRRs[0]) == len(run_id)
    assert len(theory_HRRs[0]) == len(sprite_HRRs[0])
    assert all([len(theory_HRRs[0]) == len(theory_HRRs[j]) for j in range(len(theory_HRRs))])
    assert all([len(sprite_HRRs[0]) == len(sprite_HRRs[j]) for j in range(len(sprite_HRRs))])
    assert all([len(interaction_HRRs[0]) == len(interaction_HRRs[j]) for j in range(len(interaction_HRRs))])
    assert all([len(termination_HRRs[0]) == len(termination_HRRs[j]) for j in range(len(termination_HRRs))])

    nsamples = len(theory_HRRs)

    #
    # first aggregate HRRs according to boxcars from beta series GLM
    #

    # aggregate for boxcars
    agg_theory_HRRs = [[] for _ in range(nsamples)] 
    agg_sprite_HRRs = [[] for _ in range(nsamples)] 
    agg_interaction_HRRs = [[] for _ in range(nsamples)]
    agg_termination_HRRs = [[] for _ in range(nsamples)] 
    agg_run_id = []
    beta_id = [] # boxcar/beta idx within run, before aggregation

    r = 1 # current run id
    onsets, durations = get_onsets_and_durs_from_beta_series_GLM(glmodel, subj_id, r)

    b = 0 # current boxcar index
    st = 0 # index of first theory for current boxcar
    for en in range(len(theory_HRRs[0])):

        #print st
        #print en
        #print ts[st]
        #print onsets[b]
        #print onsets[b] + durations[b]
        assert ts[st] >= onsets[b] and ts[st] <= onsets[b] + durations[b]

        beta_id.append(b)

        # if we're at the last frame, 
        # or we're about to move to the next boxcar,
        # or we're about to move to the next run,
        # compute aggregate theory until now
        if en + 1 == len(theory_HRRs[0]) or run_id[en + 1] == r + 1 or ts[en + 1] > onsets[b] + durations[b]:

            #print '          end of boxcar!!! aggregate [', st, ',', en, ']; b =', b, ' r =', r
           
            for j in range(nsamples):
                theory_HRR = aggregate_HRRs(theory_HRRs[j], st, en + 1, agg)
                agg_theory_HRRs[j].append(theory_HRR)
                
                sprite_HRR = aggregate_HRRs(sprite_HRRs[j], st, en + 1, agg)
                agg_sprite_HRRs[j].append(sprite_HRR)

                interaction_HRR = aggregate_HRRs(interaction_HRRs[j], st, en + 1, agg)
                agg_interaction_HRRs[j].append(interaction_HRR)

                termination_HRR = aggregate_HRRs(termination_HRRs[j], st, en + 1, agg)
                agg_termination_HRRs[j].append(termination_HRR)
                
            agg_run_id.append(r)

            st = en + 1

            if en + 1 == len(theory_HRRs[0]):
                #print '               ...last iter!'
                pass # last iteration

            elif run_id[en + 1] == r + 1:
                #print '               ...next run!'

                # end of run => go to next one
                assert b + 1 == len(onsets)
                assert ts[en + 1] < ts[en]

                b = 0
                r += 1
                if r < 7:
                    onsets, durations = get_onsets_and_durs_from_beta_series_GLM(glmodel, subj_id, r)

            else:
                #print '               ...next boxcar!'
                # go to next boxcar
                assert ts[en + 1] > onsets[b] + durations[b]
                assert run_id[en + 1] == r
                assert b + 1 < len(onsets)

                b += 1

        else:
            assert ts[en] >= onsets[b] and ts[en] <= onsets[b] + durations[b]
            assert run_id[en] == r
       
    assert b == len(onsets) - 1
    assert r == 6
    assert len(agg_theory_HRRs[0]) == len(onsets) * 6

    #
    # second, compute RDMs
    #

    n = len(agg_theory_HRRs[0])
    theory_RDMs = np.zeros((nsamples, n, n))
    sprite_RDMs = np.zeros((nsamples, n, n))
    interaction_RDMs = np.zeros((nsamples, n, n))
    termination_RDMs = np.zeros((nsamples, n, n))

    for j in range(nsamples):

        if dist == 'correlation':
            theory_RDM = 1 - np.corrcoef(agg_theory_HRRs[j])
            sprite_RDM = 1 - np.corrcoef(agg_sprite_HRRs[j])
            interaction_RDM = 1 - np.corrcoef(agg_interaction_HRRs[j])
            termination_RDM = 1 - np.corrcoef(agg_termination_HRRs[j])

        elif dist == 'cosine':
            theory_RDM = 1 - k.cosine_similarity(agg_theory_HRRs[j])
            sprite_RDM = 1 - k.cosine_similarity(agg_sprite_HRRs[j])
            interaction_RDM = 1 - k.cosine_similarity(agg_interaction_HRRs[j])
            termination_RDM = 1 - k.cosine_similarity(agg_termination_HRRs[j])

        elif dist == 'euclidean':
            theory_RDM = k.euclidean_distances(agg_theory_HRRs[j])
            sprite_RDM = k.euclidean_distances(agg_sprite_HRRs[j])
            interaction_RDM = k.euclidean_distances(agg_interaction_HRRs[j])
            termination_RDM = k.euclidean_distances(agg_termination_HRRs[j])

        else: 
            assert False, 'invalid distance metric'

        theory_RDMs[j,:,:] = theory_RDM
        sprite_RDMs[j,:,:] = sprite_RDM
        interaction_RDMs[j,:,:] = interaction_RDM
        termination_RDMs[j,:,:] = termination_RDM

    theory_RDM = np.mean(theory_RDMs, axis=0)
    sprite_RDM = np.mean(sprite_RDMs, axis=0)
    interaction_RDM = np.mean(interaction_RDMs, axis=0)
    termination_RDM = np.mean(termination_RDMs, axis=0)

    return theory_RDM, sprite_RDM, interaction_RDM, termination_RDM, theory_RDMs, sprite_RDMs, interaction_RDMs, termination_RDMs, agg_theory_HRRs, agg_sprite_HRRs, agg_interaction_HRRs, agg_termination_HRRs, agg_run_id, beta_id



def gen_and_save_subject_RDMs_batched(subj_id):

    # generate HRRs and RDMs in batches, b/c of OOM (HRRs are too big)
    # batches is better than 1 by 1 b/c of overhead of querying mongo
    #

    K = 10 
    N = 10
    E = 0.05
    nsamples = 10
    dist = 'correlation'
    glmodel = 24
    agg = 'avg'

    batch_size = 10
    assert nsamples % batch_size == 0

    all_theory_RDMs = []
    all_sprite_RDMs = []
    all_interaction_RDMs = []
    all_termination_RDMs = []

    for batch in range(nsamples / batch_size):
        print 'BATCH ', batch

        theory_HRRs, sprite_HRRs, interaction_HRRs, termination_HRRs, ts, run_id, play_key, frame, block_ons_idx, block_offs_idx = gen_subject_HRRs(subj_id, K, N, E, batch_size)

        _, _, _, _, theory_RDMs, sprite_RDMs, interaction_RDMs, termination_RDMs, agg_theory_HRRs, agg_sprite_HRRs, agg_interaction_HRRs, agg_termination_HRRs, agg_run_id, beta_id = gen_subject_RDMs(subj_id, theory_HRRs, sprite_HRRs, interaction_HRRs, termination_HRRs, ts, run_id, dist, agg, glmodel)

        all_theory_RDMs.append(theory_RDMs)
        all_sprite_RDMs.append(sprite_RDMs)
        all_interaction_RDMs.append(interaction_RDMs)
        all_termination_RDMs.append(termination_RDMs)

    theory_RDMs = np.concatenate(all_theory_RDMs, axis=0)
    sprite_RDMs = np.concatenate(all_sprite_RDMs, axis=0)
    interaction_RDMs = np.concatenate(all_interaction_RDMs, axis=0)
    termination_RDMs = np.concatenate(all_termination_RDMs, axis=0)

    theory_RDM = np.mean(theory_RDMs, axis=0)
    sprite_RDM = np.mean(sprite_RDMs, axis=0)
    interaction_RDM = np.mean(interaction_RDMs, axis=0)
    termination_RDM = np.mean(termination_RDMs, axis=0)

    # save last batch of HRRs, for sanity checks
    # ...or not (memory)
    #
    '''
    HRR_filename='mat/HRR_subject_subj=%s_K=%d_N=%d_E=%.3f_nsamples=%d.mat' % (subj_id, K, N, E, nsamples)

    d = {
        'theory_HRRs': theory_HRRs,
        'sprite_HRRs': sprite_HRRs,
        'interaction_HRRs': interaction_HRRs,
        'termination_HRRs': termination_HRRs,
        'ts': ts,
        'run_id': run_id,
        'play_key': play_key,
        'K': K,
        'N': N,
        'E': E,
        'nsamples': nsamples,
        'batch_size': batch_size,
        'subj_id': subj_id
    }

    scipy.io.savemat(HRR_filename, d)
    '''

    # save RDMs
    #
    RDM_filename='mat/HRR_subject_RDM_subj=%s_K=%d_N=%d_E=%.3f_nsamples=%d_dist=%s.mat' % (subj_id, K, N, E, nsamples, dist)

    d = {
        'theory_RDM': theory_RDM,
        'sprite_RDM': sprite_RDM,
        'interaction_RDM': interaction_RDM,
        'termination_RDM': termination_RDM,
        #'theory_RDMs': theory_RDMs,  # -- too much memory
        #'sprite_RDMs': sprite_RDMs,
        #'interaction_RDMs': interaction_RDMs,
        #'termination_RDMs': termination_RDMs,
        'agg_theory_HRRs': agg_theory_HRRs,
        'agg_sprite_HRRs': agg_sprite_HRRs,
        'agg_interaction_HRRs': agg_interaction_HRRs,
        'agg_termination_HRRs': agg_termination_HRRs,
        'ts': ts,
        'run_id': run_id,
        'beta_id': beta_id,
        'agg_run_id': agg_run_id,
        'K': K,
        'N': N,
        'E': E,
        'dist': dist,
        'nsamples': nsamples,
        'subj_id': subj_id,
        'glmodel': glmodel,
        'agg': agg
    }

    scipy.io.savemat(RDM_filename, d)




def gen_and_save_subject_kernels_batched(subj_id):

    # copy of gen_and_save_subject_RDMs_batched but for kernels

    # generate HRRs and kernels in batches, b/c of OOM (HRRs are too big)
    # batches is better than 1 by 1 b/c of overhead of querying mongo
    #

    K = 10 
    N = 10
    E = 0.05
    nsamples = 100
    normalize = True

    sigma_w = 1; # TODO parameter

    batch_size = 10
    assert nsamples % batch_size == 0

    all_theory_kernels = []
    all_sprite_kernels = []
    all_interaction_kernels = []
    all_termination_kernels = []

    for batch in range(nsamples / batch_size):
        print 'BATCH ', batch

        theory_HRRs, sprite_HRRs, interaction_HRRs, termination_HRRs, ts, run_id, play_key, frame, block_ons_idx, block_offs_idx = gen_subject_HRRs(subj_id, K, N, E, batch_size, normalize)

        theory_kernels, r_id, theory_Xx, theory_sf = gen_subject_kernels(subj_id, theory_HRRs, ts, run_id, block_ons_idx, block_offs_idx, sigma_w)
        sprite_kernels, _, sprite_Xx, sprite_sf = gen_subject_kernels(subj_id, sprite_HRRs, ts, run_id, block_ons_idx, block_offs_idx, sigma_w)
        interaction_kernels, _, interaction_Xx, interaction_sf = gen_subject_kernels(subj_id, interaction_HRRs, ts, run_id, block_ons_idx, block_offs_idx, sigma_w)
        termination_kernels, _, termination_Xx, termination_sf = gen_subject_kernels(subj_id, termination_HRRs, ts, run_id, block_ons_idx, block_offs_idx, sigma_w)

        all_theory_kernels.append(theory_kernels)
        all_sprite_kernels.append(sprite_kernels)
        all_interaction_kernels.append(interaction_kernels)
        all_termination_kernels.append(termination_kernels)

    theory_kernels = np.concatenate(all_theory_kernels, axis=0)
    sprite_kernels = np.concatenate(all_sprite_kernels, axis=0)
    interaction_kernels = np.concatenate(all_interaction_kernels, axis=0)
    termination_kernels = np.concatenate(all_termination_kernels, axis=0)

    theory_kernel = np.mean(theory_kernels, axis=0)
    sprite_kernel = np.mean(sprite_kernels, axis=0)
    interaction_kernel = np.mean(interaction_kernels, axis=0)
    termination_kernel = np.mean(termination_kernels, axis=0)

    theory_kernel_std = np.std(theory_kernels, axis=0)
    sprite_kernel_std = np.std(sprite_kernels, axis=0)
    interaction_kernel_std = np.std(interaction_kernels, axis=0)
    termination_kernel_std = np.std(termination_kernels, axis=0)

    # save last batch of HRRs, for sanity checks
    # ...or not (memory)
    #
    '''
    HRR_filename='mat/HRR_subject_subj=%s_K=%d_N=%d_E=%.3f_nsamples=%d_for_ker.mat' % (subj_id, K, N, E, nsamples)

    d = {
        'theory_HRRs': theory_HRRs,
        'sprite_HRRs': sprite_HRRs,
        'interaction_HRRs': interaction_HRRs,
        'termination_HRRs': termination_HRRs,
        'ts': ts,
        'run_id': run_id,
        'play_key': play_key,
        'K': K,
        'N': N,
        'E': E,
        'nsamples': nsamples,
        'batch_size': batch_size,
        'subj_id': subj_id
    }

    scipy.io.savemat(HRR_filename, d)
    '''

    # save kernels
    #
    kernel_filename='mat/HRR_subject_kernel_subj=%s_K=%d_N=%d_E=%.3f_nsamples=%d_sigma_w=%.3f_norm=%d.mat' % (subj_id, K, N, E, nsamples, sigma_w, normalize)

    d = {
        'theory_kernel': theory_kernel,
        'sprite_kernel': sprite_kernel,
        'interaction_kernel': interaction_kernel,
        'termination_kernel': termination_kernel,
        'theory_kernel_std': theory_kernel_std,
        'sprite_kernel_std': sprite_kernel_std,
        'interaction_kernel_std': interaction_kernel_std,
        'termination_kernel_std': termination_kernel_std,
        #'theory_kernels': theory_kernels, # -- too much memory
        #'sprite_kernels': sprite_kernels,
        #'interaction_kernels': interaction_kernels,
        #'termination_kernels': termination_kernels,
        'theory_Xx': theory_Xx,
        'sprite_Xx': sprite_Xx,
        'interaction_Xx': interaction_Xx,
        'termination_Xx': termination_Xx,
        'theory_sf': theory_sf,
        'sprite_sf': sprite_sf,
        'interaction_sf': interaction_sf,
        'termination_sf': termination_sf,
        'r_id': r_id,
        'ts': ts,
        'block_ons_idx': block_ons_idx,
        'block_offs_idx': block_offs_idx,
        'K': K,
        'N': N,
        'E': E,
        'sigma_w': sigma_w,
        'nsamples': nsamples,
        'subj_id': subj_id,
    }

    scipy.io.savemat(kernel_filename, d)




def gen_and_save_subject_unique_HRRs(subj_id):

    # copy of gen_and_save_subject_kernels_batched but for unique HRRs

    # generate HRRs for each unique theory only, assign unique ID to each theory,
    # and pass to MATLAB to modify theory sequence and recompute kernels easily in the same loop as fittitg the GP, for decoding
    #

    K = 10 
    N = 10
    E = 0.05
    nsamples = 1
    normalize = True

    theory_id_seq, gameString_to_id, gameStrings, theories, theory_HRRs, sprite_HRRs, interaction_HRRs, termination_HRRs, ts, run_id, play_key, frame, block_ons_idx, block_offs_idx, game_names = gen_subject_unique_HRRs(subj_id, K, N, E, nsamples, normalize)

    # save unique HRRs and theory sequence
    #
    HRR_filename='mat/unique_HRR_subject_subj=%s_K=%d_N=%d_E=%.3f_nsamples=%d_norm=%d.mat' % (subj_id, K, N, E, nsamples, normalize)
    theoriesDir = 'theories'
    theories_filename='%s/unique_theories_subject_subj=%s_K=%d_N=%d_E=%.3f_nsamples=%d_norm=%d.pickle' % (theoriesDir, subj_id, K, N, E, nsamples, normalize)

    with open(theories_filename, 'wb') as f:
        cloudpickle.dump(theories, f)

    d = {
        'theory_id_seq': theory_id_seq,
        'unique_theories_filename': theories_filename,
        'gameStrings': gameStrings,
        'theory_HRRs': theory_HRRs,
        'sprite_HRRs': sprite_HRRs,
        'interaction_HRRs': interaction_HRRs,
        'termination_HRRs': termination_HRRs,
        'ts': ts,
        'run_id': run_id,
        'play_key': play_key,
        'K': K,
        'N': N,
        'E': E,
        'normalize': normalize,
        'block_ons_idx': block_ons_idx,
        'block_offs_idx': block_offs_idx,
        'nsamples': nsamples,
        'game_names': game_names,
        'subj_id': subj_id
    }

    scipy.io.savemat(HRR_filename, d)




if __name__ == '__main__':
    subj_id = int(sys.argv[1])

    #gen_and_save_subject_RDMs_batched(subj_id)
    #gen_and_save_subject_kernels_batched(subj_id)
    gen_and_save_subject_unique_HRRs(subj_id)

    print 'Done'
