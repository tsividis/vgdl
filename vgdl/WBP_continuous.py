#! /home/eshnich/.conda/envs/planning/bin/python

print "STARTING!"
import sys
import os
sys.path.append('/om/user/eshnich/vgdl/vgdl') 
print "step1"
from IPython import embed
import itertools
import numpy as np
from numpy import zeros
import pygame
print "step2"
from ontology import BASEDIRS
import ontology
import core
from core import VGDLSprite, colorDict, sys
from stateobsnonstatic import StateObsHandlerNonStatic
from rlenvironmentnonstatic import *
import argparse
import random
import math
from threading import Thread
from threading import Lock
from collections import defaultdict, deque
import time
print "step3"
#import ipdb
#import vgdl
import heapq
import copy
from threading import Lock
print "a"
from Queue import Queue
from util import *
print "b"
import multiprocessing
#import ctypes
from ontology import Immovable, Passive, Resource, ResourcePack, RandomNPC, Chaser, AStarChaser, OrientedSprite, Missile
from ontology import initializeDistribution, updateDistribution, updateOptions, sampleFromDistribution, spriteInduction, selectObjectGoal
print "c"
from theory_template import TimeStep, Precondition, InteractionRule, TerminationRule, TimeoutRule, SpriteCounterRule, MultiSpriteCounterRule, \
NoveltyRule, generateSymbolDict, ruleCluster, Theory, Game, writeTheoryToTxt, generateTheoryFromGame
from rlenvironmentnonstatic import createRLInputGame
print "step4"
from line_profiler import LineProfiler
import cPickle

from pygame.locals import K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT

sys.path.extend([''])
import vgdl
print "FINISHED IMPORTS"
NONE = 0
ACTIONS = [K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT, NONE]
actionDict = {K_SPACE: 'space', K_UP: 'up', K_DOWN: 'down', K_LEFT: 'left', K_RIGHT: 'right', NONE: 'wait'}


#-----parameters------
WALL_EDGE = 1 #weight of edge adjacent to a wall when constructing graph.                                                                       
REMOVE_MOVERS = True #whether to remove moving NPCs from the set of atoms
LIMIT = 3 #number of times pixel atom can be seen before counted as true
GRID_LIMIT = 150 #number of times grid atom can be seen before counted as true
SPEED_THRESH = [] #speed threshholds when incorporating speed into the atoms. If list is empty, speed is not used
ROLLOUT_DEPTH = 45 #number of frames we look ahead in a rollout
WIN_RATIO = 5 #ratio of how many more times winning termination conditions count than losing conditions
DEPTH_WEIGHT = 0.0 #how much to weight the depth of a node in the tree
ALPHA1 = 1000 #weight given toward collecting an object which gives progress towards a goal (first order heuristic)
ALPHA2 = 1 #weight give towards distance to good objects (second order heuristic)
OBJCOLLECT_WEIGHT = 0.0 #.005

N_METABOLICS = 1000
MULT_METABOLICS = 0.1#0.0012
DO_METABOLICS = False #False

C = 0.875 #(1-ball_width/2)

ignored_sprites = ['wall', 'background','ladder','conveyor','rope','offrope'] #sprite types we ignore in calculating atoms
print "FINISHED SETTING VALUES"
#----------------------

