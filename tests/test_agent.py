import unittest
import time

from vgdl.util import embed

from vgdl.agent import Agent, VrleInitPhase #, sampleFromDistribution
from vgdl.ontology import *

# imports all the game files created in games to the global namespace
from tests.games import *
from tests.theory_tools import *
from tests.locals import *

# I'm not sure if this actually matters...
FILENAME = 'tests.game.inference'
EMBED_ON_FAILURE = False

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

	def run(self, results=None):
		self.currentResults = results
		unittest.TestCase.run(self, results)

	def tearDown(self):
		if EMBED_ON_FAILURE:
			errors = self.currentResults.errors
			failures = self.currentResults.failures
			if failures or errors:
				print 
				print 'ERRORS:'
				print '=================='
				for error, message in errors:
					print error
					print message
				print
				print 'FAILURES:'
				print '=================='
				for failure, message in failures:
					print failure
					print message
				print '==================='
				print 'EMBEDING inside test_agent'
				embed()

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
		if episode_num == 0:
			self.agent.initializeHypotheses(episode_num)
		assert self.agent.hypotheses, 'No hypotheses initilialized'
		envReal = self.agent.fastcopy(self.agent.rle)
		self.agent.rleHistory[episode_num].append(envReal)

	def generateTheoryRLEs(self):
		return VrleInitPhase(self.agent.hypotheses, self.agent.rle)

	########################################
	# Execution
	def executeStep(self, episode_num, action_num, action, last_step):
		theoryRLEs = self.generateTheoryRLEs()

		scoresAndHypotheses = self.agent.executeStep(episode_num, self.agent.rleHistory, self.agent.actionHistory, 
											     										action, self.agent.hypotheses, last_step)
		self.agent.hypotheses = [tup[1] for tup in scoresAndHypotheses]

	def runEpisode(self, episode_num, actions):
		self.initializeEpisode(episode_num)
		last_step = False
		for num, action in enumerate(actions):
			if num == len(actions)-1:
				last_step = True
			self.executeStep(episode_num, num, action, last_step)

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

	def stringDiffs(self, set_name, diff1, diff2):
		string = '\n%s Not Equal' % set_name
		string += '\nEverything equal except...' 
		string += '\n>>>'
		string += '--- Theory1 has these while Theory2 does not'
		for diff in diff1:
			string += '\n%s' % str(diff)
		string += '\n--- Theory2 has these while Theory1 does not'
		for diff in diff2:
			string += '\n%s' % str(diff)
		string += '\n<<<\n'
		return string

	def stringAllDiffs(self, theory1, theory2, ignore_novelty_terminations=True):
		display = "Theory diffs\n"
		if not classAssignmentsEqual(theory1, theory2):
			display += self.stringDiffs('SpriteSet', *classAssignmentsDiff(theory1, theory2))
		if not interactionSetsEqual(theory1, theory2):
			display += self.stringDiffs('InteractionSet', *interactionSetsDiff(theory1, theory2))
		if not terminationSetsEqual(theory1, theory2, ignore_novelty_terminations):
			display += self.stringDiffs('TerminationSet', *terminationSetsDiff(theory1, theory2))
		return display

	def stringLowErrorHypotheses(self, error_limit=0.01):
		string += '===============Low Error Hypotheses=============='
		for e, h in zip(self.agent.scores, self.agent.hypotheses):
			if e < error_limit:
				string += '\n%s' % h

		return string

	########################################
	# Assertion Function
	def assertTheoriesEqual(self, theory1, theory2, ignore_novelty_terminations=True):
		self.assertTrue(theoriesEqual(theory1, theory2), self.stringAllDiffs(theory1, theory2, ignore_novelty_terminations))

	def assertTheoriesNotEqual(self, theory1, theory2, ignore_novelty_terminations=True):
		display = 'Theories Equal\n'
		display += '>>> Theory1 and Theory2\n'
		display += str(theory1)
		display += '\n<<<'
		self.assertFalse(theoriesEqual(theory1, theory2), display)

	def assertAgentHasTheory(self, theory, ignore_novelty_terminations=True):
		diffs = "\nTop 3 Theory diffs\n"
		if not theoryInHypotheses(theory, self.agent.hypotheses):
			for h in self.agent.hypotheses[:3]:
				diffs += self.stringAllDiffs(h, theory, ignore_novelty_terminations)

		self.assertTrue(theoryInHypotheses(theory, self.agent.hypotheses), 'Theory not in hypotheses: \n%s\n%s' % (theory, diffs))


	def assertTheoryBelowEpsilonError(self, h_index, epsilon=0.01):
		''''''
		self.assertTrue(self.agent.scores[h_index] <= epsilon, 'Hypothesis does not have low error')

	def assertAgentHasTheories(self):
		self.assertTrue(len(self.agent.hypotheses) > 0, 'Agent has no theories')

	def _testTest(self):
		self.assertTrue(False)


