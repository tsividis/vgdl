import unittest

from vgdl.util import embed

from vgdl.agent import Agent, VrleInitPhase, sampleFromDistribution
from vgdl.ontology import *

# imports all the game files created in games to the global namespace
from tests.games import *
from tests.theory_tools import *
from tests.locals import *

# I'm not sure if this actually matters...
FILENAME = 'tests.game.inference'

###########################################
# The abstract base class. Only add Assertion Methods
class _TestAgent(unittest.TestCase):

	#######################################
	# Set Up and Tear Down
	#
	# Simply creates a new agent for every test. You have to set up the games individually.
	def setUp(self):
		# embed()
		self.agent = Agent('full', FILENAME)

	def tearDown(self):
		pass

	########################################
	# Initialization
	def initializeCurriculum(self, game_string, level_string, action_sequences):
		num_episodes = len(action_sequences)
		self.agent.gameString = game_string
		self.agent.levelString = level_string
		self.agent.rleHistory = [[] for i in range(num_episodes)]
		self.agent.actionHistory = [[] for i in range(num_episodes)]
		self.agent.all_objects = [{} for i in range(num_episodes)]

	def initializeEpisode(self, episode_num):
		'''Sets up episode'''
		self.agent.initializeEnvironment()
		self.agent.all_objects[episode_num] = self.agent.rle._game.getObjects()
		if episode_num == 0 or not self.agent.hypotheses:
			print self.agent.learnAvatar
			self.agent.initializeHypotheses(self.agent.all_objects[episode_num])
		assert self.agent.hypotheses, 'No hypotheses initilialized'
		envReal = self.agent.fastcopy(self.agent.rle)
		self.agent.rleHistory[episode_num].append(envReal)

	def initRunCreate(self, game, level, action_sequences):
		self.runCurriculum(game, level, action_sequences)

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
	def executeStep(self, episode_num, action, last_step):
		theoryRLEs = self.generateTheoryRLEs()

		self.agent.hypotheses, self.agent.scoresAndHypotheses = self.agent.executeStep(episode_num, self.agent.rleHistory, self.agent.actionHistory, 
											     										action, self.agent.hypotheses, theoryRLEs, last_step)
		self.agent.hypotheses = [tup[1] for tup in self.agent.scoresAndHypotheses]

	def runEpisode(self, episode_num, actions):
		self.initializeEpisode(episode_num)
		last_step = False
		for num, action in enumerate(actions):
			if num+1 == len(actions):
				last_step = True
			self.executeStep(episode_num, action, last_step)

	def runCurriculum(self, game_string, level_string, action_sequences):
		self.initializeCurriculum(game_string, level_string, action_sequences)
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
		self.assertTrue(theoryInHypotheses(theory, self.agent.hypotheses), 'Theory not in hypotheses: \n%s' % theory._string(False, True, False))


	def assertTheoryBelowEpsilonError(self, hypothesis, epsilon=0.01):
		''''''
		for e, h in self.agent.scoresAndHypotheses:
			if h == hypothesis:
				self.assertTrue(e <= epsilon, 'Hypothesis does not have low error')

	def assertAgentHasTheories(self):
		self.assertTrue(len(self.agent.hypotheses) > 0, 'Agent has no theories')


def _testConstructor(game, level, action_sequences, expected_theory=None):
	'''Creates a basic test case. Theory learned == Real Game Description'''
	# print game
	def testCase(self):
		print 'RUNNING TEST'
		print game, '\n', level, '\n', action_sequences, '\n'
		self.initRunCreate(game, level, action_sequences)
		if expected_theory:
			theory = generateTheoryFromGameString(expected_theory)
		else:
			theory = generateTheoryFromGameString(game)
<<<<<<< HEAD
<<<<<<< HEAD
		self.initRunCreate(game, level, action_sequences)

=======
>>>>>>> parent of 6a4ea44... working on 3rd test
=======
>>>>>>> parent of 6a4ea44... working on 3rd test
		# embed()
		self.assertAgentHasTheory(theory)
		self.assertTheoriesEqual(self.agent.hypotheses[0], theory)
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
		self.initRunCreate(*basics.test2)
		real_description = generateTheoryFromGameString(basecs.test2.game)
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

class inference(_TestAgent):

	# test1 = _testConstructor(*inference.test1)
	test0 = _testConstructor(*inference.test0)

	test1 = _testConstructor(*inference.test1)

	test2 = _testConstructor(*inference.test2)

	test3 = _testConstructor(*inference.test3)

	test4 = _testConstructor(*inference.test4)

	# test5 = _testConstructor(*inference.test5)


	# test5 = _testConstructor(*inference.test5)



	# print inference.test0.game
