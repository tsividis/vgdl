from rlenvironmentnonstatic import createRLInputGame, createRLInputGameFromStrings, defInputGame, createMindEnv
from EMPA import Agent
from games_to_hyperparameters import *
import time
import os
import pygame
import json
from IPython import embed
import importlib
import uuid
import copy
from collections import defaultdict, OrderedDict
import cPickle, os, random
import numpy as np

random.seed(42)
np.random.seed(42)

hyperparameter_sets = [
    {'idx'           : 0,
     'short_horizon' : False,
     'first_order_horizon': True,
     'sprite_first_alpha': 10000,
     'sprite_second_alpha': 100,
     'sprite_negative_mult': .1,
     'multisprite_first_alpha': 10000,
     'multisprite_second_alpha': 100,
     'novelty_first_alpha': 5000,
     'novelty_second_alpha': 50,
     },
    {'idx'           : 1,
     'short_horizon' : False,
     'first_order_horizon': False,
     'sprite_first_alpha': 10000,
     'sprite_second_alpha': 100,
     'sprite_negative_mult': 10.,
     'multisprite_first_alpha': 10000,
     'multisprite_second_alpha': 100,
     'novelty_first_alpha': 5000,
     'novelty_second_alpha': 50,
     },
    {'idx'           : 2,
     'short_horizon' : False,
     'first_order_horizon': False,
     'sprite_first_alpha': 10000,
     'sprite_second_alpha': 100,
     'sprite_negative_mult': .1,
     'multisprite_first_alpha': 10000,
     'multisprite_second_alpha': 100,
     'novelty_first_alpha': 5000,
     'novelty_second_alpha': 50,
     },
    {'idx'           : 3,
     'short_horizon' : True,
     'first_order_horizon': True,
     'sprite_first_alpha': 10000,
     'sprite_second_alpha': 100,
     'sprite_negative_mult': 10, #normally .1
     'multisprite_first_alpha': 10000,
     'multisprite_second_alpha': 100,
     'novelty_first_alpha': 5000,
     'novelty_second_alpha': 50,
     },
    {'idx'           : 4,
     'short_horizon' : True,
     'first_order_horizon': True,
     'sprite_first_alpha': 10000,
     'sprite_second_alpha': 100,
     'sprite_negative_mult': .1, #normally .1
     'multisprite_first_alpha': 10000,
     'multisprite_second_alpha': 100,
     'novelty_first_alpha': 5000,
     'novelty_second_alpha': 10,
     }
]

def retrieve_states(filename):
    '''retrieve game states info from data file'''
    '''each data file is a list of dictionaries'''
    json_file = open(filename, 'rb')
    mydict = json.load(json_file)
    json_file.close()
    #print mydict
    statesList = []
    for idx, dictState in enumerate(mydict):
        statesList.append(dictState)
    return statesList

def gen_color():
    from vgdl.colors import colorDict
    color_list = colorDict.values()
    color_list = [c for c in color_list if c not in ['UUWSWF']]
    for color in color_list:
        yield color

def read_gvgai_game(filename):
    with open(filename, 'r') as f:
        new_doc = []
        g = gen_color()
        for line in f.readlines():
            #new_line = (" ".join([string if string[:4]!="img=" else "color={}".format(next(g)) for string in line.split(" ")]))
            new_line = (" ".join([string for string in line.split(" ")]))
            new_doc.append(new_line)
        new_doc = "\n".join(new_doc)
    return new_doc

