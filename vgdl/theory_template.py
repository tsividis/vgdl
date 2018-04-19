from random import choice
import itertools, copy, scipy.misc
import numpy as np
import dill
import tempfile
from class_theory_template import *
from taxonomy import *
from IPython import embed
from ontology import *
from collections import defaultdict
import ipdb
import operator
import time, math
from util import factorize, objectsToSymbol, ccopy
from rlenvironmentnonstatic import createMindEnv
from line_profiler import LineProfiler


ALNUM = '0123456789bcdefhijklmnpqrstuvwxyzQWERTYUIOPSDFHJKLZXCVBNM,./;[]<>?:`-=~!@#$%^&*()_+'
AvatarTypes = [MovingAvatar, HorizontalAvatar, VerticalAvatar, FlakAvatar, AimedFlakAvatar, OrientedAvatar,
RotatingAvatar, RotatingFlippingAvatar, NoisyRotatingFlippingAvatar, ShootAvatar, AimedAvatar,
AimedFlakAvatar, InertialAvatar, MarioAvatar]

"""
Theory induction on VGDL Games
"""

class Precondition(object):
	"""
	Appended to InteractionRules if conflicting effects occur from the same interaction, due to changed resources.
	"""
	def __init__(self, text, item, operator_name, num, negated=False):
		self.text = text
		self.item = item
		self.operator_name = operator_name
		self.num = num
		self.negated = negated

	def copy(self):
		return Precondition(self.text, self.item, self.operator_name, self.num, self.negated)

	def check(self, dictionary):
		if self.item not in dictionary.keys():
			dictionary[self.item] = 0

		if self.operator_name == '>':
			answer = dictionary[self.item] > self.num
		elif self.operator_name == '>=':
			answer = dictionary[self.item] >= self.num
		elif self.operator_name == '<':
			answer = dictionary[self.item] < self.num
		elif self.operator_name == '<=':
			answer = dictionary[self.item] <= self.num

		if self.negated:
			return not answer
		else:
			return answer

	def negate(self):
		self.negated = not self.negated
		self.text = 'not '+ self.text

	def display(self):
		print self.text

	def __eq__(self, other):
		try:
			return self.text == other.text
		except AttributeError:
			return False

	def __ne__(self, other):
		return not self.__eq__(other)

class InteractionRule(object):
	"""
	Rule defining how 2 classes of objects interact with each other.
	# TODO: Should enforce proper syntax for interaction rules

	"""
	def __init__(self, interaction, c1, c2, args, preconditions=set(), generic=False):
		self.interaction = interaction
		self.slot1 = c1
		self.slot2 = c2
		self.args = args
		self.preconditions = preconditions
		self.generic = generic ## if generic, this interaction rule belongs to the generic prior that is meant to be overriden.
		self._hash = hash((self.interaction, self.slot1, self.slot2, tuple(sorted(self.args.iteritems()))))

	def display(self):
		print self

	def __repr__(self):
		if not self.preconditions:
			string = "%s %s %s %r" % (self.interaction, self.slot1, self.slot2, self.args)
		else:
			string = "%s %s %s %r %r" % (self.interaction, self.slot1, self.slot2, self.args, [p.text for p in self.preconditions])
		return string

	def copy(self):
		return InteractionRule(self.interaction, self.slot1, self.slot2, dict(self.args) if self.args else {},
				set([p.copy() for p in self.preconditions]), self.generic)

	def asTuple(self):
		return (self.interaction, self.slot1, self.slot2, self.args)

	def addPrecondition(self, precondition):
		"""
		TODO: Now that we've reimplemented preconditions as lambda functions,
		it can't properly check for equality of preconditions. You *may*
		be able to get around this by checking for the equality of precondition.text
		and making sure that precondition.text always reflects the functioning of the
		lambda function.
		"""
		curr_preconditions = [p.text for p in self.preconditions]
		if precondition.text not in curr_preconditions: #TODO: change equality for preconditions?
			self.preconditions = set([precondition]) #TODO: Need to change this, if we accept more than one precondition for an interaction rule

	def checkPreconditions(self, agentState):
		return all([p.check(agentState) for p in self.preconditions])

	def __hash__(self):
		return self._hash #+hash(time.time())

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return all([
				self.asTuple()==other.asTuple(),
				self.preconditions==other.preconditions
				])
		else:
			return False

	def __ne__(self, other):
		return not self.__eq__(other)

class TerminationRule:
	"""
	TODO: eventually incorporate multiple sprite termination conditions and timeout termination conditions.
	At the moment, we assume single sprite conditions
	"""
	def __init__(self, termination, win, **kwargs):
		self.termination = termination(win=win, **kwargs)
		# self._hash = hash(self.termination.name)

	def isDone(self, game):
		return self.termination.isDone()

	def copy(self):
		return ccopy(self)

	def display(self):
		print (self.termination.name+'Rule', self.termination.get_args())

	def __eq__(self,other):
		return self.asTuple() == other.asTuple()

	def __hash__(self):
		return self._hash

def TerminationRuleConstructor(rule_type, **kwargs):
	try:
		if rule_type == 'NoveltyTerminationRule':
			termination_rule = NoveltyRule
		else:
			termination_rule = eval(rule_type)
		return termination_rule(**kwargs)
	except NameError:
		raise NameError, "termination rule '%s' not defined" % rule_type

class TimeoutRule(TerminationRule):
	def __init__(self, limit=0, win=False):
		self.termination = Timeout(limit=limit, win=win)
		self.ruleType = "TimeoutRule"
		self._hash = hash(self.asTuple())

	def __repr__(self):
		return str(self.asTuple())

	def display(self):
		print self.asTuple()

	def asTuple(self):
		return (self.ruleType, self.termination.limit, self.termination.win)

class NoveltyRule(TerminationRule):
	""" Game ends when the number of sprites of type 'stype' hits 'limit' (or below). """
	def __init__(self,s1,s2,win,args=None):
		"""sclass = sprite class, snumber = sprite number, win = whether termination is a win"""
		self.termination = NoveltyTermination(s1=s1, s2=s2, win=win, args=args)
		self.ruleType = "NoveltyRule"
		args = args if args else {}
		self._hash = hash((self.ruleType, self.termination.s1, self.termination.s2, self.termination.win, tuple(sorted(args.iteritems()))))

	def __repr__(self):
		return str(self.asTuple())

	def display(self):
		print self.asTuple()

	def asTuple(self):
		return (self.ruleType, self.termination.s1, self.termination.s2, self.termination.win, self.termination.args)

class SpriteCounterRule(TerminationRule):
	""" Game ends when the number of sprites of type 'stype' hits 'limit' (or below). """
	def __init__(self,stype,limit,win):
		"""sclass = sprite class, snumber = sprite number, win = whether termination is a win"""
		self.termination = SpriteCounter(limit=limit, stype=stype, win=win)
		self.ruleType = "SpriteCounterRule"
		self._hash = hash(self.asTuple())

	def __repr__(self):
		return str(self.asTuple())

	def display(self):
		print self.asTuple()

	def asTuple(self):
		return (self.ruleType, self.termination.stype, self.termination.limit, self.termination.win)

class MultiSpriteCounterRule(TerminationRule):
    """ Game ends when the sum of all sprites of types 'stypes' hits 'limit'. """
    def __init__(self, limit=0, win=True, stypes = []):
    	argList = dict((str(i), stype) for i, stype in enumerate(stypes))
        self.termination = MultiSpriteCounter(limit=limit,win=win, **argList)
        self.ruleType = "MultiSpriteCounterRule"
        self._hash = hash((self.ruleType, tuple(sorted(self.termination.stypes)), self.termination.limit, self.termination.win))


    def __repr__(self):
    	return str(self.asTuple())

    def display(self):
        print self.asTuple()

    def asTuple(self):
        return (self.ruleType, set(self.termination.stypes), self.termination.limit, self.termination.win)

## Helper print function
def printInteractionSet(interactionSet):
		print [i.display() for i in interactionSet]

