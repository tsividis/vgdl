import os
import subprocess
import shutil
import numpy as np
import random
import time
import copy
from collections import defaultdict
from core import colorDict, VGDLParser, sys
from datetime import datetime
from math import log
from pygame import K_LEFT, K_UP, K_RIGHT, K_DOWN, K_SPACE
from termcolor import colored
from util import *
from ontology import *
from hyperparameters import hyperparameter_sets, metacontroller_sets
from agent_utils import translate_events, findNearestSprite, getSpritesByColor
from theory_template import TimeStep, Theory, Game, writeTheoryToTxt, generateSymbolDict
from metacontroller import Metacontroller
from dynamic_type_inference import dynamicTypeDistribution_VGDL1
import WBP
from rlenvironmentnonstatic import createRLInputGame, createRLInputGameFromStrings, defInputGame, createMindEnv
from bookkeeping import Bookkeeping

actionDict = {K_SPACE: 'space', K_UP: 'up', K_DOWN: 'down', K_LEFT: 'left', K_RIGHT: 'right', 0:'none', None: 'none'}

AvatarTypes = [MovingAvatar, HorizontalAvatar, VerticalAvatar, FlakAvatar, AimedFlakAvatar, OrientedAvatar,RotatingAvatar, RotatingFlippingAvatar, NoisyRotatingFlippingAvatar, ShootAvatar, AimedAvatar,AimedFlakAvatar, InertialAvatar, MarioAvatar]

