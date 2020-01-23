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
import copy
from threading import Lock
from Queue import Queue
from util import *
from ontology import Immovable, Passive, Resource, ResourcePack, RandomNPC, Chaser, AStarChaser, OrientedSprite, Missile
from theory_template import TimeStep, Precondition, InteractionRule, TerminationRule, TimeoutRule, SpriteCounterRule, MultiSpriteCounterRule, \
NoveltyRule, generateSymbolDict, ruleCluster, Theory, Game, writeTheoryToTxt, generateTheoryFromGame
from ontology import MovingAvatar, HorizontalAvatar, VerticalAvatar, FlakAvatar, AimedFlakAvatar, OrientedAvatar, \
	RotatingAvatar, RotatingFlippingAvatar, NoisyRotatingFlippingAvatar, ShootAvatar, AimedAvatar, \
		AimedFlakAvatar
from rlenvironmentnonstatic import createRLInputGame
from hyperparameters import hyperparameter_sets
import cPickle

from pygame.locals import K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT
NONE = 0
ACTIONS = [K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT, NONE]
actionDict = {K_SPACE: 'space', K_UP: 'up', K_DOWN: 'down', K_LEFT: 'left', K_RIGHT: 'right', NONE: 'wait'}

#############################################
# Sprites with 'DARKGRAY' colorName are not
# updated in _performAction and fastcopy
#############################################

