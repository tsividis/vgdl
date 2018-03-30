import unittest

from vgdl.agent import Agent, VrleInitPhase, sampleFromDistribution
from vgdl.theory_template import Game
from pygame.locals import *
from vgdl.ontology import *

from collections import namedtuple

# imports all the game files created in games to the global namespace
from tests.games import *

FILENAME = 'tests.game.simple'

Interaction = namedtuple('Interaction', 'slot1, slot2,  interaction, args')
ClassAssignment = namedtuple('ClassAssignment', 'vgdlType, args')

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
	# Theory Tools
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


	def getColorAssignments(self, hypothesis):
		'''Returns class assignments where class names are converted to their respective color names'''
		color_assignments = {}
		for class_name, vgdl_classes in hypothesis.classes.iteritems():
			color_name = vgdl_classes[0].colorName
			sprite_object = hypothesis.spriteObjects[color_name]
			color_assignments[color_name] = ClassAssignment(sprite_object.vgdlType, sprite_object.args)
		return color_assignments

	def getColorName(self, hypothesis, class_name):
		'''Returns the the color of a given class in a given hypothesis'''
		assert class_name in hypothesis.classes, 'Key Error: class name not in hypothesis'
		return hypothesis.classes[class_name][0].colorName

	def getColorInteractionSet(self, hypothesis):
		'''Reterns interaction set where class names are converted to their respective color names'''
		color_interaction_set = []
		for rule in hypothesis.interactionSet:
			color1 = self.getColorName(hypothesis, rule.slot1)
			color2 = self.getColorName(hypothesis, rule.slot2)
			interaction = Interaction(color1, color2, rule.interaction, rule.args.copy())
			color_interaction_set.append(interaction)
		return color_interaction_set

	def argsEqual(self, args1, args2):
		if set(args1) == set(args2):
			for key in args1:
				if args1[key] != args2[key]:
					return False
			return True
		return False


	def interactionsEqual(self, interaction1, interaction2):
		for i1, i2 in zip(interaction1[:-1], interaction2[:-1]):
			if i1 != i2:
				return False
		return self.argsEqual(interaction1.args, interaction2.args)

	def hypothesisContainsInteraction(self, hypothesis, interaction):
		'''assert hypothesis contains a specific interaction 
		relating color1 and color2 with specific arguments'''

		rule = hypothesis.interactionSet[0]
		for i in self.getColorInteractionSet(hypothesis):
			if self.interactionsEqual(i, interaction):
				return True
		return False

	def hypothesisAssignsVGDLType2Color(self, hypothesis, color_name, vgdl_type):
		return self.getColorAssignments(hypothesis)[color_name].vgdlType == vgdl_type


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
	# Theory Assertion
	def assertHypothesesSmallError(self):
		'''Assert one or more of the Hypotheses have small error'''
		self.assertTrue(len([h for h in self.agent.hypotheses]) > 0)

	def assertHypothesesContainTheory(self, theory):
		'''Assert hypotheses contains exact theory'''
		self.assertTrue(True)

	def assertHypothesisContainsSpriteType(self, hypothesis, color, sprite_type):
		'''assert hypothesis classifeid color as sprite_type'''
		self.assertTrue(True)

	########################################
	# Test Suite
	def testLevel0(self):
		action_sequences = [[K_UP]]
		self.initialize(simple.game, simple.levels[0], action_sequences)
		self.executeStep(0, K_UP)
		hypothesis = self.agent.hypotheses[0]
		interaction = Interaction('DARKBLUE', 'DARKBLUE', 'stepBack', {})
		self.assertTrue(self.hypothesisContainsInteraction(hypothesis, interaction))

	def testLevel1(self):
		action_sequences = [[K_UP]]
		self.initialize(simple.game, simple.levels[0], action_sequences)
		self.executeStep(0, K_UP)
		hypothesis = self.agent.hypotheses[0]

		self.assertTrue(self.hypothesisAssignsVGDLType2Color(hypothesis, 'DARKBLUE', MovingAvatar))




	
