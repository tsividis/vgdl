from util import *
from core import colorDict, VGDLParser, sys, keyPresses
from ontology import *
from theory_template import TimeStep, Precondition, InteractionRule, TerminationRule, TimeoutRule, \
SpriteCounterRule, MultiSpriteCounterRule, ruleCluster, Theory, Game, writeTheoryToTxt, generateSymbolDict, \
generateTheoryFromGame, getPosterior
import os, subprocess, shutil
from collections import defaultdict
from hyperparameters import hyperparameter_sets, metacontroller_sets
from math import log
from pprint import pprint
import WBP
import importlib
import numpy as np
import random
import cPickle, cloudpickle
import time
from datetime import datetime
import copy
from agent_utils import translateEvents, observe
from rlenvironmentnonstatic import createRLInputGame, createRLInputGameFromStrings, defInputGame, createMindEnv
from termcolor import colored
from pygame import K_LEFT, K_UP, K_RIGHT, K_DOWN, K_SPACE

MAX_STEPS = 10000
actionDict = {K_SPACE: 'space', K_UP: 'up', K_DOWN: 'down', K_LEFT: 'left', K_RIGHT: 'right', 0:'none'}
AvatarTypes = [MovingAvatar, HorizontalAvatar, VerticalAvatar, FlakAvatar, AimedFlakAvatar, OrientedAvatar,
RotatingAvatar, RotatingFlippingAvatar, NoisyRotatingFlippingAvatar, ShootAvatar, AimedAvatar,
AimedFlakAvatar, InertialAvatar, MarioAvatar]

fMRI_screensize = (1200, 900) # TODO dedupe momchil

