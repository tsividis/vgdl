import numpy as np
from numpy import zeros
import pygame    
from ontology import BASEDIRS
from core import VGDLSprite, colorDict
from stateobsnonstatic import StateObsHandlerNonStatic 
from rlenvironmentnonstatic import *
import argparse
import random
from IPython import embed
import math
from Queue import Queue
from threading import Thread
from collections import defaultdict, deque
import time
import copy
from ontology import Immovable, Passive, Resource, ResourcePack, RandomNPC, Chaser, AStarChaser, OrientedSprite, Missile
from ontology import initializeDistribution, updateDistribution, updateOptions, sampleFromDistribution, spriteInduction, selectSubgoal
from theory_template import TimeStep, Precondition, InteractionRule, TerminationRule, TimeoutRule, SpriteCounterRule, MultiSpriteCounterRule, ruleCluster, Theory, Game, writeTheoryToTxt

#A hack to display things to the terminal conveniently.
np.core.arrayprint._line_width=250

"""
Run: python -m vgdl.basic_mcts
(from the top-level vgdl directory.)

Then run: actions = planActLoop(max_actions_per_plan=10, planning_steps=100, defaultPolicyMaxSteps=50)

__

Calling rle.step(a). Returns a dictionary with:
'reward', 'observation' and 'pcontinue': whether it was a terminal state

Getting sprites:
mcts.rle._game.sprite_groups
"""