## Base class for width-based planners (IW(k) and 2BFS)
class WBP():
	def __init__(self, rle, gameFilename, theory=None, fakeInteractionRules = [], annealing=1, max_nodes=10000, limit=LIMIT, grid_limit=GRID_LIMIT,shortHorizon=False,firstOrderHorizon=False,seen_limits=[]):
		self.rle = rle
		self.gameFilename = gameFilename
		self.T = len(rle._obstypes.keys())+1 #number of object types. Adding avatar, which is not in obstypes.
		
		self.trueAtoms = defaultdict(lambda:0) #set() ## set of atoms that have been true at some point thus far in the planner.
		self.objectTypes = rle._game.sprite_groups.keys()
		self.objectTypes.sort() #wall, avatar, etc.
		self.phiSize = sum([len(rle._game.sprite_groups[k]) for k in rle._game.sprite_groups.keys() if k not in ['wall', 'avatar']])#number of not wall/avatar objects
		
		self.avatar = rle._game.sprite_groups["avatar"][0]#FIX
		self.square_size = (self.avatar.rect.width,self.avatar.rect.height)#FIX
		
		self.vecDim = [rle.outdim[0]*rle.outdim[1]*self.square_size[0]*self.square_size[1], 2, self.T]
		self.objIDs = {}
		self.solution = None
		self.maxNumObjects = 6
		self.trackTokens = False
		self.vecSize = None
		self.addWaitAction = True
		self.annealing = annealing
		self.statesEncountered = []
		self.padding = 5  ##5 is arbitrary; just to make sure we don't get overlap when we add positions
		self.max_nodes = max_nodes
		self.quitting = False
		self.gameString_array = []
		self.avatar_ID = None
		if theory == None:
			self.theory = generateTheoryFromGame(rle, alterGoal=False)
		else:
			self.theory=theory
		print 'max nodes', self.max_nodes

		i=1
		for k in rle._game.all_objects.keys():
			self.objIDs[k] = i * (self.vecDim[0]+self.padding)
			

			if isinstance(rle._game.all_objects[k]['sprite'],vgdl.core.Avatar):
				
				#embed()
				self.avatar_ID = i * (self.vecDim[0]+self.padding)
			i+=1

		self.canJump = False
		self.addSpaceBarToActions()
		self.all_locs = []
		self.avatar_locs_disc = defaultdict(lambda:0)
		self.key = defaultdict(lambda:0)
		self.no_key = defaultdict(lambda:0)
		self.graph = {}

		self.distances = self.dijkstra() #uncomment if any other game than breakout

		self.num_paths = 1
		self.all_paths = []
		self.LIMIT = limit
		self.GRID_LIMIT = grid_limit

		self.speed_thresh = SPEED_THRESH

		self.wait_steps = 0

		self.winning_states = []

	def makeGraph(self):
		graph = {}
		wallLocs = self.findObjectsInRLE(self.rle,'wall')
		wallLocs = set([(x[0]/self.square_size[0],x[1]/self.square_size[1]) for x in wallLocs])
		for i in range(self.rle.outdim[1]):
			for j in range(self.rle.outdim[0]):
				if (i,j) not in wallLocs:
					graph[(i,j)] = set()
					for (x,y) in [(0,1),(0,-1),(1,0),(-1,0)]:
						if (i + x, j + y) not in wallLocs and i+x in range(self.rle.outdim[1]) and j+y in range(self.rle.outdim[0]):
								graph[(i,j)].add((i+x,j+y))
		edges = defaultdict(lambda:1)

		for wall in wallLocs:
			for (x,y) in [(1,1),(1,-1),(-1,1),(-1,-1)]:
				diag = (wall[0]+x,wall[1]+y)
				vert = (wall[0],wall[1]+y)
				horiz = (wall[0]+x,wall[1])
				if diag in graph and horiz in graph and vert in graph:
					edges[(vert,diag)] = WALL_EDGE
					edges[(diag,vert)] = WALL_EDGE
					edges[(horiz,diag)] = WALL_EDGE
					edges[(diag,horiz)] = WALL_EDGE
		

		return graph, edges

	def dijkstra(self):
		graph, edges = self.makeGraph()
		self.graph = graph
		dist = {}

		for (i,j) in graph:
			dist[(i,j)] = self.single_source(graph, edges, (i,j))

		return dist

	def single_source(self, graph, edges, source):
		dist = {}
		dist[source] = 0
		queue = {source}
		visited = set()

		while queue:

			minNode = None
			for node in queue:
				if minNode is None:
					minNode = node
				else:
					if dist[node] < dist[minNode]:
						minNode = node

			queue.remove(minNode)
			visited.add(minNode)
			current = minNode

			for neighbor in graph[current]:
				if neighbor not in visited:
					if neighbor in dist:
						if dist[current] + edges[(current,neighbor)] < dist[neighbor]:
							dist[neighbor] = dist[current] + edges[(current,neighbor)]
					else:
						dist[neighbor] = dist[current] + edges[(current,neighbor)]
					queue.add(neighbor)
		return dist

	def grid(self,loc):
		return (loc[0]/self.square_size[0],loc[1]/self.square_size[1])

	#return geodesic distance between two locations ----------------------
	#(Note: this is probably unnecessarily complicated)
	def geoDist(self,loc1,loc2):

		return manhattanDist(loc1,loc2)/float(self.square_size[0]) #in the end want to use manhattan distance 
		#+ learn geodesic distance via teleporting

		
		'''
		grid1= self.grid(loc1)
		grid2= self.grid(loc2)
		
		x1 = loc1[0]/float(self.square_size[0]) - grid1[0]
		y1 = loc1[1]/float(self.square_size[1]) - grid1[1]
		x2 = loc2[0]/float(self.square_size[0]) - grid2[0]
		y2 = loc2[1]/float(self.square_size[1]) - grid2[1]

		#if tuple(loc1) in self.graph and tuple(loc2) in self.graph:
		#	return self.distances[loc1][loc2]

		inWall = False

		#smooth out distances at grid vertices to calculate distances between points at interior of squares
		
		dist = 0
		a1 = self.loop4d()
		a2 = self.loop4d()
		
		for exp in a1:
			for coord in a2:
				if all(i >= j for i, j in zip(exp,coord)):
					val = self.comp_exp((x1,y1,x2,y2),exp)
					if val:
						try:
							dist += (1 if (sum(coord)%2 == sum(exp)%2) else -1)*val* \
							self.distances[(grid1[0]+coord[0],grid1[1]+coord[1])][(grid2[0]+coord[2],grid2[1]+coord[3])]
						except:
							inWall = True
							break

		#this stuff is not generalizable and hardcoded to get montezuma to work for now. 
		#Allows for ladder avatars to have part of their body inside a wall
		if inWall:
			
			wall_loc = [(grid1[0] + i,grid1[1] + j) for i in [0,1] for j in [0,1] if 
				(grid1[0] + i,grid1[1] + j) not in self.graph and i - x1 < 1 and j - y1 < 1]
			if not wall_loc:
				wall_loc = [(grid2[0] + i,grid2[1] + j) for i in [0,1] for j in [0,1] if 
				(grid2[0] + i,grid2[1] + j) not in self.graph and i - x2 < 1 and j - y2 < 1]
				wall = wall_loc[0]
				
				s = self.square_size[0]

				try:
					if grid2 in self.graph:
						A = self.geoDist(loc1,(grid2[0]*s,grid2[1]*s))
					if (grid2[0],grid2[1]+1) in self.graph:
						B = self.geoDist(loc1,(grid2[0]*s,s*(grid2[1]+1)))
					if (grid2[0]+1,grid2[1]) in self.graph:
						C = self.geoDist(loc1,(s*(grid2[0]+1),s*grid2[1]))
					if (grid2[0]+1,grid2[1]+1) in self.graph:
						D = self.geoDist(loc1,(s*(grid2[0]+1),s*(grid2[1]+1)))

					if not grid2 in self.graph:
						A = B + C - D
					if not (grid2[0],grid2[1]+1) in self.graph:
						B = A + D - C
					if not (grid2[0]+1,grid2[1]) in self.graph:
						C = A + D - B
					if not (grid2[0]+1,grid2[1]+1) in self.graph:
						D = B + C - A

					return A + (C-A)*x2 + (B-A)*y2
				except:
					return sys.maxint
			#embed()
			return self.geoDist(loc2,loc1)
			
			#return manhattanDist(loc1,loc2)/float(self.square_size[0])
			#this is wrong and only works for breakout but i dont want to worry about this right now
					
		return dist
		'''

	def loop4d(self):
		array = []
		for x1 in [0,1]:
			for y1 in [0,1]:
				for x2 in [0,1]:
					for y2 in [0,1]:
						array.append((x1,y1,x2,y2))
		return array

	def comp_exp(self,var,exp):
		prod = 1
		for i in range(4):
			if exp[i]:
					prod*=var[i]
		return prod

	#------------------------------------------------------


	#returns array of locations of objects of a given type
	#each block corresponds to 1 unit
	def findObjectsInRLE(self, rle, objName):
		try:
			objLocs = [(element.rect.left,element.rect.top) for element in rle._game.sprite_groups[objName]
			if element not in rle._game.kill_list]
		except:
			return None
		return objLocs

	#same as above but for the avatar
	#WRONG if we have avatar transitions
	def findAvatarInRLE(self, rle):
		avatar_loc = (rle._game.sprite_groups['avatar'][0].rect.left,rle._game.sprite_groups['avatar'][0].rect.top)
		return avatar_loc

	#adds spacebar to actions (ex. shooting game)
	def addSpaceBarToActions(self):
		## Note: if an object that isn't instantiated in the beginning is of a class that
		## spacebar applies to, we won't pick up on it here.
		shootingClasses = ['MarioAvatar', 'ClimbingAvatar', 'ShootAvatar', 'Switch', 'FlakAvatar']

		classes = [str(o[0].__class__) for o in self.rle._game.sprite_groups.values() if len(o)>0]
		spacebarAvailable = False
		noUp = False
		for sc in shootingClasses:
			if any([sc in c for c in classes]):
				spacebarAvailable = True
				if sc == 'MarioAvatar':
					noUp = True
					self.canJump = True
				break

		if any(['HorizontalAvatar' in c for c in classes]):
			noUp = True


		if spacebarAvailable:
			self.actions = [K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT]
		else:
			self.actions = [K_RIGHT,K_UP, K_DOWN, K_LEFT]
		if self.addWaitAction:
			self.actions.append(NONE)
		if noUp:
			self.actions.remove(K_UP)
			self.actions.remove(K_DOWN)
		return

	# returns the current avatar in the game
	def getAliveAvatar(self,rle):
		avatars = []
		for k in rle._game.sprite_groups.keys():
				for o in rle._game.sprite_groups[k]:
					if o not in rle._game.kill_list and isinstance(o,vgdl.core.Avatar):
						avatars.append(o)

		if len(avatars) >= 1:
			return avatars[0]
		#embed()
		#print "Either 0 or >1 avatars!"
		return None
		embed()

	#returns a list of all actions available to the avatar
	def getActions(self,rle):
		avatar = self.getAliveAvatar(rle)
		self.canJump = False

		if isinstance(avatar,vgdl.ontology.HorizontalAvatar):
			self.actions = [K_RIGHT,K_LEFT]

		elif isinstance(avatar,vgdl.ontology.VerticalAvatar):
			self.actions = [K_UP,K_DOWN]

		elif isinstance(avatar,vgdl.ontology.MarioAvatar):
			self.actions = [K_SPACE, K_LEFT, K_RIGHT]
			#print "MARIO"
			self.canJump = True

		else:
			self.actions = [K_RIGHT,K_UP, K_DOWN, K_LEFT]

		if self.addWaitAction:
			self.actions.append(NONE) 
		return


	#returns set of atom values, using pixel locations to calculate
	def calculateAtoms(self, rle):
		lst = []

		for k in [t for t in rle._game.sprite_groups.keys() if t not in ignored_sprites]:
			for o in rle._game.sprite_groups[k]:
				if not isinstance(o, vgdl.core.Avatar) and (not isinstance(o,vgdl.ontology.RandomNPC) and not isinstance(o,vgdl.ontology.Missile) or not REMOVE_MOVERS):
					if o not in rle._game.kill_list:
					## turn location into vector position (rows appended one after the other.) 0 if object has been killed
						pos = (o.rect.left, o.rect.top)
						vecValue = pos[1] + pos[0]*rle.outdim[0]*self.square_size[1] + 1
					else:
						vecValue = 0
					objPosCombination = self.objIDs[o.ID] + vecValue
					lst.append(objPosCombination) #unique for each object-location combination

		#avatar atom:
		avatar = self.getAliveAvatar(rle)
		if avatar is not None:
			pos = (avatar.rect.left, avatar.rect.top)
			try:
				ori = avatar.orientation
				a = 1 if ori[0] > ori[1] else 0
				b = 1 if ori[0] + ori[1] > 0 else 0
				vecValue = pos[1] + pos[0]*rle.outdim[0]*self.square_size[1] + 1 + 0.5*a + 0.25*b
			except:
				vecValue = pos[1] + pos[0]*rle.outdim[0]*self.square_size[1] + 1

			if self.speed_thresh:
				speed = avatar.speed
				if speed <= self.speed_thresh[0]:
					ind = 0
				elif speed > self.speed_thresh[-1]:
					ind = len(self.speed_thresh)
				else:
					ind = [i for i in range(1,len(self.speed_thresh)) if self.speed_thresh[i-1] < speed and self.speed_thresh[i] >=  speed][0]
				vecValue += ind/float(4*(len(self.speed_thresh)+1))

			objPosCombination = self.avatar_ID + vecValue
			lst.append(objPosCombination)


		#atom expressing which objects are currently alive
		present = []
		for k in [t for t in self.objectTypes if t not in ignored_sprites]: ##maybe add the avatar to this global state
			for o in sorted(rle._game.sprite_groups[k], key=lambda s:s.ID):
				if not isinstance(o, vgdl.core.Avatar):
					if o not in rle._game.kill_list:
						present.append(1)
					else:
						present.append(0)
		ind = sum([present[i]*2**i for i in range(len(present))]) #atom indicating which objects are alive
		lst.append(ind)

		if not self.vecSize:
			self.vecSize = len(lst)
		return set(lst)

	#returns set of atom values which use grid locations to calculate
	def gridAtoms(self,rle):
		lst = []

		for k in [t for t in rle._game.sprite_groups.keys() if t not in ignored_sprites]:
			for o in rle._game.sprite_groups[k]:
				if not isinstance(o, vgdl.core.Avatar) and (not isinstance(o,vgdl.ontology.RandomNPC) and not isinstance(o,vgdl.ontology.Missile) or not REMOVE_MOVERS):
					if o not in rle._game.kill_list:
						pos = rle._rect2pos(o.rect)
						vecValue = pos[1] + pos[0]*rle.outdim[0] + 1
					else:
						vecValue = 0
					objPosCombination = -(self.objIDs[o.ID] + vecValue)
					lst.append(objPosCombination)

		avatar = self.getAliveAvatar(rle)
		if avatar is not None:
			pos = rle._rect2pos(avatar.rect)
			vecValue = pos[1] + pos[0]*rle.outdim[0] + 1
			objPosCombination = -(self.avatar_ID + vecValue)
			lst.append(objPosCombination)
		return set(lst)


	def compareDicts(self, d1,d2):
		## only tells us what is in d2 that isn't in d1, as well as differences in values between shared keys
		return [k for k in d2.keys() if (k not in d1.keys() or d1[k]!=d2[k])]

	def delta(self, node1, node2):
		if node1 is None:
			diff = node2.state
		else:
			diff = node2.state-node1.state
		return diff

	#selects node with lowest novelty, using greatest reward as tiebreaker
	def noveltySelection(self, QNovelty, QReward):
		bestNodes = sorted(QNovelty, key=lambda n: (n.novelty, -n.intrinsic_reward))
		current = bestNodes.pop(0)
		QNovelty.remove(current)
		try:
			QReward.remove(current)
		except:
			pass
		return current

	#selects node with greatest reward (only considering those w/ novelty = 1,2), using novelty as tiebreaker
	def rewardSelection(self, QReward, QNovelty): 

		badNodes = []
		for n in QReward:
			if n.novelty >= 3:
				badNodes.append(n)
		for n in badNodes:
			QReward.remove(n)
		try:
			best = min(QReward)
			current = random.choice([i for i in QReward if i.__eq__(best)])
			QReward.remove(current)
			return current
		except:
			return None

 	def BFS_profiler(self):
 		lp = LineProfiler()
 		lp_wrapper = lp(self.BFS)
 		lp_wrapper()
 		lp.print_stats()


 	#Runs our best-first search algorithm with novelty pruning
	def BFS(self,return_best = False):
		QNovelty, QReward = [], []
		visited, rejected = [], []
		start = Node(self.rle, self, [], None)
		start.rle = self.rle
		#visited.append(start)
		start.eval()
		QReward.append(start)
		
		i=0
		path = []
		wins = 0
		min_path_length = sys.maxint
		best_path = None
		best_node = None
		found_key = False

		while (len(QNovelty)>0 or len(QReward)>0) and i<self.max_nodes:
		
			current = self.rewardSelection(QReward, QNovelty)

			if current is None:
				self.quitting = True
				#print(i)
				print("quitting, no novel node found")
				#embed()
				break
				
			self.statesEncountered.append(current.rle._game.getFullState())
			current.updateNoveltyDict(QNovelty, QReward)
			visited.append(current)
			#print current.predict
			'''
			print(i)
			print(current.rle.show())
			'''
			avatar = self.getAliveAvatar(current.rle)
			if avatar is not None:
				loc = current.rle._rect2pos(avatar.rect)
				if len([o for o in current.rle._game.kill_list if o in current.rle._game.sprite_groups['key']]) > 0:
					self.key[loc] += 1
					print 'key'
				else:
					self.no_key[loc] += 1
				self.avatar_locs_disc[loc] += 1
				#print loc
			else:
				print "NO AVATAR"
				#embed()
			print avatar
			if i % 500 == 0:
				print self.avatar_locs_disc
				print self.key
			
			
			self.getActions(current.rle)

			actions = self.actions
			if self.canJump:
				try:
					if self.getAliveAvatar(current.rle).jumping:
						actions = [NONE]
				except:
					pass

			for a in actions:
				#if a == K_SPACE:
				#	embed()
				child = Node(self.rle, self, current.actionSeq+[a], current)
				child.eval()

				if child.win:
					# Get the gameString representation of the RLE at each
					# timestep in the chosen solution, so as to be able to
					# compare it to the agent's RLE at execution time and
					# correct for stochasticity effects
					#wins += 1
					self.winning_states.append(child)
					ended, win, t = child.rle._isDone(getTermination=True)
					self.solution = child.actionSeq
					self.statesEncountered.append(child.rle._game.getFullState())
					print "win"

					# node = child
					# gameString_array = []
					# object_positions_array = []
					# while node is not None:
					# 	gameString_array.append(node.rle.show())
					# 	object
					# 	node = node.parent
					# self.gameString_array = gameString_array[::-1]
					# child.rle._isDone()
					# self.solution = child.actionSeq
					
					# print(child.rle.show(indent=True))
					#path.append(child.rle.show(indent=True))
					

					# if len(gameString_array) < min_path_length:
					# 	best_path = gameString_array
					# 	best_node = child
					# 	min_path_length = len(gameString_array)

					# if wins >= self.num_paths:
					# 	print i
					# 	print "{} paths found, returning best".format(wins)
					# 	return best_node, best_path, i

				else:
					#if child.isTerminal() and not child.isWin():
					#	print("LOSE")
					#else:
					QReward.append(child)
					#QNovelty.append(child)
			i+=1

			if self.winning_states:
				print "we have {} winning states".format(len(self.winning_states))
				bestNodes = sorted(self.winning_states, key=lambda n: (-n.intrinsic_reward))
				bestNode = bestNodes[0]
				node = bestNode
				gameString_array, object_positions_array = [], []
				while node is not None:
					gameString_array.append(node.rle.show(color='green'))
					object_positions_array.append(node.rle)
					node = node.parent
				self.gameString_array = gameString_array[::-1]
				self.object_positions_array = object_positions_array[::-1]
				# gameString_array.append(bestNode.rle.show())
				# object_positions_array.append(copy.deepcopy(bestNode.rle))
				return bestNode, gameString_array, object_positions_array

		self.solution = []#Node(self.rle, self, [], None)
		if i>=self.max_nodes:
			if self.short_horizon:
				print "playing with short horizon; reached max of {} nodes".format(self.max_nodes)
				node = max(visited, key=lambda n:n.intrinsic_reward)
				parentNode = copy.deepcopy(node)
				self.solution = node.actionSeq
				print self.solution
				gameString_array, object_positions_array = [], []
				while parentNode is not None:
					gameString_array.append(parentNode.rle.show())
					object_positions_array.append(copy.deepcopy(parentNode.rle))
					parentNode = parentNode.parent
				self.gameString_array = gameString_array[::-1]
				self.object_positions_array = object_positions_array[::-1]
				# print "win"
				# embed()
				return node, gameString_array, object_positions_array
			else:
				# self.quitting = True
				print "Got no plan after searching {} nodes".format(self.max_nodes)
		return None, None, None
		# if return_best:
		# 	#embed()
		# 	visited.remove(start)
		# 	best = min(visited)
		# 	last = random.choice([n for n in visited if n.__eq__(best)])
			
		# 	return last, visited, i
		# 	#should remove visited later

		# self.solution = []
		# if i>=self.max_nodes:
		# 	self.quitting = True
		# 	print "Quitting after {} nodes".format(self.max_nodes)
		# else:
		# 	print "No novel nodes found"
		# print "{} paths found, returning best".format(wins)
		# return best_node, best_path, i

	def node_profiler(self,lock,QReward,QNovelty,visited,p):
		lp = LineProfiler()
 		lp_wrapper = lp(self.openNode)
 		lp_wrapper(lock,QReward,QNovelty,visited,p)
 		lp.print_stats()

 	#algorithm of one process in our parallelized BFS
	def openNode(self, lock,QReward,QNovelty,visited,p):
		generated_nodes = []
		while self.nodes < self.max_nodes and not self.won and self.wait_steps < 3*p:
			lock.acquire()
			try:
			
				QReward.extend(generated_nodes)
				generated_nodes = []
				current = self.rewardSelection(QReward, QNovelty)

				if current is None:
					wait = True
					self.wait_steps += 1
				else:
					self.wait_steps = 0
					wait = False
					self.nodes += 1
					print self.nodes
					avatar = self.getAliveAvatar(current.rle)

					if avatar is not None:
						loc = current.rle._rect2pos(avatar.rect)
						self.avatar_locs_disc[loc]+=1
						print loc
					else:
						print "NOT ALIVE"
					if self.nodes % 500 == 0:
						print self.avatar_locs_disc
					self.statesEncountered.append(current.rle._game.getFullState())
					current.updateNoveltyDict(QNovelty, QReward)
					visited.append(current)

					self.getActions(current.rle)

					actions = self.actions

			finally:
				lock.release()

			if wait:
				time.sleep(1)
				#print "sleeping"
			if current is not None and not self.won:

				#avatar = self.getAliveAvatar(current.rle)
				#print self.nodes
				#if avatar is not None:
				#	loc = current.rle._rect2pos(avatar.rect)
				#	print loc

				if self.canJump:
					try:
						if self.getAliveAvatar(current.rle).jumping:
							actions = [NONE]
					except:
						pass

				for a in actions:
					child = Node(self.rle, self, current.actionSeq+[a], current)
					child.eval()
					generated_nodes.append(child)

					if child.win:
						self.won = True
						node = child
						gameString_array = []
						while node is not None:
							gameString_array.append(node.rle.show())
							node = node.parent
						self.gameString_array = gameString_array[::-1]
						child.rle._isDone()
						self.solution = child.actionSeq
						self.statesEncountered.append(child.rle._game.getFullState())
						print(child.rle.show(indent=True))
						print("WIN!")
						break

	#our parallelized BFS algorithm, to run on openmind
	#NOTE - doesn't work yet, since python 2 threading doesn't actually speed anything up
	def parallelBFS(self, num_processes, return_best=True):
		QNovelty, QReward = [], []
		visited, rejected = [], []
		start = Node(self.rle, self, [], None)
		start.rle = self.rle
		#visited.append(start)
		start.eval()
		QReward.append(start)
		self.nodes = 0
		lock = Lock()
		self.won=False
		
		#i=0
		path = []
		wins = 0
		min_path_length = sys.maxint
		best_path = None
		best_node = None
		found_key = False

		threads = []
		for i in range(num_processes):
			threads.append(Thread(target=self.openNode, args=(lock,QReward,QNovelty,visited,num_processes)))
			threads[i].start()

		for i in range(num_processes):
			threads[i].join()

		if self.wait_steps >= 3*num_processes:
			print "quitting, no novel node found"

		if return_best:
			#embed()
			visited.remove(start)
			best = min(visited)
			last = random.choice([n for n in visited if n.__eq__(best)])
			
			return last, visited, self.nodes

