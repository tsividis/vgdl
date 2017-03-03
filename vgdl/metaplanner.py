
from mcts import *
from qlearner import *
from aStar import *


def translateEvents(events, all_objects):
	if events is None:
		return None
	# all_objects = rle._game.getObjects()

	def getObjectColor(objectID):
		return all_objects[objectID]['type']['color']

	outlist = []
	for event in events:
		if len(event) > 3:
			tmp = [event[0], getObjectColor(event[1]), getObjectColor(event[2])]
			tmp.extend(event[3:])
			outlist.append(tuple(tmp))
		if len(event)==3:
			outlist.append((event[0], getObjectColor(event[1]), getObjectColor(event[2])))
		elif len(event)==2:
			outlist.append((event[0], getObjectColor(event[1])))
	
	if len(outlist)>0:
		print outlist
	return list(set(outlist)) # make sure effects in timeStep are unique.


def observe(rle, obsSteps):
	print "observing"
	for i in range(obsSteps):
		spriteInduction(rle._game, step=1)
		spriteInduction(rle._game, step=2)
		rle.step((0,0))
		spriteInduction(rle._game, step=3)
	return


def planActLoop(rleCreateFunc, filename, max_actions_per_plan, planning_steps, defaultPolicyMaxSteps, playback=False):
	
	rle = rleCreateFunc(OBSERVATION_GLOBAL)
	game, level = defInputGame(filename)
	outdim = rle.outdim
	print rle.show()
	
	terminal = rle._isDone()[0]
	
	i=0
	finalStates = [rle._game.getFullState()]
	while not terminal:
		mcts = Basic_MCTS(existing_rle=rle, game=game, level=level)
		mcts.startTrainingPhase(planning_steps, defaultPolicyMaxSteps, rle)
		# mcts.debug(mcts.rle, output=True, numActions=3)
		# break
		actions = mcts.getBestActionsForPlayout()

		# if len(actions)<max_actions_per_plan:
		# 	print "We only computed", len(actions), "actions."

		new_state = rle._getSensors()
		terminal = rle._isDone()[0]

		for j in range(min(len(actions), max_actions_per_plan)):
			if actions[j] is not None and not terminal:
				print ACTIONS[actions[j]]
				res = rle.step(actions[j])
				new_state = res["observation"]
				terminal = not res['pcontinue']
				print rle.show()
				finalStates.append(rle._game.getFullState())

		i+=1

	if playback:
		from vgdl.core import VGDLParser
		VGDLParser.playGame(game, level, finalStates)
		embed()


def planUntilSolved(rleCreateFunc, filename, defaultPolicyMaxSteps, partitionWeights, playback=False, maxEpisodes=700):
	
	rle = rleCreateFunc(OBSERVATION_GLOBAL)
	game, level = defInputGame(filename)
	outdim = rle.outdim
	symbolDict = generateSymbolDict(rle)
	print rle.show()

	goal_loc = np.where(np.reshape(rle._getSensors(), rle.outdim)==8)
	goal_loc = goal_loc[0][0], goal_loc[1][0]
	terminal = rle._isDone()[0]
	
	i=0
	finalStates = [rle._game.getFullState()]
	## Have to make this as a theory and then write it, so that you can find what the immovables are
	## then these can get incorporated when you look for subgoals.
	theory = generateTheoryFromGame(rle)
	# theory.display()
	theoryString, levelString, inverseMapping, immovables =\
	writeTheoryToTxt(rle, theory, symbolDict, "./examples/gridphysics/whatever.py", goal_loc)

	rle = createMindEnv(theoryString, levelString, output=False)
	rle.immovables = immovables

	mcts = Basic_MCTS(existing_rle=rle, game=game, level=level, partitionWeights=[5,2,3])
	subgoals = mcts.getSubgoals(subgoal_path_threshold=3)
	print "subgoals", subgoals

	
	total_steps = 0
	solved = True
	numActions = 0
	for subgoal in subgoals:
		rle, actions, steps = getToWaypoint(rle, subgoal, symbolDict, defaultPolicyMaxSteps, partitionWeights=[10,2,4])
		numActions += len(actions)
		print steps, "steps"
		total_steps += steps
		if total_steps > maxEpisodes:
			solved = False
			break

	if solved:
		print "Found and executed plan using", total_steps, "epiosodes of MCTS."
	else:
		print "didn't solve game even using %i episodes of MCTS"%total_steps

	return mcts, total_steps, solved, numActions