## Base class for width-based planners (IW(k) and 2BFS)
class WBP():
	def __init__(self, rle, gameFilename, theory=None, fakeInteractionRules = [], seen_limits=[], max_nodes=100000,
		firstOrderHorizon=False, stall_mode=False, hyperparameters={}, extra_atom=False, IW_k=1, objectNumberTrackingLimit=1000, objectLocationTrackingLimit=1000, 
		objectsWhoseLocationsWeIgnore=['Flicker', 'Random'], lesion=[], display=False):
		self.rle = rle
		self.gameFilename = gameFilename

		###################################################
		### 		Parameter settings					###
		###################################################
		self.hyperparameter_index = hyperparameters['idx'] ## for keeping track of what we're running
		self.hyperparameters = dict((k, hyperparameters[k]) for k in hyperparameters.keys() if k not in ['idx'])
		self.IW_k = IW_k
		self.objectNumberTrackingLimit = objectNumberTrackingLimit
		self.objectLocationTrackingLimit = objectLocationTrackingLimit
		self.max_nodes = max_nodes
		self.objectsWhoseLocationsWeIgnore = objectsWhoseLocationsWeIgnore
		self.objectsWhosePresenceWeIgnore = ['Flicker']
		self.classesWhoseLocationsWeIgnore = []
		self.classesWhosePresenceWeIgnore = []
		self.allowRollouts = True
		self.quitting = False
		self.lesion = lesion
		# Compute starting number of each SpriteCounter stype
		self.firstOrderHorizon = firstOrderHorizon
		if any([s in self.lesion for s in ['AGH2', 'AGH3']]):
			# print "no firstOrderHorizon"
			self.firstOrderHorizon = False
		self.extra_atom = extra_atom
		self.rolloutHyperparameters = dict([(k,v) if 'second' not in k else (k,0) for k,v in self.hyperparameters.items()])
		## 'stall' mode generates a quick-and-dirty plan that just tries to ensure safety -- increase negative multiplier on proximity to items thought to be dangerous, then plan.
		self.stall_mode = stall_mode
		if self.stall_mode:
			self.hyperparameters['sprite_negative_mult'] = 100
		self.padding = 5  ##5  is arbitrary; just to make sure we don't get overlap when we add positions in our self-made hash used to track IW atoms

		###################################################
		###    Bookkeeping and output data structures   ###
		###################################################

		self.pixel_size = self.rle._game.screensize[0]/self.rle._game.width
		self.visited_positions = np.zeros(np.array(self.rle._game.screensize)/
			self.pixel_size)

		self.objIDs = {}
		self.trueAtoms = defaultdict(lambda:0) ## set of atoms that have been true at some point thus far in the planner.
		self.objectTypes = sorted(rle._game.sprite_groups.keys())
		self.seen_limits = seen_limits ## Filling up agent's stores of any given resource it can pick up is a curiosity goal; we keep track of what we've witnessed here so that we can only assign credit (and return a plan) if it's the first time the agent has done this
		
		for i,k in enumerate(rle._game.all_objects.keys()):
			self.objIDs[k] = i * 100 * (rle.outdim[0]*rle.outdim[1]+self.padding)

		self.winning_states = []
		self.total_nodes_opened, self.total_nodes_selected = 0, 0
		self.actions = self.getAvailableActions()
		self.solution = None
		self.gameString_array = []

		###################################################
		### 		Theory-based heuristics				###
		###################################################

		if theory == None:
			self.theory = generateTheoryFromGame(rle, alterGoal=False)
		else:
			self.theory=copy.deepcopy(theory)
			self.theory.interactionSet.extend(fakeInteractionRules)
			self.theory.updateTerminations()
	
		if any([t in str(s.vgdlType) for s in self.theory.spriteObjects.values() for t in ['Missile', 'Random', 'Chaser']]):
			movingTypesInGame = True
		else:
			movingTypesInGame = False

		if self.theory.classes['avatar'][0].args and 'stype' in self.theory.classes['avatar'][0].args:
			self.thingWeShoot = self.theory.classes['avatar'][0].args['stype']
		else:
			self.thingWeShoot = None

		self.killer_types = [inter.slot2 for inter in self.theory.interactionSet if inter.slot1=='avatar' and inter.interaction in ['killSprite']]

		self.position_score_multiplier = -10
		if self.hyperparameter_index in ['long-term'] and not movingTypesInGame:
			self.position_score_multiplier = -1

		## Ignore objects we don't want to track (i.e., object we know are guaranteed not to move, or objects that move but are too numerous to use IW1 without dramatically expanding the search space.)
		self.objectsToTrack = []
		for k in rle._game.sprite_groups.keys():
			if ((k in self.theory.classes.keys() and ('Resource' or 'Immovable') in str(self.theory.classes[k][0].vgdlType) and not \
			(('bounceForward' or 'pullWithIt') in [rule.interaction for rule in self.theory.interactionSet if k in [rule.slot1, rule.slot2]])) or
			len(rle._game.sprite_groups[k])>self.objectNumberTrackingLimit):
				pass
			else:
				self.objectsToTrack.append(k)

			## Don't track (in either way) objects that are very numerous; completely breaks calculateAtoms()
			## Also don't track projectiles we generate 
			if (len(rle._game.sprite_groups[k])>self.objectNumberTrackingLimit) or k==self.thingWeShoot:
				self.classesWhosePresenceWeIgnore.append(k)
			if (len(rle._game.sprite_groups[k])>self.objectLocationTrackingLimit):
				self.classesWhoseLocationsWeIgnore.append(k)

		## Used to track subgoals. If we start planning in an episode with, say, 8 object tokens of a type we want to get to 0 of, subgoal progress occurs if any node we open has <8 of them.
		self.starting_stype_n = {}
		for term in self.theory.terminationSet:
			if isinstance(term, SpriteCounterRule):
				stype = term.termination.stype
				objs = self.rle.findObjectsInRLE(stype)
				n_stypes = len(objs) if objs is not None else 0
				self.starting_stype_n[stype] = n_stypes
			elif isinstance(term, MultiSpriteCounterRule):
				stypes = term.termination.stypes
				n_stypes = sum([len(self.rle.findObjectsInRLE(stype)) for stype in stypes if self.rle.findObjectsInRLE(stype)])
				self.starting_stype_n[tuple(stypes)] = n_stypes

		###################################################
		### 		Diagnostic printouts				###
		###################################################
		self.display = False
		if self.display:
			print "In planner; MovingTypesInGame: {}. Planning with idx {} and position_multiplier {}".format(movingTypesInGame, self.hyperparameter_index, self.position_score_multiplier)

			if self.stall_mode:
				print "Planning in stall_mode. Switched sprite_negative_mult to {}".format(self.hyperparameters['sprite_negative_mult'])
			else:
				print "Planning normally"

			print 'max nodes', self.max_nodes
			print "exta atom is {}".format(self.extra_atom)
			if self.killer_types:
				print 'killer types', self.killer_types
			print "available actions:", self.actions
			print "ignoring presences for", self.classesWhosePresenceWeIgnore
			print "ignoring locations for", self.classesWhoseLocationsWeIgnore


	def getAvailableActions(self):		
		## get actions from avatar-type definition
		actions = self.rle._game.getAvatars()[0].declare_possible_actions().values()
		actions.append(NONE)
		actions = sorted(actions)		

		return actions

	def calculateAtoms(self, rle):
		
		## Hashes the state according to object-token location and presence/absence of items of each type. Idea is to prune states where no new atom is made true in this search episode.

		lst = []
		## Track specific locations of objects
		kl_set = set(rle._game.kill_list)
		for k in self.objectsToTrack:
			## Don't track Flicker in atoms. The point is that the Flicker should have an effect on other objects, so atom novelty that would have been a function of the Flicker's presence is being taken care of by that. Otherwise the agent can keep exploring states that have no actual effect on the game state: Using its Flicker on every possible location on the board.
			if ((len(rle._game.sprite_groups[k])>0 and
					rle._game.sprite_groups[k][0].colorName in self.theory.spriteObjects.keys() and
					any([obj in str(self.theory.spriteObjects[rle._game.sprite_groups[k][0].colorName].vgdlType) for obj in self.objectsWhoseLocationsWeIgnore])) or
				k in self.classesWhoseLocationsWeIgnore) or k==self.thingWeShoot:

				pass
			else:
				for o in rle._game.sprite_groups[k]:
					if o not in kl_set:
						## turn location into vector position (rows appended one after the other.)
						pos = float(o.rect.left)/rle._game.block_size, float(o.rect.top)/rle._game.block_size
						vecValue = 10*pos[1] + 10*pos[0]*rle.outdim[0] + 10
					else:
						vecValue = 0
					try:
						if k == rle._game.getAvatars()[0].stype:
							# Add avatar orientation to atom
							orientation = rle._game.sprite_groups[k][0].orientation
							if orientation[0] < 0 and orientation[1] == 0:
								vecValue += 0
							elif orientation[0] > 0 and orientation[1] == 0:
								vecValue += 100000
							elif orientation[0] == 0 and orientation[1] < 0:
								vecValue += 200000
							elif orientation[0] == 0 and orientation[1] > 0:
								vecValue += 300000
					except (IndexError, AttributeError) as e:
						pass

					objPosCombination = self.objIDs[o.ID] + vecValue
					lst.append(objPosCombination)

		## Track present/absent objects
		present = []
		for k in [t for t in self.objectTypes if t not in ['wall', 'avatar']]:
			if (len(rle._game.sprite_groups[k])>0 and
					rle._game.sprite_groups[k][0].colorName in self.theory.spriteObjects.keys() and
					any([obj in str(self.theory.spriteObjects[rle._game.sprite_groups[k][0].colorName].vgdlType) for obj in self.objectsWhosePresenceWeIgnore]) or
					k in self.classesWhosePresenceWeIgnore) or k==self.thingWeShoot:
				pass
			else:
				for o in sorted(rle._game.sprite_groups[k], key=lambda s:s.ID):
					if o not in kl_set:
						present.append(1)
					else:
						present.append(0)
		ind = sum([present[i]*2**i for i in range(len(present))])
		lst.append(ind)

		if self.extra_atom:
			try:
				avatar_pos = rle.findAvatarInRLE()
				vecValue = avatar_pos[1] + avatar_pos[0]*rle.outdim[0] + 1
			except:
				vecValue = [0]

			stateIW1 = [vecValue] + rle.show_binary(self.thingWeShoot)
			lst.append(hash(tuple(stateIW1)))
		return set(lst)


	def noveltySelection(self, QNovelty, QReward):
		bestNodes = sorted(QNovelty, key=lambda n: (n.novelty, -n.intrinsic_reward))
		current = bestNodes.pop(0)
		QNovelty.remove(current)
		try:
			QReward.remove(current)
		except:
			pass
		return current

	def rewardSelection(self, QReward, QNovelty):
		if 'IW' in self.lesion:
			## IW ablations: don't filter for novelty
			acceptableNodes = QReward
			acceptableNodes = filter(lambda n: (not n.terminal or n.win), acceptableNodes)
			bestNodes = sorted(acceptableNodes, key=lambda n: (-n.intrinsic_reward))
		else:
			## Normal case: Always use novelty to filter. 
			acceptableNodes = filter(lambda n: n.novelty<self.IW_k+1, QReward)
			# # # ## sort max to min for pop()
			bestNodes = sorted(acceptableNodes, key=lambda n: (-n.intrinsic_reward, n.novelty))
		
		try:
			
			current = bestNodes.pop(0)
			if (current.terminal, current.win) == (True, False):
				print "rewardSelection picked a loss node!!"
				embed()
			if current.terminal and not current.win:
				print "rewardSelection picked a loss node!!"
				embed()
			if current.badOutcomes:
				print "picked a node with >0 badoutcomes"
				embed()
		except:
			if self.display:
				print("RewardSelection didn't find a node that satisfied novelty criteria.")
			return 'pickMaxNode'
		
		QReward.remove(current)
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

		print "planning..."
		
		while (len(QNovelty)>0 or len(QReward)>0) and i<self.max_nodes:

			if i>0 and i%100==0 and self.display:
				print "searching node {}".format(i)

			## Pop best node according to heuristics
			current = self.rewardSelection(QReward, QNovelty)
			

			if current in [None, 'pickMaxNode']:

				if self.stall_mode:
					node = max(visited, key=lambda n:(n.intrinsic_reward, len(n.actionSeq)))
				else:
					if self.display:
						print "Failed to find a novel node. Quitting"
					node = start

				parentNode = node
				self.solution = node.actionSeq

				## If you planned in 'stall' mode and didn't get a solution, make sure you return something anyway (otherwise main agent cycle will break)
				if self.stall_mode and not self.solution:
					# print "you should never actually end up here"
					if QReward:
						node = max(QReward, key=lambda n:(n.intrinsic_reward, len(n.actionSeq)))
					else:
						## QReward only has nodes that didn't result in loss states. Return *some* plan here to make sure things don't break
						## This is a plan of taking a single 'wait' action.
						if self.display:
							print "QReward was empty -- returning a plan of a single 'none' action"
						start = Node(self.rle, self, [], None)
						start.rle = self.rle
						child = Node(self.rle, self, start.actionSeq+[0], start)
						child.eval()
						node = child

					parentNode = node
					self.solution = node.actionSeq

				gameString_array, object_positions_array = [], []
				while parentNode is not None:
					gameString_array.append(parentNode.rle.show())
					object_positions_array.append(copy.deepcopy(parentNode.rle))
					parentNode = parentNode.parent
				self.gameString_array = gameString_array[::-1]
				self.object_positions_array = object_positions_array[::-1]

				## If we failed to find a plan and weren't in 'stall' mode, we should tell the metacontroller we'd like to quit.
				## It then will quit if this happens a couple times.
				self.quitting = True

				if self.display:
					print "was in None or PickMaxNode"

				return node, gameString_array, object_positions_array

			
			##
			## Normal case:
			##

			## Update dictionary of locations visited by avatar in search, to encourage it to move around (this is to counterbalance IW: If we're tracking lots of different items in IW, it's possible to get novelty by just watching the world unfold, and usually this isn't the way to find a good plan. So avatar will move around even if it could have gotten IW novelty without doing so.)
			try:
				(x, y) = np.array((current.rle._game.getAvatars()[0].rect.x,
					current.rle._game.getAvatars()[0].rect.y))/self.pixel_size
				self.visited_positions[x, y] += 1
			except IndexError:
				pass

			current.updateNoveltyDict(QNovelty, QReward)
			visited.append(current)

			current_actions = self.actions

			try:
				# If there's already a Missile on the screen
				# and the projectile class is a singleton
				# and the action chosen is shooting
				# and we're safe:
				# Don't search actual actions -- just search what happens if you wait for the thing you shot to get somewhere.
				# Removing this just enlarges the search tree
				if (current.rle._game.getAvatars() and hasattr(current.rle._game.getAvatars()[0], 'stype') and
						'Missile' in str(self.theory.classes[current.rle._game.getAvatars()[0].stype][0].vgdlType) and
						current.rle.findObjectsInRLE(current.rle._game.getAvatars()[0].stype) and
						'singleton' in self.theory.classes[current.rle._game.getAvatars()[0].stype][0].args and
						bool(self.theory.classes[current.rle._game.getAvatars()[0].stype][0].args['singleton']) and
						len([s for s in current.rle._game.sprite_groups[current.rle._game.getAvatars()[0].stype] if s not in current.rle._game.kill_list])>0):
					current_actions = [0]
					avatar = current.rle._game.getAvatars()[0]
					killer_sprites = [s for k in self.killer_types for s in current.rle._game.sprite_groups[k]]
					if killer_sprites:
						nearest = find_nearest_sprite(avatar, killer_sprites)
						if manhattan_distance(current.rle._rect2pos(avatar.rect), current.rle._rect2pos(nearest.rect))>3:
							current_actions = [0]
						else:
							current_actions = self.actions
							if self.display:
								print "didn't change current_actions; will plan normally"
								print "nearest dangerous sprite:", manhattan_distance(current.rle._rect2pos(avatar.rect), current.rle._rect2pos(nearest.rect))

			except (IndexError, AttributeError, TypeError) as e:
				print "Problem checking missile-shooting conditions."
				pass

			if self.display:
				print "________________"
				if current.actionSeq:
					print actionDict[current.actionSeq[-1]]
				print current.rle.show()

			## See what happens when we take each available action from current node
			for a in current_actions:
				skipAction = False
				if not skipAction:
					child = Node(self.rle, self, current.actionSeq+[a], current)
					child.eval() ## Evaluate child node value

					ended, win = child.terminal, child.win

					if self.firstOrderHorizon:
						# Return plan if first-order progress was made towards
						# a win condition (if we're running in short-term mode)
						foundWin = False
						for term in self.theory.terminationSet:
							if isinstance(term, SpriteCounterRule) and term.termination.win==True:
								stype = term.termination.stype
								n_stypes = len([0 for sprite in child.rle.findObjectsInRLE(stype)])
								if stype in self.starting_stype_n.keys() and self.starting_stype_n[stype] > n_stypes:
									if ended and not win:
										child.win, foundWin = False, False
									else:
										child.terminal = True
										child.win, foundWin = True, True
										if self.display:
											print "exiting early because progress was made toward", stype

							elif isinstance(term, MultiSpriteCounterRule) and term.termination.win==True:
								stypes = term.termination.stypes
								n_stypes = sum([len(child.rle.findObjectsInRLE(stype)) for stype in stypes if child.rle.findObjectsInRLE(stype)])
								if tuple(stypes) in self.starting_stype_n.keys() and self.starting_stype_n[tuple(stypes)] > n_stypes:
									if ended and not win:
										child.win, foundWin = False, False
									else:
										child.terminal = True
										child.win, foundWin = True, True
										if self.display:
											print "exiting early because progress was made toward", stypes
							if foundWin:
								break

					## If we reach a state that the planner should consider a win state (meaning either a real win or a subgoal win in short-term mode, or a curiosity goal in either mode)
					if child.win:
						## Store winning state (and grab winning plan and states) so we can compare predictions with reality in main_agent as we execute the plan
						self.winning_states.append(child)
						node = child
						gameString_array, object_positions_array = [], []
						while node is not None:
							gameString_array.append(node.rle.show(color='green'))
							object_positions_array.append(node.rle)
							node = node.parent
						self.gameString_array = gameString_array[::-1]
						self.object_positions_array = object_positions_array[::-1]
						ended, win, t = child.rle._isDone(getTermination=True)

						self.solution = child.actionSeq
					else:
						if not (child.terminal and not child.win):
							QNovelty.append(child)
							QReward.append(child)
			i+=1
			self.total_nodes_selected = i
			self.total_nodes_opened += len(current_actions)

			if self.winning_states:
				bestNodes = sorted(self.winning_states, key=lambda n: (-n.intrinsic_reward))
				bestNode = bestNodes[0]
				if self.display:
					print "found winning states"
				return bestNode, gameString_array, object_positions_array

		self.solution = []

		## Stall mode
		if self.stall_mode:
			if QReward:
				if self.display:
					print "In short-horizon mode; selecting highest-reward longest sequence"
				node = max(QReward, key=lambda n:(n.intrinsic_reward, len(n.actionSeq)))
			else:
				## QReward only has nodes that didn't result in loss states. Return *some* plan here to make sure things don't break
				## This is a plan of taking a single 'wait' action.
				if self.display:
					print "QReward was empty -- returning a futile plan of a single 'none' action"
				start = Node(self.rle, self, [], None)
				start.rle = self.rle
				child = Node(self.rle, self, start.actionSeq+[0], start)
				child.eval()
				node = child

			parentNode = node
			self.solution = node.actionSeq

			gameString_array, object_positions_array = [], []
			while parentNode is not None:
				gameString_array.append(parentNode.rle.show())
				object_positions_array.append(copy.deepcopy(parentNode.rle))
				parentNode = parentNode.parent
			self.gameString_array = gameString_array[::-1]
			self.object_positions_array = object_positions_array[::-1]
			if not self.stall_mode and self.display:
				print "End of shorthorizon plan"
			elif self.stall_mode and self.display:
				print "End of stall_mode plan"
			return node, gameString_array, object_positions_array
		return None, None, None

