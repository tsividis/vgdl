import numpy as np
from numpy import zeros
import pygame    
from ontology import BASEDIRS
from core import VGDLSprite
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

#A hack to display things to the terminal conveniently.
np.core.arrayprint._line_width=150

"""
Run: python -m vgdl.basic_mcts
(from the top-level vgdl directory.)


Calling rle.step(a). Returns a dictionary with:
'reward', 'observation' and 'pcontinue': whether it was a terminal state


when you do rle.step(a), what happens to the state in other branches of the tree?

##Helps learning time to not use manhattan distance in bestchild.
## But manhattan distance is helpful for default policy.
"""

class Basic_MCTS:
	def __init__(self, decay_factor, rleCreateFunc, obsType, num_workers, existing_rle=False):
		# assumption: not starting on terminal state
		"""
		root = the root node of the MCTS tree 
		actions = the list of actions that could be taken
		treePolicy = the policy used to select the descendant node to expand 
		             in the selection step
		defaultPolicy = the policy used in the simulation step.
		"""
		self.decay_factor = decay_factor
		## Each time you call self.rleCreateFunc, it returns an rle (rl environment) to you.
		## We do this once per episode.
		self.rleCreateFunc = rleCreateFunc
		self.obsType = obsType
		## A few different ways to get observations of the game-state.
		## Observations of everything that's happening on the screen: OBSERVATION_GLOBAL
		## or just of the squares surrounding your avatar: some_other_keyword.
		if existing_rle:
			rle = existing_rle
			print "got an existing RLE. State:"
			res = rle.step((0,0)) #get first observation
			print np.reshape(res['observation'], rle.outdim)
			print "________________________________________"
			print ""
		else:
			rle = self.rleCreateFunc(OBSERVATION_GLOBAL)
		self.rle = rle
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

		## find location of goal, add to rewardDict.
		## also add neighbors of goal rewardQueue.
		##TODO: update this if goal moves!!
		goal_code = 2**(1+sorted(self._obstypes.keys())[::-1].index("goal"))
		goal_loc = np.where(np.reshape(self.rle._getSensors(), self.outdim)==goal_code)
		goal_loc = goal_loc[0][0], goal_loc[1][0]
		self.rewardDict = {goal_loc:1}
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




	# def propagateToNeighbors(self, loc, decay):

	def scanDomainForMovementOptions(self):
		##TODO: Take a state, so that you can re-perform this scan as needed and take changes into account.
		##TODO: query VGDL description for penetrable/nonpenetrable objects, add to list.
		immovables = ['wall']
		immovable_codes = [2**(1+sorted(self._obstypes.keys())[::-1].index(i)) for i in immovables]
		
		actionDict = defaultdict(list)
		neighborDict = defaultdict(list)
		action_superset = [(-1,0), (1,0), (0,-1), (0,1)] ##TODO: add (0,0) at some point, but probably not in the subsequent loop.
		
		##Take np.reshaped(state)
		board = np.reshape(self.rle._getSensors(), self.outdim)
		x,y=np.shape(board)
		for i in range(x):
			for j in range(y):
				if board[i,j] not in immovable_codes:
					for action in action_superset:
						nextPos = (i+action[0], j+action[1])
						if board[nextPos] not in immovable_codes:
							actionDict[(i,j)].append(action)
							neighborDict[(i,j)].append(nextPos)
		self.actionDict = actionDict
		self.neighborDict = neighborDict
		return


	def propagateRewards(self):
		decay = .9
		i=0
		while len(self.rewardQueue)>0:
			loc = self.rewardQueue.popleft()

			if loc not in self.processed:# self.rewardDict.keys():

				valid_neighbors = [n for n in self.neighborDict[loc] if n in self.rewardDict.keys()]
				self.rewardDict[loc] = max([self.rewardDict[n] for n in valid_neighbors]) * decay
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
		avatar_loc = np.where(reshaped_state==1)
		goal_loc = np.where(reshaped_state==goal)
		# if goal in reshaped_state and 
		dist = avatar_loc[0][0]-goal_loc[0][0], avatar_loc[1][0]-goal_loc[1][0]

		return dist


	def startTrainingPhase(self, numTrainingCycles, step_horizon, VRLE,  test=False):
		# apparently the reset method is inefficient
		# def createRLE(q, rle_total):
		# 	for i in range(rle_total):
		# 		q.put(self.rleCreateFunc(OBSERVATION_GLOBAL))

		oldTime = time.time()
		# q = Queue()
		# workers = []
		# for i in range(self.num_workers):
		# 	rle_total = (numTrainingCycles/self.num_workers) + (i < (numTrainingCycles % self.num_workers))
		# 	worker = Thread(target=createRLE, args=(q, rle_total,))
		# 	worker.setDaemon(True)
		# 	worker.start()
		# 	workers.append(worker)

		#track total iterations spent in treePolicy
		tree_policy_iters, default_policy_iters = 0, 0
		for i in range(numTrainingCycles):
			# Vrle = self.rleCreateFunc(OBSERVATION_GLOBAL)
			Vrle = copy.deepcopy(VRLE)
			res = Vrle.step((0,0))
			# print "in training phase.", np.where(res['observation']==1)
			if test:
				embed()

			if i%10==0:
				print "Training cycle: %i"%i

			reward, vl, iters = self.treePolicy(self.root, Vrle, step_horizon)
			tree_policy_iters += iters
			if not vl.terminal:
				reward, dPiters = self.defaultPolicy(vl, Vrle, step_horizon, domain_knowledge=False)
				if reward==0:
					deltaX, deltaY = self.getManhattanDistanceComponents(vl.state)
					if abs(deltaX)+abs(deltaY) == 0:
						heuristicValue = float('inf')
					else:
						loc = np.where(np.reshape(vl.state, self.outdim)==1)
						loc = loc[0][0], loc[1][0]
						heuristicValue = self.rewardDict[loc]# heuristicValue = 1./(abs(deltaX)+abs(deltaY))
					reward = heuristicValue
				default_policy_iters += dPiters
			self.backup(vl, reward)

		# for worker in workers:
		# 	worker.join()
		# print "Tree policy iters:", tree_policy_iters
		# print "Default policy iters:", default_policy_iters
		# print "Ratio:", 1.*tree_policy_iters/default_policy_iters
		# print "Total time: %f"%(time.time()-oldTime)
		outTime = time.time()-oldTime
		# print "training phase time", outTime
		return outTime

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
				terminal = not res['pcontinue']
				if terminal:
					reward = res['reward']
					# print "treePolicy", time.time()-t1
					return reward, v, iters


	def expand(self,v, rle, domain_knowledge=False):
		expan_action = None
		child = None
		reward = 0

		if domain_knowledge:
			state  = np.reshape(v.state, self.outdim)
			avatar_loc = np.where(state==1)
			avatar_loc = (avatar_loc[0][0], avatar_loc[1][0])
			# print "in", avatar_loc
			# print "choices", self.actionDict[avatar_loc]
			# print "self.actions", self.actions
			action_choices = self.actionDict[avatar_loc]
		else:
			action_choices = self.actions

		for a in action_choices:
			if a not in v.children:
				expand_action = a
				# print "expanded", a
				res = rle.step(a)
				new_state = res["observation"]
				terminal = not res['pcontinue']
				if terminal:
					reward = res['reward']

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
					# deltaY, deltaX = self.getManhattanDistanceComps(rle)
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
		# import numpy as np
		# import random
		outList = []
		numActions = 4
		actionKeys = range(4)
		## Returns shuffled list of n_samples drawn from 'actions'.
		# partition = np.random.multinomial(n_samples, np.random.dirichlet([1]*numActions,1)[0])
		partition = np.random.dirichlet([1]*numActions,1)[0]
		outList = [self.actionDict[np.random.choice(actionKeys, p=partition)] for _ in range(n_samples)]
		# for i in range(numActions):
		# 	for j in range(partition[i]):
		# 		outList.append(actions[i])
		# random.shuffle(outList)
		return outList

	def defaultPolicyB(self, s, rle, step_horizon):
		"""
		i = iteration number
		"""
		t1 = time.time()
		reward = 0
		stepSize = 1 # try 13 later
		# rotatedVecMap = {(0,1):(1,0), (1,0):(0,-1), (0,-1):(-1,0), (-1,0):(0,1)}
		# vecDist = dict()
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
		# print "end of defaultPolicy:"
		# print np.reshape(new_state, self.outdim)
		# reshaped_state = np.reshape(state, self.outdim)
		# avatar_end_loc = np.where(reshaped_state==1)
		# dist = abs(avatar_end_loc[0][0]-avatar_initial_loc[0][0]) + abs(avatar_end_loc[1][0]-avatar_initial_loc[1][0])
		# print "end of defaultPolicy"
		# print dist
		# print time.time()-t1
		return reward, iters

		# while not terminal and iters < step_horizon:
		# 	iters += 1
		# 	vecDistSum = 0
		# 	for preRotatedVec in rotatedVecMap:
		# 		rotatedVec = rotatedVecMap[preRotatedVec]
		# 		for i in range(stepSize):
		# 			vec = tuple(i*np.array(preRotatedVec) + (stepSize-i)*np.array(rotatedVec))
		# 			comps = self.getManhattanDistanceComponents(state) # needs to change
		# 			# comps = self.getManhattanDistanceComps(rle) # needs to change
		# 			deltaY, deltaX = comps
		# 			manhattanDistance = abs(deltaX + vec[0]) + abs(deltaY + vec[1])
		# 			vecDist[vec] = math.exp(-temperature * manhattanDistance)
		# 			vecDistSum += vecDist[vec]

		# 	for vec in vecDist:
		# 		vecDist[vec] /= vecDistSum

		# 	samples = np.random.multinomial(1, vecDist.values(), size=1)
		# 	sample_index = np.nonzero(samples)[1][0]
		# 	sample = vecDist.keys()[sample_index]
			
		# 	sample = random.choice([(-1,0), (1,0), (0,-1), (0,1)])


		# 	a = sample

		# 	res = rle.step(a)
		# 	new_state = res["observation"]
		# 	state = new_state
		# 	terminal = not res['pcontinue']
		# 	reward += g*res['reward']
		# 	g *= self.decay_factor

		# 	self.defaultTime += 1 # useless right now.

		# 	print "end of defaultPolicy:"
		# 	print np.reshape(new_state, self.outdim)
		# 	return reward, iters

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
		avatar_initial_loc = np.where(reshaped_state==1)

		avatar_loc = (avatar_initial_loc[0][0], avatar_initial_loc[1][0])
		while not terminal and iters < step_horizon:

			reshaped_state = np.reshape(state, self.outdim)
			avatar_loc = np.where(reshaped_state==1)
			avatar_loc = (avatar_loc[0][0], avatar_loc[1][0])

			iters += 1


			# vecDistSum = 0
			# for preRotatedVec in rotatedVecMap:
			# 	rotatedVec = rotatedVecMap[preRotatedVec]
			# 	for i in range(stepSize):
			# 		vec = tuple(i*np.array(preRotatedVec) + (stepSize-i)*np.array(rotatedVec))
			# 		comps = self.getManhattanDistanceComponents(state) # needs to change
			# 		# comps = self.getManhattanDistanceComps(rle) # needs to change
			# 		deltaY, deltaX = comps
			# 		manhattanDistance = abs(deltaX + vec[0]) + abs(deltaY + vec[1])
			# 		vecDist[vec] = math.exp(-temperature * manhattanDistance)
			# 		vecDistSum += vecDist[vec]

			# for vec in vecDist:
			# 	vecDist[vec] /= vecDistSum

			# samples = np.random.multinomial(1, vecDist.values(), size=1)
			# sample_index = np.nonzero(samples)[1][0]
			# sample = vecDist.keys()[sample_index]
			
			# sample = random.choice([(-1,0), (1,0), (0,-1), (0,1)])

			# print "sample", sample
			# print vecDist

			# print vecDist, samples, sample_index, sample
			# sample = np.random.choice(vecDist.keys(), 1, vecDist.values())[0]
			
			if domain_knowledge:
				sample = random.choice(self.actionDict[avatar_loc])
			else:
				sample = random.choice([(-1,0), (1,0), (0,-1), (0,1)])
			
			a = sample

				# a = self.actions[random.randint(0,len(self.actions)-1)] # COMMENT OUT
			res = rle.step(a)
			new_state = res["observation"]
			state = new_state
			terminal = not res['pcontinue']
			reward += g*res['reward']
			g *= self.decay_factor


			# if terminal:
			# 	reward = res['reward']

			# s_new = MCTS_node(new_state,terminal, rle._actionset, parent = s)
			# s.createChild(a,s_new)

			# s = s_new
			self.defaultTime += 1 # useless right now.
			# actionList.append(a)

			# embed()
			# stepSize = (stepSize + 1)/2
		# print reward, vecDist[sample], iters
		# if reward == 0:
		# 	deltaX, deltaY = self.getManhattanDistanceComponents(state)
		# 	heuristicValue = abs(deltaX) + abs(deltaY)

		# 	print deltaX, deltaY, 1./heuristicValue
		# 	return 1./heuristicValue, iters
		# # 	return .5*vecDist[sample], iters
		# else:
		reshaped_state = np.reshape(state, self.outdim)
		avatar_end_loc = np.where(reshaped_state==1)
		# dist = abs(avatar_end_loc[0][0]-avatar_initial_loc[0][0]) + abs(avatar_end_loc[1][0]-avatar_initial_loc[1][0])
		# print "end of defaultPolicy:"
		# print dist
		# print np.reshape(new_state, self.outdim)
		# print "defaultpolicy", time.time()-t1
		return reward, iters
		# return reward+vecDist[sample], iters

	def backup(self, v,reward):
		"""reward = 1 if win, -1 if loss"""
		while v:
			v.backProp(reward)
			reward *= self.decay_factor
			v = v.parent

# class Reward_node:
# 	def __init__(self, tree, loc, neighbors):


##initialize self.rewardDict[goal_loc] = 1.

# 		for n in self.neighbors:
# 			if n not in self.tree.rewardQueue:
# 				self.tree.append(n)


		## start at goal state
		## append neighbors to list

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
		    	# if len(self.children) == len(self.tree.actionDict[avatar_loc]):
		    	# self.expanded = True
		    # if len(self.children) == len(self.actions):


	def getReward(self):
		if self.visitCount > 0:
			return float(self.qVal)/self.visitCount

		else:
			return -1

def planActLoop(max_actions_per_plan, planning_steps, defaultPolicyMaxSteps, playback=False):
	obsType = OBSERVATION_GLOBAL
	rleCreateFunc = createRLSimpleGame5
	rle = rleCreateFunc(OBSERVATION_GLOBAL)

	outdim = rle.outdim

	res = rle.step((0,0)) #get first observation
	# print np.reshape(res['observation'], outdim)
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
			# print "cycle", i, "action", j
			if actions[j] is not None and not terminal:
				# reshaped_state = np.reshape(new_state, mcts.outdim)
				# avatar = 1
				# goal = 2**(1+sorted(mcts._obstypes.keys())[::-1].index("goal"))
				# avatar_loc = np.where(reshaped_state==1)
				# goal_loc = np.where(reshaped_state==goal)
				# print "avatar, goal", avatar_loc, goal_loc
				dist = mcts.getManhattanDistanceComponents(new_state)
				# print ""
				# print 'dist', dist
				print 'action', actions[j]
				res = rle.step(actions[j])
				new_state = res["observation"]
				terminal = not res['pcontinue']
				print np.reshape(new_state, mcts.outdim)
				finalActions.append(actions[j])

		i+=1
	if playback:
		from vgdl.core import VGDLParser
		from examples.gridphysics.simpleGame5 import box_level, push_game
		game = push_game
		level = box_level
		VGDLParser.playGame(game, level, finalActions)

	return finalActions

if __name__ == "__main__":
	## passing a function. That function contains things set in
	## 'rlenvironmentnonstatic' file
	## You have to make a function that creates the environment.
	## Make the game, then follow the layout in 'rlenvironmentnonstatic'
	
	# obsType = OBSERVATION_GLOBAL
	# rleCreateFunc = createRLSimpleGame5
	# mcts = Basic_MCTS(1, rleCreateFunc, obsType, 1)

	# outTime = mcts.startTrainingPhase(100, 100, test=False)
	# print outTime
	# distance = mcts.debug(mcts.rle)[2]
	embed()


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