class Theory(object):
	"""
	A VGDL description of a game
	"""
	def __init__(self, game):
		self.game = game
		self.parent = None
		self.children = []
		self.twins = [] #Not used now, but potentially use to keep better track of genealogy
		self.depth = 0

		# Following VGDL structure
		self.spriteSet = [] # Includes properties of sprites/objects
		self.levelMapping = [] # Map of the game
		self.interactionSet = [] # Interaction rules
		self.terminationSet = set() # Conditions that lead to game termination

		self.spriteObjects = {} # Maps sprite color -> Sprite object
		self.classes = {} # Maps classes -> objects
		self.predicates = set() # Types of possible interactions

		self.dryingPaint = set()
		self.inModification = {}

		self.falsified = set()
		self.multi_falsified = set()

		self.posterior = False

		self.goalColor = False ## TODO. Hack added 1/18/17 in lieu of termination set.

		self.resource_limits = defaultdict(lambda:1)

		self.errorHistory = []
		self.cumulativeError = 0.

		self.expandedSprites = []
		self.errorMapHistory = []
		self.lineage = []

		self.setOfImaginedEffects = set()
		
		self.experienceReplayRecord = {} ## store (targetColor, rleHistory.ID, len(rleHistory)):penalty
		self.mark = False ## For convenient marking and finding of hypotheses

	## We don't want this to be precomputed because our way of generating child theories
	## is to copy a theory and then change its interactionSet and spriteSet.
	def __hash__(self):
		return hash(sum([r.__hash__() for r in self.interactionSet]) + sum([s.__hash__() for s in self.spriteSet]))

	def copy(self):
		newTheory = Theory(self.game)
		newTheory.spriteSet = [s.copy() for s in self.spriteSet]
		newTheory.classes = {s.className if s.className else 'EOS':[s] for s in newTheory.spriteSet}
		newTheory.spriteObjects = {s.colorName:s for s in newTheory.spriteSet}
		newTheory.expandedSprites = list(self.expandedSprites)
		newTheory.interactionSet = [r.copy() for r in self.interactionSet]
		newTheory.terminationSet = ccopy(self.terminationSet)
		newTheory.dryingPaint = set(self.dryingPaint)
		newTheory.errorMapHistory = list(self.errorMapHistory) # currently unused but useful for debugging.
		newTheory.experienceReplayRecord = ccopy(self.experienceReplayRecord)
		newTheory.falsified = set(self.falsified)
		newTheory.setOfImaginedEffects = set(self.setOfImaginedEffects)
		return newTheory

	def initializeSpriteSet(self, vgdlSpriteParse=False, spriteInductionResult=False):
		if not (vgdlSpriteParse or spriteInductionResult):
			print "You must provide either a vgdlSpriteParse or the result of having performed sprite induction."
			return
		if vgdlSpriteParse:
			self.spriteSet = [s for s in vgdlSpriteParse if s.colorName is not None]
		if spriteInductionResult:
			self.spriteSet = spriteInductionResult

		# End of screen is a special object. Initialize it here.
		eos = Sprite(core.EOS, 'ENDOFSCREEN', 'EOS', None)
		self.spriteSet.append(eos)

		# Get mapping from sprite color to Sprite object
		for s in self.spriteSet:
			self.spriteObjects[s.colorName] = s

	def reconcileInteractionsAndSprites(self):
		## VGDL contains some exceptions to the independence between interactionSet and spriteSet:
		## e.g., teleportation targets are specified in the spriteSet even though teleportation is an interaction.
		## resolve such exceptions here, by passing info from one part to the other as needed.
		for interactionRule in self.interactionSet:
			if 'teleportToExit' in interactionRule.interaction:
				color = self.classes[interactionRule.slot2][0].colorName
				## If we haven't already made this a Portal, take care of the details.
				if self.spriteObjects[color].vgdlType!=Portal:
					self.spriteObjects[color].args = ccopy(interactionRule.args)
					self.spriteObjects[color].vgdlType = Portal
					self.classes[interactionRule.slot2][0] = self.spriteObjects[color]
					for rule in self.interactionSet:
						if rule.slot1==interactionRule.slot1 and 'stype' in interactionRule.args and \
								rule.slot2==interactionRule.args['stype'] and rule!=interactionRule and rule.interaction != 'stepBack':
								rule.interaction = 'nothing'
					interactionRule.args = {}

	def addSpriteToTheory(self, newSpriteName, color, vgdlType='default', args=None):
		if vgdlType=='default':
			vgdlType = ResourcePack
		sprite = Sprite(vgdlType, color, className=newSpriteName, args=args)
		self.classes[newSpriteName] = [sprite]
		self.spriteSet.append(sprite)
		self.spriteObjects[color] = sprite
		for (o1,o2) in itertools.product([newSpriteName], self.classes.keys()):
			rule1 = InteractionRule('stepBack', o1, o2, {}, set(), generic=True)
			rule2 = InteractionRule('stepBack', o2, o1, {}, set(), generic=True)
			self.interactionSet.append(rule1)
			self.interactionSet.append(rule2)
		return

	"""Main functions"""

	def prior(self, granularity=2, ruleWeight=.001):
		## Very simple prior, prefering:
			# Avatar = default type
			# Everything else doesn't move
			# Short non-default ruleset; penalty for rules involving preconditions
			# Penalty for stochastic predicates
			# Preference for explanations involving avatar being the cause of change:
			#	 (penalty for long ruleset is shorter than penalty for type deviations)
		# granularity is how specific we decide to get. note that they build on previous granularities
		#	0: uniform prior
		#	1: L1 norm, essentially. just number of nondefault rules and classes
		# 	2: more specific beliefs about what's more and less "complicated" in a game

		stochasticClasses = ['Chaser', 'RandomNPC']
		stochasticRules = ['flipDirection']
		crazyRules = ['undoAll']

		classScore = 0.
		ruleScore = 0.

		if granularity > 0:
			classScore += sum(1 for c in self.classes if not 'ResourcePack' in str(self.classes[c][0].vgdlType))
			ruleScore += sum(1 if rule.interaction != 'stepBack' else 0 for rule in self.interactionSet)
			# future note: technically, having removed stepBack should increase the ruleScore

		if granularity > 1:
			for c in [cl for cl in self.classes if cl!='EOS']:
				vgdlTypeString = str(self.classes[c][0].vgdlType)
				if 'Avatar' in vgdlTypeString:
					if 'Moving' not in vgdlTypeString:
						classScore += 1
				elif any([t in vgdlTypeString for t in stochasticClasses]):
					classScore += 1.5
				elif not any([t in vgdlTypeString for t in ['Resource','Immovable']]):
					classScore += 1

			ruleScore += sum(1 for rule in self.interactionSet if rule.interaction in stochasticRules + crazyRules)
			# also get all the conditionals
			ruleScore += sum(0.5 for rule in self.interactionSet if 'killIf' in rule.interaction)

		if granularity > 2:
			# maybe take number of args into account or something.
			pass
			# ruleScore += sum(len(rule.args) for rule in self.interactionSet)

		return classScore + ruleScore * ruleWeight

	def colorToClassMapper(self,color):
		for c in self.classes:
			for c_class in self.classes[c]:
				if c_class.colorName == color:
					return c

		raise Exception("No corresponding class found for color")

	def explainTermination(self, timestep, prevTimeSteps,result):
		"""
		adds all hypotheses about the termination conditions to the terminationSet
		params:
		timestep: the very last time step (at which termination occurs)
		prevTimeSteps: all time steps previous to the termination time step
		result: a dictionary for which the key 'win' is a boolean describing whether the game was won
		"""
		win = result['win']
		classesWithDiffAmounts = {} # objects which have different amounts in the termination time step from any previous timestep
		prevClassGameStates = [self.makeGameStateWithClasses(t.gameState['objects']) for t in prevTimeSteps]
		classGameState = self.makeGameStateWithClasses(timestep.gameState['objects'])
		for c in classGameState:
			timestep_amt = classGameState[c]
			timestep_amt_unique = not timestep_amt in [g[c] for g in prevClassGameStates]
			if timestep_amt_unique:
				classesWithDiffAmounts[c] = timestep_amt

		for event in timestep.events:
			for i in [1,2]:
				terminationClassColor = event[i] #self.getClass(event[i])
				terminationClassSymbol = self.colorToClassMapper(terminationClassColor)
				if terminationClassSymbol in classesWithDiffAmounts:
					timestep_amt = classesWithDiffAmounts[terminationClassSymbol]
					spriteCounterRule= SpriteCounterRule(terminationClassSymbol,timestep_amt,win)

					self.terminationSet.add(spriteCounterRule)

		time = result["time"]
		timeoutRule = TimeoutRule(limit=time, win=win)
		self.terminationSet.add(timeoutRule)


	def updateInteractionsPreconditions(self, resource, limit=None):
		if not limit:
			new_precond = Precondition(
			text='new precondition for '+resource,
			item=resource, operator_name='>', num=0)
		else:
			new_precond = Precondition(
			text='new precondition for '+resource,
			item=resource, operator_name='>=', num=limit)

		# Add new generic rules for the avatar with preconditions
		newInteractionRules = []
		nonAvatars = [o for o in self.spriteSet if o.vgdlType not in AvatarTypes and o.colorName!='ENDOFSCREEN']
		for o in nonAvatars:
			rule = InteractionRule('killSprite', o.className, 'avatar', {}, set([new_precond]), generic=True)
			newInteractionRules.append(rule)
		# ipdb.set_trace()

		return newInteractionRules

	def updateTerminations(self, rle=None, ruleSetToUpdate=None):
		if not ruleSetToUpdate:
			ruleSetToUpdate = self.interactionSet

		self.terminationSet = set([t for t in self.terminationSet
							   if t.ruleType=='SpriteCounterRule' and
							   not t.termination.win and t not in self.falsified])

		colors = [tt[0].colorName for tt in self.classes.values() if tt[0].colorName != 'ENDOFSCREEN']
		
		if rle:
			objects = rle._game.observation['trackedObjects']
			absentColors = []
			for color in colors:
				sprites = objects[color] if color in objects else []

				count = len(sprites)
				if count == 0:
					absentColors.append(color)
					## If the game didn't end, you can't win or lose based on this particular class being 0
					done, win = rle._isDone()
					if not done:
						for win in [True, False]:
							false_rule = SpriteCounterRule(self.colorToClassMapper(color), 0, win)
							self.falsified.add(false_rule)
					else:
						# game is done. Hypothesize new theory. Code seems to work without doing this.
						# new_rule = SpriteCounterRule(self.colorToClassMapper(color), 0, win)
						# if new_rule not in self.falsified and new_rule not in self.terminationSet:
						# 	self.terminationSet.add(new_rule)

						## If you won/lost, you can't lose/win based on this class being 0
						false_rule = SpriteCounterRule(self.colorToClassMapper(color), 0, not win)
						self.falsified.add(false_rule)

						if not win:
							## If you lost, maybe you lost because this class was 0. Check whether we'd already falsified this rule.
							loss_terminationRule = SpriteCounterRule(self.colorToClassMapper(color), 0, False)
							if loss_terminationRule not in self.falsified:
								self.terminationSet.add(loss_terminationRule)

			for n in range(2, len(absentColors) + 1):
				for color_combination in itertools.combinations(absentColors, n):

					class_combination = [self.colorToClassMapper(color) for color in color_combination]
					## If the game didn't end, falsify multiSpriteCounter rules for this state.
					done, win = rle._isDone()
					if not done:
						for win in [True, False]:
							new_rule = MultiSpriteCounterRule(stypes=class_combination, win=win)
							self.multi_falsified.add(new_rule)
					else: # game ended
						new_rule = MultiSpriteCounterRule(stypes=class_combination, win=win)
						if new_rule not in self.multi_falsified:
							self.terminationSet.add(new_rule)

						false_rule = MultiSpriteCounterRule(stypes=class_combination, win=not win)
						self.multi_falsified.add(false_rule)

		## Every time we do replay, we store the effects we would have witnessed if that theory had been true
		## For effects we think we've witnessed, we don't need NoveltyRules.
		imaginedEffectTuples = set([(eff[1], eff[2]) for eff in self.setOfImaginedEffects])

		for rule in ruleSetToUpdate:
			if rule.asTuple()[0] in ['stepBack', 'killSprite', 'killIfHasLess', 'killIfHasMore', 'killIfOtherHasLess', 'killIfOtherHasMore', 'transformTo', 'nothing']:
				if rule.generic and rule.preconditions:
					if (rule.slot1, rule.slot2) not in imaginedEffectTuples:
						terminationRule = NoveltyRule(rule.slot1, rule.slot2, True, copy.deepcopy(rule.preconditions))
						if (all([not ((t.termination.s2==rule.slot1) and (t.termination.s1==rule.slot2))
								for t in self.terminationSet if t.ruleType=='NoveltyRule']) and
							all([not terminationRule.__eq__(t) for t in self.terminationSet]) and
							all([not terminationRule.__eq__(t) for t in self.falsified])):
							if (rule.slot1=='c4' and rule.slot2=='avatar') or (rule.slot1=='avatar' and rule.slot2=='c4'):
								print "found avatar c4"
								# embed()
							self.terminationSet.add(terminationRule)
				elif rule.generic and not rule.preconditions:
					if (rule.slot1, rule.slot2) not in imaginedEffectTuples:
						## Omit noveltytermination for randoms bumping into objects in the game; makes us disrupt plans even though we shouldnt't.
						if ('Random' not in str(self.classes[rule.slot1][0].vgdlType)) and ('Random' not in str(self.classes[rule.slot2][0].vgdlType)) or rule.asTuple()[0]!='nothing':
							terminationRule = NoveltyRule(rule.slot1, rule.slot2, True)
							if (all([not ((t.termination.s2==rule.slot1) and (t.termination.s1==rule.slot2))
									for t in self.terminationSet if t.ruleType=='NoveltyRule']) and
								all([not terminationRule.__eq__(t) for t in self.terminationSet]) and
								all([not terminationRule.__eq__(t) for t in self.falsified])):
								if (rule.slot1=='c4' and rule.slot2=='avatar') or (rule.slot1=='avatar' and rule.slot2=='c4'):
									print "found avatar c4"
									# embed()

								self.terminationSet.add(terminationRule)


				# if rule.generic:
				# 	preconditions = copy.deepcopy(rule.preconditions) if rule.preconditions else None
				# 	terminationRule = NoveltyRule(rule.slot1, rule.slot2, True, preconditions)
				# 	if terminationRule not in self.falsified:
				# 		for t in self.terminationSet:
				# 			if t.ruleType != 'NoveltyRule': continue
				# 			if t.termination.s2 != rule.slot1 and t.termination.s1 != rule.slot2:
				# 				break
				# 		else:
				# 			self.terminationSet.add(terminationRule)

				## For things it appears we can kill, add SpriteCounterRules
				elif rule.asTuple()[0] in ['killSprite', 'killIfHasLess', 'killIfHasMore', 'killIfOtherHasLess', 'killIfOtherHasMore', 'transformTo']:
					# terminationRule = SpriteCounterRule(rule.slot1, 0, True)
					# if (all([not terminationRule.__eq__(t) for t in self.terminationSet]) and
						# all([not terminationRule.__eq__(t) for t in self.falsified])):
						# self.terminationSet.add(terminationRule)
					terminationRule = SpriteCounterRule(rule.slot1, 0, True)
					if terminationRule not in self.falsified:
						self.terminationSet.add(terminationRule)

			if rule.slot1!='EOS' and rule.slot2 == 'EOS' and rule.generic:
				terminationRule = NoveltyRule(rule.slot1, rule.slot2, True)
				self.terminationSet.add(terminationRule)

		falsified_win_stypes = set([sprite_rule.termination.stype for sprite_rule in self.falsified
			if (sprite_rule.termination.win and sprite_rule.termination.stype != 'EOS' and sprite_rule.termination.stype !='avatar')])
		
		## ?
		try:
			falsified_win_stypes.remove(self.classes['avatar'][0].args['stype'])
		except:
			pass

		for n in range(2, len(falsified_win_stypes) + 1):
			for sprite_combination in itertools.combinations(falsified_win_stypes, n):
				terminationRule = MultiSpriteCounterRule(stypes=sprite_combination)
				if terminationRule not in self.multi_falsified:
					self.terminationSet.add(terminationRule)

		self.terminationSet = sorted(self.terminationSet, key=lambda t:t.ruleType)

		return self.terminationSet, self.falsified, self.multi_falsified

	def getClassFromColor(self, color):
		for c in self.classes:
			if color in [cl.colorName for cl in self.classes[c]]:
				return c
		return False

	def _stringRules(self, ignore_step_back=True, color_names=False, compare_theory=None):
		string = '\nInteractionSet:'
		for rule in self.interactionSet:
			# if rule.interaction == 'nothing':
				# continue
			if ignore_step_back and rule.interaction == 'stepBack':
				continue
			else:
				rule_name, c1, c2, args = rule.asTuple()
				if color_names:
					rule_tuple = (rule_name, self.classes[c1][0].colorName, self.classes[c2][0].colorName, args)
				else:
					rule_tuple = (rule_name, c1, c2, args)

				rule_string = "%s %s %s %r" % rule_tuple

				if compare_theory:
					note = ""
					if rule not in compare_theory.interactionSet:
						note = "+"
					string += "\n%s\t%s" % (note, rule_string)
				else:
					string += "\n\t%s" % rule_string
		return string

	def displayRules(self):
		print ""
		print "InteractionSet:"
		for rule in self.interactionSet:
			if rule.interaction != 'stepBack':
				rule.display()

	def _stringClasses(self, color_names=False):
		string = "\nClass assignments:"
		for c in self.classes:
			class_list = [cl.colorName for cl in self.classes[c]]
			if color_names:
				c = cl.colorName
			string += "\n\t{}: {}: {}: {}".format(c, class_list, self.spriteObjects[cl.colorName].vgdlType, \
				self.spriteObjects[cl.colorName].args)
		return string

	def displayClasses(self):
		print self._stringClasses()

	def _stringTerminations(self, ignore_novelty_terminations=True, color_names=False):
		string = "\nTerminationSet:"
		for tc in self.terminationSet:
			if ignore_novelty_terminations and tc.ruleType == 'NoveltyRule':
				pass
			else:
				term_tuple = tc.asTuple()
				new_term = []

				for value in term_tuple:
					try:
						if value in self.classes:
							value = self.classes[value][0].colorName
					except TypeError:
						pass
					new_term.append(value)
				tc = tuple(new_term)
				string += "\n\t%s" % str(tc)
		return string

	def displayTerminationSet(self):
		print self._stringTerminations()

	def display(self):
		print self
		return

	def __repr__(self):
		string = "------ Theory ------"
		string += self._stringClasses()
		string += self._stringRules()
		string += self._stringTerminations()
		string += '\n------------------'
		return string

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			interactionSetEqual = set(self.interactionSet) == set(other.interactionSet)
			spriteSetEqual = set(self.spriteSet) == set(other.spriteSet)
			# terminationSetEqual = equalLists(self.terminationSet, other.terminationSet)
			return all([
				spriteSetEqual,
				interactionSetEqual, # TODO: Check if this uses InteractionRule overloaded __eq__
				# terminationSetEqual,
				])
		else:
			return False

	def __ne__(self, other):
		return not self.__eq__(other)

