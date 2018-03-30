import unittest

from IPython import embed

from vgdl.agent import Agent, VrleInitPhase, sampleFromDistribution
from vgdl.theory_template import Game, generateTheoryFromGame
from pygame.locals import *
from vgdl.ontology import *

# imports all the game files created in games to the global namespace
from tests.games import *
from tests.theory_tools import *

FILENAME = 'tests.game.simple'

class TestAgent(unittest.TestCase):

	def setUp(self):
		self.agent = Agent('full', FILENAME)

	def tearDown(self):
		pass

	########################################
	# Initialization
	def initializeEnvironment(self, game_string=None, level_string=None):
		self.agent.gameString = game_string
		self.agent.levelString = level_string
		self.agent.initializeEnvironment()

	def initializeCurriculum(self, num_episodes):
		self.agent.rleHistory = [[] for i in range(num_episodes)]
		self.agent.actionHistory = [[] for i in range(num_episodes)]
		self.agent.all_objects = [{} for i in range(num_episodes)]

	def initializeEpisode(self, episode_num):
		'''Sets up episode'''
		self.agent.all_objects[episode_num] = self.agent.rle._game.getObjects()
		if not self.agent.hypotheses:
			self.agent.initializeHypotheses(self.agent.all_objects[episode_num])
		envReal = self.agent.fastcopy(self.agent.rle)
		self.agent.rleHistory[episode_num].append(envReal)

	def initialize(self, game_string, level_string, action_sequences):
		'''Sets up environment, curriculum, and episode'''
		num_episodes = len(action_sequences)
		self.initializeEnvironment(game_string, level_string)
		self.initializeCurriculum(num_episodes)
		self.initializeEpisode(0)

	#######################################
	# Agent Theory Tools
	def sampleFromDistribution(self, all_objects):
		game = self.agent.rle._game
		return sampleFromDistribution(game, game.spriteDistribution, all_objects, 
			game.spriteUpdateDict, self.agent.bestSpriteTypeDict, 
			oldSpriteSet=None, mode='default', learnAvatar=True)

	def buildGenericTheory(self, all_objects):
		spriteTypeHypothesis, _, _, _ = self.sampleFromDistribution(all_objects)
		game_object = Game(spriteInductionResult=spriteTypeHypothesis)
		theory = game_object.buildGenericTheory(spriteTypeHypothesis)
		return theory

	def generateTheoryRLEs(self):
		return VrleInitPhase(self.agent.hypotheses, self.agent.rle, self.agent.symbolDict)

	########################################
	# Execution
	def executeStep(self, episode_num, action, lastStep=False):
		theoryRLEs = self.generateTheoryRLEs()
		self.agent.hypotheses = self.agent.executeStep(episode_num, self.agent.rleHistory, self.agent.actionHistory, 
											     action, self.agent.hypotheses, theoryRLEs, lastStep)

	def runEpisode(self, episode_num, actions):
		self.initializeEpisode(episode_num)
		for action in actions:
			self.executeStep(episode_num, action)

	def runCurriculum(self, action_sequences):
		self.initializeCurriculum(len(action_sequences))
		for episode_num, actions in enumerate(action_sequences):
			self.runEpisode(episode_num, actions)

	########################################
	# Display Functions
	def displayHypotheses(self):
		print '==========HYPOTHESES=============='
		for h in self.agent.hypotheses:
			print h.__dict__.keys()
			h.display()

	########################################
	# Test Suite
	def testLevel0(self):
		action_sequences = [[K_UP]]
		self.initialize(simple.game, simple.levels[0], action_sequences)

		theory = generateTheoryFromGame(self.agent.rle)
		# self.executeStep(0, K_UP)
		# hypothesis = self.agent.hypotheses[0]
		# interaction = Interaction('DARKBLUE', 'DARKBLUE', 'stepBack', {})
		# # interaction2 = Interaction('DARKBLUE', 'DARKBLUE', 'killSprite', {})
		# self.assertTrue(hypothesisContainsInteraction(hypothesis, interaction))
		# # self.assertTrue(*hypothesisContainsInteraction(hypothesis, interaction2))

	def testLevel1(self):
		action_sequences = [[K_UP]]
		self.initialize(simple.game, simple.levels[0], action_sequences)
		self.executeStep(0, K_UP)
		hypothesis = self.agent.hypotheses[0]

		self.assertTrue(hypothesisAssignsVGDLType2Color(hypothesis, 'DARKBLUE', MovingAvatar))




	
