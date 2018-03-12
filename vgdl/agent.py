import multiprocessing as mp
from functools import partial
from util import *
from core import colorDict, VGDLParser, sys, keyPresses
from ontology import *
from theory_template import TimeStep, Precondition, InteractionRule, TerminationRule, TimeoutRule, \
SpriteCounterRule, MultiSpriteCounterRule, ruleCluster, Theory, Game, writeTheoryToTxt, generateSymbolDict, \
generateTheoryFromGame, expandLine, expandSprites, PreconditionInduction, proposePredicates, getRuleSetsForClassPairPredicate,\
interateThresholds
import os, subprocess, shutil
from collections import defaultdict
import importlib
import numpy as np
import ipdb, time
import os, subprocess, shutil
import copy
import math
import warnings
from metaplanner import translateEvents, observe
from rlenvironmentnonstatic import createRLInputGame, createRLInputGameFromStrings, defInputGame, createMindEnv
from stateobsnonstatic import buildTracker
from termcolor import colored
from line_profiler import LineProfiler
from vgdl.util import manhattanDist, manhattanDist2
from pygame.locals import K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT
from colors import colorDict
import copy_reg
import types

AvatarTypes = [MovingAvatar, HorizontalAvatar, VerticalAvatar, FlakAvatar, AimedFlakAvatar, OrientedAvatar,
RotatingAvatar, RotatingFlippingAvatar, NoisyRotatingFlippingAvatar, ShootAvatar, AimedAvatar,
AimedFlakAvatar, InertialAvatar, MarioAvatar]

ACTIONDICT = {K_UP: (0,1), K_DOWN: (0,-1),K_LEFT: (-1,0), K_RIGHT: (1,0), K_SPACE: (0,0), 0: (0,0)}

class errorMapEntry:
	def __init__(self):
		self.diagnosis = []
		self.targetToken = None
		self.targetClass = None
		self.targetColor = None
		self.intPairs = []
		self.culpritClasses = []
	
	def display(self):
		print ""
		print "diagnosis: {}".format(self.diagnosis)
		print "targetToken: {}".format(self.targetToken)
		print "targetClass: {}".format(self.targetClass)
		print "targetColor: {}".format(self.targetColor)
		# if self.targetToken is not None:
			# print "targetColor: {}".format(self.targetToken.colorName)
		print "intPairs: {}".format(self.intPairs)
		print "culpritClasses: {}".format(self.culpritClasses)

	def copy(self):
		e                   = errorMapEntry()
		e.diagnosis         = self.diagnosis
		e.targetToken       = ccopy(self.targetToken)
		e.targetClass       = self.targetClass
		e.targetColor 		= self.targetColor
		e.intPairs          = self.intPairs
		e.culpritClasses    = self.culpritClasses
		
		return e

	def __eq__(self, other):
		if self.diagnosis == other.diagnosis and self.intPairs == other.intPairs and self.culpritClasses == other.culpritClasses:
			return True
		else:
			return False