def equalLists(lst1, lst2):
	l1 = [r for r in lst1 if r not in lst2]
	l2 = [r for r in lst2 if r not in lst1]
	if len(l1)+len(l2)==0:
		return True
	else:
		return False

def normalize(array):
	z = float(sum(array))
	if z == 0:
		return [1./len(array)]*len(array) #if all items have the same score of 0, return the same score for all.
	else:
		return [a/z for a in array]

class Game(object):
	"""
	VGDL Game and Induction State.
	"""
	def __init__(self, vgdlString=False, spriteInductionResult=False):

		self.vgdlString = vgdlString
		self.spriteInductionResult = spriteInductionResult
		if self.vgdlString:
			self.vgdlSpriteParse = self.makeSpriteParse()
		else:
			self.vgdlSpriteParse = False

		# Induction states
		self.hypothesisSpace = []
		self.theoryCount = 0

		#inherit ontology from VGDL
		self.VGDLTree = VGDLTree

		self.nodes_generated = 0
		self.nodes_eliminated = 0
		self.nodes_accepted = 0

	def display(self):
		print self.theoryCount

	def makeSpriteParse(self):
		s = SpriteParser()
		return s.parseGame(self.vgdlString)

	def buildGenericTheory(self, spriteSample=True, vgdlSpriteParse=False, learnAvatar=True):

		T = Theory(self)

		if spriteSample:
			T.initializeSpriteSet(vgdlSpriteParse=False, spriteInductionResult=spriteSample)
		else:
			T.initializeSpriteSet(vgdlSpriteParse = vgdlSpriteParse, spriteInductionResult=False)

		# Assign class names
		avatars = [o for o in T.spriteSet if o.vgdlType in AvatarTypes]
		nonAvatars = [o for o in T.spriteSet if o.vgdlType not in AvatarTypes and o.colorName!='ENDOFSCREEN']
		allSprites = avatars+nonAvatars
		eos = [o for o in T.spriteSet if o.colorName=='ENDOFSCREEN'][0]

		if not learnAvatar:
			avatar.className = 'avatar'
			T.classes[avatar.className] = [avatar]

			projectileName = ''
			try:
				projectileName = avatar.args['stype']
			except (TypeError, KeyError) as e:
				pass

			projectileTypes = [Flicker, OrientedFlicker, Missile]
			for i in range(len(nonAvatars)):
				if projectileName == nonAvatars[i].className:
					nonAvatars[i].className = projectileName
				else:
					nonAvatars[i].className = 'c'+str(i+2)

				T.classes[nonAvatars[i].className] = [nonAvatars[i]]
		else:
			for i in range(len(allSprites)):
				allSprites[i].className = 'c'+str(i+2)
				T.classes[allSprites[i].className] = [allSprites[i]]

		T.classes['EOS'] = [eos] ##initialize EOS with special name, since it gets such special treatment in VGDL text files.

		for (o1, o2) in itertools.product(allSprites, allSprites):

			## Default hypothesis that avatar can kill everything but that everything else is 'nothing'
			# if o1.vgdlType not in AvatarTypes and o2.vgdlType not in AvatarTypes:
			# 	rule = InteractionRule('nothing', o1.className, o2.className, {}, set(), generic=True)
			# 	T.interactionSet.append(rule)
			# elif o1.vgdlType not in AvatarTypes:
			# 	rule = InteractionRule('killSprite', o1.className, o2.className, {}, set(), generic=True)
			# 	T.interactionSet.append(rule)

			## Default hypothesis that everything is stepBack
			rule = InteractionRule('stepBack', o1.className, o2.className, {}, set(), generic=True)
			T.interactionSet.append(rule)

		for s1 in nonAvatars + avatars:
			## append EOS rule
			rule = InteractionRule('stepBack', s1.className, 'EOS', {}, set(), generic=True)
			T.interactionSet.append(rule)

		rule =  SpriteCounterRule("avatar", 0, False)
		T.terminationSet.add(rule)

		T.updateTerminations()
		return T