#Class for a node in our search tree
class Node():
	def __init__(self, rle, WBP, actionSeq, parent):
		self.rle = rle
		self.WBP = WBP
		self.actionSeq = actionSeq
		self.parent = parent
		self.state = {} #values of atoms
		self.grid_state = {}
		self.candidates = []
		self.grid_candidates = []
		self.pixel_novelty = None
		self.grid_novelty = None
		self.novelty = None
		self.reward = None
		self.intrinsic_reward = 0
		self.metabolic_cost = 0
		self.children = None
		self.reconstructed=False
		self.expanded = False
		self.rolloutDepth = ROLLOUT_DEPTH
		if self.parent is not None:
			self.rolloutArray = parent.rolloutArray[1:]
		else:
			self.rolloutArray = []

		self.rand = random.random() #random id given to each node, used for picking a random node in reward selection

		if self.parent is None:
			self.depth = 1
		else:
			self.depth = self.parent.depth + 1

	def __eq__(self,other):
		#return (-self.intrinsic_reward, self.novelty, self.rand) == (-other.intrinsic_reward, other.novelty, other.rand)
		return (-self.intrinsic_reward, self.novelty) == (-other.intrinsic_reward, other.novelty)

	def __gt__(self,other):
		#return (-self.intrinsic_reward, self.novelty, self.rand) > (-other.intrinsic_reward, other.novelty, other.rand)
		return (-self.intrinsic_reward, self.novelty) > (-other.intrinsic_reward, other.novelty)


