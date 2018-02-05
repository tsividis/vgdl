# from IPython import embed
# from multiprocessing import Pool
import pathos.pools as pp
import multiprocessing
from multiprocessing.pool import ThreadPool
from functools import partial
import threading
from util import *
from core import colorDict, VGDLParser, sys, keyPresses
from ontology import *
from theory_template import TimeStep, Precondition, InteractionRule, TerminationRule, TimeoutRule, \
SpriteCounterRule, MultiSpriteCounterRule, ruleCluster, Theory, Game, writeTheoryToTxt, generateSymbolDict, \
generateTheoryFromGame, expandLine, expandSprites, PreconditionInduction
import os, subprocess, shutil
from collections import defaultdict
# import WBP_grid, WBP_continuous
import importlib
import numpy as np
import ipdb, time
import os, subprocess, shutil
import copy
import math
import warnings
from metaplanner import translateEvents, observe
from rlenvironmentnonstatic import createRLInputGame, createRLInputGameFromStrings, defInputGame, createMindEnv
from termcolor import colored
from line_profiler import LineProfiler
from vgdl.util import manhattanDist, manhattanDist2
from pygame.locals import K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT
from colors import colorDict
from pprint import pprint
# Plotting
from matplotlib import pyplot as plt
import seaborn as sns
sns.set_context('paper', font_scale = 2, rc = {'lines.linewidth': 2})
sns.set_style("ticks", {'axes.grid': True})
import copy_reg
import types

AvatarTypes = [MovingAvatar, HorizontalAvatar, VerticalAvatar, FlakAvatar, AimedFlakAvatar, OrientedAvatar,
RotatingAvatar, RotatingFlippingAvatar, NoisyRotatingFlippingAvatar, ShootAvatar, AimedAvatar,
AimedFlakAvatar, InertialAvatar, MarioAvatar]

# orientationPairs = {(0, 1):(0, -1), DOWN:UP, LEFT:RIGHT, RIGHT:LEFT}


def picklecopy(obj):
	return 

class errorMapEntry:
	def __init__(self):
		self.diagnosis = []
		self.targetToken = None
		self.targetClass = None
		self.intPairs = []
		self.culpritClasses = []
	
	def display(self):
		print ""
		print "diagnosis: {}".format(self.diagnosis)
		print "targetToken: {}".format(self.targetToken)
		print "targetClass: {}".format(self.targetClass)
		if self.targetToken is not None:
			print "targetColor: {}".format(self.targetToken.colorName)
		print "intPairs: {}".format(self.intPairs)
		print "culpritClasses: {}".format(self.culpritClasses)

	def copy(self):
		e                   = errorMapEntry()
		e.diagnosis         = self.diagnosis
		e.targetToken       = ccopy(self.targetToken)
		e.targetClass       = self.targetClass
		e.intPairs          = self.intPairs
		e.culpritClasss     = self.culpritClasses
		
		return e

	def __eq__(self, other):
		if self.diagnosis==other.diagnosis and self.intPairs==other.intPairs and self.culpritClasses==other.culpritClasses:
			return True
		else:
			return False