class Basic_MCTS:
	def __init__(self, existing_rle=False, rleCreateFunc=False, obsType = OBSERVATION_GLOBAL, decay_factor=1, num_workers=1):
		if not existing_rle and not rleCreateFunc:
			print "You must pass either an existing rle or an rleCreateFunc"
			return
		# assumption: not starting on terminal state
		"""
		root = the root node of the MCTS tree 
		actions = the list of actions that could be taken
		treePolicy = the policy used to select the descendant node to expand 
		             in the selection step
		defaultPolicy = the policy used in the simulation step.
		"""
		## A few different ways to get observations of the game-state.
		## Observations of everything that's happening on the screen: OBSERVATION_GLOBAL
		## or just of the squares surrounding your avatar: some_other_keyword.
		if existing_rle:
			rle = existing_rle
		else:
			rle = rleCreateFunc(OBSERVATION_GLOBAL)
		self.rleCreateFunc = rleCreateFunc
		self.rle = rle
		## Each time you call self.rleCreateFunc, it returns an rle (rl environment) to you.
		## We do this once per episode.
		self.obsType = obsType
		self.decay_factor = decay_factor

		# always compute using a separate rle. This is only meant to be used for manhattan distance.
		self._obstypes = rle._obstypes
		self.outdim = rle.outdim
		## returns a representation of the current state.
		## numpy array. Each location in the array is a different grid cell.
		## Each sprite is a unique number. Empty:0, boxes can be 1, agent: 4
		## Assignments of types:number come from the rle instead
		## Different instances of same type have same number.
		## You can have multiple sprites on same square. Number we are shown 
		## is the sum of the IDs.
		## IDs are generated such that the objects are recoverable from the sum.
		self.actions = rle._actionset + [(0,0)]
		self.root = MCTS_node(self, rle._getSensors(None), False, self.actions)
		self.currentNode = self.root
		self.defaultTime = 0
		self.treeTime = 0
		self.num_workers = num_workers
		self.neighborDict = {}
		self.rewardQueue = deque()
		self.pseudoRewardDecay = .96

		## find location of goal, add to rewardDict.
		## also add neighbors of goal rewardQueue.
		##TODO: update this if goal moves!!
		goal_code = 2**(1+sorted(self._obstypes.keys())[::-1].index("goal"))
		goal_loc = np.where(np.reshape(self.rle._getSensors(), self.outdim)==goal_code)
		goal_loc = goal_loc[0][0], goal_loc[1][0]
		if 'avatar' in self._obstypes.keys():
			inverted_avatar_loc=self._obstypes['avatar'][0]
			avatar_loc = (inverted_avatar_loc[1], inverted_avatar_loc[0])
			self.avatar_code = np.reshape(self.rle._getSensors(), self.outdim)[avatar_loc[0]][avatar_loc[1]]
		else:
			self.avatar_code = 1
		self.maxPseudoReward = 1000
		self.rewardDict = {goal_loc:self.maxPseudoReward}
		self.processed = [goal_loc]

		self.scanDomainForMovementOptions()

		self.rewardQueue.append(goal_loc)
		for n in self.neighborDict[goal_loc]:
			self.rewardQueue.append(n)
		
		self.propagateRewards()

		# self.actionDict = {}
		# ##Populate dictionary for use in action-sampling in defaultPolicy. Not sampling (0,0).
		# for i in range(len(rle._actionset)):
		# 	self.actionDict[i] = rle._actionset[i]




	# def scaleRewards(self):
	# 	## Maximum possible distance is having to navigate the entire grid. Scale with worst-case assumption
	# 	longest_path = self.rle._getSensors()[0]

	def scanDomainForMovementOptions(self):
		##TODO: Take a state, so that you can re-perform this scan as needed and take changes into account.
		##TODO: query VGDL description for penetrable/nonpenetrable objects, add to list.
		# print "in scanDomainForMovementOptions"
		immovable_codes = []
		# immovables = ['wall']
		immovables = self.rle.immovables
		# print "immovables", immovables
		for i in immovables:
			if i in self._obstypes.keys():
				immovable_codes.append(2**(1+sorted(self._obstypes.keys())[::-1].index(i)))
		# immovable_codes = [2**(1+sorted(self._obstypes.keys())[::-1].index(i)) for i in immovables]

		# if immovables:
		# 	print "inscandomain"
		# 	embed()
		actionDict = defaultdict(list)
		neighborDict = defaultdict(list)
		action_superset = [(0,0),(-1,0), (1,0), (0,-1), (0,1)] ##TODO: add (0,0) at some point, but probably not in the subsequent loop.
		
		##Take np.reshaped(state)
		board = np.reshape(self.rle._getSensors(), self.outdim)
		x,y=np.shape(board)
		for i in range(x):
			for j in range(y):
				if board[i,j] not in immovable_codes:
					for action in action_superset:
						nextPos = (i+action[0], j+action[1])
						## Don't look at positions off the board.
						if 0<=nextPos[0]<x and 0<=nextPos[1]<y:
							if board[nextPos] not in immovable_codes:
								actionDict[(i,j)].append(action)
								neighborDict[(i,j)].append(nextPos)
		self.actionDict = actionDict
		self.neighborDict = neighborDict
		return


	def propagateRewards(self):
		i=0
		while len(self.rewardQueue)>0:
			loc = self.rewardQueue.popleft()

			if loc not in self.processed:# self.rewardDict.keys():

				valid_neighbors = [n for n in self.neighborDict[loc] if n in self.rewardDict.keys()]
				self.rewardDict[loc] = max([self.rewardDict[n] for n in valid_neighbors]) * self.pseudoRewardDecay
				self.processed.append(loc)
			
				for n in self.neighborDict[loc]:
					if n not in self.processed:
						self.rewardQueue.append(n)
		return 

	def getManhattanDistance(self, state): ##used to be passed self, state
		"""
		expect avatar to be called 'avatar' in class section of theory
		expect goal to be called 'goal' in class section of theory
		currently expects the state observation to follow a grid string format (orignal default format)
		"""
		deltaY, deltaX = self.getManhattanDistanceComponents(state)
		return abs(deltaX) + abs(deltaY)

	def getManhattanDistanceComponents(self, state):
		
		reshaped_state = np.reshape(state, self.outdim)
		avatar = 1
		goal = 2**(1+sorted(self._obstypes.keys())[::-1].index("goal"))
		avatar_loc = np.where(reshaped_state==self.avatar_code)
		goal_loc = np.where(reshaped_state==goal)
		# if goal in reshaped_state and
		# print avatar_loc[0], goal_loc[0]
		if len(avatar_loc[0])>0 and len(goal_loc[0])>0:
			dist = avatar_loc[0][0]-goal_loc[0][0], avatar_loc[1][0]-goal_loc[1][0]
			return dist
		elif len(avatar_loc[0])==0 and len(goal_loc[0])>0:
			return 0,0 ##TODO: hacked on 1/18. Fix
		elif len(avatar_loc[0])>0 and len(goal_loc[0])==0:
			return 100,100
		else:
			return 0,0



	def startTrainingPhase(self, numTrainingCycles, step_horizon, VRLE,  test=False):

		oldTime = time.time()

		#track total iterations spent in treePolicy
		tree_policy_iters, default_policy_iters = 0, 0
		for i in range(numTrainingCycles):
			Vrle = copy.deepcopy(VRLE)
			if test:
				embed()

			# if i%10==0:
			# 	print "Training cycle: %i"%i

			reward, vl, iters = self.treePolicy(self.root, Vrle, step_horizon)
			tree_policy_iters += iters
			if not vl.terminal:
				reward, dPiters = self.defaultPolicy(vl, Vrle, step_horizon, domain_knowledge=True)

				loc = np.where(np.reshape(vl.state, self.outdim)==self.avatar_code)
				

				## TODO: you hacked this if-statement together to avoid a crash, but is it doing what you want?
				## e.g., do you want to just assume this means the avatar is gone and you want to give a reward of 0?
				if len(loc[0])>0:
					loc = loc[0][0], loc[1][0] 
					if loc in self.rewardDict.keys():
						reward = reward + self.rewardDict[loc]
					else:
						reward =reward
				else:
					reward = reward
				# if reward==0:
				# 	deltaX, deltaY = self.getManhattanDistanceComponents(vl.state)
				# 	if abs(deltaX)+abs(deltaY) == 0:
				# 		heuristicValue = float('inf')
				# 	else:
				# 		loc = np.where(np.reshape(vl.state, self.outdim)==1)
				# 		loc = loc[0][0], loc[1][0]
				# 		heuristicValue = self.rewardDict[loc]# heuristicValue = 1./(abs(deltaX)+abs(deltaY))
				# 	reward = heuristicValue
				default_policy_iters += dPiters
			self.backup(vl, reward)
		outTime = time.time()-oldTime
		return self

	def getBestActionsForPlayout(self):
		v = self.root
		actions = []
		while v and not v.terminal:
			a, v = self.bestChild(v,0)
			actions.append(a)
		return actions

	def debug(self, rle, output=False, numActions=1):
		cntr=0
		v = self.root
		if output:
			print "current state"
			print np.reshape(v.state, self.outdim)
		actions, nodes = [], []
		while v and not v.terminal and cntr<numActions:
			# print v.children.iteritems()
			if output:
				print "options"
				print [(k,c.qVal) for k,c in v.children.iteritems()]
			a, v = self.bestChild(v,0)
			actions.append(a)
			nodes.append(v)
			if output:
				if v:
					print "selected"
					print a
					print "resulted in"
					print np.reshape(v.state, self.outdim)
					print ""
			cntr+=1
		if v.terminal:
			distance = 0
		else:
			state = nodes[-1].state
			deltaX, deltaY = self.getManhattanDistanceComponents(state)
			distance = abs(deltaX)+abs(deltaY)
		return actions, nodes, distance


	def treePolicy(self, v, rle, step_horizon):
		"""
		i = iteration number
		"""
		t1 = time.time()
		count = 0
		iters = 0
		while not v.terminal and iters < step_horizon:
			iters += 1
			self.treeTime += 1
			count += 1
			if not v.expanded:
				reward, c = self.expand(v, rle, domain_knowledge=False)
				# print "treePolicy", time.time()-t1
				return reward, c, iters

			else:
				Cp = 0.70710 # suggested exploration weight
				a, v = self.bestChild(v,Cp) 
				res = rle.step(a)
				terminal = (not res['pcontinue']) or (rle._avatar is None)
				if terminal:
					reward = res['reward']
					if reward==1:
						reward = self.maxPseudoReward #
					# print "treePolicy", time.time()-t1
					return reward, v, iters


	def expand(self,v, rle, domain_knowledge=False):
		expan_action = None
		child = None
		reward = 0

		if domain_knowledge:
			state  = np.reshape(v.state, self.outdim)
			avatar_loc = np.where(state==self.avatar_code)
			avatar_loc = (avatar_loc[0][0], avatar_loc[1][0])
			action_choices = self.actionDict[avatar_loc]
		else:
			action_choices = self.actions

		for a in action_choices:
			if a not in v.children:
				expand_action = a
				# print "expanded", a
				res = rle.step(a)
				new_state = res["observation"]

				##Buggy code on VGDL side forces us to also check the rle.
				terminal = (not res['pcontinue']) or (rle._avatar is None)
				

				if terminal:
					reward = res['reward']
					if reward==1:
						reward = self.maxPseudoReward

				# print "in expand. terminal?", terminal
				child = MCTS_node(self, new_state, terminal, self.actions, parent = v)

				if domain_knowledge:
					v.createChild(a, child, avatar_loc, domain_knowledge)
				else:
					v.createChild(a, child)
				break

		return reward, child

	def bestChild(self, v, Cp):
		def transform(x):
			coefficient = 0.
			slowdown_factor = 1./3
			return coefficient/(1+math.exp(-slowdown_factor * x)) # sigmoid

		maxFuncVal = -float('inf')
		bestChild = None
		bestAction = None

		for a,c in v.children.items():
			if v.equals(c):
				funcVal = -float('inf')
			elif c.visitCount == 0:
				funcVal = float('inf')
			else:
				if c.terminal:
					deltaY, deltaX = self.getManhattanDistanceComponents(v.state)
					manhattanDistance = abs(deltaX + a[0]) + abs(deltaY + a[1])
					if manhattanDistance:
						manhattanDistanceTransform = transform(manhattanDistance)
						funcVal = float(c.qVal)/c.visitCount + Cp * math.sqrt(2*math.log(v.visitCount)/c.visitCount) + Cp*float(manhattanDistanceTransform)/c.visitCount

					else:
						funcVal = float('inf')
				else:
					manhattanDistanceTransform = transform(self.getManhattanDistance(c.state))
					funcVal = float(c.qVal)/c.visitCount + Cp * math.sqrt(2*math.log(v.visitCount)/c.visitCount) + Cp*float(manhattanDistanceTransform)/c.visitCount

			if funcVal > maxFuncVal:
				maxFuncVal = funcVal
				bestAction = a
				bestChild = c
		
		# if bestChild == None:# and maxFuncVal > -float('inf'): ## you need a tiebreaker
		# 	bestAction = random.choice(v.children.keys())
		# 	bestChild = v.children[bestAction]
		# 	print "maxfuncval", maxFuncVal
		# 	print "tiebreaker. Selected", bestAction
		# 	print bestChild.state

		return bestAction, bestChild

	def makeActionSet(self, n_samples):

		outList = []
		numActions = 4
		actionKeys = range(4)
		## Returns shuffled list of n_samples drawn from 'actions'.
		partition = np.random.dirichlet([1]*numActions,1)[0]
		outList = [self.actionDict[np.random.choice(actionKeys, p=partition)] for _ in range(n_samples)]
		return outList

	def defaultPolicyB(self, s, rle, step_horizon):
		"""
		Version that samples a chunk of actions.
		"""
		t1 = time.time()
		reward = 0
		stepSize = 1 # try 13 later

		temperature = 3
		terminal = False
		iters = 0
		state = s.state
		g = .5
		# reshaped_state = np.reshape(state, self.outdim)
		# avatar_initial_loc = np.where(reshaped_state==1)

		samples = self.makeActionSet(step_horizon)

		for i in range(len(samples)):
			iters += 1
			if not terminal:
				a = samples[i]
				t2 = time.time()
				res = rle.step(a)
				new_state = res["observation"]
				state = new_state
				terminal = not res['pcontinue']
				reward += g*res['reward']
				g *= self.decay_factor

				self.defaultTime += 1 # useless right now.
			else:
				break

		return reward, iters


	def defaultPolicy(self, s, rle, step_horizon, domain_knowledge=False):
		"""
		i = iteration number
		"""
		t1 = time.time()
		reward = 0
		stepSize = 1 # try 13 later
		rotatedVecMap = {(0,1):(1,0), (1,0):(0,-1), (0,-1):(-1,0), (-1,0):(0,1)}
		vecDist = dict()
		temperature = 3
		terminal = False
		iters = 0
		state = s.state
		g = .5
		reshaped_state = np.reshape(state, self.outdim)

		##TODO: can delete this if you're not calculating distances at the end of this func

		avatar_initial_loc = np.where(reshaped_state==self.avatar_code)
		if len(avatar_initial_loc[0])>0:
			avatar_loc = (avatar_initial_loc[0][0], avatar_initial_loc[1][0])
		else:
			terminal = True
		
		terminal = rle._isDone()[0]

		while not terminal and iters < step_horizon:

			reshaped_state = np.reshape(state, self.outdim)
			avatar_loc = np.where(reshaped_state==self.avatar_code, True, False)
			avatar_loc = (avatar_loc[0][0], avatar_loc[1][0])

			iters += 1
			
			if domain_knowledge:
				if avatar_loc in self.actionDict.keys():
					sample = random.choice(self.actionDict[avatar_loc])
				else:
					sample = random.choice([(-1,0), (1,0), (0,-1), (0,1)])

			else:
				sample = random.choice([(-1,0), (1,0), (0,-1), (0,1)])
			
			a = sample

			res = rle.step(a)
			new_state = res["observation"]
			state = new_state
			terminal = not res['pcontinue']
			reward += g*res['reward']
			g *= self.decay_factor

			self.defaultTime += 1 

		reshaped_state = np.reshape(state, self.outdim)
		avatar_end_loc = np.where(reshaped_state==1)

		return reward, iters
		# return reward+vecDist[sample], iters

	def backup(self, v,reward):
		"""reward = 1 if win, -1 if loss"""
		while v:
			v.backProp(reward)
			reward *= self.decay_factor
			v = v.parent


