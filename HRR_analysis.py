#!/usr/bin/env python
# coding: utf-8

# # HRR Analysis

# In[4]:


import numpy as np
import math
import os 
import matplotlib.pyplot as plt
import csv
import scipy.stats
import sklearn.metrics.pairwise as k


# ### Helper functions

# In[5]:


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


def gameDescription(fileName):
        
    f = open(fileName, 'r')
    lines = f.readlines()

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
        
        sprite_info["name"] = tokens[0]
        sprite_info["type"] = tokens[2]
        
        for token in tokens[2:]:
            if "=" in token:
                field, value = token.split("=")
                # cooldown, spawnCooldown, speed, total, prob, limit
                # orientation, color eliminated
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
            print("there shouldn't be EOS")
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
            
    f.close()
    return spriteSet, interactionSet, terminationSet


# In[16]:


def identify_tokens(file_path):
    
    # a dictionary containing theory information
    gameDescriptions = {}
    
    game_files = file_path

    for f in os.listdir(game_files):
        if "txt" in f and "lvl" not in f:
            #print(f)
            game_name = " ".join(f[:-4].split("_"))
            if "expt" in game_name:
                game_name = game_name.split(" ")[1]
            gameFileName = game_files + "/" + f
            sprite_set, interaction_set, termination_set = gameDescription(gameFileName)
            game = {"sprites": sprite_set, "interactions": interaction_set, "terminations": termination_set}
            gameDescriptions[game_name] = game
    
    
    # to figure out how many tokens we will embed
    tokens = []
    sprite_names = []
    

    for game_file in gameDescriptions:
        
        # first identify all sprite names
        sprite_names = []
        for idx, sprite_info in enumerate(gameDescriptions[game_file]['sprites']):
            for field in sprite_info:
                if field == "name":
                    sprite_names.append(sprite_info[field])
                
        # sprite set info
        for idx, sprite_info in enumerate(gameDescriptions[game_file]['sprites']):
            for field in sprite_info:
                # we do not care about the names of objects in the description file
                if field == "name":
                    continue
                if field not in tokens and field not in sprite_names:
                    tokens.append(field)
                value = sprite_info[field]
                if value not in tokens and value not in sprite_names:
                    tokens.append(value)
                    
        # interaction set info
        for info in gameDescriptions[game_file]['interactions']:
            for field in info:
                if field is not "parameters":
                    if field not in tokens and field not in sprite_names:
                        tokens.append(field)
                    if info[field] not in tokens and info[field] not in sprite_names:
                        tokens.append(info[field])
                else:
                    for subfield in info[field]:
                        if subfield not in tokens and subfield not in sprite_names:
                            tokens.append(subfield)
                        if info[field][subfield] not in tokens and info[field][subfield] not in sprite_names:
                            tokens.append(info[field][subfield])
        
        # interaction set info
        for info in gameDescriptions[game_file]['terminations']:
            for field in info:
                if field not in tokens:
                    tokens.append(field)
                if info[field] not in tokens and info[field] not in sprite_names:
                    tokens.append(info[field])
                    
    return gameDescriptions, tokens


# In[17]:


path = "game_files"
all_theories, all_tokens = identify_tokens(path)


# In[20]:


print all_theories


# In[ ]:





# In[ ]:





# In[ ]:





# In[18]:


# let's assume that the maximum number of items to be combined for a game theory is 100
tokens_total = len(all_tokens)
dimension = dim(100, tokens_total, 0.05)
print(dimension)


# In[792]:


def subject_embeddings(tokens, total, dim):
    # should now do this once per subject
    embedding_dictionary = {} 
    embeddings = embedding_initializations(int(total), int(dim))
    for idx, token in enumerate(tokens):
        embedding_dictionary[token] = embeddings[idx]
    return embedding_dictionary


# In[895]:


def subject_game_embeddings(embeddings, theories, dim):
    
    all_games = {}
    all_sprites = {}
    
    for game in theories:
        print(game)
        game_embedding = np.zeros(dim)
        sprite_set = theories[game]['sprites']
        interaction_set = theories[game]['interactions']
        termination_set = theories[game]['terminations']
    
        sprite_embeddings = {}
        
        sprite_names = []
        embedded_sprites = []
        stype_sprites = {}
        nonstype_sprites = []
        
        # first embed non-stype sprites: base vectors should have an expected length of 1
        for sprite_info in sprite_set:
            sprite_name = sprite_info['name']
            sprite_embedding = np.zeros(dimension)
            s = False
            for field in sprite_info:
                if 'stype' in field:
                    s = True
            if s:
                continue
            else:
                for field in sprite_info:
                    if field == 'name':
                        continue
                    else:
                        feature_embedding = encode(embeddings[field], embeddings[sprite_info[field]])
                        sprite_embedding = np.add(sprite_embedding, feature_embedding)
            sprite_embedding = sprite_embedding / np.sqrt(np.sum(np.square(sprite_embedding)))
            embedded_sprites.append(sprite_name)
            sprite_embeddings[sprite_name] = sprite_embedding
            if sprite_name not in all_sprites:
                all_sprites[sprite_name] = sprite_embedding
            
        # then let's deal with stype sprites whose stype arguments are already embedded: base vectors should have an expected length of 1
        for sprite_info in sprite_set:
            sprite_name = sprite_info['name']
            sprite_embedding = np.zeros(dimension)
            if sprite_name in embedded_sprites:
                continue
            s = None
            for field in sprite_info:
                if 'stype' in field:
                    s = field
            if sprite_info[s] not in embedded_sprites:
                continue
            else:
                for field in sprite_info:
                    if field == 'name':
                        continue
                    elif 'stype' in field:
                        feature_embedding = encode(embeddings[field], sprite_embeddings[sprite_info[field]])
                        sprite_embedding = np.add(sprite_embedding, feature_embedding)
                    else:
                        feature_embedding = encode(embeddings[field], embeddings[sprite_info[field]])
                        sprite_embedding = np.add(sprite_embedding, feature_embedding)
            sprite_embedding = sprite_embedding / np.sqrt(np.sum(np.square(sprite_embedding)))
            embedded_sprites.append(sprite_name)
            sprite_embeddings[sprite_name] = sprite_embedding
            if sprite_name not in all_sprites:
                all_sprites[sprite_name] = sprite_embedding
            
        # the remaining stype sprites: base vectors should have an expected length of 1
        for sprite_info in sprite_set:
            sprite_name = sprite_info['name']
            sprite_embedding = np.zeros(dimension)
            if sprite_name in embedded_sprites:
                continue
            s = None
            for field in sprite_info:
                if 'stype' in field:
                    s = field
            if sprite_info[s] not in embedded_sprites:
                print(s)
                print(sprite_info[s])
                print("????")
            else:
                for field in sprite_info:
                    if field == 'name':
                        continue
                    elif 'stype' in field:
                        feature_embedding = encode(embeddings[field], sprite_embeddings[sprite_info[field]])
                        sprite_embedding = np.add(sprite_embedding, feature_embedding)
                    else:
                        feature_embedding = encode(embeddings[field], embeddings[sprite_info[field]])
                        sprite_embedding = np.add(sprite_embedding, feature_embedding)
            sprite_embedding = sprite_embedding / np.sqrt(np.sum(np.square(sprite_embedding)))
            embedded_sprites.append(sprite_name)
            sprite_embeddings[sprite_name] = sprite_embedding
            if sprite_name not in all_sprites:
                all_sprites[sprite_name] = sprite_embedding
            
        for sprite in sprite_embeddings:
            game_embedding = np.add(game_embedding, sprite_embeddings[sprite])
        
        #print(sprite_embeddings)
        for interaction_info in interaction_set:
            interaction_embedding = np.zeros(dim)
            for field in interaction_info:
                if field is not "parameters":
                    if field not in embeddings or (interaction_info[field] not in embeddings and interaction_info[field] not in sprite_embeddings):
                        print("{}, {}".format(field, interaction_info[field]))
                    if 'agent' in field or 'patient' in field:
                        embedding = encode(embeddings[field], sprite_embeddings[interaction_info[field]])
                        interaction_embedding = np.add(interaction_embedding, embedding)
                    else:
                        embedding = encode(embeddings[field], embeddings[interaction_info[field]])
                        interaction_embedding = np.add(interaction_embedding, embedding)
                else:
                    for subfield in interaction_info[field]:
                        if interaction_info[field][subfield] in embedded_sprites:
                            embedding = encode(embeddings[subfield], sprite_embeddings[interaction_info[field][subfield]])
                            interaction_embedding = np.add(interaction_embedding, embedding)
                        else:
                            embedding = encode(embeddings[subfield], embeddings[interaction_info[field][subfield]])
                            interaction_embedding = np.add(interaction_embedding, embedding)
            game_embedding = np.add(game_embedding, interaction_embedding)
        
        for termination_info in termination_set:
            termination_embedding = np.zeros(dim)
            for field in termination_info:
                if 'stype' in field:
                    embedding = encode(embeddings[field], sprite_embeddings[termination_info[field]])
                    termination_embedding = np.add(termination_embedding, embedding)
                else:
                    embedding = encode(embeddings[field], embeddings[termination_info[field]])
                    termination_embedding = np.add(termination_embedding, embedding)
            game_embedding = np.add(game_embedding, termination_embedding)
                
        all_games[game] = game_embedding
    return all_games, all_sprites


