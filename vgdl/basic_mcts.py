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

class Basic_MCTS:
	def __init__(self, rleCreateFunc, obsType):
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
		# self.rle = rle
		self.rle = self.rleCreateFunc(self.obsType)
		self.root = MCTS_node(self.rle._getSensors(None), False, self.rle._actionset)
		self.actions = self.rle._actionset
		self.currentNode = self.root

	def startTrainingPhase(self, numTrainingCycles):
		# apparently the reset method is inefficient
		for i in range(numTrainingCycles):
			self.rle = createRLSimpleGame3(OBSERVATION_GLOBAL)
			# self.rle = self.rleCreateFunc(self.obsType)
			reward, vl = self.treePolicy(self.root)
			if not vl.terminal:
				reward = self.defaultPolicy(vl)

			self.backup(vl, reward)

	def startTestingPhase(self, numTestingCycles):
		rewardSum = 0
		# for i in range(numTestingCycles):
		#self.rle = createRLSimpleGame3(OBSERVATION_GLOBAL)
		self.rle = self.rleCreateFunc(self.obsType)
		v = self.root
		Cp = 0
		reward = 0
		actionList = []
		while not v.terminal:
			a, v = self.bestChild(v,Cp)
			actionList.append(a)
			embed()
			res = self.rle.step(a)
			terminal = res['pcontinue']
			if terminal:
				reward = res['reward']

		rewardSum += reward
		print "finished startTestingPhase"
		embed()

		return rewardSum



	def treePolicy(self, v):
		count = 0
		while not v.terminal:
			count += 1
			if not v.expanded:
				reward, c = self.expand(v)
				# rle.step(a)
				return reward, c

			else:
				Cp = 0.70710 # suggested exploration weight
				a, v = self.bestChild(v,Cp) 
				res = self.rle.step(a)
				terminal = not res['pcontinue']
				if terminal:
					reward = res['reward']
					return reward, v


	def expand(self,v):
		expan_action = None
		child = None
		reward = 0
		for a in self.actions:
			if a not in v.children:
				expand_action = a
				res = self.rle.step(a)
				new_state = res["observation"]
				terminal = not res['pcontinue']
				if terminal:
					reward = res['reward']

				child = MCTS_node(new_state, terminal, self.rle._actionset, parent = v)
				v.createChild(a,child)
				break

		return reward, child

	def bestChild(self, v, Cp):
		maxFuncVal = -float('inf')
		bestChild = None
		bestAction = None
		for a,c in v.children.items():
			if v.equals(c):
				funcVal = -float('inf')
			elif c.visitCount == 0:
				funcVal = float('inf')
			else:
				funcVal = float(c.qVal)/c.visitCount + Cp * math.sqrt(2*math.log(v.visitCount)/c.visitCount)

			if funcVal > maxFuncVal:
				maxFuncVal = funcVal
				bestAction = a
				bestChild = c

		return bestAction, bestChild

	def defaultPolicy(self, s):
		reward = 0
		while not s.terminal:
			# print "in default"
			a = self.actions[random.randint(0,len(self.actions)-1)]
			res = self.rle.step(a)
			new_state = res["observation"]
			terminal = not res['pcontinue']
			if terminal:
				reward = res['reward']

			s_new = MCTS_node(new_state,terminal, self.rle._actionset, parent = s)
			s.createChild(a,s_new)

			s = s_new

		return reward

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



if __name__ == "__main__":
	obsType = OBSERVATION_GLOBAL
	rleCreateFunc = createRLSimpleGame4
	mcts = Basic_MCTS(rleCreateFunc, obsType)
	mcts.startTrainingPhase(1000)
	rewardSum = mcts.startTestingPhase(50)
	# embed()
