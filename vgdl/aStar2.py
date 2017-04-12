import numpy as np
from numpy import zeros
import pygame    
from ontology import BASEDIRS
from core import VGDLSprite, colorDict, sys
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
from ontology import Immovable, Passive, Resource, ResourcePack, RandomNPC, Chaser, AStarChaser, OrientedSprite, Missile
from ontology import initializeDistribution, updateDistribution, updateOptions, sampleFromDistribution, spriteInduction, selectObjectGoal
from theory_template import TimeStep, Precondition, InteractionRule, TerminationRule, TimeoutRule, SpriteCounterRule, MultiSpriteCounterRule, \
generateSymbolDict, ruleCluster, Theory, Game, writeTheoryToTxt, generateTheoryFromGame
from rlenvironmentnonstatic import createRLInputGame
import curses

#A hack to display things to the terminal conveniently.
np.core.arrayprint._line_width=250

ACTIONS = {(0,0):'stay',(0,-1):'up', (0,1):'down', (1,0):'right', (-1,0):'left', None:'none'}

class Node:
	def __init__(self, index, sprite, terminal=False, win=False):
		self.sprite = sprite
		self.index = index
		self.terminal = terminal
		self.win = win

class AStar:
	def __init__(self, rle, gameString, levelString):
		self.rle = rle
		self.gameString = gameString
		self.levelString = levelString
		# self.actions = [(0,0), (1,0), (-1,0), (0,1), (0,-1)]
		self.actions = [(1,0), (-1,0), (0,1), (0,-1)]
		self.maxPseudoReward = 1
		self.pseudoRewardDecay = .8
		goalLoc = self.findObjectInRLE(rle, 'goal')
		self.rewardDict = {goalLoc:self.maxPseudoReward}
		self.open = set()
		self.closed = set()

		self.scanDomainForMovementOptions()
		self.propagateRewards(goalLoc)

	def scanDomainForMovementOptions(self):
		##TODO: Take a state, so that you can re-perform this scan as needed and take changes into account.
		##TODO: query VGDL description for penetrable/nonpenetrable objects, add to list.
		immovable_codes = []
		# immovables = ['wall']
		try:
			immovables = self.rle.immovables
			# immovables = ['wall', 'poison']
			print "immovables", immovables
		except:
			immovables = ['wall', 'poison']
			print "Using defaults as immovables", immovables

		for i in immovables:
			if i in self.rle._obstypes.keys():
				immovable_codes.append(2**(1+sorted(self.rle._obstypes.keys())[::-1].index(i)))

		actionDict = defaultdict(list)
		neighborDict = defaultdict(list)
		# action_superset = [(0,0),(-1,0), (1,0), (0,-1), (0,1)]
		action_superset = [(-1,0), (1,0), (0,-1), (0,1)]
		
		board = np.reshape(self.rle._getSensors(), self.rle.outdim)
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
	
	def propagateRewards(self, goalLoc):
		rewardQueue = deque()
		processed = [goalLoc]
		rewardQueue.append(goalLoc)
		for n in self.neighborDict[goalLoc]:
			if n not in rewardQueue:
				rewardQueue.append(n)

		while len(rewardQueue)>0:
			loc = rewardQueue.popleft()
			if loc not in processed:
				valid_neighbors = [n for n in self.neighborDict[loc] if n in self.rewardDict.keys()]
				self.rewardDict[loc] = max([self.rewardDict[n] for n in valid_neighbors]) * self.pseudoRewardDecay
				processed.append(loc)
				for n in self.neighborDict[loc]:
					if n not in processed:
						rewardQueue.append(n)
		return

	def h(self, avatarLoc, goalLoc):
		return self.manhattanDistance(avatarLoc, goalLoc)

	def getLowestF(self, noes, f_score):
		"""
		Searches for the node with the lowest f_score
		"""
		f_best = 9999 
		node_best = None
		for node in nodes:
			if f_score[node.index] < f_best:
				f_best = f_score[node.index]
				node_best = node

		return node_best

	def reconstruct_path(self, came_from, current):
		#print self.get_tile_from_index(current.index)
		if current.index in came_from:
			p = self.reconstruct_path(came_from, came_from[current.index])
			p.append(current)
			return p
		else:
			return [current]
	
	def neighbor_nodes(self, node):
		sprite = node.sprite;
		return self.neighbor_nodes_of_sprite(sprite)

	def neighbor_nodes_of_sprite(self, sprite):
		tileX, tileY = self.get_sprite_tile_position(sprite)

		tiles = [ (tileX-1,tileY), (tileX+1, tileY), (tileX,tileY-1), (tileX, tileY+1)]
		neighbors = []
		for (tilex, tiley) in tiles:
			if (tilex >= 0 and tilex < self.game.width and tiley >= 0 and tiley < self.game.height):
				index = self.get_index(tilex, tiley)
				if index in self.walkable_tile_indices:
					neighbors.append(self.walkable_tiles[index])

		# neighbor_indices = [neighbor.index for neighbor in neighbors]
		# print 'neighbors(%s,%s):%s' %(tileX, tileY, map(self.get_tile_from_index, neighbor_indices))

		return neighbors
		
	def findObjectInRLE(self, rle, objName):
		if objName not in rle._obstypes.keys():
			print objName, "not in rle."
			return None
		objCode = 2**(1+sorted(self.rle._obstypes.keys())[::-1].index(objName))
		objLoc = np.where(np.reshape(self.rle._getSensors(), self.rle.outdim)==objCode)
		objLoc = objLoc[0][0], objLoc[1][0] #(y,x)
		return objLoc
	
	def findAvatarInRLE(self, rle):
		# avatar_code = 1
		# state = np.reshape(rle._getSensors(), self.rle.outdim)
		# if avatar_code in state:
		# 	avatar_loc = np.where(state==avatar_code)
		# 	avatar_loc = avatar_loc[0][0], avatar_loc[1][0]
		# else:
		# 	avatar_loc = None
		if rle._avatar:
			avatar_loc = rle._rect2pos(rle._avatar.rect)
		else:
			avatar_loc = None
		return avatar_loc

	def findAvatarInState(self, s):
		## takes a string representation of a state, returns avatar location
		state = np.reshape(np.fromstring(s,dtype=float), self.rle.outdim)
		avatar_code = 1
		if avatar_code in state:
			avatar_loc = np.where(state==avatar_code)
			avatar_loc = avatar_loc[0][0], avatar_loc[1][0]
		else:
			avatar_loc = None
		return avatar_loc
	
	def selectAction(self, s, policy, partitionWeights = None, domainKnowledge=True, printout=False):
		if policy == 'epsilonGreedy':
			if random.random() < self.epsilon:
				return random.choice(self.actions)
			else:
				bestQVal, bestA, QValsAreAllEqual = self.bestSA(s, partitionWeights, domainKnowledge = True)
				return bestA
		elif policy == 'greedy':
			bestQVal, bestA, QValsAreAllEqual = self.bestSA(s, partitionWeights = [1,0], domainKnowledge = True)
			if printout:
				print bestQVal
			if QValsAreAllEqual:
				return None
			else:
				return bestA

	def getPseudoReward(self, s, a):
		## returns pseudoreward of taking action a from location currentLoc.
		## gives pseudoReward[currentLoc] if a doesn't move states.
		currentLoc = self.findAvatarInState(s)
		if currentLoc:
			nextLoc = currentLoc[0]+a[1], currentLoc[1]+a[0] #again, locations are (y,x) and actions are (x,y)
		else:
			return 0.
		if nextLoc in self.rewardDict.keys():
			return self.rewardDict[nextLoc]
		elif currentLoc in self.rewardDict.keys():
			return self.rewardDict[currentLoc]
		else:
			return 0.

	def manhattanDistance(self, avatarLoc, goalLoc):
		return abs(avatarLoc[0]-goalLoc[0]) + abs(avatarLoc[1] - goalLoc[1])

	def bestNode(self):
		# bestVal = 9999
		# bestNode = None
		# for node in self.open:
		# 	if node.f() < bestVal:
		# 		bestVal = 
		bestVal = min([n.f() for n in self.open])
		options = [n for n in self.open if n.f() == bestVal]
		# if any([(o.terminal and not o.win) for o in options]):
		# 	print "found bad option"
		# 	embed()
		return random.choice(options)
	
	def makeNeighbors(self, node):
		neighbors = []
		s = self.findAvatarInState(node.state)
		for a in self.actionDict[s]:
			newRLE = copy.deepcopy(node.rle)
			newRLE.step(a)
			terminal, win = newRLE._isDone()[0], newRLE._isDone()[1]
			if not terminal:
				avatarLoc, goalLoc = self.findAvatarInRLE(newRLE), self.findObjectInRLE(newRLE, 'goal')
				try:
					h = self.manhattanDistance(avatarLoc, goalLoc)
				except:
					print "couldn't find h"
					embed()
				win = False
			else:
				if win:
					h = 0
				else:
					h = float('inf') ## TODO: probably not a good call.
			newNode = Node(newRLE, newRLE._getSensors().tostring(), node, node.g+1, h, terminal, win)
			neighbors.append(newNode)
		return neighbors

	def search(self):
		rle = copy.deepcopy(self.rle)
		terminal, win = rle._isDone()[0], rle._isDone()[1]
		s = rle._getSensors().tostring()
		bestChildSum, makeneighborSum, loopSum = 0, 0, 0
		i=0
		total_reward = 0.	
		avatarLoc, goalLoc = self.findAvatarInRLE(rle), self.findObjectInRLE(rle, 'goal')
		try:
			node = Node(rle, s, None, 0., self.manhattanDistance(avatarLoc, goalLoc), terminal, win)
		except:
			print "couldn't make node becuase of manhattan distance"
			embed()
		self.open.add(node)

		while len(self.open)>0:
			t1 = time.time()
			current = self.bestNode()
			# print current.f(), len(self.open), [o.f() for o in self.open]
			bestChildSum += time.time() - t1
			if current.terminal and current.win:
				print 'bestChildSum, makeneighborsum, loopsum', bestChildSum, makeneighborSum, loopSum
				return self.constructPath(current)
			else:
				self.open.remove(current)
				self.closed.add(current)
				t2 = time.time()
				Neighbors = self.makeNeighbors(current)
				makeneighborSum = time.time() - t2
				for neighbor in Neighbors:
					if neighbor.state not in [n.state for n in self.closed]:
						# neighbor.f = neighbor.g + newNode.h
						if neighbor.state not in [n.state for n in self.open]:
							self.open.add(neighbor)
						else:
							neighbors = [n for n in self.open if n.state==neighbor.state]
							if len(neighbors)>1:
								print "found more than one neighbor"
								embed()
							openNeighbor = neighbors[0]

							# openNeighbor = [n for n in self.open if n.state==neighbor.state][0]

							if neighbor.g < openNeighbor.g:
								openNeighbor.g = neighbor.g
								openNeighbor.parent = neighbor.parent
			loopSum += time.time() - t1
			print i
			i +=1
		print 'bestChildSum, makeneighborsum, loopsum', bestChildSum, makeneighborSum, loopSum
		return False

	def constructPath(self, node):
		path = []
		path.append(node)
		while node.parent is not None:
			node = node.parent
			path.insert(0, node) ##prepend
		return path

	def playPath(self, path):
		for p in path:
			print p.show()

if __name__ == "__main__":
	
	# gameFilename = "examples.gridphysics.simpleGame4_small"
	# gameFilename = "examples.gridphysics.simpleGame_teleport"
	# gameFilename = "examples.gridphysics.simpleGame_many_poisons_huge"
	gameFilename = "examples.gridphysics.movers3"

	gameString, levelString = defInputGame(gameFilename, randomize=True)
	rleCreateFunc = lambda: createRLInputGame(gameFilename)
	rle = rleCreateFunc()
	agent = AStar(rle, gameString, levelString)
	path = agent.search()
	print "found path"

	embed()