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
import time

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
			print np.reshape(res['observation'], (18,27))
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
		self.root = MCTS_node(rle._getSensors(None), False, self.actions)
		self.currentNode = self.root
		self.defaultTime = 0
		self.treeTime = 0
		self.num_workers = num_workers
		self.actionDict = {}
		##Populate dictionary for use in action-sampling in defaultPolicy. Not sampling (0,0).
		for i in range(len(rle._actionset)):
			self.actionDict[i] = rle._actionset[i]


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

	# def getManhattanDistanceComponents(self, state):
	# 	"""
	# 	expect avatar to be called 'avatar' in class section of theory
	# 	expect goal to be called 'goal' in class section of theory
	# 	currently expects the state observation to follow a grid string format (orignal default format)
	# 	"""
	# 	# oldTime = time.time()
	# 	reshaped_state = np.reshape(state, self.outdim)
	# 	# np_state = np.array([[j for j in i.split('\t')] for i in state.splitlines()])
	# 	avatar = 1
	# 	## Example: to find what ID a box would have, you'd just do ...index("box"). This is the
	# 	## Schaul function for figuring the sprite IDs.
	# 	goal = 2**(1+sorted(self._obstypes.keys())[::-1].index("goal"))
	# 	avatar_loc = None
	# 	goal_loc = None
	# 	numRows, numCols = self.outdim
	# 	for i in range(numRows): 
	# 		for j in range(numCols):
	# 			if (reshaped_state[i,j] / goal) % 2 == 1:
	# 				goal_loc = (i,j)

	# 			if (reshaped_state[i,j]/ avatar) % 2 == 1:
	# 				avatar_loc = (i,j)
	# 	dist = avatar_loc[0]-goal_loc[0], avatar_loc[1] - goal_loc[1]
	# 	# newTime = time.time()
	# 	# print newTime-oldTime
	# 	return dist


	def startTrainingPhase(self, numTrainingCycles, step_horizon, test=False):
		# apparently the reset method is inefficient
		def createRLE(q, rle_total):
			for i in range(rle_total):
				q.put(self.rleCreateFunc(OBSERVATION_GLOBAL))

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
			# rle._postInitReset()
			# rle._game.reset()
			rle = self.rleCreateFunc(OBSERVATION_GLOBAL)
			if test:
				embed()
			# rle = q.get()
			# if i%10==0:
				# print "Training cycle: %i"%i

			# rle = self.rleCreateFunc(self.obsType)
			reward, vl, iters = self.treePolicy(self.root, rle, step_horizon)
			tree_policy_iters += iters
			if not vl.terminal:
				# reward, dPiters = self.defaultPolicy(vl, rle, step_horizon - iters)
				# print ""
				# print "before defaultPolicy"
				# print np.reshape(vl.state, self.outdim)
				# print ""
				reward, dPiters = self.defaultPolicy(vl, rle, step_horizon)
				# print reward
				# print 'default policy', dPiters
				# print ""
				# print "after defaultPolicy"
				# print np.reshape(vl.state, self.outdim)
				# if reward==0:
				# 	# deltaX, deltaY = self.getManhattanDistanceComps(rle)
				# 	deltaX, deltaY = self.getManhattanDistanceComponents(vl.state)
				# 	if abs(deltaX)+abs(deltaY) == 0:
				# 		heuristicValue = float('inf')
				# 	else:
				# 		heuristicValue = 1./(abs(deltaX)+abs(deltaY))
				# 	reward = heuristicValue
				default_policy_iters += dPiters
			self.backup(vl, reward)

		# for worker in workers:
		# 	worker.join()
		# print "Tree policy iters:", tree_policy_iters
		# print "Default policy iters:", default_policy_iters
		# print "Ratio:", 1.*tree_policy_iters/default_policy_iters
		# print "Total time: %f"%(time.time()-oldTime)
		outTime = time.time()-oldTime
		# print outTime
		return outTime

	def getBestActionsForPlayout(self):
		v = self.root
		actions = []
		while v and not v.terminal:
			a, v = self.bestChild(v,0)
			# for a,c in v.children.items():

			actions.append(a)

			# bestVisitCount = 0
			# bestChild = None
			# for a,c in v.children.items():
			# 	if c.visitCount > bestVisitCount:
			# 		bestVisitCount = c.visitCount
			# 		bestAction = a
			# 		bestChild = c
			#
			# v = bestChild
			# actions.append(bestAction)
			

			# res = rle.step(a)
			# terminal = not res['pcontinue']
			# if terminal:
			# 	reward = res['reward']

		return actions

	def debug(self, rle, output=False):
		v = self.root
		if output:
			print "current state"
			print np.reshape(v.state, self.outdim)
		actions, nodes = [], []
		while v and not v.terminal:
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
		state = nodes[-2].state
		deltaX, deltaY = self.getManhattanDistanceComponents(state)
		distance = abs(deltaX)+abs(deltaY)
		return actions, nodes, distance


	def treePolicy(self, v, rle, step_horizon):
		"""
		i = iteration number
		"""
		count = 0
		iters = 0
		while not v.terminal and iters < step_horizon:
			iters += 1
			self.treeTime += 1
			count += 1
			if not v.expanded:
				reward, c = self.expand(v, rle)
				# rle.step(a)
				return reward, c, iters

			else:
				Cp = 0.70710 # suggested exploration weight
				a, v = self.bestChild(v,Cp) 
				res = rle.step(a)
				terminal = not res['pcontinue']
				if terminal:
					reward = res['reward']
					return reward, v, iters


	def expand(self,v, rle):
		expan_action = None
		child = None
		reward = 0
		for a in self.actions:
			if a not in v.children:
				expand_action = a
				res = rle.step(a)
				new_state = res["observation"]
				terminal = not res['pcontinue']
				if terminal:
					reward = res['reward']

				child = MCTS_node(new_state, terminal, self.actions, parent = v)

				v.createChild(a,child)
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

	def defaultPolicy(self, s, rle, step_horizon):
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
		avatar_initial_loc = np.where(reshaped_state==1)
		while not terminal and iters < step_horizon:
			iters += 1
			vecDistSum = 0
			for preRotatedVec in rotatedVecMap:
				rotatedVec = rotatedVecMap[preRotatedVec]
				for i in range(stepSize):
					vec = tuple(i*np.array(preRotatedVec) + (stepSize-i)*np.array(rotatedVec))
					comps = self.getManhattanDistanceComponents(state) # needs to change
					# comps = self.getManhattanDistanceComps(rle) # needs to change
					deltaY, deltaX = comps
					manhattanDistance = abs(deltaX + vec[0]) + abs(deltaY + vec[1])
					vecDist[vec] = math.exp(-temperature * manhattanDistance)
					vecDistSum += vecDist[vec]

			for vec in vecDist:
				vecDist[vec] /= vecDistSum

			samples = np.random.multinomial(1, vecDist.values(), size=1)
			sample_index = np.nonzero(samples)[1][0]
			sample = vecDist.keys()[sample_index]
			
			# sample = random.choice([(-1,0), (1,0), (0,-1), (0,1)])

			# print "sample", sample
			# print vecDist

			# print vecDist, samples, sample_index, sample
			# sample = np.random.choice(vecDist.keys(), 1, vecDist.values())[0]
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
		# print time.time()-t1, iters
		return reward, iters
		# return reward+vecDist[sample], iters

	def backup(self, v,reward):
		"""reward = 1 if win, -1 if loss"""
		while v:
			v.backProp(reward)
			reward *= self.decay_factor
			v = v.parent



class MCTS_node:
	def __init__(self,state, terminal, actions, parent=None):
		"""
		state = representation of the game state corresponding to this node
		self.children = a dictionary mapping each action to the child that results
		"""
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

	def createChild(self,action,child):
		# check the following if condition
		if action not in self.children:
		    self.children[action] = child
		    if len(self.children) == len(self.actions):
		    	self.expanded = True

	def getReward(self):
		if self.visitCount > 0:
			return float(self.qVal)/self.visitCount

		else:
			return -1

## you need a global RLE whose state you can change.
def planActLoop(max_actions_per_plan, planning_steps, defaultPolicyMaxSteps):
	obsType = OBSERVATION_GLOBAL
	rleCreateFunc = createRLSimpleGame5
	rle = rleCreateFunc(OBSERVATION_GLOBAL)

	res = rle.step((0,0)) #get first observation
	# print np.reshape(res['observation'], (18,27))
	terminal = not res['pcontinue']
	
	# for i in range(3):
	i=0
	while not terminal:
		## Warning -- won't run if end state is only one action away.
		mcts = Basic_MCTS(1, rleCreateFunc, obsType, 1, rle)
		mcts.startTrainingPhase(planning_steps, defaultPolicyMaxSteps, test=False)
		mcts.debug(mcts.rle, output=True)
		actions = mcts.getBestActionsForPlayout()
		res = rle.step((0,0))
		new_state = res["observation"]
		terminal = not res['pcontinue']
		for j in range(max_actions_per_plan):
			print "cycle", i, "action", j
			if actions[j] is not None and not terminal:
				# reshaped_state = np.reshape(new_state, mcts.outdim)
				# avatar = 1
				# goal = 2**(1+sorted(mcts._obstypes.keys())[::-1].index("goal"))
				# avatar_loc = np.where(reshaped_state==1)
				# goal_loc = np.where(reshaped_state==goal)
				# print "avatar, goal", avatar_loc, goal_loc
				dist = mcts.getManhattanDistanceComponents(new_state)
				print ""
				# print 'dist', dist
				print 'action', actions[j]
				res = rle.step(actions[j])
				new_state = res["observation"]
				terminal = not res['pcontinue']

				# print np.reshape(new_state, mcts.outdim)

		i+=1
	return

if __name__ == "__main__":
	# obsType = OBSERVATION_GLOBAL
	# self.rleCreateFunc = createRLSimpleGame4
	## passing a function. That function contains things set in
	## 'rlenvironmentnonstatic' file
	## You have to make a function that creates the environment.
	## Make the game, then follow the layout in 'rlenvironmentnonstatic'
	

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

