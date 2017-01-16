from basic_mcts_domain import *
from util import *
from core import colorDict
from ontology import Immovable, Passive, Resource, ResourcePack, RandomNPC, Chaser, AStarChaser, OrientedSprite, Missile
from ontology import initializeDistribution, updateDistribution, updateOptions, sampleFromDistribution, spriteInduction, selectSubgoal
from theory_template import TimeStep, Precondition, InteractionRule, TerminationRule, TimeoutRule, SpriteCounterRule, MultiSpriteCounterRule, ruleCluster, Theory, Game

'''
## helpful functions or access methods:
rle._getSensors()
rle.step((0,0)) ## will actually move the gamestate if things are moving, though.
rle._game.sprite_groups ## dict of unique object types and their positions

for the equivalents in thought world, just do mcts.rle.whatever
'''

def translateEvents(events, all_objects):
	if events is None:
		return None
	# all_objects = rle._game.getObjects()

	def getObjectColor(objectID):
		return all_objects[objectID]['type']['color']

	outlist = []
	for event in events:
		if len(event)==3:
			outlist.append((event[0], getObjectColor(event[1]), getObjectColor(event[2])))
		elif len(event)==2:
			outlist.append((event[0], getObjectColor(event[1])))
	if len(outlist)>0:
		print outlist
	return outlist


if __name__ == "__main__":

	finalEventList = []
	agentStatePrev = {}
	obsType = OBSERVATION_GLOBAL
	thinking_steps = 50
	thinking_default_steps=50
	
	## Initialize rle the agent behaves in.
	rleCreateFunc = createRLSimpleGame4
	rle = rleCreateFunc(OBSERVATION_GLOBAL)
	rle._game.unknown_objects = rle._game.sprite_groups.keys()
	rle._game.unknown_objects.remove('avatar') ##for now we're asumming agent knows self.
	terminal = False
	outdim = rle.outdim
	## Save all objects, some of which may be killed in the game.
	## TODO: this will be problematic when new objects appear, if you don't update it.
	all_objects = rle._game.getObjects() 

	print np.reshape(rle._getSensors(), outdim)

	spriteInduction(rle, step=0)

	## Subgoal selection


	goals = ['box1', 'box2']
	## Temporary hack -- change as soon as we can write theory files.
	theories = [createRLVirtualGame, createRLVirtualGame2]
	
	## 1/15/17:
	##TODO: It looks like it's planning and achieving each of the two goals.

	## Theory swap: just have a method that updates a Theory object to reflect what you just saw.

	## But if you do that, what's the point of theory induction? You're not learning much; you're just memorizing.
	## This is actually a problem; you need to think about this.

	##Then: you have goal selection and plans to achieve those goals finished. What you need is:
	## Selected goal + theory writes to VGDL file, which you then use to initialize the Vrle.
	## any movement of objects you use to do spriteSet induction
	## any events you've observed you use to do interactionSet induction (should be easy)

	## separate outer and inner loops better.

	##Start a loop.
	# while len(unknown_objects)>0 and not terminal:
	for i in range(2):

		subgoal = selectSubgoal(rle, method='preselected')

		print "object goal is", colorDict[str(subgoal.color)], rle._rect2pos(subgoal.rect)
		
		## Initialize some theory
		## Includes specifying the goal you selected as the termination condition. E.g., use pos.
		## This will merely overwrite the pre-existing file.
		## Plan to achieve that goal
		##World in agent's head.
		rleVirtualFunc = theories[i]
		# print rleVirtualFunc
		Vrle = rleVirtualFunc(OBSERVATION_GLOBAL)

		mcts = Basic_MCTS(1, rleVirtualFunc, obsType, 1, Vrle)
		mcts.startTrainingPhase(thinking_steps, thinking_default_steps, Vrle, test=False)
		actions = mcts.getBestActionsForPlayout()

		## Simplest way is as soon as you have an event that includes that object, you can move on.
		goal_achieved = False
		while not terminal and not goal_achieved:
			mcts = Basic_MCTS(1, rleVirtualFunc, obsType, 1, Vrle)
			mcts.startTrainingPhase(thinking_steps, thinking_default_steps, Vrle, test=False)
			actions = mcts.getBestActionsForPlayout()
			for j in range(len(actions)):
				if not terminal and not goal_achieved:

					spriteInduction(rle, step=1)

					## Take actual step. RLE Updates all positions.
					res = rle.step(actions[j])
					new_state = res['observation']
					terminal = not res['pcontinue']
					effects = translateEvents(res['effectList'], all_objects) ##TODO: this gets object colors, not IDs.
					
					print actions[j]
					print np.reshape(new_state, outdim)
					## see line 815-> in core.py. That goes here.
					

					# Save the event and agent state
					try:
						agentState = dict(rle._game.getAvatars()[0].resources)
						agentStatePrev = agentState

					# If agent is killed before we get agentState
					except Exception as e:              # TODO: how to process changes in resources that led to termination state?
						agentState = agentStatePrev


					if effects:
						state = rle._game.getFullState()
						event = {'agentState': agentState, 'agentAction': actions[j], 'effectList': effects, 'gameState': rle._game.getFullStateColorized()}
						finalEventList.append(event)

						for effect in effects:
							rle._game.collision_objects.add(effect[1]) ##sometimes event is just (predicate, obj1)
							if len(effect)==3: ## usually event is (predicate, obj1, obj2)
								rle._game.collision_objects.add(effect[2])

						if subgoal.color in [item for sublist in effects for item in sublist]:
							print "achieved goal"
							goal_achieved = True
							## TODO: remove instantiated_goal object type.
							rle._game.unknown_objects.remove(subgoal.name)

						## Now do interactionSet induction

						## Sampling from the spriteDisribution makes sense, as it's
						## independent of what we've learned about the interactionSet.
						## Every timeStep, we should update our beliefs given what we've seen.
						sample = sampleFromDistribution(rle._game.spriteDistribution, all_objects)
						g = Game(spriteInductionResult=sample)
						terminationCondition = {'ended': False, 'win':False, 'time':rle._game.time}
						trace = ([TimeStep(e['agentAction'], e['agentState'], e['effectList'], e['gameState']) for e in finalEventList], terminationCondition)

						## TODO: You're re-running all of theory induction for every timestep
						## every time. Fix this.
						## if you fix it, note that you'd be passing a different g each time,
						## since you sampled (above).
						hypotheses = list(g.runDFSInduction(trace, 20, True))

					spriteInduction(rle, step=2)

		# print [e['effectList'] for e in finalEventList]
		print ""

	embed()