class Node():
	def __init__(self, rle, WBP, actionSeq, parent):
		self.rle = rle
		self.WBP = WBP
		self.actionSeq = actionSeq
		self.parent = parent
		self.state = {}
		self.candidates = set()
		self.novelty = None
		self.reward = None
		self.intrinsic_reward = 0
		self.metabolic_cost = 0
		self.children = None
		self.reconstructed=False
		self.expanded = False
		self.rolloutDepth = max(rle.outdim)
		if self.parent is not None:
			self.rolloutArray = parent.rolloutArray[1:]
		else:
			self.rolloutArray = []
		self.okOutcomes = None
		self.badOutcomes = None

	def fastcopy(self, rle):
		## Method for rapid copying of a simulator environment (the rle)
		newRle = self.empty_copy(rle)
		for k,v in rle.__dict__.iteritems():
			ctype = str(type(getattr(rle,k)))
			if 'defaultdict' in ctype or 'dict' in ctype:
				newRle.__dict__[k] = v.copy()
			elif 'list' in ctype:
				newRle.__dict__[k] = v[:]
			else:
				newRle.__dict__[k] = v

		newRle._game = self.empty_copy(rle._game)
		ignoreKeys = ['spriteDistribution',
					  'object_token_spriteDistribution',
					  'spriteUpdateDict',
					  'movement_options',
					  'object_token_movement_options',
					  'uiud']
		sprite_attrs = ['ID', 'name','rect','x','y','orientation','stypes',
						'lastrect','lastmove','stypes', 'lastdisplacement',
						'speed','cooldown','direction','color','colorName']

		for k,v in rle._game.__dict__.iteritems():
			if k in ignoreKeys: continue

			ctype = str(type(getattr(rle._game,k)))

			if 'list' in ctype:
				if k != 'kill_list':
					newRle._game.__dict__[k] = v[:]
				else:
					newRle._game.kill_list = v[:]
			elif 'defaultdict' in ctype or 'dict' in ctype:
				if k != 'sprite_groups':
					newRle._game.__dict__[k] = quickcopy(v)
				else:
					new_sprite_groups = defaultdict(list)
					for group_name, group in rle._game.sprite_groups.iteritems():
						for sprite in group:
							if sprite.colorName == 'DARKGRAY':
								new_sprite_groups[group_name].append(sprite)
							else:
								new_sprite = self.empty_copy(sprite)
								try:
									for attr in sprite.__dict__.keys():
										if hasattr(sprite, attr):
											setattr(new_sprite, attr, getattr(sprite, attr))
									setattr(new_sprite, 'resources', quickcopy(sprite.__dict__['resources']))
								except:
									embed()
								new_sprite_groups[group_name].append(new_sprite)
					newRle._game.sprite_groups = new_sprite_groups
			elif 'vgdl' in ctype:
				newRle._game.__dict__[k] = quickcopy(v)
			else:
				setattr(newRle._game, k, quickcopy(v))
		return newRle

	def rollout(self, Vrle, thingWeShoot):
		## Do rollouts when we shoot projectiles, to get credit for their trajectory rather than just their one-step value
		successfulRollout = False
		j=0
		while not successfulRollout:
			vrle = self.fastcopy(Vrle)
			potentialProjectiles = [s for s in vrle._game.sprite_groups[thingWeShoot] if vrle._game.sprite_groups[thingWeShoot] and s.lastmove==0]
			thingWeShot = potentialProjectiles[0] if potentialProjectiles else None

			prevHeuristicVal = self.heuristics(vrle, **self.WBP.rolloutHyperparameters)
			rolloutArray = []
			i=0
			terminal, win = vrle._isDone()

			while i<self.rolloutDepth and thingWeShot not in vrle._game.kill_list and not terminal:
				a = random.choice([K_UP, K_DOWN, K_LEFT, K_RIGHT]) ## move randomly during rollout
				res = vrle.step(a, getTermination=True, getEffectList=True)
				if self.WBP.display:
					print vrle.show(indent=True, color='cyan')
				currHeuristicVal = self.heuristics(vrle, **self.WBP.rolloutHyperparameters)
				heuristicVal = currHeuristicVal-prevHeuristicVal
				rolloutArray.append(heuristicVal)
				prevHeuristicVal = currHeuristicVal
				terminal, win, t = vrle._isDone(getTermination=True)
				if self.WBP.display and win and t.name=='SpriteCounter':
					print t.stype
				if self.WBP.firstOrderHorizon:
					# Return plan if any subgoal progress was made towards
					# a win condition
					foundWin = False
					for term in self.WBP.theory.terminationSet:
						if isinstance(term, SpriteCounterRule) and term.termination.win==True:
							stype = term.termination.stype
							n_stypes = len([0 for sprite in vrle.findObjectsInRLE(stype)])
							if stype in self.WBP.starting_stype_n.keys() and self.WBP.starting_stype_n[stype] > n_stypes:
								if not (terminal and not win):
									terminal, win = True, True
									if self.WBP.display:
										print "exiting rollout early because progress was made toward", stype
						elif isinstance(term, MultiSpriteCounterRule) and term.termination.win==True:
							stypes = term.termination.stypes
							n_stypes = sum([len(vrle.findObjectsInRLE(stype)) for stype in stypes if vrle.findObjectsInRLE(stype)])
							if tuple(stypes) in self.WBP.starting_stype_n.keys() and self.WBP.starting_stype_n[tuple(stypes)] > n_stypes:
								if not(terminal and not win):
									terminal, win = True, True
									if self.WBP.display:
										print "exiting rollout early because progress was made toward", stypes
						if win:
							break

				if terminal:
					try:
						if (t.name=='NoveltyTermination' and
								self.rle._game.getAvatars()[0].stype
								not in [t.s1, t.s2]):
							# If we have a novelty termination not involving
							# the projectile, ignore it. That is, if you shoot a projectile but the agent witnesses a collision involving two other objects, shooting the projectile shouldn't get credit for that event.
							terminal, win = False, False
						## More generally, if the thing we shot wasn't involved in any interaction, ignore it.
						if thingWeShot is not None:
							if not any([thingWeShot.ID in e for e in res['effectList']]):
								terminal, win = False, False
						if terminal:
							if self.WBP.display:
								print t.name, t.s1, t.s2
					except (IndexError, AttributeError) as e:
						# Avatar is dead or doesn't have a projectile
						pass
				i+=1
			## we want optimistic estimates of the future value of a shot.
			## Take up to 100 samples but don't get caught in an infinite loop.
			if terminal and not win and j<100:
				successfulRollout = False
				j+=1
			else:
				successfulRollout = True
		if win:
			if self.WBP.display:
				print "rolloutwin"
			self.terminal = terminal
			self.win = win
		return rolloutArray

	def spritecounter_val(self, theory, term, stype, rle, first_alpha=10000.,
						  second_alpha=100, negative_mult=.1, surrogate_multisprite_counter=False):

		# First order: progress in terms of number of sprites remaining.
		# Second order: distance to the closest instance of a target sprite type.

		val = 0
		if not surrogate_multisprite_counter:
			compute_second_order = True
		else:
			compute_second_order = False

		# Check if condition is win or loss and multiply accordingly.
		if term.termination.win:
			mult = -1
		else:
			mult = negative_mult

		# Get all types that kill or transform stype (the target)
		killer_types = [
			inter.slot2 for inter in theory.interactionSet
			if (inter.interaction in ['killSprite', 'transformTo', 'collectResource'] and
				 not inter.generic and
				 not inter.preconditions
				and inter.slot1 == stype)]

		## If you can shoot a Flicker, give yourself credit for being close to things it kills, but remove credit for that Flicker being close to those things.
		try:
			if rle._game.getAvatars()[0].stype in killer_types:
				if rle._game.getAvatars()[0].stype in theory.classes:
					color = theory.classes[rle._game.getAvatars()[0].stype][0].color
				else:
					color = rle._game.sprite_groups[rle._game.getAvatars()[0].stype][0].colorName

				if 'Flicker' in str(theory.spriteObjects[color].vgdlType) or 'Missile' in str(theory.spriteObjects[color].vgdlType):
					killer_types.append(rle._game.getAvatars()[0].name)
					killer_types.remove(rle._game.getAvatars()[0].stype)

		except (IndexError, AttributeError) as e:
			pass

		# This list comprehension checks whether the avatar kills the stype with a preconditioned
		# interaction, and if so adds 'avatar' to the list as well as the precondition for that rule
		avatar_preconditions = [
			(inter.slot2, inter.preconditions) for inter in theory.interactionSet
			if (inter.interaction in ['killSprite', 'killIfOtherHasMore', 'transformTo']  and
				 not inter.generic
				 and inter.preconditions
				and inter.slot1 == stype)]

		tmp_list = []

		## If we have preconditions, find the objects that we should go to given that we satisfy the relevant preconditions. E.g., if we have a key and want to know what
		## happens with item x, go to it.
		for avatar in avatar_preconditions:

			precondition = list(avatar[1])[0]
			item, num, negated, operator_name = precondition.item, precondition.num, precondition.negated, precondition.operator_name
			if negated:
				oppositeOperatorMap = {"<=": ">", ">=": "<", "<": ">=", ">": "<="}
				true_operator = oppositeOperatorMap[operator_name]
			else:
				true_operator = operator_name
			try:
				current_resource = rle._game.sprite_groups[avatar[0]][0].resources[precondition.item]
				## If we satisfy the precondiiton, append to tmp_list, then to killer_types (meaning we are capable of killing stype now)
				if eval("{}{}{}".format(current_resource, true_operator, num)):
					tmp_list.append(avatar)
			except (IndexError, KeyError) as e:
				pass

		for t in tmp_list:
			killer_types.append(t[0])
			avatar_preconditions.remove(t)

		# Get attributes from terminationSet
		limit = term.termination.limit

		## No longer used (I think)
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
			n_stypes = len([0 for sprite in rle.findObjectsInRLE(stype)]) if rle.findObjectsInRLE(stype) else 0
			distance_to_goal = abs(n_stypes - limit)

		if distance_to_goal!=0:
			val -= float(mult * first_alpha) / distance_to_goal ## Penalize quadratically for classes for which we'd have to kill many instances.
		else:
			val -= mult*first_alpha ## we shouldn't go in here, as if we've actually destroyed the relevant sprite we'll trigger a win condition.

		if compute_second_order:
			## Get all positions of objects whose type is in killer_types; compute minimum distance
			## of each to the stypes we have to destroy. Return min over all mins.
			objs = [rle.findObjectsInRLE(ktype) for ktype in killer_types]
			objs = [obj for obj in objs if obj]

			try:
				if len(objs)>0:
					kill_positions = np.concatenate([o for o in objs if len(o)==max([len(obj) for obj in objs])])
				else:
					kill_positions = np.array(objs)
			except TypeError:
				kill_positions = np.array([])

			possiblePairList = []
			stype_positions = rle.findObjectsInRLE(stype)
			try:
				# A consequence of the two-way generic interactions in the
				# theory is that minimum-distance object pairs whose interactions
				# were not yet observed will have their distance penalized twice
				# as much when none of those objects is an avatar. This implies
				# that avatar novel interactions will be favored over other ones
				possiblePairList = [manhattan_distance(obj, pos)
					 for pos in kill_positions
					 for obj in stype_positions]

				distance = min(possiblePairList)
				# print("second order distance is {}".format(distance))
			except (ValueError, TypeError) as e:
				distance = 100

			if possiblePairList:
				n_sprites = len(stype_positions) if stype!='avatar' else 20
				## More credit for progress toward objects that are less numerous (heuristic way of evaluating feasibility of goal)
				added_val = float(mult * second_alpha * distance)/n_sprites**2
			elif stype!='avatar':
				# This helps in cases in which either the stype or the killer_type is not always on the screen
				# Then, you should not be disincentivized to create it, which can be achieved through this high penalty
				distance = 101
				added_val = float(mult * second_alpha * distance)
			elif not stype_positions:
				## If we couldn't compute a second-order distance because the avatar is dead, give infinite penalty.
				added_val = -float('inf')
			else:
				added_val = 0.
			val += added_val

			if avatar_preconditions:
				avatars = [rle.findObjectsInRLE(ktype[0]) for ktype in avatar_preconditions]

				resource_names = [list(resource[1])[0].item for resource in avatar_preconditions]

				resource_yielder_names = [[inter.slot2 if (inter.interaction=='changeResource' and inter.args['resource']==res) else 
						inter.slot1 if (inter.interaction=='collectResource' and res==inter.args['resource']==res) else None
						for inter in theory.interactionSet] for res in resource_names]

				resource_yielder_names = [[r for r in ryn if r] for ryn in resource_yielder_names] ## Remove 'None' yielded by last else condition above

				try:
					resource_positions = [np.concatenate([rle.findObjectsInRLE( yielder) for yielder in yielders]) for yielders in resource_yielder_names]
				except:
					resource_positions = []

				resource_limits = np.array([list(resource[1])[0].num + 1
					if list(resource[1])[0].operator_name == '>'
					else list(resource[1])[0].num
					for resource in avatar_preconditions])
				try:
					avatar_resource_quantities = np.array([rle._game.getAvatars()[0].resources[res] for res in resource_names])
				except IndexError:
					avatar_resource_quantities = np.array([0 for res in resource_names])
				precondition_distances = []
				try:
					for (obj1_positions, obj2_positions) in zip(avatars, resource_positions):
						# A consequence of the two-way generic interactions in the
						# theory is that minimum-distance object pairs whose interactions
						# were not yet observed will have their distance penalized twice
						# as much when none of those objects is an avatar. This implies
						# that avatar novel interactions will be favored over other ones
						try:
							possiblePairList = np.array([manhattan_distance(obj1, obj2)
								for obj1 in obj1_positions
								for obj2 in obj2_positions])
						except:
							pass

						precondition_distances.append(min(possiblePairList))

					physical_distance = min(precondition_distances)
					sprite_n_distance = abs(resource_limits-avatar_resource_quantities)
					# Normalize by number of sprites, enforcing a prior that encourages goals that involve killing fewer objects
					val += float(mult * second_alpha * (physical_distance / 10.)) - 10000
					val += float(mult * second_alpha * sprite_n_distance) - 10000

				except (ValueError, TypeError) as e:
					pass

				if not resource_positions:
					# print "didn't find resource positions"
					# This helps in cases in which either the stype or the killer_type is not always on the screen
					# Then, you should not be disincentivized to create it, which can be achieved through this high penalty
					distance = 100
					val += float(mult * second_alpha * distance) - 20000

		return val

	def multispritecounter_val(self, theory, term, rle, first_alpha=10000,
							   second_alpha=100):
		## Warning: This will only work if term.termination.limit==0. Otherwise you could
		## end up with, say, count(stype)==1 for each constituent stype, meaning the terminations
		## would all be fulfilled, even though sum([count(stype) for stype in stypes]) != 1.

		val = 0
		for stype in term.termination.stypes:
			val += self.spritecounter_val(theory, term, stype, rle,
				first_alpha=first_alpha, second_alpha=second_alpha, surrogate_multisprite_counter=True)
		val /= len(term.termination.stypes)
		return val

	def noveltytermination_val(self, theory, term, s1, s2, rle, first_alpha=1000,
						  second_alpha=10):
		val = 0
		compute_second_order = True

		# print term.termination.win, term.termination.args
		# Check if condition is win or loss and multiply accordingly
		if term.termination.win:
			mult = -1
		else:
			compute_second_order = False
			mult = 1

		# ## Don't give heuristic bonus for using the flicker. But the agent is still incentivized to try to make the flicker interact with other objects because of noveltyTerminationConditions.

		## If the terminationRule is precondition-dependent, check that first. Don't give heuristic val if the preconditions aren't fulfilled. As in, if you're curious about Avatar_with_key - red_object, only evaluate proximity between avatar and red if the avatar has the key.
		if term.termination.args:
			item, num, negated, operator_name = term.termination.args.item, term.termination.args.num, term.termination.args.negated, term.termination.args.operator_name
			if negated:
				oppositeOperatorMap = {"<=": ">", ">=": "<", "<": ">=", ">": "<="}
				true_operator = oppositeOperatorMap[operator_name]
			else:
				true_operator = operator_name

			try:
				resource_str = str(rle._game.getAvatars()[0].resources[item])
			except IndexError:
				return 2 * mult * first_alpha, 10000

			if not eval(resource_str+true_operator+str(num)):
				return 0, 10000		

		if compute_second_order:
			## Get all positions of objects whose type is in killer_types; compute minimum distance
			## of each to the stypes we have to destroy. Return min over all mins.

			if 'Flicker' in str(theory.classes[s1][0].vgdlType) and not ('Flicker' in str(theory.classes[s2][0].vgdlType) or s2=='avatar'):
				s1 = s2
				s2 = 'avatar'

			s2_positions = rle.findObjectsInRLE(s2)
			s1_positions = rle.findObjectsInRLE(s1)
		
			## Don't return a value for novelty for the mere existence of a projectile that has novelty bonuses
			if self.WBP.thingWeShoot in theory.classes and self.WBP.thingWeShoot in [s1,s2]:
				return 0, 10000

			n_sprites = len(s1_positions) if s1_positions else 0
			possiblePairList = []
			try:
				# A consequence of the two-way generic interactions in the
				# theory is that minimum-distance object pairs whose interactions
				# were not yet observed will have their distance penalized twice
				# as much when none of those objects is an avatar. This implies
				# that non-avatar novel interactions will be favored over others

				possiblePairList = [manhattan_distance(obj, pos)
					 for pos in s2_positions
					 for obj in s1_positions
					 if manhattan_distance(obj, pos) != 0]
				distance = min(possiblePairList)
					 # This is a trick to avoid getting distance 0 for objects
					 # of same type. If the list turns out to be empty, it will
					 # raise an error and set the distance to 0
				# print distance
			except (ValueError, TypeError) as e:
				distance = 0

			if possiblePairList:
				n_sprites = len(possiblePairList)
				## Normalize by number of sprites, enforcing a prior that encourages goals that involve killing fewer objects
				## as you get closer to the item, this quantity increases, contributing to a higher overall score
				val += float(mult * second_alpha * distance /max(self.rle.outdim[0], self.rle.outdim[1]) )

		if n_sprites==0:
			return val, 10000
		return val, distance*n_sprites

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

	def heuristics(self, rle=None, sprite_first_alpha=10000.,
		sprite_second_alpha=100, sprite_negative_mult=.1,
		multisprite_first_alpha=10000, multisprite_second_alpha=100,
		novelty_first_alpha=1000, novelty_second_alpha=10, time_alpha=10):
		
		## "No goal gradient" ablations
		if any([s in self.WBP.lesion for s in ['AGH1', 'AGH3']]):
			return 0.

		if rle==None:
			rle = self.rle

		theory = self.WBP.theory
		heuristicVal = 0
		avatarNoveltyVals = []
		for term in theory.terminationSet:
			if isinstance(term, SpriteCounterRule):
				spritecounter_val = self.spritecounter_val(theory, term, term.termination.stype, rle,
					first_alpha=sprite_first_alpha, second_alpha=sprite_second_alpha,
					negative_mult=sprite_negative_mult)
				heuristicVal += spritecounter_val

			elif isinstance(term, MultiSpriteCounterRule):
				multispritecounter_val = self.multispritecounter_val(theory, term, rle,
						first_alpha=multisprite_first_alpha, second_alpha=multisprite_second_alpha)
				heuristicVal += multispritecounter_val

			elif isinstance(term, TimeoutRule):
				timeout_val = time_alpha * \
					self.timeout_val(theory, term, rle)
				heuristicVal += timeout_val

			elif isinstance(term, NoveltyRule):
				noveltytermination_val, ranking = self.noveltytermination_val(
					theory, term, term.termination.s1, term.termination.s2, rle,
					first_alpha=novelty_first_alpha, second_alpha=novelty_second_alpha)
				if 'avatar' == term.termination.s2:
					avatarNoveltyVals.append([noveltytermination_val,
						ranking])
				else:
					heuristicVal += noveltytermination_val

		if avatarNoveltyVals:
			heuristicVal += min(avatarNoveltyVals, key= lambda x: x[1])[0]
				
		return heuristicVal

	def position_score(self, factor=1.):
		try:
			(x, y) = np.array((self.rle._game.getAvatars()[0].rect.x,
				self.rle._game.getAvatars()[0].rect.y))/self.WBP.pixel_size
			# print factor * self.WBP.visited_positions[x, y]
			return factor * self.WBP.visited_positions[x, y]**2
		except IndexError:
			# print "index error in position score"
			return 0

	def empty_copy(self, obj):
		class Empty(obj.__class__):
			def __init__(self): pass
		newcopy = Empty()
		newcopy.__class__ = obj.__class__
		return newcopy

	def getToCurrentState(self):
		if self.parent and self.parent.rle is not None:
			## try to copy parent lastState. Then take action and store as current lastState. If that fails, replay from beginning and store as current lastState
			try:
				vrle = self.fastcopy(self.parent.rle)
				if len(self.actionSeq)>0:
					a = self.actionSeq[-1]
					res = vrle.step(a, return_obs=True)
					self.terminal, self.win = res['ended'], res['win']
					self.metabolic_cost = 0

			except:
				print "conditions met but copy failed"
				embed()
		else:
			self.reconstructed=True
			vrle = self.fastcopy(self.rle)
			self.terminal, self.win = vrle._isDone()
			i=0
			while not self.terminal and len(self.actionSeq)>i:
				a = self.actionSeq[i]
				res = vrle.step(a, return_obs=True)
				self.metabolic_cost = 0
				self.terminal, self.win = res['ended'], res['win']
				i += 1
		return vrle, self.terminal, self.win

	def eval(self):
		# ## Evaluate current node, including calculating intrinsic reward: f(rewards, heuristics, etc.)

		self.rle, self.terminal, self.win = self.getToCurrentState()

		self.updateObjIDs(self.rle)

		self.state = self.WBP.calculateAtoms(self.rle)

		for i in range(1,self.WBP.IW_k+1):
			for c in itertools.combinations(self.state, i):
				c = tuple(sorted(c))
				if self.WBP.trueAtoms[c] == 0:
					self.candidates.add(c)

		self.updateNovelty()

		if self.WBP.allowRollouts and len(self.actionSeq)>0 and self.actionSeq[-1]==32:
			## if the thing we shoot is a missile, do a rollout
			if 'Missile' in str(self.WBP.theory.classes[self.WBP.thingWeShoot][0].vgdlType):
				self.rolloutArray = self.rollout(self.rle, self.WBP.thingWeShoot)

		## Calculate heuristic value
		self.heuristicVal = self.heuristics(**self.WBP.hyperparameters)

		## Add position_score (to counteract IW) and game score
		self.intrinsic_reward = self.heuristicVal + self.position_score(self.WBP.position_score_multiplier) + self.rle._game.score

		try:
			## Planner should return a plan when the agent has reached the limit of any particular resource (because we now should be curious about new objects, which we're taking care of in main_agent)
			if any([self.rle._game.getAvatars()[0].resources[k]==self.WBP.theory.resource_limits[k] for k in self.rle._game.getAvatars()[0].resources.keys() if k not in self.WBP.seen_limits]):
				if self.WBP.display:
					print "resource limit win. Need {} and have {}".format(self.WBP.theory.resource_limits, self.rle._game.getAvatars()[0].resources)
				self.win=True
		except IndexError:
			pass

		return self.win

	def updateNovelty(self):
		if len(self.candidates)==0:
			self.novelty = self.WBP.IW_k+1
		else:
			self.novelty = min([len(c) for c in self.candidates])
		return self.novelty

	def updateNoveltyDict(self, QNovelty, QReward):
		jointSet = list(set(QNovelty+QReward))
		for c in self.candidates:
			if self.WBP.trueAtoms[c] == 0:
				self.WBP.trueAtoms[c] = 1
				for n in jointSet:
					if c in n.candidates:
						n.candidates.remove(c)
		for n in jointSet:
			n.novelty = n.updateNovelty()
		return

	def updateObjIDs(self, vrle):
		i = 0
		for objType in vrle._game.sprite_groups:
			for s in vrle._game.sprite_groups[objType]:
				if s.ID not in self.WBP.objIDs.keys():
					if s.name=='bullet':
						s.ID = len(vrle.getAliveSpritesByName(s.name))
					else:
						s.ID = len(vrle._game.sprite_groups[objType])
					self.WBP.objIDs[s.ID] = (len(self.WBP.objIDs.keys())+1) * 100 * (self.rle.outdim[0]*self.rle.outdim[1]+self.WBP.padding)
					i+=1
		return

