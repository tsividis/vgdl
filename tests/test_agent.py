import unittest

from IPython import embed

from vgdl.agent import Agent, VrleInitPhase, sampleFromDistribution
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
		self.agent.hypotheses, self.agent.scoresAndHypotheses = self.agent.executeStep(episode_num, self.agent.rleHistory, self.agent.actionHistory, 
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
	def stringHypotheses(self):
		string = '==========HYPOTHESES=============='
		for h in self.agent.hypotheses:
			string += '\n%s' % h

	def stringCompareTheories(self, theory1, theory2, string_function, **kwargs):
		string = '--- Theory1'
		string += '%s' % getattr(theory1, string_function)(**kwargs)
		string += '\n--- Theory2'
		string += '%s\n---' % getattr(theory2, string_function)(**kwargs)
		return string

	def stringLowErrorHypotheses(self, error):
		string += '===============Low Error Hypotheses=============='
		for e, h in self.agent.scoresAndHypotheses:
			if e < error:
				string += '\n%s' % h


	########################################
	# Assertion Function
	def assertTheoriesEqual(self, theory1, theory2, ignore_novelty_terminations=True):
		display = 'Theoies Not Equal\n'
		if not classAssignmentsEqual(theory1, theory2):
			display += '\n>>> Class Assignments not Equal'
			display += '\n%s\n<<<' % self.stringCompareTheories(theory1, theory2, '_stringClasses')
		if not interactionSetsEqual(theory1, theory2):
			display += '\n>>> Interaction Sets not Equal'
			display += '\n%s\n<<<' % self.stringCompareTheories(theory1, theory2, '_stringRules', ignore_step_back=False)
		if not terminationSetsEqual(theory1, theory2, ignore_novelty_terminations):
			display += '\n>>> Termination Sets not Equal'
			display += '\n%s\n<<<' % self.stringCompareTheories(theory1, theory2, '_stringTerminations')
		# display += '\n%s' % theory1
		# display += '\n%s' % theory2 
		self.assertTrue(theoriesEqual(theory1, theory2), display)

	def assertHypothesisHasLowError(self, hypothesis, scores_and_hypotheses, error=0.0):
		''''''
		self.assertTrue(True)

	########################################
	# Test Suite
	def testLevel0(self):
		test_hypothesis = generateTheoryFromGameString(simple.test_hypothesis)
		action_sequences = [[K_UP, K_UP, K_UP]]
		self.initialize(simple.game, simple.levels[0], action_sequences)

		# self.executeStep(0, K_UP)
		self.runCurriculum(action_sequences)

		
		h0 = self.agent.hypotheses[0]
		# self.assertTrue(theoriesEqual(h0, test_hypothesis))
		self.assertTheoriesEqual(h0, test_hypothesis)

		# hypothesis = self.agent.hypotheses[0]
		# interaction = Interaction('DARKBLUE', 'DARKBLUE', 'stepBack', {})
		# # interaction2 = Interaction('DARKBLUE', 'DARKBLUE', 'killSprite', {})
		# self.assertTrue(hypothesisContainsInteraction(hypothesis, interaction))
		# # self.assertTrue(*hypothesisContainsInteraction(hypothesis, interaction2))

	# def testLevel1(self):
	# 	action_sequences = [[K_UP]]
	# 	self.initialize(simple.game, simple.levels[0], action_sequences)
	# 	self.executeStep(0, K_UP)
	# 	hypothesis = self.agent.hypotheses[0]

	# 	self.assertTrue(hypothesisAssignsVGDLType2Color(hypothesis, 'DARKBLUE', MovingAvatar))


# if __name__ == '__main__':


	
