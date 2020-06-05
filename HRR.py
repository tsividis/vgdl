# from https://github.com/yl3506/heroku_vgdl/tree/master/HRR_Analysis

import numpy as np
import math
import os 
import csv
import scipy.stats
import sklearn.metrics.pairwise as k
from IPython import embed
import time
from pprint import pprint
import logging, sys

# ### Helper functions

# In[5]:

logging.basicConfig(stream=sys.stderr, level=logging.ERROR)

logging.disable(logging.INFO)


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

    def embedGame(self, gameDesc):
        
        #pprint(gameDesc)

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
            sprite_embedding = sprite_embedding / np.sqrt(np.sum(np.square(sprite_embedding))) # unit length TODO legit?
            sprite_embeddings[sprite_name] = sprite_embedding
            
        logging.debug('...more sprites')

        # then let's deal with stype sprites whose stype arguments are already embedded: base vectors should have an expected length of 1
        moreRemaining = True
        while moreRemaining:

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
                sprite_embedding = sprite_embedding / np.sqrt(np.sum(np.square(sprite_embedding))) # unit length TODO legit?
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

        game_HRR = np.add(game_HRR, spriteSet_HRR)
        game_HRR = np.add(game_HRR, interactionSet_HRR)
        game_HRR = np.add(game_HRR, terminationSet_HRR)
                
        return game_HRR, spriteSet_HRR, interactionSet_HRR, terminationSet_HRR



def sanity():

    from pymongo import MongoClient
    from fmri_play import game_names

    client = MongoClient('localhost', 27017)
    db = client['heroku_7lzprs54']

    games = []
    for i in range(len(game_names)):
        game = db.games.find_one({'name': game_names[i]})
        games.append(game)
    ng = len(games)

    niters = 100
    K = 100
    N = 100
    E = 0.05
    
    rs = np.zeros((niters, ng, ng))

    for i in range(niters):
        logging.info('iter ' + str(i)) 

        s1 = SubjectHRR(K, N, E)
        s2 = SubjectHRR(K, N, E)
        
        g1 = np.zeros((len(games), s1.D))
        g2 = np.zeros((len(games), s2.D))
        for j in range(ng):
            game = games[j]

            logging.debug(' ---------------' + game_names[j])

            lines = game['descs'][0].replace('\t', '    ').split('\n')
            desc = getGameDescriptionFromLines(lines)
            
            g1[j,:], _, _, _ = s1.embedGame(desc)
            g2[j,:], _, _, _ = s2.embedGame(desc)

        r = np.corrcoef(g1, g2)
        r = r[ng:,:ng] # cross-correlations
        rs[i,:,:] = r

    rm = np.mean(rs, axis=0)
    rsem = np.std(rs, axis=0) / math.sqrt(niters)

    return rm, rsem, rs, game_names
