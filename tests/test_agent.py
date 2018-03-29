import unittest

from vgdl.agent import Agent, VrleInitPhase
from vgdl.theory_template import Game
from pygame.locals import *

# imports all the game files created in games to the global namespace
from tests.games import *

FILENAME = 'tests.game.simple'

class TestAgent(unittest.TestCase):

	def setUp(self):
		self.agent = Agent('full', FILENAME)

	########################################
	# Initialization
	def initializeEnvironment(self, game_string=None, level_string=None):
		self.agent.gameString = game_string
		self.agent.levelString = level_string
		self.agent.initializeEnvironment()

	def initializeCurriculum(self, action_sequences):
		num_episodes = len(action_sequences)
		self.agent.rleHistory = [[] for i in range(num_episodes)]
		self.agent.actionHistory = [[] for i in range(num_episodes)]
		self.agent.all_objects = [{} for i in range(num_episodes)]
		self.action_sequences = [actions[:] for actions in action_sequences]

	def initializeEpisode(self, episode_num):
		self.action_num = 0
		self.agent.all_objects[episode_num] = self.agent.rle._game.getObjects()
		if episode_num == 0:
			self.agent.initializeHypotheses(self.agent.all_objects[episode_num])
		envReal = self.agent.fastcopy(self.agent.rle)
		self.agent.rleHistory[episode_num].append(envReal)

	def buildTheory(self, game_string):
		theory = Game(game_string).buildGenericTheory()
		# for interaction_rule in theory.interactionSet:
		# 	if interaction_rule.slot1 == 'avatar':
		# 		interaction_rule.interaction = 
		return theory

	def generateTheoryRLEs(self):
		return VrleInitPhase(self.agent.hypotheses, self.agent.rle, self.agent.symbolDict)

	def executeStep(self, episode_num, action, lastStep=False):
		theoryRLEs = self.generateTheoryRLEs()
		self.agent.hypotheses = self.executeStep(episode_num, self.agent.rleHistory, self.agent.actionHistory, 
											     action, self.agent.hypotheses, theoryRLEs, lastStep)

	def runEpisode(self, episode_num, actions):
		self.initializeEpisode(episode_num)
		for action in actions:
			self.executeStep(episode_num, action)

	def runCurriculum(self, action_sequences):
		for episode_num, actions in enumerate(action_sequences):
			self.runEpisode(episode_num, actions)

	########################################
	# Theory Assertion
	def assertTheory(self):
		self.assertEqual(1, 1)

	########################################
	# Test Suite
	def testLevel0(self):
		action_sequences = [[K_UP, K_UP], [K_DOWN, K_DOWN]]
		self.assertTrue(True)

	def testLevel1(self):
		self.assertTheory()




	