def generateTheoryFromGame(rle, alterGoal=False):
	"""
	Given an rle, returns a very barebones theory object.
	This object has only 2 fields set: the interaction set, and the classes.
	"""
	theory = Theory(rle._game)

	inverseClasses = dict()
	for i,s in enumerate(rle._game.sprite_constr):
		(vgdlType, settings, _) = rle._game.sprite_constr[s]
		# Handle objects for which color is not declared
		# Should probably be done in a cleaner way when testing agent.py
		# since we suppose a 1:1 mapping from colors to objects
		try:
			color = colorDict[str(settings['color'])]
		except KeyError:
			color = 'noColor'

		if alterGoal and s=='goal':
			s = s[::-1] #reverse string. goal is to change names so as to not confuse anything with actual goal once you set it.
						# 'goal' is the only name that means something to all RLEs, so we're making sure to change this one.
		sprite = Sprite(vgdlType, color, className=s, args=settings) #classname was i
		theory.classes[s] = [sprite]
		theory.spriteObjects[sprite.colorName] = sprite
		theory.spriteSet.append(sprite)
		inverseClasses[s] = i

	## Add EOS as a class, too.
	eos = Sprite(core.VGDLSprite, 'ENDOFSCREEN', None, None)
	theory.classes['EOS'] = [eos]
	theory.spriteObjects[eos.colorName] = eos
	theory.spriteSet.append(eos)

	for g1, g2, effect, kwargs in rle._game.collision_eff:
		if alterGoal:
			if g1=='goal':
				g1 = g1[::-1]
			if g2=='goal':
				g2 = g2[::-1]
		interaction = InteractionRule(effect.__name__, g1, g2, kwargs)
		theory.interactionSet.append(interaction)

	# Add termnation set
	for termination in rle._game.terminations:
		# No support for MultiSpriteCounterRule yet
		# Checking type with 'hasattr': ugly but isinstance breaks due to
		# relative imports
		if termination.name == 'SpriteCounter':
			if alterGoal and termination.stype=='goal':
				termination.stype='laog'
			spritecounter = SpriteCounterRule(limit=termination.limit,
											  stype=termination.stype,
											  win=termination.win)
			theory.terminationSet.add(spritecounter)
		elif termination.name == 'MultiSpriteCounter':
			if alterGoal:
				termination.stypes = ['laog' if t=='goal' else t for t in termination.stypes]
			multiSpriteCounter = MultiSpriteCounterRule(limit=termination.limit,
											  stypes=termination.stypes,
											  win=termination.win)
			theory.terminationSet.add(multiSpriteCounter)
		elif termination.name == 'Timeout':
			timeout = TimeoutRule(limit=termination.limit,
								  win=termination.win)
			theory.terminationSet.add(timeout)
		elif termination.name == 'NoveltyRule':
			noveltyrule = NoveltyRule(s1=termination.s1, s2=termination.s2, win=termination.win)
			theory.terminationSet.add(noveltyrule)

	return theory

def generateSymbolDict(rle):
	## run this once at the beginning of each game.
	## if new objects appear that are of an unknown type we have to be able to deal with this; writeTheoryToTxt should be
	## able to append to this dict if it finds any unknown objects.
	inverseMapping = dict()

	idx = 0
	try:
		colors = [colorDict[str(rle._game.sprite_constr[k][1]['color'])] for k in rle._obstypes.keys()]
	except:
		print "problem with generateSymbolDict"
		embed()
	## Note: this is not privileged info about the avatar; it's just grabbing the possible visible colors in the game.
	try:
		colors.append(colorDict[str(rle._game.sprite_constr['avatar'][1]['color'])])
	except:
		colors.append(colorDict[str(rle._game.sprite_constr['avatar'][0].color)])
	possibilities = list(set([c for c in colors]))

	for p in possibilities:
		inverseMapping[p] = ALNUM[idx]
		idx+=1

	return inverseMapping


## TODO: check and complete list of predicates
# predicates = 
# ['attractGaze','bounceForward', 'bounceDirection', 'changeResource', 
# 'changeScore', 'killSprite', 'killIfHasMore', 'killIfHasLess', 
# 'killOtherHasMore', 'killOtherHasLess' 'killIfSlow', 'nothing', 
# 'spawnIfHasMore', 'transformTo', 'transformToOnLanding', 'triggerOnLanding', 
# 'slipForward', 'wallBounce', 'wrapAround']

def getKeywordsFromOntology(interactionName):
	ontologyKeywordDict = \
	{'changeResource': ['resource', 'value', 'limit'],\
	'changeScore': ['value'],\
	'transformTo': ['stype'],\
	'teleportToExit': ['stype'],\
	'killIfSlow': ['limitspeed'],\
	'killIfTooFast': ['speed'],\
	'killIfHasMore': ['resource', 'limit'],\
	'killIfOtherHasMore': ['resource', 'limit'],\
	'killIfHasLess': ['resource', 'limit'],\
	'killIfOtherHasLess': ['resource', 'limit'],\

	 ##TODO: Fill in proposeArgs for the following keywords.
	'spawnIfHasMore': ['resource', 'stype', 'limit'],\
	'wallStop': ['friction'],\
	'wallBounce': ['friction'],\
	'slipForward': ['prob'],\
	'attractGaze': ['prob'],\
	'bounceDirection': ['friction']
	# 'reverseFloeIfActivated': ['strigger'],\
	# 'trigger': ['strigger'],\
	# 'detrigger': ['strigger'],\
	# 'transformToOnLanding': ['stype'],\
	# 'triggerOnLanding': ['strigger'],\
	}
	if interactionName in ontologyKeywordDict.keys():
		return ontologyKeywordDict[interactionName]
	else:
		return []


thresholdOrdering = {\
	'killIfHasLess': 		range(-2,11),
	'killIfHasMore': 		range(-2,11),
	'killIfOtherHasLess': 	range(-2,11),
	'killIfOtherHasMore': 	range(-2,11),
	'killIfTooFast': 		range(-5,100,5),
	'killIfSlow': 			range(-5,100,5)
}


