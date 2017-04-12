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
from threading import Thread
from collections import defaultdict, deque
import time
import copy
from threading import Lock
from Queue import Queue
import multiprocessing
from qlearner import *
from ontology import Immovable, Passive, Resource, ResourcePack, RandomNPC, Chaser, AStarChaser, OrientedSprite, Missile
from ontology import initializeDistribution, updateDistribution, updateOptions, sampleFromDistribution, spriteInduction, selectObjectGoal
from theory_template import TimeStep, Precondition, InteractionRule, TerminationRule, TimeoutRule, SpriteCounterRule, MultiSpriteCounterRule, \
generateSymbolDict, ruleCluster, Theory, Game, writeTheoryToTxt, generateTheoryFromGame
from rlenvironmentnonstatic import createRLInputGame

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

"""
OLETS conversion notes:
you're disabling pseudoreward propagations and have disabled reward scaling, as this was related to pseudorewards.
if you run getBestActionsForPlayout() you only really want to pick the first action.
#THEN: once you take it you should reuse that entire part of the tree.

TODO Tuesday morning:
Look at results from more recent GVG-AI competitions; is there a better algo?
Compare to java source code. Why is your implementation so bad??
"""
ACTIONS = {(0,0):'stay',(0,-1):'up', (0,1):'down', (1,0):'right', (-1,0):'left', None:'none'}