class Agent:
	def __init__(self, modelType, gameFilename):
		self.modelType = modelType
		self.gameFilename = gameFilename
		self.gameString = None
		self.levelString = None
		self.annealingFactor = 1.
		self.shortHorizon = False
		if self.shortHorizon == True:
			self.starting_max_nodes = 1000
			self.max_nodes_annealing = 1.05
		else:
			self.starting_max_nodes = 10000
			self.max_nodes_annealing = 10
		self.firstOrderHorizon = True ## Makes you commit to a plan once first-order distances change (e.g., spritecounter values)
		self.regrounding = 50
		self.selective_regrounding = True
		self.avoid_danger = True
		self.safeDistance = 6
		self.emptyPlansLimit = 5
		self.longHorizonObservationLimit = 2
		self.learnAvatar = True
		self.hypotheses = []
		self.symbolDict = None
		self.finalEventList = []
		self.statesEncountered = []
		self.fakeInteractionRules = []
		self.all_objects = {}
		self.bestSpriteTypeDict = defaultdict(lambda : {})
		self.spriteUpdateDict = defaultdict(lambda : 0)
		self.best_params = None
		## To track how many times we have run spriteType updates to each particular object
		# self.bestSpriteTypeDict = defaultdict(lambda: {'count':0, 'distribution':None})
		self.seen_resources = []
		self.seen_limits = []
		self.new_objects = {}
		self.memory = []
		self.rleHistory = []
		self.actionHistory = []
		self.allTheories = []
		self.theoryScoreHistory = []
		self.meanErrorHistory = []
		self.minStepError = []
		self.actionSet = [K_RIGHT, K_LEFT, K_UP, K_DOWN, K_SPACE]
		self.randomTheories = []
		self.benchmarkHistory = []
		self.resourceObservations = {'speed':[], 'changeResource':[]}
		self.observed_resources = set()
		self.distributions = {}
		self.history = {}
		self.lastObjectState = {}

	def initializeEnvironment(self):
		if self.gameString == None or self.levelString == None:
			self.gameString, self.levelString = defInputGame(self.gameFilename, randomize=False)
		self.rleCreateFunc = lambda: createRLInputGameFromStrings(self.gameString, self.levelString)
		self.rle = self.rleCreateFunc()
		self.rle._game.spriteUpdateDict = self.spriteUpdateDict
		self.rle._game.observation = buildTracker(self.rle)
		return

	def initializeRLEFromGame(self):
		gameString, levelString = self.gameString, self.levelString
		if gameString == None or levelString == None:
			gameString, levelString = defInputGame(self.gameFilename, randomize=False)
		rleCreateFunc = lambda: createRLInputGameFromStrings(gameString, levelString)
		rle = rleCreateFunc()
		return rle

	def getStateByColor(self, rle):
		state = {}
		for k in rle._game.sprite_groups.keys():
			if len(rle._game.sprite_groups[k]) > 0:
				color = rle._game.sprite_groups[k][0].colorName
				sprite_list = []
				for sprite in rle._game.sprite_groups[k]:
					if sprite not in rle._game.kill_list:
						if hasattr(sprite, 'orientation'):
							o = sprite.orientation 
						else:
							o = (0,0)

						sprite_list.append({'speed':sprite.speed, 'orientation':o, 'position':(sprite.rect.left,sprite.rect.top)})
				state[color] = sprite_list
		return state

	def IDmatch(self, envA, envB):
		"""
		Returns: dictionary with entries -> sB ID: matched sA ID
		"""
		warning = False
		d = {}
		# Match environments by position and color
		matched_sprites, lonely_sprites_envA, lonely_sprites_envB = matchEnvs(envA, envB)
		# Warn if there are unmatched or not accurately matched sprites
		if len(lonely_sprites_envA)!=0 or len(lonely_sprites_envB)!=0:
			warning = True
			print "WARNING: Unmatched sprites in IDmatch -> truPenalty potentially flawed"
			## this is called only when you're setting two environments. So by definition, the environments should
			## be identical.
		if any( [m[2]!=0 for m in matched_sprites] ) == True:
			#print "WARNING: Non-zero distance between matched sprites (in IDmatch)"
			pass
		# Assign IDs
		for m in matched_sprites:
			sA, sB = m[0], m[1]
			d[sB.ID.urn] = sA.ID.urn
		return d, warning

	def initializeHypotheses(self, allObjects, learnSprites=True, learnAvatar=True, num_variants=0):
		if learnSprites:
			observe(self.rle, 0, self.bestSpriteTypeDict)
			## Sample from distribution but actually just set everything to default.
			spriteTypeHypothesis, exceptedObjects, _, self.best_params = sampleFromDistribution(self.rle._game, \
				self.rle._game.spriteDistribution, allObjects, self.rle._game.spriteUpdateDict, self.bestSpriteTypeDict, \
				oldSpriteSet=None, mode='default', learnAvatar=learnAvatar)
			self.rle._game.exceptedObjects = exceptedObjects
			gameObject = Game(spriteInductionResult=spriteTypeHypothesis)
			initialTheory = gameObject.buildGenericTheory(spriteTypeHypothesis)
			initialTheory.terminationSet = [r for r in initialTheory.terminationSet if r.ruleType == 'SpriteCounterRule']
		else:
			gameObject = Game(self.gameString)
			initialTheory = gameObject.buildGenericTheory(spriteSample=False, vgdlSpriteParse = gameObject.vgdlSpriteParse)

		initialTheory.mostRecentEdit = 'none'

		self.symbolDict = generateSymbolDict(self.rle)

		if learnAvatar:
			## Instantiate a hypothesis that each singleton class might be the avatar
			self.hypotheses = []
			## Grab all singleton classes and instantiate hypotheses that they are the avatar.
			for color in self.symbolDict.keys():
				if len(getSpritesByColor(self.rle._game, color)) == 1:
					newTheory = copy.deepcopy(initialTheory)
					oldClassName = newTheory.spriteObjects[color].className
					del newTheory.classes[oldClassName]
					newTheory.spriteObjects[color].className = 'avatar'
					newTheory.spriteObjects[color].vgdlType = MovingAvatar
					newTheory.classes['avatar'] = [newTheory.spriteObjects[color]]

					for rule in newTheory.interactionSet:
						if rule.slot1 == oldClassName:
							rule.slot1='avatar'
						if rule.slot2 == oldClassName:
							rule.slot2='avatar'

					## Rename classes to ensure canonical ordering: c2, c3, ...
					if min([int(k[1:]) for k in newTheory.classes.keys() if 'c' in k])>2:
						for s in newTheory.spriteSet:
							if s.className is not None and 'c' in s.className:
								tmpClassName = s.className
								del newTheory.classes[tmpClassName]
								s.className = 'c'+str(int(s.className[1:])-1)
								newTheory.classes[s.className] = [s]
						for rule in newTheory.interactionSet:
							if 'c' in rule.slot1:
								rule.slot1 = 'c'+str(int(rule.slot1[1:])-1)
							if 'c' in rule.slot2:
								rule.slot2 = 'c'+str(int(rule.slot2[1:])-1)

					self.hypotheses.append(newTheory)
					self.distributions[color] = PreconditionInduction()
					self.history[color] = {}
		else:
			self.hypotheses = [initialTheory]

		## For debugging purposes: generate variants of the theory
		## (as a stand-in for a more generic induction/elaboration process)
		predicate_options = ['nothing', 'stepBack', 'killSprite', 'bounceForward', 'undoAll', 'reverseDirection']
		for i in range(num_variants):
			spriteTypeHypothesis, exceptedObjects, _, self.best_params = sampleFromDistribution(self.rle._game, \
				self.rle._game.spriteDistribution, allObjects, self.rle._game.spriteUpdateDict, self.bestSpriteTypeDict, \
				oldSpriteSet=None, mode='random')
			gameObject = Game(spriteInductionResult=spriteTypeHypothesis)
			theory = gameObject.buildGenericTheory(spriteTypeHypothesis)
			for interactionRule in theory.interactionSet:
				if interactionRule.slot1 == 'avatar':
					interactionRule.interaction = random.choice(['nothing', 'stepBack', 'bounceForward', 'undoAll', 'reverseDirection'])
				else:
					interactionRule.interaction = random.choice(predicate_options)
				if interactionRule.slot2 == 'EOS' and interactionRule.slot1!='avatar':
					interactionRule.interaction = random.choice(['stepBack', 'reverseDirection', 'killSprite'])

			theory.terminationSet = [r for r in initialTheory.terminationSet if r.ruleType == 'SpriteCounterRule']

			self.randomTheories.append(theory)

		return gameObject

	def testCurriculum(self, level_game_pairs=None):
		if not level_game_pairs:
			level_game_pairs = importlib.import_module(self.gameFilename).level_game_pairs  
		
		for n_level, level_game in enumerate(level_game_pairs):

			print("Playing level {}".format(n_level))
			(self.gameString, self.levelString) = level_game

			gameObject = None

			for epoch in range(1):
				# self.testTracker(gameObject)
				self.testEpisode(gameObject,epoch=epoch)
		return

	def testEpisode(self, gameObject, epoch=0):
		
		actions = [K_LEFT, K_LEFT, K_LEFT, K_LEFT, K_DOWN, K_DOWN, K_RIGHT, K_RIGHT, K_RIGHT, K_RIGHT, K_RIGHT, K_RIGHT, K_RIGHT]
		# actions = [K_LEFT, K_LEFT, K_DOWN, K_DOWN, K_RIGHT, K_RIGHT, K_RIGHT]
		# actions = [K_LEFT, K_UP, K_LEFT, K_LEFT]
		self.initializeEnvironment()
		# embed()

		self.trueTheory = generateTheoryFromGame(self.rle)
		self.trueTheory.trueTheory = True

		print "initializing RLE. Epoch={}".format(epoch)
		num_cores = mp.cpu_count()
		print "num cores: {}".format(num_cores) 
		if num_cores<40:
			print "WARNING: running on < 40 cores."

		self.all_objects= self.rle._game.getObjects()

		if epoch == 0:
			gameObject = self.initializeHypotheses(self.all_objects, learnSprites=True, learnAvatar=self.learnAvatar, num_variants=0)

		## Start storing encountered states.
		effectsEncountered = []
		statesEncountered = [self.rle._game.getFullState()]
		self.statesEncountered.append(self.rle._game.getFullState())
		envReal = self.fastcopy(self.rle)
		self.rleHistory.append(envReal)

		t1 = time.time()
		for num, action in enumerate(actions):
			if self.rle._isDone()[0]:
				print "Game is over."
				break
			print ">>> Step", num+1, "of", len(actions), "<<<"
			## initialize VRLEs
			theoryRLEs = VrleInitPhase(self.hypotheses, self.rle, self.symbolDict, self.best_params)
			lastStep=False
			if num == len(actions)-1:
				lastStep=True
			t2 = time.time()
			hypotheses = self.executeStep(action, self.hypotheses, theoryRLEs, lastStep)
			print ""
			print "executed step in {} seconds".format(time.time()-t2)
			print ""
			self.hypotheses = hypotheses

		print "{} time-steps took {} seconds".format(len(actions), time.time()-t1)
		# print ">>> Embedded at the end of testEpisode"
		embed()

		return

	def manageNewObjects(self, hypotheses, envRealPrev, action, learnAvatar=True):

		## Add newly-seen objects.
		current_objects = self.rle._game.getObjects()
		if learnAvatar:
			if any([current_objects[k]['sprite'].colorName not in [self.all_objects[key]['sprite'].colorName for key in self.all_objects.keys()] for k in current_objects.keys()]):
				for k in current_objects.keys():
					distributionInitSetup(self.rle._game, k)
					if k not in self.all_objects.keys():
						self.all_objects[k] = current_objects[k]
				spriteInduction(self.rle._game, step=1, bestSpriteTypeDict=self.bestSpriteTypeDict, action=action,
					oldSpriteSet=self.hypotheses[0].spriteSet, old_outcome=None, specificSpritesToUpdate=[], 
					percentile=10, max_num=20, allMovement=False)
				spriteInduction(self.rle._game, step=2, bestSpriteTypeDict=self.bestSpriteTypeDict, action=action,
					oldSpriteSet=self.hypotheses[0].spriteSet, old_outcome=None, specificSpritesToUpdate=[], 
					percentile=10, max_num=20, allMovement=False)
		else:
			for k in current_objects.keys():
				colorName = current_objects[k]['sprite'].colorName
				if colorName not in [self.all_objects[key]['sprite'].colorName for key in self.all_objects.keys()]:
					self.all_objects[k] = current_objects[k]
					distributionInitSetup(self.rle._game, k)
					## prevent spriteInduction from trying to infer anything about newly-appeared sprites in this timestep.
					self.rle._game.ignoreList.append(k)
					self.new_objects[colorName] = 0

		return hypotheses

	def predictCollisionsBasedOnTheory(self, theory, envReal, envRealPrev, action):
		avatar_color = theory.classes['avatar'][0].colorName
		observation = envRealPrev._game.observation['trackedObjects']
		avatar_is_dead = len(envReal._game.observation['trackedObjects'][avatar_color]) == 0

		predictions = {k:[] for k,v in observation.iteritems() if len(v)>0}
		trackedSprites = [item for sublist in observation.values() for item in sublist]
		
		## Generate predictions for each sprite. We do this rather than running an RLE forward because
		## an RLE about a hypothetical theory won't necessarily make the right collisions happen.
		## That is, we need to know what collisions might potentially occur and know the involved items.
		for trackedSprite in trackedSprites:
			try:
				speed = trackedSprite.speed
				if speed is None:
					speed = 1.
				if trackedSprite.colorName == avatar_color and not \
				any([k in str(theory.classes['avatar'][0].vgdlType) for k in ['Aimed', 'Rotating', 'Oriented']]):
					orientation = ACTIONDICT[action]
				else:
					orientation = trackedSprite.orientation
				pos = (trackedSprite.rect.left, trackedSprite.rect.top)
				expected_pos = [pos[0]+orientation[0]*speed*trackedSprite.rect.width, \
								pos[1]+orientation[1]*speed*trackedSprite.rect.width]
				predictions[trackedSprite.colorName].extend([expected_pos])
			except:
				print "had trouble with avatar prediction in getTheoryLadenPrediction"
				embed()

		if avatar_is_dead:
			avatar_loc = predictions[avatar_color][0]
		else:
			avatar_loc = envReal._game.observation['trackedObjects'][avatar_color][0].rect.left, \
						 envReal._game.observation['trackedObjects'][avatar_color][0].rect.top

		candidates = []
		locs = {}
		for key in predictions:
			for location in predictions[key]:
				if self.intersect(location, avatar_loc):
					candidates.append(key)
					locs[key] = location
					break
		return candidates, locs

	def intersect(self, p1, p2):
		return (abs(p1[0] - p2[0]) <= self.rle._game.block_size and abs(p1[1] - p2[1]) <= self.rle._game.block_size)
	
	def fastcopy(self, rle):

		newRle = self.initializeRLEFromGame()
		newRle._obstypes = ccopy(rle._obstypes)
		if hasattr(rle, '_gravepoints'):
			newRle._gravepoints = ccopy(rle._gravepoints)
		newRle._game.sprite_groups = ccopy(rle._game.sprite_groups)
		newRle._game.kill_list = ccopy(rle._game.kill_list)
		newRle._game.lastcollisions = ccopy(rle._game.lastcollisions)
		newRle._game.time = ccopy(rle._game.time)
		newRle._game.score = ccopy(rle._game.score)
		newRle._game.keystate = ccopy(rle._game.keystate)
		newRle._game.observation = ccopy(rle._game.observation)
		newRle.symbolDict = ccopy(rle.symbolDict)
		newRle._game.sprite_groups['avatar'][0].resources = ccopy(rle._game.sprite_groups['avatar'][0].resources)
		return newRle

	def executeStepProfiler(self, action, hypotheses, theoryRLEs, lastStep=False):
		lp = LineProfiler()
		lp_wrapper = lp(self.executeStep)
		hypotheses = lp_wrapper(action, hypotheses, theoryRLEs, lastStep)
		lp.print_stats()
		return hypotheses

	def executeStep(self, action, hypotheses, theoryRLEs, lastStep=False):

		theory_change_flag = False

		t1=time.time()
		spriteInduction(self.rle._game, step=1, bestSpriteTypeDict=self.bestSpriteTypeDict, action=action,
			oldSpriteSet=hypotheses[0].spriteSet, old_outcome=None, specificSpritesToUpdate=[], 
			percentile=10, max_num=20, allMovement=False)
		spriteInduction(self.rle._game, step=2, bestSpriteTypeDict=self.bestSpriteTypeDict, action=action,
			oldSpriteSet=hypotheses[0].spriteSet, old_outcome=None, specificSpritesToUpdate=[], 
			percentile=10, max_num=20, allMovement=False)
		print "spriteInduction prep took {} seconds".format(time.time()-t1)

		envRealPrev = self.fastcopy(self.rle)
		self.actionHistory.append(action)
		
		# print "pre-step in executeStep"
		# from vgdl.agent import VrleInitPhase, matchEnvs
		## self.hypotheses[0].interactionSet = self.hypotheses[0].interactionSet[0:-1]
		# theoryRLEs = VrleInitPhase(self.hypotheses, self.rle, self.symbolDict, self.best_params)
		# embed()

		self.rle.step(action)
		envReal = self.fastcopy(self.rle)
		hypotheses = self.manageNewObjects(hypotheses, envRealPrev, action, learnAvatar=self.learnAvatar)

		## We are passing the real environment, but experienceReplay filters that rle through the processFrame function (via matchEnvs()).
		self.rleHistory.append(envReal)
		
		_, new_sprites, _ = matchEnvs(envReal, envRealPrev)
		self.rle._game.sprite_appearances = new_sprites

		print ""
		print keyPresses[action]
		print self.rle.show(color='blue')

		print "evaluating {} old theories and proposing new ones".format(len(theoryRLEs))
		updateTerminations(self.rle, hypotheses)
		newTheories = []
	
		for num, env in enumerate(theoryRLEs):
			theories = testAndExpand(theoryRLEs, self.hypotheses, action, self.rle, envRealPrev, num, \
				self.rleHistory, self.actionHistory, self.symbolDict, self.best_params, self.bestSpriteTypeDict)
			newTheories.extend(theories)

		# print "Have {} new theories in outer loop".format(len(newTheories))
		# t1 = time.time()
		newTheories = list(set(newTheories))
		# print "filtering took {} seconds".format(time.time()-t1)
		# print "After filtering for duplicates, have {} theories".format(len(newTheories))
		# embed()
		self.allTheories.extend(newTheories)
		print ""
		print "Tested and expanded {} theories to produce {} child theories".format(len(theoryRLEs), len(newTheories))

		if newTheories:
			penalties, cumulative_penalties, experienceReplayRLEs = experienceReplay(newTheories, self.rleHistory, self.actionHistory,
				self.symbolDict, self.best_params, method='all', displayTheories=False)

			scoreAndTheoryTuples = zip(penalties, newTheories)
			scoreAndTheoryTuples = sorted(scoreAndTheoryTuples, key=lambda x: (x[0], len(x[1].interactionSet)))

			for num, sh in enumerate(scoreAndTheoryTuples):
				print "Theory: {} | Error: {}".format(num, sh[0])
				sh[1].display()
			scoreAndTheoryTuples = [s for s in scoreAndTheoryTuples if not hasattr(s[1],'trueTheory')]      

			if not lastStep:
				scoresAndHypotheses = [(h[0],h[1]) for h in filterTheories(scoreAndTheoryTuples, percentile=30, max_num=30,
					proportionOfSpriteTheories=None)]
			else:
				scoresAndHypotheses = [(h[0],h[1]) for h in filterTheories(scoreAndTheoryTuples, percentile=30, max_num=30,
					proportionOfSpriteTheories=None)]

			print "Experience replay complete."
			for num, sh in enumerate(scoresAndHypotheses):
				print "Theory: {} | Error: {}".format(num, sh[0])
			print ""
			hypotheses = [sh[1] for sh in scoresAndHypotheses]
			print "{} survived".format(len(hypotheses))

			if len(hypotheses) == 0:
				print "0 hypotheses survived filter"
				embed()
		else:
			print "Got no new theories"

		# print "just expanded all theories"
		# embed()

		self.statesEncountered.append(self.rle._game.getFullState())
		self.rle._game.sprite_appearances = []

		for h in hypotheses:
			h.dryingPaint = set()
		return hypotheses


	########################################################################
	######## TESTING HYPOTHESES BY RANDOM SAMPLING OR OTHER METHODS ########
	########################################################################


	def testSteps(self, rle, actions, hypotheses, last_only=False, check=False):
		## Evaluates all the hypotheses on the state of the provided rle, given actions.
		## last_only: will take all actions and only *then* evaluate the distance between real and imagined states
		
		theoryRLEs = VrleInitPhase(hypotheses, rle, self.symbolDict, self.best_params)
		# Match IDs between real and theory RLEs
		ID_dictlist = []
		for tR in theoryRLEs:
			match, warning = self.IDmatch(tR, rle)
			if warning:
				print "IDmatch produced a warning, but environments should be the same"
				embed()
			ID_dictlist.append( match)
		# Calculate penalties
		cumulative_penalties = []

		for n,action in enumerate(actions):
			penalties = []
			if last_only == False or n == len(actions)-1:
				envRealPrev = self.fastcopy(rle)
			rle.step(action)
			for num, env in enumerate(theoryRLEs):
				env.step(action)
				if last_only == False or n == len(actions)-1:
					penalty = self.truPenalty(env, rle, ID_dictlist[num])
					# penalty, errorList = errorSignal(env, rle, hypotheses[num], envRealPrev)
					penalties.append(penalty)
			if last_only == False or n == len(actions)-1:
				cumulative_penalties.append(penalties)

		cumulative_penalties = np.array(cumulative_penalties)
		return np.mean(cumulative_penalties, axis=0)

	def randomizeState(self, rle):
		rleCopy = self.fastcopy(rle)
		x_options = range(1, rleCopy._game.width-1)
		y_options = range(1, rleCopy._game.height-1)
		pos_options = list(itertools.product(x_options, y_options))
		nonWallObjects = [s for sp in rleCopy._game.sprite_groups.values() for s in sp if s.name!='wall']
		for obj in nonWallObjects:
			newPos = random.choice(pos_options)
			pos_options.remove(newPos)
			rleCopy._setRectPos(obj, newPos)
		rleCopy.step(0)
		return rleCopy
	
	def sampleWithReplacement(self, lst, k):
		outlist = []
		for i in range(k):
			outlist.append(random.choice(lst))
		return outlist

	def testHypotheses(self, hypotheses, rrle=[], num_samples=10, actions_per_sample=10, last_only=False, check=False):
		if rrle == []:
			rle = self.initializeRLEFromGame()
			rrle = []
			for sample in range(num_samples):
				rrle.append(self.randomizeState(rle))
		cumulative_penalties = []
		for sample in range(num_samples):
			actions = self.sampleWithReplacement(self.actionSet, actions_per_sample)
			penalties = self.testSteps(rrle[sample], actions, hypotheses, last_only=last_only, check=False)
			cumulative_penalties.append(penalties)
		cumulative_penalties = np.array(cumulative_penalties)
		cumulative_penalties = list(np.mean(cumulative_penalties, axis=0))
		scoreAndTheoryTuples = zip(cumulative_penalties, hypotheses)
		return scoreAndTheoryTuples

