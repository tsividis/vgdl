from IPython import embed
import itertools
import numpy as np
from numpy import zeros
import pygame
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
from collections import defaultdict, deque
import time
import ipdb
import vgdl
import heapq
import copy
from threading import Lock
from Queue import Queue
from util import *
import multiprocessing
from ontology import Immovable, Passive, Resource, ResourcePack, RandomNPC, Chaser, AStarChaser, OrientedSprite, Missile
from ontology import initializeDistribution, updateDistribution, updateOptions, sampleFromDistribution, spriteInduction, selectObjectGoal
from theory_template import TimeStep, Precondition, InteractionRule, TerminationRule, TimeoutRule, SpriteCounterRule, MultiSpriteCounterRule, \
NoveltyRule, generateSymbolDict, ruleCluster, Theory, Game, writeTheoryToTxt, generateTheoryFromGame
from rlenvironmentnonstatic import createRLInputGame

from line_profiler import LineProfiler
import cPickle

from pygame.locals import K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT
NONE = 0
ACTIONS = [K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT, NONE]
actionDict = {K_SPACE: 'space', K_UP: 'up', K_DOWN: 'down', K_LEFT: 'left', K_RIGHT: 'right', NONE: 'wait'}

WALL_EDGE = 1
MAX_TIMES_IN_SQUARE = sys.maxint

REMOVE_MOVERS = True