class MCTS_node:
	def __init__(self, tree, state, terminal, actions, parent=None):
		"""
		state = representation of the game state corresponding to this node
		self.children = a dictionary mapping each action to the child that results
		"""
		self.tree = tree
		self.state = state
		self.terminal = terminal # boolean
		self.actions = actions
		self.visitCount = 0
		self.qVal = 0
		self.expanded = False
		self.parent = parent # set to None if root node
		self.children = dict()
		self.exploredChildren = dict()
		self.expanded = False

	def equals(self,v):
		return np.array_equal(self.state,v.state)

	def backProp(self,win):
		"""
		win = 1 if you won 
		or win = -1 if loss
		"""
		self.qVal+= win 
		self.visitCount += 1

	def createChild(self,action,child, avatar_loc=False, domain_knowledge=False):
		# check the following if condition
		if action not in self.children:
		    self.children[action] = child
		    if domain_knowledge:
		    	self.expanded = len(self.children) == len(self.tree.actionDict[avatar_loc])
		    else:
		    	self.expanded = len(self.children) == len(self.actions)



	def getReward(self):
		if self.visitCount > 0:
			return float(self.qVal)/self.visitCount

		else:
			return -1
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

## make plan
## 


def observe(rle, obsSteps):
	print "observing"
	for i in range(obsSteps):
		spriteInduction(rle, step=1)
		rle.step((0,0))
		# print np.reshape(rle._getSensors(), rle.outdim)
		spriteInduction(rle, step=2)
	return