def proposeArgs(theory, predicate, errorMap, observations, generic=False):

	## if generic==False, this will propose all args given what's in resourceObservations
	## which is the result of a function responsible for tracking possible resources, speeds, etc.

	## if generic==True, it will just generate all possible args given some hypothesis space.
	## For a predicate like changeResource this will result in a large number of args.

	args = getKeywordsFromOntology(predicate)
	argList = []
	if not args:
		return [{}]
	else:
		if not generic:
			if predicate == 'changeResource':
				resources = observations['trackedObjects'][errorMap.targetToken.colorName][0].inventory
				diffs =  observations['trackedObjects'][errorMap.targetToken.colorName][0].inventoryDiff()
				for resource, val in diffs.items():
					if resource in resources.keys():
						limit = resources[resource][1]
					else:
						limit = observations['trackedObjects'][errorMap.targetToken.colorName][0].lastinventory[resource][1]
					resourceClass = theory.spriteObjects[resource].className
					argList.append({'resource':resourceClass, 'value': val, 'limit':limit})
			elif predicate == 'changeScore':
				if observations['score']<observations['lastscore']:
					print "got negative score in proposeArgs()"
					embed()
				argList.append({'value':observations['score']-observations['lastscore']})
			elif predicate == 'killIfSlow':
				values = [0]
				for val in values:
					argList.append({'limitspeed':val})
			elif predicate == 'killIfTooFast':
				values = [0]
				for val in values:
					argList.append({'speed':val})
			elif predicate in ['killIfHasMore', 'killIfHasLess', 'killIfOtherHasMore', 'killIfOtherHasLess']:
				try:
					if observations['trackedObjects'][theory.classes['avatar'][0]]:
						resources = [theory.spriteObjects[rcolor].className for rcolor in observations['trackedObjects'][theory.classes['avatar'][0].colorName][0].inventory.keys()]
					else:
						resources = [c for c in theory.classes if 'Resource' in str(theory.classes[c][0].vgdlType) and 'ResourcePack' not in str(theory.classes[c][0].vgdlType)]
				except:
					print "problem with resources in proposeArgs()", " ...or the avatar died"
					embed()
				limits = [-2]
				for comb in list(itertools.product(resources, limits)):
					if comb:
						argList.append({'resource':comb[0], 'limit':comb[1]})
			elif predicate == 'transformTo':
				for stype in [k for k in theory.classes.keys() if k not in ['avatar', 'EOS']]:
					argList.append({'stype':stype})
			elif predicate == 'teleportToExit':
				for stype in [k for k in theory.classes.keys() if k not in ['avatar', 'EOS']]:
					argList.append({'stype':stype})
			else:
				print "Error: Have not implemented non-generic proposeArgs() yet."
				embed()
		else:
			if predicate=='changeResource':
				resources = [k for k in theory.classes.keys() if k not in ['avatar', 'EOS']]
				values = [1]
				limits = [1,3]
				for comb in list(itertools.product(resources, values, limits)):
					argList.append({'resource':comb[0], 'value':comb[1], 'limit':comb[2]})
			if predicate == 'changeScore':
				values = [1]
				for val in values:
					argList.append({'value':val})
			if predicate == 'transformTo':
				for stype in [k for k in theory.classes.keys() if k not in ['avatar', 'EOS']]:
					argList.append({'stype':stype})
			if predicate == 'teleportToExit':
				for stype in [k for k in theory.classes.keys() if k not in ['avatar', 'EOS']]:
					argList.append({'stype':stype})
			if predicate == 'killIfSlow':
				values = [1,2,3]
				for val in values:
					argList.append({'limitspeed':val})
			if predicate == 'killIfTooFast':
				values = [10,11,12]
				for val in values:
					argList.append({'speed':val})
			if predicate in ['killIfHasMore', 'killIfHasLess', 'killIfOtherHasMore', 'killIfOtherHasLess']:
				resources = [k for k in theory.classes.keys() if k not in ['avatar', 'EOS']]
				limits = [1,2]
				for comb in list(itertools.product(resources, limits)):
					argList.append({'resource':comb[0], 'limit':comb[1]})
		## TODO: Fill in the other resources
	return argList


def proposePredicates(singlePairErrorSignal, observations):
	## Takes the error signal and proposes the appropriate predicates by looking
	## at the memory. For now it would only access the memory to make new proposals
	## that build on previous ones (e.g., incrementing n, or going to conditional kill
	## events if non-conditional kill events have already been proposed)
	## NOTE: if more predicates are added whose effects are not immediately observable by the
	##  "CV system" (like flipDirection), make sure to add them to the list in stateobsnonstatic!

	predicates = []

	physicsType = 'gridphysics' if observations['isGrid'] else 'continuousphysics'
	## List of predicates that are unique to a physics type
	physicsToPredicateMapping = {
	'all' : 					['killSprite', 'cloneSprite', 'transformTo', 'transformToOnLanding',\
								'killIfHasLess', 'killIfHasMore', 'killIfOtherHasLess', 'killIfOtherHasMore',\
								'killIfTooFast', 'killIfSlow',\
								'undoAll', 'nothing',\
								'turn', 'turnAround', 'reverseDirection', 'wrapAround', 'flipDirection', 'bounceForward',\
								'changeResource', 'collectResource', 'changeScore', 'teleportToExit', 'conveySprite'],
	'gridphysics': 				[],
	'continuousphysics': 		['transformToOnLanding', 'killIfTooFast', 'killIfSlow', 'killIfFromAbove',\
								'killIfFromBelow', 'bounceDirection', 'flipDirection', 'conveySprite', 'pullWithIt',\
								'windGust','slipForward', 'wallBounce', 'wallStop','onRope', 'onLadder']
								}

	errorSignalToPredicateMapping = {

	## Destruction/appearance/transformation
	'objectDestruction': 		['killSprite'],
	'newObjectAppeared': 		[],	#'cloneSprite'
	'transformation': 			['transformTo'],
	'conditionalKill': 			['killIfHasLess', 'killIfHasMore', 'killIfOtherHasLess', 'killIfOtherHasMore'],
								 # 'killIfTooFast', 'killIfSlow', 'killIfFromAbove', 'killIfFromBelow'],

	## Position difference
	## NOTE: if you propose undoAll you also need to uncomment the lines that propose intPairs between any adjacent sprites
			# on the board in errorSignal()
	'noMovement': 				[],#['undoAll'], ## Possible bug: not proposing anything for noMovement
	'unexpectedPosition': 		['bounceForward', 'nothing'],
									# , 'pullWithIt', 'windGust', 'slipForward',\
									# 'wallBounce', 'wallStop'], #real sprite moves and doesn't overlap
	'unexpectedOverlap':		['nothing', 'reverseDirection'],#, 'onRope', 'onLadder'], #real sprite moved and now overlaps with another
	'orientationChange': 		['flipDirection'], #'reverseDirection', 
									#'turn', 'turnAround', 
	'wrapAround':				['wrapAround'], # no offsets
	'teleport': 				['teleportToExit'],

	## Object state change
	'inventoryChange': 			['changeResource'], #collectResource
	'scoreChange':				['changeScore'],
	## Other
	## TODO: These don't actually belong here, but we need to do more work to be able to learn these.
	'other' : 					[] #'conveySprite'
								}

	## Propose relevant rules
	##TODO: right now this just gets the list from a single key
	for predicate in singlePairErrorSignal:
		predicates.extend(errorSignalToPredicateMapping[predicate])

	## Filter out rules that aren't consistent with the known physics type
	predicates = [p for p in predicates if p in physicsToPredicateMapping['all'] or 
		p in physicsToPredicateMapping[physicsType]]

	## TODO: Fill out the case where you consult the proposalMemory to make more complicated
	## proposals

	return list(set(predicates))