def initialize_agent(gameFileString, game_name, game_level, movie_name, agent=None):
    start = time.time()

    if game_name in ['antagonist', 'helper', 'explore/exploit', 'ee', 'preconditions', 'push_boulders', 'relational']:
        game_name = 'expt_'+game_name

    game_levels = [l for l in os.listdir(gameFileString) if l[0:len(game_name+'_lvl')] == game_name+'_lvl']

    if "{}.txt".format(game_name) in os.listdir(gameFileString):
        gvgname = "./{}/{}".format(gameFileString, game_name)
        game_description = read_gvgai_game('{}.txt'.format(gvgname))
        game_descriptions = [game_description]*len(game_levels)
    else:
        game_descriptions = [read_gvgai_game("./{}/{}".format(gameFileString, d)) for d in os.listdir(gameFileString) if (game_name in d and 'desc' in d)]
    # embed()


    level_game_pairs = []
    gvgname = "./{}/{}".format(gameFileString, game_name)
    for level_number in range(len(game_levels)):
        with open('{}_lvl{}.txt'.format(gvgname, level_number), 'r') as level:
            level_game_pairs.append([game_descriptions[level_number], level.read()])
    print(game_level)
    print("level_game_pairs length {}".format(len(level_game_pairs)))

    if agent==None:
        print "no agent yet; initializing from scratch"
        try:
            agent = Agent('full', game_name, hyperparameter_sets=hyperparameter_sets, hyperparameter_index=0, movieName=movie_name)

        except:
            print("problem initializing agent for {}. Probably filename needs to have 'expt' appened to it".format(game_name))
            embed()
    else:
        print "not initializing new agent -- just setting game desc and level strings"
    (agent.gameString, agent.levelString) = level_game_pairs[game_level]
    print agent.gameString
    agent.initializeEnvironment()
    end = time.time()
    print("Initialize agent (Time elapsed): {}".format(end - start))
    return agent

def find_max(rle, gameState):
    start = time.time()
    spritesInfo = gameState['objects']
    
    # find max rle x,y
    rle_max_x = 0
    rle_max_y = 0
    for stype in rle._game.sprite_groups:
        for instance in rle._game.sprite_groups[stype]:
            if int(instance.rect.top) > rle_max_y:
                rle_max_y = int(instance.rect.top)
            if int(instance.rect.left) > rle_max_x:
                rle_max_x = int(instance.rect.left)

    # find max rle x,y
    game_max_x = 0
    game_max_y = 0
    for stype in spritesInfo:
        for instance in spritesInfo[stype]:
            if int(spritesInfo[stype][instance]['y']) > game_max_y:
                game_max_y = int(spritesInfo[stype][instance]['y'])
            if int(spritesInfo[stype][instance]['x']) > game_max_x:
                game_max_x = int(spritesInfo[stype][instance]['x'])
    end = time.time()
    print("Find max (Time elapsed): {}".format(end - start))
    return rle_max_x, rle_max_y, game_max_x, game_max_y

def find_block_size(gameState):
    spritesInfo = gameState['objects']
    
    # find nonzero min x,y
    game_min_x = 100000
    game_min_y = 100000
    for stype in spritesInfo:
        for instance in spritesInfo[stype]:
            if int(spritesInfo[stype][instance]['y']) !=0 and int(spritesInfo[stype][instance]['y']) < game_min_y:
                game_min_y = int(spritesInfo[stype][instance]['y'])
            if int(spritesInfo[stype][instance]['x']) != 0 and int(spritesInfo[stype][instance]['x']) < game_min_x:
                game_min_x = int(spritesInfo[stype][instance]['x'])

    return game_min_x, game_min_y

def setGameState(rle, gameState, rle_x, game_x, rle_y, game_y):
    #start = time.time()
    spritesInfo = gameState['objects']    
    
    for key in rle._game.sprite_groups.keys():
        if key not in ['floor', 'wall', 'grass', 'highway', 'background', 'portalSlow', 'spawn', 'fastRSpawn', 'fastLSpawn',
        'slowRSpawn', 'slowLSpawn', 'mediumRSpawn', 'mediumLSpawn'] and key not in spritesInfo:
            rle._game.sprite_groups[key] = []
    for stype in spritesInfo:
        #print(stype)
        spriteInfo = spritesInfo[stype]
        instances = spriteInfo.keys()
        spriteCount = len(instances)
        if spriteCount == 0:
            rle._game.sprite_groups[stype] = []
            continue
        #rleSpriteCount = len(rle._game.sprite_groups[stype])
        rle._game.sprite_groups[stype] = []
        for i in range(0, spriteCount):
            # embed()
            # if stype in ['annoyed', 'citizen', 'george', 'quiet', 'avatar', 'cigarette']:
                # x = (  int(int(float(spriteInfo[instances[i]]['x'])/rle._game.block_size))  *rle._game.block_size  ) * float(rle_x)/float(game_x)
                # y = (  int(int(float(spriteInfo[instances[i]]['y'])/rle._game.block_size))  *rle._game.block_size  ) * float(rle_y)/float(game_y)
            # else:
            x = int(float(spriteInfo[instances[i]]['x']) * float(rle_x)/float(game_x)) 
            y = int(float(spriteInfo[instances[i]]['y']) * float(rle_y)/float(game_y))
            

            #x = int(spriteInfo[instances[i]]['x'])
            #y = int(spriteInfo[instances[i]]['y'])    
            # if stype=='log':
                # print "found log"
                # embed()
            new_sprite = rle._game._createSprite([stype], (x,y))
            if 'direction' in spriteInfo:
                new_sprite.orientation = spriteInfo['direction']
        #if stype == "avatar":
        #    print(rle._game.sprite_groups[stype])

    rle._game.score = int(gameState['score'])
    rle._game.ended = gameState['ended']
    rle._game.win = gameState['win']
    rle._game.all_objects = rle._game.getAllObjects()
    #end = time.time()
    #print("setGameState (Time elapsed): {}".format(end - start))        
    return rle