########################################################################
######## RLE INITIALIZATION AND STATE-SETTING METHODS 			########
########################################################################

def setVrleStateProfiler(rle, Vrle, hypothesis, best_params):
	lp = LineProfiler()
	lp_wrapper = lp(setVrleState)
	hypotheses = lp_wrapper(rle, Vrle, hypothesis, best_params)
	lp.print_stats()
	return


def setVrleState(rle, Vrle, hypothesis, best_params):
	## Sets positions of objects in Vrle to what they were in the rle. Bypasses clunky VGDL level description.

	avatar = hypothesis.classes['avatar'][0]
	spriteGroupsToUpdate = Vrle._game.sprite_groups
	for k in spriteGroupsToUpdate.keys():
		if spriteGroupsToUpdate[k]:
			color = Vrle._game.sprite_groups[k][0].colorName
			matchingSpritesInRLE = getObservedSpritesByColor(rle._game, color)
			for sprite in spriteGroupsToUpdate[k]:
				matchingSprite = findNearestSprite(sprite, matchingSpritesInRLE)
				# embed()
				if matchingSprite is None:
					continue
				sprite.rect 		= pygame.Rect(matchingSprite.rect.left, matchingSprite.rect.top, matchingSprite.rect.width, matchingSprite.rect.height)
				sprite.lastrect 	= pygame.Rect(matchingSprite.lastrect.left, matchingSprite.lastrect.top, matchingSprite.lastrect.width, matchingSprite.lastrect.height)
				if sprite.rect.left != sprite.lastrect.left and sprite.rect.top != sprite.lastrect.top and abs(sprite.rect.left  - sprite.lastrect.left ) != abs(sprite.rect.top - sprite.lastrect.top):
					print "in setVrleState -- illegal rect/lastrect pair"
					embed()
				sprite.lastmove 	= matchingSprite.lastmove
				
				sprite.resources = defaultdict(int)
				for rcolor in matchingSprite.inventory.keys():
					sprite.resources[hypothesis.spriteObjects[rcolor].className] = matchingSprite.inventory[rcolor][0]
				# sprite.resources    = {hypothesis.spriteObjects[rcolor].className: matchingSprite.inventory[rcolor]
											# for rcolor in matchingSprite.inventory.keys()}

				# in VGDL, only things which move passively have an orientation that isn't (0,0)
				#	if we set
				if (hypothesis.spriteObjects[matchingSprite.colorName].vgdlType in
						[MovingAvatar, HorizontalAvatar, VerticalAvatar]):
					sprite.orientation = (0,0)
				else:
					sprite.orientation 	= tuple(matchingSprite.orientation) # consider copying only for avatar?


				## Other aspects of state to potentially transfer
				# sprite.jumping = ccopy(matchingSprite.jumping)
				# sprite.wait_step = ccopy(matchingSprite.wait_step)
				# sprite.rope = ccopy(matchingSprite.rope)
				# sprite.gravity = ccopy(matchingSprite.gravity)
				# sprite.last_rope = ccopy(matchingSprite.last_rope)
				# sprite.last_gravity = ccopy(matchingSprite.last_gravity)
				# sprite.last_vy = ccopy(matchingSprite.last_vy)
				# sprite.speed = ccopy(matchingSprite.speed)
	Vrle._game.score = int(rle._game.score)
	# if 
	# print 'in setVrleState'
	# embed()
	Vrle._game.observation = buildTracker(Vrle)
	Vrle._game.observation['lastscore'] = rle._game.observation['lastscore']

	return

