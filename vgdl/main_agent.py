from IPython import embed
from util import *
from core import colorDict, VGDLParser, sys, keyPresses
from ontology import *
from theory_template import TimeStep, Precondition, InteractionRule, TerminationRule, TimeoutRule, \
SpriteCounterRule, MultiSpriteCounterRule, ruleCluster, Theory, Game, writeTheoryToTxt, generateSymbolDict, \
generateTheoryFromGame
import os, subprocess, shutil
from collections import defaultdict
import WBP
import importlib
import numpy as np
import ipdb, time
import copy
from metaplanner import translateEvents, observe
from rlenvironmentnonstatic import createRLInputGame, createRLInputGameFromStrings, defInputGame, createMindEnv


AvatarTypes = [MovingAvatar, HorizontalAvatar, VerticalAvatar, FlakAvatar, AimedFlakAvatar, OrientedAvatar,
RotatingAvatar, RotatingFlippingAvatar, NoisyRotatingFlippingAvatar, ShootAvatar, AimedAvatar,
AimedFlakAvatar, InertialAvatar, MarioAvatar]

class Agent:
	def __init__(self, modelType, gameFilename):
		self.modelType = modelType
		self.gameFilename = gameFilename
		self.gameString = None
		self.levelString = None
		self.annealingFactor = 1.
		self.shortHorizon = False
		if self.shortHorizon == True:
			self.starting_max_nodes = 20
			self.max_nodes_annealing = 1.005
		else:
			self.starting_max_nodes = 1000
			self.max_nodes_annealing = 10
		self.regrounding = 7
		self.avoid_danger = False
		self.safeDistance = 3
		self.max_quits = 3
		self.hypotheses = []
		self.symbolDict = None
		self.finalEventList = []
		self.statesEncountered = []
		self.fakeInteractionRules = []
		self.all_objects = {}
		self.bestSpriteTypeDict = defaultdict(lambda: {'count':0, 'distribution':None}) ## To track how many times we have run spriteType updates to each particular object
		self.seen_resources = []
		self.seen_limits = []
		self.new_objects = {}

	def initializeEnvironment(self):
		if self.gameString==None or self.levelString==None:
			self.gameString, self.levelString = defInputGame(self.gameFilename, randomize=False)
		self.rleCreateFunc = lambda: createRLInputGameFromStrings(self.gameString, self.levelString)
		self.rle = self.rleCreateFunc()
		return

	def getSpritesByColor(self, rle, color):
		for k in rle._game.sprite_groups.keys():
			if rle._game.sprite_groups[k] and rle._game.sprite_groups[k][0].colorName==color:
				return rle._game.sprite_groups[k]
		return None

	def findNearestSprite(self, sprite, spriteList):
		## returns the sprite in spriteList whose location best matches the location of sprite.
		return sorted(spriteList, key=lambda x:abs(x.rect[0]-sprite.rect[0])+abs(x.rect[1]-sprite.rect[1]))[0]

	def setSpritePositions(self, rle, Vrle, hypothesis):
		## Sets positions of objects in Vrle to what they were in the rle. Bypasses clunky VGDL level description.
		for k in Vrle._game.sprite_groups.keys():
			if Vrle._game.sprite_groups[k]:
				color = Vrle._game.sprite_groups[k][0].colorName
				matchingSpritesInRLE = self.getSpritesByColor(rle, color)
				for sprite in Vrle._game.sprite_groups[k]:
					matchingSprite = self.findNearestSprite(sprite, matchingSpritesInRLE)
					sprite.rect = matchingSprite.rect
					
					if 'Missile' in str(hypothesis.classes[sprite.name][0].vgdlType):
						try:
							orientationDict = self.rle._game.object_token_spriteDistribution[matchingSprite.ID][hypothesis.classes[sprite.name][0].vgdlType]['args']['orientation']
							sprite.orientation = max(orientationDict, key=orientationDict.get) ## gets max key by val
						except KeyError:
							pass
		return


	def initializeVrle(self, hypothesis):
		## World in agent's head given 'hypothesis', including object goal
		gameString, levelString, symbolDict = writeTheoryToTxt(self.rle, hypothesis, self.symbolDict,\
				 "./examples/gridphysics/theorytest.py")
		Vrle = createMindEnv(gameString, levelString, output=False)


		self.setSpritePositions(self.rle, Vrle, hypothesis)

		# try:
		# 	print([(s.rect, s.orientation) for s in Vrle._game.sprite_groups['c4']])
		# 	print([(s.rect, s.orientation) for s in self.rle._game.sprite_groups['missile1']])
		# except:
		# 	pass

		# embed()
		Vrle._game.getAvatars()[0].resources = copy.deepcopy(self.rle._game.getAvatars()[0].resources)
		try:
			Vrle._game.getAvatars()[0].orientation = copy.deepcopy(self.rle._game.getAvatars()[0].orientation)
		except AttributeError:
			pass
		# Vrle.immovables, Vrle.killerObjects = immovables, killerObjects
		return Vrle

	def VrleInitPhase(self, flexible_goals=False):
		## Initialize multiple VRLEs, each corresponding to one hypothesis in self.hypotheses
		VRLEs = []
		# print "in VrleInitPhase.", len(self.hypotheses), "hypotheses"
		# if len(self.hypotheses)>1:
		# 	print "more than one hypothesis"

		for hypothesis in self.hypotheses[0:1]:
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

	def initializeHypotheses(self, allObjects, learnSprites=True):
		if learnSprites:
			observe(self.rle, 5, self.bestSpriteTypeDict)
			spriteTypeHypothesis, exceptedObjects, _ = sampleFromDistribution(self.rle._game, self.rle._game.spriteDistribution, allObjects, self.rle._game.spriteUpdateDict, self.bestSpriteTypeDict)

			self.rle._game.exceptedObjects = exceptedObjects
			gameObject = Game(spriteInductionResult=spriteTypeHypothesis)
			initialTheory = gameObject.buildGenericTheory(spriteTypeHypothesis)

		else:
			gameObject = Game(self.gameString)
			initialTheory = gameObject.buildGenericTheory(spriteSample=False, vgdlSpriteParse = gameObject.vgdlSpriteParse)

		# Handle wall vs. projectile interaction (hacky)
		avatar = [o for o in initialTheory.spriteSet if o.vgdlType in AvatarTypes][0]
		"""
		if 'stype' in avatar.args.keys():
			# old_rule1 = InteractionRule('killSprite', avatar.args['stype'], 'c4', {}, set(), generic=True)
			# old_rule2 = InteractionRule('killSprite', avatar.args['stype'], 'avatar', {}, set(), generic=True)
			# new_rule = InteractionRule('nothing', avatar.args['stype'], 'avatar', {}, set())

			# initialTheory.interactionSet.remove(old_rule1)
			# initialTheory.interactionSet.remove(old_rule2)
			# initialTheory.interactionSet.append(new_rule)
			pass
		"""

		self.hypotheses = [initialTheory]

		self.symbolDict = generateSymbolDict(self.rle)

		return gameObject

	def completeHypotheses(self, allObjects):
		observe(self.rle, 0, self.bestSpriteTypeDict)
		spriteTypeHypothesis, exceptedObjects, _ = sampleFromDistribution(self.rle._game, self.rle._game.spriteDistribution, allObjects, self.rle._game.spriteUpdateDict, self.bestSpriteTypeDict, self.hypotheses[0].spriteSet)
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

			self.quits = 0
			print("Playing level {}".format(n_level))
			(self.gameString, self.levelString) = level_game
			self.max_nodes = self.starting_max_nodes
			win = False
			gameObject = None
			i=0
			levelEffectsEncountered = []
			allStatesEncountered = []
			t1 = time.time()
			while not win:
				gameObject, win, score, steps, statesEncountered, effectsEncountered = self.playEpisode(gameObject, flexible_goals)
				episodes.append((n_level, steps, win, score))
				allStatesEncountered.extend(statesEncountered)
				levelEffectsEncountered.append(effectsEncountered)
				VGDLParser.playGame(self.gameString, self.levelString, statesEncountered,
				persist_movie=True, make_images=True, make_movie=False, movie_dir="videos/"+self.gameFilename, padding=10)
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
		while i<num_episodes:
			gameObject, win, score, statesEncountered, _ = self.playEpisode(gameObject)
			wins.append(win)
			scores.append(score)
			i+=1
		VGDLParser.playGame(self.gameString, self.levelString, self.statesEncountered, \
			persist_movie=True, make_images=True, make_movie=True, movie_dir="videos/"+self.gameFilename, padding=10)
		print "Won {} out of {} episodes.".format(sum(wins), i)

	def updateMemory(self, rle):

		types = list(set([rle._game.all_objects[k]['type']['color'] for k in rle._game.all_objects.keys()]))
		for obj_type in types:
			## find the most-updated object, use that one for the sprite hypothesis.
			options = [k for k in rle._game.all_objects.keys() if rle._game.all_objects[k]['type']['color'] == obj_type]
			k = max(options, key=lambda x:rle._game.spriteUpdateDict[x])

			if rle._game.spriteUpdateDict[k] > self.bestSpriteTypeDict[obj_type]['count']:
				self.bestSpriteTypeDict[obj_type]['count'] = copy.deepcopy(rle._game.spriteUpdateDict[k])
				self.bestSpriteTypeDict[obj_type]['distribution'] = copy.deepcopy(rle._game.spriteDistribution[k])
		return

	def playEpisode(self, gameObject, flexible_goals=False):
		from vgdl.util import manhattanDist

		## Initialize external environment
		self.initializeEnvironment()
		print "initializing RLE"
		steps = 0
		self.all_objects= self.rle._game.getObjects()
		ended, win = self.rle._isDone()
		annealing = 1
		## Start storing encountered states.
		effectsEncountered = []
		statesEncountered = [self.rle._game.getFullState()]
		self.statesEncountered.append(self.rle._game.getFullState())

		## initialize theory if necessary.
		if len(self.hypotheses) == 0:
			gameObject = self.initializeHypotheses(self.all_objects, learnSprites=True)
			print "initializing hypotheses"
		else:
			gameObject = self.completeHypotheses(self.all_objects)
			print "had hypotheses -- completing them."
			# If theory is being carried over, falsify termination hypotheses
			# given new level state
			if not flexible_goals:
				[t.updateTerminations(rle=self.rle) for t in self.hypotheses]

		while not ended:
			## initialize one or many VRLEs according to hypothesis-selection method
			theoryRLEs = self.VrleInitPhase(flexible_goals)


			p = WBP.WBP(theoryRLEs[0], self.gameFilename, theory=self.hypotheses[0], fakeInteractionRules = self.fakeInteractionRules,
				seen_limits = self.seen_limits, annealing=annealing, max_nodes=self.max_nodes, shortHorizon=self.shortHorizon)
			bestNode, gameStringArray = p.BFS()
			solution = p.solution

			self.quits += p.quitting #1 if p.quitting else 0

			quitting = self.quits>self.max_quits

			gameString_array = p.gameString_array
			if solution:
				print "got solution of length", len(solution)
			## add new objects? (line 310 of metaplanner)

			if not quitting:
				for i, action in enumerate(solution):
					self.hypotheses[0].dryingPaint = set()

					hypotheses, theory_change_flag, effects = self.executeStep(action, self.hypotheses, statesEncountered,
						run_induction = not flexible_goals)
					print "theory_change_flag", theory_change_flag
					effectsEncountered.extend(effects)
					steps +=1
					if theory_change_flag:
						self.hypotheses = hypotheses
						break
					ended, win = self.rle._isDone()
					if ended:
						break

					## Make sure you're far enough from unpredictable dangerous objects.

					# Check for disparities between plan and reality
					# (e.g. stochastic effects)
					# if self.rle._game.is_stochastic and i>self.regrounding:
					if i>self.regrounding:
					# if True:
						try:
							if any(np.where(list(gameString_array[i+1]))[0] !=
								   np.where(list(self.rle.show()))[0]):
								print 'regrounding'
								break
						except:
							# Mismatch in gamestring lengths
							print 'regrounding'
							break

					if self.avoid_danger:
						try:
							random_npc_positions = [self.rle._rect2pos(element.rect)
								for objName in self.rle._game.sprite_groups.keys()
								for element in self.rle._game.sprite_groups[objName]
								if element not in self.rle._game.kill_list and
								'RandomNPC' in str(element.__class__)]

							avatar_positions = [self.rle._rect2pos(avatar.rect)
							 	for avatar in self.rle._game.getAvatars()]

							possiblePairList = [manhattanDist(avatar, random)
								for avatar in avatar_positions
								for random in random_npc_positions]

							if min(possiblePairList) < self.safeDistance:
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
				self.updateMemory(self.rle)

				return gameObject, False, self.rle._game.score, steps, statesEncountered, effectsEncountered


			annealing *= self.annealingFactor
			ended, win = self.rle._isDone()
			# if ended and not win:
			# 	print "lost game. embedding"
			# 	embed()

		score = self.rle._game.score
		self.updateMemory(self.rle)
		print "ended episode. Win={}".format(win)
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


		for k in self.new_objects.keys():
			self.new_objects[k] += 1

		if any([self.new_objects[k]>5 for k in self.new_objects.keys()]):
			# if self.new_objects[k] > 5:
			spriteTypeHypothesis, exceptedObjects, _ = sampleFromDistribution(self.rle._game, self.rle._game.spriteDistribution, self.all_objects, self.rle._game.spriteUpdateDict, self.bestSpriteTypeDict, self.hypotheses[0].spriteSet)
			gameObject = Game(spriteInductionResult=spriteTypeHypothesis)

			newHypotheses = []
			for hypothesis in hypotheses:
				newHypotheses.append(gameObject.addNewObjectsToTheory(hypothesis, spriteTypeHypothesis))
			hypotheses = newHypotheses

		[self.new_objects.pop(k, None) for k in self.new_objects.keys() if self.new_objects[k]>5] ## don't track items once we've updated the theory
		return hypotheses

	def executeStep(self, action, hypotheses, statesEncountered, run_induction=True):

		theory_change_flag = False

		spriteInduction(self.rle._game, step=1, bestSpriteTypeDict=self.bestSpriteTypeDict, oldSpriteSet=hypotheses[0].spriteSet)
		spriteInduction(self.rle._game, step=2, bestSpriteTypeDict=self.bestSpriteTypeDict, oldSpriteSet=hypotheses[0].spriteSet)

		agentState = dict(self.rle._game.getAvatars()[0].resources)

		res = self.rle.step(action)

		print ""
		print keyPresses[action]

		try:
			agentState = dict(self.rle._game.getAvatars()[0].resources)

			for e in res['effectList']:
				if 'changeResource' in e:
					changes = e[3]
					if changes['value'] < 0:
						# ipdb.set_trace()
						# undo one negative change to account for eventhandler ordering
						agentState[changes['resource']] -= changes['value']
						break
			self.rle.agentStatePrev = agentState
		# If agent is killed before we get agentState
		except Exception as e:
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
			self.rle.agentStatePrev = agentState



		hypotheses = self.manageNewObjects(hypotheses)

		statesEncountered.append(self.rle._game.getFullState())
		self.statesEncountered.append(self.rle._game.getFullState())
		terminal = self.rle._isDone()[0]

		distributionsHaveChanged = spriteInduction(self.rle._game, step=3, bestSpriteTypeDict=self.bestSpriteTypeDict, oldSpriteSet=hypotheses[0].spriteSet)

		effects = translateEvents(res['effectList'], self.all_objects, self.rle)
		print self.rle.show()
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

			sample, exceptedObjects, _ = sampleFromDistribution(self.rle._game, self.rle._game.spriteDistribution, self.all_objects, self.rle._game.spriteUpdateDict, self.bestSpriteTypeDict, self.hypotheses[0].spriteSet)

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

				elif agentState[resource]==limit and resource not in self.seen_limits:
					self.fakeInteractionRules.extend(hypotheses[0].updateInteractionsPreconditions(resource, limit))
					self.fakeInteractionRules = list(set(self.fakeInteractionRules))
					# resourceColor = self.rle._game.sprite_groups[resource][0].colorName
					self.seen_limits.append(resource)

					## go through everything that can be killed and add a SpriteCounterRule for it?
					spritecounter = SpriteCounterRule(limit=limit,
											  stype=resource,
											  win=True)
					hypotheses[0].terminationSet.append(spritecounter)

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
	# filename = "examples.gridphysics.demo_helper"


	# filename = "examples.gridphysics.expt_physics_sharpshooter"
	# filename = "examples.gridphysics.demo_transform_relational"
	# filename = "examples.gridphysics.simpleGame_push_boulders"
	# filename = "examples.gridphysics.pick_apples"
	# filename = "examples.gridphysics.expt_exploration_exploitation_debugging"

	filename = "examples.gridphysics.expt_movers"

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

	gvggames = ['aliens', 'boulderdash', 'butterflies', 'chase', 'frogs',  # 0-4
		'missilecommand', 'portals', 'sokoban', 'survivezombies', 'zelda']  # 5-9

	gameName = gvggames[0]
	gvgname = "../gvgai/training_set_1/{}".format(gameName)

	gameString = read_gvgai_game('{}.txt'.format(gvgname))


	level_game_pairs = []
	for level_number in range(5):
		with open('{}_lvl{}.txt'.format(gvgname, level_number), 'r') as level:
			level_game_pairs.append([gameString, level.read()])

	##uncomment this line to run local games
	# gameName = filename

	agent = Agent('full', gameName)

	##then pass this down for multiple episodes
	gameObject = None
	agent.playCurriculum(level_game_pairs=level_game_pairs)

	##and use this line
	# agent.playCurriculum(level_game_pairs=None)