def saveModelStates(filename, organizedData):    
    '''save data into json file'''
    gameInstances = []
    for key in organizedData:
        gameInstance = {}
        newKey = '_'.join(key)
        print(newKey)
        gameInstance[newKey] = organizedData[key]
        gameInstances.append(gameInstance)
    f = open(filename, 'w')
    with open(filename, 'w') as fout:
        json.dump(gameInstances, fout) 
    f.close()

def processModelData(directory, games_to_make, modelType='EMPA'):
    allData = {}
    frameKeys = ["objects", "win", "frame", "actions", "events", "ended", "score", "real_time", "killed"]
    for folder in os.listdir(directory):
        if folder != '.DS_Store':
            modelKey = folder
            filename = modelKey
            for subfolder in os.listdir(directory + "/" + folder):
                if subfolder == '.DS_Store':
                    continue
                #if subfolder != 'avoidgeorge':
                #    continue
                #gameData = 
                #gameData[subfolder] = [] 
                for pickleFile in os.listdir(directory + "/" + folder + "/" + subfolder):
                    if pickleFile == '.DS_Store':
                        continue
                    #print(pickleFile)
                    with open(directory + "/" + folder + "/" + subfolder + "/" + pickleFile, 'r') as f:
                        gameData = cPickle.load(f)
                        if modelType=='DDQN':
                            gameData = gameData[0]
                            print(gameData['game_info'])
                            gameName = gameData['game_info']['game_name']
                        else:
                            gameName = gameData['gameInfo']['gameName']
                        #if not gameName == "frogs":
                        #    continue
                        print "attempting to make {}".format(games_to_make)
                        # print(gameName)
                        if games_to_make!='all':
                            if gameName not in games_to_make:
                                continue
                        #print("gameName is: {}".format(gameName))
                        gameTuple = gameName.split("_")
                        #if "variant" == gameTuple[0] and "expt" == gameTuple[1]:
                        #    gameName = "expt"
                        #gameName = "gvgai_avoidgeorge"
                        #gameLevel = "1"
                        #gameRound = "1"
                        if modelType=='DDQN':
                            gameString = gameData['game_info']['game_string']
                        else:
                            gameString = gameData['gameInfo']['gameString']
                        #print(gameString)
                        parsedGameString = gameString.split()
                        markers = ['InteractionSet', 'TerminationSet', 'LevelMapping']
                        
                        spriteStartIndex = None
                        spriteEndIndex = None
                        objColorDict = {}
                        
                        for idx, token in enumerate(parsedGameString):
                            if token == 'SpriteSet':
                                spriteStartIndex = idx + 1
                            if token in markers and spriteStartIndex is not None:
                                spriteEndIndex = idx
                                break
                                
                        spriteSet = parsedGameString[spriteStartIndex:spriteEndIndex]
                        print(spriteSet)
                        for idx, token in enumerate(spriteSet):
                            if token == ">":
                                obj = spriteSet[idx-1]
                                for token in spriteSet[idx+1:]:
                                    if token == ">":
                                        print(token)
                                        break
                                    parseToken = token.split("=")
                                    if len(parseToken) > 1:
                                        if parseToken[0] == "color":
                                            color = parseToken[1]
                                            objColorDict[color] = obj
                        print(objColorDict)
                                            
                        levelString = gameData['gameInfo']['levelString']
                        #print(levelString)
                        levels_played = gameData['episodes']
                        
                        gameArray = []
                        for i, episodes in enumerate(levels_played):
                            for j, episode in enumerate(episodes):
                                episodeDict = {}
                                #print("i:{}, j:{}".format(i, j))
                                gameLevel = str(i)
                                gameRound = str(j)
                                gameNumber = "1"
                                key = [gameName, gameLevel, gameNumber, gameRound]
                                key = "_".join(key)
                                frames = []
                                new_logs = {} ## key: row of log. value: first appearance in that row in a while
                                #print(episode)
                                # print "NEW EPISODE"
                                # print ""
                                # print ""
                                for frameIdx, frame in enumerate(episode):
                                    #if i == 0 and j == 1:
                                    #    print(frame)
                                    #    print("")
                                    #print(frameIdx)
                                    # if j==2 and frame['events']:
                                        # print(frame['events'])
                                        # embed()

                                    frameDict = {}
                                    objectDict = {}
                                    try:
                                        for tup in frame['objects']:
                                            sprite = str(objColorDict[tup[0]])
                                            x = tup[1][0]
                                            y = tup[1][1]
                                            resources = tup[2]
                                            spriteId = str(random.randint(1,500))
                                            if sprite not in objectDict:
                                                objectDict[sprite] = {}
                                            while spriteId in objectDict[sprite]:
                                                spriteId = str(random.randint(1,500))
                                            objectDict[sprite][spriteId] = {}
                                            objectDict[sprite][spriteId]['x'] = float(x)*40.0
                                            objectDict[sprite][spriteId]['y'] = float(y)*40.0
                                            objectDict[sprite][spriteId]['resources'] = resources
                                    except:
                                        print "failed at tup in frame['objects']"
                                        embed()
                                    
                                    # if len(frames)>0:
                                        # prevFrame = frames[-1]
                                        # embed()

                                    frameDict['objects'] = objectDict
                                    frameDict['win'] = frame['win']
                                    frameDict['frame'] = frame['timestep']
                                    frameDict['actions'] = {}
                                    frameDict['events'] = {}
                                    frameDict['ended'] = frame['ended']
                                    frameDict['score'] = frame['score']
                                    frameDict['real_time'] = frameIdx
                                    frameDict['killed'] = {}
                                    frames.append(frameDict)
                                episodeDict[key] = frames
                                gameArray.append(episodeDict)
                                
                        param_ID = gameData['modelParams']
                        allData[pickleFile] = gameArray
                        #print(param_ID)
                        #allData[]
                        #return gameArray#gameString, levelString
    return allData