class Agent:
    def __init__(self, modelType, gameFilename, hyperparameter_sets, hyperparameter_index='short-term', metacontroller_index=0, IW_k=1, extra_atom_allowed=True, task_ID=0, produce_printout=False, movieName=None):
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
        self.hyperparameter_index = hyperparameter_index
        self.hyperparameters = hyperparameter_sets[self.hyperparameter_index]
        self.shortHorizon = self.hyperparameters['short_horizon'] # Params used in short-horizon planning
        self.return_subgoal_plans = self.hyperparameters['return_subgoal_plans'] # Makes agent commit to a plan once first-order distances change (e.g., spritecounter values)
        self.IW_k = IW_k # Only using IW 1
        self.extra_atom_allowed = extra_atom_allowed # Adding optional extra atom to IW
        self.epsilon_greedy = False # Ablation
        self.absolute_max_nodes = 32000 #To save on compute, don't deal with games that require more than this
        self.shortHorizonNodes = 500 ## This isn't used, but code needs further cleanup to actually delete it.
        self.shortHorizonAnnealing = 1.05 ##  This isn't used, but code needs further cleanup to actually delete it.
        self.forfeit_level = False
        self.agentState = defaultdict(lambda: 0)

        self.metacontroller_params = metacontroller_sets[metacontroller_index]
        self.random_steps_on_plan_failure = self.metacontroller_params['random_steps_on_plan_failure']
        self.longHorizonNodes = self.metacontroller_params['longHorizonNodes']
        self.longhorizonAnnealing = self.metacontroller_params['longhorizonAnnealing']
        self.shortHorizonRandomChoice = self.metacontroller_params['shortHorizonRandomChoice']
        self.stall_mode_max_nodes = self.metacontroller_params['stall_mode_max_nodes']
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
    
    
        self.stall_mode = False
        self.regrounding = 1
        self.takingRandomSteps = False

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

        self.solution = []
        self.steps_in_solution = 0
        self.action = None
        self.quitting = False
        self.re_plan = False
        self.predicted_states = [] ##TODO: Pass to memory
        self.printable_predicted_states = []
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
            print "current working dir", os.getcwd()
            if 'pedro' in os.getcwd():
                print "pedro in os.getcwd(); using long dirname"
                dirname_for_results = "../data/demo_data_files/EMPA/local/results/{}/{}/".format(self.param_ID, self.gameFilename)
            else:
                print "pedro NOT in os.getcwd(); using short dirname"
                print "param_ID, gamefilename", self.param_ID, self.gameFilename
                dirname_for_results = "results/{}/{}/".format(self.param_ID, self.gameFilename)
            print "chose dirname:", dirname_for_results
            filename = "{}{}_{}".format(dirname_for_results, self.gameFilename, self.timestamp)
            self.filename = filename
            print "chose filename", self.filename
            if not os.path.exists(dirname_for_results):
                print "dirname_for_results {} didn't exist".format(dirname_for_results)
                try:
                    # print "path didn't exist; making", dirname
                    os.makedirs(dirname_for_results)
                except:
                    print "failed to make dir {} in main_agent.py".format(dirname_for_results)
        if self.write_video_info:
            self.dirname_for_video = "raw_video_info/{}/{}/".format(self.param_ID, self.gameFilename)
            if not os.path.exists(self.dirname_for_video):
                os.makedirs(self.dirname_for_video)

    def hyperparameterSwitch(self, new_index):
        if new_index!=self.hyperparameter_index:
            self.hyperparameter_index = new_index
            self.hyperparameters = self.hyperparameter_sets[new_index]
            self.shortHorizon = self.hyperparameters['short_horizon']
            self.return_subgoal_plans = self.hyperparameters['return_subgoal_plans']
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
        planner_hyperparameters = dict((k, self.hyperparameters[k]) for k in self.hyperparameters.keys() if k not in ['short_horizon', 'return_subgoal_plans'])
        return planner_hyperparameters


    def setSpritePositions(self, environment, Vrle, hypothesis):
        ## Sets positions of objects in Vrle to what they were in the environment. E.g., if we want to start a simulation according to the model specified by 'hypothesis' at the state contained in 'rle', this will return Vrle: a playable game whose rules run according to the model.

        old_sprite_groups = Vrle.getSpriteGroups()
        for k in old_sprite_groups.keys():
            if old_sprite_groups[k]:
                color = Vrle.getSpriteGroups()[k][0].colorName
                matchingSpritesInRLE = getSpritesByColor(environment, color)
                for sprite in old_sprite_groups[k]:
                    matchingSprite = findNearestSprite(sprite, matchingSpritesInRLE)
                    sprite.rect = matchingSprite.rect
                    sprite.lastmove = matchingSprite.lastmove
                    sprite.ID2 = matchingSprite.ID
                    if sprite.name in hypothesis.classes and 'Missile' in str(hypothesis.classes[sprite.name][0].vgdlType) and self.best_params!=None:
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
        # t1 = time.time()
        gameString, levelString, symbolDict = writeTheoryToTxt(self.environment, hypothesis, self.symbolDict,\
                 "./theory_files/{}.py".format(self.gameFilename))
        # print "writeTheory: {}".format(time.time()-t1)
        # t1 = time.time()
        Vrle = createMindEnv(gameString, levelString, output=False)

        self.setSpritePositions(self.environment, Vrle, hypothesis)
        # print "createMindEnv and setSpritePositions: {}".format(time.time()-t1)
        # t1 = time.time()
        try:
            Vrle.getAvatars()[0].resources = copy.deepcopy(self.environment.getAvatars()[0].resources)
            Vrle.getAvatars()[0].orientation = copy.deepcopy(self.environment.getAvatars()[0].orientation)
        except (IndexError, AttributeError) as e:
            pass
        # print "Avatar resource stuff: {}".format(time.time()-t1)

        return Vrle

    def VrleInitPhase(self):
        ## Initialize multiple VRLEs, each corresponding to one hypothesis in self.hypotheses. In practice we only use one.
        VRLEs = []

        for hypothesis in self.hypotheses[0:1]:
            # t1 = time.time()
            tempHypothesis = copy.deepcopy(hypothesis)
            # print "vrleInitPhase1: {}".format(time.time()-t1)
            # t1 = time.time()

            tmpFakeInteractionRules = copy.deepcopy(self.fakeInteractionRules)
            # print "vrleInitPhase 2: {}".format(time.time()-t1)
            # t1 = time.time()

            tempHypothesis.interactionSet.extend(tmpFakeInteractionRules)
            # print "vrleInitPhase3: {}".format(time.time()-t1)
            # t1 = time.time()

            tempHypothesis.updateTerminations()
            # print "vrleInitPhase4: {}".format(time.time()-t1)
            # t1 = time.time()

            VRLEs.append(self.initializeVrle(tempHypothesis))
            # print "vrleInitPhase5: {}".format(time.time()-t1)


        return VRLEs

    def initializeHypotheses(self, allObjects, statesEncountered, compactStates):
        ## Creates initial hypothesis objects by observing the game,
        ## doing initial inference over sprite types, and returning partial
        ## candidate models.

        ## Initialize dynamic-type distribution
        self.distribution = dynamicTypeDistribution_VGDL1()

        ## Set up hypothetical locations for the next timestep
        self.distribution.spriteInduction(self.environment._game, self.memory, step=1, bestSpriteTypeDict=self.bestSpriteTypeDict, dynamic_type_lesion=self.dynamic_type_lesion)

        ## Sample dynamic types
        spriteTypeHypothesis, _, self.best_params = self.distribution.sampleFromDynamicTypeDistribution(self.environment._game, self.memory,
            allObjects, self.bestSpriteTypeDict)

        gameObject = Game(spriteInductionResult=spriteTypeHypothesis)
        initialTheory = gameObject.buildGenericTheory(spriteTypeHypothesis)

        avatar = [o for o in initialTheory.spriteSet if o.vgdlType in AvatarTypes][0]
        
        self.hypotheses = [initialTheory]
        self.symbolDict = generateSymbolDict(self.environment)

        return gameObject

    def completeHypotheses(self, allObjects, compactStates):
        self.distribution.spriteInduction(self.environment._game, self.memory, step=1, bestSpriteTypeDict=self.bestSpriteTypeDict, dynamic_type_lesion=self.dynamic_type_lesion)

        spriteTypeHypothesis, _, self.best_params= self.distribution.sampleFromDynamicTypeDistribution(self.environment._game, self.memory, allObjects, self.bestSpriteTypeDict, self.hypotheses[0].spriteSet)
        gameObject = Game(spriteInductionResult=spriteTypeHypothesis)
        
        ## TODO: Look into this loop. Is it needed?
        newHypotheses = []
        try:
            for hypothesis in self.hypotheses:
                newHypotheses.append(gameObject.addNewObjectsToTheory(hypothesis, spriteTypeHypothesis))
        except:
            pass
        self.hypotheses = newHypotheses


    def compactify(self, environment, planner_nodes=0):
        ## Used for saving minimal state
        current_time = time.time()
        gameObject = environment._game
        ended, win = environment._isDone()
        state = {'timestep': gameObject.time,
                 'time_elapsed': current_time - self.last_recorded_time,
                 'score': gameObject.score,
                 'planner_settings': self.hyperparameter_index,
                 'planner_nodes': planner_nodes, ## how many nodes were searched to determine this particular action? 0 if this is resulting from a cached plan.
                 'ended': ended,
                 'win': win,
                 'objects': [(colorDict[str(s.color)], (s.rect.left/gameObject.block_size, s.rect.top/gameObject.block_size), s.resources if s.name=='avatar' else {}) for s in environment.getAliveSprites()],
                 'events': list(environment.getEffectListByClass())
                 }
        self.last_recorded_time = current_time
        return state

    def beginningOfEpisodeManagement(self):
        ### AGENT EPISODE INIT STUFF ###
        self.forfeit_level = False

        self.longHorizonObservations = 0
        self.previous_objects = self.all_objects if self.all_objects else {}
        self.all_objects= self.environment.getObjects()

        ## Reset these for each episode. Used for data analysis
        self.bookkeeping.effectsEncountered = []
        self.bookkeeping.statesEncountered = []
        self.bookkeeping.compactStates = []

        if self.make_movie or self.record_video_info:
            self.bookkeeping.statesEncountered.append(self.environment.getFullState())
        
        self.last_recorded_time = time.time()
        if self.record_states:
            self.bookkeeping.compactStates.append(self.compactify(self.environment))
        
        ## Initialize memory of object positions
        self.memory.objectMemoryDict, self.memory.previousPositions = {}, {}
        for k, v in self.environment._game.all_objects.iteritems():
            self.memory.objectMemoryDict[k] = (int(self.environment._game.all_objects[k]['sprite'].rect.x), int(self.environment._game.all_objects[k]['sprite'].rect.y))
            self.memory.previousPositions[k] = (int(self.environment._game.all_objects[k]['sprite'].rect.x), int(self.environment._game.all_objects[k]['sprite'].rect.y))

        ## initialize theory if necessary.
        if len(self.hypotheses) == 0:
            gameObject = self.initializeHypotheses(self.all_objects, self.bookkeeping.statesEncountered, self.bookkeeping.compactStates)
            if self.display_text:
                print "initializing hypotheses"
        else:
            gameObject = self.completeHypotheses(self.all_objects, self.bookkeeping.compactStates)
            if self.display_text:
                print "had hypotheses -- completing them."
            ## TODO: This belongs elsewhere
            # If theory is being carried over, falsify termination hypotheses
            # given new level state.
            [t.updateTerminations(rle=self.environment) for t in self.hypotheses]

        self.bookkeeping.episodeSaveFile = 'episode_'+self.gameFilename+'_'+self.task_ID
        loadedState = self.bookkeeping.loadCurriculumState(self.bookkeeping.episodeSaveFile)
        if loadedState is not None:
            self, self.bookkeeping.effectsEncountered, self.bookkeeping.statesEncountered, self.bookkeeping.compactStates, loadedState['effectsEncountered'], loadedState['statesEncountered'], loadedState['compactStates'], loadedState['annealing']

        ## Do beginning-of-episode Avatar resource-management.
        resources = self.environment.getAvatars()[0].resources
        for resource, val in resources.items():
            if resource not in self.seen_resources and val>0:
                self.seen_resources.append(resource)
                self.hypotheses[0].resource_limits[resource] = self.environment.getResourceLimits()[resource]
            if resource not in self.seen_limits and val==self.environment.etResourceLimits()[resource]:
                self.seen_limits.append(resource)

        try:
            self.agentState = copy.deepcopy(self.environment.getAvatars()[0].resources)
        except IndexError:
            self.agentState = defaultdict(lambda: 0)

        self.memory.episodeSteps = self.environment.getTime()

        self.solution = []
        self.steps_in_solution = 0

    def planAsNeeded(self):

        """ 
        Calls all planning-related functions:
        Uses an existing plan if it is still valid;
        otherwise determines the appropriate mode for re-planning,
        re-plans, and sets self.solution
        """

        # t1 = time.time()
        ## initialize one or many VRLEs (simulators) according to hypothesis-selection method
        ## Later -- consider not constantly reinitializing vrles
        self.quitting = False
        
        # print "plan phase 1: {}".format(time.time()-t1)
        # t1 = time.time()
        ended, win = self.environment._isDone()

        ## ended and not win and time==2000 means we lost on timeout
        ## pass this to proper inference.
        if ended and not win and self.environment.getTime()==2000:
            if self.produce_printout:
                print "lost on timeout. switching hyperparameters"
            self.hyperparameterSwitch(new_index='long-term')

        self.re_plan = self.metacontroller.isReplanningNecessary()

        # print "plan phase 2: {}".format(time.time()-t1)
        # t1 = time.time()

        if self.re_plan==True:
            self.theoryRLEs = self.VrleInitPhase()

            self.metacontroller.setMaxNodes()
            self.steps_in_solution = 0

            # print "plan phase 3: {}".format(time.time()-t1)
            # t1 = time.time()

            ## Initialize planner
            planner_hyperparameters = dict((k, self.hyperparameters[k]) for k in self.hyperparameters.keys() if k not in ['short_horizon', 'return_subgoal_plans'])  

            # t1 = time.time()
            p = WBP.WBP(self.theoryRLEs[0], self.gameFilename, theory=self.hypotheses[0], fakeInteractionRules = self.fakeInteractionRules,seen_limits = self.seen_limits, max_nodes=self.max_nodes,
                return_subgoal_plans=self.return_subgoal_plans, stall_mode=self.stall_mode, hyperparameters=planner_hyperparameters, 
                extra_atom=self.extra_atom, IW_k=self.IW_k, lesion=self.planner_lesion, boltz_hyps = self.boltz_hyps)
            # print "plan phase 4: {}".format(time.time()-t1)
            # t1 = time.time()

            # take epsilon greedy action
            if np.random.uniform() > self.epsilon:
                # best action
                best_action = True
            else:
                # boltzmann action
                best_action = False

            print('BEST ACTION: {}, EPSILON: {}'.format(best_action, self.epsilon)) 
            # import ipdb; ipdb.set_trace()
            self.root_node, self.till_bfs = p.plan(
                    self.till_bfs,
                    self.boltz_temp,
                    self.root_node,
                    best_action
            )
            
            # decay boltzmann temperature
            if best_action == False:
                self.boltz_temp -= (self.boltz_hyps['boltz_init']-self.boltz_hyps['boltz_min'])/self.boltz_hyps['boltz_exploit']
                self.boltz_temp = max(self.boltz_hyps['boltz_min'], self.boltz_temp)
            
            # decay epsilon
            self.epsilon -= (self.boltz_hyps['epsilon_init']-self.boltz_hyps['epsilon_min'])/self.boltz_hyps['epsilon_exploit']
            self.epsilon = max(self.boltz_hyps['epsilon_min'], self.epsilon)

            self.steps_so_far += 1
            # p.BFS()

            # print "plan phase 5: {}".format(time.time()-t1)
            # t1 = time.time()

            # if p.bestNode is not None:
            #     self.solution = p.solution
            #     self.predicted_states = p.predicted_states
            #     if self.solution and self.display_text:
            #         print "got solution"
            # else:self.total_planner_steps, self.value_array, self.reward_array, 50self.total_planner_steps, self.value_array, self.reward_array, 50
            #     self.solution = []

            self.solution = p.solution
            self.predicted_states = p.predicted_states
            self.printable_predicted_states = p.printable_predicted_states
            planner_recommended_quitting = p.quitting
            

            self.solution, self.predicted_states, self.printable_predicted_states = self.metacontroller.determinePlanningModeAndReplanIfNecessary(self.solution, self.environment, planner_recommended_quitting)
            # print "plan phase 6: {}".format(time.time()-t1)
            # t1 = time.time()

            ## Most common scenario: planner worked. Show projected plan and states, then act.
            if self.solution:
                print "found plan of length {}. Intended actions and predicted states:".format(len(self.solution))
                for i,g in enumerate(self.printable_predicted_states[1:]):
                    print(i)
                    print actionDict[self.solution[i]]
                    print colored(g, 'green')
                    # print colored(self.printable_predicted_states[i], 'green')
                # print "==============================================================="


            ### BOOKKEEPING ###
            self.planner_nodes_opened_on_most_recent_step = len(self.solution)

        if self.metacontroller.quitting:
            print "Metacontroller suggests quitting:", self.metacontroller.quitting
            self.metacontroller.quitting = False
            self.quitting = True
            action = 0

        if not ended:
            if not self.quitting:
                action = self.solution[self.steps_in_solution]
                # self.value_array.append(self.plan_value_array[self.steps_in_solution])
                # self.reward_array.append(self.plan_reward_array[self.steps_in_solution])
                self.steps_in_solution += 1
        else:
            action = 0
            self.quitting = True

        return action


    def step(self, action):

        t1 = time.time()

        if self.environment.getTime() == 0:
            self.beginningOfEpisodeManagement()

        # print "phase 1: {}".format(time.time()-t1)
        # t1 = time.time()


        self.bookkeeping.saveEpisodeState(self)

        hypotheses = self.hypotheses

        ended, win = self.environment._isDone()

        self.hypotheses[0].dryingPaint = set()

        theory_change_flag = False

        try:
            self.agentState = copy.deepcopy(self.environment.getAvatars()[0].resources)

            for e in self.environment._game.effectList:
                if 'changeResource' in e:
                    changes = e[3]
                    if changes['value'] < 0:
                        # undo one negative change to account for eventhandler ordering
                        self.agentState[changes['resource']] -= changes['value']
                        break

            self.environment.agentStatePrev = self.agentState

        ## If agent is killed before we grab its agentState,
        ## use what's printed in the effect label to get it. 
        except (IndexError, AttributeError) as e:
            ignored_negative_change = False
            for e in self.environment._game.effectList:
                if 'changeResource' in e:
                    changes = e[3]
                    if changes['value'] > 0 or ignored_negative_change:
                        self.agentState[changes['resource']] += changes['value']
                    else:
                        self.agentState[changes['resource']] += 0
                        ignored_negative_change = True
            self.environment.agentStatePrev = self.agentState
        
        for k,v in self.agentState.items():
            self.agentState[k] = max(0, v)

        # print "phase 2: {}".format(time.time()-t1)
        # t1 = time.time()

        hypotheses = self.manageNewObjects(hypotheses)

        if self.make_movie or self.record_video_info:
            self.bookkeeping.statesEncountered.append(self.environment.getFullState())
        if self.record_states:
            self.bookkeeping.compactStates.append(self.compactify(self.environment, self.planner_nodes_opened_on_most_recent_step))

        self.planner_nodes_opened_on_most_recent_step = 0

        # print "phase 3: {}".format(time.time()-t1)
        # t1 = time.time()

        distributionsHaveChanged = self.distribution.spriteInduction(self.environment._game, self.memory, step=3, bestSpriteTypeDict=self.bestSpriteTypeDict, oldSpriteSet=hypotheses[0].spriteSet)
        
        # print "phase 4: {}".format(time.time()-t1)
        # t1 = time.time()


        effects = self.environment.getEffectListByColor()
        effectList = self.environment._game.effectList
        
        if ended:
            self.quitting = ended
            self.episodeRecord.insert(0, (win, effects))

        if self.display_states:
            print "score: {}, game step: {}".format(self.environment.getScore(), self.environment.getTime())

        print "action", self.memory.totalGameSteps+self.environment.getTime()
        
        # print "phase 5: {}".format(time.time()-t1)
        # t1 = time.time()


        ## 'action', here refers to the previously-taken action,
        ## that led to the current state, current effects, current agentState
        event = {'agentState': self.agentState, 'agentAction': self.action, 'effectList': effects, \
            'gameState': None, 'rle': self.environment}

        newEffects = False

        ## If any collisions occurred
        if effects:
            # if self.display_text:
            # print effects
            # embed()
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

                if self.agentState[resource]>=limit and resource not in self.seen_limits:
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
        

        # print "phase 6: {}".format(time.time()-t1)
        

        inf_t1 = time.time()

        self.fakeInteractionRules = [r for r in self.fakeInteractionRules if
            not any([self.matchEventToRuleByIDAndSpriteName(e, r) for e in event['effectList']])]

        ## Ideally you'd update the model at every step, but it takes a lot of time
        ## so: Update when a new event happens (in which case you definitely need to update it), or when your MAP object-type hypothesis has changed for some class (in which case you definitely need to update it), or if we don't have a super-large number of time-steps in our history, do it sometimes (with probability .2)
        if (newEffects or (random.random()<.2 and len(self.finalTimeStepList)<300)) or distributionsHaveChanged:
            # print "event", (not all([e in all_effects for e in effects])), "distributions changed", distributionsHaveChanged
            # if self.display_text:
            print "new event", newEffects, "distributions changed", distributionsHaveChanged

            if newEffects or distributionsHaveChanged:
                theory_change_flag = True
            
            # t1 = time.time()
            
            sample, _, self.best_params= self.distribution.sampleFromDynamicTypeDistribution(self.environment._game, self.memory, self.all_objects, self.bestSpriteTypeDict, self.hypotheses[0].spriteSet, display=self.display_text)
            
            # print "inference phase 1: {}".format(time.time()-t1)
            # t1 = time.time()
            
            game_object = Game(spriteInductionResult=sample)
            
            terminationCondition = {'ended': False, 'win':False, 'time':self.environment.getTime()}
            trace = (self.finalTimeStepList, terminationCondition)

            hypotheses = list(game_object.runInduction(game_object.spriteInductionResult, trace, 20, \
            verbose=False, existingTheories=hypotheses))

            # print "inference phase 2: {}".format(time.time()-t1)
            # t1 = time.time()

            if hypotheses[0].__dict__ != self.hypotheses[0].__dict__:
                theory_change_flag = True

        # print "phase 7: {}".format(time.time()-inf_t1)
        # t1 = time.time()

        ## We also need to update termination conditions even when we haven't seen a new event,
        ## because the state is informative about termination conditions.
        oldTerminationSet = set(hypotheses[0].terminationSet)
        if event['effectList']:
            [t.updateTerminations(event=event) for t in hypotheses]

        if set(hypotheses[0].terminationSet) != oldTerminationSet:
            if self.display_text:
                print "terminationSet Change"
            theory_change_flag = True

        if theory_change_flag and not distributionsHaveChanged and self.display_text:
            print "changed theory:"
            # hypotheses[0].display()

        # print "phase 8: {}".format(time.time()-t1)
        # t1 = time.time()

        ## Setup for next timestep
        self.distribution.spriteInduction(self.environment._game, self.memory, step=1, bestSpriteTypeDict=self.bestSpriteTypeDict, oldSpriteSet=hypotheses[0].spriteSet, dynamic_type_lesion=self.dynamic_type_lesion)

        # print "phase 9: {}".format(time.time()-t1)
        # t1 = time.time()

        self.memory.nextPositions = {}
        for k, v in self.environment._game.all_objects.iteritems():
            self.memory.nextPositions[k] = (int(self.environment._game.all_objects[k]['sprite'].rect.x), int(self.environment._game.all_objects[k]['sprite'].rect.y))
            try:
                if self.memory.previousPositions[k] != self.memory.nextPositions[k]:
                    self.memory.objectMemoryDict[k] = copy.deepcopy(self.memory.previousPositions[k])
            except KeyError:
                pass
        self.memory.previousPositions = copy.deepcopy(self.memory.nextPositions)

        # print "phase 10: {}".format(time.time()-t1)
        # t1 = time.time()

        try:
            self.agentState = copy.deepcopy(self.environment.getAvatars()[0].resources)
        except IndexError:
            self.agentState = defaultdict(lambda: 0)

        self.bookkeeping.effectsEncountered.extend(effects)
        self.memory.episodeSteps +=1
        if theory_change_flag:
            self.hypotheses = hypotheses
            # self.hypotheses[0].display()

        self.re_plan = theory_change_flag

        # print "phase 11: {}".format(time.time()-t1)
        # t1 = time.time()

        self.action = self.planAsNeeded()

        # print "phase 12: {}".format(time.time()-t1)
        # t1 = time.time()

        print "quitting:", self.quitting
        return self.action, self.quitting

    def checkForDangerOrAvatarMisLocation(self, environment, hypothesis, predicted_states, i):
        
        ## For metacontroller to decide whether there's danger worth worrying about (like if something dangerous isn't where the agent predicted it would be), or if Avatar ended up in a surprising location.

        ## i corresponds to the index of the action we took

        regroundingFlag = False

        if not predicted_states:
            return regroundingFlag

        rleDict, hypDict = {}, {}

        for s in predicted_states[i].getAliveSprites():
            hypDict[s.ID2] = s

        try:
            killer_types = [inter.slot2 for inter in hypothesis.interactionSet if inter.slot1=='avatar' and inter.interaction in ['killSprite']]
            killer_colors = [hypothesis.classes[k][0].color for k in killer_types]
        except:
            print "problem in checkForDangerOrAvatarMisLocation"
            embed()

        for s in environment.getAliveSprites():
            ## If the object isn't in our predicted environment or the positions vary
            if s.name=='avatar' or s.colorName in killer_colors:
                if environment.getAvatars() and s.ID not in hypDict and manhattan_distance(s.rect, environment.getAvatars()[0].rect) < self.safeDistance*s.rect.width:

                    regroundingFlag=True
                    # if self.produce_printout:
                    print colored("Regrounding because we didn't predict the appearance of {} and it's too close for comfort".format(s), 'white', 'on_yellow')
                    break
                if s.name!='avatar' and environment.getAvatars() and s.ID in hypDict and s.rect!=hypDict[s.ID].rect and manhattan_distance(s.rect, environment.getAvatars()[0].rect) < self.safeDistance*s.rect.width:
                    # if self.produce_printout:
                    print colored("Regrounding because distance between {} and {} is {}, which is less than the safe distance of {}. We thought it would be at {}".format(
                            s, environment.getAvatars()[0], manhattan_distance(s.rect, environment.getAvatars()[0].rect), self.safeDistance*s.rect.width, hypDict[s.ID]),
                            'white', 'on_yellow')
                    # embed()
                    regroundingFlag=True
                    break
                if s.name=='avatar' and s.rect!=hypDict[s.ID].rect:
                    print colored("Regrounding because avatar is not where we expected", 'white', 'on_yellow')
                    regroundingFlag = True
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
                if not all([p.check(self.environment.agentStatePrev) for p in list(rule.preconditions)]):
                    return False
                else:
                    return True
        else:
            return False

    def manageNewObjects(self, hypotheses):
        ## Add newly-seen objects to object-type distribution
        current_objects = self.environment.getObjects()
        for k in current_objects.keys():
            spriteName = current_objects[k]['sprite'].name
            if spriteName not in [self.all_objects[key]['sprite'].name for key in self.all_objects.keys()]:
                if self.display_text:
                    print "new object", spriteName
                self.all_objects[k] = current_objects[k]
                self.distribution.distributionInitSetup(self.environment._game, k)
                ## prevent spriteInduction from trying to infer anything about newly-appeared sprites in this timestep, as likelihood function hasn't been seeded for these objects.
                self.memory.ignoreList.append(k)
                self.new_objects[spriteName] = 0

        return hypotheses

    def observe(self, environment, memory, obsSteps, bestSpriteTypeDict, display=False, hypothesis=None):
        ## Agent just observes the state for 'obsSteps' steps and updates object-type distribution.
        ## if called with obsSteps==0, it'll just initialize the object-type distribution
        if display and self.produce_printout:
            print "observing for {} steps".format(obsSteps)
        if obsSteps>0:
            for i in range(obsSteps):
                self.distribution.spriteInduction(environment._game, self.memory, step=1, bestSpriteTypeDict=bestSpriteTypeDict, dynamic_type_lesion=self.dynamic_type_lesion)
                # self.distribution.spriteInduction(environment._game, self.memory, step=2, bestSpriteTypeDict=bestSpriteTypeDict, dynamic_type_lesion=self.dynamic_type_lesion)
                environment.step((0,0))
                if self.make_movie or self.record_video_info:
                    self.bookkeeping.statesEncountered.append(self.environment.getFullState(observe_state=True))
                if self.record_states:
                    self.bookkeeping.compactStates.append(self.compactify(self.environment))
                if self.produce_printout:
                    print "score: {}, timestep: {}".format(environment.getScore(), environment.getTime())
                    print environment.show(color='blue')
                print "action", self.memory.totalGameSteps+environment.getTime()
                self.memory.nextPositions = {}
                for k, v in environment._game.all_objects.iteritems():
                    self.memory.nextPositions[k] = (int(environment._game.all_objects[k]['sprite'].rect.x), int(environment._game.all_objects[k]['sprite'].rect.y))
                    try:
                        if self.memory.previousPositions[k] != self.memory.nextPositions[k]:
                            self.memory.objectMemoryDict[k] = copy.deepcopy(self.memory.previousPositions[k])
                    except KeyError:
                        pass
                self.memory.previousPositions = copy.deepcopy(self.memory.nextPositions)
                self.distribution.spriteInduction(environment._game, self.memory, step=3,  bestSpriteTypeDict=bestSpriteTypeDict)
        else:
            self.distribution.spriteInduction(environment._game, self.memory, step=1,  bestSpriteTypeDict=bestSpriteTypeDict, dynamic_type_lesion=self.dynamic_type_lesion)
        return

    def makeHeatmap(self, statesEncountered, filename):
        from vgdl.plotting import featurePlot
        import matplotlib.pyplot as plt
        from matplotlib.ticker import NullLocator
        import numpy as np

        states = [s['objects']['avatar'].keys()[0] for s in statesEncountered
                  if (not s['observe_state']) and s['objects']['avatar'].keys()]
        width, height = self.environment.width, self.environment.height
        correction_factor = self.environment.screensize[0]/width
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

class Memory:
    def __init__(self):
        self.ignoreList = []
        self.objectMemoryDict = {}
        self.previousPositions = {}
        self.nextPositions = {}
        self.spriteUpdateDict = defaultdict(lambda : 0)
        self.totalGameSteps = 0
        self.episodeSteps = 0