def initializeVrleProfiler(hypothesis, stateToSet, symbolDict, best_params):
	lp = LineProfiler()
	lp_wrapper = lp(initializeVrle)
	Vrle = lp_wrapper(hypothesis, stateToSet, symbolDict, best_params)
	lp.print_stats()
	return Vrle

def initializeVrle(hypothesis, stateToSet, symbolDict, best_params, writeFile=False, debug=False):

	## World in agent's mind given 'hypothesis', including object goal
	gameString, levelString, symbolDict = writeTheoryToTxt(stateToSet, hypothesis, symbolDict,\
		 "./examples/gridphysics/theorytest.py", writeFile=writeFile)

	try:
		Vrle = createMindEnv(gameString, levelString, output=False)
	except:
		print "in initializeVrle"
		embed()
	Vrle._game.colorToClassDict = {k:v.className for k,v in hypothesis.spriteObjects.items()}
	## Don't do any of the rest if we have an ungrammatical hypothesis caused by num(avatars)>1.
	if len(stateToSet._game.observation['trackedObjects'][hypothesis.classes['avatar'][0].colorName])>1:
		print "Warning. In initializeVrle. Got more than one avatar. Returning None as Vrle."
		Vrle = None
		return Vrle
	
	## Initialize imaginary state to match real state.
	setVrleState(stateToSet, Vrle, hypothesis, best_params)

	return Vrle

def VrleInitPhaseProfiler(hypotheses, stateToSet, symbolDict, best_params):
	lp = LineProfiler()
	lp_wrapper = lp(VrleInitPhase)
	VRLEs = lp_wrapper(hypotheses, stateToSet, symbolDict, best_params)
	lp.print_stats()
	return VRLEs

def VrleInitPhase(hypotheses, stateToSet, symbolDict, best_params):
	## Initialize multiple VRLEs, each corresponding to one hypothesis in theories
	## Set their state to that of the provided RLE
	VRLEs = []

	for hypothesis in hypotheses:
		VRLEs.append(initializeVrle(hypothesis, stateToSet, symbolDict, best_params))

	return VRLEs

def findNearestSprite(sprite, spriteList):
	## returns the sprite in spriteList whose location best matches the location of sprite.
	if spriteList == []:
		return None
	else:
		distList = [abs(x.rect.left-sprite.rect.left)+abs(x.rect.top-sprite.rect.top) for x in spriteList]
		return spriteList[distList.index(min(distList))]



########################################################################
######## ERROR SIGNAL AND STATE-COMPARISON METHODS 				########
########################################################################