def loadEMPAData(fullData):
    # populate experimentsDict that contains all model data
    experimentsDict = defaultdict(dict)
    count = 0

    for experimentID in fullData:
        #experimentID = "model"
        experimentsDict[experimentID] = defaultdict(dict)
        experimentsDict[experimentID]["gamesIndex"] = defaultdict(dict)
        experimentsDict[experimentID]["gamesData"] = defaultdict(dict)
        data = fullData[experimentID]

        for idx, dictState in enumerate(data):
            for key in dictState:
                print(key)
                jumped = False
                real_key = key            
                gameData = sorted(dictState[key], key=lambda k: k['frame'])
                tup = real_key.split("_")
                gameName =  "_".join(tup[:-3])
                gameLevel = tup[-3]
                gameNumber = tup[-2]
                gameRound = tup[-1]
                
                # store game indices
                experimentsDict[experimentID]["gamesIndex"][gameNumber] = gameName
                
                # store game data
                if gameName not in experimentsDict[experimentID]["gamesData"]:
                    experimentsDict[experimentID]["gamesData"][gameName] = defaultdict(dict)
                
                if gameLevel not in experimentsDict[experimentID]["gamesData"][gameName]:
                    experimentsDict[experimentID]["gamesData"][gameName][gameLevel] = defaultdict(dict)
                experimentsDict[experimentID]["gamesData"][gameName][gameLevel][gameRound] = gameData
            
        # print(experimentsDict[experimentID]["gamesIndex"])
    return experimentsDict

