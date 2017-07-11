from IPython import embed
import itertools
import numpy as np
from numpy import zeros
import pygame
from ontology import BASEDIRS
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
LIMIT = 2
WALL_EDGE = 1
MAX_TIMES_IN_SQUARE = sys.maxint

## Base class for width-based planners (IW(k) and 2BFS)
class WBP():
	def __init__(self, rle, gameFilename, theory=None, fakeInteractionRules = [], annealing=1, max_nodes=5000):
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

		# for rule in self.theory.interactionSet:
		# 	if 'stepBack'==rule.interaction:
		# 		ipdb.set_trace()
		i=1
		for k in rle._game.all_objects.keys():
			self.objIDs[k] = i * (self.vecDim[0]+self.padding)
			i+=1
		self.addSpaceBarToActions()

		self.avatar_locs = set()

		#move away from squares we've already been in heuristic:
		self.visited = [[0,0],0]
		self.canJump = False
		self.all_locs = []

		self.avatar_locs_disc = defaultdict(lambda:0)
		self.graph = {}
		self.distances = self.dijkstra()
		self.box_weights = self.calc_weights()

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
						if (i + x, j + y) not in wallLocs and i+x in range(rle.outdim[1]) and j+y in range(rle.outdim[0]):
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

		#smooth out distances at grid vertices to calculate distances between points at interior of squares
		
		dist = 0
		a1 = self.loop4d()
		a2 = self.loop4d()
		for exp in a1:
			for coord in a2:
				if all(i >= j for i, j in zip(exp,coord)):
					val = self.comp_exp((x1,y1,x2,y2),exp)
					if val:
						dist += (1 if (sum(coord)%2 == sum(exp)%2) else -1)*val* \
						self.distances[(grid1[0]+coord[0],grid1[1]+coord[1])][(grid2[0]+coord[2],grid2[1]+coord[3])]

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

	#returns set of atom values
	def calculateAtoms(self, rle):
		lst = []

		for k in rle._game.sprite_groups.keys():
			for o in rle._game.sprite_groups[k]:
				if o not in rle._game.kill_list:
					## turn location into vector posd2[ition (rows appended one after the other.) 0 if object has been killed
					pos = (o.rect.left, o.rect.top)
					vecValue = pos[1] + pos[0]*rle.outdim[0]*self.square_size[1] + 1
				else:
					vecValue = 0
				objPosCombination = self.objIDs[o.ID] + vecValue
				lst.append(objPosCombination) #unique for each object-location combination
		present = []
		for k in [t for t in self.objectTypes if t not in ['wall', 'avatar']]: ##maybe add the avatar to this global state
			for o in sorted(rle._game.sprite_groups[k], key=lambda s:s.ID):
				if o not in rle._game.kill_list:
					present.append(1)
				else:
					present.append(0)
		ind = sum([present[i]*2**i for i in range(len(present))]) #atom indicating which objects are alive
		lst.append(ind)
		if not self.vecSize:
			self.vecSize = len(lst)
			# print "Vector is length {}".format(self.vecSize)
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

		current = min(QReward)
		QReward.remove(current)
		return current

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

		print(actionDict)

		while (len(QNovelty)>0 or len(QReward)>0) and i<self.max_nodes:
		
			current = self.rewardSelection(QReward, QNovelty)

			if current is None:
				self.quitting = True
				print(i)
				print("quitting, no novel node found")
				return None

			self.statesEncountered.append(current.rle._game.getFullState())

			print current.rle.show(indent=True)
			print current.rle._game.sprite_groups["avatar"][0].rect
			
			self.all_locs.append(self.findAvatarInRLE(current.rle))
			current.updateNoveltyDict(QNovelty, QReward)
			current.updateCenter()
			self.avatar_locs_disc[self.grid(self.findAvatarInRLE(current.rle))] += 1
			visited.append(current)
			self.avatar_locs.add(current.rle._rect2pos(current.rle._game.sprite_groups['avatar'][0].rect))

			print current.rle._game.sprite_groups["ball"][0].rect
			print current.intrinsic_reward
			print current.depth

			actions = self.actions
			if self.canJump and current.rle._game.sprite_groups["avatar"][0].jumping:
				actions = [NONE]
			
			for a in actions:

				child = Node(self.rle, self, current.actionSeq+[a], current)
				child.eval()

				if child.win:
					# Get the gameString representation of the RLE at each
					# timestep in the chosen solution, so as to be able to
					# compare it to the agent's RLE at execution time and
					# correct for stochasticity effects
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
					print i
					return child, gameString_array, i
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
		return None