## Function generating penalty and error map
def errorSignal(envA, envB, theory, envPrev, p_dist=1, p_speed=1, p_miss=10, p_score=1, targetColor=None, penalty_only=False):
	"""
	envA: hypothetical environment
	envB: real environment
	theory: corresponds to hypothetical
	p_dist: distance penalty per grid point
	p_speed: pentalty for distances arising from wrong speed
	p_miss: penalty for missing or additional sprite
	p_score: penalty for getting the score wrong
	penalty_only: return penalty, [] (empty list instead or errorMap)

	Calculates d_theory(envA, envB): distance between the states of the environments
	using the ontology of the supplied theory.

	Also returns errorMap, a dict that contains
	keys: (class1, class2). values: a diagnostic error signal
	"""

	# Initialization
	total_penalty = 0.
	errorMap = []

	## Check for an ungrammatical theory.
	if envA is None:
		print "Warning: got ungrammatical theory"
		e = errorMapEntry()
		e.diagnosis.append('ungrammatical theory')
		e.targetToken = None
		e.targetClass = None
		e.targetColor = None
		errorMap.append(e)
		total_penalty = 1e6
		return total_penalty, errorMap

	# Match sprites in environments and get sprites that couldn't be matched
	matched_sprites, lonely_sprites_envA, lonely_sprites_envB = matchEnvs(envA, envB)

	# if not targetColor:
		# print matched_sprites
	if targetColor:
		try:
			matched_sprites = [m for m in matched_sprites if m[0].colorName == targetColor]
			# print targetColor
			# if matched_sprites:
				# targetColor = matched_sprites[0][0].colorName
				# print targetColor
			lonely_sprites_envA = [s for s in lonely_sprites_envA if s.colorName == targetColor]
			lonely_sprites_envB = [s for s in lonely_sprites_envB if s.colorName == targetColor]
			# print len(lonely_sprites_envA), len(lonely_sprites_envB)
			# else:
				# lonely_sprites_envA = []
				# lonely_sprites_envB = []
		except:
			print "targetClass filter in errorSignal failed"
			embed()
	## Test output
	# print '>>> matched_sprites:'
	# for i in range(len(matched_sprites)):
		# if True: #matched_sprites[i][2]!=0:
			# print matched_sprites[i]
	# print '>>> lonely_sprites_envA:', [s for s in lonely_sprites_envA]
	# print '>>> lonely_sprites_envB:', [s for s in lonely_sprites_envB]

	## Penalize distance and additional/missing sprites
	for t in matched_sprites:
		## Distance penalty
		sA, sB = t[0], t[1] #sprites in envA, envB      
		dist = t[2] #distance to sprite in envB
		sA_type = theory.spriteObjects[sA.colorName].vgdlType
		d = 30. # grid spacing

		# If RandomNPC: compare sB position to where it could have been given the hypothetical speed and random direction
		if 'Random' in str(sA_type):   


			if 'speed' in theory.spriteObjects[sA.colorName].args.keys():
				sA_speed = theory.spriteObjects[sA.colorName].args['speed']
			elif 'speed' in theory.spriteObjects[sA.colorName].__dict__.keys():
				sA_speed = theory.spriteObjects[sA.colorName].speed
			else:
				## this only happens when you initialize the real theory for testing but haven't explicitly set the speed
				## in the VGDL description
				sA_speed = 1
			sPrev, dist_ts = find_sPrev(sB, envB, envPrev) #sA in previous environment
			if sPrev is None:
				continue
			xB = sB.rect.left/d
			yB = sB.rect.top/d
			xPrev = sPrev.rect.left/d
			yPrev = sPrev.rect.top/d

			dist_rNPC = manhattanDist((xB,yB), (xPrev, yPrev))
			# dist_rNPC = [ manhattanDist( (xB,yB), (xPrev,yPrev) ), \
			#                    manhattanDist( (xB,yB), (xPrev+sA_speed,yPrev) ), \
			#                    manhattanDist( (xB,yB), (xPrev-sA_speed,yPrev) ), \
			#                    manhattanDist( (xB,yB), (xPrev,yPrev+sA_speed) ), \
			#                    manhattanDist( (xB,yB), (xPrev,yPrev-sA_speed) ), \
			#                  ]
			# mindist_rNPC = min(dist_rNPC)
			# total_penalty += p_speed*mindist_rNPC #penalize speed separately to discourage keeping around too many similar theories
			
			total_penalty += p_speed*min(dist,1.)
		elif 'Missile' in str(sA_type):
			total_penalty += p_speed*t[2] #penalize speed separately to discourage keeping around too many similar theories
		elif 'Chaser' in str(sA_type):
			
			sPrev, _ = find_sPrev(sB, envB, envPrev)
			xA = sA.rect.left/d
			yA = sA.rect.top/d
			if sPrev is None:
				continue

			## TODO: This will break if things don't exist in the game at this point that match stype
			# stype = theory.spriteObjects[sA.colorName].args['stype']

			sA.stype = getSpritesByColor(envPrev._game, sA.colorName)[0].colorName
			sA.fleeing = theory.spriteObjects[sA.colorName].args['fleeing']
			try:
				closestTargets = findChaserOptions(sA, sPrev, envPrev._game, fleeing=sA.fleeing) ##TODO: Don't use envPrev._game.
			except:
				print "tried to find chaseroptions in errorSignal"
				embed()

			#New 2/12
			del sA.stype
			del sA.fleeing

			## this should be arbitrarily high, actually. If you want this to be a surrogate likelihood function,
			## the prob that a chaser moves away from what it's chasing is 0.
			chaser_penalty = 0. if (xA,yA) in closestTargets else 100.

			total_penalty += p_speed*chaser_penalty
		# All of the other types are deterministic
		else:
			total_penalty += p_dist*t[2] 


		inventory_penalty = 0
		keys = list(set(t[0].inventory.keys()+t[1].inventory.keys()))

		for k in keys:
			t0_k = t[0].inventory[k] if k in t[0].inventory.keys() else (0,0)
			t1_k = t[1].inventory[k] if k in t[1].inventory.keys() else (0,0)
			inventory_penalty += abs(t0_k[0]-t1_k[0])

		# if not targetColor and len(keys)>0 and not 'changeResource' in [r.interaction for r in theory.interactionSet] and inventory_penalty == 0:
		# 	print keys
		# 	print "in errorSignal, looking at targetColor and keys"
		# 	print "inventory_penalty", inventory_penalty
		# 	embed()
		total_penalty += inventory_penalty

	# Missing/additional/transformation penalty
	total_penalty += p_miss * ( len(lonely_sprites_envA) + len(lonely_sprites_envB) )

	if envA._game.observation['score'] != envB._game.observation['score']:
		total_penalty += p_score*abs(envA._game.observation['score']-envB._game.observation['score'])

	if penalty_only:
		return total_penalty, []

	### Construct errorMap using previous state ###

	# 1) Position mismatch: Things have moved.

	# Case A: matched sprites have different positions from what predicted
	for t in matched_sprites:
		dist_envs = t[2] #distance between sprites in real and theory environments
		if dist_envs == 0.: #sprites located where expected -> no conflict
			continue
		sA = t[0]
		sB = t[1]
		posCurr = envB._rect2pos(sB.rect) #current position of sprite
		# Find sprite corresponding to sB in previous time step
		sPrev, dist_ts = find_sPrev(sB, envB, envPrev)
		if sPrev == None:
			warnings.warn('sPrev not found in position mismatch error')
			continue
		# Determine errorMapEntry object for position mismatch problem
		errs = diagnosePosMismatch(sA, sB, sPrev, envA, envB, envPrev, dist_ts)
		errorMap.extend(errs)

	# Case B: Sprite moved in real environment, but we predicted a destruction
	# For this, we check if lonely envB sprite has match in envPrev (and pass to (2) if not)
	appeared_sprites_envB = []
	for sB in lonely_sprites_envB:
		# Find sprite corresponding to sB in previous time step
		sPrev, dist_ts = find_sPrev(sB, envB, envPrev)
		if sPrev == None: #sB has no match in envPrev
			appeared_sprites_envB.append(sB)
			continue 

		# Find erroneously destroyed sA by finding envA sprite closest to sPrev
		candidates_in_killList = [s for s in envA._game.kill_list if s.colorName == sPrev.colorName]
		
		## These are both double-checking things that should have been taken care of better
		## by the sprite matching. But since it's imperfect given our limited knowledge, we're
		## being more thorough.

		if candidates_in_killList == []:
			if not sPrev: #there is no envA sprite where sPrev should have been
				print "empty killList in A, meaning the matching is wrong"
				## You need to figure out what to pass to diagnosePosMismatch for sA, since it
				## doesn't exist.
				embed()
				#appeared_sprites_envB.append(sB)
				continue
		else:
			sA = findNearestSprite(sPrev, candidates_in_killList)
			if manhattanDist2(sA, sPrev)>1 and not sPrev: #there is no envA sprite where sPrev should have been
				## if there was a kill event and an appearance event somewhere far, we should really see this as
				## an appearance
				## Really, you should look at sprite matching better.

				print "manhattanDist2 > 1"
				embed()
				appeared_sprites_envB.append(sB)
				continue
		# Now we are completely sure that sprite in envA has been erroneously removed
		errs = diagnosePosMismatch(sA, sB, sPrev, envA, envB, envPrev, dist_ts)
		errorMap.extend(errs)

	# 2) Unexpected destruction/appearance/transformation
	# 2.1) Transformation
	for iA,sA in enumerate(lonely_sprites_envA):
		for iB,sB in enumerate(appeared_sprites_envB):
			if manhattanDist2(sA, sB)<=2:
				e = errorMapEntry()
				e.diagnosis.append('transformation')
				e.targetToken = sA
				e.targetClass = sA.colorName
				e.targetColor = sA.colorName
				# Find sprite corresponding to sB in previous time step
				color = sB.colorName
				sB.colorName = sA.colorName
				matched_ts, _, _ = matchEnvs(envB, envPrev) #matches real env across timestep
				sB.colorName = color
				sPrev = [matched_ts[i][1] for i in range(len(matched_ts)) if matched_ts[i][0] == sB]

				if sPrev == []: #This was an appearance, pass to (2.3) below
					continue
				else: #This was indeed a transformation
					print "WARNING: Found unexpected transformation"
					sPrev = sPrev[0]
					# Find neighbors of target sprite in the previous time step
					neighbors_prev = neighborsPrev(envA, envPrev, sPrev)
					# Write potential interaction pairs to error map entry
					for className in neighbors_prev:
						e.intPairs.append( (theory.spriteObjects[sPrev.colorName].className,className) )
					errorMap.append(e)
					# Remove transformed-sprite-pair from respective lists
					lonely_sprites_envA.pop(iA)
					appeared_sprites_envB.pop(iB)
	# if envB._isDone()[0]:
		# print "avatar died. in errorSignal"
		# embed()
	# 2.2) Destruction
	for sA in lonely_sprites_envA: #sA should have been destroyed
		e = errorMapEntry()
		e.targetClass = sA.colorName
		e.targetColor = sA.colorName
		candidates_in_killList = [s for s in envB._game.kill_list if s.colorName == sA.colorName]
		sB = findNearestSprite(sA, candidates_in_killList)
		if sB == None:
			print "WARNING: No target and interaction pair found in object destruction. You have not implemented this diagnosis."
			e.diagnosis.append('objectDidNotAppear')
			e.targetToken = None
			e.intPairs = []
			errorMap.append(e)
			continue
		else:
			e.diagnosis.append('objectDestruction')
			e.targetToken = sB
			# Find the sprite that was destroyed in envB from the kill_list
			# Find neighbors of target sprite in the previous time step
			sPrev = sB #sprite was destroyed but hasn't moved

		neighbors_prev = neighborsPrev(envA, envPrev, sPrev)
		neighbors_prev = [c for c in neighbors_prev if c!=sA.colorName]
		# Write potential interaction pairs to error map entry
		for className in neighbors_prev:
			e.intPairs.append( (sA.colorName,className) )
		errorMap.append(e)
	# 2.3) Appearance
	for sB in appeared_sprites_envB:
		print "WARNING: Found unexpected appearance"
		e = errorMapEntry()
		e.diagnosis.append('newObjectAppeared')
		e.targetToken = sB

		# Find class of new object by comparing colors, or give 'unknown' if unsuccessful
		color = sB.colorName
		all_sprites_envA = []
		for g in envA._game.sprite_groups.keys():
			all_sprites_envA += envA._game.sprite_groups[g]
		sMatch = [s for s in all_sprites_envA if s.colorName == color]
		if sMatch == []:
			e.targetClass = 'unknown'
		else:
			e.targetClass = sMatch[0].colorName
			e.targetColor = sMatch[0].colorName

		# Find neighbors of target sprite in the real environment (envB) in the current time step -> could have caused appearance
		# And also in the previous time-step.
		# Simultaneously find culprit classes - an overlapping sprite could have launched the sprite due to its class
		
		neighbors_curr_and_prev = neighborsPrev(envA, envB, sB) + neighborsPrev(envA, envPrev, sB)
		# nearestSprite = findNearestSprite(sB, [item for sublist in envA._game.sprite_groups.values() for item in sublist])
		nearestSprite = findNearestSprite(sB, [item for sublist in envA._game.observation['trackedObjects'].values() for item in sublist])

		if nearestSprite.colorName in neighbors_curr_and_prev:
			e.intPairs.append((e.targetClass, nearestSprite.colorName))
		else:
			print "got new sprite class but nearest prev-step sprite isn't a current neighbor"
			embed()
		errorMap.append(e)

	# 3) Inventory change
	for t in matched_sprites:
		inventory_penalty = 0
		keys = list(set(t[0].inventory.keys()+t[1].inventory.keys()))
		for k in keys:
			t0_k = t[0].inventory[k] if k in t[0].inventory.keys() else (0,0)
			t1_k = t[1].inventory[k] if k in t[1].inventory.keys() else (0,0)
			inventory_penalty += abs(t0_k[0]-t1_k[0])

		if inventory_penalty > 0:
			e = errorMapEntry()
			e.diagnosis.append('inventoryChange')
			sA, sB = t[0], t[1]
			e.targetToken = sB
			e.targetClass = sA.colorName
			e.targetColor = sB.colorName
			sPrev, dist_ts = find_sPrev(sB, envB, envPrev)
			neighbors_prev = neighborsPrev(envB, envPrev, sPrev)
			e.intPairs.extend([(e.targetClass, n) for n in neighbors_prev])
			errorMap.append(e)

	# 4) Score change
	if envA._game.observation['score'] != envB._game.observation['score']:
		e = errorMapEntry()
		e.diagnosis.append('scoreChange')
		avatar_color = theory.classes['avatar'][0].colorName
		sA = envA._game.observation['trackedObjects'][avatar_color][0]
		sB = envB._game.observation['trackedObjects'][avatar_color][0]
		e.targetToken = sA
		e.targetClass = sA.colorName
		e.targetColor = sA.colorName
		sPrev, dist_ts = find_sPrev(sB, envB, envPrev)
		neighbors_prev = neighborsPrev(envB, envPrev, sPrev)
		e.intPairs.extend([(e.targetClass, n) for n in neighbors_prev])
		errorMap.append(e)

	## Share information across errorMap items and make a unique list
	if len(errorMap) > 1:
		diagnosis_class_pairs = list(set([(e.diagnosis[0], e.targetClass) for e in errorMap]))
		for dcp in diagnosis_class_pairs:
			int_pairs = [item for sublist in [e.intPairs for e in errorMap if e.diagnosis[0] == dcp[0] and e.targetClass == dcp[1]] for item in sublist]
			int_pairs = list(set(int_pairs))
			## give int_pairs to each matching errorMap item.
			for e in errorMap:
				if e.diagnosis[0] == dcp[0] and e.targetClass == dcp[1]:
					e.intPairs = int_pairs

		lst = [errorMap[0]]
		for e in errorMap[1:]:
			if [not(e.diagnosis == l.diagnosis and e.targetClass == l.targetClass and e.targetToken == l.targetToken) for l in lst]:
				lst.append(e)

		errorMap = lst

	## Sort so that you fix errors involving any new classes first when you build theories.
	errorMap = sorted(errorMap, key=lambda x: x.targetClass!='unknown')

	## convert color names in targetClass and intPairs to theory class names:
	for e in errorMap:
		if not e.targetClass in theory.spriteObjects.keys():
			print "target class unknown? in errorSignal"
			embed()
		e.targetClass = theory.spriteObjects[e.targetClass].className if e.targetClass in theory.spriteObjects.keys() else 'unknown'

		if e.intPairs:
			newIntPairs = []
			for pair in e.intPairs:
				p0 = theory.spriteObjects[pair[0]].className if pair[0] in theory.spriteObjects.keys() else 'unknown'
				p1 = theory.spriteObjects[pair[1]].className if pair[1] in theory.spriteObjects.keys() else 'unknown'
				pair = (p0, p1)
				newIntPairs.append(pair)
			e.intPairs = newIntPairs

	return total_penalty, errorMap

