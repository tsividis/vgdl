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

from pygame.locals import K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT
NONE = 0
ACTIONS = [K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT, NONE]
actionDict = {K_SPACE: 'space', K_UP: 'up', K_DOWN: 'down', K_LEFT: 'left', K_RIGHT: 'right', NONE: 'wait'}
LIMIT = 1

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
		self.addWaitAction = False
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
		for sc in shootingClasses:
			if any([sc in c for c in classes]):
				spacebarAvailable = True
				break
		if spacebarAvailable:
			self.actions = [K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT]
		else:
			#self.actions = [K_UP, K_DOWN, K_LEFT, K_RIGHT]
			self.actions = [K_RIGHT,K_UP, K_DOWN, K_LEFT]
		if self.addWaitAction:
			self.actions.append(NONE)
		return

	#returns set of atom values
	def calculateAtoms(self, rle):
		lst = []

		for k in rle._game.sprite_groups.keys():
			for o in rle._game.sprite_groups[k]:
				if o not in rle._game.kill_list:
					## turn location into vector posd2[ition (rows appended one after the other.) 0 if object has been killed
					#pos = rle._rect2pos(o.rect) #x,y
					pos = (o.rect.left, o.rect.top)
					vecValue = pos[1] + pos[0]*rle.outdim[0]*self.square_size[1] + 1
				else:
					vecValue = 0
				objPosCombination = self.objIDs[o.ID] + vecValue
				lst.append(objPosCombination) #unique for each object-location combination
		present = []
		for k in [t for t in self.objectTypes if t not in ['wall', 'avatar']]: ##maybe add the avatar to this global state
			# for o in rle._game.sprite_groups[k]:
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
	def rewardSelection(self, QReward, QNovelty):
		# acceptableNodes = QReward
		acceptableNodes = filter(lambda n:n.novelty<3, QReward)
		# if len(acceptableNodes)==0:
			# acceptableNodes = QReward
			# print "Removed filter"
			# embed()
		bestNodes = sorted(acceptableNodes, key=lambda n: (-n.intrinsic_reward, n.novelty))
		
		try:
			current = bestNodes.pop(0)
		except:
			return None
		#QReward.remove(current)
		try:
			QNovelty.remove(current)
		except:
			pass
		return current

	def BFS(self):
		QNovelty, QReward = [], []
		visited, rejected = [], []
		start = Node(self.rle, self, [], None)
		start.rle = self.rle
		visited.append(start)
		start.eval()
		QNovelty.append(start)
		QReward.append(start)
		i=0
		path = []

		while (len(QNovelty)>0 or len(QReward)>0) and i<self.max_nodes:
			"""
			if i%2==0:
			else:
			"""
			# current = self.noveltySelection(QNovelty, QReward)
			current = self.rewardSelection(QReward, QNovelty)
			# print embed()

			
			#for n in QNovelty:
				#print(n.WBP.findAvatarInRLE(n.rle))
			

			if current is None:
				self.quitting = True
				print(i)
				print("quitting, no novel node found")
				return None
			self.statesEncountered.append(current.rle._game.getFullState())
			print("BFS")
			print current.rle.show(indent=True)
			print current.rle._game.sprite_groups["avatar"][0].rect
			if current.actionSeq:
				print actionDict[current.actionSeq[-1]]
			#path.append(current.rle.show(indent=True))
			current.updateNoveltyDict(QNovelty, QReward)
			# embed()
			visited.append(current)

			for a in self.actions:
				
				child = Node(self.rle, self, current.actionSeq+[a], current)
				child.eval()
				#print(actionDict[a])
				#print(child.WBP.findAvatarInRLE(child.rle))
				#print("")
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
					return child, gameString_array
					#return child, gameString_array, path
				else:
					QNovelty.append(child)
					QReward.append(child)
			i+=1
			#print i
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
		self.rolloutDepth = 13#max(rle.outdim)
		if self.parent is not None:
			self.rolloutArray = parent.rolloutArray[1:]
		else:
			self.rolloutArray = []