class OLETS:
	def __init__(self, existing_rle=False, game = None, level = None, partitionWeights=[1,0,1],\
		         rleCreateFunc=False, obsType = OBSERVATION_GLOBAL, decay_factor=.8, num_workers=1):
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
		subgoal_path_threshold = the max size possible for a path to a subgoal. If
					this has value None, then don't use subgoals.
		"""
		## A few different ways to get observations of the game-state.
		## Observations of everything that's happening on the screen: OBSERVATION_GLOBAL
		## or just of the squares surrounding your avatar: some_other_keyword.

		## Each time you call self.rleCreateFunc, it returns an rle (rl environment) to you.
		## We do this once per episode.
		## But if we get an existing_rle, we just use that (used for re-planning in an existing game)		
		if existing_rle:
			rle = existing_rle
		else:
			rle = rleCreateFunc(OBSERVATION_GLOBAL)
		self.rleCreateFunc = rleCreateFunc
		self.rle = rle

		self.obsType = obsType
		self.decay_factor = decay_factor
		self._obstypes = rle._obstypes
		self.outdim = rle.outdim ## ensures all self.outdim and np.reshape() calls using it are (x,y)
		self.actions = rle._actionset + [(0,0)]
		self.defaultTime = 0
		self.treeTime = 0
		self.num_workers = num_workers
		self.neighborDict = {}
		self.rewardQueue = deque()

		avatar_code = 1
		avatar_loc = np.where(np.reshape(self.rle._getSensors(), self.outdim)==avatar_code)
		avatar_loc = avatar_loc[0][0], avatar_loc[1][0] ## (y,x)

		goal_code = 2**(1+sorted(self._obstypes.keys())[::-1].index("goal"))
		goal_loc = np.where(np.reshape(self.rle._getSensors(), self.outdim)==goal_code)
		goal_loc = goal_loc[0][0], goal_loc[1][0] #(y,x)

		self.visitedLocations = defaultdict(lambda:0)

		if 'avatar' in self._obstypes.keys():
			inverted_avatar_loc=self._obstypes['avatar'][0]
			avatar_loc = (inverted_avatar_loc[1], inverted_avatar_loc[0])
			self.avatar_code = np.reshape(self.rle._getSensors(), self.outdim)[avatar_loc[0]][avatar_loc[1]]
		else:
			self.avatar_code = 1

		if game and level:
			# self.pseudoRewardDecay = 0.8
			self.maxPseudoReward = 10 #1k
			self.pseudoRewardDecay = .8
			# self.maxPseudoReward = 1/((1-self.pseudoRewardDecay)*(self.pseudoRewardDecay**len(level)))
		else:
			self.maxPseudoReward = 100 #10k
			self.pseudoRewardDecay = .6

		self.rewardScaling = 1000
		self.rewardDict = {goal_loc:self.maxPseudoReward}
		self.processed = [goal_loc]
		self.actionDict = None ## gets initialized in scanDomainForMovementOptions
		self.neighborDict = None ## gets initialized in scanDomainForMovementOptions

		self.scanDomainForMovementOptions()
		self.root = node(self, False, 0, self.actionDict[avatar_loc], .05)
		self.currentNode = self.root
		# self.propagateRewards(goal_loc)


	# def getSubgoals(self, subgoal_path_threshold):

		# avatar_code = 1
		# avatar_loc = np.where(np.reshape(self.rle._getSensors(), self.outdim)==avatar_code)
		# avatar_loc = avatar_loc[0][0], avatar_loc[1][0]
		# ## find location of goal, add to rewardDict.
		# ## also add neighbors of goal rewardQueue.
		# ##TODO: update this if goal moves!!
		# goal_code = 2**(1+sorted(self._obstypes.keys())[::-1].index("goal"))
		# killerObjectCodes = []
		# if hasattr(self.rle, 'killerObjects'):
		# 	for o in self.rle.killerObjects:
		# 		if o in self.rle._obstypes.keys():
		# 			killerObjectCodes.append(2**(1+sorted(self.rle._obstypes.keys())[::-1].index(o)))
		# board = np.reshape(self.rle._getSensors(), self.rle.outdim)
		# goal_loc = np.where(board==goal_code)
		# goal_loc = goal_loc[0][0], goal_loc[1][0]
		# self.subgoals = []
		# path = self.getPathToGoal(avatar_loc, goal_loc)
		# if subgoal_path_threshold > len(path):
		# 	# don't use any subgoals in this case.
		# 	return [goal_loc]
		# else:
		# 	subgoal_index = -1
		# 	num_subgoals = int(math.ceil(float(len(path))/subgoal_path_threshold))
		# 	for i in range(num_subgoals):
		# 		if i < len(path) % num_subgoals:
		# 			subgoal_index += (len(path)/num_subgoals + 1)
		# 		else:
		# 			subgoal_index += len(path)/num_subgoals

		# 		## Doesn't add subgoals that correspond to objects we know to be dangerous.
		# 		if board[path[subgoal_index][0]][path[subgoal_index][1]] not in killerObjectCodes:
		# 			self.subgoals.append(path[subgoal_index])
		# 		else:
		# 			for i in range(1, subgoal_path_threshold):
		# 				# print "path fell on a killer object. changing path slightly."
		# 				try:
		# 					if path[subgoal_index-i] not in killerObjectCodes:
		# 						self.subgoals.append(path[subgoal_index-i])
		# 						# print "found altered path", path[subgoal_index-i]
		# 						break
		# 					elif path[subgoal_index+i] not in killerObjectCodes:
		# 						self.subgoals.append(path[subgoal_index+i])
		# 						# print "found altered path", path[subgoal_index+i]
		# 						break
		# 				except:
		# 					print "indices didn't work out in looking for different path"

		# 		# self.subgoals.append(path[subgoal_index])
		# return self.subgoals

	def scanDomainForMovementOptions(self):
		##TODO: Take a state, so that you can re-perform this scan as needed and take changes into account.
		##TODO: query VGDL description for penetrable/nonpenetrable objects, add to list.
		immovable_codes = []
		# immovables = ['wall']
		try:
			immovables = self.rle.immovables
			# immovables = ['wall', 'poison']
			# print "immovables", immovables
		except:
			immovables = ['wall', 'poison']
			print "Using defaults as immovables", immovables

		for i in immovables:
			if i in self._obstypes.keys():
				immovable_codes.append(2**(1+sorted(self._obstypes.keys())[::-1].index(i)))

		actionDict = defaultdict(list)
		neighborDict = defaultdict(list)
		# action_superset = [(0,0),(-1,0), (1,0), (0,-1), (0,1)]
		action_superset = [(-1,0), (1,0), (0,-1), (0,1)]
		
		board = np.reshape(self.rle._getSensors(), self.outdim)
		y,x=np.shape(board)
		for i in range(y):
			for j in range(x):
				if board[i,j] not in immovable_codes:
					for action in action_superset:
						nextPos = (i+action[1], j+action[0])
						## Don't look at positions off the board.
						if 0<=nextPos[0]<y and 0<=nextPos[1]<x:
							if board[nextPos] not in immovable_codes:
								actionDict[(i,j)].append(action)
								neighborDict[(i,j)].append(nextPos)
		self.actionDict = actionDict
		self.neighborDict = neighborDict
		return

	def propagateRewards(self, goal_loc):
		self.rewardQueue.append(goal_loc)
		for n in self.neighborDict[goal_loc]:
			if n not in self.rewardQueue:
				self.rewardQueue.append(n)

		while len(self.rewardQueue)>0:
			loc = self.rewardQueue.popleft()
			if loc not in self.processed:
				valid_neighbors = [n for n in self.neighborDict[loc] if n in self.rewardDict.keys()]
				self.rewardDict[loc] = max([self.rewardDict[n] for n in valid_neighbors]) * self.pseudoRewardDecay
				self.processed.append(loc)
				for n in self.neighborDict[loc]:
					if n not in self.processed:
						self.rewardQueue.append(n)
		return

	def getPathToGoal(self, avatar_loc, goal_loc):
		q = deque()
		# q stores tuples in which the first element is a node and the next
		# is the shortest path to that node
		q.append((avatar_loc, []))
		node = avatar_loc
		path = []
		seen = {avatar_loc}
		while q:
			node, path = q.popleft()
			seen.add(node)
			if node == goal_loc:
				break

			for neighbor in self.neighborDict[node]:
				if not neighbor in seen:
					q.append((neighbor, path + [neighbor]))

		if node != goal_loc:
			raise Exception("Didn't find a path to the goal location.")

		return path

	def findAvatarInRLE(self, rle):
		avatar_code = 1
		state = np.reshape(rle._getSensors(), self.rle.outdim)
		if avatar_code in state:
			avatar_loc = np.where(state==avatar_code)
			avatar_loc = avatar_loc[0][0], avatar_loc[1][0]
		else:
			avatar_loc = None
		return avatar_loc

	def mctsSearch(self, numTrainingCycles):
		numIters = 0
		Vrle = copy.deepcopy(self.rle)
		while numIters<numTrainingCycles:
			selected, reward = self.treePolicy(Vrle)
			selected.backUp(reward)
			numIters += 1
		return

	def treePolicy(self, rle):

		reward = res['reward']
		return node, reward
	## you have to accumulate the reward as you go down the tree.


	def runSimulation(self, numTrainingCycles, step_horizon):
		#track total iterations spent in treePolicy
		tree_policy_iters, default_policy_iters = 0, 0
		rewards = []
		for i in range(numTrainingCycles):
			Vrle = copy.deepcopy(self.rle)

			if i%100==0 and len(rewards)>0:
				print "Training cycle: %i"%i
				print "avg. rewards for last group of 100", np.mean(rewards[-100:])

			reward, v, iters, terminal = self.treePolicy(self.root, Vrle, step_horizon)

			tree_policy_iters += iters

			# if not terminal:
			# 	reward, dPiters = self.defaultPolicy(v, Vrle, step_horizon, domain_knowledge=True)
			# 	if reward > 0 and not defaultPolicySolveStep:
			# 		defaultPolicySolveStep = i

			# 	loc = np.where(np.reshape(v.state, self.outdim)==self.avatar_code)
								
			# 	default_policy_iters += dPiters

			# rewards.append(reward)
			# self.backup(v, reward)

		return self, i


	def getBestActionsForPlayout(self, partitionWeights, debug=False):
		v = self.root
		actions = []
		while len(v.children.keys())>0:
			a, v = self.pickAction(v)
			actions.append(a)
			v = v.children[a]
		return actions

	# def getBestStatesForPlayout(self, rleCreateFunc):
	# 	rle = rleCreateFunc(OBSERVATION_GLOBAL)
	# 	v = self.root
	# 	states = [rle._game.getFullState()]
	# 	while v and not v.terminal:
	# 		a,v = self.maxChild(v)
	# 		rle.step(a)
	# 		states.append(rle._game.getFullState())

	# 	return states

	# def debug(self, rle, output=False, numActions=1):
		cntr=0
		v = self.root
		if output:
			print "current state"
			print np.reshape(v.state, rle.outdim)
		actions, nodes = [], []
		while v and not v.terminal and cntr<numActions:
			if output:
				print "options"
				print [(ACTIONS[k],c.qVal) for k,c in v.children.iteritems()]
			a, v = self.bestChild(v,(1,0,0))

			actions.append(a)
			nodes.append(v)
			if output:
				if v:
					print "selected"
					print ACTIONS[a]
					print "resulted in"
					print np.reshape(v.state, rle.outdim)
					print ""
			cntr+=1
		# if v.terminal:
		# 	distance = 0
		else:
			state = nodes[-1].state
			# distance = abs(deltaX)+abs(deltaY)
		return actions, nodes#, distance

	def pickAction(self, v, rle):
		bestVal, bestAction = -float('inf'), None

		avatarLoc = self.findAvatarInRLE(rle)
		actions = self.actionDict[avatarLoc]
		random.shuffle(actions)
		# embed()
		for a in actions:
			actionVal = self.OLE(v, a, avatarLoc)
			if actionVal > bestVal:
				bestVal = actionVal
				bestAction = a

		if bestAction == None:	## Tiebreaker
			bestAction = random.choice(v.children.keys())
		print bestAction, bestVal
		return bestAction

	def treePolicy(self, v, rle, step_horizon, solveSteps = None):
		count = 0
		iters = 0
		reward = 0
		terminal = False
		while not terminal and iters < step_horizon:
			iters += 1
			count += 1
			avatarLoc = self.findAvatarInRLE(rle)
			self.visitedLocations[avatarLoc] +=1
			if len(v.children.keys()) != len(self.actionDict[avatarLoc]):
				print "not expanded"
				print v.children.keys(), self.actionDict[avatarLoc]
				reward, c = self.expand(v, rle, domain_knowledge=True)
				return reward, c, iters, terminal
			else:
				# print 'selecting new node'
				# embed()
				a = self.pickAction(v, rle)
				res = rle.step(a)
				reward = res['reward']
				avatarLoc = self.findAvatarInRLE(rle)
				self.visitedLocations[avatarLoc] += 1
				print rle.show()
				if a not in v.children.keys():
					print a, "not in children.keys"
					embed()
				v = v.children[a]
				terminal = rle._isDone()[0]
		print "ended run"
		# embed()		
		v.n_e += 1
		v.R_e += reward
		self.backup(v)

		return reward, v, iters, terminal

	# def expand(self, v, rle, domain_knowledge=True):

	# 	if domain_knowledge:
	# 		avatarLoc = self.findAvatarInRLE(rle)
	# 		action_choices = self.actionDict[avatarLoc]
	# 	else:
	# 		action_choices = self.actions

	# 	print "in expand", len(action_choices), len(v.children.keys())
	# 	for a in action_choices:
	# 		if a not in v.children.keys():
	# 			expand_action = a
	# 			res = rle.step(a)
	# 			print a
	# 			print rle.show()
	# 			avatarLoc = self.findAvatarInRLE(rle)
	# 			self.visitedLocations[avatarLoc] +=1
	# 			new_state = res["observation"]

	# 			terminal = rle._isDone()[0]
	# 			reward = res['reward']

	# 			child = node(self, terminal, self.actions, parent = v)

	# 			if domain_knowledge:
	# 				print "creating w/ domain knowledge"
	# 				v.createChild(a, child, avatarLoc, domain_knowledge)
	# 			else:
	# 				v.createChild(a, child)
	# 			break
		
	# 	return reward, child

	# def maxChild(self, v):
	# 	tmp = np.where(np.reshape(v.state, self.outdim)==1)
	# 	avatar_loc = tmp[0][0], tmp[1][0]
	# 	qVals = [v.children[a].qVal for a in v.children.keys()]
	# 	if len(qVals)>0 and avatar_loc in self.neighborDict.keys() and len(qVals)>=len(self.neighborDict[avatar_loc])-1: #  -1, since (0,0) is not an action.
	# 			maxVal = max(qVals)
	# 			choices = [(a,c) for (a,c) in v.children.items() if c.qVal==maxVal]
	# 			for (a,c) in v.children.items():
	# 				print a, c.qVal
	# 			print ""
	# 			return random.choice(choices)
	# 	else:
	# 		return (None, None)

	# def bestChild(self, v, partitionWeights, solveSteps = None, debug=False):
	# 	"""
	# 	solveSteps = the number of steps that have passed since default policy solved the game
	# 	"""
		
	# 	def transform(loc):
	# 		slowdown_factor = 1 # 1./3
	# 		if loc in self.rewardDict:
	# 			distanceFunc = self.rewardDict[loc]
	# 			return 1/(1+math.exp(-slowdown_factor * distanceFunc)) # sigmoid
	# 		else:
	# 			return 0.

	# 	maxFuncVal = -float('inf')
	# 	bestChild = None
	# 	bestAction = None
	# 	sumQVal = 0
	# 	sumVisitCount = 0
	# 	sumPseudoReward = 0
	# 	heuristic_coefficient = partitionWeights[2]
	# 	exploration_coefficient = partitionWeights[1]
	# 	heuristic_decay_factor = 0.999
	# 	exploration_decay_factor = 0.999
	# 	if solveSteps:
	# 		# print solveSteps
	# 		heuristic_coefficient *= (heuristic_decay_factor**solveSteps)
	# 		exploration_coefficient *= (exploration_decay_factor**solveSteps)
	# 		self.printheuristicweight = heuristic_coefficient
	# 		self.printexplorationweight = exploration_coefficient
	# 		# print "heuristic coefficient is now", heuristic_coefficient

	# 	for a,c in v.children.items():
	# 		if v.equals(c):
	# 			continue
	# 		elif c.visitCount == 0:
	# 			continue
	# 		else:
	# 			if self.avatar_code not in [l%2 for l in c.state]: ##we're in a terminal losing state
	# 																## Don't give pseudoreward
	# 				if not c.terminal:
	# 					print "terminal state but avatar not in c.state"
	# 					embed()

	# 				# vLoc = np.where(np.reshape(v.state, self.outdim)%2==self.avatar_code)
	# 				# if len(vLoc[0])>0:
	# 				# 		vLoc = vLoc[0][0], vLoc[1][0] 

	# 				# cLoc = (vLoc[0] + a[1], vLoc[1] + a[0])

	# 				# if cLoc in self.rewardDict:
	# 				# 	sumQVal += abs(float(c.qVal)/c.visitCount)
	# 				# 	sumVisitCount += abs(math.sqrt(2*math.log(v.visitCount)/c.visitCount))
	# 				# 	sumPseudoReward += abs(transform(cLoc))/c.visitCount
	# 				# else:
	# 				# 	continue

	# 				sumQVal += abs(float(c.qVal)/c.visitCount)
	# 				sumVisitCount += abs(math.sqrt(2*math.log(v.visitCount)/c.visitCount))
	# 				sumPseudoReward += 0. #abs(transform(cLoc))/c.visitCount


	# 			else:
	# 				loc = np.where(np.reshape(c.state, self.outdim)%2==self.avatar_code)
	# 				if len(loc[0])>0:
	# 					loc = loc[0][0], loc[1][0] 
	# 				try:
	# 					sumQVal += abs(float(c.qVal)/c.visitCount)
	# 					sumVisitCount += abs(math.sqrt(2*math.log(v.visitCount)/c.visitCount))
	# 					sumPseudoReward += abs(transform(loc))/c.visitCount
	# 				except TypeError:
	# 					print "loc is weird type"
	# 					embed()



	# 	# print ""
	# 	if debug:
	# 		print np.reshape(v.state, self.outdim)
	# 	for a,c in v.children.items():
	# 		if v.equals(c):
	# 			funcVal = -float('inf')
	# 		elif c.visitCount == 0:
	# 			funcVal = float('inf')
	# 		else:
	# 			if self.avatar_code not in [l%2 for l in c.state]: ##we're in a terminal losing state
	# 																## Don't give pseudoreward
	# 				# vLoc = np.where(np.reshape(v.state, self.outdim)%2==self.avatar_code)
	# 				# if len(vLoc[0])>0:
	# 						# vLoc = vLoc[0][0], vLoc[1][0] 

	# 				# cLoc = (vLoc[0] + a[1], vLoc[1] + a[0])
	# 				# if cLoc in self.rewardDict:
	# 				qValFunction = 0
	# 				if sumQVal == 0:
	# 					qValFunction = 0
	# 				else:
	# 					qValFunction = float(c.qVal)/c.visitCount/sumQVal

	# 				funcVal = partitionWeights[0]*qValFunction \
	# 				        + exploration_coefficient*math.sqrt(2*math.log(v.visitCount)/c.visitCount)/sumVisitCount \
	# 						+ 0.


	# 				# else:
	# 				# 	funcVal = -float('inf')

	# 				# qValFunction = 0
	# 				# if sumQVal == 0:
	# 				# 	qValFunction = 0
	# 				# else:
	# 				# 	qValFunction = float(c.qVal)/c.visitCount/sumQVal

	# 				# funcVal = partitionWeights[0]*qValFunction \
	# 				#         + exploration_coefficient*math.sqrt(2*math.log(v.visitCount)/c.visitCount)/sumVisitCount \
	# 				# 		+ heuristic_coefficient* (transform(cLoc)/c.visitCount)/ sumPseudoReward


	# 			else:
	# 				loc = np.where(np.reshape(c.state, self.outdim)%2==self.avatar_code)
	# 				if len(loc[0])>0:
	# 						loc = loc[0][0], loc[1][0] 

	# 				qValFunction = 0
	# 				if sumQVal == 0:
	# 					qValFunction = 0
	# 				else:
	# 					qValFunction = (float(c.qVal)/c.visitCount)/sumQVal


	# 				funcVal = partitionWeights[0]* qValFunction \
	# 				        + exploration_coefficient*math.sqrt(2*math.log(v.visitCount)/c.visitCount)/sumVisitCount \
	# 				        + heuristic_coefficient*(transform(loc)/c.visitCount)/sumPseudoReward	
	# 			if debug:
	# 				print a, funcVal

	# 		if funcVal > maxFuncVal:
	# 			maxFuncVal = funcVal
	# 			bestAction = a
	# 			bestChild = c
	# 	if bestChild == None:
	# 		bestAction = random.choice(v.children.keys())
	# 		bestChild = v.children[bestAction]

	# 	if debug:
	# 		print ""
	# 	return bestAction, bestChild

	# def defaultPolicy(self, v, rle, step_horizon, domain_knowledge=False):

		# reward = 0
		# terminal = False
		# iters = 0
		# state = v.state
		# g = 1
		
		# terminal = rle._isDone()[0]

		# while not terminal and iters < step_horizon:

		# 	reshaped_state = np.reshape(state, self.outdim)
		# 	avatar_loc = np.where(reshaped_state==self.avatar_code, True, False)
		# 	avatar_loc = (avatar_loc[0][0], avatar_loc[1][0])

		# 	iters += 1
			
		# 	if domain_knowledge and avatar_loc in self.actionDict.keys():
		# 		sample = random.choice(self.actionDict[avatar_loc])
		# 	else:
		# 		sample = random.choice([(-1,0), (1,0), (0,-1), (0,1)])
			
		# 	a = sample

		# 	res = rle.step(a)
		# 	# print rle.show()
		# 	new_state = res["observation"]
		# 	state = new_state
		# 	terminal = rle._isDone()[0]
		# 	if terminal and res['reward']==1:
		# 		reward += g*self.rewardScaling
		# 	else:
		# 		reward += g*res['reward']
		# 	# reward += g*res['reward']
			
		# 	g *= self.decay_factor

		# return reward, iters

	def backup(self, v):
		while v:
			# embed()
			v.n_s += 1
			try:
				v.R_m = v.R_e/v.n_s + ((1-v.n_e)/v.n_s) * max([v.children[k].R_m for k in v.children.keys()])
			except:
				v.R_m = v.R_e/v.n_s + ((1-v.n_e)/v.n_s)
			v = v.parent

	def OLE(self, node, action, avatarLoc):
		# print "in OLE"
		# embed()
		nextPos = (action[1]+avatarLoc[0], action[0]+avatarLoc[1])
		return node.R_m + math.sqrt(math.log(node.n_s)/node.n_s_a[action]) - .2*self.visitedLocations[nextPos]

