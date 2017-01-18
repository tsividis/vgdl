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

def playEpisode(rleCreateFunc=createRLSimpleGame4, hypotheses=[]):
	## Initialize rle the agent behaves in.

	rle = rleCreateFunc(OBSERVATION_GLOBAL)
	rle._game.unknown_objects = rle._game.sprite_groups.keys()
	rle._game.unknown_objects.remove('avatar') 		## For now we're asumming agent knows self.
	rle.agentStatePrev = {}
	all_objects = rle._game.getObjects()
	

	spriteInduction(rle, step=0)					## Initialize sprite induction

	if len(hypotheses)==0:
		## Initialize mental theory
		sample = sampleFromDistribution(rle._game.spriteDistribution, all_objects)
		g = Game(spriteInductionResult=sample)
		t = g.buildGenericTheory(sample)
		hypotheses = [t]

	##working hypothesis is hypotheses[0] for now.
	unknown_objects= []
	for rule in hypotheses[0].interactionSet:
		##right now this only tries to learn about avatar touching things
		##not things touching things
		##Also sometimes you're going to randomly choose an unreachable object!
		if rule.generic:
			## make sure this is right if you have multiple objects in the class.
			## e.g., review induction assumptions.
			col = hypotheses[0].classes[rule.slot1][0].color
			key = [k for k in rle._game.sprite_groups.keys() if \
			colorDict[str(rle._game.sprite_groups[k][0].color)]==col][0]
			unknown_objects.append(rle._game.sprite_groups[key])
	print ""
	print ""
	print np.reshape(rle._getSensors(), rle.outdim)

	ended, won = rle._isDone()
	finalEventList = []
	while len(unknown_objects)>0 and not ended:
		object_goal = random.choice(unknown_objects)[0]
		subgoal = random.choice(rle._game.sprite_groups[object_goal.name])
		game, level = writeTheoryToTxt(rle, hypotheses[0], "./examples/gridphysics/theorytest.py", rle._rect2pos(subgoal.rect))
		Vrle = createMindEnv(game, level, OBSERVATION_GLOBAL)	##World in agent's head.
		## Plan to achieve that goal
		rle, hypotheses, finalEventList = getToSubgoal(rle, Vrle, subgoal, all_objects, finalEventList)
		ended, won = rle._isDone()

	return hypotheses, won

if __name__ == "__main__":

	finalEventList = []
	obsType = OBSERVATION_GLOBAL
	thinking_steps = 50
	thinking_default_steps=50
	
	numEpisodes = 10

	hypotheses = []
	for episode in range(numEpisodes):
		hypotheses, won = playEpisode(rleCreateFunc=createRLSimpleGame4, hypotheses=hypotheses)
		print "episode ended. Win:", won
