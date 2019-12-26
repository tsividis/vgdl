from util import *
from core import colorDict, VGDLParser, sys, keyPresses
from ontology import *
from theory_template import TimeStep, Precondition, InteractionRule, TerminationRule, TimeoutRule, \
SpriteCounterRule, MultiSpriteCounterRule, ruleCluster, Theory, Game, writeTheoryToTxt, generateSymbolDict, \
generateTheoryFromGame
import os, subprocess, shutil
from collections import defaultdict
from hyperparameters import hyperparameter_sets, metacontroller_sets
from math import log
import WBP
import importlib
import numpy as np
import random
import cPickle, cloudpickle
import time
from datetime import datetime
import copy
from agent_utils import translate_events
from rlenvironmentnonstatic import createRLInputGame, createRLInputGameFromStrings, defInputGame, createMindEnv
from dynamic_type_inference import dynamicTypeDistribution_VGDL1
from termcolor import colored
from pygame import K_LEFT, K_UP, K_RIGHT, K_DOWN, K_SPACE


MAX_STEPS = 10000
actionDict = {K_SPACE: 'space', K_UP: 'up', K_DOWN: 'down', K_LEFT: 'left', K_RIGHT: 'right', 0:'none'}
AvatarTypes = [MovingAvatar, HorizontalAvatar, VerticalAvatar, FlakAvatar, AimedFlakAvatar, OrientedAvatar,
RotatingAvatar, RotatingFlippingAvatar, NoisyRotatingFlippingAvatar, ShootAvatar, AimedAvatar,
AimedFlakAvatar, InertialAvatar, MarioAvatar]


class Metacontroller:
    def __init__(self, agent):
        self.agent = agent
        self.display_text = self.agent.display_text
        self.quitting = False

    def checkForRepeatedDeaths(self):
        return self.agent.checkForRepeatedDeaths(self.agent.episodeRecord, 2)

    def checkForMovingTypes(self, env):
        return self.agent.checkForMovingTypes(env, self.agent.hypotheses[0])

    def noNewObjectsInAWhile(self, env):
        return self.agent.noNewObjectsInAWhile(env, self.agent.noNewObjectNum)

    def testSwitchHyperparams(self, new_hyperparameter):
        self.agent.hyperparameter_index = new_hyperparameter

    def setMaxNodes(self):
        ## You don't anneal max_nodes up for shortHorizon planning. Randomly pick a horizon from [200,500,1000] each time. (Did this to save on compute -- doing 1k each time would be strictly better).
        if self.agent.shortHorizon and self.agent.shortHorizonRandomChoice:
            self.agent.max_nodes = random.choice(self.agent.shortHorizonRandomChoice)
        else:
            self.agent.max_nodes = self.agent.stored_max_nodes

        if self.agent.produce_printout:
            print "==============================================================="
            print "planning with max_nodes: {}, short_horizon: {}".format(self.agent.max_nodes, self.agent.shortHorizon)

    def annealUp(self):
        ## Agent failed the game either because it made a mistake it couldn't recover from or because search timed out.
        ## Search more deeply next time.
        quit_level = False
        curr_max_nodes = self.agent.max_nodes
        self.agent.max_nodes *= self.agent.max_nodes_annealing
        self.agent.stored_max_nodes = self.agent.max_nodes
        if self.agent.produce_printout:
            print "annealing up from {} to {} nodes".format(curr_max_nodes, self.agent.max_nodes)
        if self.agent.max_nodes > self.agent.absolute_max_nodes:
            if self.agent.produce_printout:
                print "Exceeded absolute_max_nodes of {}. Annealing back down to {} and quitting the level".format(self.absolute_max_nodes, self.agent.max_nodes/self.agent.max_nodes_annealing)
            self.agent.max_nodes /= self.agent.max_nodes_annealing
            self.agent.stored_max_nodes = self.agent.max_nodes
            quit_level = True
        return quit_level

    ##overload the agent functions so that you can call them directly from here
    ##TODO: change self.rle in here to env

    def determinePlanningModeAndReplanIfNecessary(self, solution, env, planner_recommended_quitting):
        self.display_text = True
        self.agent.produce_printout = True
        if not solution:
            ## If planner didn't give a solution, switch modes according to metacontroller policy
            if self.checkForRepeatedDeaths():
                if self.agent.hyperparameter_index == 'long-term':
                    new_index = 'long-term' ## don't switch away from idx_1
                    conservative = False
                if self.agent.hyperparameter_index == 'short-term':
                    if self.display_text:
                        print "Repeated deaths. Switching to long-range planning"
                    new_index = 'long-term'
                    conservative = False
                planner_hyperparameters = self.agent.hyperparameterSwitch(new_index=new_index)

            elif self.agent.hyperparameter_index == 'short-term':
                movingTypes = self.checkForMovingTypes(env)
                if env.getTime()>self.agent.bookkeeping.compactStates[-1]['timestep']:
                    scoreChange = env.getScore()!=self.agent.bookkeeping.compactStates[-1]['score']
                else:
                    scoreChange = True
                if self.display_text:
                    print "moving types: {}".format(movingTypes)
                    print "noNewObjectsInAWhile: {}".format(self.noNewObjectsInAWhile(env))
                    print "scoreChange: {}".format(scoreChange)
                if self.noNewObjectsInAWhile(env) and \
                        (not movingTypes or (movingTypes and not scoreChange)):
                    if self.agent.produce_printout:
                        print "switching to long-range planning"
                    ## switch to long-range planning
                    new_index = 'long-term'
                    planner_hyperparameters = self.agent.hyperparameterSwitch(new_index=new_index)
                    conservative = False
                else:
                    if self.agent.produce_printout:
                        print "planning in 'stall' mode"
                    new_index = 'short-term'
                    planner_hyperparameters = self.agent.hyperparameterSwitch(new_index=new_index)
                    conservative = True
                    self.agent.stored_max_nodes = self.agent.max_nodes ##taking annealing into account
                    self.agent.max_nodes = self.agent.conservative_max_nodes
            else:
                conservative = False
            if self.display_text:
                print "planning in {} mode".format(self.agent.hyperparameter_index)
                print "max_nodes: {}, short_horizon: {}, conservative: {}".format(self.agent.max_nodes, self.agent.shortHorizon, conservative)

            # TODO: Implement conservative mode as a separate mode.
            if conservative: #aka 'stall' mode
                ## Replan in new mode
                p = WBP.WBP(self.agent.theoryRLEs[0], self.agent.gameFilename, theory=self.agent.hypotheses[0], fakeInteractionRules = self.agent.fakeInteractionRules,
                    seen_limits = self.agent.seen_limits, annealing=self.agent.annealing, max_nodes=self.agent.max_nodes, shortHorizon=self.agent.shortHorizon,
                    firstOrderHorizon=self.agent.firstOrderHorizon, conservative=conservative, hyperparameters=planner_hyperparameters, 
                    extra_atom=self.agent.extra_atom, IW_k=self.agent.IW_k, objectNumberTrackingLimit=self.agent.objectNumberTrackingLimit,
                    objectLocationTrackingLimit=self.agent.objectLocationTrackingLimit, lesion=self.agent.planner_lesion)
                planner_recommended_quitting = p.quitting
                bestNode, gameStringArray, objectPositionsArray = p.BFS()
                self.agent.total_planner_steps += p.total_nodes_opened
                self.agent.planner_nodes_opened_on_most_recent_step = p.total_nodes_opened
                # print "total planner steps in main_agent:", self.total_planner_steps
                if bestNode is not None:
                    solution = p.solution
                    gameString_array = p.gameString_array
                    self.agent.objectPositionsArray = objectPositionsArray[::-1]
                    if solution and self.display_text:
                        print "got solution"
                else:
                    solution = []
        self.agent.takingRandomSteps = False

        if (not solution) or planner_recommended_quitting:
            # Here we make a distinction between quitting because you've
            # exhausted the number of nodes you can visit or because you
            # ran out of novelty. In the first case, you only wait longer,
            # in the second case, you also add a new atom to IW
            if self.agent.extra_atom_allowed:
                if self.display_text:
                    print "turning on extra atom"
                self.agent.extra_atom = True
            
            ## if you don't get a plan with short-horizon mode you'll plan in stall mode. You only get here if you're in long-term planning and don't find a plan.

            if self.agent.longHorizonObservations<self.agent.longHorizonObservationLimit: 
                if self.agent.produce_printout:
                    print "Didn't get solution. Taking {} random steps and then replanning".format(self.agent.random_steps_on_plan_failure)
                solution = [] ## You may have gotten p.quitting but also a solution; make sure you don't try to act on that if the planner decided it wasn't worth it.
                for i in range(self.agent.random_steps_on_plan_failure):
                    solution.append(random.choice(self.agent.hypotheses[0].getLegalActions()
))
                self.agent.longHorizonObservations += 1
                self.agent.takingRandomSteps = True
            else:
                self.quitting = True
                print "DECIDING TO QUIT"

        else:
            print "No need to switch hyperparameters. Staying in {} mode".format(self.agent.hyperparameter_index)

        return solution
