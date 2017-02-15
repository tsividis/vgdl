
from mcts_pseudoreward_heuristic import *
from util import *
from core import colorDict, VGDLParser
from ontology import Immovable, Passive, Resource, ResourcePack, RandomNPC, Chaser, AStarChaser, OrientedSprite, Missile
from ontology import initializeDistribution, updateDistribution, updateOptions, sampleFromDistribution, spriteInduction, selectObjectGoal
from theory_template import TimeStep, Precondition, InteractionRule, TerminationRule, TimeoutRule, SpriteCounterRule, \
MultiSpriteCounterRule, ruleCluster, Theory, Game, writeTheoryToTxt, generateSymbolDict
import importlib
from rlenvironmentnonstatic import createRLInputGame


## Specify a game or a set of games
## number of episodes per game


## hypotheses to plans
## hypothesis to plan


## simplest explore/exploit strategy:
	## keep track of unknown objects and goal. touch everytning you don't know until you know the goal. get to goal.
##


## For now, only implementing version of agent that can deal with single goals.

class Agent:
	def __init__(self, gameFilename, plannerType):
		self.gameName = gameFilename[gameFilename.rfind('.')+1:] ## store just the game name
		self.hypotheses = []
		self.symbolDict = None
		self.knownColors = []
		self.goalColor = None
		self.finalEventList = []
		self.plannerType = plannerType
		self.initializeEnvironment(gameFilename)
	
	def initializeEnvironment(self, gameFilename):
		self.gameString, self.levelString = defInputGame(gameFilename)
		self.rleCreateFunc = lambda: createRLInputGame(gameFilename)
		rle = self.rleCreateFunc()
		avatarColor = colorDict[str(rle._game.sprite_groups['avatar'][0].color)]
		self.knownColors.append(avatarColor)
		return

	def initializeHypotheses(self, rle, allObjects):

		observe(rle, 5)
		spriteTypeHypothesis = sampleFromDistribution(rle._game.spriteDistribution, allObjects)
		gameObject = Game(spriteInductionResult=spriteTypeHypothesis)
		initialTheory = gameObject.buildGenericTheory(spriteTypeHypothesis)
		self.hypotheses = [initialTheory]

		## Old: Used to check for Vrle and initialize accordingly.
		## New: assumption is Vrle needs to be initialized only if there are no hypotheses, so doing it all in
		## one chunk.

		self.symbolDict = generateSymbolDict(rle)
		
		# ##TODO: You may not need to initialize the VRLE here.
		# game, level, immovables = writeTheoryToTxt(rle, self.hypotheses[0], self.symbolDict,\
		#  	"./examples/gridphysics/theorytest.py")

		# Vrle = createMindEnv(game, level, output=False)
		# Vrle.immovables = immovables

		return gameObject

	def getSpriteColor(self, sprite):
		return colorDict[str(sprite.color)]

	def getSpriteNameColor(self, spriteName, rle):
		return self.getSpriteColor(rle._game.sprite_groups[spriteName][0])

	def objectSelectionPhase(self, unknownColors, rle):
		## TODO: this is contingent on only one goal existing.
		
		## Select known goal if it's known, otherwise unkown object.
		if self.goalColor:
			key = [k for k in rle._game.sprite_groups.keys() if self.getSpriteNameColor(k, rle) == self.goalColor][0]
			objectGoal = rle._game.sprite_groups[key][0]
			actualGoal = objectGoal
			objectGoalLocation = rle._rect2posFlipCoords(actualGoal.rect)
			print "goal is known:", self.goalColor
			print ""
		else:
			try:
				objectGoal = selectObjectGoal(rle, unknownColors, method="random_then_nearest")
				objectGoalLocation = rle._rect2posFlipCoords(objectGoal.rect)
				print "object goal is", self.getSpriteColor(objectGoal), "at location", objectGoalLocation
				print ""
			except:
				print "no unknown objects and no goal? Embedding so you can debug."
				embed()

		return objectGoal, objectGoalLocation

	def initializeVrle(self, hypothesis, objectGoalLocation, rle):
		## World in agent's head given 'hypothesis', including object goal
		gameString, levelString, symbolDict, immovables = writeTheoryToTxt(rle, hypothesis, self.symbolDict,\
				 "./examples/gridphysics/theorytest.py", objectGoalLocation)

		print "Initializing mental theory *with* object goal"
		Vrle = createMindEnv(gameString, levelString, output=True)
		Vrle.immovables = immovables
		return Vrle

	def VrleInitPhase(self, objectGoalLocation, rle):
		## Initialize multiple VRLEs, each corresponding to one hypothesis in self.hypotheses
		VRLEs = []
		for hypothesis in self.hypotheses:
			VRLEs.append(self.initializeVrle(hypothesis, objectGoalLocation, rle))
		return VRLEs


	def playMultipleEpisodes(self, numEpisodes):
		
		tally, finalEventList, totalStatesEncountered = [], [], []

		gameObject = None
		for i in range(numEpisodes):
			gameObject, won, statesEncountered = self.playEpisode(gameObject, finalEventList)
			VGDLParser.playGame(self.gameString, self.levelString, statesEncountered, persist_movie=True, movie_dir="videos/"+self.gameName)
			totalStatesEncountered.append(statesEncountered)
			tally.append(won)
			print "Episode ended. Won:", won
		print "Won", sum(tally), "out of ", len(tally), "episodes."
		


		return


	def playEpisode(self, gameObject, finalEventList):

		## Initialize external environment
		rle = self.rleCreateFunc()
		allObjects= rle._game.getObjects()

		unknownColors = [colorDict[str(rle._game.sprite_groups[k][0].color)] for k in rle._game.sprite_groups.keys()]
		unknownColors = [c for c in unknownColors if c not in self.knownColors]

		print "Known colors:", self.knownColors

		ended, won = rle._isDone()
		totalStatesEncountered = [rle._game.getFullState()]

		## Start storing encountered states.

		while not ended:

			## initialize theory if necessary.
			if len(self.hypotheses) == 0:
				gameObject = self.initializeHypotheses(rle, allObjects)

			## select explore / exploit goal
			objectGoal, objectGoalLocation = self.objectSelectionPhase(unknownColors, rle)

			## initialize one or many VRLEs according to hypothesis-selection method
			VRLEs = self.VrleInitPhase(objectGoalLocation, rle)

			## get to that goal

				## VRLEs, hypothesis-selection-method .....
				## figures out plan determined as above
				## carries out plan.

			rle, self.hypotheses, finalEventList, candidateNewColors, statesEncountered, gameObject = \
				getToObjectGoal(rle, VRLEs[0], self.plannerType, gameObject, self.hypotheses[0], self.gameString, self.levelString, \
					objectGoal, allObjects, finalEventList, symbolDict=self.symbolDict)
			totalStatesEncountered.extend(statesEncountered)
			ended, won = rle._isDone()


			if won:
				self.goalColor = finalEventList[-1]['effectList'][0][1]

			## update knowns/unknowns
			for col in candidateNewColors:
				if col not in self.knownColors:
					self.knownColors.append(col)

		return gameObject, won, totalStatesEncountered

if __name__ == "__main__":
	
	filename = "examples.gridphysics.simpleGame4_huge"
	plannerType = "QLearning"
	agent = Agent(filename, plannerType)
	agent.playMultipleEpisodes(10)


