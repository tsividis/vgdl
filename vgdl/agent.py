from basic_mcts_domain import *
from core import colorDict
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
	print outlist
	return outlist


if __name__ == "__main__":

	obsType = OBSERVATION_GLOBAL
	thinking_steps = 50
	thinking_default_steps=50
	##REAL WORLD
	rleCreateFunc = createRLSimpleGame4
	rle = rleCreateFunc(OBSERVATION_GLOBAL)
	all_objects = rle._game.getObjects() ##this will be problematic when new objects appear, if you don't update it.
	outdim = rle.outdim

	print np.reshape(rle._getSensors(), outdim)
	terminal = False


	eventList = []

	unknown_objects = rle._game.sprite_groups.keys()
	unknown_objects.remove('avatar') ##for now we're asumming agent knows self.


	goals = ['box1', 'box2']
	theories = [createRLVirtualGame, createRLVirtualGame2]
	
	##TODO: It looks like it's planning and achieving each of the two goals.
	## The loop isn't properly made; it doesn't ned after achieving both of its goals.

	## separate outer and inner loops better.


	##Start a loop.
	# while len(unknown_objects)>0:
	for i in range(2):
	# 	## Select a goal, according to some policy. Simplest for now: sample randomly from each type.
	# 	object_goal = random.choice(unknown_objects)
		object_goal = goals[i]
		print "goal is", goals[i]
	# 	unknown_objects.remove(object_goal)
		instantiated_goal = random.choice(rle._game.sprite_groups[object_goal]) # TODO: instead, find nearest instance of that object. Not necessarily trivial becase you could mistakenly pick something that's impossible to get to.
		name, ID, color, pos = instantiated_goal.name, instantiated_goal.ID, colorDict[str(instantiated_goal.color)], (instantiated_goal.rect[0], instantiated_goal.rect[1]) ##pos is in pixels. Fix.
	## Initialize some theory
		## Includes specifying the goal you selected as the termination condition. E.g., use pos.
		## This will merely overwrite the pre-existing file.
		## Plan to achieve that goal
		##World in agent's head.
		rleVirtualFunc = theories[i]
		print rleVirtualFunc
		Vrle = rleVirtualFunc(OBSERVATION_GLOBAL)

		mcts = Basic_MCTS(1, rleVirtualFunc, obsType, 1, Vrle)
		mcts.startTrainingPhase(thinking_steps, thinking_default_steps, Vrle, test=False)
		actions = mcts.getBestActionsForPlayout()

		## we need to know whether in the virtual world the goal was achieved so that we can stop pursuing it.
		## Simplest way is as soon as you have an event that includes that object, you can move on.
		goal_achieved = False
		while not terminal and not goal_achieved:
			mcts = Basic_MCTS(1, rleVirtualFunc, obsType, 1, Vrle)
			mcts.startTrainingPhase(thinking_steps, thinking_default_steps, Vrle, test=False)
			actions = mcts.getBestActionsForPlayout()
			for j in range(len(actions)):
				if not terminal:
					res = rle.step(actions[j])
					new_state = res['observation']
					print actions[j]
					print np.reshape(new_state, outdim)
					terminal = not res['pcontinue']

					events = translateEvents(res['events'], all_objects) ##TODO: this gets object colors, not IDs.
					if events:
						eventList.append(events)
						for event in events:
							if color in event:
								print "achieved goal"
								goal_achieved = True
								break

		#amend theory
	# embed()


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