def getToSubgoal(rle, vrle, subgoal, all_objects, finalEventList, verbose=True, max_actions_per_plan=1, planning_steps=100, defaultPolicyMaxSteps=50):
	## Takes a real world, a theory (instantiated as a virtual world)
	## Moves the agent through the world, updating the theory as needed
	## Ends when subgoal is reached.
	## Right now will only properly work with max_actions_per_plan=1, as you want to re-plan when the theory changes.
	## Otherwise it will only replan every max_actions_per_plan steps.
	## Returns real world in its new state, as well as theory in its new state.
	## TODO: also return a trace of events and of game states for re-creation
	
	hypotheses = []
	terminal = rle._isDone()[0]
	goal_achieved = False

	def noise(action):
		prob=0.
		if random.random()<prob:
			return random.choice(BASEDIRS)
		else:
			return action

	## TODO: this will be problematic when new objects appear, if you don't update it.
	# all_objects = rle._game.getObjects()

	print ""
	print "object goal is", colorDict[str(subgoal.color)], rle._rect2pos(subgoal.rect)
	actions_executed = []
	# embed()
	while not terminal and not goal_achieved:
		# print "top of loop"
		mcts = Basic_MCTS(existing_rle=vrle)
		# embed()
		# if len(vrle.immovables)>0:
		# 	print "in gettosubgoal"
		# 	embed()
		planner = mcts.startTrainingPhase(planning_steps, defaultPolicyMaxSteps, vrle, test=False)
		# embed()
		actions = mcts.getBestActionsForPlayout()
		# print actions
		# embed()
		for i in range(len(actions)):
			if not terminal and not goal_achieved:
				spriteInduction(rle, step=1)

				## Take actual step. RLE Updates all positions.
				res = rle.step(noise(actions[i])) ##added noise for testing, but prob(noise)=0 now.
				actions_executed.append(actions[i])
				new_state = res['observation']
				terminal = rle._isDone()[0]
				effects = translateEvents(res['effectList'], all_objects) ##TODO: this gets object colors, not IDs.
				
				print actions[i]
				print np.reshape(new_state, rle.outdim)
				
				# Save the event and agent state
				try:
					agentState = dict(rle._game.getAvatars()[0].resources)
					rle.agentStatePrev = agentState
				# If agent is killed before we get agentState
				except Exception as e:	# TODO: how to process changes in resources that led to termination state?
					agentState = rle.agentStatePrev

				## If there were collisions, update history and perform interactionSet induction
				if effects:
					state = rle._game.getFullState()
					event = {'agentState': agentState, 'agentAction': actions[i], 'effectList': effects, 'gameState': rle._game.getFullStateColorized()}
					finalEventList.append(event)

					for effect in effects:
						rle._game.collision_objects.add(effect[1]) ##sometimes event is just (predicate, obj1)
						if len(effect)==3: ## usually event is (predicate, obj1, obj2)
							rle._game.collision_objects.add(effect[2])

					if colorDict[str(subgoal.color)] in [item for sublist in effects for item in sublist]:
						print "reached subgoal"
						goal_achieved = True
						if subgoal.name in rle._game.unknown_objects:
							rle._game.unknown_objects.remove(subgoal.name)
						goalLoc=None
					else:
						goalLoc = rle._rect2pos(subgoal.rect)

					## Sampling from the spriteDisribution makes sense, as it's
					## independent of what we've learned about the interactionSet.
					## Every timeStep, we should update our beliefs given what we've seen.
					# if not sample:
					sample = sampleFromDistribution(rle._game.spriteDistribution, all_objects)
					
					g = Game(spriteInductionResult=sample)
					terminationCondition = {'ended': False, 'win':False, 'time':rle._game.time}
					trace = ([TimeStep(e['agentAction'], e['agentState'], e['effectList'], e['gameState']) for e in finalEventList], terminationCondition)


					hypotheses = list(g.runInduction(sample, trace, 20))

					
					# print "in getToSubgoal"
					# embed()
					candidate_new_objs = []
					for interaction in hypotheses[0].interactionSet:
						if not interaction.generic:
							if interaction.slot1 != 'avatar':
								candidate_new_objs.append(interaction.slot1)
							if interaction.slot2 != 'avatar':
								candidate_new_objs.append(interaction.slot2)
					candidate_new_objs = list(set(candidate_new_objs))
					candidate_new_colors = []
					for o in candidate_new_objs:
						cols = [c.color for c in hypotheses[0].classes[o]]
						candidate_new_colors.extend(cols)

					## among the many things to fix:
					for e in finalEventList[-1]['effectList']:
						if e[1] == 'DARKBLUE':
							candidate_new_colors.append(e[2])
						if e[2] == 'DARKBLUE':
							candidate_new_colors.append(e[1])

					game, level, immovables = writeTheoryToTxt(rle, hypotheses[0], "./examples/gridphysics/theorytest.py", goalLoc=goalLoc)
					# all_immovables.extend(immovables)
					# print all_immovables
					vrle = createMindEnv(game, level, OBSERVATION_GLOBAL)
					vrle.immovables = immovables


					## TODO: You're re-running all of theory induction for every timestep
					## every time. Fix this.
					## if you fix it, note that you'd be passing a different g each time,
					## since you sampled (above).
					# hypotheses = list(g.runDFSInduction(trace, 20))

				spriteInduction(rle, step=2)
		if terminal:
			if rle._isDone()[1]:
				print "game won"
			else:
				print "Agent died."
	return rle, hypotheses, finalEventList, candidate_new_colors, actions_executed