class Agent:
	def __init__(self, modelType, gameFilename):
		self.modelType = modelType
		self.gameFilename = gameFilename
		self.gameString = None
		self.levelString = None
		self.annealingFactor = 1.
		self.shortHorizon = False
		if self.shortHorizon == True:
			self.starting_max_nodes = 1000
			self.max_nodes_annealing = 1.05
		else:
			self.starting_max_nodes = 10000
			self.max_nodes_annealing = 10
		self.firstOrderHorizon = True ## Makes you commit to a plan once first-order distances change (e.g., spritecounter values)
		self.regrounding = 50
		self.selective_regrounding = True
		self.avoid_danger = True
		self.safeDistance = 6
		self.emptyPlansLimit = 5
		self.longHorizonObservationLimit = 2
		self.learnAvatar = True
		self.hypotheses = []
		self.symbolDict = None
		self.finalEventList = []
		self.statesEncountered = []
		self.fakeInteractionRules = []
		self.all_objects = {}
		self.bestSpriteTypeDict = defaultdict(lambda : {})
		self.spriteUpdateDict = defaultdict(lambda : 0)
		self.best_params = None
		## To track how many times we have run spriteType updates to each particular object
		# self.bestSpriteTypeDict = defaultdict(lambda: {'count':0, 'distribution':None})
		self.seen_resources = []
		self.seen_limits = []
		self.new_objects = {}
		self.proposalMemory = defaultdict(lambda:[])
		self.memory = []
		self.rleHistory = []
		self.actionHistory = []
		self.allTheories = []
		self.theoryScoreHistory = []
		self.meanErrorHistory = []
		self.minStepError = []
		self.actionSet = [K_RIGHT, K_LEFT, K_UP, K_DOWN, K_SPACE]
		self.randomTheories = []
		self.benchmarkHistory = []
		self.subsamplePercentage = .2 # e.g., .5 = 50%.
		self.actionsPerIndex = 2
		self.resourceObservations = {'speed':[], 'changeResource':[]}
		self.observed_resources = set()
		self.distributions = PreconditionInduction()
		self.lastObjectState = {}

	def initializeEnvironment(self):
		if self.gameString==None or self.levelString==None:
			self.gameString, self.levelString = defInputGame(self.gameFilename, randomize=False)
		self.rleCreateFunc = lambda: createRLInputGameFromStrings(self.gameString, self.levelString)
		self.rle = self.rleCreateFunc()
		self.rle._game.spriteUpdateDict = self.spriteUpdateDict
		return

	def initializeRLEFromGame(self):
		gameString, levelString = self.gameString, self.levelString
		if gameString==None or levelString==None:
			gameString, levelString = defInputGame(self.gameFilename, randomize=False)
		rleCreateFunc = lambda: createRLInputGameFromStrings(gameString, levelString)
		rle = rleCreateFunc()
		return rle

	def getStateByColor(self, rle):
		state = {}
		for k in rle._game.sprite_groups.keys():
			if len(rle._game.sprite_groups[k]) > 0:
				color = rle._game.sprite_groups[k][0].colorName
				sprite_list = []
				for sprite in rle._game.sprite_groups[k]:
					if sprite not in rle._game.kill_list:
						if hasattr(sprite, 'orientation'):
							o = sprite.orientation 
						else:
							o = (0,0)

						sprite_list.append({'speed':sprite.speed, 'orientation':o, 'position':(sprite.rect.x,sprite.rect.y)})
				state[color] = sprite_list
		return state

	def findNearestSprite(self, sprite, spriteList):
		## returns the sprite in spriteList whose location best matches the location of sprite.
		if spriteList==[]:
			return None
		else:
			return sorted(spriteList, key=lambda x:abs(x.rect[0]-sprite.rect[0])+abs(x.rect[1]-sprite.rect[1]))[0]

	def matchEnvs2(self, envA, envB, debug=False):
		matched_sprites, lonely_sprites_envA, lonely_sprites_envB = [],[],[]
		for k in [key for key in envA._game.sprite_groups.keys() if envA._game.sprite_groups[key]]:
			# Find matching sprites via color
			color = envA._game.sprite_groups[k][0].colorName
			matchingSpritesInEnvA = [s for s in getSpritesByColor(envA._game, color) if s not in envA._game.kill_list]
			matchingSpritesInEnvB = [s for s in getSpritesByColor(envB._game, color) if s not in envB._game.kill_list]
			
			## Remove unique overlapping sprites
			to_remove_from_A, to_remove_from_B = [], []
			for s in matchingSpritesInEnvA:
				matchingSprite = findNearestSprite(s, matchingSpritesInEnvB)
				dist = manhattanDist2(s, matchingSprite)
				if dist==0:
					to_remove_from_A.append(s)
					to_remove_from_B.append(matchingSprite)

			


	# Function matching environment and determining sprites that couldn't be matched
	def matchEnvs(self, envA, envB, debug=False):
		# Initialization
		matched_sprites = [] #tuples of matched sprites: (envA sprite, envB sprite, dist) - helps penalize distance and find missing
		lonely_sprites_envA = [] #envA sprites that have no partner in envB
		lonely_sprites_envB = [] #envB sprites that have no partner in envA
		if debug:
			print "in matchEnvs"
			embed()
		# Loop over keys in envA
		for k in [key for key in envA._game.sprite_groups.keys() if envA._game.sprite_groups[key]]:
			# Find matching sprites via color
			color = envA._game.sprite_groups[k][0].colorName
			matchingSpritesInEnvA = getSpritesByColor(envA._game, color)
			matchingSpritesInEnvA = [s for s in matchingSpritesInEnvA if s not in envA._game.kill_list]
			if matchingSpritesInEnvA == []:
				continue
			matchingSpritesInEnvB = getSpritesByColor(envB._game, color)
			matchingSpritesInEnvB = [s for s in matchingSpritesInEnvB if s not in envB._game.kill_list]
			if matchingSpritesInEnvB == []:
				lonely_sprites_envA.extend(matchingSpritesInEnvA)
				#lonely_sprites_envA = [s for sublist in lonely_sprites_envA for s in sublist]
				continue
			
			# Loop over matching sprites in envA and find corresponding sprites in envB
			## this line is key
			for sprite in matchingSpritesInEnvA:
				corrSprite = self.findNearestSprite(sprite, matchingSpritesInEnvB)
				dist = manhattanDist2(sprite, corrSprite)
				#print (sprite, corrSprite, dist)
				matched_sprites.append( (sprite, corrSprite, dist) )

		# Clean up matched_sprites set towards bijective mapping
		## This only deletes multiple matches, but doesn't re-match
		matched_sprites_envB = [matched_sprites[i][1] for i in range(len(matched_sprites))]
		matched_dist = [matched_sprites[i][2] for i in range(len(matched_sprites))]
		for sprite in matched_sprites_envB:
			## All the indices of sprites that are matched to this one sprite
			indices = [i for i,t in enumerate(matched_sprites) if t[1]==sprite]
			if len(indices)==1: #no multiple mappings to sprite
				continue
			else: #remove mappings with largest distances
				idx_rm = np.argsort(matched_dist)
				idx_rm = [i for i in idx_rm if any(i==indices)][1:] # <-- Looks wrong! We're matching indices to distances!
				#print '>>> TEST', i==indices
				[lonely_sprites_envA.append(matched_sprites[i][0]) for i in idx_rm] #add to-be-removed sprites in envA to lonely list
				[matched_sprites.pop(i-n) for n,i in enumerate(idx_rm)] #removes entries

		# Find sprites that exist in envB but not envA
		matched_sprites_envB = [matched_sprites[i][1] for i in range(len(matched_sprites))]
		for k in [key for key in envB._game.sprite_groups.keys() if envB._game.sprite_groups[key]]:
			color = envB._game.sprite_groups[k][0].colorName
			matchingSprites = getSpritesByColor(envB._game, color)
			if matchingSprites == None:
				continue
			matchingSprites = [s for s in matchingSprites if s not in envB._game.kill_list]
			if matchingSprites == []:
				continue
			for sprite in matchingSprites:
				if not any([matched_sprites_envB[i]==sprite for i in range(len(matched_sprites_envB))]):
					lonely_sprites_envB.append(sprite)

		# ## Test output
		# print '>>> matched_sprites:'
		# for i in range(len(matched_sprites)):
		#   if True: #matched_sprites[i][2]!=0:
		#       print matched_sprites[i]
		# print '>>> lonely_sprites_envA:', [s for s in lonely_sprites_envA]
		# print '>>> lonely_sprites_envB:', [s for s in lonely_sprites_envB]

		## Re-match elements of same class that are 'lonely' in both environments
		# (these could be result of teleporting - to do: add teleportation distance metric here)
		# (Watch out: we could have had a blue block deleted and a different one created somewhere else)
		dist_rematch = []
		mindist_rematch = []
		sprites_rematchA = [] #re-matched sprites in envA
		sprites_rematchB = [] #re-matched sprites in envB
		if lonely_sprites_envB != []:
			to_remove = []
			for sA in lonely_sprites_envA:
				dist_temp = []
				for sB in lonely_sprites_envB:
					if sB.colorName==sA.colorName:
						dist_temp.append( manhattanDist2(sA, sB) )
					else:
						dist_temp.append(2e6)
						to_remove.append(sA) ## If there is no rematch for this sprite, take it off the lonely list.
				dist_rematch.append(dist_temp)
				mindist_rematch.append(min(dist_temp))
			lonely_sprites_envA = [s for s in lonely_sprites_envA if s not in to_remove]
			if len(dist_rematch)>1:
				embed()
		while len(mindist_rematch)>0 and min(mindist_rematch)<1e6: #run as long as potential re-matches available
			idx_sprite = np.argmin(mindist_rematch) #first re-match sprite with minimum distance to potential partner
			idx_match = np.argmin(dist_rematch[idx_sprite]) #re-match to closest potential partner
			#print '>>> idx_sprite', idx_sprite
			#print '>>> idx_match', idx_match
			# Append (envA sprite, envB sprite, dist) tuple to matched sprites list
			try:
				matched_sprites.append( (lonely_sprites_envA[idx_sprite], lonely_sprites_envB[idx_match], min(mindist_rematch)) )
			except:
				print "idx_sprite / idx_match problem"
				embed()
			# Set distance out of matching range - for both sprite A and B
			dist_rematch[idx_sprite] = [2e6 for i in range(len(dist_rematch[0]))]
			for i in range(len(dist_rematch)):
				#print '>>> dist_rematch[i]', dist_rematch[i][idx_match]
				dist_rematch[i][idx_match]=2e6
			# Update minimum distance list
			mindist_rematch = [ min([d for d in dist_rematch[i]]) for i in range(len(dist_rematch)) ]
			# Update re-matching lists for both environments
			sprites_rematchA.append(lonely_sprites_envA[idx_sprite])
			sprites_rematchB.append(lonely_sprites_envB[idx_match])
		# Delete re-matched sprites from lonely lists
		for s in sprites_rematchA:
			lonely_sprites_envA.remove(s)
		for s in sprites_rematchB:
			lonely_sprites_envB.remove(s)

		# print "envA", lonely_sprites_envA
		# print envA.show()
		# print "envB", lonely_sprites_envB
		# print envB.show()
		# print ""
		# embed()
		return matched_sprites, lonely_sprites_envA, lonely_sprites_envB


	def neighborsPrev(self, envA, envPrev, sPrev):
		"""
		Function to find neighbors of target sprite in the previous time step
		envA: hypothetical environment, current step
		envPrev: real environment, previous step
		sPrev: target sprite in envPrev
		"""
		# Find potential interaction partners: neighboring sprites in previous step
		all_sprites = []
		for g in envPrev._game.sprite_groups.keys():
			all_sprites += envPrev._game.sprite_groups[g]
		# Neighbors of problematic sprite in real world in previous time step
		neighbors = [s for s in all_sprites if manhattanDist2(s, sPrev)<=np.sqrt(2) and s!=sPrev and (s not in envPrev._game.kill_list)]
		# Determine corresponding classes in theory environment
		neighbors_color = [s.colorName for s in neighbors]
		neighbors_color = list(set(neighbors_color))
		neighbors_theoClassNames = []
		for color in neighbors_color:
			for className in envA._game.sprite_groups.keys():
				if envA._game.sprite_groups[className]!=[] and  envA._game.sprite_groups[className][0].colorName==color:
					neighbors_theoClassNames.append(className)
		neighbors_theoClassNames = list(set(neighbors_theoClassNames)) #delete double entries
		return neighbors_theoClassNames


	def find_sPrev(self, sB, envB, envPrev):
		"""
		Find sprite in envPrev (previous environment) corresponding to a sprite in
		envB (current environment), and the distance that the sprite has traveled
		in the time step
		"""
		matched_ts, _, _ = self.matchEnvs(envB, envPrev) #matches real env across timestep
		dist_ts = [matched_ts[i][2] for i in range(len(matched_ts)) if matched_ts[i][0]==sB] #distance that sB has moved over timestep
		sPrev = [matched_ts[i][1] for i in range(len(matched_ts)) if matched_ts[i][0]==sB] #sB in previous step
		if sPrev == []:
			print "no sPrev"
			# embed()
			sPrev = None
			dist_ts = None
		else:
			sPrev = sPrev[0]
			dist_ts = dist_ts[0]
		return sPrev, dist_ts


	def diagnosePosMismatch(self, sA, sB, sPrev, envA, envB, envPrev, dist_ts):
		"""
		Returns errorMapEntry object containing the position mismatch error
		"""

		# Step through sub-problems
		e = errorMapEntry()
		e.targetToken = sB
		e.targetClass = sA.name

		errorMaps = [e]
		# Find neighbors of target sprite in the previous time step
		neighbors_prev = self.neighborsPrev(envA, envPrev, sPrev)



		# Write potential interaction pairs to error map entry
		for className in neighbors_prev:
			e.intPairs.append( (sA.name,className) )
		# Determine mininum distance to neighbors in current real env -> to distinguish unexpectedPosition and unexpectedOverlap
		all_sprites_envB = []
		for g in envB._game.sprite_groups.keys():
			all_sprites_envB += envB._game.sprite_groups[g]
		nearest_sprite = self.findNearestSprite(sB, [s for s in all_sprites_envB if (s!=sB) and (s not in envB._game.kill_list)])
		nearest_dist = manhattanDist2(sB, nearest_sprite)
		# Determine orientation in current and previous step -> to detect orientation change
		try:
			oB = sB.orientation
			oPrev = sPrev.orientation
		except:
			oB,oPrev = None,None

		# if sA.colorName=='PINK':
			# print "in diagnosePosMismatch"
			# embed()
		## Categorize into sub-problem-class
		# 1.1) noMovement
		if dist_ts == 0:
			e.diagnosis.append('noMovement')
			## Form all possible pairs of classes and propose these. This is because undoAll could cause this, so it's literally any classes combining.
			e.intPairs = list(itertools.combinations([k for k in envA._game.sprite_groups.keys() if envA._game.sprite_groups[k]],2))
			for k in envA._game.sprite_groups.keys():
				if len(envA._game.sprite_groups[k])>1:
					e.intPairs.append((k,k))
		# 1.2) orientationChange
		if dist_ts!=0 and oB!=None and oB!=oPrev:
			e.diagnosis.append('orientationChange')
		# 1.3) unexpectedPosition
		if dist_ts!=0 and nearest_dist>=1:
			e.diagnosis.append('unexpectedPosition')
		# 1.4) unexpectedOverlap
		if dist_ts!=0 and nearest_dist<1:

			e.diagnosis.append('unexpectedOverlap')
			# find sprite in envA that corresponds to covered sprite in envB
			color = nearest_sprite.colorName
			className_envA = ''
			for k in [key for key in envA._game.sprite_groups.keys() if envA._game.sprite_groups[key]]:
				if color == envA._game.sprite_groups[k][0].colorName:
					className_envA = k
			covered_sprite_envA = self.findNearestSprite(sB,envA._game.sprite_groups[className_envA])
			e.intPairs = [(sA.name, covered_sprite_envA.name)] #overwrite interaction pair by the overlapping sprite pair
		if dist_ts>2:
			e2 = errorMapEntry()
			e2.targetToken = e.targetToken
			e2.targetClass = e.targetClass
			e2.diagnosis.append('teleport')
			e2.intPairs = [(sA.name, n) for n in neighbors_prev]
			errorMaps.append(e2)
		# Return list of errorMapEntry objects
		return errorMaps


	## Function generating penalty and error map
	def errorSignal(self, envA, envB, theory, envPrev, p_dist=1, p_speed=1, p_miss=10, targetClass=None, penalty_only=False):
		"""
		envA: hypothetical environment
		envB: real environment
		theory: corresponds to hypothetical
		p_dist: distance penalty per grid point
		p_speed: pentalty for distances arising from wrong speed
		p_miss: penalty for missing or additional sprite
		penalty_only: return penalty, [] (empty list instead or errorMap)

		Calculates d_theory(envA, envB): distance between the states of the environments
		using the ontology of the supplied theory.

		Also returns errorMap, a dict that contains
		keys: (class1, class2). values: a diagnostic error signal
		"""

		# Initialization
		total_penalty = 0.
		errorMap = []

		# Match sprites in environments and get sprites that couldn't be matched
		matched_sprites, lonely_sprites_envA, lonely_sprites_envB = self.matchEnvs(envA, envB)
		# print "in errorSignal"
		# embed()
		if targetClass:
			try:
				matched_sprites = [m for m in matched_sprites if m[0].name==targetClass]
				if matched_sprites:
					targetColor = matched_sprites[0][0].colorName
					lonely_sprites_envA = [s for s in lonely_sprites_envA if s.name==targetClass]
					lonely_sprites_envB = [s for s in lonely_sprites_envB if s.colorName==targetColor]
				else:
					lonely_sprites_envA = []
					lonely_sprites_envB = []
			except:
				print "targetClass filter in errorSignal failed"
				embed()
		## Test output
		# print '>>> matched_sprites:'
		# for i in range(len(matched_sprites)):
			# if True: #matched_sprites[i][2]!=0:
				# print matched_sprites[i]
		# print '>>> lonely_sprites_envA:', [s for s in lonely_sprites_envA]
		# print '>>> lonely_sprites_envB:', [s for s in lonely_sprites_envB]

		## Penalize distance and additional/missing sprites
		# Distance penalty
		for t in matched_sprites:
			sA, sB = t[0], t[1] #sprites in envA, envB      
			dist = t[2] #distance to sprite in envB
			sA_type = theory.classes[sA.name][0].vgdlType
			d = 30. # grid spacing

			# If RandomNPC: compare sB position to where it could have been given the hypothetical speed and random direction
			if 'Random' in str(sA_type): # == "<class 'vgdl.ontology.RandomNPC'>":      
				try:
					sA_speed = theory.classes[sA.name][0].args['speed']
				except:
					sA_speed = theory.classes[sA.name][0].speed
				sPrev, dist_ts = self.find_sPrev(sB, envB, envPrev) #sA in previous environment
				if sPrev is None:
					print 'sPrev not found -> penalty unreliable'
					continue
					# embed()
				xB = sB.rect.left/d
				yB = sB.rect.top/d
				xPrev = sPrev.rect.left/d
				yPrev = sPrev.rect.top/d

				dist_rNPC = manhattanDist((xB,yB), (xPrev, yPrev))
				# dist_rNPC = [ manhattanDist( (xB,yB), (xPrev,yPrev) ), \
				#                    manhattanDist( (xB,yB), (xPrev+sA_speed,yPrev) ), \
				#                    manhattanDist( (xB,yB), (xPrev-sA_speed,yPrev) ), \
				#                    manhattanDist( (xB,yB), (xPrev,yPrev+sA_speed) ), \
				#                    manhattanDist( (xB,yB), (xPrev,yPrev-sA_speed) ), \
				#                  ]
				# mindist_rNPC = min(dist_rNPC)
				# total_penalty += p_speed*mindist_rNPC #penalize speed separately to discourage keeping around too many similar theories
				total_penalty += p_speed*min(dist,1.)
			elif 'Missile' in str(sA_type): # == "<class 'vgdl.ontology.Missile'>": 
				total_penalty += p_speed*t[2] #penalize speed separately to discourage keeping around too many similar theories
			elif 'Chaser' in str(sA_type):
				# print "found chaser"

				# if colorDict[str(sA.stype)]=='BLUE':
				#   print "found blue chaser"
				#   sPrev, _ = self.find_sPrev(sB, envB, envPrev)
				#   print "prev position:", sPrev.rect.left/30., sPrev.rect.top/30.
				#   embed()
				
				sPrev, _ = self.find_sPrev(sB, envB, envPrev)
				xA = sA.rect.left/d
				yA = sA.rect.top/d
				if sPrev is None:
					continue
				closestTargets = findChaserOptions(sA, sPrev, envPrev._game, fleeing=sA.fleeing)
				chaser_penalty = 0. if (xA,yA) in closestTargets else 2.

				total_penalty += p_speed*chaser_penalty
			# All of the other types are deterministic
			else:
				total_penalty += p_dist*t[2]    

		# Missing/additional/transformation penalty
		total_penalty += p_miss * ( len(lonely_sprites_envA) + len(lonely_sprites_envB) )

		if penalty_only:
			return total_penalty, []

		### Construct errorMap using previous state ###

		# 1) Position mismatch: Things have moved.

		# Case A: matched sprites have different positions from what predicted
		for t in matched_sprites:
			dist_envs = t[2] #distance between sprites in real and theory environments
			if dist_envs==0.: #sprites located where expected -> no conflict
				continue
			sA = t[0]
			sB = t[1]
			posCurr = envB._rect2pos(sB.rect) #current position of sprite
			# Find sprite corresponding to sB in previous time step
			sPrev, dist_ts = self.find_sPrev(sB, envB, envPrev)
			if sPrev==None:
				warnings.warn('sPrev not found in position mismatch error')
				continue
			# Determine errorMapEntry object for position mismatch problem
			errs = self.diagnosePosMismatch(sA, sB, sPrev, envA, envB, envPrev, dist_ts)
			errorMap.extend(errs)

		# Case B: Sprite moved in real environment, but we predicted a destruction
		# For this, we check if lonely envB sprite has match in envPrev (and pass to (2) if not)
		appeared_sprites_envB = []
		for sB in lonely_sprites_envB:
			# Find sprite corresponding to sB in previous time step
			sPrev, dist_ts = self.find_sPrev(sB, envB, envPrev)
			if sPrev == None: #sB has no match in envPrev
				appeared_sprites_envB.append(sB)
				continue 

			### Tim says if we're not finding anything in the kill list but did have sPrev, something is wrong.
			### As in, this should be a problem with matchEnvs and sPrev. Look at their outputs


			# Find erroneously destroyed sA by finding envA sprite closest to sPrev
			candidates_in_killList = [s for s in envA._game.kill_list if s.colorName==sPrev.colorName]
			
			## These are both double-checking things that should have been taken care of better
			## by the sprite matching. But since it's imperfect given our limited knowledge, we're
			## being more thorough.

			if candidates_in_killList==[]:
				if not sPrev: #there is no envA sprite where sPrev should have been
					print "empty killList in A, meaning the matching is wrong"
					## You need to figure out what to pass to diagnosePosMismatch for sA, since it
					## doesn't exist.
					embed()
					#appeared_sprites_envB.append(sB)
					continue
			else:
				sA = self.findNearestSprite(sPrev, candidates_in_killList)
				if manhattanDist2(sA, sPrev)>1 and not sPrev: #there is no envA sprite where sPrev should have been
					## if there was a kill event and an appearance event somewhere far, we should really see this as
					## an appearance
					## Really, you should look at sprite matching better.

					print "manhattanDist2 > 1"
					embed()
					appeared_sprites_envB.append(sB)
					continue
			# Now we are completely sure that sprite in envA has been erroneously removed
			errs = self.diagnosePosMismatch(sA, sB, sPrev, envA, envB, envPrev, dist_ts)
			errorMap.extend(errs)
	
		# 2) Unexpected destruction/appearance/transformation
		# 2.1) Transformation
		for iA,sA in enumerate(lonely_sprites_envA):
			for iB,sB in enumerate(appeared_sprites_envB):
				if manhattanDist2(sA, sB)<=2:
					#print "Embedded in transformation handling"
					#embed()
					e = errorMapEntry()
					e.diagnosis.append('transformation')
					e.targetToken = sA
					e.targetClass = sA.name
					# Find sprite corresponding to sB in previous time step
					color = sB.colorName
					sB.colorName = sA.colorName
					matched_ts, _, _ = self.matchEnvs(envB, envPrev) #matches real env across timestep
					sB.colorName = color
					sPrev = [matched_ts[i][1] for i in range(len(matched_ts)) if matched_ts[i][0]==sB]

					if sPrev==[]: #This was an appearance, pass to (2.3) below
						continue
					else: #This was indeed a transformation
						print "WARNING: Found unexpected transformation"
						sPrev = sPrev[0]
						# Find neighbors of target sprite in the previous time step
						neighbors_prev = self.neighborsPrev(envA, envPrev, sPrev)
						# Write potential interaction pairs to error map entry
						for className in neighbors_prev:
							e.intPairs.append( (theory.spriteObjects[sPrev.colorName].className,className) )
						errorMap.append(e)
						# Remove transformed-sprite-pair from respective lists
						lonely_sprites_envA.pop(iA)
						appeared_sprites_envB.pop(iB)
		# 2.2) Destruction
		for sA in lonely_sprites_envA: #sA should have been destroyed
			e = errorMapEntry()
			e.targetClass = sA.name
			candidates_in_killList = [s for s in envB._game.kill_list if s.colorName==sA.colorName]
			sB = self.findNearestSprite(sA, candidates_in_killList)
			if sB==None:
				print "WARNING: No target and interaction pair found in object destruction. You have not implemented this diagnosis."
				e.diagnosis.append('objectDidNotAppear')
				e.targetToken = None
				e.intPairs = []
				errorMap.append(e)
				continue
			else:
				e.diagnosis.append('objectDestruction')
				e.targetToken = sB
				# Find the sprite that was destroyed in envB from the kill_list
				# Find neighbors of target sprite in the previous time step
				sPrev = sB #sprite was destroyed but hasn't moved
			neighbors_prev = self.neighborsPrev(envA, envPrev, sPrev)
			neighbors_prev = [c for c in neighbors_prev if c!=sA.name]
			# Write potential interaction pairs to error map entry
			for className in neighbors_prev:
				e.intPairs.append( (sA.name,className) )
			errorMap.append(e)
		# 2.3) Appearance
		for sB in appeared_sprites_envB:
			print "WARNING: Found unexpected appearance"
			e = errorMapEntry()
			e.diagnosis.append('newObjectAppeared')
			e.targetToken = sB
			# Find class of new object by comparing colors, or give 'unknown' if unsuccessful
			color = sB.colorName
			all_sprites_envA = []
			for g in envA._game.sprite_groups.keys():
				all_sprites_envA += envA._game.sprite_groups[g]
			sMatch = [s for s in all_sprites_envA if s.colorName==color]
			if sMatch==[]:
				e.targetClass = 'unknown'
			else:
				e.targetClass = sMatch[0].name

			# Find neighbors of target sprite in the real environment (envB) in the current time step -> could have caused appearance
			# Simultaneously find culprit classes - an overlapping sprite could have launched the sprite due to its class
			neighbors_curr = self.neighborsPrev(envA, envB, sB) #use this function to find neighbors in current state and not previous ("Prev" label is unnecessary)
			nearestSprite = self.findNearestSprite(sB, [item for sublist in envA._game.sprite_groups.values() for item in sublist])
			if nearestSprite.name in neighbors_curr:
				e.intPairs.append((e.targetClass, nearestSprite.name))
				e.culpritClasses.append(nearestSprite.name)
			else:
				print "got new sprite class but nearest prev-step sprite isn't a current neighbor"
			# for className in neighbors_curr:
			# 	e.intPairs.append( (sA.name,className) )
			# 	# Culprit classes are given by the names of the potential interaction partners
			# 	e.culpritClasses.append(className)
			errorMap.append(e)


		# 3) State change
		# Call s.resources on all sprites in envA and envB. See which ones have changed
		# and if that is consistent between envA and envB
		#TODO

		## Clean errorMap: delete redundant interaction pairs under same diagnosis (only works if there is just one diagnosis per errorMapEntry)
		dia_list = [e.diagnosis[0] for e in errorMap]
		dia_list = list(set(dia_list))
		for dia in dia_list:
			errors = [e for e in errorMap if e.diagnosis[0]==dia]
			for n,e in enumerate(errors):
				other_pairs = []
				[other_pairs.extend(errorMap[i].intPairs) for i in range(n+1,len(errorMap)) ]
				# Permute tuples of other pairs to compare pairs in current error
				other_pairs = [(p[1],p[0]) for p in other_pairs]
				# Find unique interaction pairs for current error
				unique_pairs_e = []
				[unique_pairs_e.append(p) for p in e.intPairs if (p not in other_pairs)]
				# Set interaction pairs to unique pairs
				e.intPairs = unique_pairs_e

		## TODO: penalize randomNPCs more smartly - currently they're kind of a joker, obscuring push events

		## NOTE: We could extend by penalizing as a function of (most likely) vgdlType and color
		## NOTE: Use intializeHypotheses function in this file to build my test theories

		## Sort so that you fix errors involving any new classes first.
		errorMap = sorted(errorMap, key=lambda x: x.targetClass!='unknown')
		return total_penalty, errorMap


	def IDmatch(self, envA, envB):
		"""
		Returns: dictionary with entries -> sB ID: matched sA ID
		"""
		warning = False
		d = {}
		# Match environments by position and color
		matched_sprites, lonely_sprites_envA, lonely_sprites_envB = self.matchEnvs(envA, envB)
		# Warn if there are unmatched or not accurately matched sprites
		if len(lonely_sprites_envA)!=0 or len(lonely_sprites_envB)!=0:
			warning = True
			print "WARNING: Unmatched sprites in IDmatch -> truPenalty potentially flawed"
			## this is called only when you're setting two environments. So by definition, the environments should
			## be identical.
			# embed()
		if any( [m[2]!=0 for m in matched_sprites] ) == True:
			#print "WARNING: Non-zero distance between matched sprites (in IDmatch)"
			pass
		# Assign IDs
		for m in matched_sprites:
			sA, sB = m[0], m[1]
			d[sB.ID.urn] = sA.ID.urn
		return d, warning


	def truPenalty(self, envA, envB, IDmatch, p_dist=1, p_speed=.5, p_miss=10):
		penalty = 0
		# List all sprites and IDs in both environments
		all_sprites_envA = []
		all_sprites_envB = []
		all_IDs_envA = []
		all_IDs_envB = []
		for g in envA._game.sprite_groups.keys():
			all_sprites_envA.extend( envA._game.sprite_groups[g] )
		for g in envB._game.sprite_groups.keys():
			all_sprites_envB.extend( envB._game.sprite_groups[g] )
		if len(all_sprites_envA)!=len(all_sprites_envB):
			# At least one sprite has already been killed at beginning
			penalty += p_miss * abs( len(all_sprites_envA) - len(all_sprites_envB) )
			#print "WARNING: Different numbers of sprites in enviroments (in truPenalty)"
		all_IDs_envA = [s.ID.urn for s in all_sprites_envA]
		all_IDs_envB = [s.ID.urn for s in all_sprites_envB]
		# Re-match all sprites using IDmatch dict
		rematched_sprites = []
		for sB in all_sprites_envB:
			try:
				sA = [ s for s in all_sprites_envA if s.ID.urn==IDmatch[sB.ID.urn] ]
			except:
				# At least one sprite has already been killed at beginning - handled above
				continue
			if len(sA)!=1:
				print "WARNING: Unmatched sprites in (truPenalty)"
			else:
				sA = sA[0]
				rematched_sprites.append([sA, sB])
		# Step through all sprite pairs
		for sA, sB in rematched_sprites:
			# Check if one or both sprites have been killed and penalize mismatch (heavily)
			if sB in envB._game.kill_list:
				if sA in envA._game.kill_list:
					pass
				else:
					penalty += p_miss
			elif sA in envA._game.kill_list:
				penalty += p_miss
			# Penalize distance mismatch
			dist = manhattanDist2(sA, sB)
			penalty += dist*p_dist

			## TODO: punish randomNPCs only if they have ventured out of possible range

		#print ">>> in truPenalty"
		#embed()

		return penalty


	def setSpritePositions(self, rle, Vrle, hypothesis, useHypothesis=True):
		## Sets positions of objects in Vrle to what they were in the rle. Bypasses clunky VGDL level description.

		old_sprite_groups = Vrle._game.sprite_groups
		for k in old_sprite_groups.keys():
			if old_sprite_groups[k]:
				color = Vrle._game.sprite_groups[k][0].colorName
				matchingSpritesInRLE = getSpritesByColor(rle._game, color)
				for sprite in old_sprite_groups[k]:
					matchingSprite = self.findNearestSprite(sprite, matchingSpritesInRLE)
					if matchingSprite is None:
						continue
					sprite.rect = matchingSprite.rect
					sprite.lastmove = matchingSprite.lastmove
					if useHypothesis:
						if 'Missile' in str(hypothesis.classes[sprite.name][0].vgdlType) and self.best_params!=None:
							try:
								## Enforce consistency: inferred value for individual orientations has to be consistent with 
								# what we're saying the horizontal/vertical orientation is of the entire group.

								orientation = tuple(np.sign(np.array(self.rle._game.previousPositions[matchingSprite.ID]) - 
									np.array(self.rle._game.objectMemoryDict[matchingSprite.ID])))

								if orientation == (0,0):
									print "found 0,0 orientation. Using generic missile orientation:", sprite.orientation, sprite.speed, sprite.cooldown
									pass

								else:
									sprite.orientation = orientation

							except KeyError:
								print "Failed to get params for Missile in main_agent"
								# embed()
								pass
					# else:
						# print "setting sprite positions"
						# if hasattr(matchingSprite, 'orientation'):
							# sprite.orientation = matchingSprite.orientation
						# embed()
		return


	def initializeVrleProfiler(self, hypothesis=None, stateToSet=None):
		lp = LineProfiler()
		lp_wrapper = lp(self.initializeVrle)
		Vrle = lp_wrapper(hypothesis, stateToSet)
		lp.print_stats()
		return Vrle

	def initializeVrle(self, hypothesis=None, stateToSet=None, debug=False):
		if stateToSet is None:
			stateToSet = self.rle

		def writeTheoryToTxtProfiler(rle, theory, symbolDict, txtFile, goalLoc = None):
			lp = LineProfiler()
			lp_wrapper = lp(writeTheoryToTxt)
			theoryString, levelString, symbolDict = lp_wrapper(rle, theory, symbolDict, txtFile, goalLoc)
			lp.print_stats()
			return theoryString, levelString, symbolDict


		if hypothesis is not None:
			## World in agent's mind given 'hypothesis', including object goal
			gameString, levelString, symbolDict = writeTheoryToTxt(stateToSet, hypothesis, self.symbolDict,\
				 "./examples/gridphysics/theorytest.py", debug=debug)
			useHypothesis=False ## not dealing with inferring Missile orientation for now.
		else:
			gameString = self.gameString
			levelString = self.levelString
			useHypothesis=False

		try:
			Vrle = createMindEnv(gameString, levelString, output=False)
		except:
			print "in initializeVrle"
			embed()
		if len(Vrle._game.sprite_groups['avatar'])>1:
			print "Warning. In initializeVrle. Got more than one avatar"
			embed()
		
		## Initialize imaginary state to match real state.
		self.setSpritePositions(stateToSet, Vrle, hypothesis, useHypothesis=useHypothesis)

		## TODO: imaginary state should not match real state; it should match the inferred state of that particular object.
		avatar = Vrle._game.getAvatars()[0]
		# embed()
		matchingSprite = [s for s in getSpritesByColor(stateToSet._game, avatar.colorName) if s.rect==avatar.rect][0]
		# Vrle._game.getAvatars()[0].lastmove = ccopy(matchingSprite.lastmove)

		if any([k in str(hypothesis.spriteObjects[avatar.colorName]) for k in ['Oriented', 'Rotating']]):
			Vrle._game.getAvatars()[0].orientation = ccopy(matchingSprite.orientation)
		try:
			Vrle._game.getAvatars()[0].resources = ccopy(matchingSprite.resources)
			Vrle._game.getAvatars()[0].jumping = ccopy(matchingSprite.jumping)
			Vrle._game.getAvatars()[0].wait_step = ccopy(matchingSprite.wait_step)
			Vrle._game.getAvatars()[0].rope = ccopy(matchingSprite.rope)
			Vrle._game.getAvatars()[0].gravity = ccopy(matchingSprite.gravity)
			Vrle._game.getAvatars()[0].last_rope = ccopy(matchingSprite.last_rope)
			Vrle._game.getAvatars()[0].last_gravity = ccopy(matchingSprite.last_gravity)
			Vrle._game.getAvatars()[0].last_vy = ccopy(matchingSprite.last_vy)
			Vrle._game.getAvatars()[0].lastrect = ccopy(matchingSprite.lastrect)
			Vrle._game.getAvatars()[0].speed = ccopy(matchingSprite.speed)

		except (IndexError, AttributeError) as e:
			pass

		# Vrle.immovables, Vrle.killerObjects = immovables, killerObjects
		return Vrle


	def VrleInitPhaseProfiler(self, theories=[], stateToSet=None, flexible_goals=False):
		lp = LineProfiler()
		lp_wrapper = lp(self.VrleInitPhase)
		VRLEs = lp_wrapper(theories, stateToSet, flexible_goals)
		lp.print_stats()
		return VRLEs

	def VrleInitPhase(self, theories=[], stateToSet=None, flexible_goals=False):
		## Initialize multiple VRLEs, each corresponding to one hypothesis in theories
		## Set their state to that of the provided RLE
		VRLEs = []
		# print "in VrleInitPhase.", len(self.hypotheses), "hypotheses"
		# if len(self.hypotheses)>1:
		#   print "more than one hypothesis"

		if not theories:
			theories = self.hypotheses
		# else:
			# print "Initializing {} theories in VRLEInitPHase".format(len(theories))
		for hypothesis in theories:
			VRLEs.append(self.initializeVrle(hypothesis, stateToSet=stateToSet))

			# tempHypothesis = copy.deepcopy(hypothesis)
			# tmpFakeInteractionRules = copy.deepcopy(self.fakeInteractionRules)
			# tempHypothesis.interactionSet.extend(tmpFakeInteractionRules)
			# if not flexible_goals:
				# tempHypothesis.updateTerminations()
			# print "fake hypotheses"
			# if self.fakeInteractionRules:/
				# tempHypothesis.display()
			# VRLEs.append(self.initializeVrle(tempHypothesis, stateToSet=stateToSet))
		# print("wrote theory to text")


		return VRLEs

	#<< To build own theory: check comments below
	def initializeHypotheses(self, allObjects, learnSprites=True, learnAvatar=True, num_variants=0):
		if learnSprites:
			observe(self.rle, 0, self.bestSpriteTypeDict)
			## Sample from distribution but actually just set everything to default.
			spriteTypeHypothesis, exceptedObjects, _, self.best_params = sampleFromDistribution(self.rle._game, \
				self.rle._game.spriteDistribution, allObjects, self.rle._game.spriteUpdateDict, self.bestSpriteTypeDict, \
				oldSpriteSet=None, mode='default', learnAvatar=learnAvatar)
			self.rle._game.exceptedObjects = exceptedObjects
			gameObject = Game(spriteInductionResult=spriteTypeHypothesis)
			initialTheory = gameObject.buildGenericTheory(spriteTypeHypothesis)
			initialTheory.terminationSet = [r for r in initialTheory.terminationSet if r.ruleType=='SpriteCounterRule']
		else:
			gameObject = Game(self.gameString)
			initialTheory = gameObject.buildGenericTheory(spriteSample=False, vgdlSpriteParse = gameObject.vgdlSpriteParse)

		initialTheory.mostRecentEdit = 'none'

		self.symbolDict = generateSymbolDict(self.rle)

		if learnAvatar:
			## Instantiate a hypothesis that each singleton class might be the avatar
			self.hypotheses = []
			## Grab all singleton classes and instantiate hypotheses that they are the avatar.
			for color in self.symbolDict.keys():
				if len(getSpritesByColor(self.rle._game, color))==1:
					newTheory = copy.deepcopy(initialTheory)
					oldClassName = newTheory.spriteObjects[color].className
					del newTheory.classes[oldClassName]
					newTheory.spriteObjects[color].className = 'avatar'
					newTheory.spriteObjects[color].vgdlType = MovingAvatar
					newTheory.classes['avatar'] = [newTheory.spriteObjects[color]]

					for rule in newTheory.interactionSet:
						if rule.slot1==oldClassName:
							rule.slot1='avatar'
						if rule.slot2==oldClassName:
							rule.slot2='avatar'

					## Rename classes to ensure canonical ordering: c2, c3, ...
					if min([int(k[1:]) for k in newTheory.classes.keys() if 'c' in k])>2:
						for s in newTheory.spriteSet:
							if s.className is not None and 'c' in s.className:
								tmpClassName = s.className
								del newTheory.classes[tmpClassName]
								s.className = 'c'+str(int(s.className[1:])-1)
								newTheory.classes[s.className] = [s]
						for rule in newTheory.interactionSet:
							if 'c' in rule.slot1:
								rule.slot1 = 'c'+str(int(rule.slot1[1:])-1)
							if 'c' in rule.slot2:
								rule.slot2 = 'c'+str(int(rule.slot2[1:])-1)

					self.hypotheses.append(newTheory)
		else:
			self.hypotheses = [initialTheory]

		## For debugging purposes: generate variants of the theory
		## (as a stand-in for a more generic induction/elaboration process)
		predicate_options = ['nothing', 'stepBack', 'killSprite', 'bounceForward', 'undoAll', 'reverseDirection']
		for i in range(num_variants):
			spriteTypeHypothesis, exceptedObjects, _, self.best_params = sampleFromDistribution(self.rle._game, \
				self.rle._game.spriteDistribution, allObjects, self.rle._game.spriteUpdateDict, self.bestSpriteTypeDict, \
				oldSpriteSet=None, mode='random')
			gameObject = Game(spriteInductionResult=spriteTypeHypothesis)
			theory = gameObject.buildGenericTheory(spriteTypeHypothesis)
			for interactionRule in theory.interactionSet:
				if interactionRule.slot1 == 'avatar':
					interactionRule.interaction = random.choice(['nothing', 'stepBack', 'bounceForward', 'undoAll', 'reverseDirection'])
				else:
					interactionRule.interaction = random.choice(predicate_options)
				if interactionRule.slot2=='EOS' and interactionRule.slot1!='avatar':
					interactionRule.interaction = random.choice(['stepBack', 'reverseDirection', 'killSprite'])

			theory.terminationSet = [r for r in initialTheory.terminationSet if r.ruleType=='SpriteCounterRule']

			self.randomTheories.append(theory)


		return gameObject


	def expandTheoryProfiler(self, theory, errorList, envRealPrev, envRealCurrent):
		lp = LineProfiler()
		lp_wrapper = lp(self.expandTheory)
		newTheories = lp_wrapper(theory, errorList, envRealPrev, envRealCurrent)
		lp.print_stats()
		return newTheories

	# def expandTheories(self, theories, errorList, envRealPrev, envRealCurrent, prevAction):
	#   func = partial(self.expandTheory, errorList, envRealPrev, envRealCurrent, prevAction, theory)
	#   p = ThreadPool(processes=20)
	#   results = p.map(func, [[h] for h in hypotheses])
	#   p.close()
	#   p.join()

	def expandTheories(self, theories, errorList, envRealPrev, envRealCurrent, prevAction):
		# print "In expandTheories. errorList length: {}. Theories length {}".format(len(errorList), len(theories))
		# print [e.diagnosis for e in errorList]
		if len(errorList)==0:
			return theories
		if len(errorList)==1:

			## Skip this whole step if you've already made changes for this theory. Just pass it on and you'll
			## evaluate it on the whole dataset in the outer loop.
			if len(theories)==1 and any([errorList[0]==e for e in theories[0].errorMapHistory]):
				newTheories = [theories[0]]
				return newTheories

			print "In base case. Correcting error for {} for {} theories".format(errorList[0].targetClass, len(theories))
			# if len(theories)==1:
				# embed()
			newTheories = []
			for theory in theories:
				newTheories.extend(self.expandTheoryForOneErrorMap(errorList[0], envRealPrev, envRealCurrent, prevAction, theory))
			
			print "Now running experience replay on {} theories".format(len(newTheories))
			penalties, cumulative_penalties, _ = self.experienceReplay(newTheories, self.rleHistory[-2:], self.actionHistory[-1:], 
				method='all', targetClass = errorList[0].targetClass)

			scoreAndTheoryTuples = zip(penalties, newTheories)
			scoreAndTheoryTuples = sorted(scoreAndTheoryTuples, key=lambda x: x[0])
			scoresAndHypotheses = [(h[0],h[1]) for h in self.filterTheories(scoreAndTheoryTuples, percentile=0, max_num=None,
					proportionOfSpriteTheories=None)]

			newTheories = [s[1] for s in scoresAndHypotheses]

			# print "In expandTheory () base case. Produced {} new theories".format(len(newTheories))
			# for s in scoresAndHypotheses:
			#   print "error: {}".format(s[0])
			#   s[1].display()

		else:
			tmpTheories = self.expandTheories(theories, [errorList[0]], envRealPrev, envRealCurrent, prevAction)
			newTheories = self.expandTheories(tmpTheories, errorList[1:], envRealPrev, envRealCurrent, prevAction)
		# print "{} new theories".format(len(newTheories))
		return newTheories


	def expandTheoryForOneErrorMap(self, errorMap, envRealPrev, envRealCurrent, action, theory):

		## This fixes the problems generated by a single errorMap entry.

		## TODO:
		##modularize. one function should be able to fix the problems generated by one classPair
		## another calls that function on all classPairs        
		
		## For now, only take an errorSignal with one key.
		## TODO: Implement a loop that goes through all keys by:
		## proposing all theories (given the proposalMemory) for one key
		## filtering to get high-probability ones (or at least ones that reduce that error signal)

		## TODO: when you get an errorMap.culpritClass, this is where you propose
		## the kinds of things that explain shooting.

		from vgdl.theory_template import expandLine, expandSprites, proposePredicates
		n=1

		def expandLineProfiler(theory, errorMap, targetClassPair, 
						predicates, n, 
						resourceObservations, generic):
			lp = LineProfiler()
			lp_wrapper = lp(expandLine)
			classPair, theories, predicateGroups = lp_wrapper(theory, errorMap, targetClassPair, 
														predicates, n, 
														resourceObservations, generic)
			lp.print_stats()
			return classPair, theories, predicateGroups



		## TODO: write sample resourceObservations that correspond to the format
		## where you can make the argList just reference the appropriate predicate
		## or at least have proposeArgs modify it slightly.
		self.resourceObservations = {'speed': [0, 10],\
								'changeResource': [{'resource':'c2', 'value':1, 'limit':1}],\
								'changeScore':{'speed':1}}      

		## TODO: Get these from somewhere else
		globalObservations = {'physicsType':'continuousphysics'}

		## If we were about to make modifications we've made already, don't waste the time.
		if any([errorMap==e for e in theory.errorMapHistory]):
			newTheories = [theory]
			return newTheories

		newTheories = []

		## For debugging. Don't make children of the true theory.
		if hasattr(theory, 'trueTheory'):
			newTheories = [theory]
			return newTheories

		if errorMap.targetClass == 'unknown':
			## assign new class here so you can use it for both expandSprites() and expandLine()
			class_num = len([k for k in theory.classes.keys() if k!='EOS']) + 1
			errorMap.targetClass = 'c'+str(class_num)
			newPairs = []
			for num,pair in enumerate(errorMap.intPairs):
				newPair = tuple([p if p!='unknown' else errorMap.targetClass for p in list(pair)])
				newPairs.append(newPair)
			errorMap.intPairs = newPairs
			print "Got unknown targetclass for {}. Added generic sprite to spriteSet and interactionSet".format(errorMap.targetToken.colorName)
			theory.addSpriteToTheory(errorMap.targetClass, errorMap.targetToken.colorName)

			## now get overlapping/nearby classes and reassign the target class to the shooter/spawnpoint/etc. 
			## the next step will take care of not doing inference on these if we've done it already.
			## NOTE: errorMap takes a unique targe class, and there are cases where you might have multiple singleton neighbors.
			## For now you're taking just a random choice between those.
			neighbors = self.neighborsPrev(envRealCurrent, envRealCurrent, errorMap.targetToken)
			options = [item for sublist in [envRealCurrent._game.sprite_groups[k] for k in neighbors if len(envRealCurrent._game.sprite_groups[k])==1] for item in sublist]
			if len(options)>1:
				print "Warning: More than one singleton neighbor of a newly-spawned sprite. Randomly picking one as agent"
			print options
			overlapping_item = random.choice(options)
			# overlapping_item = [item for sublist in envRealCurrent._game.sprite_groups.values() for item in sublist if 
				# item.rect==errorMap.targetToken.rect and item.colorName!=errorMap.targetToken.colorName][0]
			errorMap.targetToken = overlapping_item
			errorMap.targetClass = theory.spriteObjects[overlapping_item.colorName].className

			## Redo induction for this type, even if you've done it before.
			if errorMap.targetClass in theory.expandedSprites:
				theory.expandedSprites.remove(errorMap.targetClass)
		
		## SpriteSet induction step
		if errorMap.targetClass not in theory.expandedSprites:
			className, theories = expandSprites(self.rle._game, theory, errorMap, 
				envRealPrev, envRealCurrent, self.bestSpriteTypeDict, action, percentile=20, max_num=30,
				resourceObservations=self.resourceObservations)
			newTheories.extend(theories)

		## InteractionSet induction step
		for targetClassPair in errorMap.intPairs:
			predicates = proposePredicates(errorMap.diagnosis, self.memory, self.proposalMemory, globalObservations)
			classPair, theories, predicateGroups = expandLine(theory, errorMap, targetClassPair, 
				predicates = predicates, n=n, 
				resourceObservations=self.resourceObservations, generic=True)
			newTheories.extend(theories)
			## TODO: think more about this; right now you're keeping around all the predicateGroups
			## that each theory proposes when you call expandLine on it, so you have mutliple copies
			## of the same predicateGroups.
			self.proposalMemory[targetClassPair].extend(predicateGroups)


		if not newTheories:
			newTheories = [theory]
			theory.errorMapHistory.append(errorMap)
			# print "got no new theories in expandTheoryForOneErrorMap"
			# embed()
		return newTheories

	def completeHypotheses(self, allObjects, first_time_playing_level):
		if first_time_playing_level:
			observe(self.rle, 15, self.bestSpriteTypeDict) ## observe many steps so that you're not completely clueless about object movements for the new level
		else:
			observe(self.rle, 15, self.bestSpriteTypeDict) ## observe a couple steps so that you're not completely clueless about object movements when you're restarting a level.
		
		## Make sure any objects that appeared while we were observing are reflected in allObjects
		for k,v in self.rle._game.getObjects().items():
			if k not in allObjects:
				allObjects[k] = v

		spriteTypeHypothesis, exceptedObjects, _, self.best_params= sampleFromDistribution(self.rle._game, self.rle._game.spriteDistribution, 
			allObjects, self.rle._game.spriteUpdateDict, self.bestSpriteTypeDict, self.hypotheses[0].spriteSet)
		gameObject = Game(spriteInductionResult=spriteTypeHypothesis)
		newHypotheses = []
		for hypothesis in self.hypotheses:
			newHypotheses.append(gameObject.addNewObjectsToTheory(hypothesis, spriteTypeHypothesis))
		self.hypotheses = newHypotheses

	def testCurriculum(self, level_game_pairs=None):
		if not level_game_pairs:
			level_game_pairs = importlib.import_module(self.gameFilename).level_game_pairs  
		
		for n_level, level_game in enumerate(level_game_pairs):

			print("Playing level {}".format(n_level))
			(self.gameString, self.levelString) = level_game

			gameObject = None

			for epoch in range(1):
				self.testEpisode(gameObject,epoch=epoch)
		return

	def playCurriculum(self, heatmap=False, level_game_pairs=None):
		""" Plays a game level until it wins, then moves to the next one until
		completion. """
		if not level_game_pairs:
			level_game_pairs = importlib.import_module(self.gameFilename).level_game_pairs
		episodes = []
		allEffectsEncountered = []
		shutil.rmtree("images/tmp")
		os.makedirs("images/tmp")
		j=0
		flexible_goals = False

		for n_level, level_game in enumerate(level_game_pairs):

			print("Playing level {}".format(n_level))
			(self.gameString, self.levelString) = level_game
			self.max_nodes = self.starting_max_nodes
			win = False
			gameObject = None
			i=0
			levelEffectsEncountered = []
			allStatesEncountered = []
			t1 = time.time()
			first_time_playing_level = True

			while not win:
				gameObject, win, score, steps, statesEncountered, effectsEncountered = self.playEpisode(gameObject, flexible_goals, win, first_time_playing_level)
				episodes.append((n_level, steps, win, score))
				allStatesEncountered.extend(statesEncountered)
				levelEffectsEncountered.append(effectsEncountered)
				VGDLParser.playGame(self.gameString, self.levelString, statesEncountered,
				persist_movie=True, make_images=True, make_movie=False, movie_dir="videos/"+self.gameFilename, padding=10)
				first_time_playing_level = False
				i += 1
				print "Finished in ", time.time() - t1
				# if i >=10:
					# break
			if heatmap:
				self.makeHeatmap(allStatesEncountered, '{}_{}_level{}_heatmap.pdf'.format(
					# self.gameFilename[self.gameFilename.find('expt'):],
					gvgname[gvgname.find('set_1/')+6:],
					self.modelType, n_level))

			allEffectsEncountered.append(levelEffectsEncountered)

			## Uncomment if you want to run flexible goals version.
			# j+=1
			# if j>0:
			#   flexible_goals=True

			if flexible_goals:
				## When you embed, you can manually input changes in theory. See flexible_goals.py for an example.
				print "in main_agent; playing with flexible_goals"
				embed()

		# self.makeMovie()


		output = {'modelType':self.modelType,
					# 'gameName': self.gameFilename[self.gameFilename.find('expt'):],
					'gameName': gvgname[gvgname.find('set_1/')+6:],
					'condition': 'normal',
					'episodes' : episodes}

		write_to_csv('pilotModelRuns_'+gvgname[gvgname.find('set_1/')+6:]+'.csv', output)
		self.makeMovie()

	def makeHeatmap(self, statesEncountered, filename):
		from vgdl.plotting import featurePlot
		import matplotlib.pyplot as plt
		from matplotlib.ticker import NullLocator
		import numpy as np

		states = [s['objects']['avatar'].keys()[0] for s in statesEncountered
				  if s['objects']['avatar'].keys()]
		width, height = self.rle._game.width, self.rle._game.height
		correction_factor = self.rle._game.screensize[0]/width
		corrected_states = [(s[0]/correction_factor, s[1]/correction_factor) for s in states]

		m = np.zeros((width, height))
		Xs, Ys = [],[]
		im = plt.imread('flexible_goals.png')
		implot = plt.imshow(im)
		w, h = implot.get_extent()[1], implot.get_extent()[2]
		block_size = w/width

		for s in corrected_states:
			x = s[0]
			y = s[1]
			m[x, y] += 1
			Xs.append(x*block_size+block_size/2.)
			Ys.append(y*block_size+block_size/2.)
		plt.scatter(x=Xs, y=Ys, alpha=.5, edgecolor='')
		# plt.imshow(m.T, cmap='viridis')
		plt.gca().set_axis_off()
		plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0,
			hspace = 0, wspace = 0)
		plt.margins(0, 0)
		plt.gca().xaxis.set_major_locator(NullLocator())
		plt.gca().yaxis.set_major_locator(NullLocator())
		plt.savefig(filename, bbox_inches='tight', pad_inches=0)
		plt.close()

	def makeSummaryPlot(self, allEffectsEncountered):
		import matplotlib.pyplot as plt
		import importlib

		mod = importlib('vgdl.colors')
		colors = [cl[0].color for cl in self.hypotheses[0].classes.values()]
		for color in colors:
			times_touched_per_level = []
			for level in allEffectsEncountered:
				times_touched = len([effect
					for attempt in level
					for effect in attempt
					if ((effect[1]==color and effect[2]=='DARKBLUE')
						or (effect[2]==color and effect[1]=='DARKBLUE'))])
				times_touched_per_level.append(times_touched)
			color_to_plot = [float(value)/255 for value in getattr(mod, color)]
			plt.plot(times_touched_per_level, color=color_to_plot)
		plt.show()


	def makeMovie(self):
		print "Creating Movie"
		movie_dir = "videos/"+self.gameFilename

		if not os.path.exists(movie_dir):
			print movie_dir, "didn't exist. making new dir"
			os.makedirs(movie_dir)
		round_index = len([d for d in os.listdir(movie_dir) if d != '.DS_Store'])
		video_dirname = movie_dir+"/round"+str(round_index)+".mp4"
		images_dir = "images/tmp/%09d.png"
		com = "ffmpeg -i " +images_dir+ " -pix_fmt yuv420p -filter:v 'setpts=4.0*PTS' "+ video_dirname
		command = "{}".format(com)
		subprocess.call(command, shell=True)
		# empty image directory
		shutil.rmtree("images/tmp")
		os.makedirs("images/tmp")
		return

	def playMultipleEpisodes(self, num_episodes):
		i=0
		gameObject = None
		wins, scores = [], []
		win = False
		while i<num_episodes:
			gameObject, win, score, statesEncountered, _ = self.playEpisode(gameObject, flexible_goals=False,first_time_playing_level=False)
			wins.append(win)
			scores.append(score)
			i+=1
		VGDLParser.playGame(self.gameString, self.levelString, self.statesEncountered, \
			persist_movie=True, make_images=True, make_movie=True, movie_dir="videos/"+self.gameFilename, padding=10)
		print "Won {} out of {} episodes.".format(sum(wins), i)


	def playEpisodeProfiler(self, gameObject, flexible_goals=False, first_time_playing_level=False):
		lp = LineProfiler()
		lp_wrapper = lp(self.playEpisode)
		gameObject, win, score, steps, statesEncountered, effectsEncountered = lp_wrapper(gameObject, flexible_goals, first_time_playing_level)
		lp.print_stats()
		return gameObject, win, score, steps, statesEncountered, effectsEncountered




	def testEpisode(self, gameObject, epoch=0):
		
		# ### For Game A ###
		# actions = \
		# [32, 32, 32, 32, K_RIGHT, 32, K_RIGHT, K_LEFT, 32, K_LEFT, K_LEFT, 32, K_UP, 32, \
		# K_UP, 32, K_DOWN, K_DOWN, 32, K_LEFT, K_LEFT, 32, K_LEFT, K_LEFT, 32, K_LEFT, 32, \
		# K_LEFT, K_UP, 32, K_UP, 32, K_DOWN, 32, 32, K_UP, 32, K_RIGHT, 32, K_DOWN, K_RIGHT, \
		# 32, K_RIGHT, K_RIGHT, 32, 32]
		
		### For Game B & C ###
		# actions = \
		# [32, 32, 32, 32, K_RIGHT, K_RIGHT, K_RIGHT, 32, K_RIGHT, K_RIGHT, 32, K_UP, 32, \
		# K_DOWN, K_RIGHT, 32, 32, K_UP, K_UP, 32, 32, K_LEFT, K_DOWN, K_LEFT, K_LEFT, K_LEFT, \
		# K_LEFT, K_LEFT, K_UP, K_RIGHT, K_RIGHT, K_RIGHT, K_RIGHT, K_LEFT, K_LEFT, 32]

		# ### For Game C
		# actions = \
		# [32, 32, 32, 32, K_RIGHT, K_RIGHT, 32, K_RIGHT, K_RIGHT, K_RIGHT, 32, K_RIGHT, K_UP, \
		# K_UP, 32, 32, K_LEFT, K_LEFT, K_LEFT, K_DOWN, K_DOWN, 32, 32]

		# actions = [0,0,0,0,0, K_RIGHT, K_RIGHT,0,0,0,0,0,0,0,0,0,0,0]
		# actions = [0,0,0,0,0,0,0,0,0,0,0]
		actions = [K_RIGHT, K_LEFT, K_LEFT]
		# actions = [K_RIGHT,K_UP,K_SPACE, 0, 0, 0]
		# actions = [K_SPACE, 0, K_SPACE]
		actions = [0, 0, 0, 0, 0, 0]
		
		self.initializeEnvironment()
		# embed()

		self.trueTheory = generateTheoryFromGame(self.rle)
		self.trueTheory.trueTheory = True
		print "initializing RLE. Epoch={}".format(epoch)
		num_cores = multiprocessing.cpu_count()
		print "num cores: {}".format(num_cores) 
		if num_cores<40:
			print "WARNING: running on < 40 cores."

		self.all_objects= self.rle._game.getObjects()

		if epoch==0:
			gameObject = self.initializeHypotheses(self.all_objects, learnSprites=True, learnAvatar=self.learnAvatar, num_variants=0)

		## Start storing encountered states.
		effectsEncountered = []
		statesEncountered = [self.rle._game.getFullState()]
		self.statesEncountered.append(self.rle._game.getFullState())
		envReal = self.fastcopy(self.rle)
		self.rleHistory.append(envReal)

		agentState = self.resourceManagement(pre_step=True)

		#OBJECT TRACKING
		resourceObservations = self.getObservations(agentState, self.rle, self.rle)

		#updates the distributions
		# self.distributions.updateDist(resourceObservations)

		# plt.ion() #allow for plot updating

		t1 = time.time()
		for num, action in enumerate(actions):
			print ">>> Step", num+1, "of", len(actions), "<<<"
			## initialize VRLEs
			theoryRLEs = self.VrleInitPhase()
			lastStep=False
			if num==len(actions)-1:
				lastStep=True
			t2 = time.time()
			hypotheses = self.executeStep(action, self.hypotheses, theoryRLEs, lastStep)
			print ""
			print "executed step in {} seconds".format(time.time()-t2)
			print ""
			self.hypotheses = hypotheses

			# ##Plot scores from random enviroment sampling
			# plt.close('all')
			# self.plotScores()
			# plt.pause(0.01)

		print "{} time-steps took {} seconds".format(len(actions), time.time()-t1)
		print ">>> Embedded at the end of testEpisode"
		embed()

		return


	def playEpisode(self, gameObject, flexible_goals=False, win=False, first_time_playing_level=False):

		## TODO: When you start using this function with the new induction,
		## Take out objectMemoryDict() stuff.

		## Initialize external environment
		self.initializeEnvironment()
		print "initializing RLE"
		steps = 0
		self.quits = 0
		self.longHorizonObservations = 0
		self.all_objects= self.rle._game.getObjects()
		ended, win = self.rle._isDone()
		annealing = 1
		## Start storing encountered states.
		effectsEncountered = []
		statesEncountered = [self.rle._game.getFullState()]
		self.statesEncountered.append(self.rle._game.getFullState())

		## Initialize memory of object positions
		self.rle._game.objectMemoryDict, self.rle._game.previousPositions = {}, {}
		for k, v in self.rle._game.all_objects.iteritems():
			self.rle._game.objectMemoryDict[k] = (int(self.rle._game.all_objects[k]['sprite'].rect.x), int(self.rle._game.all_objects[k]['sprite'].rect.y))
			self.rle._game.previousPositions[k] = (int(self.rle._game.all_objects[k]['sprite'].rect.x), int(self.rle._game.all_objects[k]['sprite'].rect.y))

		## initialize theory if necessary.
		if len(self.hypotheses) == 0:
			gameObject = self.initializeHypotheses(self.all_objects, learnSprites=True, learnAvatar=True, num_variants=0)
			print "initializing hypotheses"
		else:
			gameObject = self.completeHypotheses(self.all_objects, first_time_playing_level)
			print "had hypotheses -- completing them."
			# If theory is being carried over, falsify termination hypotheses
			# given new level state
			if not flexible_goals:
				[t.updateTerminations(rle=self.rle) for t in self.hypotheses]

		emptyPlans = 0
		while not ended:
			## initialize one or many VRLEs according to hypothesis-selection method
			theoryRLEs = self.VrleInitPhase(flexible_goals=flexible_goals)
			quitting = False

			p = WBP.WBP(theoryRLEs[0], self.gameFilename, theory=self.hypotheses[0], fakeInteractionRules = self.fakeInteractionRules,
				seen_limits = self.seen_limits, annealing=annealing, max_nodes=self.max_nodes, shortHorizon=self.shortHorizon,
				firstOrderHorizon=self.firstOrderHorizon)
			bestNode, gameStringArray, objectPositionsArray = p.BFS()
			
			if bestNode is not None:
				solution = p.solution
				gameString_array = p.gameString_array
				objectPositionsArray = objectPositionsArray[::-1]
			else:
				solution = []

			if solution and not p.quitting:
				print "============================================="
				print "got solution of length", len(solution)
				for i,g in enumerate(p.gameString_array):
					print colored(g, 'green')
					if i<len(bestNode.actionSeq):
						print keyPresses[bestNode.actionSeq[i]]
				print "============================================="

			if self.shortHorizon:
				if not solution:
					emptyPlans +=1
				else:
					emptyPlans = 0
			else:
				if (not solution) or p.quitting:
					if self.longHorizonObservations<self.longHorizonObservationLimit:
						print "Didn't get solution or decided to quit. Observing, then replanning."
						observe(self.rle, 0, self.bestSpriteTypeDict)
						solution = [] ## You may have gotten p.quitting but also a solution; make sure you don't try to act on that if the planner decided it wasn't worth it.
						self.longHorizonObservations += 1
					else:
						quitting = True

			if emptyPlans > self.emptyPlansLimit:
				observe(self.rle, 5, self.bestSpriteTypeDict)




















			
			actions = [K_RIGHT, K_RIGHT]
			if len(actions)==1:
				envRealPrev = copy.deepcopy(self.rle) #environment at step n-1; deepcopy is expensive
				envTheoPrev = copy.deepcopy(theoryRLEs[1])
				hypPrev = copy.deepcopy(self.hypotheses[1])
			
			for n,action in enumerate(actions):
				self.rle.step(action)

				newTheories = []
				for num, env in enumerate(theoryRLEs):
					env.step(action)

				if n==len(actions)-2:
					envRealPrev = copy.deepcopy(self.rle) #deepcopy is expensive
					envTheoPrev = copy.deepcopy(theoryRLEs[1])
					hypPrev = copy.deepcopy(self.hypotheses[1])

				# if n==len(actions)-3:
				#   hypPrevprev = copy.deepcopy(self.hypotheses[1])

			#TEST
			#theoryRLEs[1].step(K_LEFT)

			## Theory before previous step
			#print '--- Theory 1 world before previous step ---'
			#print hypPrevprev.display()

			## Actual world - previous step
			print '--- Actual world after previous step ---'
			print envRealPrev.show()

			## Theory world - previous step
			print '--- Theory 1 world after previous step ---'
			print envTheoPrev.show() 
			print hypPrev.display()

			## Actual world - current step
			print '--- Actual world after current step ---'
			print self.rle.show()

			## Theory world - current step
			for num, env in enumerate(theoryRLEs):
				## Tim: uncomment if you want to see the full theory corresponding to each env
				if num==1:
					print '--- Theory 1 world after current step ---'
					print env.show()
					self.hypotheses[num].display()  
					break

			## Tim: Can run the state-distance function here.
			for num, env in enumerate(theoryRLEs):
				if num==1:
					penalty, errorMap = self.errorSignal(env, self.rle, self.hypotheses[num], envRealPrev)
					break





















			if not quitting:
				for i, action in enumerate(solution):

					self.hypotheses[0].dryingPaint = set()

					print "before execute step"
					print self.rle._isDone()
					hypotheses, theory_change_flag, effects = self.executeStep(action, self.hypotheses, statesEncountered,
						run_induction = not flexible_goals)

					self.rle._game.nextPositions = {}
					for k, v in self.rle._game.all_objects.iteritems():
						self.rle._game.nextPositions[k] = (int(self.rle._game.all_objects[k]['sprite'].rect.x), int(self.rle._game.all_objects[k]['sprite'].rect.y))
						try:
							if self.rle._game.previousPositions[k] != self.rle._game.nextPositions[k]:
								self.rle._game.objectMemoryDict[k] = ccopy(self.rle._game.previousPositions[k])
						except KeyError:
							pass
					self.rle._game.previousPositions = ccopy(self.rle._game.nextPositions)


					# pinkID = [k for k in self.rle._game.all_objects.keys() if self.rle._game.all_objects[k]['features']['color']=='PINK'][0]
					# print "prev position", self.rle._game.previousPositions[pinkID]
					# print "memoryDict", self.rle._game.objectMemoryDict[pinkID]
					# print "curr position", self.rle._game.all_objects[pinkID]['sprite'].rect


					ID = [k for k in self.rle._game.all_objects.keys() if self.rle._game.all_objects[k]['sprite'].colorName=='BROWN']

					# for k,v in self.best_params.items():
						# print k,v

					# print "theory_change_flag", theory_change_flag
					# if theory_change_flag:

					effectsEncountered.extend(effects)
					steps +=1

					ended, win = self.rle._isDone()
					
					if theory_change_flag:
						self.hypotheses = hypotheses
						break

					if ended:
						break

					## Make sure you're far enough from unpredictable dangerous objects.

					# Check for disparities between plan and reality
					# (e.g. stochastic effects)
					# if self.rle._game.is_stochastic and i>self.regrounding:
					if (i+1)%self.regrounding==0:
					# if True:
						try:
							rlePositions = sorted([(int(item.rect.x), int(item.rect.y), item) for sublist in self.rle._game.sprite_groups.values() for item in sublist])
							hypPositions = sorted([(int(item.rect.x), int(item.rect.y), item) for sublist in objectPositionsArray[i+1]._game.sprite_groups.values() for item in sublist])
							rlePositionsTuples, hypPositionsTuples = [(p[0], p[1]) for p in rlePositions], [(p[0], p[1]) for p in hypPositions]

							killer_types = [inter.slot2 for inter in hypotheses[0].interactionSet if inter.slot1=='avatar' and inter.interaction in ['killSprite']]
							# print "killer types", killer_types
							regroundingFlag = False
							for objPos in hypPositions:
								if not regroundingFlag and (objPos[0], objPos[1]) not in rlePositionsTuples:
									# print "found object position difference", colored(objPos, 'white', 'on_magenta')
									# print 'regrounding because of', objPos[2].colorName, objPos[2], "position:", self.rle._rect2pos(objPos[2].rect)
									# try: 
										# print "orientation:", objPos[2].orientation
									# except AttributeError:
										# pass
									nearest = self.findNearestSprite(objPos[2], [h[2] for h in rlePositions])
									# print "Nearest sprite:", nearest.colorName, nearest, "position:", self.rle._rect2pos(nearest.rect)
									# try:
										# print "orientation:", nearest.orientation
									# except AttributeError:
										# pass
									# print ""
									# embed()
									if self.selective_regrounding:
										if ((objPos[2].name=='avatar') or
											(objPos[2].name in killer_types and manhattanDist(self.rle._rect2pos(objPos[2].rect), self.rle._rect2pos(self.rle._game.getAvatars()[0].rect)) < self.safeDistance)):

											# if objPos[2].name=='avatar':
												# embed()
											regroundingFlag = True
											# embed()
											break
									else:
										regroundingFlag = True
										break

							if regroundingFlag:
								print "regrounding"
								break
							# if tuple(rlePositions) != tuple(hypPositions):
							# # if any(np.where(list(gameString_array[i+1]))[0] !=
							# #        np.where(list(self.rle.show()))[0]):
							#   print 'regrounding'
							#   embed()
							#   # embed()
							#   break
						except:
							# Mismatch in gamestring lengths
							print ""
							print 'regrounding problem'
							embed()
							break

					if self.avoid_danger: ## this is just exercising caution when near random objects, irrespective of whether they kill us or not
						try:
							random_npc_colors = [self.hypotheses[0].classes[k][0].color for k in self.hypotheses[0].classes.keys() if self.hypotheses[0].classes[k] and 'Random' in str(self.hypotheses[0].classes[k][0].vgdlType)]
							random_npc_classes = [k for k in self.rle._game.sprite_groups.keys() if self.rle._game.sprite_groups[k] and self.rle._game.sprite_groups[k][0].colorName in random_npc_colors]
							random_npc_positions = []

							for c in random_npc_classes:
								for element in self.rle._game.sprite_groups[c]:
									if element not in self.rle._game.kill_list:
										random_npc_positions.append(self.rle._rect2pos(element.rect))

							avatar_positions = [self.rle._rect2pos(avatar.rect)
								for avatar in self.rle._game.getAvatars()]

							possiblePairList = [manhattanDist(avatar, random)
								for avatar in avatar_positions
								for random in random_npc_positions]

							if min(possiblePairList) <= self.safeDistance:
								print("Close to RandomNPC, regrounding")
								break

						except ValueError:
							# print("error in avoid_danger: is the avatar dead?")
							pass


				if self.shortHorizon:
					self.max_nodes *= self.max_nodes_annealing
			else:
				## You failed the game either because you made a mistake you couldn't recover from or because you timed out in your search.
				## Search more deeply next time.
				self.max_nodes *= self.max_nodes_annealing
				# self.updateMemory(self.rle)

				return gameObject, False, self.rle._game.score, steps, statesEncountered, effectsEncountered


			annealing *= self.annealingFactor
			ended, win = self.rle._isDone()
			# if ended and not win:
			#   print "lost game. embedding"
			#   embed()


		## Update global memory of updates
		# for k in game.spriteUpdateDict:
			# self.spriteUpdateDict[k] = game.spriteUpdateDict[k]

		score = self.rle._game.score
		# self.updateMemory(self.rle)

		output = "ended episode. Win={}                 ".format(win)
		if win:
			print colored('________________________________________________________________', 'white', 'on_green')
			print colored('________________________________________________________________', 'white', 'on_green')

			print colored(output, 'white', 'on_green')
			print colored('________________________________________________________________', 'white', 'on_green')
		else:
			print colored('________________________________________________________________', 'white', 'on_red')
			print colored(output, 'white', 'on_red')
			print colored('________________________________________________________________', 'white', 'on_red')
		return gameObject, win, score, steps, statesEncountered, effectsEncountered

	def matchEventToRuleByIDAndSpriteName(self, event, rule):
		# Check if the two objects involved in the
		# event are the same as those in the novelty
		# termination rule (invariant by order)
		hypSlot1 = self.hypotheses[0].spriteObjects[event[1]].className
		hypSlot2 = self.hypotheses[0].spriteObjects[event[2]].className
		if set([hypSlot1, hypSlot2]) == set([rule.slot1, rule.slot2]):
			if not rule.preconditions:
				return True
			else:
				if not all([p.check(self.rle.agentStatePrev) for p in list(rule.preconditions)]):
					return False
				else:
					return True
		else:
			return False

	def manageNewObjects(self, hypotheses, envRealPrev, action, learnAvatar=True):

		## Add newly-seen objects.
		current_objects = self.rle._game.getObjects()
		if learnAvatar:
			if any([current_objects[k]['sprite'].colorName not in [self.all_objects[key]['sprite'].colorName for key in self.all_objects.keys()] for k in current_objects.keys()]):
				for k in current_objects.keys():
					distributionInitSetup(self.rle._game, k)
					if k not in self.all_objects.keys():
						self.all_objects[k] = current_objects[k]
				spriteInduction(self.rle._game, step=1, bestSpriteTypeDict=self.bestSpriteTypeDict, action=action,
					oldSpriteSet=self.hypotheses[0].spriteSet, old_outcome=None, specificSpritesToUpdate=[], 
					percentile=10, max_num=20, allMovement=False)
				spriteInduction(self.rle._game, step=2, bestSpriteTypeDict=self.bestSpriteTypeDict, action=action,
					oldSpriteSet=self.hypotheses[0].spriteSet, old_outcome=None, specificSpritesToUpdate=[], 
					percentile=10, max_num=20, allMovement=False)

				# print "found new object"
				# embed()
		else:
			for k in current_objects.keys():
				colorName = current_objects[k]['sprite'].colorName
				if colorName not in [self.all_objects[key]['sprite'].colorName for key in self.all_objects.keys()]:
					self.all_objects[k] = current_objects[k]
					distributionInitSetup(self.rle._game, k)
					## prevent spriteInduction from trying to infer anything about newly-appeared sprites in this timestep.
					self.rle._game.ignoreList.append(k)
					self.new_objects[colorName] = 0

		return hypotheses




	def resourceManagement(self, pre_step=True, res=None):

		if pre_step:
			try:
				agentState = ccopy(self.rle._game.getAvatars()[0].resources)
			except IndexError:
				agentState = defaultdict(lambda: 0)
			try:
				agentState['speed'] = self.rle._game.getAvatars()[0].speed
			except AttributeError:
				agentState['speed'] = 0
			try:
				agentState['orientation'] = self.rle._game.getAvatars()[0].orientation
			except:
				agentState['orientation'] = (0,0)
		else:
			try:
				agentState = ccopy(self.rle._game.getAvatars()[0].resources)

				# for e in res['effectList']:
				# 	if 'changeResource' in e:
				# 		changes = e[3]
				# 		if changes['value'] < 0:
				# 			# ipdb.set_trace()
				# 			# undo one negative change to account for eventhandler ordering
				# 			agentState[changes['resource']] -= changes['value']
				# 			break
			# If agent is killed before we get agentState
			except (IndexError, AttributeError) as e:
				# agentState = defaultdict(lambda:0)
				print "error with post-step resourceManagement"
				embed()
				# ignored_negative_change = False
				# for e in res['effectList']:
				# 	if 'changeResource' in e:
				# 		changes = e[3]
				# 		if changes['value'] > 0 or ignored_negative_change:
				# 			agentState[changes['resource']] += changes['value']
				# 		else:
				# 			agentState[changes['resource']] += 0
				# 			ignored_negative_change = True
			try:
				agentState['speed'] = self.rle._game.getAvatars()[0].speed
			except AttributeError:
				agentState['speed'] = 0
			try:
				agentState['orientation'] = self.rle._game.getAvatars()[0].orientation
			except:
				agentState['orientation'] = (0,0)

		return agentState

	def getObservations(self, agentState, envReal, envRealPrev):
		
		##TODO: generalize. this might have to be theory-specific, since different theories 
		## might hypothesize different avatars
		
		#whether the avatar is still alive 
		avatar_is_dead = len(getSpritesByColor(envReal._game,'DARKBLUE'))==0

		#using the previous state, we predict where the objects are going to be
		self.predictions = {}
		for key in self.lastObjectState.keys():
			#predictions done a little differently for avatar
			if key == 'DARKBLUE' and not avatar_is_dead:
				#predicting avatar location needs to be done properly
				try:
					speed = agentState['speed']
					orientation = self.lastObjectState[key][0]['orientation']
					pos = self.lastObjectState[key][0]['position']
					expected_pos = [pos[0] + orientation[0]*speed, pos[1] + orientation[1]*speed]
					positions = [expected_pos]
				except:
					print "in getObservations try/except"
					embed()
					pass
			else:
				positions = []
				for i in self.lastObjectState[key]:
					speed = i['speed']
					orientation = i['orientation']
					pos = i['position']
					if speed == None:
						expected_pos = pos
					else:
						expected_pos = [pos[0] + orientation[0]*speed, pos[1] + orientation[1]*speed]
					positions.append(expected_pos)
			self.predictions[key] = positions
		
		## TODO: This doesn't look like it's rolling forward all predictions at the same time
		## and using that to make a prediction. What you need is a theory-based prediction (as in, a step forward)
		## in the simulator, and then knowledge about the intersections given each theory.

		#get list of possible objects which could have collided with avatar
		candidates = []
		locs = {}
		current_state = self.getStateByColor(envRealPrev)

		if len(current_state['DARKBLUE']) > 0:
			avatar = current_state['DARKBLUE'][0]['position']
		elif 'DARKBLUE' in self.predictions.keys():
			avatar = self.predictions['DARKBLUE'][0]
		for key in self.predictions.keys():
			if key is not 'DARKBLUE':
				for i in self.predictions[key]:
					#see what objects intersected with our avatar
					if self.intersect(i,avatar):
						candidates.append(key)
						locs[key] = i
						break
		print 'CANDIDATES'
		print candidates

		#build our dictionary of observations
		resourceObservations = {'speed':{},'resource':defaultdict(lambda:{})}

		#two cases - whether this collision killed the avatar or not
		if avatar_is_dead:
			for sprite in candidates:
				resourceObservations['speed'][sprite] = (None,agentState['speed']) # <--- Why are we switching order here and in the line 3 below?
		else:
			for sprite in candidates:
				resourceObservations['speed'][sprite] = (agentState['speed'],None)
		
		for key in agentState.keys():
			if key not in ['orientation','speed']:
				self.observed_resources.add(key)
		
		THRESHHOLD = 0.5*self.rle._game.block_size
		for sprite in candidates:
			#we must determine if the sprite has dissapeared
			sprite_gone = True
			if len(current_state[sprite]) == len(self.lastObjectState[sprite]):
				sprite_gone = False
			else:
				#match closest sprite
				#locs[sprite] is where we expect the sprite to be
				for i in current_state[sprite]:
					pos = i['position']
					if abs(pos[0] - locs[sprite][0]) + abs(pos[1] - locs[sprite][1]) < THRESHHOLD:
						resourceObservations['resource'][sprite] = {}
			for res in self.observed_resources:
				val = agentState[res]
				#return whether this collision killed the sprite or the avatar - this format is used when updating distributions
				resourceObservations['resource'][sprite][res] = (val, not avatar_is_dead, not sprite_gone)

		_, new_sprites, _ = self.matchEnvs(envReal, envRealPrev)
		new_sprites = [(s.colorName, s.rect.left, s.rect.top) for s in new_sprites]
		self.lastObjectState = current_state
		return resourceObservations, new_sprites

	def intersect(self, p1, p2):
		return (abs(p1[0] - p2[0]) <= self.rle._game.block_size and abs(p1[1] - p2[1]) <= self.rle._game.block_size)
	
	def filterTheories(self, scoreAndTheoryTuples, percentile, max_num, proportionOfSpriteTheories):
		## Returns the max_num theories that are at percentile or greater, given their score.

		scoreAndTheoryTuples = sorted(scoreAndTheoryTuples, key=lambda x: x[0])
		cutoff = np.percentile([s[0] for s in scoreAndTheoryTuples], percentile)
		candidates = [s for s in scoreAndTheoryTuples if s[0]<=cutoff]

		if max_num is None:
			max_num = len(candidates)+1
		if proportionOfSpriteTheories is None:
			candidates = sorted(candidates, key=lambda x:x[0])
			return candidates[0:max_num]

		sprite_candidates = [s for s in candidates if s[1].mostRecentEdit=='spriteInduction']
		induction_candidates = [s for s in candidates if s[1].mostRecentEdit=='interactionSetInduction']
		no_edit_candidates = [s for s in candidates if s[1].mostRecentEdit=='none']
		if len(sprite_candidates)>int(math.floor(max_num*proportionOfSpriteTheories)):
			num_sprite_candidates_chosen = min(int(math.floor(max_num*proportionOfSpriteTheories)), len(sprite_candidates))
			filtered = sprite_candidates[0:num_sprite_candidates_chosen]
		else:
			num_sprite_candidates_chosen = len(sprite_candidates)
			filtered = sprite_candidates

		remaining = max_num - len(filtered)
		filtered = induction_candidates[0:min(remaining, len(induction_candidates))] + filtered + no_edit_candidates

		if len(filtered)<max_num:
			diff = max_num - len(filtered)
			filtered = filtered + sprite_candidates[num_sprite_candidates_chosen:min(len(sprite_candidates), num_sprite_candidates_chosen+diff)]
		filtered = sorted(filtered, key=lambda x: x[0])

		return filtered

	def fastcopy(self, rle):

		newRle = self.initializeRLEFromGame()
		newRle._obstypes = ccopy(rle._obstypes)
 		if hasattr(rle, '_gravepoints'):
			newRle._gravepoints = ccopy(rle._gravepoints)
		newRle._game.sprite_groups = ccopy(rle._game.sprite_groups)
		newRle._game.kill_list = ccopy(rle._game.kill_list)
		newRle._game.lastcollisions = ccopy(rle._game.lastcollisions)
		newRle._game.time = ccopy(rle._game.time)
		newRle._game.score = ccopy(rle._game.score)
		newRle._game.keystate = ccopy(rle._game.keystate)
		newRle.symbolDict = ccopy(rle.symbolDict)
		newRle._game.getAvatars()[0].resources = ccopy(rle._game.getAvatars()[0].resources)
		return newRle

	def executeStepProfiler(self, action, hypotheses, theoryRLEs, lastStep=False):
		lp = LineProfiler()
		lp_wrapper = lp(self.executeStep)
		hypotheses = lp_wrapper(action, hypotheses, theoryRLEs, lastStep)
		lp.print_stats()
		return hypotheses

	def testAndExpand(self, theoryRLEs, hypotheses, action, envRealPrev, index):
		num = index
		env = theoryRLEs[num]
		hypothesis = hypotheses[num]
		env_sprites = [s for k in env._game.sprite_groups.keys() for s in env._game.sprite_groups[k] if s not in env._game.kill_list]
		env_colors = set([s.colorName for s in env_sprites if s])

		env.step(action)
		env_sprites = [s for k in env._game.sprite_groups.keys() for s in env._game.sprite_groups[k] if s not in env._game.kill_list]
		env_colors = set([s.colorName for s in env_sprites if s])

		penalty, errorList = self.errorSignal(env, self.rle, hypothesis, envRealPrev)
		
		# if errorList:
		#   hypothesis.display()
		#   for e in errorList:
		#       e.display()
		#   print ""
		#   embed()
		# else:
		# 	print "No error"
			# embed()
		# print "expanding theories"
		theories = self.expandTheories([hypothesis], errorList, envRealPrev, self.rle, action)
		return theories

	def executeStep(self, action, hypotheses, theoryRLEs, lastStep=False):

		theory_change_flag = False

		t1=time.time()
		spriteInduction(self.rle._game, step=1, bestSpriteTypeDict=self.bestSpriteTypeDict, action=action,
			oldSpriteSet=hypotheses[0].spriteSet, old_outcome=None, specificSpritesToUpdate=[], 
			percentile=10, max_num=20, allMovement=False)
		spriteInduction(self.rle._game, step=2, bestSpriteTypeDict=self.bestSpriteTypeDict, action=action,
			oldSpriteSet=hypotheses[0].spriteSet, old_outcome=None, specificSpritesToUpdate=[], 
			percentile=10, max_num=20, allMovement=False)
		print "spriteInduction prep took {} seconds".format(time.time()-t1)

		agentStatePrev = self.resourceManagement(pre_step=True)
		envRealPrev = self.fastcopy(self.rle)
		self.actionHistory.append(action)
		self.rle.step(action)
		agentState = self.resourceManagement(pre_step=False)
		envReal = self.fastcopy(self.rle)


		hypotheses = self.manageNewObjects(hypotheses, envRealPrev, action, learnAvatar=self.learnAvatar)


		self.rleHistory.append(envReal)
		
		#OBJECT TRACKING
		resourceObservations, new_sprites = self.getObservations(agentState, envReal, envRealPrev)
		print resourceObservations
		# print "got resource observations"
		# embed()
		self.rle._game.sprite_appearances = new_sprites
		print "new sprites", new_sprites
		#updates the distributions
		# self.distributions.updateDist(resourceObservations)
		# print self.distributions.distr
		# print "updated distributions. You'll have to access this when you expand theories."

		print ""
		print keyPresses[action]

		# agentState = self.resourceManagement(pre_step=False, res)
		# self.rle.agentStatePrev = agentState
		## Evaluate each theory on this step
		## Propose new theories
		# flag=False
		print "evaluating {} old theories and proposing new ones".format(len(theoryRLEs))
		newTheories = []

		prev_real_sprites = [s for k in envRealPrev._game.sprite_groups.keys() for s in envRealPrev._game.sprite_groups[k] if s not in envRealPrev._game.kill_list]
		prev_real_colors = set([s.colorName for s in prev_real_sprites if s])

		real_sprites = [s for k in self.rle._game.sprite_groups.keys() for s in self.rle._game.sprite_groups[k] if s not in self.rle._game.kill_list]
		real_colors = set([s.colorName for s in real_sprites if s])

		## DEBUG code. delete soon
		# if len(self.rleHistory)<3:
		#   for i in range(20):
		#       self.rleHistory.append(ccopy(self.rleHistory[0]))
		#       self.actionHistory.append(0)
	
		## Original version
		# t1 = time.time()
		# for num, env in enumerate(theoryRLEs):
		#   env_sprites = [s for k in env._game.sprite_groups.keys() for s in env._game.sprite_groups[k] if s not in env._game.kill_list]
		#   env_colors = set([s.colorName for s in env_sprites if s])

		#   env.step(action)
		#   env_sprites = [s for k in env._game.sprite_groups.keys() for s in env._game.sprite_groups[k] if s not in env._game.kill_list]
		#   env_colors = set([s.colorName for s in env_sprites if s])

		#   penalty, errorList = self.errorSignal(env, self.rle, self.hypotheses[num], envRealPrev)
			
		#   # print "theory {} had {} errors".format(num, len(errorList))
		#   # if errorList:
		#   #   self.hypotheses[num].display()
		#   #   for e in errorList:
		#   #       e.display()
		#   #   print ""
		#   # print "expanding theories"
		#   theories = self.expandTheories([self.hypotheses[num]], errorList, envRealPrev, self.rle, action)

		#   # if errorList:
		#   #   print "theory {} produced {} compound children".format(num, len(theories))
		#   #   print ""

		#   newTheories.extend(theories)
		# print "Normal version tested and expanded {} theories in {} seconds".format(len(theoryRLEs), time.time()-t1)

		## Serial compact version
		# t1 = time.time()
		for num, env in enumerate(theoryRLEs):
			theories = self.testAndExpand(theoryRLEs, self.hypotheses, action, envRealPrev, num)
			newTheories.extend(theories)
		# print "Serially tested and expanded {} theories in {} seconds".format(len(theoryRLEs), time.time()-t1)

		## Parallel version
		# t1 = time.time()
		# func = partial(self.testAndExpand, theoryRLEs, self.hypotheses, action, envRealPrev)
		# p = ThreadPool(processes=40)
		# results = p.map(func, range(len(theoryRLEs)))
		# newTheories = [item for sublist in results for item in sublist]
		# p.close()
		# p.join()
		# print "Parallel tested and expanded {} theories in {} seconds".format(len(theoryRLEs), time.time()-t1)

		self.allTheories.extend(newTheories)
		print self.rle.show(color='blue')
		print "evaluation complete. Now running experienceReplay on {} theories".format(len(newTheories))

		if newTheories:

			## DEBUG: remove soon!
			# if len(newTheories)>20:
			#   print "DEBUG change. Filtering theories 0:20"
			#   newTheories = newTheories[0:20]

			penalties, cumulative_penalties, experienceReplayRLEs = self.experienceReplay([self.trueTheory]+newTheories, self.rleHistory, self.actionHistory,
				method='all', displayTheories=False)

			# penalties, cumulative_penalties, experienceReplayRLEs = self.experienceReplay((newTheories, self.rleHistory, self.actionHistory, 'all', None, False))
			# for t in newTheories:
				# r = threading.Thread(target=self.experienceReplay, args=(([t], self.rleHistory, self.actionHistory, 'all', None, False ),))
				# r.start()

			# p = pp.ProcessPool(processes=8)
			# output = p.map(self.experienceReplay, [([t], self.rleHistory, self.actionHistory, 'all', None, False) for t in newTheories])
			# p.close()
			# p.join()
			# map(self.experienceReplay, [([t], self.rleHistory, self.actionHistory, 'all', None, False) for t in newTheories[0:5]])
			# print "ended in {} seconds".format(time.time()-t1)
			# embed()

			scoreAndTheoryTuples = zip(penalties, [self.trueTheory]+newTheories, experienceReplayRLEs)

			# scoreAndTheoryTuples = zip(penalties, newTheories, experienceReplayRLEs)
			scoreAndTheoryTuples = sorted(scoreAndTheoryTuples, key=lambda x: x[0])

			for num, sh in enumerate(scoreAndTheoryTuples):
				print "Theory: {} | Error: {}".format(num, sh[0])
				sh[1].display()
			print ""

			scoreAndTheoryTuples = [s for s in scoreAndTheoryTuples if not hasattr(s[1],'trueTheory')]      

			if not lastStep:
				scoresAndHypotheses = [(h[0],h[1]) for h in self.filterTheories(scoreAndTheoryTuples, percentile=80, max_num=30,
					proportionOfSpriteTheories=None)]
			else:
				scoresAndHypotheses = [(h[0],h[1]) for h in self.filterTheories(scoreAndTheoryTuples, percentile=80, max_num=30,
					proportionOfSpriteTheories=None)]

			print "Experience replay complete."
			for num, sh in enumerate(scoresAndHypotheses):
				print "Theory: {} | Error: {}".format(num, sh[0])
			print ""
			hypotheses = [sh[1] for sh in scoresAndHypotheses]
			print "{} survived".format(len(hypotheses))
			print ""

			if len(hypotheses)==0:
				print "0 hypotheses survived filter"
				embed()
		else:
			print "Got no new theories"

		### Store one-step penalties ###
		# Update mean error history
		# self.meanErrorHistory.append( [np.mean(hypotheses[i].errorHistory) for i in range(len(hypotheses))] )
		# Update minimum step error
		# self.minStepError.append( hypotheses[0].errorHistory[-1] )

		# ### Store sampled scores ###
		# num_samples=20
		# # Random game instances for scoring
		# rle = self.initializeRLEFromGame()
		# rrle = []
		# for sample in range(num_samples):
		#   rrle.append(self.randomizeState(rle))
		# # Theory scores on sampled game instances
		# tt = time.time()
		# print ">>> Theory scores"
		# scoreR = self.testHypotheses(hypotheses, rrle=rrle, num_samples=num_samples, actions_per_sample=20, last_only=True)
		# self.theoryScoreHistory.append(scoreR)
		# # Benchmark: Mean scores of random theories on sampled game instances
		# print ">>> Benchmark scores"
		# scoreB = self.testHypotheses(self.randomTheories, rrle=rrle, num_samples=num_samples, actions_per_sample=20, last_only=True)
		# self.benchmarkHistory.append(scoreB)
		# # Test output
		# print ">>> TIME", time.time()-tt
		# print "Theory scores on sampled game instances:"
		# print [scoreR[i][0] for i in range(len(scoreR))]

		# print ">>> Embedded at end of executeStep"
		# embed()

		self.statesEncountered.append(self.rle._game.getFullState())
		self.rle._game.sprite_appearances = []
		return hypotheses


	def planWithTheory(self, rle, theory):

		## First you have to pretend the theory has learned the rule corresponding to the goal; otherwise
		## this is ill-posed.
		## Add real goal to terminationSet
		terminationRule = SpriteCounterRule('c4', 0, True)
		theory.terminationSet.append(terminationRule)
		for rule in theory.interactionSet:
			if rule.slot1=='c4' and rule.slot2=='avatar':
				rule.interaction = 'killSprite'
		## add killSprite rule to terminationSet

		p = WBP(rle, self.gameFilename, theory=theory, fakeInteractionRules = [],
			seen_limits = self.seen_limits, annealing=1, max_nodes=500, shortHorizon=False,
			firstOrderHorizon=self.firstOrderHorizon)
		bestNode, gameStringArray, objectPositionsArray = p.BFS()
		embed()
		return

	########################################################################
	######## TESTING HYPOTHESES BY RANDOM SAMPLING OR OTHER METHODS ########
	########################################################################

	def subSampleStates(self, rleHistory):
		## Returns a random subsample of inidces in the rleHistory to test,
		## as well as how many actions per index to test

		## Note to self: it may happen that you sample: 
		## indices = [0,2,10], actionsPerIndex=5, 
		## in which case you'll double-penalize states 2,3,4.

		numStatesToSample = int(math.ceil(self.subsamplePercentage*len(rleHistory)))
		indices = list(np.random.choice(len(rleHistory)-1, numStatesToSample, replace=False))
		actionsPerIndex = self.actionsPerIndex

		return indices, actionsPerIndex

	def getSalientStates(self, rleHistory):
		## make sure you don't sample the last state
		## get actionsPerIndex

		pass

	def experienceReplayProfiler(self, hypotheses, rleHistory, actionHistory, method='all', displayStates=False):
		lp = LineProfiler()
		lp_wrapper = lp(self.experienceReplay)
		mean_penalties, cumulative_penalties = lp_wrapper(hypotheses, rleHistory, actionHistory, method, displayStates)
		lp.print_stats()
		return mean_penalties, cumulative_penalties


	def experienceReplay(self, hypotheses, rleHistory, actionHistory, method='all', targetClass=None, displayStates=False, displayTheories=False):
		# print "Running experience replay on {} theories and {} time-steps".format(len(hypotheses), len(rleHistory))
		t1 = time.time()
		results = []
		for num, h in enumerate(hypotheses):
			if displayTheories:
				print "running experienceReplay on {}:".format(num)
				h.display()
			results.append(self.singleTheoryExperienceReplay(rleHistory, actionHistory, method, targetClass, displayStates, [h]))
		print "Serial experienceReplay for {} hypotheses and {} time-steps took {} seconds".format(len(hypotheses), len(rleHistory), time.time()-t1)
		# embed()
		# t1 = time.time()
		# res = [0]*len(hypotheses)
		# for num, h in enumerate(hypotheses):
		#   r = threading.Thread(target=self.singleTheoryExperienceReplay, args=(self.rleHistory, self.actionHistory, 'all',
		#   None, False, [h], num, res))
		#   r.start()
		# print "Threaded experienceReplay for {} hypotheses took {} seconds".format(len(hypotheses), time.time()-t1)

		# t1 = time.time()
		# func = partial(self.singleTheoryExperienceReplay, rleHistory, actionHistory, method, targetClass, displayStates)
		# p = ThreadPool(processes=48)
		# results = p.map(func, [[h] for h in hypotheses])
		# p.close()
		# p.join()

		mean_penalties = [r[0][0] for r in results]
		cumulative_penalties = [r[1][0][0] for r in results]
		theoryRLEs = [r[2][0] for r in results]

		# print "Parallel experience replay on {} hypotheses took {} seconds".format(len(hypotheses),time.time()-t1)

		# print "ran experience replay on {} theories and {} time-steps in {} seconds".format(len(hypotheses), len(rleHistory), time.time()-t1)
		return mean_penalties, cumulative_penalties, theoryRLEs

	def singleTheoryExperienceReplay(self, rleHistory, actionHistory, method, targetClass, displayStates, hypotheses):
	# def singleTheoryExperienceReplay(self, args):
	# def experienceReplay(self, args):
		# rleHistory, actionHistory, method, targetClass, displayStates, hypotheses = args[0], args[1], args[2], args[3], args[4], args[5]
		import numpy as np

		if method=='all':
			indices = [0]
			actionsPerIndex = len(actionHistory)
		elif method=='screenLastStep':# and len(rleHistory)>=2:
			## Can't screen last step with fewer than two RLEs in history.
			if len(rleHistory)<2:
				actionsPerIndex = 0
				indices = [0]
				print "got screenLastStep on short sequence"
			else:
				indices = [-2]
				actionsPerIndex = 1
		elif method=='subsample':
			indices, actionsPerIndex = self.subSampleStates(rleHistory)
		elif method=='salient':
			indices, actionsPerIndex = self.getSalientStates(rleHistory)

		cumulative_penalties = []

		for idx in indices:
			## 1. set imagined states to historical states  2. match IDs between real and theory RLEs
			t1 = time.time()
			theoryRLEs = self.VrleInitPhase(hypotheses, rleHistory[idx]) 
			# ID_dictlist = []
			# for tR in theoryRLEs:
			# 	match, warning = self.IDmatch(tR, rleHistory[idx])
			# 	if warning:
			# 		print "ID match gave a warning. Environments should have all same objects but they don't."
			# 		embed()
				# ID_dictlist.append( match ) 

			## Take a predetermined number of actions starting from idx
			end = min(idx+actionsPerIndex, len(actionHistory))

			if displayStates:
				print "index: {}".format(idx)
				print rleHistory[idx].show()
				for env in theoryRLEs:
					print env.show(color='blue')

			for n, action in enumerate(actionHistory[idx:end]):
				penalties = []
				if displayStates:
					print action
					print rleHistory[idx+n+1].show(color='green')
				for num, env in enumerate(theoryRLEs):                      

					# if 'Chaser' in str(hypotheses[num].spriteObjects['YELLOW'].vgdlType):
					#   print hypotheses[num].spriteObjects['YELLOW'].args
					#   print "action num", n
					#   # print "penalty", penalty
					#   print "true pos", rleHistory[idx+n]._rect2pos(rleHistory[idx+n]._game.sprite_groups['dough'][0].rect)
					#   print "hyp pos", env._rect2pos(env._game.sprite_groups[hypotheses[num].spriteObjects['YELLOW'].className][0].rect)
					#   print rleHistory[idx+n].show(color='green')
					#   print env.show()
					#   embed()

					env.step(action)
					try:
						penalty, errorList = self.errorSignal(env, rleHistory[idx+n+1], hypotheses[num], 
							rleHistory[idx+n], targetClass=targetClass, penalty_only=True)
						penalties.append(penalty)

					# if penalty and 'Chaser' in str(hypotheses[num].spriteObjects['YELLOW'].vgdlType):
					#   print hypotheses[num].spriteObjects['YELLOW'].args
					#   print "action num", n
					#   # print "penalty", penalty
					#   print "true pos", rleHistory[idx+n+1]._rect2pos(rleHistory[idx+n+1]._game.sprite_groups['dough'][0].rect)
					#   print "hyp pos", env._rect2pos(env._game.sprite_groups[hypotheses[num].spriteObjects['YELLOW'].className][0].rect)
					#   print rleHistory[idx+n+1].show(color='green')
					#   print env.show()
					#   embed()
					except:
						print "in experienceReplay"
						embed()
					# if displayStates:
					# 	print penalty
					# 	print env.show(color='blue')
					
				cumulative_penalties.append(penalties)
		
		if not cumulative_penalties:
			print "Warning: did not run experience replay."
			# embed()
			cumulative_penalties = [[0]*len(hypotheses)]

		cumulative_penalties = np.array(cumulative_penalties)
		mean_penalties = np.mean(cumulative_penalties, axis=0)
		return mean_penalties, cumulative_penalties, theoryRLEs


	def testSteps(self, rle, actions, hypotheses, last_only=False, check=False):
		## Evaluates all the hypotheses on the state of the provided rle, given actions.
		## last_only: will take all actions and only *then* evaluate the distance between real and imagined states
		
		theoryRLEs = self.VrleInitPhase(hypotheses, rle)
		# Match IDs between real and theory RLEs
		ID_dictlist = []
		for tR in theoryRLEs:
			match, warning = self.IDmatch(tR, rle)
			if warning:
				print "IDmatch produced a warning, but environments should be the same"
				embed()
			ID_dictlist.append( match)
		# Calculate penalties
		cumulative_penalties = []

		for n,action in enumerate(actions):
			penalties = []
			if last_only==False or n==len(actions)-1:
				envRealPrev = self.fastcopy(rle)
			rle.step(action)
			for num, env in enumerate(theoryRLEs):
				env.step(action)
				if last_only==False or n==len(actions)-1:
					penalty = self.truPenalty(env, rle, ID_dictlist[num])
					# penalty, errorList = self.errorSignal(env, rle, hypotheses[num], envRealPrev)
					penalties.append(penalty)
			if last_only==False or n==len(actions)-1:
				cumulative_penalties.append(penalties)

		cumulative_penalties = np.array(cumulative_penalties)
		# print ">>> Embedded in testSteps"
		# embed()
		return np.mean(cumulative_penalties, axis=0)

	def randomizeState(self, rle):
		rleCopy = self.fastcopy(rle)
		x_options = range(1, rleCopy._game.width-1)
		y_options = range(1, rleCopy._game.height-1)
		pos_options = list(itertools.product(x_options, y_options))
		nonWallObjects = [s for sp in rleCopy._game.sprite_groups.values() for s in sp if s.name!='wall']
		for obj in nonWallObjects:
			newPos = random.choice(pos_options)
			pos_options.remove(newPos)
			rleCopy._setRectPos(obj, newPos)
		rleCopy.step(0)
		return rleCopy
	
	def sampleWithReplacement(self, lst, k):
		outlist = []
		for i in range(k):
			outlist.append(random.choice(lst))
		return outlist

	def testHypotheses(self, hypotheses, rrle=[], num_samples=10, actions_per_sample=10, last_only=False, check=False):
		if rrle==[]:
			rle = self.initializeRLEFromGame()
			rrle = []
			for sample in range(num_samples):
				rrle.append(self.randomizeState(rle))
		cumulative_penalties = []
		for sample in range(num_samples):
			actions = self.sampleWithReplacement(self.actionSet, actions_per_sample)
			penalties = self.testSteps(rrle[sample], actions, hypotheses, last_only=last_only, check=False)
			cumulative_penalties.append(penalties)
		cumulative_penalties = np.array(cumulative_penalties)
		cumulative_penalties = list(np.mean(cumulative_penalties, axis=0))
		scoreAndTheoryTuples = zip(cumulative_penalties, hypotheses)
		#scoreAndTheoryTuples = sorted(scoreAndTheoryTuples, key=lambda x: x[0])
		# print ">>> Embeeded in testHypotheses"
		# embed()
		return scoreAndTheoryTuples

	def plotScores(self, save=False, savename='0-vgdl_score_plot'):
		print "Plotting results..."
		# Get list of scores for each step
		scores = []
		for s in self.theoryScoreHistory:
			scores.append([s[i][0] for i in range(len(s))])
		# Get list of benchmark theory scores for each step
		benchmarks = []
		for s in self.benchmarkHistory:
			benchmarks.append([s[i][0] for i in range(len(s))])
		# Plot scores
		N = len(scores)
		f = plt.figure(figsize = (11, 5))
		ax1 = plt.subplot(111)
		# ax2 = plt.subplot(212)
		f.tight_layout(pad=1.5)
		c = sns.color_palette('deep')

		# Sampled score - surviving batch
		for i in range(N):
			if i==0:
				ax1.plot( (i+1)*np.ones(len(scores[i])), scores[i], '.', c=c[2], ms=7, alpha=.5, label=r"Sampled score for $\{ \theta_s^{(i)} \}$" )
			else:
				ax1.plot( (i+1)*np.ones(len(scores[i])), scores[i], '.', c=c[2], ms=7, alpha=.5 )
		# Sampled score for theory that we considered best in training
		ax1.plot( range(1,N+1), [ scores[i][0] for i in range(N) ], c=c[2], label=r"Sampled score for $\theta_s^*$" )
		
		# Mean error history - all
		for i in range(N):
			if i==0:
				ax1.plot( (i+1)*np.ones(len(self.meanErrorHistory[i])), self.meanErrorHistory[i], '.', c=c[0], ms=7, alpha=.5, label=r"Mean penalty for $\{ \theta_s^{(i)} \}$" )
			else:
				ax1.plot( (i+1)*np.ones(len(self.meanErrorHistory[i])), self.meanErrorHistory[i], '.', c=c[0], ms=7, alpha=.5 )
		# Mean error history - best
		ax1.plot( range(1,N+1), [10*m[0] for m in self.meanErrorHistory], '-', c=c[0], label=r'Mean penalty for $\theta_s^*$ $\times 10$'  )
		
		# Current step error - best
		ax1.plot( range(1,N+1), 10*np.array(self.minStepError), ':', c=c[0], label=r'Current penalty for $\theta_s^*$ $\times 10$'  )

		# # Benchmarks - all
		# for i in range(N):
		#   if i==0:
		#       ax1.plot( (i+1)*np.ones(len(benchmarks[i])), benchmarks[i], '.', c=c[1], ms=7, alpha=.5, label=r"Benchmark set" )
		#   else:
		#       ax1.plot( (i+1)*np.ones(len(benchmarks[i])), benchmarks[i], '.', c=c[1], ms=7, alpha=.5 )
		# Benchmark - best
		ax1.plot( range(1,N+1), [ min(benchmarks[i]) for i in range(N) ], c=c[1], label=r"Benchmark score" )
		ax1.plot( range(1,N+1), [ min(benchmarks[i]) for i in range(N) ], '.', ms=7, c=c[1] )

		# print ">>> Embedded in plot"
		# embed()

		# Plot cosmetics
		ax1.set_xlabel('Step'), ax1.set_ylabel('Score')
		# ax2.set_xlabel('Step'), ax2.set_ylabel('Score')
		#ax1.legend(loc='upper right', fontsize=8)
		box = ax1.get_position()
		ax1.set_position([box.x0, box.y0, box.width * 0.65, box.height])
		ax1.legend(loc='center left', bbox_to_anchor=(1, 0.5))
		# ax2.legend(loc='upper right', fontsize=8)
		if save==True:
			plt.savefig(savename+'.pdf')
		else:
			plt.show()