def gen_color():
	from vgdl.colors import colorDict
	color_list = colorDict.values()
	color_list = [c for c in color_list if c not in ['UUWSWF']]
	for color in color_list:
		yield color
	
def read_gvgai_game(filename):
	with open(filename, 'r') as f:
		new_doc = []
		g = gen_color()
		for line in f.readlines():
			new_line = (" ".join([string if string[:4]!="img="
				else "color={}".format(next(g))
				for string in line.split(" ")]))
			new_doc.append(new_line)
		new_doc = "\n".join(new_doc)
	return new_doc



if __name__ == "__main__":
	import argparse

	## Continuous physics games can't work right now. RLE is discretized, getSensors() relies on this, and a lot of the induction/planning
	## architecture depends on that. Will take some work to do this well. Best plan is to shrink the grid squares and increase speeds/strengths of
	## objects.
	# gameFilename = "examples.gridphysics.theorytest"
	# gameFilename = "examples.gridphysics.boulderdash"
	# gameFilename = "examples.continuousphysics.breakout_big"


	gameFileString = 'all_games'


	parser = argparse.ArgumentParser(description='Process game number.')
	parser.add_argument('--game_name', type=str, default=str(0), help='game name')
	parser.add_argument('--hyperparameter_index', type=str, default='short-term', help='hyperparameter_index')
	parser.add_argument('--level', type=int, default=0, help='level')
	args = parser.parse_args()
	game_name = args.game_name
	hyperparameter_index = args.hyperparameter_index
	level_num = args.level

	if game_name!=str(0):
		gvgname = "./{}/{}".format(gameFileString,game_name)
		gameString = read_gvgai_game('{}.txt'.format(gvgname))
		game_levels = [l for l in os.listdir(gameFileString) if l[0:len(game_name+'_lvl')] == game_name+'_lvl']
		print game_levels
		level_game_pairs = []
		for level_number in range(len(game_levels)):
			with open('{}_lvl{}.txt'.format(gvgname, level_number), 'r') as level:
				level_game_pairs.append([gameString, level.read()])

		gameString, levelString = level_game_pairs[level_num]
		rleCreateFunc = lambda: createRLInputGameFromStrings(gameString, levelString)
		gameFilename = game_name

	else:
		gameFilename = "examples.gridphysics.aliens"
		gameString, levelString = defInputGame(gameFilename, randomize=True)
		rleCreateFunc = lambda: createRLInputGame(gameFilename)
	rle = rleCreateFunc()


	hyperparameters = hyperparameter_sets[hyperparameter_index]
	planner_hyperparameters = dict((k, hyperparameters[k]) for k in hyperparameters.keys() if k not in ['short_horizon', 'first_order_horizon'])
	max_nodes = 500 if hyperparameters['short_horizon'] else 1000

	## Initialize planner
	p = WBP(rle, gameFilename, max_nodes=max_nodes, 
			firstOrderHorizon=hyperparameters['first_order_horizon'], stall_mode=False, 
			hyperparameters=planner_hyperparameters, extra_atom=True)

	t1 = time.time()
	bestNode, gameStringArray, objectPositionsArray = p.BFS()
	t2 = time.time()-t1
	solution = []
	if bestNode is not None:
		solution = p.solution
		gameString_array = p.gameString_array
		objectPositionsArray = objectPositionsArray[::-1]
	if solution and not p.quitting:
		print "============================================="
		print "got solution of length", len(solution)
		print colored(p.gameString_array[0], 'green')
		for i,g in enumerate(p.gameString_array[1:]):
			print actionDict[solution[i]]
			print colored(g, 'green')
		print "============================================="

	print colored(rle.show(), 'blue')
	for a in solution:
		rle.step(a)
		print colored(rle.show(), 'blue')

	print rle._isDone()
	print "total nodes opened: {}. total nodes selected: {}".format(p.total_nodes_opened, p.total_nodes_selected)
	print "total time searched: {} seconds".format(t2)