def parallelizedPlanUntilSolved(rleCreateFunc, filename, defaultPolicyMaxSteps, partitionWeightsList, numWorkers=4):
	"""
	partitionWeightsList = a list of partitionWeight tuples.
	numWorkers = the number of threads which are running planUntilSolved in parallel
	"""
	# m = multiprocessing.Manager()
	weightsQueue = multiprocessing.Queue()
	# contract: the weightsQueue will contain all the partition weights in the beginning
	# and a numWorkers number of DONE_MESSAGEs at the very end
	# to enssure each of the workers stops running.
	resultsQueue = multiprocessing.Queue()
	weightInfo = dict()
	DONE_MESSAGE = "DONE"
	def worker(weightsQue, resultsQue, DONE_MESSAGE):
		i = 0
		while not weightsQue.empty():
			message = weightsQue.get()
			if message == DONE_MESSAGE:
				break

			partitionWeights = message
			mcts, total_steps, solved, numActions = planUntilSolved(rleCreateFunc, filename, defaultPolicyMaxSteps, partitionWeights)
			resultsQueue.put((partitionWeights, {'total_steps': total_steps, 'solved': solved, 'numActions': numActions}))


	jobs = []
	for partitionWeights in partitionWeightsList:
		weightsQueue.put(partitionWeights)


	for i in range(numWorkers):
		weightsQueue.put(DONE_MESSAGE)
		p = multiprocessing.Process(target=worker, args=(weightsQueue, resultsQueue, DONE_MESSAGE))
		jobs.append(p)
		p.start()

	for j in jobs:
		j.join()

	while not resultsQueue.empty():
		(partitionWeights, result) = resultsQueue.get()
		weightInfo[partitionWeights] = result

	return weightInfo

# if __name__ == "__main__":
# 	## passing a function. That function contains things set in
# 	## 'rlenvironmentnonstatic' file
# 	## You have to make a function that creates the environment.
# 	## Make the game, then follow the layout in 'rlenvironmentnonstatic'
	
# 	filename = "examples.gridphysics.simpleGame4"
# 	game_to_play = lambda obsType: createRLInputGame(filename)
# 	# planUntilSolved(game_to_play, filename, 50, [5,1,5])
# 	# partitionWeightsList = [(5,1,5), (5,3,3)]
# 	# partitionWeightsList = [(5,1,5)]
# 	partitionWeightsList = [(5,1,5),(5,3,3), (5,3,1), (5,1,3), (3,1,5), (3,5,1), (1,3,5), (5,5,1), (1,5,3)]
# 	weightInfoList = []
# 	totalWeightInfo = {k: {'solved': 0, 'total_steps': 0, 'numActions': 0} for k in partitionWeightsList}
# 	numIters = 5
# 	for i in range(numIters):
# 		weightInfo = parallelizedPlanUntilSolved(game_to_play, filename, 50, partitionWeightsList, numWorkers=4)
# 		weightInfoList.append(weightInfo)
# 		for k in totalWeightInfo:
# 			totalWeightInfo[k]['solved'] = totalWeightInfo[k]['solved'] + (weightInfo[k]['solved']/float(numIters))
# 			totalWeightInfo[k]['total_steps'] += weightInfo[k]['total_steps']/float(numIters)
# 			if weightInfo[k]['solved']:
# 				totalWeightInfo[k]['numActions'] += weightInfo[k]['numActions']

# 	for k in totalWeightInfo:
# 		totalWeightInfo[k]['numActions'] /= float(totalWeightInfo['solved'])

# 	embed()

def getToWaypoint(rle, subgoal, plannerType, symbolDict, defaultPolicyMaxSteps, partitionWeights, act=True):

	theory = generateTheoryFromGame(rle)


	theoryString, levelString, inverseMapping, immovables =\
	writeTheoryToTxt(rle, theory, symbolDict, "./examples/gridphysics/waypointtheory.py", subgoal)
	Vrle = createMindEnv(theoryString, levelString, output=False)
	Vrle.immovables = immovables

	print "mental map with subgoal", subgoal
	print Vrle.show()
	print "planner type", plannerType
	if plannerType=='mcts':
		mcts = Basic_MCTS(existing_rle=Vrle, game=theoryString, level=levelString, partitionWeights=partitionWeights)
		# print "made mcts for subgoal,", subgoal
		# embed()
		m, steps = mcts.startTrainingPhase(1200, defaultPolicyMaxSteps, Vrle, mark_solution=True, solution_limit=20)
		actions = mcts.getBestActionsForPlayout((1,0,0), debug=False)
	elif plannerType=='QLearning':
		planner = QLearner(Vrle, gameString=theoryString, levelString=levelString)
		steps = planner.learn(300, satisfice=True)
		actions = planner.getBestActionsForPlayout()
	print "Found plan to subgoal. Actions", actions
	if act:
		for a in actions:
			rle.step(a)
			print rle.show()
	return rle, actions, steps