# # HRR Similarity Matrix

# In[899]:


all_games = []
for game in all_theories:
    all_games.append(game)
print(all_games)


# In[958]:


subject_embedding_dict = subject_embeddings(all_tokens, tokens_total, dimension)
subject_game_embeddings_dict, sprites = subject_game_embeddings(subject_embedding_dict, all_theories, dimension)


# In[959]:


def decoding_test(token_embeddings, game_embeddings, theories):
    # rank 5
    count = 0
    correct = 0
    
    for game in theories:
        game_embedding = game_embeddings[game]
        theory = theories[game]
        sprites = theory["sprites"]
        interactions = theory["interactions"]
        for sprite in sprites:
            for field in sprite:
                if field == "name":
                    continue
                    
                # decode value
                field_embedding = token_embeddings[field]
                decoded = decode(field_embedding, game_embedding)
                target = sprite[field]
                target_rank = []
                for token in token_embeddings:
                    if token == field:
                        continue
                    else:
                        token_v = token_embeddings[token].reshape(1, -1)
                        decoded_v = decoded.reshape(1, -1)
                        sim = k.cosine_similarity(token_v, decoded_v)
                        target_rank.append((token, sim))
                ranked = sorted(target_rank, key=lambda tup: tup[1], reverse=True)
                for i in range(5):
                    if ranked[i][0] == target:
                        correct += 1
                count += 1
                
                # decode field
                value = sprite[field]
                value_embedding = token_embeddings[value]
                decoded = decode(value_embedding, game_embedding)
                target = field
                target_rank = []
                for token in token_embeddings:
                    if token == value:
                        continue
                    else:
                        token_v = token_embeddings[token].reshape(1, -1)
                        decoded_v = decoded.reshape(1, -1)
                        sim = k.cosine_similarity(token_v, decoded_v)
                        target_rank.append((token, sim))
                ranked = sorted(target_rank, key=lambda tup: tup[1], reverse=True)
                for i in range(5):
                    if ranked[i][0] == target:
                        correct += 1
                count += 1
                
        for interaction in interactions:
            for field in interaction:
                if field == "parameters":
                    for field in interaction["parameters"]:
                        field_embedding = token_embeddings[field]
                        decoded = decode(field_embedding, game_embedding)
                        target = interaction["parameters"][field]
                        target_rank = []
                        for token in token_embeddings:
                            if token == field:
                                continue
                            else:
                                token_v = token_embeddings[token].reshape(1, -1)
                                decoded_v = decoded.reshape(1, -1)
                                sim = k.cosine_similarity(token_v, decoded_v)
                                target_rank.append((token, sim))
                        ranked = sorted(target_rank, key=lambda tup: tup[1], reverse=True)
                        for i in range(5):
                            if ranked[i][0] == target:
                                correct += 1
                        count += 1
                
                        # decode field
                        value = interaction["parameters"][field]
                        value_embedding = token_embeddings[value]
                        decoded = decode(value_embedding, game_embedding)
                        target = field
                        target_rank = []
                        for token in token_embeddings:
                            if token == value:
                                continue
                            else:
                                token_v = token_embeddings[token].reshape(1, -1)
                                decoded_v = decoded.reshape(1, -1)
                                sim = k.cosine_similarity(token_v, decoded_v)
                                target_rank.append((token, sim))
                        ranked = sorted(target_rank, key=lambda tup: tup[1], reverse=True)
                        for i in range(5):
                            if ranked[i][0] == target:
                                correct += 1
                        count += 1
                else:
                    field_embedding = token_embeddings[field]
                    decoded = decode(field_embedding, game_embedding)
                    target = interaction[field]
                    target_rank = []
                    for token in token_embeddings:
                        if token == field:
                            continue
                        else:
                            token_v = token_embeddings[token].reshape(1, -1)
                            decoded_v = decoded.reshape(1, -1)
                            sim = k.cosine_similarity(token_v, decoded_v)
                            target_rank.append((token, sim))
                    ranked = sorted(target_rank, key=lambda tup: tup[1], reverse=True)
                    for i in range(5):
                        if ranked[i][0] == target:
                            correct += 1
                    count += 1
                
                    # decode field
                    value = interaction[field]
                    value_embedding = token_embeddings[value]
                    decoded = decode(value_embedding, game_embedding)
                    target = field
                    target_rank = []
                    for token in token_embeddings:
                        if token == value:
                            continue
                        else:
                            token_v = token_embeddings[token].reshape(1, -1)
                            decoded_v = decoded.reshape(1, -1)
                            sim = k.cosine_similarity(token_v, decoded_v)
                            target_rank.append((token, sim))
                    ranked = sorted(target_rank, key=lambda tup: tup[1], reverse=True)
                    for i in range(5):
                        if ranked[i][0] == target:
                            correct += 1
                    count += 1
                
        
    return correct, count


