
from mcts_pseudoreward_heuristic import *
from util import *
from core import colorDict
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


class Agent:
	def __init__(self, gameFilename):
		self.hypotheses = None
		self.unknownColors = None
		self.goalColor = None
		self.finalEventList = []

		self.initializeEnvironment()
	
	def initializeEnvironment(self, gameFilename):
		self.gameString, self.levelString = defInputGame(gameFilename)
		self.rleCreateFunc = lambda: createRLInputGame(gameFilename)
		return

	def playMultipleEpisodes(self, numEpisodes):
		
		tally = []

		for i in range(numEpisodes):
			score, trace = self.playEpisode()
			tally.append(score)
			print "Episode ended. Score:", score
		print "Won", sum(tally), "out of ", len(tally), "episodes."

		return

	def playEpisode(self):
		rle = self.rleCreateFunc() ## Initialize external environment
		
		return score, trace