def objectGoalReached(effects, object_goal):
	## Check if you reached object goal
	goal_achieved = False
	for e in effects:
		if 'DARKBLUE' in e and colorDict[str(object_goal.color)] in e:
			print "goal achieved"
			goal_achieved = True
			break
	return goal_achieved

def updateCandidateColors(hypotheses, finalEventList):

	## new colors that we have maybe learned about
	candidate_new_objs, candidate_new_colors = [], []

	for interaction in hypotheses[0].interactionSet:
		if not interaction.generic:
			if interaction.slot1 != 'avatar':
				candidate_new_objs.append(interaction.slot1)
			if interaction.slot2 != 'avatar':
				candidate_new_objs.append(interaction.slot2)
	candidate_new_objs = list(set(candidate_new_objs))
	for o in candidate_new_objs:
		cols = [c.color for c in hypotheses[0].classes[o]]
		candidate_new_colors.extend(cols)

	## among the many things to fix:

	for e in finalEventList[-1]['effectList']:
		if e[1] == 'DARKBLUE':
			candidate_new_colors.append(e[2])
			# print "appending", e[2], "to candidate_new_colors"
		if e[2] == 'DARKBLUE':
			candidate_new_colors.append(e[1])
			# print "appending", e[1], "to candidate_new_colors"

	candidate_new_colors = list(set(candidate_new_colors))

	return candidate_new_colors