class Node():
	def __init__(self, rle, WBP, actionSeq, parent):
		self.rle = rle
		self.WBP = WBP
		self.actionSeq = actionSeq
		self.parent = parent
		self.state = {} #values of atoms
		self.candidates = []
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
			if ((inter.interaction == 'killSprite' or
				 inter.interaction == 'transformTo') and
				 not inter.generic
				and inter.slot1 == stype)]

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
			objs = [self.WBP.findObjectsInRLE(rle, ktype) for ktype in killer_types]

			if len(objs)>0:
				kill_positions = np.concatenate([o for o in objs if len(o)==max([len(obj) for obj in objs])])
			else:
				kill_positions = np.array(objs)

			# kill_positions = np.concatenate([self.WBP.findObjectsInRLE(rle, ktype) for ktype in killer_types])
			stype_positions = self.WBP.findObjectsInRLE(rle, stype)
			try:
				# A consequence of the two-way generic interactions in the
				# theory is that minimum-distance object pairs whose interactions
				# were not yet observed will have their distance penalized twice
				# as much when none of those objects is an avatar. This implies
				# that avatar novel interactions will be favored over other ones
				#possiblePairList = [manhattanDist(obj, pos)/float(self.WBP.square_size[0])
				#	 for pos in kill_positions
				#	 for obj in stype_positions]
				#embed()
				possiblePairList = [self.WBP.geoDist(pos,obj)
					for pos in kill_positions
					for obj in stype_positions]

				distance = min(possiblePairList)
				# print distance
			except ValueError:
				distance = 0

			if possiblePairList:
				n_sprites = len(possiblePairList)
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
			if isinstance(term, SpriteCounterRule):
				spritecounter_val = self.spritecounter_val(theory, term, term.termination.stype, rle,
					first_alpha=first_alpha, second_alpha=second_alpha)
				# print("spritecounter_val for {} is equal to {}".format(
					# term.termination.stype, spritecounter_val))
				heuristicVal += spritecounter_val

			elif isinstance(term, MultiSpriteCounterRule):
				multispritecounter_val = self.multispritecounter_val(theory, term, rle,
						first_alpha=first_alpha, second_alpha=second_alpha)
				heuristicVal += multispritecounter_val

			elif isinstance(term, TimeoutRule):
				timeout_val = time_alpha * \
					self.timeout_val(theory, term, rle)
				heuristicVal += timeout_val

			elif isinstance(term, NoveltyRule):
				noveltytermination_val = self.noveltytermination_val(
					theory, term, term.termination.s1, term.termination.s2, rle,
					first_alpha=first_alpha, second_alpha=second_alpha)
				# print("noveltytermination_val for {} and {} is equal to {}".format(
					# term.termination.s1, term.termination.s2, noveltytermination_val))
				if 'avatar' == term.termination.s2:
					avatarNoveltyVals.append(.5*self.WBP.annealing*noveltytermination_val)
				else:	
					heuristicVal += .5 * self.WBP.annealing * noveltytermination_val

		if avatarNoveltyVals:
			# print noveltyVals
			heuristicVal += max(avatarNoveltyVals)

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
		ball_now = self.rle._game.sprite_groups['ball'][0]
		ball_prev = self.parent.rle._game.sprite_groups['ball'][0]

		return (ball_now.orientation[1] < 0 and ball_prev.orientation[1] > 0)


	def eval(self):
		# ## Evaluate current node, including calculating intrinsic reward: f(rewards, heuristics, etc.)

		self.rle, self.win = self.getToCurrentState()

		self.updateObjIDs(self.rle)
		self.state = self.WBP.calculateAtoms(self.rle) #new atom values

		for i in range(1,3):
			for c in itertools.combinations(self.state, i):
				c = tuple(sorted(c))
				if self.WBP.trueAtoms[c] < LIMIT:
					self.candidates.append(c)
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
		weight = 1.0

		# print self.lastState._game.score, self.heuristicVal, sum(self.rolloutArray), self.metabolic_cost
		self.intrinsic_reward = self.rle._game.score + self.heuristicVal - \
		self.metabolic_cost+sum(self.rolloutArray) + weight*self.depth + self.novel
		
		return self.win

	def updateNovelty(self):
		if len(self.candidates)==0:
			self.novelty = 3
		else:
			self.novelty = min([len(c) for c in self.candidates])

		return self.novelty

	def updateNoveltyDict(self, QNovelty, QReward):
		#jointSet = list(set(QNovelty)+set(QReward))
		jointSet = list(QReward)
		for c in self.candidates:

			changed = False
			if self.WBP.trueAtoms[c] < LIMIT:
				self.WBP.trueAtoms[c] += 1
				changed = True
			if changed and self.WBP.trueAtoms[c] == LIMIT:
				for n in jointSet:
					if c in n.candidates:
						n.candidates.remove(c)

		for n in jointSet:
			n.novelty = n.updateNovelty()
		return

	#update IDs if we get new objects
	def updateObjIDs(self, vrle):
		i = 0
		for objType in vrle._game.sprite_groups:
			for s in vrle._game.sprite_groups[objType]:
				if s.ID not in self.WBP.objIDs.keys():
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
	gameFilename = "examples.continuousphysics.mario_small"
	gameFilename = "examples.continuousphysics.avoid_goomba"
	#gameFilename = "examples.continuousphysics.mario"
	#gameFilename = "examples.continuousphysics.simple"
	#gameFilename = "examples.continuousphysics.crossroad"

	#gameFilename = "examples.gridphysics.simple_grid"
	# gameFilename = "examples.gridphysics.boulderdash" #Game is buggy.
	#gameFilename = "examples.gridphysics.expt_exploration_exploitation"
	#gameFilename = "examples.continuousphysics.ptsp_simple"
	#gameFilename = "examples.continuousphysics.ptsp"
	gameFilename = "examples.continuousphysics.breakout"


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
	#last, gameString_array, nodes = p.BFS_profiler()
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
