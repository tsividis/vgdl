import unittest

from vgdl.agent import experienceReplay, Agent
from vgdl.theory_template import Theory, Game
from examples.gridphysics.avatar_inference import game, level

FILENAME = "examples.gridphysics.avatar_inference"

class TestExperienceReplay(unittest.TestCase):

	def setUp(self):
		self.agent = Agent('full', FILENAME)

		self.theory = Theory()

	def testCase(self):
		self.assertTrue(False)


if __name__ == '__main__':
    unittest.main()