def getToObjectGoal(rle, vrle, plannerType, game_object, hypothesis, game, level, object_goal, all_objects, finalEventList, verbose=True,\
	defaultPolicyMaxSteps=50, symbolDict=None):
	## Takes a real world, a theory (instantiated as a virtual world)
	## Moves the agent through the world, updating the theory as needed
	## Ends when object_goal is reached.
	## Returns real world in its new state, as well as theory in its new state.
	## TODO: also return a trace of events and of game states for re-creation
	
	hypotheses = []
	terminal = rle._isDone()[0]
	goal_achieved = False
	outdim = rle.outdim
	candidate_new_colors = []

	def noise(action):
		prob=0.
		if random.random()<prob:
			return random.choice(BASEDIRS)
		else:
			return action

	## Add newly-seen objects.
	## TODO: This still doesn't let you add objects in the middle of an episode.
	current_objects = rle._game.getObjects()
	for k in current_objects.keys():
		if k not in all_objects.keys():
			all_objects[k] = current_objects[k]

	states_encountered = [rle._game.getFullState()]
	hypotheses = [hypothesis]
	while not terminal and not goal_achieved:

		theory_change_flag = False

		if not theory_change_flag: 
			if plannerType=='mcts':
				planner = Basic_MCTS(existing_rle=vrle, game=game, level=level, partitionWeights=[5,3,3])
				subgoals = planner.getSubgoals(subgoal_path_threshold=3)
			elif plannerType=='QLearning':
				planner = QLearner(vrle, gameString=game, levelString=level)
				subgoals = planner.getSubgoals(subgoal_path_threshold=10)
			
			print "subgoals", subgoals
			## if you can't find subgoals that get you to the goal, exit
			if len(subgoals)==0:
				return rle, hypotheses, finalEventList, candidate_new_colors, states_encountered, game_object
			total_steps = 0
			
			for subgoal in subgoals:
				if not theory_change_flag and not goal_achieved:

					## write subgoal to theory; initialize VRLE.
					game, level, symbolDict, immovables = writeTheoryToTxt(rle, hypotheses[0], symbolDict, \
						"./examples/gridphysics/theorytest.py", subgoal)
					vrle = createMindEnv(game, level, output=False)
					vrle.immovables = immovables

					## Get actions that take you to goal.
					ignore, actions, steps = getToWaypoint(vrle, subgoal, plannerType, symbolDict, defaultPolicyMaxSteps, partitionWeights=[5,3,3], act=False)

					## Sometimes you can have a theory under which you can't get to a goal!
					## i.e., if you think that the objects around you will kill you (even though they won't in real life)
					## In this, take a random action.
					if len(actions)==0:
						actions = [random.choice([(1,0), (-1,0), (0,1), (0,-1)])]

					for action in actions:
						if not theory_change_flag and not goal_achieved:
							spriteInduction(rle._game, step=1)
							spriteInduction(rle._game, step=2)
							
							try:
								agentState = dict(rle._game.getAvatars()[0].resources)
								rle.agentStatePrev = agentState
							# If agent is killed before we get agentState
							except Exception as e:	# TODO: how to process changes in resources that led to termination state?
								# agentState = defaultdict(lambda: 0)
								agentState = rle.agentStatePrev
								print "didn't find agentState resources"
								embed()


							print "agentState", agentState
							res = rle.step(noise(action))
							states_encountered.append(rle._game.getFullState())
							terminal = rle._isDone()[0]				
							effects = translateEvents(res['effectList'], all_objects)
							
							k = random.choice(rle._game.spriteDistribution.keys())

							spriteInduction(rle._game, step=3)


							if symbolDict: 
								print rle.show()
							else:
								print np.reshape(new_state, rle.outdim)

					 		## If there were collisions, update history and perform interactionSet induction if the collisions were novel.
							if effects:
								state = rle._game.getFullState()
								event = {'agentState': agentState, 'agentAction': action, 'effectList': effects, 'gameState': rle._game.getFullStateColorized()}

								goal_achieved = objectGoalReached(effects, object_goal)

								## Sampling from the spriteDisribution makes sense, as it's
								## independent of what we've learned about the interactionSet.
								## Every timeStep, we should update our beliefs given what we've seen.
								sample = sampleFromDistribution(rle._game.spriteDistribution, all_objects)

								for s in sample:
									if 'Star' in str(s.vgdlType) or 'Chaser' in str(s.vgdlType):
										print "found AStar in metaplanner", s.vgdlType
										for k in rle._game.spriteDistribution.keys():
											for j in rle._game.spriteDistribution[k].keys():
												if 'Star' in str(j) or 'Chaser' in str(j):
													if rle._game.spriteDistribution[k][j] >0.1:
														print k, j
														print rle._game.spriteDistribution[k]
										embed()
								game_object = Game(spriteInductionResult=sample)


								## Get list of all effects we've seen. Only update theory if we're seeing something new.
								all_effects = [item for sublist in [e['effectList'] for e in finalEventList] for item in sublist]
								if not all([e in all_effects for e in effects]):## TODO: make sure you write this so that it works with simultaneous effects.
									finalEventList.append(event)
									terminationCondition = {'ended': False, 'win':False, 'time':rle._game.time}
									trace = ([TimeStep(e['agentAction'], e['agentState'], e['effectList'], e['gameState']) for e in finalEventList], terminationCondition)
									theory_change_flag = True
									hypotheses = list(game_object.runInduction(game_object.spriteInductionResult, trace, 20, verbose=False)) ##if you resample or run sprite induction, this 

									if len(hypotheses)>1:
										print "more than one hypothesis"
										embed()

									candidate_new_colors = updateCandidateColors(hypotheses, finalEventList)
									
									print "updating internal theory"
									# print "avatarLoc", planner.findAvatarInRLE(rle)
									## update to incorporate what we've learned, keep the same subgoal for now; this will update at the top of the next loop.
									game, level, symbolDict, immovables = writeTheoryToTxt(rle, hypotheses[0], symbolDict, \
										"./examples/gridphysics/theorytest.py", goalLoc=(rle._rect2pos(object_goal.rect)[1], rle._rect2pos(object_goal.rect)[0]))

									vrle = createMindEnv(game, level, output=True)
									vrle.immovables = immovables
									
									# If setting the new VRLE's resources fails, it's becuase there is no avatar, so don't worry about that here.
									try:
										vrle._game.getAvatars()[0].resources = rle._game.getAvatars()[0].resources
									except:
										pass

									# hypotheses[0].display()	
									# print ""													
								else:
									finalEventList.append(event)
									terminationCondition = {'ended': False, 'win':False, 'time':rle._game.time}
									trace = ([TimeStep(e['agentAction'], e['agentState'], e['effectList'], e['gameState']) for e in finalEventList], terminationCondition)
									## TODO: you need to figure out how to incorporate the result of sprite induction in cases where you don't do
									## interactionSet induction (i.e., here.)
									hypotheses = [hypothesis]

							if terminal:
								return rle, hypotheses, finalEventList, candidate_new_colors, states_encountered, game_object

					print "executed all actions."
					## If you finish all actinos, vrle needs to reflect most recent state.
					## goalLoc will be overwritten once you find new subgoals at the top.
					game, level, symbolDict, immovables = writeTheoryToTxt(rle, hypotheses[0], symbolDict, \
						"./examples/gridphysics/theorytest.py", goalLoc=(rle._rect2pos(object_goal.rect)[1], rle._rect2pos(object_goal.rect)[0]))
					vrle = createMindEnv(game, level, output=False)
					vrle.immovables = immovables
			total_steps += steps
	return rle, hypotheses, finalEventList, candidate_new_colors, states_encountered, game_object