class Memory:
    def __init__(self):
        self.ignoreList = []
        self.objectMemoryDict = {}
        self.previousPositions = {}
        self.nextPositions = {}
        self.spriteUpdateDict = defaultdict(lambda : 0)
        self.totalGameSteps = 0
        self.episodeSteps = 0

class Bookkeeping:
    def __init__(self, saveMidEpisode, task_ID, param_ID, gameFilename):
        self.saveMidEpisode = saveMidEpisode
        self.task_ID = task_ID
        self.param_ID = param_ID
        self.gameFilename = gameFilename
        self.episodeSaveFile = None
        self.curriculumDir = 'savedCurricula'
        self.curriculumSaveFile = 'curriculum_'+self.gameFilename+'_'+self.param_ID+'_'+self.task_ID
        self.effectsEncountered = []
        self.statesEncountered = []
        self.compactStates = []

        if self.curriculumDir not in os.listdir('.'):
            os.makedirs(self.curriculumDir)

    def saveCurriculumState(self, agent, episodeCompactStates):
        if 'pedro' in os.getcwd():
            return
        filename = self.curriculumDir+'/'+curriculumSaveFile
        savedState = {'agent':agent,
                      'episodeCompactStates': episodeCompactStates}
        with open(filename, 'wb') as f:
            cloudpickle.dump(savedState, f)

    def saveEpisodeState(self, agent, annealing):
        
        if not self.saveMidEpisode:
            return

        # if 'pedro' in os.getcwd():
            # return

        filename = self.episodeSaveFile

        print "starting to save episode state"
        savedState = {'agent':agent,
                      'effectsEncountered': self.effectsEncountered,
                      'statesEncountered': self.statesEncountered,
                      'compactStates': self.compactStates,
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

    def loadCurriculumState(self, filename):
        ## For runs on cluster that may get interrupted -- if you find a saved state for this particular agent, load that and run from there.
        if filename in os.listdir(self.curriculumDir):
            try:
                print "found saved curriculum state"
                loadedState = self.loadState(self.curriculumDir+'/'+filename)
                print "loaded curriculum state"
                return loadedState
            except:
                os.remove(self.curriculumDir+'/'+filename)
                print "failed to load curriculum state. deleting corrupted file and starting from scratch"
                return None

    def deleteEpisodeFile(self):
        if self.saveMidEpisode:
            ## if the episode ends, delete the mid-episode file we were saving.
            self.episodeSaveFile = 'episode_'+self.gameFilename+'_'+self.task_ID
            os.remove(self.curriculumDir+'/'+self.episodeSaveFile)
            print "finished an episode; removing episodeSaveFile"


class Agent:
    def __init__(self, modelType, gameFilename, hyperparameter_sets, hyperparameter_index=3, metacontroller_index=0, IW_k=2, extra_atom_allowed=True, task_ID=0, produce_printout=False, movieName=None):
        self.modelType = modelType
        self.gameFilename = gameFilename
        self.gameString = None
        self.levelString = None
        self.display_text = False
        self.display_states = False
        self.record_states = True
        self.record_video_info = True
        self.write_video_info = True
        self.saveMidEpisode = False
        self.filename = None
        self.timestamp = False
        self.task_ID = task_ID
        self.loaded_n_level = 0
        self.produce_printout = produce_printout
        self.movieName = movieName
        ## Main params are loaded from hyperparameters.py
        self.hyperparameter_sets = hyperparameter_sets
        self.hyperparameter_index = 'short-term'
        self.hyperparameters = hyperparameter_sets[self.hyperparameter_index]
        self.annealingFactor = 1. # meaningless
        self.annealing = 1.
        self.shortHorizon = self.hyperparameters['short_horizon'] # Params used in short-horizon planning
        self.firstOrderHorizon = self.hyperparameters['first_order_horizon'] # Makes agent commit to a plan once first-order distances change (e.g., spritecounter values)
        self.IW_k = IW_k # Only using IW 1
        self.extra_atom_allowed = extra_atom_allowed # Adding optional extra atom to IW
        self.epsilon_greedy = False # Ablation
        self.switch_to_exploit_step = 1000 # Used for e-greedy ablation
        self.absolute_max_nodes = 50000 # Just a convenience parameter
        self.shortHorizonNodes = 500 ## This isn't used, but code needs further cleanup to actually delete it.
        self.shortHorizonAnnealing = 1.05 ##  This isn't used, but code needs further cleanup to actually delete it.
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
        ## Planner ablations
        ## AGH1 = goal gradient only | AGH2=subgoal only | AGH3=goal gradient + subgoal
        self.planner_lesion = self.metacontroller_params['planner_lesion'] if 'planner_lesion' in self.metacontroller_params else []
        ## Additonal lesions (not completed)
        self.dynamic_type_lesion = self.metacontroller_params['dynamic_type_lesion'] if 'dynamic_type_lesion' in self.metacontroller_params else []
        self.interaction_lesion = self.metacontroller_params['interaction_lesion'] if 'interaction_lesion' in self.metacontroller_params else []
        self.interaction_lesion_replacement = self.metacontroller_params['interaction_lesion_replacement'] if 'interaction_lesion_replacement' in self.metacontroller_params else []
        self.disallowed_events = self.interaction_lesion

        ## Planner ignores objects thought to move randomly and objects that don't persist (e.g. swords that flash
        ## in and out of existence) when applying IW criteria
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

        ## Longer-format param_ID string. Use this if you want all the info (e.g., for hyperparameter tuning)
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

        self.distribution = None
        self.hypotheses = []
        self.symbolDict = None
        self.finalEventList = []
        self.finalEffectList = set()
        self.finalTimeStepList = []
        self.rleHistory = []
        self.episodeRecord = []
        self.fakeInteractionRules = []
        self.all_objects = {}
        self.bestSpriteTypeDict = defaultdict(lambda : {})
        self.max_game_time_observed = 0
        self.best_params = None
        self.seen_resources = []
        self.seen_limits = []
        self.new_objects = {}


        self.objectPositionsArray = [] ##TODO: Pass to memory
        self.planner_nodes_opened_on_most_recent_step = 0
        self.memory = Memory()
        self.bookkeeping = Bookkeeping(self.saveMidEpisode, self.task_ID, self.param_ID, self.gameFilename)
        self.metacontroller = Metacontroller(self)

        self.total_planner_steps = 0
        self.levels_won = 0


        ## used for time-stamping data related to this particular run of the model.
        timestamp = datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d__%H_%M__')+self.task_ID
        
        self.timestamp = timestamp

        if self.record_states:
            # dirname = "results/{}/{}/".format(self.param_ID, self.gameFilename) # old data location
            # print "in main_agent"
            # print os.getcwd()
            dirname_for_results = "../data/demo_data_files/EMPA/local/results/{}/{}/".format(self.param_ID, self.gameFilename)
            filename = "{}{}_{}".format(dirname_for_results, self.gameFilename, self.timestamp)
            self.filename = filename
            if not os.path.exists(dirname_for_results):
                try:
                    # print "path didn't exist; making", dirname
                    os.makedirs(dirname_for_results)
                except:
                    print "failed  to make dir {} in main_agent.py".format(dirname_for_results)
        if self.write_video_info:
            self.dirname_for_video = "raw_video_info/{}/{}/".format(self.param_ID, self.gameFilename)
            if not os.path.exists(self.dirname_for_video):
                os.makedirs(self.dirname_for_video)


    # ---------------------------------------------------------------------
    #     Simulator initialization functions
    # ---------------------------------------------------------------------
    def initializeEnvironment(self):
        ## Initialize game environment

        if self.display_text:
            print "initializing RLE"

        if self.gameString==None or self.levelString==None:
            self.gameString, self.levelString = defInputGame(self.gameFilename, randomize=False)
        self.rleCreateFunc = lambda: createRLInputGameFromStrings(self.gameString, self.levelString)
        self.rle = self.rleCreateFunc()
        return

    def initializeRLEFromGame(self):
        ## Part of a method for faster state copying, used in planner, etc.
        gameString, levelString = self.gameString, self.levelString
        if gameString == None or levelString == None:
            gameString, levelString = defInputGame(self.gameFilename, randomize=False)
        rleCreateFunc = lambda: createRLInputGameFromStrings(gameString, levelString)
        rle = rleCreateFunc()
        return rle

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

    def getSpritesByColor(self, rle, color):
        outList = []
        spriteGroups = rle.getSpriteGroups()
        for k in spriteGroups.keys():
            if spriteGroups[k] and spriteGroups[k][0].colorName==color:
                outList.extend(spriteGroups[k])
        if outList:
            return outList
        else:
            return None

    def find_nearest_sprite(self, sprite, spriteList):
        ## returns the sprite in spriteList whose location best matches the location of sprite.
        return sorted(spriteList, key=lambda x:abs(x.rect[0]-sprite.rect[0])+abs(x.rect[1]-sprite.rect[1]))[0]

    def setSpritePositions(self, rle, Vrle, hypothesis):
        ## Sets positions of objects in Vrle to what they were in the rle. E.g., if we want to start a simulation according to the model specified by 'hypothesis' at the state contained in 'rle', this will return Vrle: a playable game whose rules run according to the model.

        old_sprite_groups = Vrle.getSpriteGroups()
        for k in old_sprite_groups.keys():
            if old_sprite_groups[k]:
                color = Vrle.getSpriteGroups()[k][0].colorName
                matchingSpritesInRLE = self.getSpritesByColor(rle, color)
                for sprite in old_sprite_groups[k]:
                    matchingSprite = self.find_nearest_sprite(sprite, matchingSpritesInRLE)
                    sprite.rect = matchingSprite.rect
                    sprite.lastmove = matchingSprite.lastmove
                    sprite.ID2 = matchingSprite.ID
                    if 'Missile' in str(hypothesis.classes[sprite.name][0].vgdlType) and self.best_params!=None:
                        try:
                            ## Enforce consistency: inferred value for individual orientations has to be consistent with what we're saying the horizontal/vertical orientation is of the entire group.

                            orientation = tuple(np.sign(np.array(self.memory.previousPositions[matchingSprite.ID]) - np.array(self.memory.objectMemoryDict[matchingSprite.ID])))
                            if orientation == (0,0):
                                # print "found 0,0 orientation. Using generic missile orientation:", sprite.orientation, sprite.speed, sprite.cooldown
                                pass
                            else:
                                sprite.orientation = orientation

                        except KeyError:
                            sprite.orientation = random.choice([(0,1), (0,-1), (1,0), (-1,0)])

        return

    def initializeVrle(self, hypothesis):
        ## Returns simulatable world in agent's head given 'hypothesis', including object goal
        gameString, levelString, symbolDict = writeTheoryToTxt(self.rle, hypothesis, self.symbolDict,\
                 "./theory_files/{}.py".format(self.gameFilename))
        Vrle = createMindEnv(gameString, levelString, output=False)

        self.setSpritePositions(self.rle, Vrle, hypothesis)
        try:
            Vrle.getAvatars()[0].resources = copy.deepcopy(self.rle.getAvatars()[0].resources)
            Vrle.getAvatars()[0].orientation = copy.deepcopy(self.rle.getAvatars()[0].orientation)
        except (IndexError, AttributeError) as e:
            pass
        return Vrle

    def VrleInitPhase(self):
        ## Initialize multiple VRLEs, each corresponding to one hypothesis in self.hypotheses. In practice we only use one.
        VRLEs = []

        for hypothesis in self.hypotheses[0:1]:
            tempHypothesis = copy.deepcopy(hypothesis)
            tmpFakeInteractionRules = copy.deepcopy(self.fakeInteractionRules)
            tempHypothesis.interactionSet.extend(tmpFakeInteractionRules)
            tempHypothesis.updateTerminations()
            VRLEs.append(self.initializeVrle(tempHypothesis))

        return VRLEs

    def initializeHypotheses(self, allObjects, statesEncountered, compactStates):
        ## Creates initial hypothesis objects by observing the game,
        ## doing initial inference over sprite types, and returning partial
        ## candidate models.

        self.distribution = dynamicTypeDistribution_VGDL1()

        ## 15 steps of observation before playing. Number is arbitrary; a lower number just leads to more frequent early re-planning --> more compute, but doesn't change sample efficiency.
        self.observe(self.rle,  self.memory, 4, self.bestSpriteTypeDict,  display=self.display_states, hypothesis=None)

        spriteTypeHypothesis, _, self.best_params = self.distribution.sampleFromDynamicTypeDistribution(self.rle._game, self.memory,
            allObjects, self.bestSpriteTypeDict)

        gameObject = Game(spriteInductionResult=spriteTypeHypothesis)
        initialTheory = gameObject.buildGenericTheory(spriteTypeHypothesis)

        avatar = [o for o in initialTheory.spriteSet if o.vgdlType in AvatarTypes][0]
        
        self.hypotheses = [initialTheory]
        self.symbolDict = generateSymbolDict(self.rle)

        return gameObject

    def completeHypotheses(self, allObjects, compactStates):
        previous_colors = [o['type']['color'] for o in self.previous_objects.values()]
        current_colors = [o['type']['color'] for o in allObjects.values()]
        if all([c in previous_colors for c in current_colors]):
            self.observe(self.rle,  self.memory, 0, self.bestSpriteTypeDict,  display=self.display_states, hypothesis=self.hypotheses[0]) ## if no new colors on screen, just set up likelihood updates
        else:
            self.observe(self.rle, self.memory, 5, self.bestSpriteTypeDict,  display=self.display_states, hypothesis=self.hypotheses[0]) ## if new objects, observe for a few steps so that you're not completely clueless about object movements in the new level, before you start planning.
            ## That is: VGDL description for Missiles specifies a particular orientation, but really the constraint is on horizontal/vertical movement. This decouples the way VGDL wants to take a description from what the actual claim is, and allows you to claim, e.g., that token 1 of some class is moving LEFT and token 2 of the same class is moving RIGHT at a given point in time.

        ## Make sure any objects that appeared while we were observing are reflected in allObjects
        for k,v in self.rle.getObjects().items():
            if k not in allObjects:
                allObjects[k] = v

        spriteTypeHypothesis, _, self.best_params= self.distribution.sampleFromDynamicTypeDistribution(self.rle._game, self.memory, allObjects, self.bestSpriteTypeDict, self.hypotheses[0].spriteSet)
        gameObject = Game(spriteInductionResult=spriteTypeHypothesis)
        newHypotheses = []
        try:
            for hypothesis in self.hypotheses:
                newHypotheses.append(gameObject.addNewObjectsToTheory(hypothesis, spriteTypeHypothesis))
        except:
            pass
            # print "failed in addNewObjectsToTheory"
            # embed()
        self.hypotheses = newHypotheses

    def playCurriculum(self, heatmap=False, level_game_pairs=None, make_movie=False, play_movie=False):
        """ Plays a game level until it wins, then moves to the next one until
        completion. """
        starttime = time.time()
        if not level_game_pairs:
            level_game_pairs = importlib.import_module(self.gameFilename).level_game_pairs
        episodes = []
        allEffectsEncountered = []

        self.make_movie = make_movie
        if self.make_movie:
            if 'images' in os.listdir('.') and 'tmp' in os.listdir('images') and self.gameFilename in os.listdir('images/tmp'):
                shutil.rmtree("images/tmp/"+self.gameFilename)
            os.makedirs("images/tmp/"+self.gameFilename)


        loaded_n_level=0
        curriculumSaveFile = 'curriculum_'+self.gameFilename+'_'+self.param_ID+'_'+self.task_ID
        loadedState = self.bookkeeping.loadCurriculumState(curriculumSaveFile)
        if loadedState is not None:
            self = loadedState['agent']
            loaded_n_level, within_level_iteration = loadedState['agent'].n_level, loadedState['agent'].within_level_iteration

        j=0
        fullStateEpisodes, episodeCompactStates = {}, {}
        for n_level, level_game in enumerate(level_game_pairs):

            if n_level < loaded_n_level: ## if we have a saved state that corresponds to us having played this level, skip it.
                continue

            (self.gameString, self.levelString) = level_game
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

            quit_level = False
            while not win and not quit_level:# and i<15:
                self.n_level = n_level
                self.within_level_iteration = i
                gameObject, win, score, steps, quit_level = self.playEpisode(gameObject, win)
                
                ## TODO: clean up below stuff, too.
                statesEncountered = self.bookkeeping.statesEncountered
                compactStates = self.bookkeeping.compactStates
                effectsEncountered = self.bookkeeping.effectsEncountered

                self.memory.totalGameSteps += steps
                allCompactStates.append(compactStates)
                episode_results = (n_level, steps, win, score, self.total_planner_steps)
                episodes.append(episode_results)

                if self.make_movie:
                    # self.statesEncountered = statesEncountered
                    self.makeImages()
                
                if self.record_video_info:
                    allStatesEncountered.extend(statesEncountered)

                i += 1

                episodeCompactStates[n_level] = allCompactStates
                fullStateEpisodes[n_level] = allStatesEncountered

                self.bookkeeping.saveCurriculumState(self, episodeCompactStates)

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
                    videofilename = "{}{}_{}".format(self.dirname_for_video, self.gameFilename, self.timestamp)
                    gameInfo = {'gameString':self.gameString, 'levelString':self.levelString, 'gameName':self.gameFilename}
                    with open(videofilename, 'wb') as f:
                        cPickle.dump({'gameInfo':gameInfo,'modelParams':self.param_ID, 'episodes':fullStateList, 'time_elapsed':time.time()-starttime}, f)
                if self.memory.totalGameSteps > MAX_STEPS:
                    if self.produce_printout:
                        print "reached max number of steps ({}>{}) in playCurriculum. Stopping experiment".format(self.memory.totalGameSteps, MAX_STEPS)

                self.bookkeeping.deleteEpisodeFile()

            if heatmap:
                self.makeHeatmap(allStatesEncountered, 'heatmap_{}_{}_level{}.pdf'.format(self.gameFilename, n_level, self.param_ID))

        if make_movie:
            self.makeMovie(play_movie=play_movie)

        endtime = time.time()

    def compactify(self, rle, planner_nodes=0):
        ## Used for saving minimal state
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
                 'objects': [(colorDict[str(s.color)], (s.rect.left/gameObject.block_size, s.rect.top/gameObject.block_size), s.resources if s.name=='avatar' else {}) for s in rle.getAliveSprites()],
                 'events': list(rle.getEffectListByClass())
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
        width, height = self.rle.width, self.rle.height
        correction_factor = self.rle.screensize[0]/width
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


    def makeImages(self):
        ## Used for making videos. First we save all states from all episodes as images, then we stitch together into a video.
        # params_to_print_to_video = self.param_ID
        params_to_print_to_video = ''
        game_name_to_print_to_video = self.gameFilename
        VGDLParser.playGame(self.gameString, self.levelString, self.bookkeeping.statesEncountered, \
            persist_movie=True, make_images=True, make_movie=False, movie_dir="videos/"+self.gameFilename, gameName = game_name_to_print_to_video, parameter_string=params_to_print_to_video, padding=10)

    def makeMovie(self, play_movie=False):

        VGDLParser.playGame(self.gameString, self.levelString, self.bookkeeping.statesEncountered, \
            persist_movie=True, make_images=True, make_movie=True, movie_dir="videos/"+self.gameFilename, padding=10)

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
        print "images/tmp contents:", os.getcwd()
        print "in main agent:", command
        subprocess.call(command, shell=True)
        # empty image directory
        shutil.rmtree("images/tmp/"+self.gameFilename)
        os.makedirs("images/tmp/"+self.gameFilename)

        if play_movie:
            command = ('open', '-a', 'Quicktime Player', video_dirname)
            subprocess.Popen(command)

        return


    def playEpisode(self, gameObject, win=False):

        ### ENVIRONMENT ###
        ## Initialize external environment
        self.initializeEnvironment()
        print "Playing level {}".format(self.n_level + 1)

        if self.produce_printout:
            print ""
            print self.rle.show(color='blue')


        ### AGENT EPISODE INIT STUFF ###
        quit_level = False

        self.longHorizonObservations = 0
        self.previous_objects = self.all_objects if self.all_objects else {}
        self.all_objects= self.rle.getObjects()
        self.annealing = 1

        ## Reset these for each episode. Used for data analysis
        self.bookkeeping.effectsEncountered = []
        self.bookkeeping.statesEncountered = []
        self.bookkeeping.compactStates = []

        if self.make_movie or self.record_video_info:
            self.bookkeeping.statesEncountered.append(self.rle.getFullState())
        
        self.last_recorded_time = time.time()
        if self.record_states:
            self.bookkeeping.compactStates.append(self.compactify(self.rle))
        
        ## Initialize memory of object positions
        self.memory.objectMemoryDict, self.memory.previousPositions = {}, {}
        for k, v in self.rle._game.all_objects.iteritems():
            self.memory.objectMemoryDict[k] = (int(self.rle._game.all_objects[k]['sprite'].rect.x), int(self.rle._game.all_objects[k]['sprite'].rect.y))
            self.memory.previousPositions[k] = (int(self.rle._game.all_objects[k]['sprite'].rect.x), int(self.rle._game.all_objects[k]['sprite'].rect.y))

        ## initialize theory if necessary.
        if len(self.hypotheses) == 0:
            gameObject = self.initializeHypotheses(self.all_objects, self.bookkeeping.statesEncountered, self.bookkeeping.compactStates)
            if self.display_text:
                print "initializing hypotheses"
        else:
            gameObject = self.completeHypotheses(self.all_objects, self.bookkeeping.compactStates)
            if self.display_text:
                print "had hypotheses -- completing them."
            # If theory is being carried over, falsify termination hypotheses
            # given new level state.
            [t.updateTerminations(rle=self.rle) for t in self.hypotheses]

        self.bookkeeping.episodeSaveFile = 'episode_'+self.gameFilename+'_'+self.task_ID
        loadedState = self.bookkeeping.loadCurriculumState(self.bookkeeping.episodeSaveFile)
        if loadedState is not None:
            self, self.bookkeeping.effectsEncountered, self.bookkeeping.statesEncountered, self.bookkeeping.compactStates, self.annealing = loadedState['agent'], loadedState['effectsEncountered'], loadedState['statesEncountered'], loadedState['compactStates'], loadedState['annealing']

        ## Do beginning-of-episode Avatar resource-management.
        resources = self.rle.getAvatars()[0].resources
        for resource, val in resources.items():
            if resource not in self.seen_resources and val>0:
                self.seen_resources.append(resource)
                self.hypotheses[0].resource_limits[resource] = self.rle.getResourceLimits()[resource]
            if resource not in self.seen_limits and val==self.rle.etResourceLimits()[resource]:
                self.seen_limits.append(resource)


        ended, win = self.rle._isDone()
        self.memory.episodeSteps = self.rle.getTime()
        
        ## Main episode loop
        while not ended:

            self.bookkeeping.saveEpisodeState(self, self.annealing)

            if self.memory.totalGameSteps+self.memory.episodeSteps > MAX_STEPS:
                score = self.rle.getScore()
                quit_level = False

                self.bookkeeping.saveEpisodeState(self, self.annealing)

                return gameObject, win, score, self.memory.episodeSteps, quit_level


            ## initialize one or many VRLEs (simulators) according to hypothesis-selection method
            self.theoryRLEs = self.VrleInitPhase()

            quitting = False

            self.metacontroller.setMaxNodes()

            ## short_horizon and first_order_horizon are managed separately, so we don't pass these in their standard form to the planner.
            planner_hyperparameters = dict((k, self.hyperparameters[k]) for k in self.hyperparameters.keys() if k not in ['short_horizon', 'first_order_horizon'])

            ## Initialize planner
            p = WBP.WBP(self.theoryRLEs[0], self.gameFilename, theory=self.hypotheses[0], fakeInteractionRules = self.fakeInteractionRules,seen_limits = self.seen_limits, annealing=self.annealing, max_nodes=self.max_nodes, shortHorizon=self.shortHorizon,
                firstOrderHorizon=self.firstOrderHorizon, conservative=self.conservative, hyperparameters=planner_hyperparameters, 
                extra_atom=self.extra_atom, IW_k=self.IW_k, objectNumberTrackingLimit=self.objectNumberTrackingLimit,
                objectLocationTrackingLimit=self.objectLocationTrackingLimit, lesion=self.planner_lesion)
            planner_recommended_quitting = p.quitting

            bestNode, gameStringArray, objectPositionsArray = p.BFS()
            
            self.total_planner_steps += p.total_nodes_opened
            self.planner_nodes_opened_on_most_recent_step = p.total_nodes_opened

            if bestNode is not None:
                solution = p.solution
                gameString_array = p.gameString_array
                self.objectPositionsArray = objectPositionsArray[::-1]
                if solution and self.display_text:
                    print "got solution"
            else:
                solution = []

            solution = self.metacontroller.determinePlanningModeAndReplanIfNecessary(solution, self.rle, planner_recommended_quitting)

            if self.metacontroller.quitting:
                self.metacontroller.quitting = False
                ## TODO: remove. agent should not be taking steps here.
                ## Figure out why you had to do it and remove it.
                quitting = True
                action = 0
                hypotheses, theory_change_flag, effects = self.executeStep(0, self.hypotheses, run_induction = True)

            ## Most common scenario: planner worked. Show projected plan and states, then act.
            if solution and not self.takingRandomSteps and self.display_states and self.produce_printout:

                print "found plan of length {}. Intended actions and predicted states:".format(len(solution))
                for i,g in enumerate(p.gameString_array[1:]):
                    print actionDict[solution[i]]
                    print colored(g, 'green')
                print "==============================================================="

            ## Acting/learning/monitoring the need to re-plan
            if not quitting:
                for i, action in enumerate(solution):
                    self.hypotheses[0].dryingPaint = set()

                    if self.display_text:
                        t1 = time.time()

                    effects = []

                    ## Storing info on search budget
                    plannerNodes = p.total_nodes_opened if i==0 else 0
                    hypotheses, theory_change_flag, effects = self.executeStep(action, self.hypotheses,
                        run_induction = True)
                    
                    ## For an incomplete ablation
                    if self.memory.totalGameSteps+self.memory.episodeSteps > MAX_STEPS:
                        score = self.rle.getScore()
                        quit_level = False

                        self.bookkeeping.saveEpisodeState(self, self.annealing)

                        return gameObject, win, score, self.memory.episodeSteps, quit_level

                    if self.display_text:
                        print "executeStep took {} seconds".format(time.time()-t1)
                    sys.stdout.flush()
                    
                    self.memory.nextPositions = {}
                    for k, v in self.rle._game.all_objects.iteritems():
                        self.memory.nextPositions[k] = (int(self.rle._game.all_objects[k]['sprite'].rect.x), int(self.rle._game.all_objects[k]['sprite'].rect.y))
                        try:
                            if self.memory.previousPositions[k] != self.memory.nextPositions[k]:
                                self.memory.objectMemoryDict[k] = copy.deepcopy(self.memory.previousPositions[k])
                        except KeyError:
                            pass
                    self.memory.previousPositions = copy.deepcopy(self.memory.nextPositions)

                    self.bookkeeping.effectsEncountered.extend(effects)
                    self.memory.episodeSteps +=1
                    if theory_change_flag:
                        self.hypotheses = hypotheses
                        break
                    ended, win = self.rle._isDone()

                    self.max_game_time_observed = max(self.max_game_time_observed, self.rle.getTime())
                    if ended:
                        break

                    ## Make sure agent is far enough from unpredictable dangerous objects.
                    # Check for disparities between plan and reality
                    # (e.g. stochastic effects)
                    if (i+1)%self.regrounding==0:

                        if (not self.takingRandomSteps) and self.checkForDangerOrAvatarMisLocation(self.rle, hypotheses[0], self.objectPositionsArray, i):
                            break

            else:
                quit_level = self.metacontroller.annealUp()

                win, effects = False, []
                self.episodeRecord.insert(0, (win, effects))

                self.bookkeeping.saveEpisodeState(self, self.annealing)

                display('Quitting')

                return gameObject, False, self.rle.getScore(), self.memory.episodeSteps, quit_level

            self.annealing *= self.annealingFactor
            ended, win = self.rle._isDone()
            
            if ended:
                self.episodeRecord.insert(0, (win, effects))
            
            if ended and not win and self.rle.getTime()==2000:
                if self.produce_printout:
                    print "lost on timeout. switching hyperparameters"
                self.hyperparameterSwitch(new_index=1)


        score = self.rle.getScore()
            
        if win:
            display('win')
        else:
            display('loss')

        return gameObject, win, score, self.memory.episodeSteps, quit_level

    def checkForRepeatedDeaths(self, episodeRecord, cutoff):
        ## Has agent died the same way (i.e., killed by the same object) multiple times? (Used for metacontroller policy)
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
        
        min_age = min([sprite.lastmove for sprite in rle.getAliveSprites() if sprite.name not in [thingWeShoot, 'avatar']])

        try:
            time_since_last_kill = rle.getTime() - max([item.deathage for item in rle.getDeadSprites() if item.name!=thingWeShoot])
        except:
            time_since_last_kill = rle.getTime()

        if (min_age > age_cutoff) and (time_since_last_kill > age_cutoff):
            return True
        else:
            return False

    def checkForMovingTypes(self, rle, hypothesis):
        ## Another check for whether agent is in slow-moving games (where it's the only entity that generates motion)
        if self.hypotheses[0].classes['avatar'][0].args and 'stype' in self.hypotheses[0].classes['avatar'][0].args:
            thingWeShoot = self.hypotheses[0].classes['avatar'][0].args['stype']
        else:
            thingWeShoot = None    
        moving_types = [k for k in hypothesis.classes.keys() if k!=thingWeShoot and any([t in str(hypothesis.classes[k][0].vgdlType) for t in ['Missile', 'Random', 'Chaser']])]
        moving_colors = [hypothesis.classes[k][0].color for k in moving_types]
        movingTypes = False
        if moving_colors:
            for s in rle.getAliveSprites():
                if s.colorName in moving_colors:
                    movingTypes = True
                    break
        return movingTypes

    def checkForDangerOrAvatarMisLocation(self, rle, hypothesis, objectPositionsArray, i):
        
        ## For metacontroller to decide whether there's danger worth worrying about (like if something dangerous isn't where the agent predicted it would be), or if Avatar ended up in a surprising location.

        regroundingFlag = False
        rleDict, hypDict = {}, {}

        for s in objectPositionsArray[i+1].getAliveSprites():
            hypDict[s.ID2] = s

        killer_types = [inter.slot2 for inter in hypothesis.interactionSet if inter.slot1=='avatar' and inter.interaction in ['killSprite']]
        killer_colors = [hypothesis.classes[k][0].color for k in killer_types]

        for s in rle.getAliveSprites():
            ## If the object isn't in our predicted environment or the positions vary
            if s.name=='avatar' or s.colorName in killer_colors:
                if s.ID not in hypDict and manhattan_distance(s.rect, rle.getAvatars()[0].rect) < self.safeDistance*s.rect.width:

                    regroundingFlag=True
                    if self.agent.produce_printout:
                        print colored("Regrounding because we didn't predict the appearance of {} and it's too close for comfort".format(s), 'white', 'on_yellow')
                    break
                if s.ID in hypDict and s.rect!=hypDict[s.ID].rect and manhattan_distance(s.rect, rle.getAvatars()[0].rect) < self.safeDistance*s.rect.width:
                    if self.agent.produce_printout:
                        print colored("Regrounding because distance between {} and {} is {}, which is less than the safe distance of {}. We thought it would be at {}".format(
                            s, rle.getAvatars()[0], manhattan_distance(s.rect, rle.getAvatars()[0].rect), self.safeDistance*s.rect.width, hypDict[s.ID]),
                            'white', 'on_yellow')
                    regroundingFlag=True
                    break
                rleDict[s.ID] = s
        return regroundingFlag

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
        ## Add newly-seen objects to object-type distribution
        current_objects = self.rle.getObjects()
        for k in current_objects.keys():
            spriteName = current_objects[k]['sprite'].name
            if spriteName not in [self.all_objects[key]['sprite'].name for key in self.all_objects.keys()]:
                if self.display_text:
                    print "new object", spriteName
                self.all_objects[k] = current_objects[k]
                self.distribution.distributionInitSetup(self.rle._game, k)
                ## prevent spriteInduction from trying to infer anything about newly-appeared sprites in this timestep, as likelihood function hasn't been seeded for these objects.
                self.memory.ignoreList.append(k)
                self.new_objects[spriteName] = 0

        return hypotheses

    def observe(self, rle, memory, obsSteps, bestSpriteTypeDict, display=False, hypothesis=None):
        ## Agent just observes the state for 'obsSteps' steps and updates object-type distribution.
        ## if called with obsSteps==0, it'll just initialize the object-type distribution
        if display and self.produce_printout:
            print "observing for {} steps".format(obsSteps)
        if obsSteps>0:
            for i in range(obsSteps):
                self.distribution.spriteInduction(rle._game, self.memory, step=1, bestSpriteTypeDict=bestSpriteTypeDict, dynamic_type_lesion=self.dynamic_type_lesion)
                self.distribution.spriteInduction(rle._game, self.memory, step=2, bestSpriteTypeDict=bestSpriteTypeDict, dynamic_type_lesion=self.dynamic_type_lesion)
                rle.step((0,0))
                if self.make_movie or self.record_video_info:
                    self.bookkeeping.statesEncountered.append(self.rle.getFullState(observe_state=True))
                if self.record_states:
                    self.bookkeeping.compactStates.append(self.compactify(self.rle))
                if self.produce_printout:
                    print "score: {}, timestep: {}".format(rle.getScore(), rle.getTime())
                    print rle.show(color='blue')
                print "action", self.memory.totalGameSteps+rle.getTime()
                self.memory.nextPositions = {}
                for k, v in rle._game.all_objects.iteritems():
                    self.memory.nextPositions[k] = (int(rle._game.all_objects[k]['sprite'].rect.x), int(rle._game.all_objects[k]['sprite'].rect.y))
                    try:
                        if self.memory.previousPositions[k] != self.memory.nextPositions[k]:
                            self.memory.objectMemoryDict[k] = copy.deepcopy(self.memory.previousPositions[k])
                    except KeyError:
                        pass
                self.memory.previousPositions = copy.deepcopy(self.memory.nextPositions)
                self.distribution.spriteInduction(rle._game, self.memory, step=3,  bestSpriteTypeDict=bestSpriteTypeDict)
        else:
            self.distribution.spriteInduction(rle._game, self.memory, step=1,  bestSpriteTypeDict=bestSpriteTypeDict, dynamic_type_lesion=self.dynamic_type_lesion)
            self.distribution.spriteInduction(rle._game, self.memory, step=2, bestSpriteTypeDict=bestSpriteTypeDict, dynamic_type_lesion=self.dynamic_type_lesion)
        return

    def executeStep(self, action, hypotheses, run_induction=True):

        ## Takes the specified action and does bookkeeping

        theory_change_flag = False

        self.distribution.spriteInduction(self.rle._game, self.memory, step=1, bestSpriteTypeDict=self.bestSpriteTypeDict, oldSpriteSet=hypotheses[0].spriteSet, dynamic_type_lesion=self.dynamic_type_lesion)
        # print "induction step 1 took {} seconds.".format(time.time()-t1)
        t1 = time.time()
        self.distribution.spriteInduction(self.rle._game, self.memory, step=2, bestSpriteTypeDict=self.bestSpriteTypeDict, oldSpriteSet=hypotheses[0].spriteSet, dynamic_type_lesion=self.dynamic_type_lesion)
        # print "induction step 2 took {} seconds".format(time.time()-t1)
        try:
            agentState = copy.deepcopy(self.rle.getAvatars()[0].resources)
        except IndexError:
            agentState = defaultdict(lambda: 0)

        lastScore = self.rle.getScore()
        res = self.rle.step(action)

        try:
            agentState = copy.deepcopy(self.rle.getAvatars()[0].resources)

            for e in res['effectList']:
                if 'changeResource' in e:
                    changes = e[3]
                    if changes['value'] < 0:
                        # undo one negative change to account for eventhandler ordering
                        agentState[changes['resource']] -= changes['value']
                        break

            self.rle.agentStatePrev = agentState

        ## If agent is killed before we grab its agentState,
        ## use what's printed in the effect label to get it. 
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
            self.bookkeeping.statesEncountered.append(self.rle.getFullState())
        if self.record_states:
            self.bookkeeping.compactStates.append(self.compactify(self.rle, self.planner_nodes_opened_on_most_recent_step))
        self.planner_nodes_opened_on_most_recent_step = 0
        t1 = time.time()

        distributionsHaveChanged = self.distribution.spriteInduction(self.rle._game, self.memory, step=3, bestSpriteTypeDict=self.bestSpriteTypeDict, oldSpriteSet=hypotheses[0].spriteSet)
 
        ## First interaction-rule ablation (not used)
        effects = self.rle.getEffectListByColor()
        if self.interaction_lesion_replacement == 'nothing':
            for i,e in enumerate(effects):
                if e[0] in self.disallowed_events:
                    print "replacing", e
                    effects[i] = ('nothing', e[1], e[2])
                    print "with", effects[i]
                    print ""

        if self.display_states:
            print "score: {}, game step: {}".format(self.rle.getScore(), self.rle.getTime())

        # t1 = time.time()
        print "action", self.memory.totalGameSteps+self.rle.getTime()
        if self.produce_printout:
            print ""
            print keyPresses[action]
            print self.rle.show(color='blue')

        event = {'agentState': agentState, 'agentAction': action, 'effectList': effects, \
            'gameState': None, 'rle': self.rle}

        newEffects = False

        ## If any collisions occurred
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

        ## Ideally you'd update the model at every step, but it takes a lot of time
        ## so: Update when a new event happens (in which case you definitely need to update it), or when your MAP object-type hypothesis has changed for some class (in which case you definitely need to update it), or if we don't have a super-large number of time-steps in our history, do it sometimes (with probability .2)
        if ((newEffects or (random.random()<.2 and len(self.finalTimeStepList)<300)) and run_induction) or distributionsHaveChanged:
            # print "event", (not all([e in all_effects for e in effects])), "distributions changed", distributionsHaveChanged
            if self.display_text:
                print "new event", newEffects, "distributions changed", distributionsHaveChanged

            if newEffects or distributionsHaveChanged:
                theory_change_flag = True

            t1 = time.time()
            sample, _, self.best_params= self.distribution.sampleFromDynamicTypeDistribution(self.rle._game, self.memory, self.all_objects, self.bestSpriteTypeDict, self.hypotheses[0].spriteSet, display=self.display_text)

            game_object = Game(spriteInductionResult=sample)
            
            terminationCondition = {'ended': False, 'win':False, 'time':self.rle.getTime()}
            trace = (self.finalTimeStepList, terminationCondition)

            t1 = time.time()
            hypotheses = list(game_object.runInduction(game_object.spriteInductionResult, trace, 20, \
            verbose=False, existingTheories=hypotheses))

            if hypotheses[0].__dict__ != self.hypotheses[0].__dict__:
                theory_change_flag = True

        ## We also need to update termination conditions even when we haven't seen a new event,
        ## because the state is informative about termination conditions.
        oldTerminationSet = set(hypotheses[0].terminationSet)
        if event['effectList'] and run_induction:
            [t.updateTerminations(event=event) for t in hypotheses]

        if set(hypotheses[0].terminationSet) != oldTerminationSet:
            if self.display_text:
                print "terminationSet Change"
            theory_change_flag = True

        if theory_change_flag and not distributionsHaveChanged and self.display_text:
            print "changed theory:"
            hypotheses[0].display()

        return hypotheses, theory_change_flag, effects

def display(message):
    if message=='Quitting':
        output =          "Quitting.                                                       "
        print colored('________________________________________________________________', 'white', 'on_red')
        print colored(output, 'white', 'on_red')
        print colored('________________________________________________________________', 'white', 'on_red')
    if message=='win':
        output =          "ended episode. Win=True                                         "
        print colored('________________________________________________________________', 'white', 'on_green')

        print colored(output, 'white', 'on_green')
        print colored('________________________________________________________________', 'white', 'on_green')

    if message=='loss':
        output =          "ended episode. Win=False                                        "
        print colored('________________________________________________________________', 'white', 'on_red')
        print colored(output, 'white', 'on_red')
        print colored('________________________________________________________________', 'white', 'on_red')


## For local usage/testing/debugging. Not used.
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