def planActLoop(max_actions_per_plan, planning_steps, defaultPolicyMaxSteps, playback=False):
	obsType = OBSERVATION_GLOBAL
	rleCreateFunc = createRLSimpleGame4
	rle = rleCreateFunc(OBSERVATION_GLOBAL)

	outdim = rle.outdim

	res = rle.step((0,0)) #get first observation
	print np.reshape(res['observation'], outdim)
	terminal = not res['pcontinue']
	
	i=0
	finalActions = []
	while not terminal:
		mcts = Basic_MCTS(1, rleCreateFunc, obsType, 1, rle)
		mcts.startTrainingPhase(planning_steps, defaultPolicyMaxSteps, rle, test=False)
		# mcts.debug(mcts.rle, output=True, numActions=3)
		# break
		actions = mcts.getBestActionsForPlayout()

		if len(actions)<max_actions_per_plan:
			print "We only computed", len(actions), "actions."

		res = rle.step((0,0))
		new_state = res["observation"]
		terminal = not res['pcontinue']
		for j in range(min(len(actions), max_actions_per_plan)):
			if actions[j] is not None and not terminal:
				dist = mcts.getManhattanDistanceComponents(new_state)
				print 'action', actions[j]
				res = rle.step(actions[j])
				new_state = res["observation"]
				terminal = not res['pcontinue']
				print np.reshape(new_state, mcts.outdim)
				finalActions.append(actions[j])

		i+=1
	if playback:
		from vgdl.core import VGDLParser
		from examples.gridphysics.simpleGame4 import box_level, push_game
		game = push_game
		level = box_level
		VGDLParser.playGame(game, level, finalActions)

	return finalActions