class node:
	def __init__(self, tree, parent, depth, action, tabooBias):
		"""
		self.children = a dictionary mapping each action to the child that results
		"""
		self.tree = tree
		self.epsilon = 0.05
		self.egreedyEpsilon = 0.05
		self.eMaxGreedyEpsilon = 0.05
		self.parent = parent
		self.children = {}
		self.totValue = 0.
		self.expectimax = 0.
		self.nVisits = 0.
		self.actionIndex = action
		self.nbGenerated = 0.
		self.nodeDepth = depth
		self.tabooBias = tabooBias
		self.nbExitsHere = 0.
		self.totalValueOnExit = 0.
		self.childrenMaxAdjEmax = 0.
		self.adjEmax = 0.

	def setNodeDepth(self, newDepth):
		self.nodeDepth = newDepth

	def refreshTree(self):
		for k in self.children.keys():
			child = self.children[k]
			child.depth = self.depth + 1
			child.totValue=child.totValue/child.nVisits
			child.nVisits = 1
			child.expectimax = child.totValue/child.nVisits
			child.adjEmax = child.totValue/child.nVisits
			child.totalValueOnExit = child.totalValueOnExit/child.nVisits
			child.nbExistsHere = 1
			child.refreshTree()
			child.nbGenerated=0

	def getAdjustedEmaxScore(self):
		return self.adjEmax + tree.K * math.sqrt(math.log(parent.nVisits+1)/(self.nVisits + self.epsilon)) - self.tabooBias
	
	def backUp(self, result):
		node = self
		backUpDepth = 0
		while node is not None:
			node.nVisits += 1
			node.nbGenerated += 1
			node.totValue += result
			if backUpDepth > 0:
				bestExpectimax = -float('inf')
				bestAdjustedExpectimax = -float('inf')
				for k in node.children.keys():
					if node.children[k].expectimax > bestExpectimax:
						bestExpectimax = node.children[k].expectimax
					if node.children[k].adjEmax > bestAdjustedExpectimax:
						bestAdjustedExpectimax = node.children[k].expectimax
				node.expectimax = bestExpectimax
				node.childrenMaxAdjEmax = bestAdjustedExpectimax
				node.adjEmax = (node.nbExitsHere/node.nVisits) * (node.totalValueOnExit / node.nbExitsHere) +\
					(1. - node.nbExitsHere/node.nVisits) * node.childrenMaxAdjEmax
			else:
				node.nbExitsHere += 1
				node.totalValueOnExit += result
				node.adjEmax = (node.nbExitsHere/node.nVisits) * (node.totalValueOnExit / node.nbExitsHere) +\
					(1. - node.nbExitsHere/node.nVisits) * node.childrenMaxAdjEmax
				node.expectimax = node.totValue/node.nVisits

			node = node.parent
			backUpDepth +=1

	def selectChild(self):
		child = None
		bestValue = -float('inf')
		selectedIndex = None

		if random.random() < self.eMaxGreedyEpsilon:
			# Select randomly
			selectedIndex = random.choice(self.children.keys())
			child = self.chldren[k]
		else:
			for k in self.children.keys():
				score = self.chilren[k].getAdjustedEmaxScore()
				if score > bestValue:
					child = self.children[k]
					bestValue = score
		if child is None:
			print "Warning! failed to return child"
			embed()
		else:
			return child

	def mostVisitedAction(self):
		selected = -1
		bestValue = -float('inf')
		allEqual = True
		first = -1

		for i in range(len(self.children.values())):
			if first==-1:
				first = self.children.values()[i].nVisits
			elif first !=- self.children.values()[i].nVisits:
				allEqual = False
			challengerValue = self.children.values()[i].nVisits + random.random()*self.epsilon
			if challengerValue > bestValue:
				bestValue = challengerValue
				selected = i
		if selected == -1:
			print "unexpected selection!"
			selected = 0
		elif allEqual:
			return self.bestAction()
		return self.children.keys()[selected]

	def bestAction(self):
		selected = -1
		bestValue = -float('inf')
		for i in range(len(self.children.values())):
			if self.children.values[i].totValue + random.random()*self.epsilon > bestValue:
				bestValue = self.children.values[i].totValue
				selected = i
		if selected == -1:
			print "unexpected selection in bestAction"
			selected = 0

		return self.children.keys()[selected]

	def createChild(self,action,child, avatar_loc=False, domain_knowledge=False):
		# check the following if condition

		if action not in self.children:
		    self.children[action] = child
		    # if domain_knowledge:
		    self.expanded = len(self.children.keys()) == len(self.tree.actionDict[avatar_loc])
		    print"creating Child"
		    print action
		    print self.children.keys(), self.tree.actionDict[avatar_loc]
		    print len(self.children.keys()), len(self.tree.actionDict[avatar_loc])
			# else:
				# self.expanded = len(self.children.keys()) == len(self.actions)
		else:
			print "createChild got called but with an existing action."

