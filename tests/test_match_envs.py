import unittest
from line_profiler import LineProfiler

from vgdl.agent import matchEnvs, createRLInputGameFromStrings

def createEnvsAB(game_string, level_stringA, level_stringB):
	return (createRLInputGameFromStrings(game_string, level_stringA),
			createRLInputGameFromStrings(game_string, level_stringB))

def getAllEnvSprites(env):
	return [sprite for name, sprites in env._game.sprite_groups.iteritems() for sprite in sprites]

class TestMatchEnvs(unittest.TestCase):

	def setUp(self):
		self.game_string = '''
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		wall > Immovable color=DARKGRAY
		log > Missile speed=1 color=BROWN
	LevelMapping
		A > avatar
		w > wall
		L > log
	TerminationSet
		Termination
'''
		self.level_strings1 = ('''
wwwwwwwwwwwwwww
w             w
w     A       w
wwwwwwwwwwwwwww
''', '''
wwwwwwwwwwwwwww
w             w
w      A      w
wwwwwwwwwwwwwww
''')

		self.level_strings2 = ('''
wwwwwwwwwwwwwww
w             w
w      LLL    w
wwwwwwwwwwwwwww
''', '''
wwwwwwwwwwwwwww
w             w
w     LLL     w
wwwwwwwwwwwwwww
''')

		self.level_strings3 = ('''
wwwwwwwwwwwwwww
w             w
w     LLL     w
w     LLL     w
w             w
w             w
w     A       w
wwwwwwwwwwwwwww
''', '''
wwwwwwwwwwwwwww
w     LLL     w
w     LLL     w
w             w
w             w
w             w
w     A       w
wwwwwwwwwwwwwww
''')
		self.level_strings4 = ('''
wwwwwwwwwwwwwww
w             w
w      LLL    w
w     LLL     w
w             w
w             w
w     A       w
wwwwwwwwwwwwwww
''', '''
wwwwwwwwwwwwwww
w             w
w     LLL     w
w     LLL     w
w             w
w             w
w     A       w
wwwwwwwwwwwwwww
''')

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

	def assertMatchedD1(self, matched, match_name):
		for sA, sB, dist in matched:
			if sA.name == match_name:
				self.assertEqual(dist, 1, 'incorrect match %r %r with dist %f' % (sA, sB, dist))

	def testMovingAvatar(self):
		envA, envB = createEnvsAB(self.game_string, *self.level_strings1)
		all_sprites = getAllEnvSprites(envA)

		matched, lonelyA, lonelyB = matchEnvs(envA, envB)
		self.assertEqual(len(lonelyA), 0, "Found lonely sprites in EnvA\n" +self.stringResults(matched, lonelyA, lonelyB, lonelyA))
		self.assertEqual(len(lonelyB), 0, "Found lonely sprites in EnvB\n" + self.stringResults(matched, lonelyA, lonelyB, lonelyB))
		self.assertEqual(len(all_sprites), len(matched))

	def testMovingLogs(self):		
		envA, envB = createEnvsAB(self.game_string, *self.level_strings2)
		all_sprites = getAllEnvSprites(envA)

		matched, lonelyA, lonelyB = matchEnvs(envA, envB)
		self.assertEqual(len(lonelyA), 0, "Found lonely sprites in EnvA\n" +self.stringResults(matched, lonelyA, lonelyB, lonelyA))
		self.assertEqual(len(lonelyB), 0, "Found lonely sprites in EnvB\n" + self.stringResults(matched, lonelyA, lonelyB, lonelyB))
		self.assertEqual(len(all_sprites), len(matched))
		self.assertMatchedD1(matched, 'log')

	def testLotsOfThings(self):
		envA, envB = createEnvsAB(self.game_string, *self.level_strings3)
		all_sprites = getAllEnvSprites(envA)
		matched, lonelyA, lonelyB = matchEnvs(envA, envB)
		self.assertEqual(len(lonelyA), 0, "Found lonely sprites in EnvA\n" +self.stringResults(matched, lonelyA, lonelyB, lonelyA))
		self.assertEqual(len(lonelyB), 0, "Found lonely sprites in EnvB\n" +self.stringResults(matched, lonelyA, lonelyB, lonelyB))
		self.assertEqual(len(all_sprites), len(matched))
		self.assertMatchedD1(matched, 'log')

	def testDifferentDirection(self):		
		envA, envB = createEnvsAB(self.game_string, *self.level_strings4)
		all_sprites = getAllEnvSprites(envA)

		matched, lonelyA, lonelyB = matchEnvs(envA, envB)
		self.assertEqual(len(lonelyA), 0, "Found lonely sprites in EnvA\n" +self.stringResults(matched, lonelyA, lonelyB, lonelyA))
		self.assertEqual(len(lonelyB), 0, "Found lonely sprites in EnvB\n" + self.stringResults(matched, lonelyA, lonelyB, lonelyB))
		self.assertEqual(len(all_sprites), len(matched))
		self.assertMatchedD1(matched, 'log')		