def makeEMPAMovies(experimentsDict):
    # make movies for model data
    hyperparameter_index = 0
    secondPhaseStart = False
    startLabel = None
    for ID in experimentsDict:
            experimentIndices = experimentsDict[ID]['gamesIndex']
            experimentData = experimentsDict[ID]['gamesData']
            games = []
            for gameNumber in sorted(experimentIndices.keys()):
                group = None
                VGDLgameName = experimentIndices[gameNumber]            
                gameName = VGDLgameName
                games.append(gameName)
                
                gameFile = "all_games_with_sprites"
                # print(gameName)
                gameData = experimentData[VGDLgameName]
                levels_won = 0
                group = 5
                agent = None
                for gameLevel in sorted(gameData.keys()):
                    #print(gameLevel)
                    levelData = gameData[gameLevel]
                    for gameRound in sorted(levelData.keys()):
                        frames = levelData[gameRound]
                        # gameFileString, game_name, game_level, movie_name
                        agent = initialize_agent(gameFile, gameName, int(gameLevel), "_".join([ID, VGDLgameName, gameNumber, gameLevel, gameRound]), agent=agent)

                        rle_max_x, rle_max_y, game_max_x, game_max_y = find_max(agent.rle, frames[0])

                        if 'aliens' in gameName:
                            ## use game_max_x to find where the bottom-left hidden object would have been in the original screen
                            ## insert it there at every frame before rendering.
                            game_min_x, game_min_y = find_block_size(frames[0])
                        
                            game_max_x = game_min_x*29 ## this is rightmost block
                            game_max_y = game_min_y*10 ## bottommost block

                            new_sprite = agent.rle._game._createSprite(['portalSlow'], (1050,300))


                        for i in range(0, 7):
                            if 'aliens' in gameName:
                                frames[0]['objects']['portalSlow'] = {'5000':{'resources':{}, 'x':game_max_x, 'y':game_max_y}}
                            agent.rle = setGameState(agent.rle, frames[0], rle_max_x, game_max_x, rle_max_y, game_max_y)
                            agent.statesEncountered.append(agent.rle._game.getFullState())
                        for frame in frames[1:-1]:
                            if 'aliens' in gameName:
                                frame['objects']['portalSlow'] = {'5000':{'resources':{}, 'x':game_max_x, 'y':game_max_y}}
                            agent.rle = setGameState(agent.rle, frame, rle_max_x, game_max_x, rle_max_y, game_max_y)
                            agent.statesEncountered.append(agent.rle._game.getFullState())
                        for i in range(0, 7):
                            if 'aliens' in gameName:
                                frames[-1]['objects']['portalSlow'] = {'5000':{'resources':{}, 'x':game_max_x, 'y':game_max_y}}
                            agent.rle = setGameState(agent.rle, frames[-1], rle_max_x, game_max_x, rle_max_y, game_max_y)
                            agent.statesEncountered.append(agent.rle._game.getFullState())
                        # end = time.time()
                        # print("setGameState2 total (Time elapsed): {}".format(end - start)) 
                        # start = time.time()
                # embed()
                # agent.makeMovie()
                        # end = time.time()
                        # print("moveMaking total (Time elapsed): {}".format(end - start))

