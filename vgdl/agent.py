# from IPython import embed
from util import *
from core import colorDict, VGDLParser, sys, keyPresses
from ontology import *
from theory_template import TimeStep, Precondition, InteractionRule, TerminationRule, TimeoutRule, \
SpriteCounterRule, MultiSpriteCounterRule, ruleCluster, Theory, Game, writeTheoryToTxt, generateSymbolDict, \
generateTheoryFromGame, expandLine
import os, subprocess, shutil
from collections import defaultdict
# import WBP_grid, WBP_continuous
import importlib
import numpy as np
import ipdb, time
import os, subprocess, shutil
import copy
from metaplanner import translateEvents, observe
from rlenvironmentnonstatic import createRLInputGame, createRLInputGameFromStrings, defInputGame, createMindEnv
from termcolor import colored
from line_profiler import LineProfiler
from vgdl.util import manhattanDist
from pygame.locals import K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT


AvatarTypes = [MovingAvatar, HorizontalAvatar, VerticalAvatar, FlakAvatar, AimedFlakAvatar, OrientedAvatar,
RotatingAvatar, RotatingFlippingAvatar, NoisyRotatingFlippingAvatar, ShootAvatar, AimedAvatar,
AimedFlakAvatar, InertialAvatar, MarioAvatar]