## TODO: write the function that maintains resourceObservations, or at least figure out
## its outputs and integrate with proposeArgs
def expandSprites(game, theory, errorMap, envRealPrev, envRealCurrent, action=None, percentile=20, max_num=20):
	from vgdl.ontology import spriteInduction

	if max_num is None:
		max_num = 100000
	childTheories = []

	targetClass = errorMap.targetClass
	targetToken = errorMap.targetToken

	theory.expandedSprites.append(targetClass)
	
	## Only propose sprites when something moves that we didn't think was going to move.
	## Possible bug: removed noMovement
	if all([diagnosis not in ['unexpectedPosition', 'unexpectedOverlap', 'newObjectAppeared',
		'orientationChange', 'unexpectedOverlap', 'objectDestruction', 'noMovement'] for diagnosis in errorMap.diagnosis]):
		return targetClass, childTheories

	if 'objectDestruction' in errorMap.diagnosis:
		spriteProposals = [k for k in game.spriteDistribution[targetToken.ID].keys() if 'Flicker' in str(k[0][1])]
	else:
		spriteProposals = spriteInduction(game, step=4, action=action,specificSpritesToUpdate=errorMap.targetTokens)

	## Don't instantiate non-avatar proposals for the 'avatar' class.
	if targetClass=='avatar':
		spriteProposals = [s for s in spriteProposals if 'Avatar' in str(s[0][1])]
	
	for spriteProposal in spriteProposals:

		newTheory = theory.copy()
		newTheory.mostRecentEdit = 'spriteInduction'
		e = errorMap.copy()
		e.componentsAddressed = 'spriteInduction'
		newTheory.errorMapHistory.append(e)
		vgdlType = spriteProposal[0][1]
		args = dict(spriteProposal[1:])

		## Proposal specified args in terms of color; convert to class name for the actual theory.
		if 'stype' in args.keys():
			try:
				if args['stype'] not in newTheory.spriteObjects:
					return targetClass, []
				args['stype'] = newTheory.spriteObjects[args['stype']].className
			except:
				print "got new stype as an arg but the theory doesn't have the object. In expandSprites()"
				embed()
		color = newTheory.classes[targetClass][0].colorName
		## If you're proposing an avatar change you need to do some bookkeeping to ensure only one avatar class in the description.
		if 'Avatar' in str(vgdlType):

			## Avatar can't shoot avatar.
			if 'stype' in args.keys() and args['stype'] == 'avatar':
				continue
			sprite = Sprite(vgdlType, color, className='avatar', args=args)
			tmpType = newTheory.classes[targetClass][0].vgdlType
			tmpSprite = newTheory.classes['avatar'][0]
			tmpSprite.vgdlType = tmpType
			tmpSprite.className=targetClass
			tmpSprite.args = {}
			## If the old class was also an avatar we want to use the new sprite for everything, so doing that step second, always.
			newTheory.classes[targetClass] = [tmpSprite]
			newTheory.classes['avatar'] = [sprite]
			newTheory.spriteObjects[tmpSprite.colorName] = tmpSprite
			newTheory.spriteObjects[sprite.colorName] = sprite
			newTheory.spriteSet = [item for sublist in newTheory.classes.values() for item in sublist]
			for rule in newTheory.interactionSet:
				if rule.slot1==targetClass:
					rule.slot1='tmp'
				if rule.slot2==targetClass:
					rule.slot2='tmp'
				if rule.slot1=='avatar':
					rule.slot1=targetClass
				if rule.slot2=='avatar':
					rule.slot2=targetClass
				if rule.slot1=='tmp':
					rule.slot1='avatar'
				if rule.slot2=='tmp':
					rule.slot2='avatar'
		else:
			## Don't propose non-avatar types for the thing you're calling 'avatar'.
			if targetClass=='avatar':
				continue
			sprite = Sprite(vgdlType, color, className=targetClass, args=args)
			## Remove old sprite from spriteSet
			newTheory.spriteSet.remove(newTheory.classes[targetClass][0])
			## Add new sprite
			newTheory.spriteSet.append(sprite)
			newTheory.classes[targetClass] = [sprite]
			newTheory.spriteObjects[color] = sprite
		
		childTheories.append(newTheory)

	## TODO: what to do with orientation for missiles??
	return targetClass, childTheories

predicateToOrderingMapping = {
	'killSprite':			(0,),
	'killIfHasLess': 		(0,), 
	'killIfHasMore': 		(0,),
	'killIfOtherHasLess': 	(0,), 
	'killIfOtherHasMore':	(0,),
	'killIfTooFast':		(0,),
	'killIfSlow':			(0,),
	'killIfFromAbove':		(0,),
	'killIfFromBelow':		(0,),
	'changeResource':		(0,),
	'collectResource':		(1,),
	'stepBack':				(0,),
	'cloneSprite':	 		(0,),
	'transformTo':	 		(0,),
	'transformToOnLanding': (0,),
	'turn':					(0,),
	'turnAround':			(0,),
	'reverseDirection':		(0,),
	'flipDirection':		(0,),
	'wrapAround':			(0,),
 	'teleportToExit':		(0,),
 	'conveySprite':			(0,),
	'windGust':				(0,),
	'bounceDirection':		(0,), 
	'pullWithIt':			(0,),
	'slipForward':			(0,),
	'attractGaze':			(0,),
	'wallBounce':			(0,),
	'wallStop':				(0,),
	'onRope':				(0,),
	'onLadder':				(0,),
	'nothing':				(0,),
	'bounceForward':		(0,),
 	'changeScore':			(0,1),
	'undoAll':				(0,1)}

predicatesThatConflictWithStepBack = ['nothing', 'transformTo', 'teleportToExit', 'wrapAround', 'reverseDirection', 'killIfHasLess', 'killIfHasMore']

def getRuleSetsForClassPairPredicate(classPair, predicates, theory, errorMap, observations, classPairPlusPredicateToRuleSets, n):

	## If generating rulesets for n>1, don't generate combinations of the below for a particular classPair
	conflictingPredicates = ['killIfHasMore', 'killIfHasLess', 'killIfOtherHasMore', 'killIfOtherHasLess']

	key = (classPair, tuple(sorted(predicates)))

	if key not in classPairPlusPredicateToRuleSets:

		predicateGroups = []
		for i in range(0,n+1):
			predicateGroups.extend(list(itertools.combinations(predicates, i)))

		bothOrderings = [[()], [()]]
		for i,order in enumerate([classPair, (classPair[1], classPair[0])]):

			for predicateGroup in predicateGroups:
				if len(predicateGroup)==0:
					pass
				predicateRules = []
				for predicate in predicateGroup:
					if n>1 and len(([p for p in predicateGroup if p in conflictingPredicates]))>1:
						continue
					# if n>1:
						# print "in getRuleSetsForClassPairPredicate"
						# embed()
					## orderings are (targetClass, neighbor). If the ordering we're proposing is consistent with the semantics
					## of the predicate we're proposing, add this potential rule.
					if i in predicateToOrderingMapping[predicate]:
						allArgumentCombinations = proposeArgs(theory, predicate, errorMap, observations, 
							generic=False)
						predicateRules.append([InteractionRule(predicate, order[0], order[1], args=comb) 
							for comb in allArgumentCombinations])
				if predicateRules:
					bothOrderings[i].extend(list(itertools.product(*predicateRules)))
		## Now generate combinations from each expanded predicateGroup that we added to each of the orderings
		newRuleSets = list(itertools.product(bothOrderings[0], bothOrderings[1]))
		newRuleSets = [[item for sublist in ruleSet for item in sublist] for ruleSet in newRuleSets]

		classPairPlusPredicateToRuleSets[key] = newRuleSets

	return classPairPlusPredicateToRuleSets[key]

def expandLine(theory, errorMap, classPair, predicates, classPairPlusPredicateToRuleSets, envRealPrev, envRealCurrent, action, rleHistories, actionHistories, MultiEpisodeExperienceReplay, n=1, observations=None, generic=False):
	## Modifies the theory to propose n new interactonRules involving the given classPair
	## For predicates that take arguments, finds the first (according to some ordering) satisfying argument and returns that.
	## generic=True proposes all possible combinations of args instead.
	childTheories = [theory.copy()]
	##if iterating thresholds is not relevant:
	predicatesWithThresholds = ['killIfTooFast', 'killIfSlow', 'killIfHasMore', 'killIfHasLess', 'killIfOtherHasMore', 'killIfOtherHasLess']
	relevantRulesWithArgs = [rule for rule in theory.interactionSet if rule.interaction in predicatesWithThresholds and 
			classPair[0] in rule.asTuple() and classPair[1] in rule.asTuple() and len(rule.args)>0]

	# if 'changeResource' in predicates:
		# print "got changeResource"
		# embed()
	if len(relevantRulesWithArgs) == 0:
		if 'conditionalKill' in errorMap.diagnosis:
			# print "got conditionalKill"
			# embed()
			## The only rules that should be removed when proposing conditionals are kill rules.
			## Remove the existing kill rules and replace them with conditionals.
			toRemove = [rule for rule in theory.interactionSet if classPair[0] in rule.asTuple() and classPair[1] in rule.asTuple() and 
					rule.asTuple()[1] == errorMap.targetClass and rule.asTuple()[0]=='killSprite']
			theory.interactionSet = [rule for rule in theory.interactionSet if rule not in toRemove]

			## changeResource and conditional kills make things a bit more complex; need to propose more complicated theories
			if 'changeResource' in predicates:
				n=2

		# if 'inventoryChange' in errorMap.diagnosis:
			# print "got inventory change in expandLine"
			# embed()

		## TODO: Modify getRuleSets... to only return combinations that have one changeResource and one killIf... (if n==2)
		## TODO: Modify iterateThresholds to only modify dryingPaint
		newRuleSets = getRuleSetsForClassPairPredicate(classPair, predicates, theory, errorMap, observations, classPairPlusPredicateToRuleSets, n)
		for i,ruleSet in enumerate(newRuleSets):
			if len(ruleSet) > 0:
				newTheory = theory.copy()
				newTheory.mostRecentEdit = 'interactionSetInduction'
				e = errorMap.copy()
				e.componentsAddressed = 'interactionSetInduction'
				newTheory.errorMapHistory.append(e)
				# remove old rules that conflict with the new ones
				alteredPairs = set([(rule.slot1, rule.slot2) for rule in ruleSet if rule.interaction in predicatesThatConflictWithStepBack] + \
						[(rule.slot2, rule.slot1) for rule in ruleSet if rule.interaction in predicatesThatConflictWithStepBack])
				newTheory.interactionSet = [rule for rule in newTheory.interactionSet if 'stepBack' != rule.interaction or (rule.slot1, rule.slot2) not in alteredPairs]
				for rule in ruleSet:
					ruleCopy = rule.copy()
					newTheory.interactionSet.append(ruleCopy)
					newTheory.dryingPaint.add(ruleCopy)
				newTheory.reconcileInteractionsAndSprites()
				childTheories.append(newTheory)

		childTheories = list(set(childTheories))
	
	## Iterate thresholds. If this is not relevant for a particular theory, iterateThresholds() will just return the theory unchanged.
	iteratedTheories = []
	for theory in childTheories:
		iteratedTheories.append(interateThresholds(envRealPrev, envRealCurrent, action, rleHistories, actionHistories, theory, errorMap, classPair, MultiEpisodeExperienceReplay))

	return classPair, iteratedTheories