# In[960]:


for sprite in sprites:
    if sprite not in subject_embedding_dict:
        subject_embedding_dict[sprite] = sprites[sprite]


# In[961]:


full_tokens_dict = subject_embedding_dict
correctN, countN = decoding_test(full_tokens_dict, subject_game_embeddings_dict, all_theories)


# In[962]:


print("{} {}".format(correctN, countN))


# ## Main loop: embeddings for 100 "subjects"

# In[759]:


import sklearn.metrics.pairwise as k

# 100 embedding initializations across subjects
diagonal_size = (len(all_games)*len(all_games)-len(all_games))/2
subjects_HRR_similarity = []
for i in range(100):
    #if i > 1:
    #    break
    subject_HRR_similarity = []
    subject_embedding_dict = subject_embeddings(all_tokens, tokens_total, dimension)
    subject_game_embeddings_dict = subject_game_embeddings(subject_embedding_dict, all_theories, dimension)
    # print(decoding_test(subject_game_embeddings_dict))
    for i in range(0, len(all_games)-1):
        game1 = all_games[i]
        e1 = subject_game_embeddings_dict[game1].reshape(1, -1)
        e1 = e1 / np.sqrt(np.sum(np.square(e1)))
        for j in range(i+1, len(all_games)):
            game2 = all_games[j]
            e2 = subject_game_embeddings_dict[game2].reshape(1, -1)
            e2 = e2 / np.sqrt(np.sum(np.square(e2)))
            subject_HRR_similarity.append(k.cosine_similarity(e1, e2))
    subject_HRR_similarity = np.asarray(subject_HRR_similarity)
    subjects_HRR_similarity.append(subject_HRR_similarity)