## Base class for width-based planners (IW(k) and 2BFS)
class WBP():
	def __init__(self, rle, gameFilename, theory=None, fakeInteractionRules = [], annealing=1, max_nodes=10000, limit=4):
		self.rle = rle
		self.gameFilename = gameFilename
		self.T = len(rle._obstypes.keys())+1 #number of object types. Adding avatar, which is not in obstypes.
		
		self.trueAtoms = defaultdict(lambda:0) #set() ## set of atoms that have been true at some point thus far in the planner.
		self.objectTypes = rle._game.sprite_groups.keys()
		self.objectTypes.sort() #wall, avatar, etc.
		self.phiSize = sum([len(rle._game.sprite_groups[k]) for k in rle._game.sprite_groups.keys() if k not in ['wall', 'avatar']])#number of not wall/avatar objects
		self.avatar = rle._game.sprite_groups["avatar"][0]
		self.square_size = (self.avatar.rect.width,self.avatar.rect.height)
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
		if theory == None:
			self.theory = generateTheoryFromGame(rle, alterGoal=False)
		else:
			self.theory=theory
		print 'max nodes', self.max_nodes

		self.avatar_ID = None

		# for rule in self.theory.interactionSet:
		# 	if 'stepBack'==rule.interaction:
		# 		ipdb.set_trace()
		i=1
		#embed()
		for k in rle._game.all_objects.keys():
			self.objIDs[k] = i * (self.vecDim[0]+self.padding)
			if isinstance(rle._game.all_objects[k]['sprite'],vgdl.core.Avatar):
				self.avatar_ID = i * (self.vecDim[0]+self.padding)
			i+=1

		self.canJump = False

		self.addSpaceBarToActions()

		self.avatar_locs = set()

		#move away from squares we've already been in heuristic:
		self.visited = [[0,0],0]
		
		self.all_locs = []

		self.avatar_locs_disc = defaultdict(lambda:0)
		self.key = defaultdict(lambda:0)
		self.no_key = defaultdict(lambda:0)
		self.graph = {}
		self.distances = self.dijkstra()
		self.box_weights = self.calc_weights()

		self.num_paths = 1
		self.all_paths = []

		self.LIMIT = 3
		self.GRID_LIMIT = 100

	def makeGraph(self):
		graph = {}
		wallLocs = self.findObjectsInRLE(self.rle,'wall')
		wallLocs = set([(x[0]/self.square_size[0],x[1]/self.square_size[1]) for x in wallLocs])
		for i in range(self.rle.outdim[1]):
			for j in range(self.rle.outdim[0]):
				#(i,j) is grid_loc
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
		
	def calc_weights(self):
		weights = {}
		for (x,y) in self.graph:
			w = 1.0
			if (x+1,y) not in self.graph:
				w = w/self.square_size[0]
			if (x,y+1) not in self.graph:
				w = w/self.square_size[1]
			weights[(x,y)] = w
		return weights

	def grid(self,loc):
		return (loc[0]/self.square_size[0],loc[1]/self.square_size[1])

	#return geodesic distance between two locations
	def geoDist(self,loc1,loc2):
		
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

		#this stuff is not generalizable and hardcoded to get montezuma to work for now
		if inWall:
			wall_loc = [(grid1[0] + i,grid1[1] + j) for i in [0,1] for j in [0,1] if 
				(grid1[0] + i,grid1[1] + j) not in self.graph and i - x1 < 1 and j - y1 < 1]
			#embed()
			if not wall_loc:
				wall_loc = [(grid2[0] + i,grid2[1] + j) for i in [0,1] for j in [0,1] if 
				(grid2[0] + i,grid2[1] + j) not in self.graph and i - x2 < 1 and j - y2 < 1]
				#embed()
				wall = wall_loc[0]
				
				s = self.square_size[0]

				try:
					if grid2 in self.graph:
						A = self.geoDist(loc1,(grid2[0]*s,grid2[1]*s))
						#print A
					if (grid2[0],grid2[1]+1) in self.graph:
						B = self.geoDist(loc1,(grid2[0]*s,s*(grid2[1]+1)))
						#print B
					if (grid2[0]+1,grid2[1]) in self.graph:
						C = self.geoDist(loc1,(s*(grid2[0]+1),s*grid2[1]))
						#print C
					if (grid2[0]+1,grid2[1]+1) in self.graph:
						D = self.geoDist(loc1,(s*(grid2[0]+1),s*(grid2[1]+1)))
						#print D

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
					#embed()
					return sys.maxint

			return self.geoDist(loc2,loc1)
					
		return dist

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

	def getAliveAvatar(self,rle):
		#embed()

		avatars = []
		for k in rle._game.sprite_groups.keys():
				for o in rle._game.sprite_groups[k]:
					if o not in rle._game.kill_list and isinstance(o,vgdl.core.Avatar):
						avatars.append(o)

		if len(avatars) == 1:
			#print avatars[0]
			return avatars[0]

		print "Either 0 or >1 avatars!"
		return None
		embed()

	def getActions(self,rle):
		#embed()
		avatar = self.getAliveAvatar(rle)
		#classes = [str(o[0].__class__) for o in rle._game.sprite_groups.values() if len(o)>0]
		self.canJump = False
		#embed()
		#print avatar.__class__
		if isinstance(avatar,vgdl.ontology.HorizontalAvatar):
			self.actions = [K_RIGHT,K_LEFT]

		elif isinstance(avatar,vgdl.ontology.VerticalAvatar):
			#print 'Vertical'
			self.actions = [K_UP,K_DOWN]

		elif isinstance(avatar,vgdl.ontology.MarioAvatar):
			#print('Mario')
			self.actions = [K_SPACE, K_LEFT, K_RIGHT]
			self.canJump = True

		else:
			self.actions = [K_RIGHT,K_UP, K_DOWN, K_LEFT]

		if self.addWaitAction:
			self.actions.append(NONE) 
		return


	#returns set of atom values
	def calculateAtoms(self, rle):
		lst = []

		#embed()
		for k in [t for t in rle._game.sprite_groups.keys() if t not in ['wall', 'background','ladder']]:
			for o in rle._game.sprite_groups[k]:
				if not isinstance(o, vgdl.core.Avatar) and (not isinstance(o,vgdl.ontology.RandomNPC) and not isinstance(o,vgdl.ontology.Missile) or not REMOVE_MOVERS):
					if o not in rle._game.kill_list:
					## turn location into vector posd2[ition (rows appended one after the other.) 0 if object has been killed
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
			objPosCombination = self.avatar_ID + vecValue
			lst.append(objPosCombination)



		present = []
		for k in [t for t in self.objectTypes if t not in ['wall', 'avatar','background','ladder']]: ##maybe add the avatar to this global state
			for o in sorted(rle._game.sprite_groups[k], key=lambda s:s.ID):
				if not isinstance(o, vgdl.core.Avatar):
					if o not in rle._game.kill_list:
						present.append(1)
					else:
						present.append(0)
		ind = sum([present[i]*2**i for i in range(len(present))]) #atom indicating which objects are alive
		lst.append(ind)

		#lst.extend(self.gridAtoms(rle))
		#if rle._game.sprite_groups['keyavatar']:
		#	embed()
		#print(lst)
		if not self.vecSize:
			self.vecSize = len(lst)
		#print "Vector is length {}".format(self.vecSize)
		return set(lst)


	def gridAtoms(self,rle):
		lst = []

		for k in [t for t in rle._game.sprite_groups.keys() if t not in ['wall', 'background','ladder']]:
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
	#removed the max times in each square thing
	
	def rewardSelection(self, QReward, QNovelty): #12s

		badNodes = []
		for n in QReward:
			if n.novelty >= 3:
				badNodes.append(n)
		for n in badNodes:
			QReward.remove(n)
		try:
			current = min(QReward)
			QReward.remove(current)
			return current
		except:
			return None

 	def BFS_profiler(self):
 		lp = LineProfiler()
 		lp_wrapper = lp(self.BFS)
 		lp_wrapper()
 		lp.print_stats()

	def BFS(self):
		QNovelty, QReward = [], []
		visited, rejected = [], []
		start = Node(self.rle, self, [], None)
		start.rle = self.rle
		visited.append(start)
		start.eval()
		#QNovelty.append(start)
		QReward.append(start)
		
		i=0
		path = []
		wins = 0
		min_path_length = sys.maxint
		best_path = None
		best_node = None
		found_key = False

		print(actionDict)

		while (len(QNovelty)>0 or len(QReward)>0) and i<self.max_nodes:
		
			current = self.rewardSelection(QReward, QNovelty)

			if current is None:
				self.quitting = True
				print(i)
				print("quitting, no novel node found")
				break
				

			self.statesEncountered.append(current.rle._game.getFullState())

			current.updateNoveltyDict(QNovelty, QReward)
			current.updateCenter()
			
			visited.append(current)

			print(i)

			avatar = self.getAliveAvatar(current.rle)
			if avatar is not None:
				loc = current.rle._rect2pos(avatar.rect)
				if len([o for o in current.rle._game.kill_list if o in current.rle._game.sprite_groups['key']]) > 0:
					self.key[loc] += 1
					print 'key'
				else:
					self.no_key[loc] += 1
				self.avatar_locs_disc[loc] += 1
				print loc
			else:
				"NO AVATAR"
				embed()
			print avatar

			

			self.getActions(current.rle)

			actions = self.actions
			#if i % 1000 == 0 and i > 3000:
				#embed()
			if i % 500 == 0:
				print self.avatar_locs_disc
				print self.key
			if self.canJump:
				try:
					if self.getAliveAvatar(current.rle).jumping:
						actions = [NONE]
				except:
					pass
			#print actions
			#embed()
			#goal = self.findObjectsInRLE(current.rle,'goal')[0]
			#avatar = self.getAliveAvatar(current.rle)
			#print self.geoDist(goal,(avatar.rect.x,avatar.rect.y))
			#embed()

			for a in actions:

				child = Node(self.rle, self, current.actionSeq+[a], current)
				child.eval()

				if child.win:
					# Get the gameString representation of the RLE at each
					# timestep in the chosen solution, so as to be able to
					# compare it to the agent's RLE at execution time and
					# correct for stochasticity effects
					wins += 1

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
					#path.append(child.rle.show(indent=True))
					print("WIN!")

					if len(gameString_array) < min_path_length:
						best_path = gameString_array
						best_node = child
						min_path_length = len(gameString_array)

					#print(len(child.actionSeq))
					#print(child.actionSeq)

					if wins >= self.num_paths:
						print i
						print "{} paths found, returning best".format(wins)
						#results[key] = (best_node,best_path,i)
						return best_node, best_path, i
					#return child, gameString_array, path
				else:
					if child.isTerminal() and not child.isWin():
						print("LOSE")
					#QNovelty.append(child)
					else:
						QReward.append(child)
			i+=1
		self.solution = []#Node(self.rle, self, [], None)
		if i>=self.max_nodes:
			self.quitting = True
			print "Quitting after {} nodes".format(self.max_nodes)
		else:
			print "No novel nodes found"
		print "{} paths found, returning best".format(wins)
		#results[key] = (best_node,best_path,i)
		return best_node, best_path, i

		#return None

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
		# self.lastState = None
		self.reconstructed=False
		self.expanded = False
		self.rolloutDepth = 45#max(rle.outdim)
		if self.parent is not None:
			self.rolloutArray = parent.rolloutArray[1:]
		else:
			self.rolloutArray = []

		self.rand = random.random()

		if self.parent is None:
			self.depth = 1
		else:
			self.depth = self.parent.depth + 1

	def __eq__(self,other):
		return (-self.intrinsic_reward, self.novelty, self.rand) == (-other.intrinsic_reward, other.novelty, other.rand)

	def __gt__(self,other):
		return (-self.intrinsic_reward, self.novelty, self.rand) > (-other.intrinsic_reward, other.novelty, other.rand)