class Agent:
    def __init__(self, modelType, gameFilename, hyperparameter_sets, hyperparameter_index=3, metacontroller_index=0, IW_k=2, extra_atom_allowed=True, task_ID=0, produce_printout=False, movieName=None):
        self.modelType = modelType
        self.gameFilename = gameFilename
        self.gameString = None
        self.levelString = None
        self.playback_states = None
        self.playback_keystates = None
        self.record_fMRIRegressors = False
        self.hypothesesPosterior = None
        self.display_text = False
        self.display_states = False
        self.record_states = True
        self.record_video_info = True
        self.write_video_info = True
        self.saveMidEpisode = False # momchil - false
        self.filename = None
        self.timestamp = False
        self.task_ID = task_ID
        self.produce_printout = produce_printout
        self.movieName = movieName
        ## Loading parameters
        self.hyperparameter_sets = hyperparameter_sets
        self.hyperparameter_index = hyperparameter_index
        self.hyperparameters = hyperparameter_sets[hyperparameter_index]
        self.annealingFactor = 1. # meaningless
        self.shortHorizon = self.hyperparameters['short_horizon'] # Params used in short-horizon planning
        self.firstOrderHorizon = self.hyperparameters['first_order_horizon'] # Makes you commit to a plan once first-order distances change (e.g., spritecounter values)
        self.IW_k = IW_k # Only using IW 1 now.
        self.extra_atom_allowed = extra_atom_allowed # Adding optional extra atom to IW
        self.epsilon_greedy = False # Ablation
        self.hybrid = False # Not used
        self.switch_to_exploit_step = 1000 # Only used for e-greedy ablation
        self.absolute_max_nodes = 50000 # Just a convenience parameter
        self.shortHorizonNodes = 500 ## This isn't used. but you need to clean the code up a bit to actually delete it.
        self.shortHorizonAnnealing = 1.05 ## This isn't used, either. but you need to clean the code up a bit to actually delete it.
        self.metacontroller_params = metacontroller_sets[metacontroller_index]
        self.random_steps_on_plan_failure = self.metacontroller_params['random_steps_on_plan_failure']
        self.longHorizonNodes = self.metacontroller_params['longHorizonNodes']
        self.longhorizonAnnealing = self.metacontroller_params['longhorizonAnnealing']
        self.shortHorizonRandomChoice = self.metacontroller_params['shortHorizonRandomChoice']
        self.conservative_max_nodes = self.metacontroller_params['conservative_max_nodes']
        self.extra_atom = self.metacontroller_params['extra_atom']
        self.noNewObjectNum = self.metacontroller_params['noNewObjectNum']
        self.objectLocationTrackingLimit = self.metacontroller_params['objectLocationTrackingLimit']
        self.safeDistance = self.metacontroller_params['safeDistance']
        self.longHorizonObservationLimit = self.metacontroller_params['longHorizonObservationLimit']
        self.objectNumberTrackingLimit = self.metacontroller_params['objectNumberTrackingLimit']
        ##AGH1 = goal gradient only | AGH2=subgoal only | AGH3=goal gradient + subgoal
        self.planner_lesion = self.metacontroller_params['planner_lesion'] if 'planner_lesion' in self.metacontroller_params else []
        self.dynamic_type_lesion = self.metacontroller_params['dynamic_type_lesion'] if 'dynamic_type_lesion' in self.metacontroller_params else []
        self.interaction_lesion = self.metacontroller_params['interaction_lesion'] if 'interaction_lesion' in self.metacontroller_params else []
        self.interaction_lesion_replacement = self.metacontroller_params['interaction_lesion_replacement'] if 'interaction_lesion_replacement' in self.metacontroller_params else []
        self.disallowed_events = self.interaction_lesion

        if 'objectsWhoseLocationWeIgnore' in self.metacontroller_params:
            self.objectsWhoseLocationWeIgnore = self.metacontroller_params['objectsWhoseLocationWeIgnore']
        else:
            self.objectsWhoseLocationWeIgnore = ['Flicker', 'Random']
        self.objectsWhoseLocationWeIgnoreString = ''.join([s[0] for s in self.objectsWhoseLocationWeIgnore]) if self.objectsWhoseLocationWeIgnore else 'None'
        if self.shortHorizon == True:
            self.starting_max_nodes = self.shortHorizonNodes
            self.max_nodes_annealing = self.shortHorizonAnnealing
        else:
            self.starting_max_nodes = self.longHorizonNodes
            self.max_nodes_annealing = self.longhorizonAnnealing
        self.allow_long_range = True ## for the exploration lesion we want to optionally disable long-range planning
        # self.param_ID = "IW={}_eaa={}_ea={}_sh={}_lh={}_sha={}_lha={}_shr={}_nF=True_abmax={}_lR={}_eG={}_sTE={}_hyb={}_PL={}_DTL={}_IL={}_ILR={}_nnon={}_ontl={}_oltl={}_sD={}_lhol={}_igl={}".format(self.IW_k, self.extra_atom_allowed, self.extra_atom, 
        #         self.shortHorizonNodes, self.longHorizonNodes, self.shortHorizonAnnealing, self.longhorizonAnnealing, 
        #         self.shortHorizonRandomChoice, self.absolute_max_nodes, self.allow_long_range, self.epsilon_greedy, 
        #         self.switch_to_exploit_step, self.hybrid, self.planner_lesion, self.dynamic_type_lesion, self.interaction_lesion, self.interaction_lesion_replacement,
        #         self.noNewObjectNum, self.objectNumberTrackingLimit, 
        #         self.objectLocationTrackingLimit, self.safeDistance, self.longHorizonObservationLimit,
        #         self.objectsWhoseLocationWeIgnoreString)
        self.param_ID = "eG={}_PL={}".format(self.epsilon_greedy, self.planner_lesion)
        self.param_ID = self.param_ID+'_batchID='+str(0)
    
        self.conservative = False
        self.regrounding = 1
        # self.selective_regrounding = True ## not used
        self.reground_for_npcs = False ## delete this and the code that checks it, since you haven't used it in ages.

        self.hypotheses = []
        self.symbolDict = None
        self.finalEventList = []
        self.finalEffectList = set()
        self.finalTimeStepList = []
        self.statesEncountered = []
        self.rleHistory = []
        self.episodeRecord = []
        self.fakeInteractionRules = []
        self.all_objects = {}
        self.bestSpriteTypeDict = defaultdict(lambda : {})
        self.spriteUpdateDict = defaultdict(lambda : 0)
        self.max_game_time_observed = 0
        self.best_params = None
        self.seen_resources = []
        self.seen_limits = []
        self.new_objects = {}
        self.actionSeqLength = 0.
        self.skipInduction = False

        # Hyperopt output
        self.total_game_steps = 0
        self.total_planner_steps = 0
        self.levels_won = 0

        self.todo_delete = True

    def hyperparameterSwitch(self, new_index):
        if new_index!=self.hyperparameter_index:
            self.hyperparameter_index = new_index
            self.hyperparameters = self.hyperparameter_sets[new_index]
            self.shortHorizon = self.hyperparameters['short_horizon']
            self.firstOrderHorizon = self.hyperparameters['first_order_horizon']
            if self.shortHorizon == True:
                self.starting_max_nodes = self.shortHorizonNodes
                self.max_nodes_annealing = self.shortHorizonAnnealing
            else:
                self.starting_max_nodes = self.longHorizonNodes
                self.max_nodes_annealing = self.longhorizonAnnealing
            self.max_nodes = self.starting_max_nodes
            self.stored_max_nodes = self.max_nodes

            if self.display_text:
                print "Switching hyperparameters to {}".format(new_index)
        planner_hyperparameters = dict((k, self.hyperparameters[k]) for k in self.hyperparameters.keys() if k not in ['short_horizon', 'first_order_horizon'])
        return planner_hyperparameters

    def initializeEnvironment(self):
        if self.gameString==None or self.levelString==None:
            self.gameString, self.levelString = defInputGame(self.gameFilename, randomize=False)
        self.rleCreateFunc = lambda: createRLInputGameFromStrings(self.gameString, self.levelString, visualize=True, screensize=fMRI_screensize)
        self.rle = self.rleCreateFunc()
        self.rle._game.spriteUpdateDict = self.spriteUpdateDict

        if self.playback_states: # theory induction from human replay
            self.rle._game.playback_states = self.playback_states
            self.rle._game.playback_keystates = self.playback_keystates
            self.rle._game.action_playback_only = True
            assert self.rle._game.playback_index == 0
            assert len(self.rle._game.playback_states) == len(self.rle._game.playback_keystates)
            # important to set the initial state now -- we getObjects() to initialize the theories in replayEpisode, and the UUIDs of the objects should match up, e.g. for proper event handling
            self.rle._game.setFullState(self.rle._game.playback_states[0], cheap=False, default_colors=True)
            self.rle._game.playback_index += 1
        return

    def initializeRLEFromGame(self):
        gameString, levelString = self.gameString, self.levelString
        if gameString == None or levelString == None:
            gameString, levelString = defInputGame(self.gameFilename, randomize=False)
        rleCreateFunc = lambda: createRLInputGameFromStrings(gameString, levelString)
        rle = rleCreateFunc()
        return rle

    def fastcopy(self, rle):
        ## State copying, used for saving state in search, etc.
        newRle = self.initializeRLEFromGame()
        newRle._obstypes = ccopy(rle._obstypes)
        if hasattr(rle, '_gravepoints'):
            newRle._gravepoints = ccopy(rle._gravepoints)
        newRle._game.sprite_groups = ccopy(rle._game.sprite_groups)
        newRle._game.kill_list = ccopy(rle._game.kill_list)
        newRle._game.time = ccopy(rle._game.time)
        newRle._game.score = ccopy(rle._game.score)
        newRle._game.keystate = ccopy(rle._game.keystate)
        newRle.symbolDict = ccopy(rle.symbolDict)
        newRle._game.sprite_groups['avatar'][0].resources = ccopy(rle._game.sprite_groups['avatar'][0].resources)

        return newRle

    def getSpritesByColor(self, rle, color):
        outList = []
        for k in rle._game.sprite_groups.keys():
            if rle._game.sprite_groups[k] and rle._game.sprite_groups[k][0].colorName==color:
                outList.extend(rle._game.sprite_groups[k])
        if outList:
            return outList
        else:
            return None

    def findNearestSprite(self, sprite, spriteList):
        ## returns the sprite in spriteList whose location best matches the location of sprite.
        return sorted(spriteList, key=lambda x:abs(x.rect[0]-sprite.rect[0])+abs(x.rect[1]-sprite.rect[1]))[0]

    def setSpritePositions(self, rle, Vrle, hypothesis):
        ## Sets positions of objects in Vrle to what they were in the rle. Bypasses clunky VGDL level description.

        old_sprite_groups = Vrle._game.sprite_groups
        for k in old_sprite_groups.keys():
            if old_sprite_groups[k]:
                color = Vrle._game.sprite_groups[k][0].colorName
                matchingSpritesInRLE = self.getSpritesByColor(rle, color)
                for sprite in old_sprite_groups[k]:
                    matchingSprite = self.findNearestSprite(sprite, matchingSpritesInRLE)
                    sprite.rect = matchingSprite.rect
                    sprite.lastmove = matchingSprite.lastmove
                    sprite.ID2 = matchingSprite.ID
                    if 'Missile' in str(hypothesis.classes[sprite.name][0].vgdlType) and self.best_params!=None:
                        try:
                            ## Enforce consistency: inferred value for individual orientations has to be consistent with what we're saying the horizontal/vertical orientation is of the entire group.
                            # embed()

                            orientation = tuple(np.sign(np.array(self.rle._game.previousPositions[matchingSprite.ID]) - np.array(self.rle._game.objectMemoryDict[matchingSprite.ID])))
                            # if color=='RED':
                                # embed()
                            if orientation == (0,0):
                                # print "found 0,0 orientation. Using generic missile orientation:", sprite.orientation, sprite.speed, sprite.cooldown
                                pass
                            #     embed()

                            else:
                                sprite.orientation = orientation

                        except KeyError:
                            sprite.orientation = random.choice([(0,1), (0,-1), (1,0), (-1,0)])
                            # pass
        for k,v in Vrle._game.sprite_groups.items():
            for sprite in v:
                if sprite not in Vrle._game.kill_list:
                    loc = (sprite.rect.left, sprite.rect.top)
                    if loc in Vrle._game.positionDict.keys():
                        Vrle._game.positionDict[loc].append(sprite)
                    else:
                        Vrle._game.positionDict[loc] = [sprite]
        return


    def initializeVrle(self, hypothesis):
        ## Simulatable world in agent's head given 'hypothesis', including object goal
        gameString, levelString, symbolDict = writeTheoryToTxt(self.rle, hypothesis, self.symbolDict,\
                 "./theory_files/{}.py".format(self.gameFilename))
        Vrle = createMindEnv(gameString, levelString, output=False)

        self.setSpritePositions(self.rle, Vrle, hypothesis)
        try:
            Vrle._game.getAvatars()[0].resources = copy.deepcopy(self.rle._game.getAvatars()[0].resources)
            Vrle._game.getAvatars()[0].orientation = copy.deepcopy(self.rle._game.getAvatars()[0].orientation)
        except (IndexError, AttributeError) as e:
            pass
        return Vrle

    def VrleInitPhase(self, flexible_goals=False):
        ## Initialize multiple VRLEs, each corresponding to one hypothesis in self.hypotheses
        VRLEs = []

        for hypothesis in self.hypotheses[0:1]:
            tempHypothesis = copy.deepcopy(hypothesis)
            tmpFakeInteractionRules = copy.deepcopy(self.fakeInteractionRules)
            tempHypothesis.interactionSet.extend(tmpFakeInteractionRules)
            if not flexible_goals:
                tempHypothesis.updateTerminations()
            VRLEs.append(self.initializeVrle(tempHypothesis))

        return VRLEs

    def initializeHypotheses(self, allObjects, statesEncountered, compactStates, learnSprites=True):
        ## Creates initial hypothesis objects by observing the game,
        ## doing initial inference over sprite types, and returning partial
        ## candidate models.
        if learnSprites:
            if not self.skipInduction:
                ## need to run this for one step to get a theory so we can calculate initial entropy. Then we run it another 14 times.
                self.observe(self.rle, 1, self.bestSpriteTypeDict, statesEncountered, compactStates, display=self.display_states, hypothesis=None)
                spriteTypeHypothesis, exceptedObjects, _, self.best_params = sampleFromDistribution(self.rle._game, \
                    self.rle._game.spriteDistribution, allObjects, self.rle._game.spriteUpdateDict, self.bestSpriteTypeDict, skipInduction=self.skipInduction)
                self.rle._game.exceptedObjects = exceptedObjects
                gameObject = Game(spriteInductionResult=spriteTypeHypothesis)
                initialTheory = gameObject.buildGenericTheory(spriteTypeHypothesis)

                self.observe(self.rle, 3, self.bestSpriteTypeDict, statesEncountered, compactStates, display=self.display_states, hypothesis=initialTheory)
            else:
                self.observe(self.rle, 1, self.bestSpriteTypeDict, statesEncountered, compactStates, display=self.display_states, hypothesis=initialTheory)                
            spriteTypeHypothesis, exceptedObjects, _, self.best_params = sampleFromDistribution(self.rle._game, \
                self.rle._game.spriteDistribution, allObjects, self.rle._game.spriteUpdateDict, self.bestSpriteTypeDict, skipInduction=self.skipInduction)
            self.rle._game.exceptedObjects = exceptedObjects
            gameObject = Game(spriteInductionResult=spriteTypeHypothesis)
            initialTheory = gameObject.buildGenericTheory(spriteTypeHypothesis)
        else:
            gameObject = Game(self.gameString)
            initialTheory = gameObject.buildGenericTheory(spriteSample=False, vgdlSpriteParse = gameObject.vgdlSpriteParse)

        avatar = [o for o in initialTheory.spriteSet if o.vgdlType in AvatarTypes][0]

        ### Edit hypotheses for cultural-transmission experiment here.
        ## initialTheory.interactionSet is the list to modify.

        self.hypotheses = [initialTheory]
        self.symbolDict = generateSymbolDict(self.rle)
        return gameObject

    def completeHypotheses(self, allObjects, statesEncountered, compactStates, first_time_playing_level):
        previous_colors = [o['type']['color'] for o in self.previous_objects.values()]
        current_colors = [o['type']['color'] for o in allObjects.values()]
        if all([c in previous_colors for c in current_colors]):
            self.observe(self.rle, 0, self.bestSpriteTypeDict, statesEncountered, compactStates, display=self.display_states, hypothesis=self.hypotheses[0]) ## if no new colors on screen, just set up likelihood updates
        else:
            self.observe(self.rle, 5, self.bestSpriteTypeDict, statesEncountered, compactStates, display=self.display_states, hypothesis=self.hypotheses[0]) ## if new objects, observe for a few steps so that you're not completely clueless about object movements in the new level, before you start planning.

        ## Make sure any objects that appeared while we were observing are reflected in allObjects
        for k,v in self.rle._game.getObjects().items():
            if k not in allObjects:
                allObjects[k] = v

        spriteTypeHypothesis, exceptedObjects, _, self.best_params= sampleFromDistribution(self.rle._game, self.rle._game.spriteDistribution, allObjects, self.rle._game.spriteUpdateDict, 
                self.bestSpriteTypeDict, self.hypotheses[0].spriteSet, skipInduction=self.skipInduction)
        gameObject = Game(spriteInductionResult=spriteTypeHypothesis)
        newHypotheses = []
        try:
            for hypothesis in self.hypotheses:
                newHypotheses.append(gameObject.addNewObjectsToTheory(hypothesis, spriteTypeHypothesis))
        except:
            print "failed in addNewObjectsToTheory"
            # embed()
        self.hypotheses = newHypotheses


    def calculateEntropy(self, theory, spriteDistribution):
        return None

    def playCurriculum(self, heatmap=False, level_game_pairs=None, make_movie=False, play_movie=False, playback=False):
        """ Plays a game level until it wins, then moves to the next one until
        completion. """
        starttime = time.time()
        if not level_game_pairs:
            level_game_pairs = importlib.import_module(self.gameFilename).level_game_pairs
        episodes = []
        allEffectsEncountered = []
        self.make_movie = make_movie

        ## used for time-stamping data related to this particular run of the model.
        timestamp = datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d__%H_%M__')+self.task_ID
        self.timestamp = timestamp
        if self.record_states:
            # dirname = "results/{}/{}/".format(self.param_ID, self.gameFilename) # old data location
            dirname = "demo_data_files/EMPA/local/results/{}/{}/".format(self.param_ID, self.gameFilename)
            filename = "{}{}_{}".format(dirname, self.gameFilename, timestamp)
            self.filename = filename
            if not os.path.exists(dirname):
                try:
                    os.makedirs(dirname)
                except:
                    print "failed  to make dir"
        if self.write_video_info:
            dirname = "raw_video_info/{}/{}/".format(self.param_ID, self.gameFilename)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
        if self.make_movie:
            if 'images' in os.listdir('.') and 'tmp' in os.listdir('images') and self.gameFilename in os.listdir('images/tmp'):
                shutil.rmtree("images/tmp/"+self.gameFilename)
            os.makedirs("images/tmp/"+self.gameFilename)

        if self.record_fMRIRegressors:
            curriculumRegressors = []

        # print "timestamp", self.timestamp
        # print "param_ID", self.param_ID
        curriculumDir = 'savedCurricula'
        if curriculumDir not in os.listdir('.'):
            os.makedirs(curriculumDir)
        curriculumSaveFile = 'curriculum_'+self.gameFilename+'_'+self.param_ID+'_'+self.task_ID
        loadedState = False
        loaded_n_level=0
        # embed()
        if curriculumSaveFile in os.listdir(curriculumDir):
            try:
                print "found saved curriculum state"
                loadedState = self.loadState(curriculumDir+'/'+curriculumSaveFile)
                loaded_n_level, within_level_iteration = loadedState['agent'].n_level, loadedState['agent'].within_level_iteration
                self = loadedState['agent'] ## load saved agent
                ##self.filename will get overloaded here.
                print "loaded curriculum state"
            except:
                os.remove(curriculumDir+'/'+episodeSaveFile)
                print "failed to load curriculum state. deleting corrupted file and starting from scratch"

        j=0
        flexible_goals = False
        fullStateEpisodes, episodeCompactStates = {}, {}
        for n_level, level_game in enumerate(level_game_pairs):

            if n_level < loaded_n_level: ## if we have a saved state that corresponds to us having played this level, skip it.
                continue
            if self.produce_printout:
                print ""
                print("Playing level {}".format(n_level+1))

            if playback:
                # fMRI playback from human play
                (self.gameString, self.levelString, self.playback_states, self.playback_keystates) = level_game
            else:
                (self.gameString, self.levelString) = level_game
                self.playback_states = None # TODO momchil undo
                self.playback_keystates = None # TODO momchil undo

            if self.record_fMRIRegressors:
                self.regressors = {
                    'spriteKL': [],
                    'interactionKL': [],
                    'terminationKL': [],
                    'sampleKL': [],
                    'MAPloglik': [],
                    'MAPlogpost': [],
                    'theory_change_flag': [],
                    'sprite_change_flag': [],
                    'interaction_change_flag': [],
                    'termination_change_flag': [],
                    'theoryDist': [],
                    'theory': []
                }

            self.max_nodes = self.starting_max_nodes
            self.stored_max_nodes = self.max_nodes
            win = False
            gameObject = None
            
            i=0
            if loadedState:
                i=loadedState['agent'].within_level_iteration
                episodeCompactStates = loadedState['episodeCompactStates']
            levelEffectsEncountered = []
            allStatesEncountered = []
            allCompactStates = []
            t1 = time.time()
            if i==0:
                first_time_playing_level = True
            else:
                first_time_playing_level = False
            quit_level = False
            while not win and not quit_level:# and i<15:
                self.n_level = n_level
                self.within_level_iteration = i

                if playback:
                    # fMRI playback from human play
                    gameObject, win, score, steps, statesEncountered, effectsEncountered, compactStates, quit_level = self.replayEpisode(gameObject, flexible_goals, win, first_time_playing_level)
                else:
                    gameObject, win, score, steps, statesEncountered, effectsEncountered, compactStates, quit_level = self.playEpisode(gameObject, flexible_goals, win, first_time_playing_level)

                self.total_game_steps += steps
                allCompactStates.append(compactStates)
                episode_results = (n_level, steps, win, score, self.total_planner_steps)
                episodes.append(episode_results)

                if self.make_movie:
                    self.statesEncountered = statesEncountered
                    self.makeImages()
                
                if self.record_video_info:
                    allStatesEncountered.extend(statesEncountered)

                i += 1
                # print "Finished in ", time.time() - t1

                episodeCompactStates[n_level] = allCompactStates
                fullStateEpisodes[n_level] = allStatesEncountered


                self.saveCurriculumState(curriculumDir+'/'+curriculumSaveFile, episodeCompactStates)

                ## will write all previous episodes to the file at the end of each episode.
                if self.record_states:
                    gameInfo = {'gameString':self.gameString, 'levelString':self.levelString, 'gameName':self.gameFilename}
                    episodeList = [v for k,v in sorted(episodeCompactStates.items())]

                    with open(self.filename, 'wb') as f:
                        cPickle.dump({'gameInfo':gameInfo,'modelParams':self.param_ID, 'episodes':episodeList, 'time_elapsed':time.time()-starttime}, f)

                if win:
                    self.n_level += 1
                    self.within_level_iteration = 0
                    
                ## will write video data at the end of each episode
                if self.record_video_info:
                    fullStateList = [v for k,v in sorted(fullStateEpisodes.items())]
                if self.write_video_info:
                    videofilename = "{}{}_{}".format(dirname, self.gameFilename, timestamp)
                    gameInfo = {'gameString':self.gameString, 'levelString':self.levelString, 'gameName':self.gameFilename}
                    with open(videofilename, 'wb') as f:
                        cPickle.dump({'gameInfo':gameInfo,'modelParams':self.param_ID, 'episodes':fullStateList, 'time_elapsed':time.time()-starttime}, f)
                if self.total_game_steps > MAX_STEPS:
                    if self.produce_printout:
                        print "reached max number of steps ({}>{}) in playCurriculum. Stopping experiment".format(self.total_game_steps, MAX_STEPS)

                if self.saveMidEpisode:
                    # ## if the episode ends, delete the mid-episode file we were saving.
                    episodeSaveFile = 'episode_'+self.gameFilename+'_'+self.task_ID
                    os.remove(curriculumDir+'/'+episodeSaveFile)
                    print "finished an episode; removing episodeSaveFile"

            if heatmap:
                self.makeHeatmap(allStatesEncountered, 'heatmap_{}_{}_level{}.pdf'.format(self.gameFilename, n_level, self.param_ID))

            if flexible_goals:
                ## Could include in some later project.
                ## When you embed(), you can manually input changes in theory. See flexible_goals.py for an example.
                print "in main_agent; playing with flexible_goals"
                embed()

            if self.record_fMRIRegressors:
                curriculumRegressors.append(self.regressors)

        if make_movie:
            if self.record_fMRIRegressors:
                assert len(curriculumRegressors) == 1 # TODO momchil b/c of theories
                self.makeMovie(play_movie=play_movie, regressors=self.regressors)
            else:
                self.makeMovie(play_movie=play_movie)

        endtime = time.time()

        return curriculumRegressors

    def compactify(self, rle, planner_nodes=0):
        current_time = time.time()
        gameObject = rle._game
        ended, win = rle._isDone()
        state = {'timestep': gameObject.time,
                 'time_elapsed': current_time - self.last_recorded_time,
                 'score': gameObject.score,
                 'planner_settings': self.hyperparameter_index,
                 'planner_nodes': planner_nodes, ## how many nodes were searched to determine this particular action? 0 if this is resulting from a cached plan.
                 'ended': ended,
                 'win': win,
                 'entropy': rle._game.H,
                 'objects': [(colorDict[str(s.color)], (s.rect.left/gameObject.block_size, s.rect.top/gameObject.block_size), s.resources if s.name=='avatar' else {}) 
                        for sublist in gameObject.sprite_groups.values() for s in sublist if s not in gameObject.kill_list],
                 'events': list(rle._game.effectListByClass)

                 }
        self.last_recorded_time = current_time
        return state

    def makeHeatmap(self, statesEncountered, filename):
        from vgdl.plotting import featurePlot
        import matplotlib.pyplot as plt
        from matplotlib.ticker import NullLocator
        import numpy as np

        states = [s['objects']['avatar'].keys()[0] for s in statesEncountered
                  if (not s['observe_state']) and s['objects']['avatar'].keys()]
        width, height = self.rle._game.width, self.rle._game.height
        correction_factor = self.rle._game.screensize[0]/width
        corrected_states = [(s[0]/correction_factor, s[1]/correction_factor) for s in states]

        m = np.zeros((width, height))
        Xs, Ys = [],[]

        block_size=30
        for s in corrected_states:
            x = s[0]
            y = s[1]
            m[x, y] += 1
            Xs.append(x*block_size+block_size/2.)
            Ys.append(y*block_size+block_size/2.)

        plt.imshow(m.T, cmap='viridis')
        plt.gca().set_axis_off()
        plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0,
            hspace = 0, wspace = 0)
        plt.margins(0, 0)
        plt.gca().xaxis.set_major_locator(NullLocator())
        plt.gca().yaxis.set_major_locator(NullLocator())
        plt.savefig(filename, bbox_inches='tight', pad_inches=0)
        plt.close()

    def makeSummaryPlot(self, allEffectsEncountered):
        import matplotlib.pyplot as plt
        import importlib

        mod = importlib('vgdl.colors')
        colors = [cl[0].color for cl in self.hypotheses[0].classes.values()]
        for color in colors:
            times_touched_per_level = []
            for level in allEffectsEncountered:
                times_touched = len([effect
                    for attempt in level
                    for effect in attempt
                    if ((effect[1]==color and effect[2]=='DARKBLUE')
                        or (effect[2]==color and effect[1]=='DARKBLUE'))])
                times_touched_per_level.append(times_touched)
            color_to_plot = [float(value)/255 for value in getattr(mod, color)]
            plt.plot(times_touched_per_level, color=color_to_plot)
        plt.show()


    def makeImages(self):
        ## Used for making videos. First we save all states from all episodes as images, then we stitch together into a video.
        # params_to_print_to_video = self.param_ID
        params_to_print_to_video = ''
        game_name_to_print_to_video = self.gameFilename

        VGDLParser.playGame(self.gameString, self.levelString, self.statesEncountered, \
            persist_movie=True, make_images=True, make_movie=False, movie_dir="videos/"+self.gameFilename, gameName = game_name_to_print_to_video, parameter_string=params_to_print_to_video, padding=10)

    def makeMovie(self, play_movie=False, regressors=None):

        VGDLParser.playGame(self.gameString, self.levelString, self.statesEncountered, \
            persist_movie=True, make_images=True, make_movie=True, movie_dir="videos/"+self.gameFilename, padding=10, regressors=regressors, screensize=fMRI_screensize)

        print "Creating Movie"
        # movie_dir = "videos/{}/{}".format(self.param_ID, self.gameFilename)
        # movie_dir = "videos/"
        movie_dir = "videos/"+self.gameFilename
        if not os.path.exists(movie_dir):
            print movie_dir, "didn't exist. making new dir"
            os.makedirs(movie_dir)

        round_index = len([d for d in os.listdir(movie_dir) if d != '.DS_Store' and self.gameFilename in d])
        # video_dirname = movie_dir+"/round"+str(round_index)+".mp4"
        # video_dirname = movie_dir+"/"+self.gameFilename+'_'+str(round_index)+".mp4"
        video_dirname = movie_dir+"/"+str(self.movieName)+".mp4"
        # images_dir = "images/tmp/{}/%09d.png".format(self.gameFilename)
        images_dir = "images/tmp/%09d.png"
        com = "ffmpeg -i " +images_dir+ " -pix_fmt yuv420p -filter:v 'setpts=4.0*PTS' "+ video_dirname
        command = "{}".format(com)
        subprocess.call(command, shell=True)
        # empty image directory
        shutil.rmtree("images/tmp/"+self.gameFilename)
        os.makedirs("images/tmp/"+self.gameFilename)

        if play_movie:
            command = ('open', '-a', 'Quicktime Player', video_dirname)
            subprocess.Popen(command)

        return

    def playMultipleEpisodes(self, num_episodes):
        i=0
        gameObject = None
        wins, scores = [], []
        win = False
        while i<num_episodes:
            gameObject, win, score, statesEncountered, _ = self.playEpisode(gameObject, flexible_goals=False,first_time_playing_level=False)
            wins.append(win)
            scores.append(score)
            i+=1
        VGDLParser.playGame(self.gameString, self.levelString, self.statesEncountered, \
            persist_movie=True, make_images=True, make_movie=False, movie_dir="videos/"+self.gameFilename, padding=10)
        if self.produce_printout:
            print "Won {} out of {} episodes.".format(sum(wins), i)



    def playEpisode(self, gameObject, flexible_goals=False, win=False, first_time_playing_level=False, pool=None):
        from vgdl.util import manhattanDist

        episodeSaveTime = time.time() ## in seconds
        quit_level = False
        ## Initialize external environment
        self.initializeEnvironment()
        if self.display_text:
            print "initializing RLE"
        # print "Game name:", self.gameFilename
        # print "Starting episode"
        # print "Playing level {}".format(self.n_level + 1)
        if self.produce_printout:
            print ""
            print self.rle.show(color='blue')

        self.quits = 0
        self.longHorizonObservations = 0
        self.previous_objects = self.all_objects if self.all_objects else {}
        self.all_objects= self.rle._game.getObjects()

        annealing = 1
        ## Start storing encountered states.
        effectsEncountered = []
        statesEncountered = []
        compactStates = [] ## for easy analysis of score over time.

        if self.make_movie or self.record_video_info:
            statesEncountered.append(self.rle._game.getFullState())
        
        self.last_recorded_time = time.time()
        if self.record_states:
            compactStates.append(self.compactify(self.rle))
        ## Initialize memory of object positions
        self.rle._game.objectMemoryDict, self.rle._game.previousPositions = {}, {}
        for k, v in self.rle._game.all_objects.iteritems():
            self.rle._game.objectMemoryDict[k] = (int(self.rle._game.all_objects[k]['sprite'].rect.x), int(self.rle._game.all_objects[k]['sprite'].rect.y))
            self.rle._game.previousPositions[k] = (int(self.rle._game.all_objects[k]['sprite'].rect.x), int(self.rle._game.all_objects[k]['sprite'].rect.y))

        ## initialize theory if necessary.
        if len(self.hypotheses) == 0:
            gameObject = self.initializeHypotheses(self.all_objects, statesEncountered, compactStates, learnSprites=True)
            if self.display_text:
                print "initializing hypotheses"
        else:
            gameObject = self.completeHypotheses(self.all_objects, statesEncountered, compactStates, first_time_playing_level)
            if self.display_text:
                print "had hypotheses -- completing them."
            # If theory is being carried over, falsify termination hypotheses
            # given new level state.
            if not flexible_goals:
                [t.updateTerminations(rle=self.rle) for t in self.hypotheses]

        if self.saveMidEpisode:
            ## if we get a loadedState because of interrupted runs on the clsuter, do things with it here.
            episodeSaveFile = 'episode_'+self.gameFilename+'_'+self.task_ID
            curriculumDir = 'savedCurricula'
            if episodeSaveFile in os.listdir(curriculumDir):
                try:
                    loadedState = self.loadState(curriculumDir + '/' + episodeSaveFile)

                    self = loadedState['agent']
                    effectsEncountered = loadedState['effectsEncountered']
                    statesEncountered = loadedState['statesEncountered']
                    compactStates = loadedState['compactStates']
                    annealing = loadedState['annealing']
                    print "just loaded episode state"
                except:
                    os.remove(curriculumDir+'/'+episodeSaveFile)
                    print "failed to load episode state. Deleting the corrupted file and continuing with this episode as though we hadn't saved anything."

        ## Do beginning-of-episode Avatar resource-management.
        resources = self.rle._game.getAvatars()[0].resources
        for resource, val in resources.items():
            if resource not in self.seen_resources and val>0:
                self.seen_resources.append(resource)
                self.hypotheses[0].resource_limits[resource] = self.rle._game.resources_limits[resource]
            if resource not in self.seen_limits and val==self.rle._game.resources_limits[resource]:
                self.seen_limits.append(resource)

        ended, win = self.rle._isDone()

        legalActions = [0, K_UP, K_DOWN, K_LEFT, K_RIGHT]
        if self.hypotheses[0].classes['avatar'][0].args and 'stype' in self.hypotheses[0].classes['avatar'][0].args:
            legalActions.append(K_SPACE)

        steps = self.rle._game.time
        emptyPlans = 0
        while not ended:

            if self.saveMidEpisode:
                self.saveEpisodeState(episodeSaveFile, effectsEncountered, statesEncountered, compactStates, annealing)
                self.episodeSaveTime = time.time()

            if self.total_game_steps+steps > MAX_STEPS:
                score = self.rle._game.score
                quit_level = False
                if self.saveMidEpisode:
                    self.saveEpisodeState(episodeSaveFile, effectsEncountered, statesEncountered, compactStates, annealing)
                    self.episodeSaveTime = time.time()

                return gameObject, win, score, steps, statesEncountered, effectsEncountered, compactStates, quit_level

            self.max_nodes = self.stored_max_nodes

            ## you don't need to worry about annealing, since you don't anneal up for shortHorizon planning.
            if self.shortHorizon and self.shortHorizonRandomChoice:
                self.max_nodes = random.choice(self.shortHorizonRandomChoice)

            # print "planning with hyperparameter index {}".format(self.hyperparameter_index)
            if self.produce_printout:
                print "==============================================================="
                print "planning with max_nodes: {}, short_horizon: {}".format(self.max_nodes, self.shortHorizon)

            ## initialize one or many VRLEs (simulators) according to hypothesis-selection method
            theoryRLEs = self.VrleInitPhase(flexible_goals)

            quitting = False

            planner_hyperparameters = dict((k, self.hyperparameters[k]) for k in self.hyperparameters.keys() if k not in ['short_horizon', 'first_order_horizon'])

            ## Initialize planner
            p = WBP.WBP(theoryRLEs[0], self.gameFilename, theory=self.hypotheses[0], fakeInteractionRules = self.fakeInteractionRules,
                seen_limits = self.seen_limits, annealing=annealing, max_nodes=self.max_nodes, shortHorizon=self.shortHorizon,
                firstOrderHorizon=self.firstOrderHorizon, conservative=self.conservative, hyperparameters=planner_hyperparameters, 
                extra_atom=self.extra_atom, IW_k=self.IW_k, objectNumberTrackingLimit=self.objectNumberTrackingLimit,
                objectLocationTrackingLimit=self.objectLocationTrackingLimit, lesion=self.planner_lesion)
            p_quitting = p.quitting
            print "planning..."
            p.max_nodes = 2 # TODO momchil
            bestNode, gameStringArray, objectPositionsArray = p.BFS()
            self.total_planner_steps += p.total_nodes_opened

            if bestNode is not None:
                solution = p.solution
                gameString_array = p.gameString_array
                objectPositionsArray = objectPositionsArray[::-1]
                if solution and self.display_text:
                    print "got solution"
            else:
                solution = []

            if not solution:
                ## If planner didn't give a solution, switch modes according to metacontroller policy
                if self.checkForRepeatedDeaths(self.episodeRecord, 2):
                    if self.hyperparameter_index == 1:
                        new_index = 1 ## don't switch away from idx_1
                        conservative = False
                    if self.hyperparameter_index == 3:
                        if self.display_text:
                            print "Repeated deaths. Switching to long-range planning"
                        new_index = 1
                        conservative = False
                    planner_hyperparameters = self.hyperparameterSwitch(new_index=new_index)

                elif self.hyperparameter_index == 3:
                    movingTypes = self.checkForMovingTypes(self.rle, self.hypotheses[0])
                    if self.rle._game.time>compactStates[-1]['timestep']:
                        scoreChange = self.rle._game.score!=compactStates[-1]['score']
                    else:
                        scoreChange = True
                    # if self.display_text:
                    # print "moving types: {}".format(movingTypes)
                    # print "noNewObjectsInAWhile: {}".format(self.noNewObjectsInAWhile(self.rle, self.noNewObjectNum))
                    # print "scoreChange: {}".format(scoreChange)
                    if self.noNewObjectsInAWhile(self.rle, self.noNewObjectNum) and \
                            (not movingTypes or (movingTypes and not scoreChange)):
                        if self.produce_printout:
                            print "switching to long-range planning"
                        ## switch to long-range planning
                        new_index = 1
                        planner_hyperparameters = self.hyperparameterSwitch(new_index=new_index)
                        conservative = False
                    else:
                        if self.produce_printout:
                            print "planning in 'stall' mode"
                        new_index = 3
                        planner_hyperparameters = self.hyperparameterSwitch(new_index=new_index)
                        conservative = True
                        self.stored_max_nodes = self.max_nodes ##taking annealing into account
                        self.max_nodes = self.conservative_max_nodes
                else:
                    conservative = False
                if self.display_text:
                    print "planning with hyperparameter index {}".format(self.hyperparameter_index)
                    print "max_nodes: {}, short_horizon: {}, conservative: {}".format(self.max_nodes, self.shortHorizon, conservative)
                # embed()

                if conservative: #aka 'stall'
                    ## Replan in new mode
                    p = WBP.WBP(theoryRLEs[0], self.gameFilename, theory=self.hypotheses[0], fakeInteractionRules = self.fakeInteractionRules,
                        seen_limits = self.seen_limits, annealing=annealing, max_nodes=self.max_nodes, shortHorizon=self.shortHorizon,
                        firstOrderHorizon=self.firstOrderHorizon, conservative=conservative, hyperparameters=planner_hyperparameters, 
                        extra_atom=self.extra_atom, IW_k=self.IW_k, objectNumberTrackingLimit=self.objectNumberTrackingLimit,
                        objectLocationTrackingLimit=self.objectLocationTrackingLimit, lesion=self.planner_lesion)
                    p_quitting = p.quitting
                    bestNode, gameStringArray, objectPositionsArray = p.BFS()
                    self.total_planner_steps += p.total_nodes_opened
                    # print "total planner steps in main_agent:", self.total_planner_steps
                    if bestNode is not None:
                        solution = p.solution
                        gameString_array = p.gameString_array
                        objectPositionsArray = objectPositionsArray[::-1]
                        if solution and self.display_text:
                            print "got solution"
                    else:
                        solution = []
            takingRandomSteps = False

            if (not solution) or p_quitting:
                # Here we make a distinction between quitting because you've
                # exhausted the number of nodes you can visit or because you
                # ran out of novelty. In the first case, you only wait longer,
                # in the second case, you also add a new atom to IW
                if self.extra_atom_allowed:
                    if self.display_text:
                        print "turning on extra atom"
                    self.extra_atom = True
                if self.longHorizonObservations<self.longHorizonObservationLimit: ## if you don't get a plan with short-horizon mode you'll plan in stall mode. 
                ## you only get here if you're in idx_1 (long-term planning) and don't find a plan.
                    if self.produce_printout:
                        print "Didn't get solution. Taking {} random steps and then replanning".format(self.random_steps_on_plan_failure)
                    plannerNodes = p.total_nodes_opened
                    solution = [] ## You may have gotten p.quitting but also a solution; make sure you don't try to act on that if the planner decided it wasn't worth it.
                    for i in range(self.random_steps_on_plan_failure):
                        solution.append(random.choice(legalActions))
                    self.longHorizonObservations += 1
                    takingRandomSteps = True
                else:
                    plannerNodes = p.total_nodes_opened
                    action = 0
                    hypotheses, theory_change_flag, effects = self.executeStep(action, self.hypotheses, statesEncountered, compactStates, plannerNodes,
                        run_induction = not flexible_goals)
                    print 'HYPOTHESIS' # momchil
                    hypotheses[0].display()

                    quitting = True
                    if self.total_game_steps+steps > MAX_STEPS:
                        score = self.rle._game.score
                        quit_level = False
                        if self.saveMidEpisode:
                            self.saveEpisodeState(episodeSaveFile, effectsEncountered, statesEncountered, compactStates, annealing)
                            self.episodeSaveTime = time.time()
                        return gameObject, win, score, steps, statesEncountered, effectsEncountered, compactStates, quit_level
            
            self.actionSeqLength += len(solution)

            ## Most common scenario: planner worked. Show projected plan and states, then act.
            if solution and not p.quitting and not takingRandomSteps and self.display_states and self.produce_printout:
                # print "==============================================================="
                print "found plan of length {}. Intended actions and predicted states:".format(len(solution))
                # print colored(p.gameString_array[0], 'green')
                for i,g in enumerate(p.gameString_array[1:]):
                    print actionDict[solution[i]]
                    print colored(g, 'green')
                print "==============================================================="

            ## Acting/learning/monitoring need to re-plan
            if not quitting:
                for i, action in enumerate(solution):
                    self.hypotheses[0].dryingPaint = set()

                    if self.display_text:
                        t1 = time.time()

                    effects = []
                    plannerNodes = p.total_nodes_opened if i==0 else 0
                    hypotheses, theory_change_flag, effects = self.executeStep(action, self.hypotheses, statesEncountered, compactStates, plannerNodes,
                        run_induction = not flexible_goals)
                    print 'HYPOTHESIS 2' # momchil
                    hypotheses[0].display()

                    ## For an incomplete ablation
                    if self.total_game_steps+steps > MAX_STEPS:
                        score = self.rle._game.score
                        quit_level = False
                        if self.saveMidEpisode:
                            self.saveEpisodeState(episodeSaveFile, effectsEncountered, statesEncountered, compactStates, annealing)
                            self.episodeSaveTime = time.time()

                        return gameObject, win, score, steps, statesEncountered, effectsEncountered, compactStates, quit_level

                    if self.display_text:
                        print "executeStep took {} seconds".format(time.time()-t1)
                    sys.stdout.flush()
                    
                    self.rle._game.nextPositions = {}
                    for k, v in self.rle._game.all_objects.iteritems():
                        self.rle._game.nextPositions[k] = (int(self.rle._game.all_objects[k]['sprite'].rect.x), int(self.rle._game.all_objects[k]['sprite'].rect.y))
                        try:
                            if self.rle._game.previousPositions[k] != self.rle._game.nextPositions[k]:
                                self.rle._game.objectMemoryDict[k] = copy.deepcopy(self.rle._game.previousPositions[k])
                        except KeyError:
                            pass
                    self.rle._game.previousPositions = copy.deepcopy(self.rle._game.nextPositions)

                    effectsEncountered.extend(effects)
                    steps +=1
                    if theory_change_flag:
                        self.hypotheses = hypotheses
                        break
                    ended, win = self.rle._isDone()

                    #ended = self.rle._game.ended # TODO momchil rm me

                    self.max_game_time_observed = max(self.max_game_time_observed, self.rle._game.time)
                    if ended:
                        break

                    ## Make sure you're far enough from unpredictable dangerous objects.
                    # Check for disparities between plan and reality
                    # (e.g. stochastic effects)
                    if (i+1)%self.regrounding==0:

                        if (not takingRandomSteps) and self.checkForDangerOrAvatarMisLocation(self.rle, hypotheses[0], objectPositionsArray, i):
                            break

                    if self.reground_for_npcs: ## this is just exercising caution when near random objects, irrespective of whether they kill us or not
                        try:
                            random_npc_colors = [self.hypotheses[0].classes[k][0].color for k in self.hypotheses[0].classes.keys() if self.hypotheses[0].classes[k] and 'Random' in str(self.hypotheses[0].classes[k][0].vgdlType)]
                            random_npc_classes = [k for k in self.rle._game.sprite_groups.keys() if self.rle._game.sprite_groups[k] and self.rle._game.sprite_groups[k][0].colorName in random_npc_colors]
                            random_npc_positions = []

                            for c in random_npc_classes:
                                for element in self.rle._game.sprite_groups[c]:
                                    if element not in self.rle._game.kill_list:
                                        random_npc_positions.append(self.rle._rect2pos(element.rect))

                            avatar_positions = [self.rle._rect2pos(avatar.rect)
                                 for avatar in self.rle._game.getAvatars()]

                            possiblePairList = [manhattanDist(avatar, rand)
                                for avatar in avatar_positions
                                for rand in random_npc_positions]
                            if min(possiblePairList) < self.safeDistance:
                                if self.produce_printout:
                                    print("Close to RandomNPC, regrounding")
                                # embed()
                                break

                        except ValueError:
                            pass

            else:
                ## You failed the game either because you made a mistake you couldn't recover from or because you timed out in your search.
                ## Search more deeply next time.
                curr_max_nodes = self.max_nodes
                self.max_nodes *= self.max_nodes_annealing
                self.stored_max_nodes = self.max_nodes
                if self.produce_printout:
                    print "annealing up from {} to {} nodes".format(curr_max_nodes, self.max_nodes)
                if self.max_nodes > self.absolute_max_nodes:
                    if self.produce_printout:
                        print "Exceeded absolute_max_nodes of {}. Annealing back down to {} and quitting the level".format(self.absolute_max_nodes, self.max_nodes/self.max_nodes_annealing)
                    self.max_nodes /= self.max_nodes_annealing
                    self.stored_max_nodes = self.max_nodes
                    quit_level = True
                win, effects = False, []
                self.episodeRecord.insert(0, (win, effects))
                if self.saveMidEpisode:
                    self.saveEpisodeState(episodeSaveFile, effectsEncountered, statesEncountered, compactStates, annealing)
                    self.episodeSaveTime = time.time()

                output =          "Quitting.                                                       "
                # if self.produce_printout:
                print colored('________________________________________________________________', 'white', 'on_red')
                print colored(output, 'white', 'on_red')
                print colored('________________________________________________________________', 'white', 'on_red')

                return gameObject, False, self.rle._game.score, steps, statesEncountered, effectsEncountered, compactStates, quit_level


            annealing *= self.annealingFactor
            ended, win = self.rle._isDone()

            #ended = self.rle._game.ended # TODO momchil rm me
            
            if ended:
                self.episodeRecord.insert(0, (win, effects))
            
            if ended and not win and self.rle._game.time==2000:
                if self.produce_printout:
                    print "lost on timeout. switching hyperparameters"
                self.hyperparameterSwitch(new_index=1)


        score = self.rle._game.score

        # if self.produce_printout:
        if win:
            output =          "ended episode. Win={}                                         ".format(win)
        else:
            output =          "ended episode. Win={}                                        ".format(win)            
        if win:
            # print colored('________________________________________________________________', 'white', 'on_green')
            print colored('________________________________________________________________', 'white', 'on_green')

            print colored(output, 'white', 'on_green')
            print colored('________________________________________________________________', 'white', 'on_green')
        else:
            print colored('________________________________________________________________', 'white', 'on_red')
            print colored(output, 'white', 'on_red')
            print colored('________________________________________________________________', 'white', 'on_red')


        return gameObject, win, score, steps, statesEncountered, effectsEncountered, compactStates, quit_level


    def replayEpisode(self, gameObject, flexible_goals=False, win=False, first_time_playing_level=False, pool=None):
        # minimalist version of playEpisode exclusively dedicated to replay from human play
        # no planning, no bells & whistles
        # TODO momchil potentially dedupe / merge w/ playEpisode; had to do it separately b/c playEpisode kept breaking

        from vgdl.util import manhattanDist

        episodeSaveTime = time.time() ## in seconds
        quit_level = False
        ## Initialize external environment
        self.initializeEnvironment()
        if self.display_text:
            print "initializing RLE"
        # print "Game name:", self.gameFilename
        # print "Starting episode"
        # print "Playing level {}".format(self.n_level + 1)
        if self.produce_printout:
            print ""
            print self.rle.show(color='blue')

        self.quits = 0
        self.longHorizonObservations = 0
        self.previous_objects = self.all_objects if self.all_objects else {}
        self.all_objects= self.rle._game.getObjects()

        annealing = 1
        ## Start storing encountered states.
        effectsEncountered = []
        statesEncountered = []
        compactStates = [] ## for easy analysis of score over time.

        if self.make_movie or self.record_video_info:
            statesEncountered.append(self.rle._game.getFullState())
        
        self.last_recorded_time = time.time()
        if self.record_states:
            compactStates.append(self.compactify(self.rle))
        ## Initialize memory of object positions
        self.rle._game.objectMemoryDict, self.rle._game.previousPositions = {}, {}
        for k, v in self.rle._game.all_objects.iteritems():
            self.rle._game.objectMemoryDict[k] = (int(self.rle._game.all_objects[k]['sprite'].rect.x), int(self.rle._game.all_objects[k]['sprite'].rect.y))
            self.rle._game.previousPositions[k] = (int(self.rle._game.all_objects[k]['sprite'].rect.x), int(self.rle._game.all_objects[k]['sprite'].rect.y))

        ## initialize theory if necessary.
        if len(self.hypotheses) == 0:
            gameObject = self.initializeHypotheses(self.all_objects, statesEncountered, compactStates, learnSprites=True)
            if self.display_text:
                print "initializing hypotheses"
        else:
            gameObject = self.completeHypotheses(self.all_objects, statesEncountered, compactStates, first_time_playing_level)
            if self.display_text:
                print "had hypotheses -- completing them."
            # If theory is being carried over, falsify termination hypotheses
            # given new level state.
            if not flexible_goals:
                [t.updateTerminations(rle=self.rle) for t in self.hypotheses]


        ## Do beginning-of-episode Avatar resource-management.
        resources = self.rle._game.getAvatars()[0].resources
        for resource, val in resources.items():
            if resource not in self.seen_resources and val>0:
                self.seen_resources.append(resource)
                self.hypotheses[0].resource_limits[resource] = self.rle._game.resources_limits[resource]
            if resource not in self.seen_limits and val==self.rle._game.resources_limits[resource]:
                self.seen_limits.append(resource)

        ended, win = self.rle._isDone()

        legalActions = [0, K_UP, K_DOWN, K_LEFT, K_RIGHT]
        if self.hypotheses[0].classes['avatar'][0].args and 'stype' in self.hypotheses[0].classes['avatar'][0].args:
            legalActions.append(K_SPACE)

        steps = self.rle._game.time
        emptyPlans = 0
        while not ended:

            quitting = False

            action = -666 # TODO momchil maybe take it from replay here, and not in _performAction?

            plannerNodes = 0
            hypotheses, theory_change_flag, effects = self.executeStep(action, self.hypotheses, statesEncountered, compactStates, plannerNodes,
                run_induction = not flexible_goals)
            print 'HYPOTHESIS 4' # momchil
            hypotheses[0].display()

            self.rle._game.nextPositions = {}
            for k, v in self.rle._game.all_objects.iteritems():
                self.rle._game.nextPositions[k] = (int(self.rle._game.all_objects[k]['sprite'].rect.x), int(self.rle._game.all_objects[k]['sprite'].rect.y))
                try:
                    if self.rle._game.previousPositions[k] != self.rle._game.nextPositions[k]:
                        self.rle._game.objectMemoryDict[k] = copy.deepcopy(self.rle._game.previousPositions[k])
                except KeyError:
                    pass
            self.rle._game.previousPositions = copy.deepcopy(self.rle._game.nextPositions)

            effectsEncountered.extend(effects)
            steps +=1
            if theory_change_flag:
                self.hypotheses = hypotheses

            ended, win = self.rle._isDone()

            #ended = self.rle._game.ended # TODO momchil rm me

            self.max_game_time_observed = max(self.max_game_time_observed, self.rle._game.time)
            if ended:
                break

            if self.rle._game.playback_index == len(self.rle._game.playback_states):
                # TODO momchil make ended = true instead or something
                #embed()
                break


        score = self.rle._game.score

        quit_level = True 

        return gameObject, win, score, steps, statesEncountered, effectsEncountered, compactStates, quit_level

    def checkForRepeatedDeaths(self, episodeRecord, cutoff):
        ## Have we died the same way (i.e., killed by the same object) multiple times?
        count = 1
        for i in range(1, len(episodeRecord)):
            if episodeRecord[i][0]==False and episodeRecord[i][1]==episodeRecord[i-1][1]:
                count+=1
            else:
                break
        if count>cutoff:
            return True
        else:
            return False

    def noNewObjectsInAWhile(self, rle, age_cutoff):
        ## Avoids switching to long-range planning in games where, e.g., things spawn from time to time. For games like that it makes more sense to wait for spawns to happen, rather than assuming you're in a static environment.
        if self.hypotheses[0].classes['avatar'][0].args and 'stype' in self.hypotheses[0].classes['avatar'][0].args:
            thingWeShoot = self.hypotheses[0].classes['avatar'][0].args['stype']
        else:
            thingWeShoot = None         
        
        min_age = min([item.lastmove for sublist in self.rle._game.sprite_groups.values() for item in sublist if (item not in self.rle._game.kill_list and item.name not in [thingWeShoot, 'avatar'])])

        try:
            time_since_last_kill = self.rle._game.time - max([item.deathage for item in self.rle._game.kill_list if item.name!=thingWeShoot])
        except:
            time_since_last_kill = self.rle._game.time

        if (min_age > age_cutoff) and (time_since_last_kill > age_cutoff):
            return True
        else:
            return False

    def checkForMovingTypes(self, rle, hypothesis):
        ## Another check for whether we're in slow-moving games (where only we generate motion)
        if self.hypotheses[0].classes['avatar'][0].args and 'stype' in self.hypotheses[0].classes['avatar'][0].args:
            thingWeShoot = self.hypotheses[0].classes['avatar'][0].args['stype']
        else:
            thingWeShoot = None    
        moving_types = [k for k in hypothesis.classes.keys() if k!=thingWeShoot and any([t in str(hypothesis.classes[k][0].vgdlType) for t in ['Missile', 'Random', 'Chaser']])]
        moving_colors = [hypothesis.classes[k][0].color for k in moving_types]
        movingTypes = False
        if moving_colors:
            for s in [item for sublist in self.rle._game.sprite_groups.values() for item in sublist if item not in self.rle._game.kill_list]:
                if s.colorName in moving_colors:
                    movingTypes = True
                    break
        return movingTypes

    def checkForDangerOrAvatarMisLocation(self, rle, hypothesis, objectPositionsArray, i):
        
        ## For metacontroller to decide whether there's danger worth worrying about (like if something dangerous isn't where we predicted it would be), or if Avatar ended up in a location we didn't predict.

        regroundingFlag = False
        rleDict, hypDict = {}, {}

        for s in [item for sublist in objectPositionsArray[i+1]._game.sprite_groups.values() for item in sublist if item not in objectPositionsArray[i+1]._game.kill_list]:
            hypDict[s.ID2] = s

        killer_types = [inter.slot2 for inter in hypothesis.interactionSet if inter.slot1=='avatar' and inter.interaction in ['killSprite']]
        killer_colors = [hypothesis.classes[k][0].color for k in killer_types]

        for s in [item for sublist in self.rle._game.sprite_groups.values() for item in sublist if item not in self.rle._game.kill_list]:
            ## If the object isn't in our predicted environment or the positions vary
            if s.name=='avatar' or s.colorName in killer_colors:
                if s.ID not in hypDict and manhattanDist(s.rect, self.rle._game.getAvatars()[0].rect) < self.safeDistance*s.rect.width:

                    regroundingFlag=True
                    if self.produce_printout:
                        print colored("Regrounding because we didn't predict the appearance of {} and it's too close for comfort".format(s), 'white', 'on_yellow')
                    break
                if s.ID in hypDict and s.rect!=hypDict[s.ID].rect and manhattanDist(s.rect, self.rle._game.getAvatars()[0].rect) < self.safeDistance*s.rect.width:
                    if self.produce_printout:
                        print colored("Regrounding because distance between {} and {} is {}, which is less than the safe distance of {}. We thought it would be at {}".format(
                            s, self.rle._game.getAvatars()[0], manhattanDist(s.rect, self.rle._game.getAvatars()[0].rect), self.safeDistance*s.rect.width, hypDict[s.ID]),
                            'white', 'on_yellow')
                    regroundingFlag=True
                    break
                rleDict[s.ID] = s
        return regroundingFlag


    def saveCurriculumState(self, filename, episodeCompactStates):
        if 'pedro' in os.getcwd():
            return
        savedState = {'agent':self,
                      'episodeCompactStates': episodeCompactStates}
       
        with open(filename, 'wb') as f:
            cloudpickle.dump(savedState, f)
        # f.close()

    def saveEpisodeState(self, filename, effectsEncountered, statesEncountered, compactStates, annealing):
        if 'pedro' in os.getcwd():
            return
        print "starting to save episode state"
        savedState = {'agent':self,
                      'effectsEncountered': effectsEncountered,
                      'statesEncountered': statesEncountered,
                      'compactStates': compactStates,
                      'annealing': annealing
                      }
        filepath = 'savedCurricula/'+filename

        with open(filepath, 'wb') as f:
            cloudpickle.dump(savedState, f)
        print "done saving state"

    def loadState(self, filename):
        with open(filename, 'r') as f:
            loadedState = cloudpickle.load(f)
        # f.close()
        return loadedState

    def saveState(self):
        filename = 'saved_state'
        with open(filename, 'wb') as f:
            cloudpickle.dump(self, f)
        return

    def matchEventToRuleByIDAndSpriteName(self, event, rule):
        # Check if the two objects involved in the
        # event are the same as those in the novelty
        # termination rule (invariant by order)

        if event[1] not in self.hypotheses[0].spriteObjects:
            self.hypotheses[0].addSpriteToTheory(event[1])
        if event[2] not in self.hypotheses[0].spriteObjects:
            self.hypotheses[0].addSpriteToTheory(event[2])
    
        try:
            hypSlot1 = self.hypotheses[0].spriteObjects[event[1]].className
            hypSlot2 = self.hypotheses[0].spriteObjects[event[2]].className
        except:
            print "hypslot problem in main agent"
            embed()


        if set([hypSlot1, hypSlot2]) == set([rule.slot1, rule.slot2]):
            if not rule.preconditions:
                return True
            else:
                if not all([p.check(self.rle.agentStatePrev) for p in list(rule.preconditions)]):
                    return False
                else:
                    return True
        else:
            return False

    def manageNewObjects(self, hypotheses):
        ## Add newly-seen objects.
        current_objects = self.rle._game.getObjects()
        for k in current_objects.keys():
            spriteName = current_objects[k]['sprite'].name
            if spriteName not in [self.all_objects[key]['sprite'].name for key in self.all_objects.keys()]:
                if self.display_text:
                    print "new object", spriteName
                self.all_objects[k] = current_objects[k]
                distributionInitSetup(self.rle._game, k)
                ## prevent spriteInduction from trying to infer anything about newly-appeared sprites in this timestep.
                self.rle._game.ignoreList.append(k)
                self.new_objects[spriteName] = 0

        return hypotheses

    def observe(self, rle, obsSteps, bestSpriteTypeDict, statesEncountered, compactStates, display=False, hypothesis=None):
        if display and self.produce_printout:
            print "observing for {} steps".format(obsSteps)

        if obsSteps>0:
            for i in range(obsSteps):

                if self.record_fMRIRegressors:
                    spriteDistributionPrev = self.rle._game.spriteDistribution.copy()

                spriteInduction(rle._game, step=1, bestSpriteTypeDict=bestSpriteTypeDict, dynamic_type_lesion=self.dynamic_type_lesion)
                spriteInduction(rle._game, step=2, bestSpriteTypeDict=bestSpriteTypeDict, dynamic_type_lesion=self.dynamic_type_lesion)
                rle.step((0,0))  # TODO momchil ensure this works with replay; probs not -- it assumes no action was taken, when in fact it might have been taken in replay

                if self.make_movie or self.record_video_info:
                    statesEncountered.append(self.rle._game.getFullState(observe_state=True)) # momchil
                if self.record_states:
                    compactStates.append(self.compactify(self.rle))
                if self.produce_printout:
                    print "score: {}, timestep: {}".format(rle._game.score, rle._game.time)
                    print rle.show(color='blue')
                print "action", self.total_game_steps+rle._game.time
                rle._game.nextPositions = {}
                for k, v in rle._game.all_objects.iteritems():
                    rle._game.nextPositions[k] = (int(rle._game.all_objects[k]['sprite'].rect.x), int(rle._game.all_objects[k]['sprite'].rect.y))
                    try:
                        if rle._game.previousPositions[k] != rle._game.nextPositions[k]:
                            rle._game.objectMemoryDict[k] = copy.deepcopy(rle._game.previousPositions[k])
                    except KeyError:
                        pass
                rle._game.previousPositions = copy.deepcopy(rle._game.nextPositions)

                spriteInduction(rle._game, step=3, bestSpriteTypeDict=bestSpriteTypeDict)
                if hypothesis:
                    rle._game.H = self.calculateEntropy(hypothesis, self.rle._game.spriteDistribution)
                    compactStates[-1]['entropy'] = rle._game.H

                if self.record_fMRIRegressors:
                    spriteKL = getKL(self.rle._game.spriteDistribution, spriteDistributionPrev)
                    self.regressors['spriteKL'].append((spriteKL, self.rle._game.time))
                    if hypothesis:
                        self.regressors['theory'].append((copy.deepcopy(hypothesis), self.rle._game.time))
        else:
            spriteInduction(rle._game, step=1, bestSpriteTypeDict=bestSpriteTypeDict, dynamic_type_lesion=self.dynamic_type_lesion)
            spriteInduction(rle._game, step=2, bestSpriteTypeDict=bestSpriteTypeDict, dynamic_type_lesion=self.dynamic_type_lesion)
            if hypothesis:
                rle._game.H = self.calculateEntropy(hypothesis, self.rle._game.spriteDistribution)

        return

    def executeStep(self, action, hypotheses, statesEncountered, compactStates, plannerNodes, run_induction=True):

        theory_change_flag = False

        if self.record_fMRIRegressors:
            spriteDistributionPrev = self.rle._game.spriteDistribution.copy()

        if not self.skipInduction:
            # t1 = time.time()
            spriteInduction(self.rle._game, step=1, bestSpriteTypeDict=self.bestSpriteTypeDict, oldSpriteSet=hypotheses[0].spriteSet, dynamic_type_lesion=self.dynamic_type_lesion)
            # print "induction step 1 took {} seconds.".format(time.time()-t1)
            t1 = time.time()
            spriteInduction(self.rle._game, step=2, bestSpriteTypeDict=self.bestSpriteTypeDict, oldSpriteSet=hypotheses[0].spriteSet, dynamic_type_lesion=self.dynamic_type_lesion)
            # print "induction step 2 took {} seconds".format(time.time()-t1)
        try:
            agentState = copy.deepcopy(self.rle._game.getAvatars()[0].resources)
        except IndexError:
            agentState = defaultdict(lambda: 0)

        lastScore = self.rle._game.score
        res = self.rle.step(action, regressors=self.regressors)

        if self.rle._game.playback_states:
            # off-policy training from human replay
            #
            action = res['action']
        print 'action ============================ ', action
        pprint(res)

        try:
            agentState = copy.deepcopy(self.rle._game.getAvatars()[0].resources)

            for e in res['effectList']:
                if 'changeResource' in e:
                    changes = e[3]
                    if changes['value'] < 0:
                        # undo one negative change to account for eventhandler ordering
                        agentState[changes['resource']] -= changes['value']
                        break

            self.rle.agentStatePrev = agentState

        # If agent is killed before we get agentState
        except (IndexError, AttributeError) as e:
            ignored_negative_change = False
            for e in res['effectList']:
                if 'changeResource' in e:
                    changes = e[3]
                    if changes['value'] > 0 or ignored_negative_change:
                        agentState[changes['resource']] += changes['value']
                    else:
                        agentState[changes['resource']] += 0
                        ignored_negative_change = True
            self.rle.agentStatePrev = agentState
        for k,v in agentState.items():
            agentState[k] = max(0, v)

        t1 = time.time()
        hypotheses = self.manageNewObjects(hypotheses)

        if self.make_movie or self.record_video_info:
            statesEncountered.append(self.rle._game.getFullState())
        if self.record_states:
            compactStates.append(self.compactify(self.rle, plannerNodes))

        t1 = time.time()
        if not self.skipInduction:
            distributionsHaveChanged = spriteInduction(self.rle._game, step=3, bestSpriteTypeDict=self.bestSpriteTypeDict, oldSpriteSet=hypotheses[0].spriteSet)

            if self.record_fMRIRegressors:
                spriteKL = getKL(self.rle._game.spriteDistribution, spriteDistributionPrev)
                self.regressors['spriteKL'].append((spriteKL, self.rle._game.time))
        else:
            distributionsHaveChanged = False
 
        ## First interaction-rule lesion:
        effects = self.rle._game.effectListByColor
        if self.interaction_lesion_replacement == 'nothing':
            for i,e in enumerate(effects):
                if e[0] in self.disallowed_events:
                    print "replacing", e
                    effects[i] = ('nothing', e[1], e[2])
                    print "with", effects[i]
                    print ""

        if self.display_states:
            print "score: {}, game step: {}".format(self.rle._game.score, self.rle._game.time)

        # t1 = time.time()
        print "action", self.total_game_steps+self.rle._game.time
        if self.produce_printout:
            print ""
            print keyPresses[action]
            print self.rle.show(color='blue')

        event = {'agentState': agentState, 'agentAction': action, 'effectList': effects, \
            'gameState': None, 'rle': self.rle}

        newEffects = False

        if effects:
            if self.display_text:
                print effects
            # #  PRECONDITIONS HANDLING
            # # Current assumptions:
            # # - Only one resource can change for each timestep
            # # - The first time a resource changes, it goes from 0 to a positive value
            for change_resource_effect in [e[3] for e in event['effectList'] if ('changeResource' in e)] + [e[3] for e in event['effectList'] if ('collectResource' in e)]:
                resource = change_resource_effect['resource']
                val = change_resource_effect['value']
                limit = change_resource_effect['limit']
                if (resource not in self.seen_resources and val>0):
                    self.fakeInteractionRules.extend(hypotheses[0].updateInteractionsPreconditions(resource))
                    self.fakeInteractionRules = list(set(self.fakeInteractionRules))
                    self.seen_resources.append(resource)
                    hypotheses[0].resource_limits[resource] = limit
                    theory_change_flag = True
                    newEffects = True
                    self.finalEffectList = set()

                if agentState[resource]>=limit and resource not in self.seen_limits:
                    self.fakeInteractionRules.extend(hypotheses[0].updateInteractionsPreconditions(resource, limit))
                    self.fakeInteractionRules = list(set(self.fakeInteractionRules))
                    self.seen_limits.append(resource)

                    theory_change_flag = True
                    newEffects = True
                    self.finalEffectList = set()

            self.finalEventList.append(event)
            newTimeStep = TimeStep(event['agentAction'], event['agentState'], event['effectList'], event['gameState'], event['rle'])
            self.finalTimeStepList.append(newTimeStep)
            for e in effects:
                compactEvent = (e[0], e[1], e[2])
                if compactEvent not in self.finalEffectList:
                    self.finalEffectList.add(compactEvent)
                    if self.display_text:
                        print "New event: {}".format(compactEvent)
                    newEffects = True
        
        self.fakeInteractionRules = [r for r in self.fakeInteractionRules if
            not any([self.matchEventToRuleByIDAndSpriteName(e, r) for e in event['effectList']])]

        if ((newEffects or (random.random()<.2 and len(self.finalTimeStepList)<300)) and run_induction) or distributionsHaveChanged:
            # print "event", (not all([e in all_effects for e in effects])), "distributions changed", distributionsHaveChanged
            if self.display_text:
                print "new event", newEffects, "distributions changed", distributionsHaveChanged

            if newEffects or distributionsHaveChanged:
                theory_change_flag = True

            t1 = time.time()
            sample, exceptedObjects, _, self.best_params= sampleFromDistribution(self.rle._game, self.rle._game.spriteDistribution, self.all_objects, 
                    self.rle._game.spriteUpdateDict, self.bestSpriteTypeDict, self.hypotheses[0].spriteSet, skipInduction=self.skipInduction, display=self.display_text)

            game_object = Game(spriteInductionResult=sample)
            
            terminationCondition = {'ended': False, 'win':False, 'time':self.rle._game.time}
            trace = (self.finalTimeStepList, terminationCondition) # momchil do we ever empty finalTimeStepList? across levels/games?

            t1 = time.time()
            hypotheses = list(game_object.runInduction(game_object.spriteInductionResult, trace, 20, \
            verbose=False, existingTheories=hypotheses))

            if self.record_fMRIRegressors:
                # calculate postarior of old hypotheses
                P = getPosterior(self.hypotheses, self.finalTimeStepList)
                if self.hypothesesPosterior: # posterior on prev timestep
                    # TODO momchil maybe augment old posterior with new hypotheses for better approximation of KL
                    # (need to exclude latest timesteps when computing likelihood though)
                    sampleKL = scipy.stats.entropy(P, self.hypothesesPosterior)
                    self.regressors['sampleKL'].append((sampleKL, self.rle._game.time))

                # calculate posterior using new hypotheses for next timestep
                self.hypothesesPosterior = getPosterior(hypotheses, self.finalTimeStepList)

            if hypotheses[0].__dict__ != self.hypotheses[0].__dict__:
                theory_change_flag = True

        ## We need to update termination conditions even when we haven't seen a new event,
        ## because the state is informative about termination conditions.
        oldTerminationSet = set(hypotheses[0].terminationSet)
        if event['effectList'] and run_induction:
            [t.updateTerminations(event=event) for t in hypotheses]

        self.rle._game.H = self.calculateEntropy(hypotheses[0], self.rle._game.spriteDistribution)
        statesEncountered[-1]['entropy'] = self.rle._game.H

        if set(hypotheses[0].terminationSet) != oldTerminationSet:
            if self.display_text:
                print "terminationSet Change"
            theory_change_flag = True

        if theory_change_flag and not distributionsHaveChanged and self.display_text:
            print "changed theory:"
            hypotheses[0].display()

        if self.record_fMRIRegressors:
            self.regressors['theory_change_flag'].append((theory_change_flag, self.rle._game.time))
            self.regressors['sprite_change_flag'].append((distributionsHaveChanged, self.rle._game.time))
            self.regressors['interaction_change_flag'].append((hypotheses[0].__dict__ != self.hypotheses[0].__dict__, self.rle._game.time))
            self.regressors['termination_change_flag'].append((set(hypotheses[0].terminationSet) != oldTerminationSet, self.rle._game.time))
            self.regressors['theory'].append((copy.deepcopy(hypotheses[0]), self.rle._game.time))

        return hypotheses, theory_change_flag, effects