def basicTestConstructor(game, level, action_sequences, expected_theory=None):
	'''Creates a basic test case. Theory learned == Real Game Description'''
	# print game
	def testCase(self):
		print 'RUNNING TEST'
		print game, '\n', level, '\n', action_sequences, '\n'
		if expected_theory:
			theory = generateTheoryFromGameString(expected_theory)
		else:
			theory = generateTheoryFromGameString(game)

		self.runCurriculum(game, level, action_sequences)

		self.assertAgentHasTheory(theory)
		# self.assertTheoriesEqual(self.agent.hypotheses[0], theory)
		# min_epsilon = min(self.agent.scores)
		# for i, t in enumerate(self.agent.hypotheses):
		# 	if theoriesEqual(t, theory):
		# 		self.assertTheoryBelowEpsilonError(i, min_epsilon)
		# 		break
		## Write whatever things you want to test for here.

	return testCase

######################################################################################
# The Test Class you actually want to modify!

class TestBasics(_TestAgent):

	########################################
	# Test Suite
	#
	# This is one way to create a test case. Defaults to the basics (defined above)
	testKillSpritesAndWin = basicTestConstructor(*basics.test1)
	testKillSpritesAndNothing = basicTestConstructor(*basics.test4)
	## specify what levels you want to give it here. see basics.py for examples.

	# This is another way to create a test case. You can do everything individually.
	def testKillSpriteAndStop(self):
		game, level, action_sequences, expected_theory = basics.test2
		if not expected_theory:
			expected_theory = generateTheoryFromGameString(game)
		self.runCurriculum(game, level, action_sequences)
		# this may not be that useful, but I'll keep it around anyway.
		self.assertAgentHasTheories()
		self.assertAgentHasTheory(expected_theory)
		# self.assertTheoriesEqual(self.agent.hypotheses[0], expected_theory)

	# def testKillSpritesAndNothing(self):
	# 	real_description = self.runCurriculum(*basics.test4)
	# 	self.assertTheoriesEqual(self.agent)


	def testFilter(self):
		game, level, action_sequences, _ = basics.test1
		self.initializeCurriculum(game, level, action_sequences)
		self.initializeEpisode(0)

		self.executeStep(0, K_UP, False)
		self.assertAgentHasTheories()
		self.executeStep(0, K_UP, True)
		self.assertAgentHasTheories()

class TestInference(_TestAgent):


	test1 = basicTestConstructor(*inference.test1)
	test2 = basicTestConstructor(*inference.test2)

	### test3 = basicTestConstructor(*inference.test3)

	test4 = basicTestConstructor(*inference.test4)

	test5 = basicTestConstructor(*inference.test5)

	### test6 = basicTestConstructor(*inference.test6)

	# test7 = basicTestConstructor(*inference.test7) #takes long, but add it back at some point.

	test8 = basicTestConstructor(*inference.test8)

	### test9 = basicTestConstructor(*inference.test9)
	### test10 = basicTestConstructor(*inference.test10)

	### test11 = basicTestConstructor(*inference.test11)

	test12 = basicTestConstructor(*inference.test12)

	### test13 = basicTestConstructor(*inference.test13)

	test14 = basicTestConstructor(*inference.test14)

	test15 = basicTestConstructor(*inference.test15)

	test16 = basicTestConstructor(*inference.test16)

class _TestGeneral(_TestAgent):


	# [9.328, 0.383, 0.28, 0.166, 148.216, 3.452, 104.065, 1.984, 2.221, 2.156, 34.015]
	def test_learning_times(self):
		game, level, action_sequences, _ = general.test_case
		expected_theory = generateTheoryFromGameString(game)

		self.initializeCurriculum(game, level, action_sequences)
		episode_num = 0 
		self.initializeEpisode(episode_num)


		times_per_step_level1 = [0 for i in action_sequences[episode_num]]
		last_step = False
		actions = action_sequences[episode_num]
		for num, action in enumerate(actions):
			if num == len(actions)-1:
				last_step = True

			t0 = time.time()
			self.executeStep(episode_num, action, last_step)
			t1 = time.time()

			times_per_step_level1[num] = round(t1-t0, 5)

		episode_num = 1
		self.initializeEpisode(episode_num)
		times_per_step_level2 = [0 for i in action_sequences[episode_num]]
		last_step = False
		actions = action_sequences[episode_num]
		for num, action in enumerate(actions):
			if num == len(actions)-1:
				last_step = True

			t0 = time.time()
			self.executeStep(episode_num, action, last_step)
			t1 = time.time()

			times_per_step_level2[num] = round(t1-t0, 5)

		print times_per_step_level1, times_per_step_level2
		self.assertAgentHasTheories()
		self.assertAgentHasTheory(expected_theory)

	test2 = basicTestConstructor(*general.test_case2)
		

if __name__ == "__main__":
    import argparse
    from vgdl.core import VGDLParser

    parser = argparse.ArgumentParser(description='play test games')

    parser.add_argument('test', type=str, nargs=1)    


    args = parser.parse_args()
    test = eval(args.test[0])

    game, level = test.game, test.level
    VGDLParser.playGame(test.game, test.level)