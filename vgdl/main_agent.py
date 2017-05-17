from IPython import embed
from util import *
from core import colorDict, VGDLParser, makeVideo, sys
from ontology import Immovable, Passive, Resource, ResourcePack, RandomNPC, Chaser, AStarChaser, \
OrientedSprite, Missile, initializeDistribution, updateDistribution, updateOptions, sampleFromDistribution, \
spriteInduction, selectObjectGoal
from theory_template import TimeStep, Precondition, InteractionRule, TerminationRule, TimeoutRule, \
SpriteCounterRule, MultiSpriteCounterRule, ruleCluster, Theory, Game, writeTheoryToTxt, generateSymbolDict
import WBP
import importlib
from metaplanner import translateEvents
from rlenvironmentnonstatic import createRLInputGame, createRLInputGameFromStrings, defInputGame, createMindEnv


class Agent:
	def __init__(self, gameFilename):
		self.gameFilename = gameFilename
		self.annealingFactor = 1
		self.hypotheses = []
		self.symbolDict = None
		self.finalEventList = []
		self.statesEncountered = []
		self.all_objects = {}
		self.initializeEnvironment()

	def initializeEnvironment(self):
		self.gameString, self.levelString = defInputGame(self.gameFilename, randomize=False)
		self.rleCreateFunc = lambda: createRLInputGameFromStrings(self.gameString, self.levelString)
		self.rle = self.rleCreateFunc()
		return

	def initializeVrle(self, hypothesis):
		## World in agent's head given 'hypothesis', including object goal
		gameString, levelString, symbolDict = writeTheoryToTxt(self.rle, hypothesis, self.symbolDict,\
				 "./examples/gridphysics/theorytest.py")
		Vrle = createMindEnv(gameString, levelString, output=True)
		# Vrle.immovables, Vrle.killerObjects = immovables, killerObjects
		return Vrle

	def VrleInitPhase(self):
		## Initialize multiple VRLEs, each corresponding to one hypothesis in self.hypotheses
		VRLEs = []
		print "in VrleInitPhase.", len(self.hypotheses), "hypotheses"
		for hypothesis in self.hypotheses:
			VRLEs.append(self.initializeVrle(hypothesis))
		return VRLEs

	def initializeHypotheses(self, allObjects, learnSprites=True):
		if learnSprites:
			self.observe(10)
			spriteTypeHypothesis = sampleFromDistribution(self.rle._game.spriteDistribution, allObjects)
			gameObject = Game(spriteInductionResult=spriteTypeHypothesis)
			initialTheory = gameObject.buildGenericTheory(spriteTypeHypothesis)
		else:
			gameObject = Game(self.gameString)
			initialTheory = gameObject.buildGenericTheory(spriteSample=False, vgdlSpriteParse = gameObject.vgdlSpriteParse)

		self.hypotheses = [initialTheory]

		## Old: Used to check for Vrle and initialize accordingly.
		## New: assumption is Vrle needs to be initialized only if there are no hypotheses, so doing it all in
		## one chunk.

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

	def observe(self, obsSteps):
		print "observing"
		for i in range(obsSteps):
			spriteInduction(self.rle._game, step=1)
			spriteInduction(self.rle._game, step=2)
			self.rle.step((0,0))
			spriteInduction(self.rle._game, step=3)
		return

	def playEpisode(self, gameObject):
		## Initialize external environment
		self.initializeEnvironment()

		self.all_objects= self.rle._game.getObjects()
		ended, won = self.rle._isDone()
		annealing = 1
		## Start storing encountered states.
		self.statesEncountered.append(self.rle._game.getFullState())
		
		## initialize theory if necessary.
		if len(self.hypotheses) == 0:
			gameObject = self.initializeHypotheses(self.all_objects, learnSprites=True)
			print "initializing hypotheses"
		else:
			gameObject = self.completeHypotheses(self.all_objects)
			print "had hypotheses -- completing them."

		while not ended:
			## initialize one or many VRLEs according to hypothesis-selection method
			theoryRLEs = self.VrleInitPhase()

			p = WBP.WBP(theoryRLEs[0], self.gameFilename, annealing)
			p.BFS()
			solution = p.solution
			# print "got solution"
			# embed()
			## add new objects? (line 310 of metaplanner)
			
			for action in solution:
				hypotheses, theory_change_flag = self.executeStep(action, self.hypotheses[0])
				if theory_change_flag:
					del self.hypotheses[0]
					self.hypotheses.extend(hypotheses)
					break
			annealing *= self.annealingFactor

		return

	def executeStep(self, action, hypothesis):

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
		print res['effectList']
		## Add newly-seen objects.
		current_objects = self.rle._game.getObjects()
		for k in current_objects.keys():
			if k not in self.all_objects.keys():
				self.all_objects[k] = current_objects[k]
				distributionInitSetup(self.rle._game, k)
				## prevent spriteInduction from trying to infer anything about newly-appeared sprites in this timestep.
				self.rle._game.ignoreList.append(k)

		self.statesEncountered.append(self.rle._game.getFullState())
		terminal = self.rle._isDone()[0]
		spriteInduction(self.rle._game, step=3)
		effects = translateEvents(res['effectList'], self.all_objects, self.rle)

		all_effects = [item for sublist in [e['effectList'] for e in self.finalEventList] for item in sublist]
		
		event = {'agentState': agentState, 'agentAction': action, 'effectList': effects, \
			'gameState': self.rle._game.getFullStateColorized(), 'rle': self.rle}
		if event['effectList']:
			self.finalEventList.append(event)

		print effects
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
			if len(hypotheses)>1:
				print "more than one hypothesis"
				embed()


		[t.updateTerminations() for t in self.hypotheses]
		hypotheses[0].display()
		
		print self.rle.show()

		return hypotheses, theory_change_flag



if __name__ == "__main__":
	filename = "examples.gridphysics.pick_apples"	
	agent = Agent(filename)
	
	##then pass this down for multiple episodes
	gameObject = None
	agent.playEpisode(gameObject)
	embed()

