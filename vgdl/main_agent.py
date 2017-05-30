from IPython import embed
from util import *
from core import colorDict, VGDLParser, sys
from ontology import Immovable, Passive, Resource, ResourcePack, RandomNPC, Chaser, AStarChaser, \
OrientedSprite, Missile, initializeDistribution, updateDistribution, updateOptions, sampleFromDistribution, \
spriteInduction, selectObjectGoal, distributionInitSetup
from theory_template import TimeStep, Precondition, InteractionRule, TerminationRule, TimeoutRule, \
SpriteCounterRule, MultiSpriteCounterRule, ruleCluster, Theory, Game, writeTheoryToTxt, generateSymbolDict, \
generateTheoryFromGame
import WBP
import importlib
import numpy as np
import ipdb
import copy
from metaplanner import translateEvents, observe
from rlenvironmentnonstatic import createRLInputGame, createRLInputGameFromStrings, defInputGame, createMindEnv


class Agent:
	def __init__(self, modelType, gameFilename):
		self.modelType = modelType
		self.gameFilename = gameFilename
		self.gameString = None
		self.levelString = None
		self.annealingFactor = .9
		self.max_nodes = 1000
		self.hypotheses = []
		self.symbolDict = None
		self.finalEventList = []
		self.statesEncountered = []
		self.fakeInteractionRules = []
		self.all_objects = {}
		self.seen_resources = []

	def initializeEnvironment(self):
		if self.gameString==None or self.levelString==None:
			self.gameString, self.levelString = defInputGame(self.gameFilename, randomize=False)
		self.rleCreateFunc = lambda: createRLInputGameFromStrings(self.gameString, self.levelString)
		self.rle = self.rleCreateFunc()
		return

	def initializeVrle(self, hypothesis):
		## World in agent's head given 'hypothesis', including object goal
		gameString, levelString, symbolDict = writeTheoryToTxt(self.rle, hypothesis, self.symbolDict,\
				 "./examples/gridphysics/theorytest.py")
		Vrle = createMindEnv(gameString, levelString, output=False)
		Vrle._game.getAvatars()[0].resources = copy.deepcopy(self.rle._game.getAvatars()[0].resources)
		# embed()
		# Vrle.immovables, Vrle.killerObjects = immovables, killerObjects
		return Vrle

	def VrleInitPhase(self):
		## Initialize multiple VRLEs, each corresponding to one hypothesis in self.hypotheses
		VRLEs = []
		# print "in VrleInitPhase.", len(self.hypotheses), "hypotheses"
		for hypothesis in self.hypotheses:
			tempHypothesis = copy.deepcopy(hypothesis)
			tmpFakeInteractionRules = copy.deepcopy(self.fakeInteractionRules)
			tempHypothesis.interactionSet.extend(tmpFakeInteractionRules)
			tempHypothesis.updateTerminations()
			# print "fake hypotheses"
			# if self.fakeInteractionRules:
				# tempHypothesis.display()
			VRLEs.append(self.initializeVrle(tempHypothesis))
		return VRLEs

	def initializeHypotheses(self, allObjects, learnSprites=True):
		if learnSprites:
			observe(self.rle, 10)
			spriteTypeHypothesis = sampleFromDistribution(self.rle._game.spriteDistribution, allObjects)
			gameObject = Game(spriteInductionResult=spriteTypeHypothesis)
			initialTheory = gameObject.buildGenericTheory(spriteTypeHypothesis)
		else:
			gameObject = Game(self.gameString)
			initialTheory = gameObject.buildGenericTheory(spriteSample=False, vgdlSpriteParse = gameObject.vgdlSpriteParse)

		self.hypotheses = [initialTheory]

		self.symbolDict = generateSymbolDict(self.rle)

		return gameObject

	def completeHypotheses(self, allObjects):
		observe(self.rle, 10)
		spriteTypeHypothesis = sampleFromDistribution(self.rle._game.spriteDistribution, allObjects)
		gameObject = Game(spriteInductionResult=spriteTypeHypothesis)
		newHypotheses = []
		for hypothesis in self.hypotheses:
			newHypotheses.append(gameObject.addNewObjectsToTheory(hypothesis, spriteTypeHypothesis))
		self.hypotheses = newHypotheses


	def playCurriculum(self):
		""" Plays a game level until it wins, then moves to the next one until
		completion. """
		level_game_pairs = importlib.import_module(self.gameFilename).level_game_pairs
		episodes = []
		for n_level, level_game in enumerate(level_game_pairs):
			print("Playing level {}".format(n_level))
			(self.gameString, self.levelString) = level_game
			win = False
			gameObject = None
			while not win:
				gameObject, win, score, steps, statesEncountered = self.playEpisode(gameObject)
				episodes.append((n_level, steps, win, score))

			VGDLParser.playGame(self.gameString, self.levelString, statesEncountered,
			persist_movie=True, make_images=True, make_movie=False, movie_dir="videos/"+self.gameFilename, padding=10)

		output = {'modelType':self.modelType,
					'gameName': self.gameFilename[self.gameFilename.find('expt'):],
					'condition': 'no_score',
					'episodes' : episodes}
					
		write_to_csv('pilotModelRuns.csv', output)
		makeMovie()

	def makeMovie(self):
		import os, subprocess, shutil
		print "Creating Movie"
		movie_dir = "videos/"+self.gameFilename

		if not os.path.exists(movie_dir):
			print movie_dir, "didn't exist. making new dir"
			os.makedirs(movie_dir)
		round_index = len([d for d in os.listdir(movie_dir) if d != '.DS_Store'])
		video_dirname = movie_dir+"/round"+str(round_index)+".mp4"
		images_dir = "images/tmp/%09d.png"
		com = "ffmpeg -i " +images_dir+ " -pix_fmt yuv420p -filter:v 'setpts=4.0*PTS' "+ video_dirname
		command = "{}".format(com)
		subprocess.call(command, shell=True)
		# empty image directory
		shutil.rmtree("images/tmp")
		os.makedirs("images/tmp")
		return

	def playMultipleEpisodes(self, num_episodes):
		i=0
		gameObject = None
		wins, scores = [], []
		while i<num_episodes:
			gameObject, win, score, statesEncountered = self.playEpisode(gameObject)
			wins.append(win)
			scores.append(score)
			i+=1
		VGDLParser.playGame(self.gameString, self.levelString, self.statesEncountered, \
			persist_movie=True, make_images=True, make_movie=True, movie_dir="videos/"+self.gameFilename, padding=10)
		print "Won {} out of {} episodes.".format(sum(wins), i)

	def playEpisode(self, gameObject):

		## Initialize external environment
		self.initializeEnvironment()
		print "initializing RLE"
		steps = 0
		self.all_objects= self.rle._game.getObjects()
		ended, win = self.rle._isDone()
		annealing = 1
		## Start storing encountered states.
		statesEncountered = [self.rle._game.getFullState()]
		self.statesEncountered.append(self.rle._game.getFullState())

		## initialize theory if necessary.
		if len(self.hypotheses) == 0:
			gameObject = self.initializeHypotheses(self.all_objects, learnSprites=True)
			print "initializing hypotheses"
		else:
			gameObject = self.completeHypotheses(self.all_objects)
			print "had hypotheses -- completing them."
			# If theory is being carried over, falsify termination hypotheses
			# given new level state
			[t.updateTerminations(rle=self.rle) for t in self.hypotheses]

		while not ended:
			## initialize one or many VRLEs according to hypothesis-selection method
			theoryRLEs = self.VrleInitPhase()

			p = WBP.WBP(theoryRLEs[0], self.gameFilename,
						theory=self.hypotheses[0], fakeInteractionRules = self.fakeInteractionRules, annealing=annealing, max_nodes=self.max_nodes)
			p.BFS()
			solution = p.solution
			quitting = p.quitting
			gameString_array = p.gameString_array
			# print "got solution"
			# embed()
			## add new objects? (line 310 of metaplanner)

			if not quitting:
				for i, action in enumerate(solution):
					self.hypotheses[0].dryingPaint = set()
					hypotheses, theory_change_flag = self.executeStep(action, self.hypotheses[0], statesEncountered)
					print len(statesEncountered)
					steps +=1
					if theory_change_flag:
						del self.hypotheses[0]
						self.hypotheses = hypotheses
						# self.hypotheses.extend(hypotheses)
						break
					ended, win = self.rle._isDone()
					if ended:
						break

					# Check for disparities between plan and reality
					# (e.g. stochastic effects)
					if self.rle._game.is_stochastic and i>20:
						try:
							if any(np.where(list(gameString_array[i+1]))[0] !=
								   np.where(list(self.rle.show()))[0]):
								break
						except:
							# Mismatch in gamestring lengths
							break
				# [rule.display() for rule in self.fakeInteractionRules]
			else:
				self.max_nodes *= 2
				return gameObject, False, self.rle._game.score, steps, statesEncountered

			# self.hypotheses[0].display()
			annealing *= self.annealingFactor
			ended, win = self.rle._isDone()
		score = self.rle._game.score
		print "ended episode. Win={}".format(win)
		return gameObject, win, score, steps, statesEncountered

	def matchEventToRuleByIDAndSpriteName(self, event, rule):
		# Check if the two objects involved in the
		# event are the same as those in the novelty
		# termination rule (invariant by order)
		hypSlot1 = self.hypotheses[0].spriteObjects[event[1]].className
		hypSlot2 = self.hypotheses[0].spriteObjects[event[2]].className
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

	def executeStep(self, action, hypothesis, statesEncountered):

		hypotheses = [hypothesis]
		theory_change_flag = False

		## returns rle in next state, updated hypothesis,
		spriteInduction(self.rle._game, step=1)
		spriteInduction(self.rle._game, step=2)

		try:
			agentState = dict(self.rle._game.getAvatars()[0].resources)
			self.rle.agentStatePrev = agentState
		# If agent is killed before we get agentState
		except Exception as e:
			agentState = self.rle.agentStatePrev
			print "didn't find agentState resources"
			embed()

		res = self.rle.step(action)

		## Add newly-seen objects.
		current_objects = self.rle._game.getObjects()
		for k in current_objects.keys():
			if k not in self.all_objects.keys():
				self.all_objects[k] = current_objects[k]
				distributionInitSetup(self.rle._game, k)
				## prevent spriteInduction from trying to infer anything about newly-appeared sprites in this timestep.
				self.rle._game.ignoreList.append(k)

		statesEncountered.append(self.rle._game.getFullState())
		self.statesEncountered.append(self.rle._game.getFullState())
		terminal = self.rle._isDone()[0]
		spriteInduction(self.rle._game, step=3)
		effects = translateEvents(res['effectList'], self.all_objects, self.rle)

		all_effects = [item for sublist in [e['effectList'] for e in self.finalEventList] for item in sublist]

		event = {'agentState': agentState, 'agentAction': action, 'effectList': effects, \
			'gameState': self.rle._game.getFullStateColorized(), 'rle': self.rle}
		if event['effectList']:
			self.finalEventList.append(event)

		if event['effectList']:
			## Delete fake interaction rules for events that were witnessed in this time step.
			oldFakeInteractionRules = copy.deepcopy(self.fakeInteractionRules)
			self.fakeInteractionRules = [r for r in self.fakeInteractionRules if
				not any([self.matchEventToRuleByIDAndSpriteName(e, r) for e in event['effectList']])]

			# if len(self.fakeInteractionRules)<len(oldFakeInteractionRules):
				# import ipdb; ipdb.set_trace()
			# print "before changing fakeInteractionRules"
			# embed()

			if not all([e in all_effects for e in effects]):
				theory_change_flag = True
			sample = sampleFromDistribution(self.rle._game.spriteDistribution, self.all_objects)
			game_object = Game(spriteInductionResult=sample)
			terminationCondition = {'ended': False, 'win':False, 'time':self.rle._game.time}
			trace = ([TimeStep(e['agentAction'], e['agentState'], e['effectList'], e['gameState'], e['rle']) \
				for e in self.finalEventList], terminationCondition)
			# embed()
			hypotheses = list(game_object.runInduction(game_object.spriteInductionResult, trace, 20, \
			verbose=False, existingTheories=hypotheses)) ##if you resample or run sprite induction, this
			# if len(hypotheses)>1:
			# 	print "more than one hypothesis"
			# 	embed()
			if ('stepBack' in e for e in event['effectList']):
				hypotheses[0].display()

			#  PRECONDITIONS HANDLING
			# Current assumptions:
		 	# - Only one resource can change for each timestep
			# - The first time a resource changes, it goes from 0 to a positive
			#   value
			for change_resource in [e[3] for e in event['effectList'] if 'changeResource' in e]:
				resource = change_resource['resource']
				val = change_resource['value']
				# print "adding fake rules"
				# import ipdb; ipdb.set_trace()
				if resource not in self.seen_resources and val>0:
					self.fakeInteractionRules.extend(hypotheses[0].updateInteractionsPreconditions(resource))
					self.fakeInteractionRules = list(set(self.fakeInteractionRules))
					# Add resource change to seen_resources list
					self.seen_resources.append(resource)


		if event['effectList']:
			[t.updateTerminations(event=event) for t in hypotheses]
			if theory_change_flag:
				hypotheses[0].display()



		print self.rle.show()

		return hypotheses, theory_change_flag


if __name__ == "__main__":

	##simpleGame_missile: no support for learning that it can shoot things.
	# filename = "examples.gridphysics.demo_helper"

	# filename = "examples.gridphysics.pick_apples_with_missiles"
	# filename = "examples.gridphysics.demo_transform_relational"
	# filename = "examples.gridphysics.simpleGame_push_boulders"
	# filename = "examples.gridphysics.pick_apples"
	# filename = "examples.gridphysics.expt_exploration_exploitation"

	filename = "examples.gridphysics.expt_relational"

	agent = Agent('full', filename)

	##then pass this down for multiple episodes
	gameObject = None
	agent.playCurriculum()
