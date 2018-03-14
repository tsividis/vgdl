import unittest
from line_profiler import LineProfiler
from vgdl.agent import matchEnvs, matchEnvsDeprecated, matchEnvsV2, createRLInputGameFromStrings
from collections import defaultdict

import tests.game_strings as gs

class TestMatchEnvs(unittest.TestCase):

	def setUp(self):
		self.matchEnvs = matchEnvs

		self.test_envs = {}
		for levels, level_strings in [(key, getattr(gs, key)) for key in gs.__dict__ if 'level' in key]:
			self.test_envs[levels] = self.createEnvsAB(gs.game_string, *level_strings)


	##################################################################
	# Helper functions for creating and displaying enviroments
	def createEnvsAB(self, game_string, level_stringA, level_stringB):
		envA, envB = (createRLInputGameFromStrings(game_string, level_stringA),
					  createRLInputGameFromStrings(game_string, level_stringB))

		# adds tracked objects to the mix
		for env in (envA, envB):
			env._game.observation = {'trackedObjects': defaultdict(lambda : [])}
			for stype, sprites in env._game.sprite_groups.iteritems():
				if sprites:
					color = sprites[0].colorName
					env._game.observation['trackedObjects'][color] = sprites[:]
		return envA, envB	

	def getAllEnvSprites(self, env):
		return [sprite for name, sprites in env._game.sprite_groups.iteritems() for sprite in sprites]

	def getResults(self, envA, envB):
		all_sprites = self.getAllEnvSprites(envA)
		matched, lonelyA, lonelyB = self.matchEnvs(envA, envB)
		return all_sprites, matched, lonelyA, lonelyB

	def stringResults(self, matched, lonelyA, lonelyB, lonely_types=None):
		return_string = "matched sprites\n"
		for match in matched:
			if lonely_types:
				if match[0].name != lonely_types[0].name:
					continue
			return_string += "\t" + str(match) + "\n"

		return_string += "lonely sprites env A \n\t %r \n" % lonelyA
		return_string += "lonely sprites env B \n\t %r \n" % lonelyB
		return return_string

	##################################################################
	# Basic Assertion Methods
	def assertMatchedDistance(self, matched, match_name, distance):
		for sA, sB, dist in matched:
			if sA.name == match_name:
				self.assertEqual(dist, distance, 'incorrect match %r %r with dist %f. expcected %f' % (sA, sB, dist, distance))

	def assertNoLonelySprites(self, all_sprites, matched, lonelyA, lonelyB):
		self.assertEqual(len(lonelyA), 0, "Found lonely sprites in EnvA\n" +self.stringResults(matched, lonelyA, lonelyB, lonelyA))
		self.assertEqual(len(lonelyB), 0, "Found lonely sprites in EnvB\n" + self.stringResults(matched, lonelyA, lonelyB, lonelyB))
		self.assertEqual(len(all_sprites), len(matched))

	def assertMatchPositions(self, spriteA, spriteB, pos1, pos2):
		self.assertEqual(spriteA.rect.topleft, pos1)
		self.assertEqual(spriteB.rect.topleft, pos2)

	def assertMoved(self, spriteA, spriteB, direction):
		xi, yi = spriteA.topleft
		xd, yd = direction
		self.assertEqual(spriteB.rect.topleft, (xi+xd, xi+yd))

	###################################################################
	# The Test Suite
	def testNothingMoved(self):
		'Tests "level_strings1". Nothing moved.'
		all_sprites, matched, lonelyA, lonelyB = self.getResults(*self.test_envs['level_strings0'])
		
		self.assertNoLonelySprites(all_sprites, matched, lonelyA, lonelyB)

	def testMovingAvatar(self):
		'Tests "level_strings1". Avatar moves one space to the left.'
		all_sprites, matched, lonelyA, lonelyB = self.getResults(*self.test_envs['level_strings1'])
		
		self.assertNoLonelySprites(all_sprites, matched, lonelyA, lonelyB)


	def testMovingLogs(self):	
		'Tests "level_strings2". A group of 3 logs moves to the right.'	
		all_sprites, matched, lonelyA, lonelyB = self.getResults(*self.test_envs['level_strings2'])

		self.assertNoLonelySprites(all_sprites, matched, lonelyA, lonelyB)
		self.assertMatchedDistance(matched, 'log', 1)

	def testLotsOfThings(self):
		'Tests "level_strings3". Group of 6 logs, moves up one space.'
		all_sprites, matched, lonelyA, lonelyB = self.getResults(*self.test_envs['level_strings3'])

		self.assertNoLonelySprites(all_sprites, matched, lonelyA, lonelyB)
		self.assertMatchedDistance(matched, 'log', 1)

	def testOneMovingLeftOn(self):
		'Tests "level_strings4". Two adjacent groups of 3 logs. One of them moves to the left.'		
		all_sprites, matched, lonelyA, lonelyB = self.getResults(*self.test_envs['level_strings4'])

		self.assertNoLonelySprites(all_sprites, matched, lonelyA, lonelyB)

		for sA, sB, dist in matched:
			if sA.name == 'log':
				if sB.y == 60:
					self.assertEqual(dist, 1, "Incorrect match %r %r with dist %f. expected 1.0." % (sA, sB, dist))
				if sB.y == 90:
					self.assertEqual(dist, 0, "Incorrect match %r %r with dist %f. expected 0.0." % (sA, sB, dist))

	def testOneMovingRightOn(self):
		'Tests "level_strings4". Two adjacent groups of 3 logs. One of them moves to the right.'		
		all_sprites, matched, lonelyA, lonelyB = self.getResults(*self.test_envs['level_strings5'])

		self.assertNoLonelySprites(all_sprites, matched, lonelyA, lonelyB)

		for sA, sB, dist in matched:
			if sA.name == 'log':
				if sB.y == 60:
					self.assertEqual(dist, 1, "Incorrect match %r %r with dist %f. expected 1.0." % (sA, sB, dist))
				if sB.y == 90:
					self.assertEqual(dist, 0, "Incorrect match %r %r with dist %f. expected 0.0." % (sA, sB, dist))
			
	def testOneMovingRightOff(self):
		'Tests "level_strings4". Two adjacent groups of 3 logs. One of them moves to the right.'		
		all_sprites, matched, lonelyA, lonelyB = self.getResults(*self.test_envs['level_strings6'])

		self.assertNoLonelySprites(all_sprites, matched, lonelyA, lonelyB)

		for sA, sB, dist in matched:
			if sA.name == 'log':
				if sB.y == 60:
					self.assertEqual(dist, 1, "Incorrect match %r %r with dist %f. expected 1.0." % (sA, sB, dist))
				if sB.y == 90:
					self.assertEqual(dist, 0, "Incorrect match %r %r with dist %f. expected 0.0." % (sA, sB, dist))
			
			
			