def interateThresholds(envRealPrev, envRealCurrent, action, rleHistories, actionHistories, theory, errorMap, classPair, MultiEpisodeExperienceReplay):
	
	predicatesWithThresholds = ['killIfTooFast', 'killIfSlow', 'killIfHasMore', 'killIfHasLess', 'killIfOtherHasMore', 'killIfOtherHasLess']
	## used to be interactionSet
	relevantRulesWithArgs = [rule for rule in list(theory.dryingPaint) if rule.interaction in predicatesWithThresholds and \
			classPair[0] in rule.asTuple() and classPair[1] in rule.asTuple() and len(rule.args)>0]
	if len(relevantRulesWithArgs)==1:
		# print "in iterateThresholds"
		# theory.display()
		rule = relevantRulesWithArgs[0]
		penalty,_ = MultiEpisodeExperienceReplay([theory], rleHistories, actionHistories, 
			method='all', targetColor=errorMap.targetColor)[0]
		newPenalty = penalty
		while newPenalty >= penalty:
			argsToIncrement = [(k,v) for k,v in relevantRulesWithArgs[0].args.items() if type(v)==int]
			if len(argsToIncrement)>1:
				print "got more than one arg to increment in iterateThresholds(); this shouldn't happen"
				embed()
			k,v = argsToIncrement[0]
			idx = thresholdOrdering[rule.interaction].index(v)
			if len(thresholdOrdering[rule.interaction]) > idx+1:
				rule.args[k] = thresholdOrdering[rule.interaction][idx+1]
				theory.experienceReplayRecord = {}
				newPenalty,_ = MultiEpisodeExperienceReplay([theory], rleHistories, actionHistories, 
					method='all', targetColor=errorMap.targetColor)[0]
				# print newPenalty, rule.display()
			else:
				break

	if len(relevantRulesWithArgs)>1:
		print "you got more than 1 relevant rule with an argument in iterateThresholds; this shouldn't happen"
		embed()

	return theory

def getClassNameFromSpriteString(spriteName, theory, rle):
	if spriteName in rle._game.sprite_groups and len(rle._game.sprite_groups[spriteName])>0:
		col = colorDict[str(rle._game.sprite_groups[spriteName][0].color)]
		try:
			className = [k for k in theory.classes.keys() if col in [c.colorName for c in theory.classes[k]]][0]
		except:
			print "couldn't find className"
			embed()
		return className
	elif spriteName in theory.classes.keys():
		return spriteName
	else:
		try:
			## maybe we passed a color, so we should get the class.
			return theory.spriteObjects[spriteName].className
		except:
			print "failed to get spriteName color. In getClassNameFromSpriteString"
			embed()

def buildArgsString(interactionRule, theory, rle):
	relevantArgNames = getKeywordsFromOntology(interactionRule.interaction)
	newInteractionName = interactionRule.interaction
	if interactionRule.interaction =='killSprite':
		oppositeOperatorMap = {"<=": ">", ">=": "<", "<": ">=", ">": "<="}
		precondition = list(set(interactionRule.preconditions))[0]
		if precondition:
			print "in precondition in buildArgsString"
			## We should never be here; this is deprecated.
			embed()
			if precondition.negated:
				true_operator = oppositeOperatorMap[precondition.operator_name]
			else:
				true_operator = precondition.operator_name

			if precondition.item=='speed':
				newInteractionName = 'killIfTooFast'
				limit = precondition.num
				argsString = " speed=%s"%(str(limit))
			else:
				if true_operator in {"<", "<="}:
					newInteractionName = 'killIfHasLess' #example
					if true_operator == "<":
						limit = precondition.num - 1
					else:
						limit = precondition.num

				elif true_operator in {">", ">="}:
					newInteractionName = 'killIfOtherHasMore'
					if true_operator == ">":
						limit = precondition.num + 1
					else:
						limit = precondition.num

				argsString = " resource=%s limit=%s"%(precondition.item, str(limit))
	elif interactionRule.interaction=='teleportToExit':
		print "implement teleportToExit argsstring"
		embed()
		argsString = ""
	elif interactionRule.interaction in ['killIfFromAbove', 'killIfFromBelow']:
		print "implement killIfFromAbove argsstring"
		embed()
		argsString = ""
	elif interactionRule.interaction == 'killIfTooFast':
		argsString = ""
		argsString += " speed=%s"%(interactionRule.args['speed'])
	elif interactionRule.interaction == 'changeResource':
		argsString = ""
		argsString += " resource=%s value=%s"%(interactionRule.args['resource'], interactionRule.args['value'])
	else:
		if interactionRule.args:
			argsString = ""
			for k,v in interactionRule.args.items():
				if k in ['stype', 'strigger']:
					argsString += " %s=%s"%(k, getClassNameFromSpriteString(v, theory, rle))
				else:
					argsString += " %s=%s"%(k, v)
		else:
			print "buildArgsString got called but no precondition"
			embed()

	return argsString, newInteractionName