## when to trigger rollouts, if any
## rollout length
## repeating rollouts if death? e.g., are they optimistic?
## multiple samples??
	def metabolics(self, rle, events, action, n=N_METABOLICS, mult=MULT_METABOLICS):

		metabolic_cost = 1./n
		#if action==32:
		if action!=NONE:
			metabolic_cost += (1-1./n)*mult
		if len(events)>0:
			# metabolic_cost = .3
			if any([rle._game.sprite_groups['avatar'][0].ID in e and e[0]=='bounceForward' for e in events]):
				metabolic_cost += .3#(1-1./n)*mult
			# if any([rle._game.sprite_groups['avatar'][0].ID in e and e[0]=='killSprite' for e in events]):
			# 	metabolic_cost += 0.3
		if not DO_METABOLICS:
			return 0.0
		#print metabolic_cost
		return metabolic_cost

	#computes the value of a rollout
	def rollout(self, vrle):
		successfulRollout = False
		tries = 0
		while not successfulRollout and tries < 5:
			vrle = copy.deepcopy(vrle)
			prevHeuristicVal = self.heuristics(vrle)
			rolloutArray = []
			i=0
			terminal, win = vrle._isDone()
			while i<self.rolloutDepth and not terminal:

				a = random.choice(self.WBP.actions)
				vrle.step(a)

				currHeuristicVal = self.heuristics(vrle)
				heuristicVal = currHeuristicVal-prevHeuristicVal
				rolloutArray.append(heuristicVal)
				prevHeuristicVal = currHeuristicVal

				terminal, win = vrle._isDone()
				i+=1

			if terminal and not win:
				successfulRollout = False
				tries += 1
				#print "rolling out again"
			else:
				successfulRollout = True
		return rolloutArray

	#heuristics: --------------------------------------------------------------
	def spritecounter_val(self, theory, term, stype, rle, first_alpha=1000,
						  second_alpha=1):
		val = 0
		compute_second_order = True

		# Check if condition is win or loss and multiply accordingly
		if term.termination.win:
			mult = -WIN_RATIO
		else:
			# compute_second_order = False
			mult = 1

		# Get all types that kill or transform stype
		killer_types = [
			inter.slot2 for inter in theory.interactionSet
			if (inter.interaction in ["killSprite","killIfOtherHasMore"] and
				not inter.generic
				and inter.slot1 == stype)]

		# Get attributes from terminationSet
		limit = term.termination.limit

		if 'SpawnPoint' in str(theory.classes[stype][0].vgdlType) and not killer_types:
			distance_to_goal = 0
			## Special case, where you want to track whether that spawnPoint has a limit, etc.
			## Distance to goal here is how many sprites the spawnPoint still has to shoot before it expires.
			for o in rle._game.sprite_groups[stype]:
				distance_to_goal += abs(o.total-o.counter)
			val += mult * first_alpha * distance_to_goal
			return val
		else:
			## Normal case
			n_stypes = len([0 for sprite in self.WBP.findObjectsInRLE(rle, stype)])

			distance_to_goal = abs(n_stypes - limit)

		val += mult * first_alpha * distance_to_goal

		if compute_second_order:
			## Get all positions of objects whose type is in killer_types; compute minimum distance
			## of each to the stypes we have to destroy. Return min over all mins.
			# embed()
			objs = []
			for ktype in killer_types:
				objs.extend(self.WBP.findObjectsInRLE(rle, ktype))
			if len([i for i in killer_types if 'avatar' in i]) > 0:
				avatar = self.WBP.getAliveAvatar(rle)
				if avatar:
					if isinstance(avatar,vgdl.ontology.BreakoutAvatar):
						pos = (avatar.rect.x + C*rle._game.block_size, avatar.rect.y)
					else:
						pos = (avatar.rect.x,avatar.rect.y)
					if pos not in objs:
						objs.append((avatar.rect.x,avatar.rect.y))
			kill_positions = objs

			stype_positions = self.WBP.findObjectsInRLE(rle, stype)
			try:
				# A consequence of the two-way generic interactions in the
				# theory is that minimum-distance object pairs whose interactions
				# were not yet observed will have their distance penalized twice
				# as much when none of those objects is an avatar. This implies
				# that avatar novel interactions will be favored over other ones
				possiblePairList = [self.WBP.geoDist(pos,obj)
					for pos in kill_positions
					for obj in stype_positions]

				distance = min(possiblePairList)
			except ValueError:
				distance = 0

			if possiblePairList:
				#n_sprites = len(possiblePairList)
				n_sprites = 100
				#CHANGING FOR NOW TO DEAL WITH HAVING THIS HEURISTIC USE ANY AVATAR OBJECT
				# Normalize by number of sprites, enforcing a prior that encourages
				# goals that involve killing fewer objects
				val += float(mult * second_alpha * distance)/n_sprites
			else:
				distance = 10000
				val += float(mult * second_alpha * distance)

		return val

	def multispritecounter_val(self, theory, term, rle, first_alpha=1000,
							   second_alpha=1):
		val = 0
		for stype in term.termination.stypes:
			val += self.spritecounter_val(theory, term, stype, rle,
				first_alpha=first_alpha, second_alpha=second_alpha)
			# print stype, val
		return val

	def noveltytermination_val(self, theory, term, s1, s2, rle, first_alpha=1000,
						  second_alpha=1):
		val = 0
		compute_second_order = True

		# Check if condition is win or loss and multiply accordingly
		if term.termination.win:
			mult = -1
		else:
			compute_second_order = False
			mult = 1

		if compute_second_order:
			## Get all positions of objects whose type is in killer_types; compute minimum distance
			## of each to the stypes we have to destroy. Return min over all mins.
			# embed()
			s2_positions = self.WBP.findObjectsInRLE(rle, s2)
			s1_positions = self.WBP.findObjectsInRLE(rle, s1)

			"""
			# Second order lesion
			if s1 != 'avatar' and s2 != 'avatar':
				return 0
			"""

			n_sprites = len(s1_positions)
			try:
				# A consequence of the two-way generic interactions in the
				# theory is that minimum-distance object pairs whose interactions
				# were not yet observed will have their distance penalized twice
				# as much when none of those objects is an avatar. This implies
				# that non-avatar novel interactions will be favored over others
				
				
				possiblePairList = [self.WBP.geoDist(obj,pos)
					 for pos in s2_positions
					 for obj in s1_positions
					 if self.WBP.geoDist(obj,pos) != 0]
				

				distance = min(possiblePairList)
					 # This is a trick to avoid getting distance 0 for objects
					 # of same type. If the list turns out to be empty, it will
					 # raise an error and set the distance to 0
			except ValueError:
				distance = 0

			if possiblePairList:
				n_sprites = len(possiblePairList)
				# Normalize by number of sprites, enforcing a prior that encourages
				# goals that involve killing fewer objects
				val += float(mult * second_alpha * distance)/n_sprites

		return val

	def timeout_val(self, theory, term, rle):
		val = 0
		limit = term.termination.limit

		# Check if condition is win or loss and multiply accordingly
		if term.termination.win:
			mult = -1
		else:
			mult = 1

		time_elapsed = rle._game.time
		distance_to_goal = abs(time_elapsed - limit)

		val += mult * distance_to_goal

		return val

	#--------------------------- a bit of a cheat, should remove these

	#gives reward for being close to objects that don't killyou
	def objcollect_val(self, theory, rle, weight=OBJCOLLECT_WEIGHT):
		objs = rle._game.sprite_groups.keys()
		for inter in theory.interactionSet:
			if inter.interaction == 'killSprite' and inter.slot1 == 'avatar':
				objs.remove(inter.slot2)
		objs.remove('wall')
		objs.remove('avatar')
		#objs.remove('background')

		avatar = self.WBP.getAliveAvatar(rle)
		if avatar is None:
			return 0
		if isinstance(avatar,vgdl.ontology.BreakoutAvatar):
			pos = (avatar.rect.x + C*rle._game.block_size, avatar.rect.y)
		else:
			pos = (avatar.rect.x,avatar.rect.y)

		min_dist = 100
		
		for obj in objs:
			locs = self.WBP.findObjectsInRLE(rle,obj)
			try:
				dist = [self.WBP.geoDist(pos,x) for x in locs]
				if dist:
					val = min(dist)
					if val < min_dist:
						min_dist = min(min_dist,val)
			except:
				print 'no distance available, or unable to calculate'
				pass
			

		#embed()

		return -weight*min_dist

	#predicts where the ball will be, and moves to that location
	def predictball_val(self, rle, weight = 0.0):
	
		try:
			y = self.WBP.getAliveAvatar(rle).rect.y
			ball = [i for i in rle._game.sprite_groups['ball'] if i not in rle._game.kill_list][0]
		except:
			return 0
		dx = ball.speed*ball.orientation[0]
		dy = ball.speed*ball.orientation[1]
		if dy <= 0.1:
			return 0

		t = (y - ball.rect.y)/dy
		x_pred = ball.rect.x + t*dx

		left = rle._game.block_size
		right = rle._game.block_size*(rle.outdim[1]-1) - ball.rect.width

		count = 0
		while x_pred < left or x_pred > right:
			count += 1
			if x_pred < left:
				x_pred = 2*left - x_pred
			else:
				x_pred = 2*right - x_pred

			if count > 20:
				embed()

		self.pred_x = x_pred


		dist = abs(self.WBP.getAliveAvatar(rle).rect.x + C*rle._game.block_size - x_pred)/rle._game.block_size

		return -weight*dist


	#-----------------------------------------------
	#Calculates the sum of all heuristics
	def heuristics(self, rle=None, first_alpha=ALPHA1, second_alpha=ALPHA2,
				   time_alpha=10):

		if rle==None:
			rle = self.rle

		theory = self.WBP.theory
		heuristicVal = 0
		avatarNoveltyVals = []

		for term in theory.terminationSet:

			if isinstance(term, SpriteCounterRule):
				spritecounter_val = self.spritecounter_val(theory, term, term.termination.stype, rle,
					first_alpha=first_alpha, second_alpha=second_alpha)
				#print("spritecounter = {}".format(spritecounter_val))
				heuristicVal += spritecounter_val

			elif isinstance(term, MultiSpriteCounterRule):
				multispritecounter_val = self.multispritecounter_val(theory, term, rle,
						first_alpha=first_alpha, second_alpha=second_alpha)
				#print("mulitspritecounter = {}".format(multispritecounter_val))
				heuristicVal += multispritecounter_val

			elif isinstance(term, TimeoutRule):
				timeout_val = time_alpha * \
					self.timeout_val(theory, term, rle)
				heuristicVal += timeout_val

			elif isinstance(term, NoveltyRule):
				noveltytermination_val = self.noveltytermination_val(
					theory, term, term.termination.s1, term.termination.s2, rle,
					first_alpha=first_alpha, second_alpha=second_alpha)
				#print("NOVELTY")
				# print("noveltytermination_val for {} and {} is equal to {}".format(
					# term.termination.s1, term.termination.s2, noveltytermination_val))
				if 'avatar' == term.termination.s2:
					avatarNoveltyVals.append(.5*self.WBP.annealing*noveltytermination_val)
				else:	
					heuristicVal += .5 * self.WBP.annealing * noveltytermination_val

		if avatarNoveltyVals:
			heuristicVal += max(avatarNoveltyVals)

		#heuristicVal += self.objcollect_val(theory, rle)

		return heuristicVal

	#returns the rle (with total action sequence) and whether game has been won
	def getTo_profiler(self):
		lp = LineProfiler()
 		lp_wrapper = lp(self.getToCurrentState)
 		output = lp_wrapper()
 		lp.print_stats()
 		return output
 	
 	#copies rle and takes steps to reach the current state
	def getToCurrentState(self):
		if self.parent and self.parent.rle is not None:
			
			## try to copy parent lastState. Then take action and store as current lastState.
			## if that fails, replay from beginning and store as current lastState
			try:
				#embed()
				vrle = cPickle.loads(cPickle.dumps(self.parent.rle, -1))
				
				if len(self.actionSeq)>0:
					
					a = self.actionSeq[-1]

					res = vrle.step(a)
					
					# relevantEvents = [t for t in res['effectList'] if t[0] == 'stepBack']
					# if relevantEvents:
					# 	import ipdb;ipdb.set_trace()
					self.metabolic_cost = self.parent.metabolic_cost + self.metabolics(vrle, res['effectList'], a)

					terminal, win = vrle._isDone()
			except:
				print "conditions met but copy failed"
				embed()
		else:
			self.reconstructed=True
			vrle = cPickle.loads(cPickle.dumps(self.rle, -1))
			terminal, win = vrle._isDone()
			i=0
			while not terminal and len(self.actionSeq)>i:
				a = self.actionSeq[i]
				res = vrle.step(a)
				self.metabolic_cost += self.metabolics(vrle, res['effectList'], a)
				terminal, win = vrle._isDone()
				i += 1
		return vrle, win

	def eval_profiler(self):
 		lp = LineProfiler()
 		lp_wrapper = lp(self.eval)
 		lp_wrapper()
		lp.print_stats()

	#whether to do a rollout (specifically, whether this game is breakout or not)
	#currently calculates
	def do_rollout(self):
		try:
			ball_now = [i for i in self.rle._game.sprite_groups['ball'] if i not in self.rle._game.kill_list][0]
			ball_prev = [i for i in self.parent.rle._game.sprite_groups['ball'] if i not in self.parent.rle._game.kill_list][0]

			return (ball_now.orientation[1] < 0 and ball_prev.orientation[1] > 0)
		except:
			return False


	def eval(self):
		# Evaluate current node, including calculating intrinsic reward: f(rewards, heuristics, etc.)
		self.rle, self.win = self.getToCurrentState()

		self.updateObjIDs(self.rle)
		self.state = self.WBP.calculateAtoms(self.rle) #new atom values
		self.grid_state = self.WBP.gridAtoms(self.rle)

		for i in range(1,3):
			for c in itertools.combinations(self.state, i):
				c = tuple(sorted(c))
				if self.WBP.trueAtoms[c] < self.WBP.LIMIT:
					self.candidates.append(c)

		for i in range(1,3):
			for c in itertools.combinations(self.grid_state, i):
				c = tuple(sorted(c))
				if self.WBP.trueAtoms[c] < self.WBP.GRID_LIMIT:
					self.grid_candidates.append(c)

		self.updateNovelty() #calculates novelty based on state of node (1, 2, 3)

		if len(self.actionSeq)>0 and self.do_rollout():
			self.rolloutArray = self.rollout(self.rle)
			print "in rollout"

		self.heuristicVal = self.heuristics()
		self.predict = self.predictball_val(self.rle)

		# print self.lastState._game.score, self.heuristicVal, sum(self.rolloutArray), self.metabolic_cost
		self.intrinsic_reward = self.rle._game.score + self.heuristicVal\
		- self.metabolic_cost+sum(self.rolloutArray) + DEPTH_WEIGHT*self.depth + self.predict
		
		return self.win

	#update the novelty of a single atom
	def updateNovelty(self):
		if len(self.candidates)==0:
			self.pixel_novelty = 3
		else:
			self.pixel_novelty = min([len(c) for c in self.candidates])

		if len(self.grid_candidates)==0:
			self.grid_novelty = 3
		else:
			self.grid_novelty = min([len(c) for c in self.grid_candidates])

		self.novelty = max(self.grid_novelty,self.pixel_novelty)
		return self.novelty

	#update the novelty of atoms in the Queue
	def updateNoveltyDict(self, QNovelty, QReward):

		jointSet = list(QReward)

		for c in self.candidates:

			changed = False
			if self.WBP.trueAtoms[c] < self.WBP.LIMIT:
				self.WBP.trueAtoms[c] += 1
				changed = True
			if changed and self.WBP.trueAtoms[c] == self.WBP.LIMIT:
				for n in jointSet:
					if c in n.candidates:
						n.candidates.remove(c)

		for c in self.grid_candidates:

			changed = False
			if self.WBP.trueAtoms[c] < self.WBP.GRID_LIMIT:
				self.WBP.trueAtoms[c] += 1
				changed = True
			if changed and self.WBP.trueAtoms[c] == self.WBP.GRID_LIMIT:
				for n in jointSet:
					if c in n.grid_candidates:
						n.grid_candidates.remove(c)

		for n in jointSet:
			n.novelty = n.updateNovelty()
		return

	#update IDs if we get new objects
	def updateObjIDs(self, vrle):
		i = 0
		for objType in vrle._game.sprite_groups:
			for s in vrle._game.sprite_groups[objType]:
				if s.ID not in self.WBP.objIDs.keys() and not isinstance(s,vgdl.core.Avatar):
					if s.name=='bullet':
						s.ID = len([o for o in vrle._game.sprite_groups[objType] if o not in vrle._game.kill_list])
					else:
						s.ID = len(vrle._game.sprite_groups[objType])
					self.WBP.objIDs[s.ID] = (len(self.WBP.objIDs.keys())+1) * (self.WBP.vecDim[0]+self.WBP.padding)
					i+=1
		return

	def isTerminal(self):
		return self.rle._isDone()[0]

	def isWin(self):
		return self.rle._isDone()[1]

	#does this do anything???
	def playBack(self, make_movie=False):

		self.finalStatesEncountered = []
		terminal = vrle._isDone()[0]
		i=0
		if not make_movie:
			print vrle.show()
		while not terminal and i<len(self.actionSeq):
			a = self.actionSeq[i]
			vrle.step(a)
			if not make_movie:
				print actionDict[a]
				print vrle.show()
			else:
				self.finalStatesEncountered.append(vrle._game.getFullState())
			terminal = vrle._isDone()[0]
			i+=1