def loadHumanData(games_to_make='all'):
    # for subjects data
    # print mydict
    # experimentID: gameName: gameLevel: gameRound
    directory = "./new_reconstructed_gamestates"#../../New_Reconstructed/Test"
    experimentsDict = defaultdict(dict)
    count = 0
    

    median_humans = {}
    closest_to_empa_humans = {}
    # median_humans = {'gvgai_aliens':'HkQ-A8RTm', 'gvgai_avoidgeorge': 'SJhSg3upm', 'gvgai_bait': 'HJAbk3g0X', 'gvgai_boulderdash': 'HJ32mhuaX', 'gvgai_butterflies': 'r1RkmNDa7',
    #                  'gvgai_chase': 'Hy9GxRxAX', 'corridor': 'BJKE_OCp7', 'antagonist': 'H1YxGsip7', 'ee': 'BynX6OjaX', 'explore/exploit': 'BynX6OjaX',
    #                  'helper': 'Sy-Ajie07', 'preconditions': 'B1lTauiam', 'relational': 'B1xmXXYa7', 'gvgai_frogs': 'BJKMAsppQ', 'gvgai_jaws': 'BJBo7_eA7',
    #                  'gvgai_lemmings': 'rk0Wvv3aX', 'gvgai_missilecommand': 'rkwcKTD6X', 'gvgai_myAliens': 'HJAbk3g0X', 'gvgai_plaqueattack': 'SJI0FY1C7', 'gvgai_portals': 'rkXE42OT7',
    #                  'gvgai_sokoban': 'Skiv1mYaX', 'surprise': 'Hkv3BTkRm', 'gvgai_survivezombies': 'Sk9eTyppm', 'gvgai_watergame': 'Skxfu9JRQ', 'gvgai_zelda': 'rkvT_deAm'}
    

    # closest_to_empa_humans = {'gvgai_aliens':'B14BmUA67', 'gvgai_avoidgeorge': 'SJhSg3upm', 'gvgai_bait': 'HyJXjilA7', 'gvgai_boulderdash': 'HJ32mhuaX', 'gvgai_butterflies': 'rJ0n-twp7',
    #                  'gvgai_chase': 'BJYdWTlA7', 'corridor': 'BkzUUICp7', 'antagonist': 'HylB7Kj67', 'ee': 'Bk-zxOYo67', 'explore/exploit': 'Bk-zxOYo67',
    #                  'helper': 'SkDbtae0X', 'preconditions': 'Sk6ghujTQ', 'relational': 'S1n9TQFaX', 'gvgai_frogs': 'SJ0jVapa7', 'gvgai_jaws': 'ryxGrdxCX',
    #                  'gvgai_lemmings': 'r1YCA82pm', 'gvgai_missilecommand': 'SyIbokd6Q', 'gvgai_myAliens': 'BJYdWTlA7', 'gvgai_plaqueattack': 'B1ZlOoJAm', 'gvgai_portals': 'ry4ws3_aX',
    #                  'gvgai_sokoban': 'rkzFQXKa7', 'surprise': 'Skxfu9JRQ', 'gvgai_survivezombies': 'SkdE1k6p7', 'gvgai_watergame': 'Skwm3ckC7', 'gvgai_zelda': 'ryxGrdxCX'}

    # closest_to_empa_humans = {'expt_push_boulders':  ['rkMehQR6X', 'B1f94xATX', 'HJEndgRp7', 'rk42LeATX']}
    # median_humans = {'expt_antagonist': ['HylB7Kj67']}
    # median_humans = {'gvgai_aliens':['Hy7eL_Aa7'], 'gvgai_variant_aliens_2':['r1OKn1upX'], 'gvgai_aliens_2':['r1OKn1upX']}#,

    # median_humans = {'gvgai_boulderdash':['r1G6W0dTX']} #HkFHm1TpQ
    median_humans = {'gvgai_aliens':['HkQ-A8RTm'], 'gvgai_avoidgeorge':['r1G6W0dTX'], 'gvgai_boulderdash':['r1G6W0dTX'],
    'corridor': ['Bku7ePCpm'], 'expt_antagonist':['HylB7Kj67'], 'expt_helper': ['HJp55se0Q'], 'expt_push_boulders': ['B1f94xATX'],
    'expt_relational': ['S1n9TQFaX'], 'gvgai_variant_portals_1': ['BkrUEAn6m'], 'gvgai_variant_sokoban_1': ['rybbHdlA7'], 
    'gvgai_plaqueattack':['B1ZlOoJAm'], 'gvgai_variant_zelda_1': ['ByOSP1qa7'], 'gvgai_bait': ['HyJXjilA7'], 
    'gvgai_butterflies': ['rJ0n-twp7'],
    'gvgai_zelda': ['ryITmOeR7']}

    for filename in os.listdir(directory):
        
        if not filename.split("_")[0] == "New":
                continue
        print(filename)
        # each time process a new ID
        experimentID = filename.split("_")[3]
        print(experimentID)
        ## Uncomment this if you want to find a particular subject
        if experimentID not in [item for sublist in median_humans.values()+closest_to_empa_humans.values() for item in sublist]:
            continue
        else:
            print("found an experimentDict we care about: {}".format(experimentID))
            # embed()

        count += 1
        print("{}:{}".format(count, filename))
        #filename = "Reconstructed_August22th_SJwN8HoUm"
        path = directory + "/" + filename
        json_file = open(path, 'rb')
        mydict = json.load(json_file)
        a= mydict
        json_file.close()
        
        experimentsDict[experimentID] = defaultdict(dict)
        experimentsDict[experimentID]["gamesIndex"] = defaultdict(dict)
        experimentsDict[experimentID]["gamesData"] = defaultdict(dict)
        
        for idx, dictState in enumerate(mydict):
            for key in dictState:
                print(key)
                #gameData = dictState[key]
                jumped = False
                real_key = key
                '''
                for i in range(0, len(key)):
                    if key[i].isalpha() or key[i].isdigit():
                        real_key = real_key + key[i]
                        jumped = False
                    elif key[i] == '_':
                        if not jumped:
                            jumped = True
                            continue
                        elif jumped:
                            real_key = real_key + key[i]
                            jumped = False
                '''
                
                gameData = sorted(dictState[key], key=lambda k: k['frame'])
                #(gameName, gameLevel, gameNumber, gameRound)
                tup = real_key.split("_")
                #print(tup)
                gameName =  "_".join(tup[:-3])
                print(gameName)
                # if 'variant' in gameName or 'bees' in gameName:
                    # continue
                try:
                    ## use this if you want to just get a particular game
                    # if (games_to_make!='all') and gameName not in games_to_make:
                        # print("{} not the game we want. continuing".format(gameName))
                        # continue
                    ## use this if you want to find a particular subject
                    # if not (experimentID in closest_to_empa_humans[gameName]):
                    if not (experimentID in median_humans[gameName]):
                        print("{} not the game we want. continuing".format(gameName))
                        continue
                except:
                    print("found exception on {}".format(gameName))
                    continue
                
                print(" ")
                print("Continuing with {}".format(gameName))
                #print(real_key)
                gameLevel = tup[-3]
                gameNumber = tup[-2]
                gameRound = tup[-1]
                
                # store game indices
                experimentsDict[experimentID]["gamesIndex"][gameNumber] = gameName
                
                # store game data
                if gameName not in experimentsDict[experimentID]["gamesData"]:
                    experimentsDict[experimentID]["gamesData"][gameName] = defaultdict(dict)
                
                if gameLevel not in experimentsDict[experimentID]["gamesData"][gameName]:
                    experimentsDict[experimentID]["gamesData"][gameName][gameLevel] = defaultdict(dict)
                experimentsDict[experimentID]["gamesData"][gameName][gameLevel][gameRound] = gameData
            
    return experimentsDict