def neighborsPrev(envA, envPrev, sPrev):
	"""
	Function to find neighbors of target sprite in the previous time step
	Usually the arguments correspond to the following:
	envA: hypothetical environment, current step
	envPrev: real environment, previous step
	sPrev: target sprite in envPrev
	"""
	# Find potential interaction partners: neighboring sprites in previous step
	
	all_sprites = [item for sublist in envPrev._game.observation['trackedObjects'].values() for item in sublist]

	# Neighbors of problematic sprite in real world in previous time step
	# neighbors = [s for s in all_sprites if manhattanDist2(s, sPrev)<=np.sqrt(2) and s!=sPrev and (s not in envPrev._game.kill_list)]
	neighbors = [s for s in all_sprites if manhattanDist2(s, sPrev)<=np.sqrt(2) and s!=sPrev]

	# Determine corresponding classes in theory environment
	# neighbors_color = [s.colorName for s in neighbors]
	# neighbors_color = list(set(neighbors_color))
	# neighbors_theoClassNames = []
	# for color in neighbors_color:
	# 	for className in envA._game.observation['trackedObjects'].keys():
	# 		if envA._game.observation['trackedObjects'][className]!=[] and envA._game.observation['trackedObjects'][className][0].colorName == color:
	# 			neighbors_theoClassNames.append(className)
	# neighbors_theoClassNames = list(set(neighbors_theoClassNames)) #delete double entries

	neighbors = list(set([n.colorName for n in neighbors]))	
	return neighbors

def find_sPrev(sB, envB, envPrev):
	"""
	Find sprite in envPrev (previous environment) corresponding to a sprite in
	envB (current environment), and the distance that the sprite has traveled
	in the time step
	"""
	matched_ts, _, _ = matchEnvs(envB, envPrev) #matches real env across timestep
	dist_ts = [matched_ts[i][2] for i in range(len(matched_ts)) if matched_ts[i][0] == sB] #distance that sB has moved over timestep
	sPrev = [matched_ts[i][1] for i in range(len(matched_ts)) if matched_ts[i][0] == sB] #sB in previous step
	if sPrev == []:
		sPrev = None
		dist_ts = None
	else:
		sPrev = sPrev[0]
		dist_ts = dist_ts[0]
	return sPrev, dist_ts

def diagnosePosMismatch(sA, sB, sPrev, envA, envB, envPrev, dist_ts):
	"""
	Returns errorMapEntry object containing the position mismatch error
	"""

	# Step through sub-problems
	e = errorMapEntry()
	e.targetToken = sB
	e.targetClass = sA.colorName
	e.targetColor = sA.colorName

	errorMaps = [e]
	# Find neighbors of target sprite in the previous time step
	neighbors_prev = neighborsPrev(envA, envPrev, sPrev)

	# Write potential interaction pairs to error map entry
	for className in neighbors_prev:
		e.intPairs.append( (sA.colorName,className) )
	# Determine mininum distance to neighbors in current real env -> to distinguish unexpectedPosition and unexpectedOverlap
	all_sprites_envB = [item for sublist in envB._game.observation['trackedObjects'].values() for item in sublist]
	nearest_sprite = findNearestSprite(sB, [s for s in all_sprites_envB if (s!=sB)])

	nearest_dist = manhattanDist2(sB, nearest_sprite)
	# Determine orientation in current and previous step -> to detect orientation change
	try:
		oB = sB.orientation
		oPrev = sPrev.orientation
	except:
		oB,oPrev = None,None

	## Categorize into sub-problem-class
	# 1.1) noMovement
	if dist_ts == 0:
		e.diagnosis.append('noMovement')
		## Form all possible pairs of classes and propose these. This is because undoAll could cause this, so it's literally any classes combining.
		e.intPairs = list(itertools.combinations([k for k in envA._game.observation['trackedObjects'].keys() if 
			envA._game.observation['trackedObjects'][k]], 2))

		for k in envA._game.observation['trackedObjects'].keys():
			if len(envA._game.observation['trackedObjects'][k])>1:
				e.intPairs.append((k,k))

	# 1.2) orientationChange
	if dist_ts!=0 and oB!=None and oB!=oPrev:
		e.diagnosis.append('orientationChange')
	# 1.3) unexpectedPosition
	if dist_ts!=0 and nearest_dist>=1:
		e.diagnosis.append('unexpectedPosition')
	# 1.4) unexpectedOverlap
	if dist_ts!=0 and nearest_dist<1:

		e.diagnosis.append('unexpectedOverlap')
		# find sprite in envA that corresponds to covered sprite in envB
		color = nearest_sprite.colorName
		className_envA = ''
		for k in [key for key in envA._game.observation['trackedObjects'].keys() if envA._game.observation['trackedObjects'][key]]:
			if color == envA._game.observation['trackedObjects'][k][0].colorName:
				className_envA = k

		covered_sprite_envA = findNearestSprite(sB,envA._game.observation['trackedObjects'][className_envA])

		e.intPairs = [(sA.colorName, covered_sprite_envA.colorName)] #overwrite interaction pair by the overlapping sprite pair
	if dist_ts>2:
		e2 = errorMapEntry()
		e2.targetToken = e.targetToken
		e2.targetClass = e.targetClass
		e2.targetColor = e.targetColor
		e2.diagnosis.append('teleport')
		e2.intPairs = [(sA.colorName, n) for n in neighbors_prev]
		errorMaps.append(e2)
	# Return list of errorMapEntry objects
	return errorMaps


def matchEnvs(envA, envB, debug=False):
	'''
	Compares environment A to environment B, mapping sprites from A to sprites from B 1 to 1 (if it can)
	by comparing the positions of sprites in A to positions of sprites in B of the same color. 

	Returns mapping that minimizes distance between matching sprites (hopefully?)

	returns:

		the matched sprites as a list of tuples of sprites from A and sprites from B 
	and the manhatten distance between their positions: 
		[(s_A1, s_B1, d), (s_A2, s_A3, d), ...]

		the list of "lonely sprites" in A that don't map to any sprites in A: 
			[s_A5, s_A6, ..]

		the list of "lonely sprites" in B that don't map to any sprites in B: 
			[s_A7, s_A8, ..]


	'''
	## For classes that have more than enumeration_limit instances, default to greedy version.
	enumeration_limit = 10

	matched_sprites, lonely_sprites_envA, lonely_sprites_envB = [],[],[]

	color_groupsA = defaultdict(lambda : [])
	color_groupsB = defaultdict(lambda : [])
	colors = set()

	for name, sprites in envA._game.sprite_groups.iteritems():
		if sprites:
			color = sprites[0].colorName
			color_groupsA[color] = sprites
			colors.add(color)

	for name, sprites in envB._game.sprite_groups.iteritems():
		if sprites:
			color = sprites[0].colorName
			color_groupsB[color] = sprites
			colors.add(color)

	for color in colors:
		# Find matching sprites via color
		matchingSpritesInEnvA = [s for s in getObservedSpritesByColor(envA._game, color)]
		matchingSpritesInEnvB = [s for s in getObservedSpritesByColor(envB._game, color)]

		## If it is manageable to enumerate all possible pairings
		if len(matchingSpritesInEnvA)<enumeration_limit:
			while len(matchingSpritesInEnvA)<len(matchingSpritesInEnvB):
				matchingSpritesInEnvA.append(None)
			while len(matchingSpritesInEnvB)<len(matchingSpritesInEnvA):
				matchingSpritesInEnvB.append(None)

			assignment_options = []
			for p in itertools.permutations(matchingSpritesInEnvA):
				assignment_options.append(zip(p, matchingSpritesInEnvB))

			min_sum = 1e6
			best_assignments = None
			for assignments in assignment_options:
				curr_sum = sum([manhattanDist2(p[0], p[1])**2 for p in assignments if None not in p])
				if curr_sum<min_sum:
					min_sum = curr_sum
					best_assignments = assignments
			
			for pair in best_assignments:
				if None not in pair:
					matched_sprites.append((pair[0], pair[1], manhattanDist2(pair[0], pair[1])))
				if pair[1] is None:
					lonely_sprites_envA.append(pair[0])
				if pair[0] is None:
					lonely_sprites_envB.append(pair[1])
		else:	
		## Otherwise default to a greedy version
			to_remove = []
			for sA in matchingSpritesInEnvA:
				for sB in matchingSpritesInEnvB:
					if manhattanDist2(sA, sB) == 0:
						matched_sprites.append((sA, sB, 0.0))
						matchingSpritesInEnvB.remove(sB)
						to_remove.append(sA)
						break

	return matched_sprites, lonely_sprites_envA, lonely_sprites_envB



########################################################################
######## EXPERIENCE REPLAY 										########
########################################################################


def subSampleStates(subsamplePercentage, actionsPerIndex, rleHistory):
	## Returns a random subsample of inidces in the rleHistory to test,
	## as well as how many actions per index to test

	## Note to self: it may happen that you sample: 
	## indices = [0,2,10], actionsPerIndex=5, 
	## in which case you'll double-penalize states 2,3,4.

	numStatesToSample = int(math.ceil(subsamplePercentage*len(rleHistory)))
	indices = list(np.random.choice(len(rleHistory)-1, numStatesToSample, replace=False))
	actionsPerIndex = actionsPerIndex

	return indices, actionsPerIndex