## when to trigger rollouts, if any
## rollout length
## repeating rollouts if death? e.g., are they optimistic?
## multiple samples??
	def metabolics(self, rle, events, action, n=10, mult=.3):

		metabolic_cost = 1./n
		if action==32:
			metabolic_cost += (1-1./n)*mult
		if len(events)>0:
			# metabolic_cost = .3
			if any([rle._game.sprite_groups['avatar'][0].ID in e and e[0]=='bounceForward' for e in events]):
				metabolic_cost += .3#(1-1./n)*mult
			# if any([rle._game.sprite_groups['avatar'][0].ID in e and e[0]=='killSprite' for e in events]):
			# 	metabolic_cost += 0.3
		return 0.# metabolic_cost

	def rollout(self, vrle):
		#print("begin rollout")
		successfulRollout = False
		while not successfulRollout:
			vrle = copy.deepcopy(vrle)
			prevHeuristicVal = self.heuristics(vrle)
			#prevHeuristicVal = 0
			rolloutArray = []
			i=0
			terminal, win = vrle._isDone()
			#terminal = False
			while i<self.rolloutDepth and not terminal:
				a = random.choice([K_UP, K_DOWN, K_LEFT, K_RIGHT])
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
			# embed()
			if terminal and not win:
				successfulRollout = False
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
			mult = -1
		else:
			# compute_second_order = False
			mult = 10

		# Get all types that kill or transform stype
		killer_types = [
			inter.slot2 for inter in theory.interactionSet
			if ((inter.interaction == 'killSprite' or
				 inter.interaction == 'transformTo') and
				 not inter.generic
				and inter.slot1 == stype)]

		# Get attributes from terminationSet
		limit = term.termination.limit
		# embed()

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
				possiblePairList = [manhattanDist(obj, pos)
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
				distance = 100
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
				possiblePairList = [manhattanDist(obj, pos)
					 for pos in s2_positions
					 for obj in s1_positions
					 if manhattanDist(obj, pos) != 0]
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

	def heuristics(self, rle=None, first_alpha=1000, second_alpha=1,
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
	def getToCurrentState(self):
		if self.parent and self.parent.rle is not None:
			
			## try to copy parent lastState. Then take action and store as current lastState.
			## if that fails, replay from beginning and store as current lastState
			#try:
			for i in range(1):
				vrle = copy.deepcopy(self.parent.rle)
				
				if len(self.actionSeq)>0:
					
					a = self.actionSeq[-1]

					res = vrle.step(a)
					
					# relevantEvents = [t for t in res['effectList'] if t[0] == 'stepBack']
					# if relevantEvents:
					# 	import ipdb;ipdb.set_trace()
					self.metabolic_cost = self.parent.metabolic_cost + self.metabolics(vrle, res['effectList'], a)

					terminal, win = vrle._isDone()
			#except:
			#	print "conditions met but copy failed"
				#embed()
		else:
			self.reconstructed=True
			# print "copy failed; replaying from top"
			vrle = copy.deepcopy(self.rle)
			terminal, win = vrle._isDone()
			i=0
			while not terminal and len(self.actionSeq)>i:
				a = self.actionSeq[i]
				res = vrle.step(a)
				self.metabolic_cost += self.metabolics(vrle, res['effectList'], a)
				terminal, win = vrle._isDone()
				i += 1
		return vrle, win

	def eval(self):
		# ## Evaluate current node, including calculating intrinsic reward: f(rewards, heuristics, etc.)

		self.rle, self.win = self.getToCurrentState()

		self.updateObjIDs(self.rle)
		self.state = self.WBP.calculateAtoms(self.rle) #new atom values

		for i in range(1,3):
			for c in itertools.combinations(self.state, i):
				#if self.WBP.trueAtoms[c] == 0:
				if self.WBP.trueAtoms[c] < LIMIT:
					self.candidates.append(c)
		self.updateNovelty() #calculates novelty based on state of node (1, 2, 3)

		# if self.win:
			# embed()

		## Try rollouts for aliens?
		if len(self.actionSeq)>0 and self.actionSeq[-1]==32:
			self.rolloutArray = self.rollout(self.rle)
			#print "in rollout"

		self.heuristicVal = self.heuristics()

		# print self.lastState._game.score, self.heuristicVal, sum(self.rolloutArray), self.metabolic_cost
		self.intrinsic_reward = self.rle._game.score + self.heuristicVal + \
		sum(self.rolloutArray) - self.metabolic_cost
		# self.intrinsic_reward = 0
		return self.win

	def updateNovelty(self):
		if len(self.candidates)==0:
			self.novelty = 3
		else:
			self.novelty = min([len(c) for c in self.candidates])
		return self.novelty

	def updateNoveltyDict(self, QNovelty, QReward):
		jointSet = list(set(QNovelty+QReward))
		for c in self.candidates:
			'''
			if self.WBP.trueAtoms[c] == 0:
				self.WBP.trueAtoms[c] = 1
				for n in jointSet:
					if c in n.candidates:
						n.candidates.remove(c)
			'''
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


if __name__ == "__main__":

	# gameFilename = "examples.gridphysics.simpleGame4_small"

	## make better versions
	# gameFilename = "examples.gridphysics.demo_teleport"
	# gameFilename = "examples.gridphysics.movers3c" ##solved!!
	# gameFilename = "examples.gridphysics.rivercross" ## solved!!
	# gameFilename = "examples.gridphysics.demo_dodge"  ##solved!!
	# gameFilename = "examples.gridphysics.movers5" ##solved!!
	# gameFilename = "examples.gridphysics.demo_preconditions"
	# gameFilename = "examples.gridphysics.demo_waterfall"
	# gameFilename = "examples.gridphysics.pick_apples"
	# gameFilename = "examples.gridphysics.demo_chaser"
	# gameFilename = "examples.gridphysics.simpleGame_push_boulders"
	# gameFilename = "examples.gridphysics.chase" #yes!!!
	# gameFilename = "examples.gridphysics.survivezombies" # solvable, just not very fast if long timeout.
	# gameFilename = "examples.gridphysics.demo_transform_small"

	# gameFilename = "examples.gridphysics.zelda_orig2" ## We can probably handle this, provided subgoal heuristics, once Chaser/A* are deterministic
	# gameFilename = "examples.gridphysics.missilecommand2" ## We can probably handle this, provided subgoal heuristics, once Chaser/A* are deterministic
	# gameFilename = "examples.gridphysics.chase2"
	# gameFilename = "examples.gridphysics.aliens2"


	# gameFilename = "examples.gridphysics.demo_helper"  ##
	# gameFilename = "examples.gridphysics.demo_transform" ##

	# gameFilename = "examples.gridphysics.simpleGame_missile" #later.

	# gameFilename = "examples.gridphysics.simpleGame_push_boulders2"

	# gameFilename = "examples.gridphysics.frogs" ## worked with k=2.

	# gameFilename = "examples.gridphysics.waypointtheory"  ##easy version solved!

	# gameFilename = "examples.gridphysics.simpleGame_push_boulders_multigoal" ## k=2 works!
	# gameFilename = "examples.gridphysics.simpleGame4"

	# gameFilename = "examples.gridphysics.simpleGame4_small"
	# gameFilename = "examples.gridphysics.demo_multigoal_and"

	#gameFilename = "examples.gridphysics.demo_multigoal_and_score"  ##easy version solved!
	#gameFilename = "examples.gridphysics.demo_sokoban" #later
	# gameFilename = "examples.gridphysics.demo_sokoban_score" #later
	# gameFilename = "examples.gridphysics.portals" ## stochasticity breaks it
	# gameFilename = "examples.gridphysics.demo_helper"


	# gameFilename = "examples.gridphysics.demo_multigoal_and"  ##takes forever if you have many boxes and don't use 2BFS (with metabolic penalty)


	## Continuous physics games can't work right now. RLE is discretized, getSensors() relies on this, and a lot of the induction/planning
	## architecture depends on that. Will take some work to do this well. Best plan is to shrink the grid squares and increase speeds/strengths of
	## objects.
	gameFilename = "examples.continuousphysics.mario"
	#gameFilename = "examples.continuousphysics.simple"
	#gameFilename = "examples.continuousphysics.crossroad"
	#gameFilename = "examples.gridphysics.simple_grid"
	# gameFilename = "examples.gridphysics.boulderdash" #Game is buggy.
	#gameFilename = "examples.gridphysics.expt_exploration_exploitation"
	# gameFilename = "examples.continuousphysics.ptsp_simple"


	gameString, levelString = defInputGame(gameFilename, randomize=True)
	rleCreateFunc = lambda: createRLInputGame(gameFilename)
	rle = rleCreateFunc()
	
	#embed()
	
	p = WBP(rle, gameFilename)


	#embed()
	t1 = time.time()
	last, gameString_array = p.BFS()
	from core import VGDLParser
	#embed()
	#for i in path:
	#	print(i)
	
	last.playBack(make_movie=True)
	# VGDLParser.playGame(gameString, levelString, p.statesEncountered, persist_movie=True, make_images=True, make_movie=True, movie_dir="videos/"+gameFilename, padding=0)
	# VGDLParser.playGame(gameString, levelString, last.finalStatesEncountered, persist_movie=True, make_images=True, make_movie=True, movie_dir="videos/"+gameFilename, padding=0)

	#print("time:")
	print time.time()-t1
	# embed()


#
