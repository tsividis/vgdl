import unittest

from vgdl.agent import Agent, VrleInitPhase

# imports all the game files created in games to the global namespace
from tests.games import *

FILENAME = 'tests.game.simple'

class TestAgent(unittest.TestCase):

	def setUp(self):
		self.agent = Agent('full', FILENAME)

	########################################
	# Initialization Methods
	def initializeEnvironment(self, game_string, level_string):
		self.agent.gameString = game_string
		self.agent.levelString = level_string
		self.agent.initializeEnvironment()

	def initializeCurriculum(self, num_episodes):
		self.agent.rleHistory = [[] for i in range(num_episodes)]
		self.agent.actionHistory = [[] for i in range(num_episodes)]
		self.agent.all_objects = [{} for i in range(num_episodes)]
		self.episode_num = 0
		self.action_num = 0

	def initializeEpisode(self, episode_num):
		self.all_objects[episode_num] = self.rle._game.getObjects()
		if episode_num == 0:
			self.agent.initializeHypotheses(self.agent.all_objects[episode_num])
		envReal = self.agent.fastcopy(self.agent.rle)
		self.agent.rleHistory[episode_num].appnd(envReal)

	def generateTheoryRLEs(self):
		return VrleInitPhase(self.agent.hypotheses, self.agent.rle, self.agent.symbolDict)

	def executeStep(self, episode_num, action, lastStep=False):
		theoryRLEs = self.generateTheoryRLEs()

		return self.executeStep(episode_num, self.agent.rleHistory, self.agent.actionHistory, action, self.agent.hypotheses, theoryRLEs, lastStep)

	########################################
	# Theory Assertion
	def assertTheory(self):
		self.assertEqual(1, 1)

	########################################
	# Test Suite
	def testLevel0(self):

		self.initialize(simple.game, simple.levels[0])
		self.assertTrue(True)

	def testLevel1(self):
		self.assertTheory()




	