## Store all rles. Then you can very easily do experience replay!!!


if __name__ == "__main__":

	##simpleGame_missile: no support for learning that it can shoot things.
	# filename = "examples.gridphysics.aliens"

	filename = "examples.gridphysics.avatar_inference"
	# filename = "examples.gridphysics.inference_test"

	# filename = "examples.gridphysics.collect_resource"
	# filename = "examples.continuousphysics.breakout_new"

	global WBP
	if 'grid' in filename:
		import WBP_grid as WBP
	else:
		import WBP_continuous as WBP

	level_game_pairs = None
	# Playing GVG-AI games
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

	def gen_color():
		from vgdl.colors import colorDict
		color_list = colorDict.values()
		color_list = [c for c in color_list if c not in ['UUWSWF']]
		for color in color_list:
			yield color

	# gvggames = ['aliens', 'boulderdash', 'butterflies', 'chase', 'frogs',  # 0-4
	#   'missilecommand', 'portals', 'sokoban', 'survivezombies', 'zelda']  # 5-9

	# gameName = gvggames[6]

	# gvgname = "../gvgai/training_set_1/{}".format(gameName)

	# gameString = read_gvgai_game('{}.txt'.format(gvgname))


	# level_game_pairs = []
	# for level_number in range(5):
	#   with open('{}_lvl{}.txt'.format(gvgname, level_number), 'r') as level:
	#       level_game_pairs.append([gameString, level.read()])

	##uncomment this line to run local games
	gameName = filename

	agent = Agent('full', gameName)

	##For GVGAI games, use this line
	# gameObject = None
	# agent.playCurriculum(level_game_pairs=level_game_pairs)

	##For local games, use this line
	# agent.playCurriculum(level_game_pairs=None)

	## For testing, use this line
	agent.testCurriculum(level_game_pairs=None)