# for subjects data 
def makeHumanMovies(experimentsDict):
    # hyperparameter_index = 0
    for ID in experimentsDict:
            print(ID)
            experimentIndices = experimentsDict[ID]['gamesIndex']
            experimentData = experimentsDict[ID]['gamesData']
            games = []
            for gameNumber in sorted(experimentIndices.keys()):
                #print(index)
                group = None
                VGDLgameName = experimentIndices[gameNumber]
                print(VGDLgameName)
                if VGDLgameName.split("_")[0] == 'gvgai':
                    gameName = '_'.join(VGDLgameName.split("_")[1:])
                    games.append(gameName)
                elif VGDLgameName.split("_")[0] == 'expt':
                    gameName = '_'.join(VGDLgameName.split("_")[1:])
                    games.append(gameName)
                    #continue
                
                gameFile = "../all_games"
                print(gameName)
                #if gameName == "plaqueattack" or gameName == "jaws":
                #    continue
                #if ID == "ryJJsDjIX":
                #    continue
                #if ID == "ByHB9SoIX":
                #    if gameName in ["plaqueattack", "jaws", "watergame"]:
                #        continue
                gameData = experimentData[VGDLgameName]
                #print(gameData)
                levels_won = 0
                
                # Uncomment this part when running real experiment, testing it right now
                #if VGDLgameName in group1:
                #    group = 1
                #elif VGDLgameName in group2:
                #    group = 2
                #else:
                #    print("What??!!")
                
                group = 5
                for gameLevel in sorted(gameData.keys()):
                    #print(gameLevel)
                    levelData = gameData[gameLevel]
                    for gameRound in sorted(levelData.keys()):
                        frames = levelData[gameRound]
                        #agent = initialize_agent(gameFile, gameName)
                        agent = initialize_agent(gameFile, gameName, int(gameLevel), "_".join([ID, VGDLgameName, gameNumber, gameLevel, gameRound]))
                        
                        rle_max_x, rle_max_y, game_max_x, game_max_y = find_max(agent.rle, frames[0])
                        print("rle x, y: {} {}".format(rle_max_x, rle_max_y))
                        print("game x, y: {} {}".format(game_max_x, game_max_y))


                        if 'aliens' in gameName:
                            ## use game_max_x to find where the bottom-left hidden object would have been in the original screen
                            ## insert it there at every frame before rendering.
                            game_min_x, game_min_y = find_block_size(frames[0])
                            game_max_x = game_min_x*29 ## this is rightmost block
                            game_max_y = game_min_y*10 ## bottommost block
                            new_sprite = agent.rle._game._createSprite(['portalSlow'], (game_min_x*29,game_min_y*10))

                        # embed()
                        #print(frames[0])
                        #print(agent.rle._game.sprite_groups)
                        start = time.time()
                        for i in range(0, 10):
                            if 'aliens' in gameName:
                                frames[0]['objects']['portalSlow']['5000'] = {'resources':{}, 'x':game_max_x, 'y':game_max_y}
                            agent.rle = setGameState(agent.rle, frames[0], rle_max_x, game_max_x, rle_max_y, game_max_y)
                            agent.statesEncountered.append(agent.rle._game.getFullState())
                        for frame in frames[1:-1]:
                            if 'aliens' in gameName:
                                frame['objects']['portalSlow']['5000'] = {'resources':{}, 'x':game_max_x, 'y':game_max_y}
                            agent.rle = setGameState(agent.rle, frame, rle_max_x, game_max_x, rle_max_y, game_max_y)
                            agent.statesEncountered.append(agent.rle._game.getFullState())
                        for i in range(0, 10):
                            if 'aliens' in gameName:
                                frames[-1]['objects']['portalSlow']['5000'] = {'resources':{}, 'x':game_max_x, 'y':game_max_y}
                            agent.rle = setGameState(agent.rle, frames[-1], rle_max_x, game_max_x, rle_max_y, game_max_y)
                            agent.statesEncountered.append(agent.rle._game.getFullState())
                        #agent.gameFileName = "_".join([VGDLgameName, gameNumber, gameLevel, gameRound])
                        end = time.time()
                        print("setGameState2 total (Time elapsed): {}".format(end - start)) 
                        start = time.time()
                        agent.makeMovie()
                        end = time.time()
                        print("moveMaking total (Time elapsed): {}".format(end - start)) 
            print("{}:{}".format(ID, games))

## EMPA
dirName = 'demo_data_files/EMPA/local/results'
# #'expt_push_boulders', 'frogs', 'variant_portals_1'

# fullData = processModelData(dirName,games_to_make='all')
# fullData = processModelData(dirName,games_to_make=['tiny_zelda'])
# loadedData = loadEMPAData(fullData)
# makeEMPAMovies(loadedData)

## Humans:
## will read whatever subject files are in in 'new_reconstructed_gamestates' and will make videos.
# loadedData = loadHumanData(games_to_make=['gvgai_zelda', 'gvgai_boulderdash', 'expt_helper']) #expt_push_boulders
# loadedData = loadHumanData(games_to_make='all') #expt_push_boulders
# makeHumanMovies(loadedData)

## DDQN:
# dirName = 'modelData_dqn'
## TODO: Finish this