def planActLoop(max_actions_per_plan, planning_steps, defaultPolicyMaxSteps, playback=False):
	obsType = OBSERVATION_GLOBAL
	rleCreateFunc = createRLSimpleGame4
	rle = rleCreateFunc(OBSERVATION_GLOBAL)

	outdim = rle.outdim

	print np.reshape(rle._getSensors(), outdim)
	
	terminal = rle._isDone()[0]

	# terminal = not res['pcontinue']
	
	i=0
	finalActions = []
	while not terminal:
		mcts = Basic_MCTS(existing_rle=rle)
		mcts.startTrainingPhase(planning_steps, defaultPolicyMaxSteps, rle, test=False)
		# mcts.debug(mcts.rle, output=True, numActions=3)
		# break
		actions = mcts.getBestActionsForPlayout()

		if len(actions)<max_actions_per_plan:
			print "We only computed", len(actions), "actions."

		new_state = rle._getSensors()
		terminal = rle._isDone()[0]

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

if __name__ == "__main__":
	## passing a function. That function contains things set in
	## 'rlenvironmentnonstatic' file
	## You have to make a function that creates the environment.
	## Make the game, then follow the layout in 'rlenvironmentnonstatic'
	
	obsType = OBSERVATION_GLOBAL
	rleCreateFunc = createRLSimpleGame4
	# rleCreateFunc = 
	rle = rleCreateFunc(obsType)
	mcts = Basic_MCTS(rleCreateFunc=rleCreateFunc)


	# embed()
	# outTime = mcts.startTrainingPhase(100, 100, test=False)
	# print outTime
	# distance = mcts.debug(mcts.rle)[2]


	# print distance



	#cycle through different parameter settings; run everything at once.
	# params = []
	# # cycles = [200]
	# # steps = [50, 100]
	# cycles = [200, 300]#, 400]
	# steps = [100, 200]#, 90, 120, 200]
	# for i in range(len(cycles)):
	# 	for j in range(len(steps)):
	# 		params.append((cycles[i], steps[j]))
	# # params = zip(cycles, steps)

	# for param in params:
	# 	distances, times = [], []
	# 	for i in range(3):
	# 		rleCreateFunc = createRLSimpleGame5
	# 		mcts = Basic_MCTS(1, rleCreateFunc, obsType, 1)
	# 		outTime = mcts.startTrainingPhase(param[0], param[1])
	# 		distance = mcts.debug(mcts.rle)[2] 
	# 		distances.append(distance)
	# 		times.append(outTime)
	# 	print ""
	# 	print "cycles:", param[0], "steps:", param[1], "avg. distance:", np.mean(distances), "avg. time", np.mean(times)


	##Uncomment for playback
	# from vgdl.core import VGDLParser
	# from examples.gridphysics.simpleGame5 import box_level, push_game
	# game = push_game
	# level = box_level
	# embed()

	# VGDLParser.playGame(game, level)

	# embed()
	# VGDLParser.playGame(game, level, mcts.getBestActionsForPlayout())
	# VGDLPlaybackParser.playGame(game, level, mcts.getBestActionsForPlayout())  

	# rewardSum = mcts.startTestingPhase(50)