def writeTheoryToTxt(rle, theory, txtFile, writeFile=False, debug=False, goalLoc = None, addAllObjects=False):
	"""
	-need to be able to take an optional argument that tells you the location of the goal, and put that into the level string
	-assume that the goal sprite is getting killed
	-change the actual goal to be something else
	2 ways of swapping in knowledge:
	-cleanest way:
	"""

	symbolDict = rle.symbolDict
	DIRECTION_MAP = {(0,-1):'UP', (0,1):'DOWN', (1,0):'RIGHT', (-1,0):'LEFT'}

	_obstypes = rle._obstypes
	newGoalType, newGoalColor= None, None

	colorToSprite = {}

	for spriteType in rle._game.sprite_constr:
		if spriteType != "avatar":
			try:
				colorToSprite[colorDict[str(rle._game.sprite_constr[spriteType][1]['color'])]] = spriteType
			except KeyError:
				print "in writeTheoryToTxt, keyError"
				embed()

	if goalLoc:
		newGoalCode = state[goalLoc[0]][goalLoc[1]]
		if newGoalCode == 0:
			newGoalType = 'blank_space'
		else:
			newGoalIndex = int(round(math.log(newGoalCode,2)))-1
			newGoalType = sorted(_obstypes.keys())[::-1][newGoalIndex]
			newGoalColor = colorDict[str(rle._game.sprite_constr[newGoalType][1]['color'])]

	## teleport sprites have to be handled separately, as the spriteType is relational -- it depends on
	## what is in the interactionRules.
	if theory.interactionSet[0].args is not None:
		if any([len(i.args.keys()) for i in theory.interactionSet]):
			for interactionRule in theory.interactionSet:
				if interactionRule.interaction == 'teleportToExit':
					## second element in teleport tuple is the entrance; stype is the exit
					portalEntry = interactionRule.slot2
					portalExit = getClassNameFromSpriteString(interactionRule.args['stype'], theory, rle)

					theory.classes[portalEntry][0].vgdlType = Portal
					if theory.classes[portalEntry][0].args is None:
						theory.classes[portalEntry][0].args = {'stype':portalExit}
					else:
						theory.classes[portalEntry][0].args['stype'] = portalExit

					theory.classes[portalExit][0].vgdlType = Portal

	########### generating theory string
	theoryString = 'game = """\n'
	theoryString += "BasicGame\n"
	# first phase: the sprite rules
	theoryString += "\tSpriteSet\n"


	for c, sprites in theory.classes.items():
		if c == 'EOS':
			pass
		else:
			for s in sprites:
				unfilteredType = str(s.vgdlType)
				stype = unfilteredType[unfilteredType.find("vgdl.ontology.")+len("vgdl.ontology."): unfilteredType.find(">")-1]
				argsString = ""
				## Catch-all 'OTHER' s.vgdlType is causing a problem. replace for now with generic.
				if not stype:
					if unfilteredType == "OTHER":
						stype = 'ResourcePack'
					else:
						print "writetheorytotxt. stype problem"
						embed()

				if s.args:
					for k,v in s.args.items():
						if k == "color":
							continue
						elif k == "orientation":
							argsString += " %s=%s"%(k, DIRECTION_MAP[v])
						elif k == "speed":
							argsString += " %s=%s"%(k, v)
						else:
							argsString += " %s=%s"%(k, str(v))

				try:
					argsString += " %s=%s"%("speed", str(s.speed))
				except AttributeError:
					pass

				try:
					argsString += " %s=%s"%("orientation", DIRECTION_MAP[s.orientation])
				except AttributeError:
					pass

				try:
					argsString += " %s=%s"%("fleeing", s.fleeing)
				except AttributeError:
					pass

				try:
					argsString += " %s=%s"%("cooldown", s.cooldown)
				except AttributeError:
					pass

				try:
					argsString += " %s=%s"%("spawnCooldown", s.spawnCooldown)
				except AttributeError:
					pass

				if hasattr(s, 'stype'):
					try:
						##when we initialized stypes in spriteInduction, we didn't have access to what we would call objects in the theory.
						colorConvertedToSType = theory.spriteObjects[s.stype].className
						argsString += " %s=%s"%("stype", colorConvertedToSType)
					except KeyError:
						print "in TheoryToTxt(), search for colorConvertedToSType"
						## TODO: If you, say, hypothesize that a missile is a Chaser and that it chases some random color but you don't have that color in your theory yet,
						## you can end up here.


				if "core" in stype:
					stype = stype[stype.find("core.")+len("core."):]

				if "avatar".lower() in stype.lower():
					theoryString += "\t\t%s > %s color=%s%s\n"%("avatar", stype, s.colorName, argsString)
				else:

					sname = c
					theoryString += "\t\t%s > %s color=%s%s\n"%(sname, stype, s.colorName, argsString)
					if goalLoc and newGoalType != 'blank_space' and s.colorName==newGoalColor:
						sname = colorToSprite[s.colorName]
						theoryString += "\t\t%s > %s color=%s%s\n"%("goal", stype, s.colorName, argsString)
	if debug==True:
		print "in writeTheoryToTxt debug"
		embed()

	if goalLoc:
		if newGoalType == 'blank_space':
			# we've selected an empty square to be the goal.
			theoryString += "\t\tgoal > Passive color=LIGHTRED\n"

	immovable_predicates = ['stepBack', 'undoAll']
	kill_predicates = ['killSprite', 'killIfHasLess', 'killIfHasMore', 'killIfOtherHasLess', 'killIfOtherHasMore',\
			'killIfTooFast', 'killIfSlow', 'killIfFromAbove', 'killIfFromBelow']
	immovables, killerObjects = [], []
	# second phase: the interaction rules
	theoryString += "\tInteractionSet\n"
	added_rules = []
	sortedInteractionDict = {}
	# create a dict mapping interacting class pairs to their list of interactions
	for interactionRule in theory.interactionSet:
		c1 = interactionRule.slot1
		c2 = interactionRule.slot2
		if c1 > c2:
			c1, c2 = c2, c1 # flip order

		if not (c1,c2) in sortedInteractionDict:
			sortedInteractionDict[(c1, c2)] = [interactionRule]
		else:
			sortedInteractionDict[(c1, c2)].append(interactionRule)

	sortedInteractions = []
	# For some games (e.g. boulderdash), the order of 'stepBack' interactions
	# matters: this list puts those that don't involve the avatar at the end
	nonAvatarStepBackInteractions = []
	for pair in sortedInteractionDict:
		(killIfHasLessInteractions, killInteractions, scoreChangeInteractions,
			nonKillInteractions, changeResourceInteractions) = [], [], [], [], []
		for interactionRule in sortedInteractionDict[pair]:
			if "kill" in interactionRule.interaction:
				precondition = list(set(interactionRule.preconditions))
				if precondition and precondition[0].operator_name in ['<', '<=']:
					killIfHasLessInteractions.append(interactionRule)
				else:
					# check whether this is a killing interaction
					killInteractions.append(interactionRule)
			elif "changeScore" in interactionRule.interaction:
				scoreChangeInteractions.append(interactionRule)
			elif "changeResource" in interactionRule.interaction:
				changeResourceInteractions.append(interactionRule)
			elif "stepBack" in interactionRule.interaction and 'avatar' not in [interactionRule.slot1, interactionRule.slot2]:
				nonAvatarStepBackInteractions.append(interactionRule)
			else:
				nonKillInteractions.append(interactionRule)

		sortedInteractions += (killIfHasLessInteractions +
			scoreChangeInteractions + changeResourceInteractions +
			killInteractions + nonKillInteractions)
		# make sure that killing interactions get processed before interactions
		# that don't kill.
		# EDIT: made killIfHasLess be processed first

	sortedInteractions += nonAvatarStepBackInteractions

	for interactionRule in sortedInteractions:
		if True:

			c1 = interactionRule.slot1
			c2 = interactionRule.slot2

			if c1 not in theory.classes or c2 not in theory.classes:
				print "c1 or c2 not in theory.classes"
				embed()

			if (c1=='laog' and len(theory.classes[c1])==0) or (c2=='laog' and len(theory.classes[c2])==0):
				print "found laog"
				embed()

			for s1 in theory.classes[c1]:
				if c2 not in theory.classes.keys():
					print "c2 not in theory.classes.keys() in theory template. c2={}".format(c2)
					embed()
				for s2 in theory.classes[c2]:
					argsString = ""

					if interactionRule.preconditions or interactionRule.args:
						args, interactionRule.interaction = buildArgsString(interactionRule, theory, rle)
						argsString += args

					if s1.colorName==newGoalColor:
						if not 'avatar' in str(s2.className): #only add actual goal object rule if it's not interacting with the avatar.
							theoryString += "\t\t%s %s > %s%s\n"%('goal', c2, interactionRule.interaction, argsString)
					elif s2.colorName==newGoalColor:
						if not 'avatar' in str(s1.className):#only add actual goal object rule if it's not interacting with the avatar.
							theoryString += "\t\t%s %s > %s%s\n"%(c1, 'goal', interactionRule.interaction, argsString)
					else:
						theoryString += "\t\t%s %s > %s%s\n"%(c1, c2, interactionRule.interaction, argsString)

					if 'avatar' in str(s1.vgdlType).lower():
						if interactionRule.interaction in immovable_predicates:
							# print "must add immovable"
							# embed()
							immovables.append(s2.className)
						if interactionRule.interaction in kill_predicates:
							killerObjects.append(s2.className) ##killSprite is not symmetrical; you to append things that are (avatar obj killSprite)
					elif 'avatar' in str(s2.vgdlType).lower():
						if interactionRule.interaction in immovable_predicates:
							# print "must add immovable"
							# embed()
							immovables.append(s1.className)
			added_rules.append(interactionRule)

	immovables = list(set(immovables))
	killerObjects = list(set(killerObjects))

	# third phase: the termination rules
	theoryString += "\tTerminationSet\n"
	goalConditionNotFound = True
	for terminationRule in theory.terminationSet:
		if terminationRule.ruleType == "TimeoutRule":
			theoryString += "\t\tTimeout limit=%s win=%s\n" % (str(terminationRule.termination.limit), str(terminationRule.termination.win))

		elif terminationRule.ruleType == "SpriteCounterRule":
			theoryString += "\t\tSpriteCounter stype=%s limit=%s win=%s\n" % \
						(terminationRule.termination.stype, \
						str(terminationRule.termination.limit), str(terminationRule.termination.win))
			if terminationRule.termination.stype == "goal":
				goalConditionNotFound = False
		elif terminationRule.ruleType == "NoveltyRule":

			theoryString += "\t\tNoveltyTermination s1=%s s2=%s win=%s" % \
						(terminationRule.termination.s1, terminationRule.termination.s2, str(terminationRule.termination.win))
			if terminationRule.termination.args:
				# print "found args in terminationrule"
				# embed()
				noveltyArgString = " args={item:%s,num:%s,negated:%s,operator_name:%s}" % \
				(terminationRule.termination.args.item, terminationRule.termination.args.num, terminationRule.termination.args.negated, terminationRule.termination.args.operator_name)
				theoryString += noveltyArgString

			theoryString +="\n"
		else:
			# multi sprite counter rule
			theoryString += "\t\tMultiSpriteCounter "
			for i in range(len(terminationRule.termination.stypes)):
				theoryString += "stype%i=%s " % (i, terminationRule.termination.stypes[i])

			theoryString += "limit=%s win=%s\n" % (str(terminationRule.termination.limit), str(terminationRule.termination.win))


	if goalLoc and goalConditionNotFound:
		# embed()
		theoryString += "\t\tSpriteCounter stype=goal limit=0 win=True\n"

	## fourth phase: the level mapping

	locs = defaultdict(lambda:[])
	mappedState = [[' ' for x in range(rle.outdim[1])] for y in range(rle.outdim[0])] 
	# embed()

	for lst in rle._game.observation['trackedObjects'].values():
		for sprite in lst:
			y,x = sprite.rect.top/30, sprite.rect.left/30
			locs[(y,x)].append(sprite)


	for k,v in locs.iteritems():
		symbol = objectsToSymbol(rle, v, symbolDict)
		try:
			mappedState[k[0]][k[1]] = symbol
		except:
			print "mappedState problem in writeTheoryToTxt"
			print mappedState
			embed()
	
	allObjectsSymbol = '`'
	if addAllObjects:
		mappedState[0][0] = allObjectsSymbol

	levelString = 'level="""\n'
	for mappedRow in mappedState:
		levelString += reduce(lambda a,b: a+b, mappedRow) + "\n"

	levelString += '"""\n'

	theoryString += "\tLevelMapping\n"

	for colors, symbol in symbolDict.items():
		if type(colors)==tuple:
			types = [theory.spriteObjects[c].className for c in colors if c in theory.spriteObjects.keys()]
			if len(types)==2:
				theoryString += "\t\t%s > %s %s\n"%(symbol, types[0], types[1])
			elif len(types)==3:
				theoryString += "\t\t%s > %s %s %s\n"%(symbol, types[0], types[1], types[2])
		elif type(colors)==str and colors in theory.spriteObjects.keys():
			c = theory.spriteObjects[colors].className
			theoryString += "\t\t%s > %s\n"%(symbol, c)

	if addAllObjects:
		allClasses = [c for c in theory.classes.keys() if c!='avatar' and c!='EOS']
		theoryString += "\t\t%s > %s\n"%(allObjectsSymbol, " ".join(allClasses))
	
	theoryString += '"""\n'
	
	parserString = 'if __name__ == "__main__":\n\tfrom vgdl.core import VGDLParser\n\tVGDLParser.playGame(game, level)\n'

	gameString = levelString + theoryString + parserString
	
	if writeFile:
		with open(txtFile, 'w') as f:
			f.write(gameString)
		f.close()

	levelString = levelString[levelString.find('"""')+3:-4]
	theoryString = theoryString[theoryString.find('"""')+3:-4]
	return theoryString, levelString, symbolDict