## when to trigger rollouts, if any
## rollout length
## repeating rollouts if death? e.g., are they optimistic?
## multiple samples??
	def metabolics(self, rle, events, action, n=10, mult=.3):

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
		return 0.0
		#return metabolic_cost

	def rollout(self, vrle):

		#print("begin rollout")
		successfulRollout = False
		tries = 0
		while not successfulRollout and tries < 5:
			vrle = copy.deepcopy(vrle)
			prevHeuristicVal = self.heuristics(vrle)
			#prevHeuristicVal = 0
			rolloutArray = []
			i=0
			terminal, win = vrle._isDone()
			#terminal = False
			while i<self.rolloutDepth and not terminal:
				#a = random.choice([K_UP, K_DOWN, K_LEFT, K_RIGHT])
				a = random.choice(self.WBP.actions)
				vrle.step(a)
				#print("rollout")
				#print vrle.show(indent=True)
				currHeuristicVal = self.heuristics(vrle)
				heuristicVal = currHeuristicVal-prevHeuristicVal
				rolloutArray.append(heuristicVal)
				prevHeuristicVal = currHeuristicVal
				# print "in rollout"
				# print vrle.show()
				terminal, win = vrle._isDone()
				i+=1

			if terminal and not win:
				successfulRollout = False
				tries += 1
				print "rolling out again"
			else:
				successfulRollout = True
		#print("end rollout")
		return rolloutArray

	def spritecounter_val(self, theory, term, stype, rle, first_alpha=1000,
						  second_alpha=1):
		val = 0
		compute_second_order = True

		# Check if condition is win or loss and multiply accordingly
		if term.termination.win:
			mult = -5
		else:
			# compute_second_order = False
			mult = 1

		# Get all types that kill or transform stype
		killer_types = [
			inter.slot2 for inter in theory.interactionSet
			if (inter.interaction in ["killSprite","killIfOtherHasMore"] and
				not inter.generic
				and inter.slot1 == stype)]

			#if ((inter.interaction == 'killSprite' or
			#	 inter.interaction == 'transformTo') and
			#	 not inter.generic
			#	and inter.slot1 == stype)]

		# Get attributes from terminationSet
		limit = term.termination.limit
		#embed()

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
		# print stype, n_stypes, distance_to_goal, val
		if compute_second_order:
			## Get all positions of objects whose type is in killer_types; compute minimum distance
			## of each to the stypes we have to destroy. Return min over all mins.
			# embed()
			objs = []
			for ktype in killer_types:
				objs.extend(self.WBP.findObjectsInRLE(rle, ktype))
			if len([i for i in killer_types if 'avatar' in i]) > 0:
				avatar = self.WBP.getAliveAvatar(rle)
				#objs.append(self.WBP.getAliveAvatar(rle))
				if avatar and (avatar.rect.x,avatar.rect.y) not in objs:
					objs.append((avatar.rect.x,avatar.rect.y))
			kill_positions = objs


			#objs = [self.WBP.findObjectsInRLE(rle, ktype) for ktype in killer_types]

			#if len([i for i in killer_types if 'avatar' in i]) > 0:
			#	avatar = self.WBP.getAliveAvatar(rle)
			#	objs.append([(avatar.rect.x,avatar.rect.y)])
			#print objs
			#if len(objs)>0:
			#	kill_positions = np.concatenate([o for o in objs if len(o)==max([len(obj) for obj in objs])])
			#	#print kill_positions
			#else:
			#	kill_positions = np.array(objs)


			# kill_positions = np.concatenate([self.WBP.findObjectsInRLE(rle, ktype) for ktype in killer_types])
			stype_positions = self.WBP.findObjectsInRLE(rle, stype)
			try:
				# A consequence of the two-way generic interactions in the
				# theory is that minimum-distance object pairs whose interactions
				# were not yet observed will have their distance penalized twice
				# as much when none of those objects is an avatar. This implies
				# that avatar novel interactions will be favored over other ones
				#try:
				possiblePairList = [self.WBP.geoDist(pos,obj)
					for pos in kill_positions
					for obj in stype_positions]
				#except:
				#embed()

				distance = min(possiblePairList)
				# print distance
			except ValueError:
				distance = 0

			if possiblePairList:
				n_sprites = len(possiblePairList)
				#CHANGING FOR NOW TO DEAL WITH HAVING THIS HEURISTIC USE ANY AVATAR OBJECT
				#n_sprites = len(stype_positions)
				# Normalize by number of sprites, enforcing a prior that encourages
				# goals that involve killing fewer objects
				val += float(mult * second_alpha * distance)/n_sprites
			else:
				distance = 10000
				val += float(mult * second_alpha * distance)
		#print term.termination.win
		#print val
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
			#embed()
			try:
				# A consequence of the two-way generic interactions in the
				# theory is that minimum-distance object pairs whose interactions
				# were not yet observed will have their distance penalized twice
				# as much when none of those objects is an avatar. This implies
				# that non-avatar novel interactions will be favored over others
				
				
				possiblePairList = [self.WBP.geoDist(obj,pos)
					 for pos in s2_positions
					 for obj in s1_positions
					 if geoDist(obj,pos) != 0]
				

				
				
				distance = min(possiblePairList)
					 # This is a trick to avoid getting distance 0 for objects
					 # of same type. If the list turns out to be empty, it will
					 # raise an error and set the distance to 0
				# print distance
			except ValueError:
				# embed()
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

	def updateCenter(self):

		center = self.WBP.visited[0]
		n = self.WBP.visited[1]

		avatar_loc = self.rle._rect2pos(self.rle._game.sprite_groups['avatar'][0].rect)

		if avatar_loc not in self.WBP.avatar_locs:
			center[0] += avatar_loc[0]
			center[1] += avatar_loc[1]
			n += 1
			self.WBP.visited = [center,n]
	
	
	def objcollect_val(self, theory, rle, weight=0.0):
		objs = rle._game.sprite_groups.keys()
		for inter in theory.interactionSet:
			if inter.interaction == 'killSprite' and inter.slot1 == 'avatar':
				objs.remove(inter.slot2)
		objs.remove('wall')
		objs.remove('avatar')
		objs.remove('background')

		avatar = self.WBP.findAvatarInRLE(rle)

		min_dist = sys.maxint
		
		for obj in objs:
			locs = self.WBP.findObjectsInRLE(rle,obj)
			try:
				dist = [self.WBP.geoDist(avatar,x) for x in locs]
			except:
				embed()
			if dist < min_dist:
				min_dist = min(min_dist,min(dist))

		#embed()

		return -weight*min_dist

	def novel_squares(self,weight=0.00):
		#loc = self.rle._rect2pos(self.rle._game.sprite_groups["avatar"][0].rect)	
		loc = self.WBP.grid(self.WBP.findAvatarInRLE(self.rle))
		return -(1.2**self.WBP.avatar_locs_disc[loc])*weight
		#return -weight*self.WBP.avatar_locs_disc[loc]#/self.WBP.box_weights[loc]

	def distVisited(self,weight=0.0):
		center = self.WBP.visited[0]
		n = float(self.WBP.visited[1])
		try:
			c = [center[0]*self.WBP.square_size[0]/n,center[1]*self.WBP.square_size[1]/n]
		except:
			c = [0,0]
		a = self.WBP.findAvatarInRLE(self.rle)
		
		return weight*euclideanDist(a,c)/self.WBP.square_size[0]

	def heuristics(self, rle=None, first_alpha=1000, second_alpha=1,
				   time_alpha=10):
		if rle==None:
			rle = self.rle

		theory = self.WBP.theory
		heuristicVal = 0
		avatarNoveltyVals = []
		#embed()
		for term in theory.terminationSet:
			#embed()
			if isinstance(term, SpriteCounterRule):
				spritecounter_val = self.spritecounter_val(theory, term, term.termination.stype, rle,
					first_alpha=first_alpha, second_alpha=second_alpha)
				# print("spritecounter_val for {} is equal to {}".format(
					# term.termination.stype, spritecounter_val))
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
				print("NOVELTY")
				embed()
				# print("noveltytermination_val for {} and {} is equal to {}".format(
					# term.termination.s1, term.termination.s2, noveltytermination_val))
				if 'avatar' == term.termination.s2:
					avatarNoveltyVals.append(.5*self.WBP.annealing*noveltytermination_val)
				else:	
					heuristicVal += .5 * self.WBP.annealing * noveltytermination_val

		if avatarNoveltyVals:
			# print noveltyVals
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

	def getToCurrentState(self):
		if self.parent and self.parent.rle is not None:
			
			## try to copy parent lastState. Then take action and store as current lastState.
			## if that fails, replay from beginning and store as current lastState
			try:
				
				#vrle = copy.deepcopy(self.parent.rle)
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
			# print "copy failed; replaying from top"
			#vrle = copy.deepcopy(self.rle)
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

	def do_rollout(self):
		try:
			ball_now = self.rle._game.sprite_groups['ball'][0]
			ball_prev = self.parent.rle._game.sprite_groups['ball'][0]

			return (ball_now.orientation[1] < 0 and ball_prev.orientation[1] > 0)
		except:
			return False


	def eval(self):
		# ## Evaluate current node, including calculating intrinsic reward: f(rewards, heuristics, etc.)

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

		# if self.win:
			# embed()

		## Try rollouts for aliens?
		#if len(self.actionSeq)>0 and self.actionSeq[-1]==32:
		if len(self.actionSeq)>0 and self.do_rollout():
			self.rolloutArray = self.rollout(self.rle)
			print "in rollout"

		#self.rolloutArray = []

		self.heuristicVal = self.heuristics()
		self.dist = self.distVisited()
		self.novel = self.novel_squares()
		weight = 0.0

		# print self.lastState._game.score, self.heuristicVal, sum(self.rolloutArray), self.metabolic_cost
		self.intrinsic_reward = self.rle._game.score + self.heuristicVal - \
		self.metabolic_cost+sum(self.rolloutArray) + weight*self.depth + self.novel
		
		return self.win

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

	def updateNoveltyDict(self, QNovelty, QReward):
		#jointSet = list(set(QNovelty)+set(QReward))
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
		vrle = copy.deepcopy(self.rle)
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