if __name__ == "__main__":
	
	# gameFilename = "examples.gridphysics.simpleGame_push_boulders_multigoal"
	# gameFilename = "examples.gridphysics.waypointtheory" 
	# gameFilename = "examples.gridphysics.simpleGame_teleport"
	# gameFilename = "examples.gridphysics.movers3c"
	# gameFilename = "examples.gridphysics.scoretest" 
	# gameFilename = "examples.gridphysics.rivercross" 
	gameFilename = "examples.gridphysics.simpleGame_small" 

	gameString, levelString = defInputGame(gameFilename, randomize=True)
	rleCreateFunc = lambda: createRLInputGame(gameFilename)
	rle = rleCreateFunc()
	print rle.show()
	# rle.immovables = ['wall', 'poison1', 'poison2']
	print ""
	print "Initializing learner. Playing", gameFilename

	agent = OLETS(rle, gameString, levelString)

	t1 = time.time()
	agent.runSimulation(numTrainingCycles=100, step_horizon=100)
	t2 = time.time() - t1
	print "done in {} seconds".format(t2)

	self=agent
	v=agent.root
	avatarLoc = self.findAvatarInRLE(rle)
	actions = self.actionDict[avatarLoc]
	print [(a, self.OLE(v, a, avatarLoc)) for a in actions]
	embed()

	bestAction = agent.pickAction(agent.root, rle)
	rle.step(bestAction)
	agent.rle = rle
	agent.root = agent.root.children[bestAction]
	agent.runSimulation(numTrainingCycles=500, step_horizon=100)
	print rle.show()
	v=agent.root
	avatarLoc = self.findAvatarInRLE(rle)
	actions = self.actionDict[avatarLoc]
	print [(a, self.OLE(v, a, avatarLoc)) for a in actions]