def euclideanDist(a,b):
	return math.sqrt(float((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2))

def manhattanDist(a,b):
	return (abs(b[0] - a[0]) + abs(b[1] - a[1]))

#runs multiple planners in series with different sets of parameters
def multi_plan():
	t1 = time.time()
	gameFilename = "examples.continuousphysics.montezuma_new"
	#gameFilename = "examples.continuousphysics.collect_resource"
	gameString, levelString = defInputGame(gameFilename, randomize=True)
	rleCreateFunc = lambda: createRLInputGame(gameFilename)
	rle = rleCreateFunc()

	params = [(3,150),(3,200),(3,250),(3,300)]
	result = []
	for param in params: 
		print param
		p = WBP(rle,gameFilename,limit=param[0],grid_limit=param[1])
		last, gameString_array, nodes = p.BFS()
		result.append((gameString_array,nodes))

	i = 0

	for [gameString_array,nodes] in result:
		print params[i]
		print("nodes searched = {}".format(nodes))
		if gameString_array is not None:
			print("SUCCESS! path length = {}".format(len(gameString_array)))
		else:
			print("FAILURE")
		i += 1

	print time.time()-t1
	embed()



if __name__ == "__main__":

	## Continuous physics games can't work right now. RLE is discretized, getSensors() relies on this, and a lot of the induction/planning
	## architecture depends on that. Will take some work to do this well. Best plan is to shrink the grid squares and increase speeds/strengths of
	## objects.
	#gameFilename = "examples.continuousphysics.mario_small"
	#gameFilename = "examples.continuousphysics.avoid_goomba"
	#gameFilename = "examples.continuousphysics.mario"
	#gameFilename = "examples.continuousphysics.montezuma_new"
	#gameFilename = "examples.continuousphysics.montezuma_3"
	#gameFilename = "examples.continuousphysics.montezuma_medium"
	#gameFilename = "examples.continuousphysics.ladder"
	#gameFilename = "examples.continuousphysics.simple"
	#gameFilename = "examples.continuousphysics.crossroad"
	#gameFilename = "examples.continuousphysics.collect_key"
	#gameFilename = "examples.continuousphysics.collect_resource"
	gameFilename = "examples.continuousphysics.rope_test"
	#gameFilename = "examples.gridphysics.simple_grid"
	#gameFilename = "examples.gridphysics.boulderdash" #Game is buggy.
	#gameFilename = "examples.gridphysics.expt_exploration_exploitation"
	#gameFilename = "examples.continuousphysics.ptsp_simple"
	#gameFilename = "examples.continuousphysics.ptsp"
	#gameFilename = "examples.continuousphysics.breakout"

	
	gameString, levelString = defInputGame(gameFilename, randomize=True)

	rleCreateFunc = lambda: createRLInputGame(gameFilename)
	
	#gameFilename = "examples.continuousphysics.montezuma_3"
	#rleCreateFunc = lambda: createRLInputGameFromPositions(gameFilename)


	rle = rleCreateFunc()

	times = []

	t1 = time.time()
	p = WBP(rle, gameFilename)
	
	last, gameString_array, nodes = p.parallelBFS(1)
	print p.avatar_locs_disc
	print last
	print len(last.actionSeq)
	#print len(gameString_array)
	print p.nodes
	print p.won
	print time.time()-t1