if __name__ == "__main__":

	## Continuous physics games can't work right now. RLE is discretized, getSensors() relies on this, and a lot of the induction/planning
	## architecture depends on that. Will take some work to do this well. Best plan is to shrink the grid squares and increase speeds/strengths of
	## objects.
	#gameFilename = "examples.continuousphysics.mario_small"
	#gameFilename = "examples.continuousphysics.avoid_goomba"
	#gameFilename = "examples.continuousphysics.mario"
	gameFilename = "examples.continuousphysics.montezuma_new"
	#gameFilename = "examples.continuousphysics.ladder"
	#gameFilename = "examples.continuousphysics.simple"
	#gameFilename = "examples.continuousphysics.crossroad"
	#gameFilename = "examples.continuousphysics.collect_key"
	#gameFilename = "examples.continuousphysics.collect_resource"

	#gameFilename = "examples.gridphysics.simple_grid"
	# gameFilename = "examples.gridphysics.boulderdash" #Game is buggy.
	#gameFilename = "examples.gridphysics.expt_exploration_exploitation"
	#gameFilename = "examples.continuousphysics.ptsp_simple"
	#gameFilename = "examples.continuousphysics.ptsp"
	#gameFilename = "examples.continuousphysics.breakout"


	gameString, levelString = defInputGame(gameFilename, randomize=True)
	rleCreateFunc = lambda: createRLInputGame(gameFilename)
	rle = rleCreateFunc()
	
	#embed()
	times = []
	#for i in range(10):
	t1 = time.time()
	p = WBP(rle, gameFilename)


	embed()
	#	try:
	last, gameString_array, nodes = p.BFS()
	#result = p.BFS_profiler()
	#from core import VGDLParser
	#last.playBack(make_movie=True)
	#	except:
	#		fails += 1
	#embed()
	#for i in path:
	#	print(i)
	
				# VGDLParser.playGame(gameString, levelString, p.statesEncountered, persist_movie=True, make_images=True, make_movie=True, movie_dir="videos/"+gameFilename, padding=0)
	# VGDLParser.playGame(gameString, levelString, last.finalStatesEncountered, persist_movie=True, make_images=True, make_movie=True, movie_dir="videos/"+gameFilename, padding=0)

	#print("time:")
	print time.time()-t1
		#times.append(time.time() - t1)

	embed()


#