if __name__ == "__main__":

    filename = "examples.gridphysics.theory_overload"

    level_game_pairs = None
    # Playing GVG-AI games
    def read_gvgai_game(filename):
        with open(filename, 'r') as f:
            new_doc = []
            g = gen_color()
            for line in f.readlines():
                new_line = (" ".join([string if string[:4]!="img="
                    else "color={}".format(next(g))
                    for string in line.split(" ")]))
                new_doc.append(new_line)
            new_doc = "\n".join(new_doc)
        return new_doc

    def gen_color():
        from vgdl.colors import colorDict
        color_list = colorDict.values()
        color_list = [c for c in color_list if c not in ['UUWSWF']]
        for color in color_list:
            yield color

    gvggames = ['aliens', 'boulderdash', 'butterflies', 'chase', 'frogs',  # 0-4
        'missilecommand', 'portals', 'sokoban', 'survivezombies', 'zelda']  # 5-9

    # gameName = gvggames[5]

    # gvgname = "../gvgai/training_set_1/{}".format(gameName)

    # gameString = read_gvgai_game('{}.txt'.format(gvgname))


    # level_game_pairs = []
    # for level_number in range(5):
        # with open('{}_lvl{}.txt'.format(    gvgname, level_number), 'r') as level:
            # level_game_pairs.append([gameString, level.read()])

    ##uncomment this line to run local games
    gameName = filename

    hyperparameter_sets = [{'idx'           : 2,
     'short_horizon' : False,
     'first_order_horizon': False,
     'sprite_first_alpha': 10000,
     'sprite_second_alpha': 100,
     'sprite_negative_mult': .1,
     'multisprite_first_alpha': 10000,
     'multisprite_second_alpha': 100,
     'novelty_first_alpha': 5000,
     'novelty_second_alpha': 50,
     }]

    agent = Agent('full', gameName, hyperparameter_sets[0])

    ##then pass this down for multiple episodes
    gameObject = None
    agent.playCurriculum(level_game_pairs=level_game_pairs)

    ##and use this line
    # agent.playCurriculum(level_game_pairs=None)