# In[826]:


game_pairs = []
for i in range(0, len(all_games)-1):
    game1 = all_games[i]
    for j in range(i+1, len(all_games)):
        game2 = all_games[j]
        game_pair = (game1, game2)
        if game_pair not in game_pairs:
            game_pairs.append(game_pair)


# In[827]:


print(len(game_pairs))


# In[828]:


HRR = []
for subject in subjects_HRR_similarity:
    subject_vector = []
    for sim in subject:
        subject_vector.append(sim[0][0])
    HRR.append(subject_vector)
HRR = np.asarray(HRR)


# In[970]:


pair_similarities = [[] for i in range(len(HRR[0]))]

for i in range(len(HRR)):
    for j in range(len(HRR[i])):
        pair_similarities[j].append(HRR[i][j])
        
average_similarities = []

for i, pair in enumerate(game_pairs):
    game1 = pair[0]
    game2 = pair[1]
    print("{}, similarity mean: {}, similarity std: {}".format(pair, np.mean(pair_similarities[i]), np.std(pair_similarities[i])))
    print("")
    average_similarities.append((game1, game2, np.mean(pair_similarities[i])))


# In[853]:


# this is what you want to you use for HRR
len(average_similarities)


# # Compute similarity matrices of behavioral data

# In[846]:


memory = "memory.csv"
similarity = "similarity.csv"


# In[847]:


keys = None
csv_reader = None
subjects_correct = {}
with open(memory, mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        subject = row['subject']
        if subject not in subjects_correct:
            subjects_correct[subject] = []
        correct_list = row['correct responses']
        correct_dict = {}
        full_list = correct_list.split(",")
        for i in range(6):
            real = full_list[i*2]
            real_name = " ".join(real.split("_")[1:])
            fake = full_list[i*2+1]
            correct_dict[real_name] = fake
        if row['response'] == correct_dict[row['game']]:
            subjects_correct[subject].append(1)
        else:
            subjects_correct[subject].append(0)


# In[848]:


filtered_subjects = []
for subject in subjects_correct:
    if np.sum(subjects_correct[subject]) > 1:
        filtered_subjects.append(subject)


# In[849]:


similarity_dict = {}
with open(similarity, mode='r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        if row['subject'] in filtered_subjects:
            
            game1 = row['game1']
            game2 = row['game2']
            
            if game1 not in similarity_dict:
                similarity_dict[game1] = {}
            if game2 not in similarity_dict[game1]:
                similarity_dict[game1][game2] = {}
                similarity_dict[game1][game2]['visual'] = []
                similarity_dict[game1][game2]['goal'] = []
                similarity_dict[game1][game2]['rule'] = []
                similarity_dict[game1][game2]['difficulty'] = []
                
            if game2 not in similarity_dict:
                similarity_dict[game2] = {}
            if game1 not in similarity_dict[game2]:
                similarity_dict[game2][game1] = {}
                similarity_dict[game2][game1]['visual'] = []
                similarity_dict[game2][game1]['goal'] = []
                similarity_dict[game2][game1]['rule'] = []
                similarity_dict[game2][game1]['difficulty'] = []
                
            rule = float(row['rule']) 
            goal = float(row['goal']) 
            difficulty = float(row['difficulty']) 
            visual = float(row['visual']) 
            
            similarity_dict[game1][game2]['visual'].append(visual)
            similarity_dict[game1][game2]['goal'].append(goal)
            similarity_dict[game1][game2]['rule'].append(rule)
            similarity_dict[game1][game2]['difficulty'].append(difficulty)
            
            similarity_dict[game2][game1]['visual'].append(visual)
            similarity_dict[game2][game1]['goal'].append(goal)
            similarity_dict[game2][game1]['rule'].append(rule)
            similarity_dict[game2][game1]['difficulty'].append(difficulty)


# In[850]:


game_vectors = {}
for game1 in similarity_dict:
    if game1 not in game_vectors:
        
        game_vectors[game1] = {}
        game_vectors[game1]['visual'] = [] 
        game_vectors[game1]['goal'] = []
        game_vectors[game1]['rule'] = [] 
        game_vectors[game1]['difficulty'] = []
        
        
    for game2 in similarity_dict[game1]:
        
        group_visual = np.mean(similarity_dict[game1][game2]['visual'])
        group_goal = np.mean(similarity_dict[game1][game2]['goal'])
        group_rule = np.mean(similarity_dict[game1][game2]['rule'])
        group_difficulty = np.mean(similarity_dict[game1][game2]['difficulty'])
        
        game_vectors[game1]['visual'].append(group_visual)
        game_vectors[game1]['goal'].append(group_goal)
        game_vectors[game1]['rule'].append(group_rule)
        game_vectors[game1]['difficulty'].append(group_difficulty)


# In[851]:


pairwise_similarities = {}
for game1 in similarity_dict:
    if game1 not in pairwise_similarities:
        pairwise_similarities[game1] = {}
    for game2 in similarity_dict[game1]:
        if game2 not in pairwise_similarities[game1]:
            pairwise_similarities[game1][game2] = {"difficulty": None,
                                                  "visual": None,
                                                  "goal": None,
                                                  "rule": None}
        pairwise_similarities[game1][game2]["visual"] = np.mean(similarity_dict[game1][game2]["visual"])
        pairwise_similarities[game1][game2]["goal"] = np.mean(similarity_dict[game1][game2]["goal"])
        pairwise_similarities[game1][game2]["rule"] = np.mean(similarity_dict[game1][game2]["rule"])
        pairwise_similarities[game1][game2]["difficulty"] = np.mean(similarity_dict[game1][game2]["difficulty"])


# In[852]:


pairwise_similarities.keys()


# In[862]:


HRR_similarities = average_similarities


# In[859]:


visual = []
goal = []
rule = []
difficulty = []
    
# now generate similarity vectors for each subset, vector length = 66 (size of one half of the full similarity matrix excluding the diagonal)
for i in range(len(average_similarities)):
    game1 = average_similarities[i][0]
    game1_real = game1
    game2 = average_similarities[i][1]
    game2_real = game2
    if game2_real == "myAliens":
        game2 = "myaliens"
    if game1_real == "myAliens":
        game1 = "myaliens"
    if game2_real == "plaqueattack":
        game2 = "plaqueAttack"
    if game1_real == "plaqueattack":
        game1 = "plaqueAttack"
    visual.append((game1_real, game2_real, pairwise_similarities[game1][game2]['visual']/10.0))
    goal.append((game1_real, game2_real, pairwise_similarities[game1][game2]['goal']/10.0))
    rule.append((game1_real, game2_real, pairwise_similarities[game1][game2]['rule']/10.0))
    difficulty.append((game1_real, game2_real, pairwise_similarities[game1][game2]['difficulty']/10.0))


# In[1]:


#HRR_similarities


# In[875]:


visual_v = []
goal_v = []
rule_v = []
difficulty_v = []
HRR_v = []

for i, info in enumerate(HRR_similarities):
    visual_v.append(visual[i][2])
    goal_v.append(goal[i][2])
    rule_v.append(rule[i][2])
    difficulty_v.append(difficulty[i][2])
    HRR_v.append(HRR_similarities[i][2])


# In[971]:


print("HRR-visual:{}".format(scipy.stats.spearmanr(HRR_v, visual_v)))
print("")
print("HRR-goal:{}".format(scipy.stats.spearmanr(HRR_v, goal_v)))
print("")
print("HRR-rule:{}".format(scipy.stats.spearmanr(HRR_v, rule_v)))
print("")
print("HRR-difficulty:{}".format(scipy.stats.spearmanr(HRR_v, difficulty_v)))
print("")
print("visual-goal:{}".format(scipy.stats.spearmanr(visual_v, goal_v)))
print("")
print("visual-rule:{}".format(scipy.stats.spearmanr(visual_v, rule_v)))
print("")
print("visual-difficulty:{}".format(scipy.stats.spearmanr(visual_v, difficulty_v)))
print("")
print("goal-rule:{}".format(scipy.stats.spearmanr(goal_v, rule_v)))
print("")
print("goal-difficulty:{}".format(scipy.stats.spearmanr(goal_v, difficulty_v)))
print("")
print("rule-difficulty:{}".format(scipy.stats.spearmanr(rule_v, difficulty_v)))
print("")


# In[967]:


Y = np.array(rule_v)
X = np.array([HRR_v,visual_v,goal_v, difficulty_v])
X = X.T # transpose so input vectors are along the rows
X = np.c_[X, np.ones(X.shape[0])] # add bias term
w = np.linalg.lstsq(X,Y, rcond=True)[0]
print("rule = {}*{} + {}*{} + {}*{} + {}*{} + {}".format(w[0], "HRR", w[1], "visual", w[2], "goal", w[3], "difficulty", w[4]))


# ## Old code

# In[302]:


import matplotlib.pyplot as plt
 
labels = []
for label in game_embeddings.keys():
    labels.append(label)
 
plt.figure(dpi=800, figsize=(8, 8))
fig, ax = plt.subplots(figsize=(20,20))
cax = ax.matshow(similarity_matrix, interpolation='nearest')
ax.grid(True)
plt.title('Game Embeddings Similarity Matrix')
plt.xticks(range(len(labels)), labels, rotation=90);
plt.yticks(range(len(labels)), labels);
fig.colorbar(cax, ticks=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, .75,.8,.85,.90,.95,1])
plt.show()


# In[17]:


def read_gameStates(stateSeries):
    eventSeries = []
    for state in stateSeries:
        events = {}
        # identify sprites
        # identify interactions
        # structure: events{interaction} = list(tuples) : 
        # each tuple (sub, obj) that participated in the event
        gameStates.append(stateInfo)
    return gameStates


# In[22]:


fake_game_state = """
wwwww
w.a.w
we..w
wr..w
wwwww
"""


# In[18]:


# test

sub1 = embedding_dict['collide_subject']
obj1 = embedding_dict['collide_object']
event1 = embedding_dict['collide_event']
sub2 = embedding_dict['killSprite_subject']
obj2 = embedding_dict['killSprite_object']
event2 = embedding_dict['killSprite_event']
enemy = embedding_dict["enemy"]
avatar = embedding_dict["avatar"]
resource = embedding_dict["resource"]
wall = embedding_dict["wall"]

fake_embedding = cconv(avatar, sub1) + cconv(wall, obj1) + event1 + cconv(enemy, sub2) + cconv(resource, obj2) + event2
print(fake_embedding)


# In[19]:


distances = []
correct_pairs = [['avatar', 'collide_subject'], 
                 ['wall', 'collide_object'], 
                 ['enemy', 'killSprite_subject'], 
                 ['resource', 'killSprite_object']]

for pair in correct_pairs:
    decoded_list = []
    for entity in embedding_dict:
        sprite = embedding_dict[pair[0]]
        decoded = ccorr(sprite, fake_embedding)
        difference = euclidean_distance(decoded,embedding_dict[entity])
        decoded_list.append(tuple((difference, entity)))
    sorted_list = sorted(decoded_list, key=lambda tup: tup[0])[:5]
    print("{} {}".format(pair[1], sorted_list))


# In[18]:


import json

def retrieve_states(filename):
    json_file = open(filename, 'rb')
    mydict = json.load(json_file)
    json_file.close()
    #print mydict
    statesList = []
    for idx, dictState in enumerate(mydict):
        statesList.append(dictState)
    return statesList


# In[19]:


fname = "stateFiles/Aug7th_testing"
actual_states = retrieve_states(fname)


# In[20]:


object_dict = {}
states = actual_states[1]["gvgai_chopper_0_6_5"]

for state in states:
    for key in state["objects"]:
        for instance in state['objects'][key]:
            object_dict[instance] = key
object_dict["-1"] = 'EOS'


# In[21]:


print(object_dict)


# In[22]:


event_list = []
for frame, state in enumerate(actual_states[1]["gvgai_chopper_0_6_5"]):
    if state["events"] == []:
        continue
    event_list.append(state["events"])


# In[23]:


print(event_list)


# In[24]:


for gameStateEvents in event_list:
    for event in gameStateEvents:
        print("{} {} {}".format(event[0], object_dict[str(event[1])], object_dict[str(event[2])]))


# In[25]:


gameStateEmbeddings = {}

for idx, gameStateEvents in enumerate(event_list):
    gameStateEmbeddings[idx] = {}
    gameStateEmbeddings[idx]["query_tuples"] = []
    
    stateEmbedding = None
    for gameStateEvent in gameStateEvents:
        subj = object_dict[str(gameStateEvent[2])]
        obj = object_dict[str(gameStateEvent[1])]
        
        event = gameStateEvent[0]
        
        gameStateEmbeddings[idx]["query_tuples"].append(tuple((subj, event + "_subject")))
        gameStateEmbeddings[idx]["query_tuples"].append(tuple((obj, event + "_object")))

        subj = embedding_dict[subj]
        obj = embedding_dict[obj]
        event_subject = embedding_dict[event + "_subject"]
        event_object = embedding_dict[event + "_object"]
        event = embedding_dict[event + "_event"]
        
        #print("{} {} {} {} {}".format(subj_embedding,obj_embedding,event_subject,event_object, event_embedding))
        if stateEmbedding is None:
            stateEmbedding = cconv(subj, event_subject) + cconv(obj, event_object) + event
        else:
            stateEmbedding = stateEmbedding + cconv(subj, event_subject) + cconv(obj, event_object) + event
    
    gameStateEmbeddings[idx]["state_embedding"] = stateEmbedding


# In[26]:


print(gameStateEmbeddings)


# In[27]:


entity_size = len(entity_keys)


# In[31]:


rank_accuracies = []

for index, frame in enumerate(gameStateEmbeddings):
    gameStateInfo = gameStateEmbeddings[frame]
    state_embedding = gameStateInfo["state_embedding"]
    correct_pairs = gameStateInfo["query_tuples"]

    frame_accuracy = []
    for pair in correct_pairs:
        decoded_list = []
        for entity in embedding_dict:
            sprite = embedding_dict[pair[1]]
            decoded = ccorr(sprite, state_embedding)
            difference = euclidean_distance(decoded,embedding_dict[entity])
            decoded_list.append(tuple((difference, entity)))
        #sorted_list = sorted(decoded_list, key=lambda tup: tup[0])[:5]
        sorted_list = sorted(decoded_list, key=lambda tup: tup[0])
        ranked_list = []
        for item in sorted_list:
            ranked_list.append(item[1])
        rank_accuracy = float((entity_size - ranked_list.index(pair[0]))) / float(entity_size)
        frame_accuracy.append(rank_accuracy)
        rank_accuracies.append(rank_accuracy)
    print("accuracy at frame {}: {}".format(index, float(sum(frame_accuracy)/len(frame_accuracy))))
    
    
overall_accuracy = sum(rank_accuracies) / float(len(rank_accuracies))


# In[32]:


print(overall_accuracy)


# In[ ]:




