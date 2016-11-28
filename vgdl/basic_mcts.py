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

class Basic_MCTS:
	def __init__(self, rleCreateFunc, obsType, num_workers):
		# assumption: not starting on terminal state
		"""
		root = the root node of the MCTS tree 
		actions = the list of actions that could be taken
		treePolicy = the policy used to select the descendant node to expand 
		             in the selection step
		defaultPolicy = the policy used in the simulation step.
		"""
		self.rleCreateFunc = rleCreateFunc
		self.obsType = obsType
		rle = self.rleCreateFunc(OBSERVATION_GLOBAL) # WARNING: do NOT use this right now.
		# always compute using a separate rle. This is only meant to be used for manhattan distance.
		self._obstypes = rle._obstypes
		self.outdim = rle.outdim
		self.root = MCTS_node(rle._getSensors(None), False, rle._actionset)
		self.actions = rle._actionset
		self.currentNode = self.root
		self.defaultTime = 0
		self.treeTime = 0
		self.num_workers = num_workers

	def getManhattanDistanceComponents(self, node):
		"""
		expect avatar to be called 'avatar' in class section of theory
		expect goal to be called 'goal' in class section of theory
		currently expects the state observation to follow a grid string format (orignal default format)
		"""
		reshaped_state = np.reshape(node.state, self.outdim)
		# np_state = np.array([[j for j in i.split('\t')] for i in node.state.splitlines()])
		avatar = 1
		# avatar = 2**(1+sorted(rle._obstypes.keys())[::-1].index("avatar"))
		goal = 2**(1+sorted(self._obstypes.keys())[::-1].index("goal"))
		# avatar_loc = np.where(reshaped_state == avatar)
		# goal_loc = np.where(reshaped_state == goal)
		avatar_loc = None
		goal_loc = None
		numRows, numCols = self.outdim
		for i in range(numRows): 
			for j in range(numCols):
				if (reshaped_state[i,j] / goal) % 2 == 1:
					goal_loc = (i,j)

				if (reshaped_state[i,j]/ avatar) % 2 == 1:
					avatar_loc = (i,j)

		try:
			return avatar_loc[0]-goal_loc[0], avatar_loc[1] - goal_loc[1]
		except TypeError:
			embed()

	def getManhattanDistance(self, node):
		"""
		expect avatar to be called 'avatar' in class section of theory
		expect goal to be called 'goal' in class section of theory
		currently expects the state observation to follow a grid string format (orignal default format)
		"""
		deltaY, deltaX = self.getManhattanDistanceComponents(node)
		return abs(deltaX) + abs(deltaY)

	def startTrainingPhase(self, numTrainingCycles):
		# apparently the reset method is inefficient
		def createRLE(q, rle_total):
			for i in range(rle_total):
				q.put(self.rleCreateFunc(OBSERVATION_GLOBAL))

		q = Queue()
		workers = []
		for i in range(self.num_workers):
			rle_total = (numTrainingCycles/self.num_workers) + (i < (numTrainingCycles % self.num_workers))
			worker = Thread(target=createRLE, args=(q, rle_total,))
			worker.setDaemon(True)
			worker.start()
			workers.append(worker)

		for i in range(numTrainingCycles):
			# rle._postInitReset()
			# rle._game.reset()
			rle = q.get()
			print "Training cycle: %i"%i

			# rle = self.rleCreateFunc(self.obsType)
			reward, vl = self.treePolicy(self.root, rle)
			if not vl.terminal:
				reward = self.defaultPolicy(vl, rle)

			self.backup(vl, reward)

		for worker in workers:
			worker.join()

	# def startTestingPhase(self, numTestingCycles):
	# 	rewardSum = 0
	# 	# for i in range(numTestingCycles):
	# 	#rle = createRLSimpleGame3(OBSERVATION_GLOBAL)
	# 	rle = self.rleCreateFunc(self.obsType)
	# 	v = self.root
	# 	Cp = 0
	# 	reward = 0
	# 	actionList = []
	# 	while not v.terminal:
	# 		a, v = self.bestChild(v,Cp)
	# 		actionList.append(a)
	# 		embed()
	# 		res = rle.step(a)
	# 		terminal = res['pcontinue']
	# 		if terminal:
	# 			reward = res['reward']

	# 	rewardSum += reward
	# 	print "finished startTestingPhase"
	# 	embed()

	# 	return rewardSum

	def getBestActionsForPlayout(self):
		v = self.root
		actions = []
		while not v.terminal:
			a, v = self.bestChild(v,0)
			actions.append(a)
			# res = rle.step(a)
			# terminal = not res['pcontinue']
			# if terminal:
			# 	reward = res['reward']

		return actions


	def treePolicy(self, v, rle):
		count = 0
		while not v.terminal:
			self.treeTime += 1
			count += 1
			if not v.expanded:
				reward, c = self.expand(v, rle)
				# rle.step(a)
				return reward, c

			else:
				Cp = 0.70710 # suggested exploration weight
				a, v = self.bestChild(v,Cp) 
				res = rle.step(a)
				terminal = not res['pcontinue']
				if terminal:
					reward = res['reward']
					return reward, v


	def expand(self,v, rle):
		expand_action = None
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

				child = MCTS_node(new_state, terminal, rle._actionset, parent = v)
				v.createChild(a,child)
				break

		return reward, child

	def bestChild(self, v, Cp):
		def transform(x):
			# return 1./x
			coefficient = 7.
			slowdown_factor = 1./3
			return coefficient/(1+math.exp(-slowdown_factor * x)) # sigmoid

		maxFuncVal = -float('inf')
		bestChild = None
		bestAction = None
		for a,c in v.children.items():
			# embed()
			if v.equals(c):
				funcVal = -float('inf')
			elif c.visitCount == 0:
				funcVal = float('inf')
			else:
				if c.terminal:
					deltaY, deltaX = self.getManhattanDistanceComponents(v)
					manhattanDistance = abs(deltaX + a[0]) + abs(deltaY + a[1])
					if manhattanDistance:
						manhattanDistanceTransform = transform(manhattanDistance)
						funcVal = float(c.qVal)/c.visitCount + Cp * math.sqrt(2*math.log(v.visitCount)/c.visitCount) + float(manhattanDistanceTransform)/c.visitCount

					else:
						funcVal = float('inf')

				else:
					manhattanDistanceTransform = transform(self.getManhattanDistance(c))
					funcVal = float(c.qVal)/c.visitCount + Cp * math.sqrt(2*math.log(c.visitCount)/v.visitCount) + float(manhattanDistanceTransform)/c.visitCount

			if funcVal > maxFuncVal:
				maxFuncVal = funcVal
				bestAction = a
				bestChild = c

		return bestAction, bestChild

	def defaultPolicy(self, s, rle):
		reward = 0
		stepSize = 1 # try 13 later
		rotatedVecMap = {(0,1):(1,0), (1,0):(0,-1), (0,-1):(-1,0), (-1,0):(0,1)}
		vecDist = dict()
		temperature = 0.2
		
		while not s.terminal:
			vecDistSum = 0
			for preRotatedVec in rotatedVecMap:
				rotatedVec = rotatedVecMap[preRotatedVec]
				for i in range(stepSize):
					vec = tuple(i*np.array(preRotatedVec) + (stepSize-i)*np.array(rotatedVec))
					comps = self.getManhattanDistanceComponents(s)
					if comps:
						deltaY, deltaX = comps
					else:
						embed()
					manhattanDistance = abs(deltaX + vec[0]) + abs(deltaY + vec[1])
					vecDist[vec] = math.exp(-temperature * manhattanDistance)
					vecDistSum += vecDist[vec]

			for vec in vecDist:
				vecDist[vec] /= vecDistSum

			samples = np.random.multinomial(1, vecDist.values(), size=1)
			sample_index = np.nonzero(samples)[1][0]
			# embed()
			sample = vecDist.keys()[sample_index]
			# embed()
			# print vecDist, samples, sample_index, sample
			# sample = np.random.choice(vecDist.keys(), 1, vecDist.values())[0]
			# embed()
			a = sample

			# actionList = []
			# for i in range(stepSize):
			# 	if s.terminal:
			# 		break

			# 	if xMagnitude == 0:
			# 		xPick = False
			# 	elif yMagnitude == 0:
			# 		xPick = True
			# 	else:
			# 		xPick = random.random() > float(xMagnitude)/(xMagnitude + yMagnitude)

			# 	if xPick:
			# 		xMagnitude -= 1
			# 		a = xUnitVec

			# 	else:
			# 		yMagnitude -= 1
			# 		a = yUnitVec

				# a = self.actions[random.randint(0,len(self.actions)-1)] # COMMENT OUT
			res = rle.step(a)
			new_state = res["observation"]
			terminal = not res['pcontinue']
			if terminal:
				reward = res['reward']

			s_new = MCTS_node(new_state,terminal, rle._actionset, parent = s)
			# s.createChild(a,s_new)

			s = s_new
			self.defaultTime += 1
			# actionList.append(a)

			# embed()
			# stepSize = (stepSize + 1)/2

		return reward

	# def defaultPolicy(self, s):
	# 	reward = 0
	# 	stepSize = 13
	# 	rotatedVecMap = {(0,1):(1,0), (1,0):(0,-1), (0,-1):(-1,0), (-1,0):(0,1)}
	# 	vecDist = dict()
	# 	while not s.terminal:
	# 		for preRotatedVec in rotatedVecMap:
	# 			rotatedVec = rotatedVecMap[preRotatedVec]
	# 			for i in range(stepSize):
	# 				vec = tuple(i*np.array(preRotatedVec) + (stepSize-i)*np.array(rotatedVec))
	# 				vecDist[vec] = 0

	# 		preRotatedVec = [0,0]
	# 		preRotatedVec[random.randint(0,1)] = 2*random.randint(0,1)-1
	# 		preRotatedVec = tuple(preRotatedVec)
	# 		rotatedVec = rotatedVecMap[preRotatedVec]
	# 		preRotatedMagnitude = random.randint(0,stepSize-1)
	# 		rotatedMagnitude = stepSize - preRotatedMagnitude
	# 		preRotatedMagnitudeCopy = preRotatedMagnitude
	# 		rotatedMagnitudeCopy = rotatedMagnitude
	# 		# xUnitVec = (2*random.randint(0,1)-1, 0)
	# 		# yUnitVec = (0, 2*random.randint(0,1)-1)
	# 		# xMagnitude = random.randint(0,stepSize)
	# 		# yMagnitude = stepSize - xMagnitude
	# 		# xMagnitudeCopy = xMagnitude
	# 		# yMagnitudeCopy = yMagnitude
	# 		actionList = []
	# 		for i in range(stepSize):
	# 			if s.terminal:
	# 				break

	# 			if rotatedMagnitude == 0:
	# 				rotatedPick = False
	# 			elif preRotatedMagnitude == 0:
	# 				rotatedPick = True
	# 			else:
	# 				rotatedPick = random.random() > float(rotatedMagnitude)/(rotatedMagnitude + preRotatedMagnitude)

	# 			if rotatedPick:
	# 				rotatedMagnitude -= 1
	# 				a = rotatedVec

	# 			else:
	# 				preRotatedMagnitude -= 1
	# 				a = preRotatedVec

	# 			# a = self.actions[random.randint(0,len(self.actions)-1)] # COMMENT OUT
	# 			res = rle.step(a)
	# 			new_state = res["observation"]
	# 			terminal = not res['pcontinue']
	# 			if terminal:
	# 				reward = res['reward']

	# 			s_new = MCTS_node(new_state,terminal, rle._actionset, parent = s)
	# 			s.createChild(a,s_new)

	# 			s = s_new
	# 			self.defaultTime += 1
	# 			actionList.append(a)

	# 		# embed()
	# 		stepSize = (stepSize + 1)/2

	# 	return reward

	def backup(self, v,reward):
		"""reward = 1 if win, -1 if loss"""
		while v:
			v.backProp(reward)
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



if __name__ == "__main__":
	obsType = OBSERVATION_GLOBAL
	# self.rleCreateFunc = createRLSimpleGame4
	rleCreateFunc = createRLSimpleGame_missile
	mcts = Basic_MCTS(rleCreateFunc, obsType, 3)
	mcts.startTrainingPhase(5000)
	# from vgdl.playback import VGDLParser
	from vgdl.core import VGDLParser
	from examples.gridphysics.simpleGame_missile import box_level, push_game
	game = push_game
	level = box_level
	embed()
	# VGDLParser.playGame(game, level)
	VGDLParser.playGame(game, level,mcts.getBestActionsForPlayout())
	# VGDLPlaybackParser.playGame(game, level, mcts.getBestActionsForPlayout())  

	# rewardSum = mcts.startTestingPhase(50)