def getSalientStates(rleHistory):
	## make sure you don't sample the last state
	## get actionsPerIndex
	pass

def experienceReplayProfiler(hypotheses, rleHistory, actionHistory, symbolDict, best_params, method='all', displayStates=False):
	lp = LineProfiler()
	lp_wrapper = lp(experienceReplay)
	mean_penalties, cumulative_penalties = lp_wrapper(hypotheses, rleHistory, actionHistory, symbolDict, best_params, method, displayStates)
	lp.print_stats()
	return mean_penalties, cumulative_penalties

def singleTheoryExperienceReplayProfiler(rleHistory, actionHistory, method, targetColor, displayStates, hypotheses, symbolDict, best_params):
	lp = LineProfiler()
	lp_wrapper = lp(singleTheoryExperienceReplay)
	mean_penalties, cumulative_penalties, theoryRLEs= lp_wrapper(rleHistory, actionHistory, method, targetColor, displayStates, hypotheses, symbolDict, best_params)
	lp.print_stats()
	return mean_penalties, cumulative_penalties, theoryRLEs

def singleTheoryExperienceReplay(rleHistory, actionHistory, method, targetColor, displayStates, hypotheses, symbolDict, best_params):

	subsamplePercentage = .2
	actionsPerIndex = 2

	if method == 'newMethod':
		indices = range(len(rleHistory))
		actionsPerIndex = 1
	elif method == 'all':
		indices = [0]
		actionsPerIndex = len(actionHistory)
	elif method == 'screenLastStep':# and len(rleHistory)>=2:
		## Can't screen last step with fewer than two RLEs in history.
		if len(rleHistory)<2:
			actionsPerIndex = 0
			indices = [0]
			print "got screenLastStep on short sequence"
		else:
			indices = [-2]
			actionsPerIndex = 1
	elif method == 'subsample':
		indices, actionsPerIndex = subSampleStates(subsamplePercentage, actionsPerIndex, rleHistory)
	elif method == 'salient':
		indices, actionsPerIndex = getSalientStates(subsamplePercentage, actionsPerIndex, rleHistory)

	cumulative_penalties = []

	for idx in indices:
		## 1. set imagined states to historical states  2. match IDs between real and theory RLEs
		t1 = time.time()
		theoryRLEs = VrleInitPhase(hypotheses, rleHistory[idx], symbolDict, best_params)
		## Take a predetermined number of actions starting from idx
		end = min(idx+actionsPerIndex, len(actionHistory))

		if displayStates:
			print "index: {}".format(idx)
			print rleHistory[idx].show()
			for env in theoryRLEs:
				print env.show(color='blue')

		for n, action in enumerate(actionHistory[idx:end]):
			penalties = []
			if displayStates:
				print action
				print rleHistory[idx+n+1].show(color='green')
			for num, env in enumerate(theoryRLEs):                      

				if env is not None:
					env.step(action)
				try:
					penalty, errorList = errorSignal(env, rleHistory[idx+n+1], hypotheses[num], 
						rleHistory[idx+n], targetColor=targetColor, penalty_only=True)
					penalties.append(penalty)

				except:
					print "in experienceReplay"
					embed()
				if displayStates:
					print penalty
					print env.show(color='blue')
				
			cumulative_penalties.append(penalties)
	
	if not cumulative_penalties:
		print "Warning: did not run experience replay."
		cumulative_penalties = [[0]*len(hypotheses)]

	cumulative_penalties = np.array(cumulative_penalties)
	mean_penalties = np.mean(cumulative_penalties, axis=0)
	return mean_penalties, cumulative_penalties, theoryRLEs

def experienceReplay(hypotheses, rleHistory, actionHistory, symbolDict, best_params, method='all', targetColor=None, displayStates=False, displayTheories=False):
	if len(hypotheses)>10:
		print "Running experience replay on {} theories and {} time-steps".format(len(hypotheses), len(rleHistory))

	t1 = time.time()
	results = []
	for num, h in enumerate(hypotheses):
		if displayTheories:
			print "running experienceReplay on {}:".format(num)
			h.display()
		if method == 'newMethod':
			multipleHypotheses = [h]*num_samples_per_hypothesis
			results.append(singleTheoryExperienceReplay(rleHistory, actionHistory, method, targetColor, displayStates, multipleHypotheses, symbolDict, best_params))
		else:
			results.append(singleTheoryExperienceReplay(rleHistory, actionHistory, method, targetColor, displayStates, [h], symbolDict, best_params))

	if len(hypotheses)>10:
		print "Serial experience replay on {} theories and {} time-steps took {} seconds".format(len(hypotheses), len(rleHistory), time.time()-t1)

	mean_penalties = [r[0][0] for r in results]
	cumulative_penalties = [r[1][0][0] for r in results]
	theoryRLEs = [r[2][0] for r in results]

	return mean_penalties, cumulative_penalties, theoryRLEs

########################################################################
######## THEORY MODIFICATION 									########
########################################################################

def updateTerminations(rle, hypotheses):

	terminationSet, falsified, multi_falsified = hypotheses[0].updateTerminations(rle)

	for h in hypotheses:
		h.terminationSet = terminationSet
		h.falsified = falsified
		h.multi_falsified = multi_falsified

	return
	
def filterTheories(scoreAndTheoryTuples, percentile, max_num, proportionOfSpriteTheories):
	## Returns the max_num theories that are at percentile or greater, given their score.

	percentile = 100.-percentile
	scoreAndTheoryTuples = sorted(scoreAndTheoryTuples, key=lambda x: x[0])
	cutoff = np.percentile([s[0] for s in scoreAndTheoryTuples], percentile)
	candidates = [s for s in scoreAndTheoryTuples if s[0]<=cutoff]

	if max_num is None:
		max_num = len(candidates)+1
	if proportionOfSpriteTheories is None:
		candidates = sorted(candidates, key=lambda x:x[0])
		return candidates[0:max_num]

	sprite_candidates = [s for s in candidates if s[1].mostRecentEdit == 'spriteInduction']
	induction_candidates = [s for s in candidates if s[1].mostRecentEdit == 'interactionSetInduction']
	no_edit_candidates = [s for s in candidates if s[1].mostRecentEdit == 'none']
	if len(sprite_candidates)>int(math.floor(max_num*proportionOfSpriteTheories)):
		num_sprite_candidates_chosen = min(int(math.floor(max_num*proportionOfSpriteTheories)), len(sprite_candidates))
		filtered = sprite_candidates[0:num_sprite_candidates_chosen]
	else:
		num_sprite_candidates_chosen = len(sprite_candidates)
		filtered = sprite_candidates

	remaining = max_num - len(filtered)
	filtered = induction_candidates[0:min(remaining, len(induction_candidates))] + filtered + no_edit_candidates

	if len(filtered)<max_num:
		diff = max_num - len(filtered)
		filtered = filtered + sprite_candidates[num_sprite_candidates_chosen:min(len(sprite_candidates), num_sprite_candidates_chosen+diff)]
	filtered = sorted(filtered, key=lambda x: x[0])

	return filtered

def expandTheories(theories, errorList, envRealPrev, envRealCurrent, prevAction, rleHistory, actionHistory, symbolDict, best_params, bestSpriteTypeDict):
	# print "In expandTheories. errorList length: {}. Theories length {}".format(len(errorList), len(theories))

	# MEMOIZE!
	# lookup table (dict) which maps (classPair, predicateTuple) to all combinations of all possible rules involving those classes and predicates
	classPairPlusPredicateToRuleSets = dict()

	# print 'top of expandTheories'
	# embed()

	for errorMap in errorList:
		## Skip this whole step if you've already made changes for this theory. Just pass it on and you'll
		## evaluate it on the whole dataset in the outer loop.
		if len(theories) == 1 and any([errorMap == e for e in theories[0].errorMapHistory]):
			newTheories = [theories[0]]
			theories = newTheories
			continue

		print "In base case. Correcting error for {} for {} theories".format(errorMap.targetClass, len(theories))
		t1 = time.time()
		newTheories = []
		for theory in theories:
			newTheories.extend(expandTheoryForOneErrorMap(errorMap, envRealPrev, envRealCurrent, prevAction, rleHistory, actionHistory, 
					theory, bestSpriteTypeDict, classPairPlusPredicateToRuleSets))
		print "Expanding {} theories took {} seconds".format(len(theories), time.time()-t1)

		t1 = time.time()
		newTheories = list(set(newTheories))

		penalties, cumulative_penalties, _ = experienceReplay(newTheories, rleHistory[-2:], actionHistory[-1:], 
			symbolDict, best_params, method='all', targetColor = errorMap.targetColor)

		scoreAndTheoryTuples = zip(penalties, newTheories)
		scoreAndTheoryTuples = sorted(scoreAndTheoryTuples, key=lambda x: x[0])

		scoresAndHypotheses = [(h[0],h[1]) for h in filterTheories(scoreAndTheoryTuples, percentile=0, max_num=None,
				proportionOfSpriteTheories=None)]

		newTheories = [s[1] for s in scoresAndHypotheses]

		theories = newTheories

	# if any(['conditionalKill' in e.diagnosis for e in errorList]):
	# print 'bottom of expandTheories'
	# embed()

	return theories

