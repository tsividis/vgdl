import unittest

from IPython import embed

from vgdl.agent import Agent, VrleInitPhase, sampleFromDistribution
from vgdl.ontology import *

# imports all the game files created in games to the global namespace
from tests.games import *
from tests.theory_tools import *
from tests.locals import *

# I'm not sure if this actually matters...
FILENAME = 'tests.game.simple'

###########################################
# The abstract base class. Only add Assertion Methods
class _TestAgent(unittest.TestCase):

	#######################################
	# Set Up and Tear Down
	#
	# Simply creates a new agent for every test. You have to set up the games individually.
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

	def initRunCreate(self, game, level, action_sequences):
		self.initialize(game, level, action_sequences)
		self.runCurriculum(action_sequences)
		return generateTheoryFromGameString(game)

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
		string = '\n>>> %s not Equal'
		string += '--- Theory1'
		string += '%s' % getattr(theory1, string_function)(**kwargs)
		string += '\n--- Theory2'
		string += '%s\n---' % getattr(theory2, string_function)(**kwargs)
		string += '<<<\n'
		return string

	def stringLowErrorHypotheses(self, error_limit=0.01):
		string += '===============Low Error Hypotheses=============='
		for e, h in self.agent.scoresAndHypotheses:
			if e < error_limit:
				string += '\n%s' % h

	########################################
	# Assertion Function
	def assertTheoriesEqual(self, theory1, theory2, ignore_novelty_terminations=True, ignore_terminations=False):
		display = 'Theoies Not Equal\n'
		if not classAssignmentsEqual(theory1, theory2):
			display += self.stringCompareTheories(theory1, theory2, '_stringClasses', color_names=True)
		if not interactionSetsEqual(theory1, theory2):
			display += self.stringCompareTheories(theory1, theory2, '_stringRules', ignore_step_back=False, color_names=True)
		if not ignore_terminations:
			if not terminationSetsEqual(theory1, theory2, ignore_novelty_terminations):
				display += self.stringCompareTheories(theory1, theory2, '_stringTerminations', color_names=True)
		self.assertTrue(theoriesEqual(theory1, theory2), display)

	def assertTheoriesNotEqual(self, theory1, theory2, ignore_novelty_terminations=True):
		display = 'Theories Equal\n'
		display += '>>> Theory1 and Theory2\n'
		display += str(theory1)
		display += '\n<<<'
		self.assertFalse(theoriesEqual(theory1, theory2), display)

	def assertAgentHasTheory(self, theory):
		self.assertTrue(theoryInHypotheses(theory, self.agent.hypotheses), 'Theory not in hypotheses: \n%s' % theory)


	def assertTheoryBelowEpsilonError(self, hypothesis, epsilon=0.01):
		''''''
		for e, h in self.agent.scoresAndHypotheses:
			if h == hypothesis:
				self.assertTrue(e <= epsilon, 'Hypothesis does not have low error')

	def assertAgentHasTheories(self):
		self.assertTrue(len(self.agent.hypotheses) > 0, 'Agent has no theories')

	def _testLevel0(self):
		test_hypothesis = generateTheoryFromGameString(simple.test_hypothesis2)
		action_sequences = [[K_UP]]
		self.initialize(simple.game3, simple.levels[0], action_sequences)

		# self.executeStep(0, K_UP)
		self.runCurriculum(action_sequences)

		
		h0 = self.agent.hypotheses[0]
		# self.assertTrue(theoriesEqual(h0, test_hypothesis))
		self.assertTheoriesEqual(h0, test_hypothesis)

def _testConstructor(game, level, action_sequences):
	'''Creates a basic test case. Theory learned == Real Game Description'''
	def testCase(self):
		real_description = self.initRunCreate(game, level, action_sequences)

		self.assertAgentHasTheory(real_description)
		self.assertTheoriesEqual(self.agent.hypotheses[0], real_description)
		self.assertTheoryBelowEpsilonError(self.agent.hypotheses[0])
		## Write whatever things you want to test for here.

	return testCase

######################################################################################
# The Test Class you actually want to modify!

class TestBasics(_TestAgent):

	########################################
	# Test Suite
	#
	# This is one way to create a test case. Defaults to the basics (defined above)
	testKillSpritesAndWin = _testConstructor(*basics.test1)
	testKillSpritesAndNothing = _testConstructor(*basics.test4)
	## specify what levels you want to give it here. see basics.py for examples.

	# This is another way to create a test case. You can do everything individually.
	def testKillSpriteAndStop(self):
		real_description = self.initRunCreate(*basics.test2)
		# this may not be that useful, but I'll keep it around anyway.
		self.assertTheoriesEqual(self.agent.hypotheses[0], real_description)

	# def testKillSpritesAndNothing(self):
	# 	real_description = self.initRunCreate(*basics.test4)
	# 	self.assertTheoriesEqual(self.agent)


	def testFilter(self):
		self.initialize(*basics.test1)

		self.executeStep(0, K_UP)
		self.assertAgentHasTheories()
		self.executeStep(0, K_UP)
		self.assertAgentHasTheories()


