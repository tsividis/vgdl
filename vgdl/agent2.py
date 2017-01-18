from basic_mcts_domain import *
from util import *
from core import colorDict
from ontology import Immovable, Passive, Resource, ResourcePack, RandomNPC, Chaser, AStarChaser, OrientedSprite, Missile
from ontology import initializeDistribution, updateDistribution, updateOptions, sampleFromDistribution, spriteInduction, selectSubgoal
from theory_template import TimeStep, Precondition, InteractionRule, TerminationRule, TimeoutRule, SpriteCounterRule, MultiSpriteCounterRule, ruleCluster, Theory, Game, writeTheoryToTxt

'''
## helpful functions or access methods:
rle._getSensors()
rle.step((0,0)) ## will actually move the gamestate if things are moving, though.
rle._game.sprite_groups ## dict of unique object types and their positions

for the equivalents in thought world, just do mcts.rle.whatever
'''


if __name__ == "__main__":

	finalEventList = []
	obsType = OBSERVATION_GLOBAL
	thinking_steps = 50
	thinking_default_steps=50
	
	## Initialize rle the agent behaves in.
	rleCreateFunc = createRLSimpleGame4
	rle = rleCreateFunc(OBSERVATION_GLOBAL)
	rle._game.unknown_objects = rle._game.sprite_groups.keys()
	rle._game.unknown_objects.remove('avatar') 		## For now we're asumming agent knows self.
	rle.agentStatePrev = {}
	all_objects = rle._game.getObjects()

	spriteInduction(rle, step=0)					## Initialize sprite induction

	## Initialize mental theory
	sample = sampleFromDistribution(rle._game.spriteDistribution, all_objects)
	g = Game(spriteInductionResult=sample)
	t = g.buildGenericTheory(sample)
	hypotheses = [t]	

	## When you restart episodes, reset the rle.agentStatePrev. Maybe some other things, too.
	
	print ""
	print ""
	print np.reshape(rle._getSensors(), rle.outdim)

	## Temporary hack -- change as soon as we can write theory files.
	# theories = [createRLVirtualGame, createRLVirtualGame2]
	goals = ['box1', 'box2']
	for i in range(2):
		
		# subgoal = selectSubgoal(rle, method='preselected')
		print i

		subgoal = random.choice(rle._game.sprite_groups[goals[i]])
		pos = rle._rect2pos(subgoal.rect)
		print pos

		game, level = writeTheoryToTxt(rle,hypotheses[0], "./examples/gridphysics/theorytest.py", rle._rect2pos(subgoal.rect))
		
		Vrle = createMindEnv(game, level, OBSERVATION_GLOBAL)	##World in agent's head.
		
		## Plan to achieve that goal
		rle, hypotheses, finalEventList = getToSubgoal(rle, Vrle, subgoal, all_objects, finalEventList, sample)

		print ""

	# embed()