def expandTheoryForOneErrorMap(errorMap, envRealPrev, envRealCurrent, action, rleHistory, actionHistory, theory, bestSpriteTypeDict, classPairPlusPredicateToRuleSets):

	## Fixes the problems generated by a single errorMap entry.

	n = 1 # n is the number of allowed rules for a particular classpair-ordering, probably (TODO)

	## If we were about to make modifications we've made already, don't waste the time.
	if any([errorMap == e for e in theory.errorMapHistory]):
		newTheories = [theory]
		return newTheories

	theory.errorMapHistory.append(errorMap)

	newTheories = []

	## For debugging. Don't make children of the true theory.
	if hasattr(theory, 'trueTheory'):
		newTheories = [theory]
		return newTheories

	## If there are unknown colors in an inventory, add them to the theory here.
	if 'inventoryChange' in errorMap.diagnosis:
		from vgdl.ontology import Resource
		for k in errorMap.targetToken.inventory:
			if k not in theory.spriteObjects.keys():
				color = k
				existing_classes = [key for key in theory.classes if key[0] == 'c']
				max_num = max([int(c[1:]) for c in existing_classes])
				class_num = max_num+1
				newClassName = 'c'+str(class_num)
				theory.addSpriteToTheory(newClassName, color, vgdlType=Resource, args={'limit':errorMap.targetToken.inventory[k][1]})
			else:
				theory.spriteObjects[k].vgdlType = Resource
				if theory.spriteObjects[k].args:
					theory.spriteObjects[k].args['limit'] = errorMap.targetToken.inventory[k][1]
				else:
					theory.spriteObjects[k].args = {'limit':errorMap.targetToken.inventory[k][1]}

	## If there are unknown colors on screen, add them to the theory here.
	if errorMap.targetClass not in theory.classes.keys():
		if errorMap.targetColor in theory.spriteObjects:
			errorMap.targetClass = theory.spriteObjects[errorMap.targetColor].className
		else:
			existing_classes = [key for key in theory.classes if key[0] == 'c']
			max_num = max([int(c[1:]) for c in existing_classes])
			class_num = max_num+1 
			errorMap.targetClass = 'c'+str(class_num)
			print "Got unknown targetclass for {}. Added generic sprite to spriteSet and interactionSet".format(errorMap.targetToken.colorName)
			theory.addSpriteToTheory(errorMap.targetClass, errorMap.targetToken.colorName)
			## Now get overlapping/nearby classes and reassign the target class to the shooter/spawnpoint/etc. 
			## the next step will take care of not doing inference on these if we've done it already.
			## NOTE: errorMap takes a unique targe class, and there are cases where you might have multiple singleton neighbors.
			## For now you're taking just a random choice between those.
			neighbors = neighborsPrev(envRealCurrent, envRealCurrent, errorMap.targetToken)
			options = [item for sublist in [envRealCurrent._game.observation['trackedObjects'][k] for k in neighbors if 
				len(envRealCurrent._game.observation['trackedObjects'][k]) == 1] for item in sublist]

			if len(options)>1:
				print "Warning: More than one singleton neighbor of a newly-spawned sprite. Randomly picking one as agent"
			try:
				overlapping_item = random.choice(options)
			except:
				print "overlapping_item problem in expandtheory"
				embed()

			errorMap.targetToken = overlapping_item
			errorMap.targetClass = theory.spriteObjects[overlapping_item.colorName].className

			## Redo induction for this type, even if you've done it before.
			if errorMap.targetClass in theory.expandedSprites:
				theory.expandedSprites.remove(errorMap.targetClass)

		## Replace 'unknown' with new name in intPairs
		newPairs = []
		for num,pair in enumerate(errorMap.intPairs):
			newPair = tuple([p if p!='unknown' else errorMap.targetClass for p in list(pair)])
			newPairs.append(newPair)
		errorMap.intPairs = newPairs

		print "Got unknown targetclass for {}. Added generic sprite to spriteSet and interactionSet".format(errorMap.targetToken.colorName)
		theory.addSpriteToTheory(errorMap.targetClass, errorMap.targetToken.colorName)

		## now get overlapping/nearby classes and reassign the target class to the shooter/spawnpoint/etc. 
		## the next step will take care of not doing inference on these if we've done it already.
		## NOTE: errorMap takes a unique targe class, and there are cases where you might have multiple singleton neighbors.
		## For now you're taking just a random choice between those.
		neighbors = neighborsPrev(envRealCurrent, envRealCurrent, errorMap.targetToken)
		options = [item for sublist in [envRealCurrent._game.observation['trackedObjects'][k] for k in neighbors if 
			len(envRealCurrent._game.observation['trackedObjects'][k]) == 1] for item in sublist]

		if len(options)>1:
			print "Warning: More than one singleton neighbor of a newly-spawned sprite. Randomly picking one as agent"
		try:
			overlapping_item = random.choice(options)
		except:
			print "overlapping_item problem in expandTheoryForOneErrorMap"
			embed()
		# overlapping_item = [item for sublist in envRealCurrent._game.sprite_groups.values() for item in sublist if 
			# item.rect == errorMap.targetToken.rect and item.colorName!=errorMap.targetToken.colorName][0]
		errorMap.targetToken = overlapping_item
		errorMap.targetClass = theory.spriteObjects[overlapping_item.colorName].className

		## Redo induction for this type, even if you've done it before.
		if errorMap.targetClass in theory.expandedSprites:
			theory.expandedSprites.remove(errorMap.targetClass)

	## SpriteSet induction step
	if errorMap.targetClass not in theory.expandedSprites:
		## Potential bug: used to pass self.rle._game below.
		className, theories = expandSprites(envRealCurrent._game, theory, errorMap, 
			envRealPrev, envRealCurrent, bestSpriteTypeDict, action, percentile=20, max_num=30)
		newTheories.extend(theories)

	## InteractionSet induction step
	for targetClassPair in errorMap.intPairs:

		singleIntPairErrorMap = errorMap.copy()
		singleIntPairErrorMap.intPairs = [targetClassPair]
		## If we have non-generic rules for this pair in the theory, then this has to involve some kind of precondition
		matchingRules = [rule for rule in theory.interactionSet if (rule not in list(theory.dryingPaint)) and 
			( targetClassPair == (rule.slot1, rule.slot2) or targetClassPair == (rule.slot2, rule.slot1) )]

		# if ('objectDestruction' in errorMap.diagnosis
		# 			or any('objectDestruction' in e.diagnosis for e in theory.errorMapHistory) ) \
		# 		and any([not rule.generic for rule in matchingRules]):
		if any([not rule.generic for rule in matchingRules]):
			if ('objectDestruction' in singleIntPairErrorMap.diagnosis
						or any(['objectDestruction' in e.diagnosis for e in theory.errorMapHistory if e.targetClass in targetClassPair]) ):
				# print "*******inner one happened"
				# embed()
				pass
			singleIntPairErrorMap.diagnosis.append('conditionalKill')
			# print "*******non-generic rules for classPair"
			# embed()

		## Modify theory before the last step, then embed here to continue work
		## if the diagnosis involves objectDestruction and the targetClassPair has non-generic rules,
		## change the diagnosis here to conditionalKill such that you can propose preconditions in proposePredicates
		predicates = proposePredicates(singleIntPairErrorMap.diagnosis, envRealCurrent._game.observation)

		classPair, theories = expandLine(theory, singleIntPairErrorMap, targetClassPair, predicates,
			classPairPlusPredicateToRuleSets, envRealPrev, envRealCurrent, action, rleHistory, actionHistory, experienceReplay, n=n, 
			observations=envRealCurrent._game.observation, generic=False)

		# this is because it would cause us to propose conditional stuff for later targetClassPairs
		if 'conditionalKill' in singleIntPairErrorMap.diagnosis:
			singleIntPairErrorMap.diagnosis.remove('conditionalKill')

		newTheories = list(set(theories))
	if not newTheories:
		newTheories = [theory]
		theory.errorMapHistory.append(errorMap)

	return newTheories

def testAndExpand(theoryRLEs, hypotheses, action, envReal, envRealPrev, index, rleHistory, actionHistory, symbolDict, best_params, bestSpriteTypeDict):
	num = index
	env = theoryRLEs[num]
	hypothesis = hypotheses[num]

	env.step(action)
	penalty, errorList = errorSignal(env, envReal, hypothesis, envRealPrev)
	
	if errorList:
		# hypothesis.display()
		for e in errorList:
			e.display()
			print ""
		# embed()
	# else:
		# print "No error"
		# embed()
	# print "expanding theories"
	theories = expandTheories([hypothesis], errorList, envRealPrev, envReal, action, rleHistory, actionHistory, symbolDict, best_params, bestSpriteTypeDict)

	return theories







if __name__ == "__main__":

	##simpleGame_missile: no support for learning that it can shoot things.
	# filename = "examples.gridphysics.aliens"

	# filename = "examples.gridphysics.avatar_inference"
	filename = "examples.gridphysics.collect_resource"

	# filename = "examples.gridphysics.theorytest"
	# filename = "examples.continuousphysics.breakout_new"

	global WBP
	if 'grid' in filename:
		import WBP_grid as WBP
	else:
		import WBP_continuous as WBP

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

	# gvggames = ['aliens', 'boulderdash', 'butterflies', 'chase', 'frogs',  # 0-4
	#   'missilecommand', 'portals', 'sokoban', 'survivezombies', 'zelda']  # 5-9

	# gameName = gvggames[6]

	# gvgname = "../gvgai/training_set_1/{}".format(gameName)

	# gameString = read_gvgai_game('{}.txt'.format(gvgname))


	# level_game_pairs = []
	# for level_number in range(5):
	#   with open('{}_lvl{}.txt'.format(gvgname, level_number), 'r') as level:
	#       level_game_pairs.append([gameString, level.read()])

	##uncomment this line to run local games
	gameName = filename

	agent = Agent('full', gameName)

	##For GVGAI games, use this line
	# gameObject = None
	# agent.playCurriculum(level_game_pairs=level_game_pairs)

	##For local games, use this line
	# agent.playCurriculum(level_game_pairs=None)

	## For testing, use this line
	agent.testCurriculum(level_game_pairs=None)