# orientationPairs = {(0, 1):(0, -1), DOWN:UP, LEFT:RIGHT, RIGHT:LEFT}


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
		self.resourceObservations = {}
		self.proposalMemory = defaultdict(lambda:[])
		self.memory = []

	def initializeEnvironment(self):
		if self.gameString==None or self.levelString==None:
			self.gameString, self.levelString = defInputGame(self.gameFilename, randomize=False)
		self.rleCreateFunc = lambda: createRLInputGameFromStrings(self.gameString, self.levelString)
		self.rle = self.rleCreateFunc()
		self.rle._game.spriteUpdateDict = self.spriteUpdateDict
		return

	def getSpritesByColor(self, rle, color):
		outList = []
		for k in rle._game.sprite_groups.keys():
			if rle._game.sprite_groups[k] and rle._game.sprite_groups[k][0].colorName==color:
				outList.extend(rle._game.sprite_groups[k])
		if outList:
			return list(set(outList))
		else:
			return None

	def findNearestSprite(self, sprite, spriteList):
		## returns the sprite in spriteList whose location best matches the location of sprite.
		return sorted(spriteList, key=lambda x:abs(x.rect[0]-sprite.rect[0])+abs(x.rect[1]-sprite.rect[1]))[0]




















	## TIM
	def state_distance(self, envA, envB, theory, p_dist=1, p_miss=10):
		"""
		envA: hyptothetical environment
		envB: real environment
		theory: corresponds to hypothetical
		p_dist: distance penalty per grid point
		p_miss: penalty for missing or additional sprite

		Calculates d_theory(envA, envB): distance between the states of the environments
		using the ontology of the supplied theory.

		Also returns errorMap, a dict that contains
		keys: (class1, class2). values: some sort of TBD error signal

		For now we aren't taking a starting environment into account. This means
		That we can't make a comparison between, say,
		random object was at (10, 10), has speed=2
		so at the next location it can be at (10 +- 2, 10+-2), but not anywhere else.
		The best we can do without this info is just penalize very little because it's
		a random object.
		TODO: Implement the above.
		"""

		from vgdl.util import manhattanDist
		from pygame.locals import K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT
		
		# embed()

		print '--- Called state_distance function ---'

		# Initialization
		total_penalty = 0.
		errorMap = {}
		matched_sprites = [] #tuples of matched sprites: (envA sprite, envB sprite, dist) - helps penalize distance and find missing
		lonely_sprites_envA = [] #envA sprites that have no partner in envB
		lonely_sprites_envB = [] #envB sprites that have no partner in envA

		# Loop over keys in envA
		for k in [key for key in envA._game.sprite_groups.keys() if envA._game.sprite_groups[key]]:
			# Get vgdlType, according to the theory
			vgdlType = theory.classes[k][0].vgdlType
			# Find matching sprites via color
			color = envA._game.sprite_groups[k][0].colorName
			matchingSpritesInEnvA = self.getSpritesByColor(envA, color)
			matchingSpritesInEnvB = self.getSpritesByColor(envB, color)
			if matchingSpritesInEnvB == None:
				lonely_sprites_envA.append(matchingSpritesInEnvA)
				continue
			# Loop over matching sprites in envA and find corresponding sprites in envB
			for sprite in matchingSpritesInEnvA:
				corrSprite = self.findNearestSprite(sprite, matchingSpritesInEnvB)
				dist = manhattanDist(envA._rect2pos(sprite.rect), envB._rect2pos(corrSprite.rect))
				#print (sprite, corrSprite, dist)
				matched_sprites.append( (sprite, corrSprite, dist) )

		# Clean up matched_sprites set towards bijective mapping
		matched_sprites_envB = [matched_sprites[i][1] for i in range(len(matched_sprites))]
		matched_dist = [matched_sprites[i][2] for i in range(len(matched_sprites))]
		for sprite in matched_sprites_envB:
			indices = [i for i,t in enumerate(matched_sprites) if t[1]==sprite]
			if len(indices)==1: #no multiple mappings to sprite
				continue
			else: #remove mappings with largest distances
				idx_rm = np.argsort(matched_dist)
				idx_rm = [i for i in idx_rm if any(i==indices)][1:]
				#print '>>> TEST', i==indices
				[lonely_sprites_envA.append(matched_sprites[i][0]) for i in idx_rm] #add to-be-removed sprites in envA to lonely list
				[matched_sprites.pop(i-n) for n,i in enumerate(idx_rm)] #removes entries

		# Find sprites that exist in envB but not envA
		matched_sprites_envB = [matched_sprites[i][1] for i in range(len(matched_sprites))]
		for k in [key for key in envB._game.sprite_groups.keys() if envB._game.sprite_groups[key]]:
			color = envB._game.sprite_groups[k][0].colorName
			matchingSprites = self.getSpritesByColor(envB, color)
			for sprite in matchingSprites:
				if not any([matched_sprites_envB[i]==sprite for i in range(len(matched_sprites_envB))]):
					lonely_sprites_envB.append(sprite)

		# ## Test output
		# print '>>> matched_sprites:'
		# for i in range(len(matched_sprites)):
		# 	if True: #matched_sprites[i][2]!=0:
		# 		print matched_sprites[i]
		# print '>>> lonely_sprites_envA:', [s for s in lonely_sprites_envA]
		# print '>>> lonely_sprites_envB:', [s for s in lonely_sprites_envB]

		# Re-match elements of same class that are 'lonely' in both environments
		# (these could be result of teleporting - to do: add teleportation distance metric here)
		# (Watch out: we could have had a blue block deleted and a different one created somewhere else)
		dist_rematch = []
		mindist_rematch = []
		sprites_rematchA = [] #re-matched sprites in envA
		sprites_rematchB = [] #re-matched sprites in envB
		for sA in lonely_sprites_envA:
			dist_temp = []
			for sB in lonely_sprites_envB:
				if sB.colorName==sA.colorName:
					dist_temp.append( manhattanDist(envA._rect2pos(sA.rect), envB._rect2pos(sB.rect)) )
				else:
					dist_temp.append(2e6)
				#if all([d==None for d in dist_rematch]): #case where there is no potential re-match
			dist_rematch.append(dist_temp)
			#print '>>> dist_rematch', dist_rematch
			mindist_rematch.append(min([d for d in dist_rematch[-1]]))

		while len(mindist_rematch)>0 and min(mindist_rematch)<1e6: #run as long as potential re-matches available
			idx_sprite = np.argmin(mindist_rematch) #first re-match sprite with minimum distance to potential partner
			idx_match = np.argmin(dist_rematch[idx_sprite]) #re-match to closest potential partner
			#print '>>> idx_sprite', idx_sprite
			#print '>>> idx_match', idx_match
			# Append (envA sprite, envB sprite, dist) tuple to matched sprites list
			matched_sprites.append( (lonely_sprites_envA[idx_sprite], lonely_sprites_envB[idx_match], min(mindist_rematch)) )
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

		## Test output
		print '>>> matched_sprites:'
		for i in range(len(matched_sprites)):
			if True: #matched_sprites[i][2]!=0:
				print matched_sprites[i]
		print '>>> lonely_sprites_envA:', [s for s in lonely_sprites_envA]
		print '>>> lonely_sprites_envB:', [s for s in lonely_sprites_envB]


		## Penalize distance and additional/missing sprites
		# Distance penalty
		for t in matched_sprites:
			sA = t[0] #sprite in envA
			dist = t[2] #distance to sprite in envB
			sA_type = theory.classes[sA.name][0].vgdlType
			if str(sA_type) == "<class 'vgdl.ontology.RandomNPC'>":
				sA_speed = theory.classes[sA.name][0].speed
				if dist>2*sA_speed:
					total_penalty += p_dist*t[2]
			else: #all of the other types are deterministic
				total_penalty += p_dist*t[2]				
		# Missing/additional penalty
		total_penalty += p_miss * ( len(lonely_sprites_envA) + len(lonely_sprites_envB) )

		print '>>> Total penalty:', total_penalty

		# Construct errorMap using previous state


		## TODO: penalize as a function of vgdlType and color
		## TODO: deal with cases where you don't find objects in one env but you do in the other

		## NOTE: Use intializeHypotheses function in this file to build my test theories

		return total_penalty, errorMap






































	def setSpritePositions(self, rle, Vrle, hypothesis):
		## Sets positions of objects in Vrle to what they were in the rle. Bypasses clunky VGDL level description.

		old_sprite_groups = Vrle._game.sprite_groups
		for k in old_sprite_groups.keys():
			if old_sprite_groups[k]:
				color = Vrle._game.sprite_groups[k][0].colorName
				matchingSpritesInRLE = self.getSpritesByColor(rle, color)
				for sprite in old_sprite_groups[k]:
					matchingSprite = self.findNearestSprite(sprite, matchingSpritesInRLE)
					sprite.rect = matchingSprite.rect
					sprite.lastmove = matchingSprite.lastmove
					if 'Missile' in str(hypothesis.classes[sprite.name][0].vgdlType) and self.best_params!=None:
						try:
							## Enforce consistency: inferred value for individual orientations has to be consistent with what we're saying the horizontal/vertical orientation is of the entire group.
							# embed()

							orientation = tuple(np.sign(np.array(self.rle._game.previousPositions[matchingSprite.ID]) - np.array(self.rle._game.objectMemoryDict[matchingSprite.ID])))

							if orientation == (0,0):
								# print "found 0,0 orientation. Using generic missile orientation:", sprite.orientation, sprite.speed, sprite.cooldown
								pass

							else:
								sprite.orientation = orientation

						except KeyError:
							print "Failed to get params for Missile in main_agent"
							# embed()
							pass
		return


	def initializeVrle(self, hypothesis):
		## World in agent's head given 'hypothesis', including object goal
		gameString, levelString, symbolDict = writeTheoryToTxt(self.rle, hypothesis, self.symbolDict,\
				 "./examples/gridphysics/theorytest.py")
		Vrle = createMindEnv(gameString, levelString, output=False)

		self.setSpritePositions(self.rle, Vrle, hypothesis)

		## Initialize imaginary state to match real state.
		try:
			Vrle._game.getAvatars()[0].resources = copy.deepcopy(self.rle._game.getAvatars()[0].resources)
			Vrle._game.getAvatars()[0].orientation = copy.deepcopy(self.rle._game.getAvatars()[0].orientation)
			Vrle._game.getAvatars()[0].jumping = copy.deepcopy(self.rle._game.getAvatars()[0].jumping)
			Vrle._game.getAvatars()[0].jumping = copy.deepcopy(self.rle._game.getAvatars()[0].wait_step)
			Vrle._game.getAvatars()[0].jumping = copy.deepcopy(self.rle._game.getAvatars()[0].rope)
			Vrle._game.getAvatars()[0].jumping = copy.deepcopy(self.rle._game.getAvatars()[0].gravity)
			Vrle._game.getAvatars()[0].jumping = copy.deepcopy(self.rle._game.getAvatars()[0].last_rope)
			Vrle._game.getAvatars()[0].jumping = copy.deepcopy(self.rle._game.getAvatars()[0].last_gravity)
			Vrle._game.getAvatars()[0].jumping = copy.deepcopy(self.rle._game.getAvatars()[0].last_vy)
			Vrle._game.getAvatars()[0].jumping = copy.deepcopy(self.rle._game.getAvatars()[0].lastrect)
			Vrle._game.getAvatars()[0].jumping = copy.deepcopy(self.rle._game.getAvatars()[0].speed)

		except (IndexError, AttributeError) as e:
			pass
		# Vrle.immovables, Vrle.killerObjects = immovables, killerObjects
		return Vrle

	def VrleInitPhase(self, flexible_goals=False):
		## Initialize multiple VRLEs, each corresponding to one hypothesis in self.hypotheses
		VRLEs = []
		# print "in VrleInitPhase.", len(self.hypotheses), "hypotheses"
		# if len(self.hypotheses)>1:
		# 	print "more than one hypothesis"

		# for hypothesis in self.hypotheses[0:1]:
		for hypothesis in self.hypotheses:
			tempHypothesis = copy.deepcopy(hypothesis)
			tmpFakeInteractionRules = copy.deepcopy(self.fakeInteractionRules)
			tempHypothesis.interactionSet.extend(tmpFakeInteractionRules)
			if not flexible_goals:
				tempHypothesis.updateTerminations()
			# print "fake hypotheses"
			# if self.fakeInteractionRules:/
				# tempHypothesis.display()
			VRLEs.append(self.initializeVrle(tempHypothesis))
		# print("wrote theory to text")


		return VRLEs

	#<< To build own theory: check comments below
	def initializeHypotheses(self, allObjects, learnSprites=True, num_variants=10):
		if learnSprites:
			observe(self.rle, 3, self.bestSpriteTypeDict)
			spriteTypeHypothesis, exceptedObjects, _, self.best_params = sampleFromDistribution(self.rle._game, \
				self.rle._game.spriteDistribution, allObjects, self.rle._game.spriteUpdateDict, self.bestSpriteTypeDict)
			self.rle._game.exceptedObjects = exceptedObjects
			gameObject = Game(spriteInductionResult=spriteTypeHypothesis)
			initialTheory = gameObject.buildGenericTheory(spriteTypeHypothesis)

		else:
			gameObject = Game(self.gameString)
			initialTheory = gameObject.buildGenericTheory(spriteSample=False, vgdlSpriteParse = gameObject.vgdlSpriteParse)

		# Handle wall vs. projectile interaction (hacky)
		avatar = [o for o in initialTheory.spriteSet if o.vgdlType in AvatarTypes][0]

		self.hypotheses = [initialTheory]
		self.symbolDict = generateSymbolDict(self.rle)



		## For debugging purposes, generating one variant that is off by only one interaction
		theory = copy.deepcopy(initialTheory)
		for interactionRule in theory.interactionSet: #<< find rule between avatar and e.g. c3
			#if interactionRule.slot1=='avatar' and interactionRule.slot2 == 'c2':
				#interactionRule.interaction = 'bounceForward'
			if interactionRule.interaction == 'killSprite':
				interactionRule.interaction = 'stepBack'
				break
		self.hypotheses.append(theory)

		## Generate variants of the theory
		## (as a stand-in for a more generic induction/elaboration process)
		predicate_options = ['nothing', 'stepBack', 'killSprite', 'bounceForward', 'undoAll']
		for i in range(num_variants):
			theory = copy.deepcopy(initialTheory)
			for interactionRule in theory.interactionSet:
				interactionRule.interaction = predicate_options[i%len(predicate_options)]#random.choice(predicate_options)
			self.hypotheses.append(theory)

		return gameObject

	# def initializeHypotheses(self, allObjects, learnSprites=True):
	# 	if learnSprites:
	# 		observe(self.rle, 3, self.bestSpriteTypeDict)
	# 		spriteTypeHypothesis, exceptedObjects, _, self.best_params = sampleFromDistribution(self.rle._game, \
	# 			self.rle._game.spriteDistribution, allObjects, self.rle._game.spriteUpdateDict, self.bestSpriteTypeDict)
	# 		self.rle._game.exceptedObjects = exceptedObjects
	# 		gameObject = Game(spriteInductionResult=spriteTypeHypothesis)
	# 		initialTheory = gameObject.buildGenericTheory(spriteTypeHypothesis)

	# 	else:
	# 		gameObject = Game(self.gameString)
	# 		initialTheory = gameObject.buildGenericTheory(spriteSample=False, vgdlSpriteParse = gameObject.vgdlSpriteParse)

	# 	# Handle wall vs. projectile interaction (hacky)
	# 	avatar = [o for o in initialTheory.spriteSet if o.vgdlType in AvatarTypes][0]

	# 	self.hypotheses = [initialTheory]

	# 	self.symbolDict = generateSymbolDict(self.rle)

	# 	return gameObject



	def conductInference(self, errorSignal):

		## TODO:
		##modularize. one function should be able to fix the problems generated by one classPair
		## another calls that function on all classPairs		
		
		## For now, only take an errorSignal with one key.
		## TODO: Implement a loop that goes through all keys by:
		## proposing all theories (given the proposalMemory) for one key
		## filtering to get high-probability ones (or at least ones that reduce that error signal)

		from vgdl.theory_template import expandLine, proposePredicates
		n=2

		# errorSignal = {('avatar','c2'):['unexpectedOverlap', 'orientationChange']}


		self.resourceObservations = {'speed': [0, 10],\
								'changeResource': [{'resource':'c2', 'value':1, 'limit':1}]}

		singlePairErrorSignal = {('avatar','c2'):['unexpectedOverlap', 'orientationChange']}
		globalObservations = {'physicsType':'gridphysics'}
		predicates = proposePredicates(singlePairErrorSignal, self.memory, self.proposalMemory, globalObservations)
		
		embed()
		classPair, newTheories, predicateGroups = expandLine(self.hypotheses[1], ('avatar', 'c2'), 
			predicates = predicates, n=n, 
			resourceObservations=self.resourceObservations, generic=True)

		self.proposalMemory[classPair].extend(predicateGroups)

		## TODO:
		## Decide what to do with all the new theories. Do you want to replace the existing hypothesis space?
		return

	def completeHypotheses(self, allObjects, first_time_playing_level):
		if first_time_playing_level:
			observe(self.rle, 15, self.bestSpriteTypeDict) ## observe many steps so that you're not completely clueless about object movements for the new level
		else:
			observe(self.rle, 15, self.bestSpriteTypeDict) ## observe a couple steps so that you're not completely clueless about object movements when you're restarting a level.
		
		## Make sure any objects that appeared while we were observing are reflected in allObjects
		for k,v in self.rle._game.getObjects().items():
			if k not in allObjects:
				allObjects[k] = v

		spriteTypeHypothesis, exceptedObjects, _, self.best_params= sampleFromDistribution(self.rle._game, self.rle._game.spriteDistribution, allObjects, self.rle._game.spriteUpdateDict, self.bestSpriteTypeDict, self.hypotheses[0].spriteSet)
		gameObject = Game(spriteInductionResult=spriteTypeHypothesis)
		newHypotheses = []
		for hypothesis in self.hypotheses:
			newHypotheses.append(gameObject.addNewObjectsToTheory(hypothesis, spriteTypeHypothesis))
		self.hypotheses = newHypotheses


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
			# 	flexible_goals=True

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


	def playEpisode(self, gameObject, flexible_goals=False, win=False, first_time_playing_level=False):
		# from vgdl.util import manhattanDist

		## Initialize external environment
		self.initializeEnvironment()
		print "initializing RLE"
		# embed()
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
			gameObject = self.initializeHypotheses(self.all_objects, learnSprites=True, num_variants=0)
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
			theoryRLEs = self.VrleInitPhase(flexible_goals)
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
						observe(self.rle, 5, self.bestSpriteTypeDict)
						solution = [] ## You may have gotten p.quitting but also a solution; make sure you don't try to act on that if the planner decided it wasn't worth it.
						self.longHorizonObservations += 1
					else:
						quitting = True

			if emptyPlans > self.emptyPlansLimit:
				observe(self.rle, 5, self.bestSpriteTypeDict)





















			## TIM
			from vgdl.util import manhattanDist
			from pygame.locals import K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT

			
			actions = [K_RIGHT]
			for action in actions:
				self.rle.step(action)

				newTheories = []
				for num, env in enumerate(theoryRLEs):
					env.step(action)
					env.step(K_UP) #hack to make hypothetical RLEs much different from real
					env.step(K_LEFT) #hack to make hypothetical RLEs much different from real
					env.step(K_LEFT)
					env.step(K_LEFT)
					env.step(K_LEFT)
					env.step(K_LEFT)
					env.step(K_LEFT)
			

					## Pedro: Outlining rest of functions:
					# distance, errorMap = self.state_distance(self.rle, env, self.hypotheses[num])
					# childTheories = expandTheory(self.hypotheses[num], errorMap)
					# newTheories.extend(childTheories)

				# Pedro: Filter new theories according to whatever scheme

			## Actual world
			print self.rle.show()

			#embed()

			## Tim: Predicted worlds under each theory
			for num, env in enumerate(theoryRLEs):
				## Tim: uncomment if you want to see the full theory corresponding to each env
				self.hypotheses[num].display()  
				print env.show()
				break

			## Tim: Can run the state-distance function here.
			for num, env in enumerate(theoryRLEs):
				self.state_distance(env, self.rle, self.hypotheses[num])
				break

			print "Embedded in inference part"
			embed()

			errorSignal = {('avatar','c2'):['unexpectedOverlap', 'orientationChange']}

			# self.conductInference(errorSignal)


			print "theory expansion time for n={}: {}".format(n, time.time()-t0)
			t0=time.time()
			newRLEs = [self.initializeVrle(theory) for theory in newTheories]
			print "Environment initialization for {} environments: {}".format(len(newRLEs), time.time()-t0)
			t0=time.time()
			for env in newRLEs:
				env.step(K_RIGHT)
			print "Single step time for {} environments: {}".format(len(newRLEs), time.time()-t0)
			

			## Pedro:
			## think about whether you want to store the initial state
			## so that you can make better comparisons
			## or just to have some ongoing game where you just make more theories and correct
			## them online and future behavior gets better.
			## probably the latter is simpler for now.

			# Note from Skype
			# I can replace envB by envB.step(K_RIGHT) to generate a different state


















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
								self.rle._game.objectMemoryDict[k] = copy.deepcopy(self.rle._game.previousPositions[k])
						except KeyError:
							pass
					self.rle._game.previousPositions = copy.deepcopy(self.rle._game.nextPositions)


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
							# # 	   np.where(list(self.rle.show()))[0]):
							# 	print 'regrounding'
							# 	embed()
							# 	# embed()
							# 	break
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
			# 	print "lost game. embedding"
			# 	embed()


		## Update global memory of updates
		# for k in game.spriteUpdateDict:
			# self.spriteUpdateDict[k] = game.spriteUpdateDict[k]

		score = self.rle._game.score
		# self.updateMemory(self.rle)

		output = "ended episode. Win={}					".format(win)
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

	def manageNewObjects(self, hypotheses):
		## Add newly-seen objects.
		current_objects = self.rle._game.getObjects()
		for k in current_objects.keys():
			spriteName = current_objects[k]['sprite'].name
			if spriteName not in [self.all_objects[key]['sprite'].name for key in self.all_objects.keys()]:
				print "new object", spriteName
				self.all_objects[k] = current_objects[k]
				distributionInitSetup(self.rle._game, k)
				## prevent spriteInduction from trying to infer anything about newly-appeared sprites in this timestep.
				self.rle._game.ignoreList.append(k)
				self.new_objects[spriteName] = 0

		return hypotheses

	def executeStepProfiler(self, action, hypotheses, statesEncountered, run_induction=True):
		lp = LineProfiler()
		lp_wrapper = lp(self.executeStep)
		hypotheses, theory_change_flag, effects = lp_wrapper(action, hypotheses, statesEncountered, run_induction)
		lp.print_stats()
		return hypotheses, theory_change_flag, effects


	def executeStep(self, action, hypotheses, statesEncountered, run_induction=True):

		theory_change_flag = False

		spriteInduction(self.rle._game, step=1, bestSpriteTypeDict=self.bestSpriteTypeDict, oldSpriteSet=hypotheses[0].spriteSet)
		spriteInduction(self.rle._game, step=2, bestSpriteTypeDict=self.bestSpriteTypeDict, oldSpriteSet=hypotheses[0].spriteSet)

		try:
			agentState = copy.deepcopy(self.rle._game.getAvatars()[0].resources)
		except IndexError:
			agentState = defaultdict(lambda: 0)
		try:
			agentState['speed'] = self.rle._game.getAvatars()[0].speed
		except AttributeError:
			agentState['speed'] = None

		embed()
		res = self.rle.step(action)

		print ""
		print keyPresses[action]

		try:
			agentState = copy.deepcopy(self.rle._game.getAvatars()[0].resources)

			for e in res['effectList']:
				if 'changeResource' in e:
					changes = e[3]
					if changes['value'] < 0:
						# ipdb.set_trace()
						# undo one negative change to account for eventhandler ordering
						agentState[changes['resource']] -= changes['value']
						break
		# If agent is killed before we get agentState
		except (IndexError, AttributeError) as e:
			# agentState = defaultdict(lambda:0)
			ignored_negative_change = False
			for e in res['effectList']:
				if 'changeResource' in e:
					changes = e[3]
					if changes['value'] > 0 or ignored_negative_change:
						agentState[changes['resource']] += changes['value']
					else:
						agentState[changes['resource']] += 0
						ignored_negative_change = True
		try:
			agentState['speed'] = self.rle._game.getAvatars()[0].speed
		except AttributeError:
			agentState['speed'] = None

		self.rle.agentStatePrev = agentState


		hypotheses = self.manageNewObjects(hypotheses)

		statesEncountered.append(self.rle._game.getFullState())
		self.statesEncountered.append(self.rle._game.getFullState())
		terminal = self.rle._isDone()[0]

		distributionsHaveChanged = spriteInduction(self.rle._game, step=3, bestSpriteTypeDict=self.bestSpriteTypeDict, oldSpriteSet=hypotheses[0].spriteSet)

		effects = translateEvents(res['effectList'], self.all_objects, self.rle)
		print self.rle.show(color='blue')
		print self.rle._game.score

		all_effects = [item for sublist in [e['effectList'] for e in self.finalEventList] for item in sublist]

		event = {'agentState': agentState, 'agentAction': action, 'effectList': effects, \
			'gameState': self.rle._game.getFullStateColorized(), 'rle': self.rle}
		if event['effectList']:
			self.finalEventList.append(event)

		if (event['effectList'] and run_induction) or distributionsHaveChanged:

			print "event", (not all([e in all_effects for e in effects])), "distributions changed", distributionsHaveChanged

			## Delete fake interaction rules for events that were witnessed in this time step.
			oldFakeInteractionRules = copy.deepcopy(self.fakeInteractionRules)
			self.fakeInteractionRules = [r for r in self.fakeInteractionRules if
				not any([self.matchEventToRuleByIDAndSpriteName(e, r) for e in event['effectList']])]



			if (not all([e in all_effects for e in effects])) or distributionsHaveChanged:
				theory_change_flag = True

			sample, exceptedObjects, _, self.best_params= sampleFromDistribution(self.rle._game, self.rle._game.spriteDistribution, self.all_objects, self.rle._game.spriteUpdateDict, self.bestSpriteTypeDict, self.hypotheses[0].spriteSet)

			if any(['conveySprite'==e[0] for e in event['effectList']]):
				## start storing avatar position; at next step, take curr_position - prev_position and compare to prev_action*avatar.strength. 
				## that should be the conveyor's strength.
				## overwrite sprite object in the sample w/ conveyor, get writeTheoryToTxt args working
				## and then you need to decide how to not overwrite the sprite type at every step for the conveyor.
				print "found conveysprite"
				embed()
			# for s in sample:
				# s.display()
			# embed()
			game_object = Game(spriteInductionResult=sample)

			terminationCondition = {'ended': False, 'win':False, 'time':self.rle._game.time}
			trace = ([TimeStep(e['agentAction'], e['agentState'], e['effectList'], e['gameState'], e['rle']) \
				for e in self.finalEventList], terminationCondition)
			hypotheses = list(game_object.runInduction(game_object.spriteInductionResult, trace, 20, \
			verbose=False, existingTheories=hypotheses))

			if hypotheses[0].__dict__ != self.hypotheses[0].__dict__:
				theory_change_flag = True

			# if len(hypotheses)>1:
			# 	print "more than one hypothesis"

			#  PRECONDITIONS HANDLING
			# Current assumptions:
		 	# - Only one resource can change for each timestep
			# - The first time a resource changes, it goes from 0 to a positive
			#   value
			for change_resource_effect in [e[3] for e in event['effectList'] if 'changeResource' in e]:
				resource = change_resource_effect['resource']
				val = change_resource_effect['value']
				limit = change_resource_effect['limit']

				# print "adding fake rules"
				# import ipdb; ipdb.set_trace()
				# ipdb.set_trace()

				if (resource not in self.seen_resources and val>0):
					self.fakeInteractionRules.extend(hypotheses[0].updateInteractionsPreconditions(resource))
					self.fakeInteractionRules = list(set(self.fakeInteractionRules))
					# resourceColor = self.rle._game.sprite_groups[resource][0].colorName
					# Add resource change to seen_resources list
					self.seen_resources.append(resource)

					hypotheses[0].resource_limits[resource] = limit

					## go through everything that can be killed and add a SpriteCounterRule for it?
					# spritecounter = SpriteCounterRule(limit=limit,
											  # stype=resource,
											  # win=True)
					# hypotheses[0].terminationSet.append(spritecounter)

				elif agentState[resource]==limit and resource not in self.seen_limits:
					self.fakeInteractionRules.extend(hypotheses[0].updateInteractionsPreconditions(resource, limit))
					self.fakeInteractionRules = list(set(self.fakeInteractionRules))
					# resourceColor = self.rle._game.sprite_groups[resource][0].colorName
					self.seen_limits.append(resource)



					theory_change_flag = True
					# print "reached resource limit for", resource

		if event['effectList'] and run_induction:
			[t.updateTerminations(event=event) for t in hypotheses]
		if theory_change_flag and not distributionsHaveChanged:
			print "changed theory:"
			hypotheses[0].display()


		return hypotheses, theory_change_flag, effects


if __name__ == "__main__":

	##simpleGame_missile: no support for learning that it can shoot things.

	filename = "examples.gridphysics.inference_test"
	#filename = "examples.continuousphysics.collect_resource"
	# filename = "examples.continuousphysics.rope_test"

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
	# 	'missilecommand', 'portals', 'sokoban', 'survivezombies', 'zelda']  # 5-9

	# gameName = gvggames[6]

	# gvgname = "../gvgai/training_set_1/{}".format(gameName)

	# gameString = read_gvgai_game('{}.txt'.format(gvgname))


	# level_game_pairs = []
	# for level_number in range(5):
	# 	with open('{}_lvl{}.txt'.format(gvgname, level_number), 'r') as level:
	# 		level_game_pairs.append([gameString, level.read()])

	##uncomment this line to run local games
	gameName = filename

	agent = Agent('full', gameName)

	##For GVGAI games, use this line
	# gameObject = None
	# agent.playCurriculum(level_game_pairs=level_game_pairs)

	##For local games, use this line
	agent.playCurriculum(level_game_pairs=None)
