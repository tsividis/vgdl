from random import choice
import itertools, copy, scipy.misc
import numpy as np
from sampleVGDLString import *
from class_theory_template import *
from taxonomy import *
from IPython import embed
from ontology import *
import operator
import time
"""
Theory induction on VGDL Games
"""

'''
TODO 8/2:
- Implement tree viz of hypothesis generation --> save children of each node
- More informative printing for debugging/monitoring progress *
- When DFSinduction returns before the full tree is built, return in a way that let's us save the state of the function, and continue running to get more theories --> queue
- Run on more minimal example *
- Make DFSinduction more efficient * 
	- fix the backward checks in likelihood (should you just check the most recently changed rules (anything in drying paint) against the past events?)
	- check that redundant events don't cost much extra
	- likelihood: check changed rules against all timesteps, check new timestep against all rules) --> calling checkRules / checkPredictions more targeted manner

NOTES:
Current assumptions:
	no grammar over preconditions
	preconditions limited to claims about a SINGLE object
	preconditions limited to simple comparison operators.
	Events that take place at same timestep can only be because of the same preconditions.

'''

class TimeStep: 
	"""
	Everything that happened in a time step in the game.
	
	Ex.)
	TimeStep.agentAction = 'up'
	TimeStep.agentState = {'health':1, 'treasure':2}
	TimeStep.events = [(bounceForward, BLUE, ORANGE), (undoAll, ORANGE, BLACK)]
	TimeStep.t = 4  --> meaning all of this took place at t_4
	"""

	def __init__(self, agentAction, agentState, events, gameState):
		self.agentAction = agentAction 
		self.agentState = agentState # agent's backpack
		self.events = events 
		self.t = False # Number timestep
		self.gameState = gameState

	def display(self):
		print (self.agentAction, self.agentState, self.events, self.gameState)
		return (self.agentAction, self.agentState, self.events, self.gameState)


class Precondition(object):
	"""
	Appended to InteractionRules if conflicting effects occur from the same interaction, due to changed resources.
	"""
	def __init__(self, text, fn, item):
		self.text = text
		self.fn = fn
		self.item = item
		self.negated = False

	def check(self, backpack):	# TODO: Is 'arg' most likely 'backpack'?
		# TODO: Incorporate something about if the item isn't even found in the backpack? Always return True in that case?
		try:
			answer = self.fn(backpack)
			if self.negated:
				return not answer
			else:
				return answer
		except Exception as e:
			#print e
			backpack[self.item] = 0
			return self.fn(backpack)

	def negate(self):
		self.negated = not self.negated
		self.text = 'not '+ self.text

	def display(self):
		print self.text

	def __eq__(self, other):
		return self.text == other.text

	def __ne__(self, other):
		return not self.__eq__(other)


class InteractionRule(object):
	"""
	Rule defining how 2 classes of objects interact with each other.
	# TODO: Should enforce proper syntax for interaction rules

	"""
	def __init__(self, interaction, c1, c2, resource, value, preconditions=set()):
		self.interaction = interaction
		self.slot1 = c1
		self.slot2 = c2
		self.valueChanges = {} # Change in value for resources
		self.preconditions = preconditions

		if resource:
			self.valueChanges[resource]=value

	def display(self):
		if not self.preconditions:
			print self.interaction, self.slot1, self.slot2, self.valueChanges
		else:
			print self.interaction, self.slot1, self.slot2, self.valueChanges, [p.text for p in self.preconditions]
		return

	def asTuple(self):
		return (self.interaction, self.slot1, self.slot2, self.valueChanges) #TODO: Check that adding the value here doesn't mess up equality checks elsewhere

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
	def isDone(self, game):
		return self.termination.isDone()

	def __eq__(self,other):
		return self.asTuple() == other.asTuple()


class TimeoutRule(TerminationRule):
	def __init__(self, limit=0, win=False):
		self.termination = Timeout(limit=limit, win=win)
		self.ruleType = "TerminationRule"

	def display(self):
		print (self.ruleType, self.termination.limit, self.termination.win)

	def asTuple(self):
		return (self.ruleType, self.termination.limit, self.termination.win)


class SpriteCounterRule(TerminationRule):
	""" Game ends when the number of sprites of type 'stype' hits 'limit' (or below). """
	def __init__(self,stype,limit,win):
		"""sclass = sprite class, snumber = sprite number, win = whether termination is a win"""
		self.termination = SpriteCounter(limit=limit, stype=stype, win=win)
		self.ruleType = "SpriteCounterRule"

	def display(self):
		print self.termination.stype, self.termination.limit, self.termination.win
		return 

	def asTuple(self):
		return (self.ruleType, self.termination.stype, self.termination.limit, self.termination.win)


class MultiSpriteCounterRule(TerminationRule):
	""" Game ends when the sum of all sprites of types 'stypes' hits 'limit'. """
	def __init__(self, limit=0, win=True, stypes = []):
		self.termination = MultiSpriteCounter(limit=limit,win=win,stypes=stypes)
		self.ruleType = "MultiSpriteCounterRule"

	def display(self):
		print self.termination.stypes, self.termination.limit, self.termination.win
		return 

	def asTuple(self):
		return (self.ruleType, self.termination.stypes, self.termination.limit, self.termination.win)


class ruleCluster(object):
	def __init__(self, interactionAndPreconditionList, pairList):
		self.clusteredRules = interactionAndPreconditionList
		self.pairs = pairList
		self.score = 0.

	def __eq__(self, other):
		if len(self.clusteredRules)!=len(other.clusteredRules):
			return False
		else:
			return all([r1 in [r2 for r2 in other.clusteredRules] for r1 in self.clusteredRules])

	def __ne__(self, other):
		return not self.__eq__(other)

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
		self.terminationSet = [] # Conditions that lead to game termination

		self.spriteObjects = {} # Maps sprite color -> Sprite object
		self.classes = {} # Maps classes -> objects
		self.predicates = set() # Types of possible interactions

		self.dryingPaint = set()
		self.inModification = {}

		self.posterior = False

	def initializeSpriteSet(self, vgdlSpriteParse):
		self.spriteSet = vgdlSpriteParse

		# Get mapping from sprite color to Sprite object
		for s in self.spriteSet:
			self.spriteObjects[s.color] = s

	"""Main functions"""

	def prior(self):

		def phi(numClasses, numRules, lamda):
			#TODO: Refine this to take into account the minimum necessary size of the ruleset.
			return lamda*numClasses + (1-lamda)*numRules

		#Mode is p(r-1) / (1-p). For now we pick p=.5, r=5 to reflect that phi=4 is modal.
		def negBin(k, r, p):
			return scipy.misc.comb(k+r-1, k) * p**k * (1-p)**r

		numClasses, numRules = len(self.classes.keys()), len(self.interactionSet)
		k = phi(numClasses, numRules, .5)

		return negBin(k,5,.5)


	def explainTimeStep(self, timestep, fullTimestep, currTheories=False):
		"""
		Returns a set of theories that explain all the events that took place at timestep.
		Hypotheticals can be passed as args to enable the explanation of multiple events in a single timestep.
		"""
		# print "in explainTimeStep..."
		
		# Base Case
		if len(timestep.events) == 1:
			# print "in base case of explainTimeStep"
			theories = []
			
			if not currTheories:
				theories.extend(self.explainEvent(timestep.events[0], fullTimestep))
			
			# Generate theories based on hypothetical theories
			else: 
				for theory in currTheories:
					newTheory = theory.explainEvent(timestep.events[0], fullTimestep)
					theories.extend(newTheory)
			
			for t in theories:
				t.depth = self.depth+1
			return theories

		# Recursive Case
		else:
			# print "in recursive case"
			theories = []

			if not currTheories:
				theories.extend(self.explainEvent(timestep.events[0], fullTimestep))
			
			# Generate theories based on hypothetical theories
			else: 
				for theory in currTheories:
					newTheory = theory.explainEvent(timestep.events[0], fullTimestep)
					theories.extend(newTheory)

			#theories = self.explainEvent(timestep.events[0], fullTimestep)



			updatedTimeStep = TimeStep(timestep.agentAction, timestep.agentState, timestep.events[1:], timestep.gameState)
			return self.explainTimeStep(updatedTimeStep, fullTimestep, theories)

	def explainEvent(self, event, timestep):
		"""
		Returns theories that explain the event, which is a tuple like:
		(bounceForward, BLUE, ORANGE)
		"""
		# print "in explainEvent..."
		# print "event: ", event
		theories = []

		#print " --> will check likelihood to get failCase (or just add the theory if the event is explained)"
		likelihood = self.likelihood(timestep)
		# print '\tlikelihood', likelihood

		if likelihood == 1:
			theories.append(self)
		else:
			failCase = self.getFailCases(event, timestep)
			# print "\tFail case: ", failCase

			# Add preconditions
			if failCase in [1,2,3]:
				theories.extend(self.addPreconditions(event, timestep))
			
			# Add new rule
			elif failCase == 4: 
				theories.extend(self.addRules(event))

		return theories

	def colorToClassMapper(self,color):
		for c in self.classes:
			for c_class in self.classes[c]:
				if c_class.color == color:
					return c

		raise Exception("No corresponding class found for color")

	def makeGameStateWithClasses(self, gameState):
		classGameState = {k: 0 for k in self.classes.keys()}
		for c in self.classes:
			for s in self.classes[c]:
				if s.color in gameState:
					classGameState[c] += len(gameState[s.color])

		return classGameState


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

		# print "IN TERMINATION CONDITIONS"
		# print timestep
		# # print timestep.events
		# print classesWithDiffAmounts
		# print {k:[c.asTuple() for c in v] for k,v in self.classes.items()}

		for event in timestep.events:
			for i in [1,2]:
				terminationClassColor = event[i] #self.getClass(event[i])
				terminationClassSymbol = self.colorToClassMapper(terminationClassColor)
				if terminationClassSymbol in classesWithDiffAmounts:
					timestep_amt = classesWithDiffAmounts[terminationClassSymbol]
					spriteCounterRule= SpriteCounterRule(terminationClassSymbol,timestep_amt,win)
					if not spriteCounterRule in self.terminationSet:
						self.terminationSet.append(spriteCounterRule)

		# print [t.asTuple() for t in self.terminationSet]
		# embed()
		time = result["time"]
		timeoutRule = TimeoutRule(limit=time, win=win)
		if not timeoutRule in self.terminationSet:
			self.terminationSet.append(timeoutRule)


	def likelihood(self, timestep, sparse=False):
		"""
		Makes sure that:
			-all events in the timestep were covered by the ruleset 
			-everything predicted in the ruleset happened.

		Right now returns only 1 or 0.
		"""
		#print "events in timestep {} | predictions in timestep {}".format(self.checkEventsInTimeStep(timestep), self.checkPredictionsInTimeStep(timestep))
		if self.checkEventsInTimeStep(timestep) and self.checkPredictionsInTimeStep(timestep, sparse):
			likelihood = 1.
		else:
			likelihood = 0.
		return likelihood


	def checkTerminationCounterInState(self, c, termCondition):
		"""
		c = game state with classes instead of colors
		"""
		return c[termCondition.termination.stype] == termCondition.termination.limit


	def getBadTerminationConditions(self, allTraces, verbose=False):
		"""
		Right now returns the list of termination conditions which are contradicted by the data.
		"""
		badTerminationConditions = []
		for termCondition in self.terminationSet:
			if termCondition.ruleType == "SpriteCounterRule":
				for timesteps,result in allTraces:
					for i in range(len(timesteps)):
						t = timesteps[i]
						c = self.makeGameStateWithClasses(t.gameState["objects"])
						if i == len(timesteps) - 1:
							if self.checkTerminationCounterInState(c, termCondition) and termCondition.termination.win != result["win"]:
								if not termCondition in badTerminationConditions:
									badTerminationConditions.append(termCondition)
						else:
							if self.checkTerminationCounterInState(c, termCondition): # if condition were true, would have ended on this time step.
								if not termCondition in badTerminationConditions:
									badTerminationConditions.append(termCondition)

			elif termCondition.ruleType == "TimeoutRule":
				for timesteps, result in allTraces:
					if result["time"] > termCondition.termination.limit:
						if not termCondition in badTerminationConditions:
							badTerminationConditions.append(termCondition)

		return badTerminationConditions


	def checkEventsInTimeStep(self, timestep):
		"""
		Check if all events in the timestep are covered by the interaction rule set.
		"""
		interpretations = [self.interpret(event) for event in timestep.events]
		return all([self.checkEvents(i, timestep) for i in interpretations])


	def checkPredictionsInTimeStep(self, timestep, sparse=False):
		"""
		Check if all predictions for the timestep actually occurred. 
		"""
		#Note: This fn cannot be exactly like checkPredictions(), becase here we don't care whether 'drying paint' is 
		#T or F. We need to actually check all the predictions.
		interpretations = [self.interpret(event).asTuple() for event in timestep.events if self.interpret(event) is not False]

		relevantRules = []
		for event in timestep.events:
			relevantRules.extend(self.findRelevantRules(event, timestep.agentState, checkDryingPaint=False, sparse=sparse))

		if False in relevantRules: 
			return False
		else:
			for rule in relevantRules:
				if rule.asTuple() not in interpretations:
					return False
			return True

	
	def getFailCases(self, event, timestep, verbose=False):
		"""
		Note: the only predictions we care about checking for here are the ones that are in the original theory.
		Predictions made by 'drying-paint' theories shouldn't be taken into account in the sense that all of these should receive
		the same treatment. That is, if we have (bf c1 c2) in the original theory, and are currently explaining the events:
		(ks c1 c2) (uA c1 c2),
		what we want to do is realize that (ks c1 c2) needs a precondition on it. Then we add this to a theory (as drying paint)
		and when we explain (uA c1 c2), we want to do exactly what we did with (ks c1 c2); recognize that it needs a single precondition.
		So checkPredictions only checks for theories that are not in dryingPaint.
		"""

		failCases = {(True, True): 	 [0, "Event likelihood = 1"],
					 (True, False):  [1, "Event likelihood failed because the interactionSet predicts things that didn't happen. "+
					 "Solution: Add preconditions to subset of interactionSet."],
					 (False, True):  [2, "Event likelihood failed because interpreted event is not in interactionSet. "+
					 "Solution: Add new rule with precondition on it."],
					 (False, False): [3, "Event likelihood failed both ways."+
					 "Solution: Add new rule with precondition on it; negate that precondition for other relevant rules."],
					 (False, ()):    [4, "Event likelihood failed because interactionSet hasn't seen the event."+
					 "Solution: AddRule()"]}

		(eventInRules, predictionsHappened) = self.checkEvents(self.interpret(event), timestep), self.checkPredictions(event, timestep)

		# self.display()
		# print "event", event
		# print "interaction set:", [i.asTuple() for i in self.interactionSet]
		
		if verbose:
			print failCases[(eventInRules, predictionsHappened)][1]

		return failCases[(eventInRules, predictionsHappened)][0]


	def checkEvents(self, interpretation, timestep):
		"""
		Checks whether everything in the interpretation is accounted for by the interactionSet.
		"""
		
		if interpretation:
			interpretation = interpretation.asTuple()
			for rule in self.interactionSet:
				precon_list = [p.text for p in rule.preconditions]
				if rule.asTuple()==interpretation:
					if not rule.preconditions: # If no preconditions for the rule, then all is well.
						return True 
					else:
						return all([p.check(timestep.agentState) for p in rule.preconditions])

		# If we've checked everything and found no matching rule or rule+precondition, return False.			
		return False 



	def checkPredictions(self, event, timestep):
		"""
		Check if the relevant predictions to a specific event occurred. 
		"""
		# TODO: Add comments here
		interpretations = [self.interpret(e).asTuple() for e in timestep.events if self.interpret(e) is not False] 
		if interpretations:
			relevantRules = self.findRelevantRules(event, timestep.agentState, checkDryingPaint=True)
			if False in relevantRules:
				return () 
			if relevantRules:
				return all([rule.asTuple() in interpretations for rule in relevantRules])
		
		# If no interpretations, or if no relevant rules
		return ()


	def addRules(self, event):
		"""
		Search over possible assignments for classes; posit new classes if necessary
		Return theories that have either 
		Try to make it fit according to the current rules by searching
		over possible class assignments for the objects.
		Returns a list of theories.
		"""
		# print 'in addRules...'
		newTheories = []
		possibleAssignments = self.searchForAssignments(event)
		try: 
			resource = event[3]
			value = event[4]

		except:
			resource = None
			value = 0

		obj1 = self.spriteObjects[event[1]]
		obj2 = self.spriteObjects[event[2]]


		if possibleAssignments:
			for assignment in possibleAssignments:
				interaction = InteractionRule(event[0], assignment[0], assignment[1], resource, value) #This isn't strictly necessary, but follows createChild requirements.
				# print "interaction ", interaction.display()
				classAssignments = [(assignment[0], obj1), (assignment[1], obj2)]
				newTheory = self.createChild([interaction, classAssignments])
				newTheory.display()
				# Checks and only adds to newTheories if the created theory was actually different.
				if newTheory:
					newTheories.append(newTheory)

		# print "adding {} theories with new assignments".format(len(newTheories))
		return newTheories


	def addPreconditions(self, event, timestep):
		"""
		Creates preconditions based on the agentState that might help to explain the event.
		Returns a list of theories.
		"""
		newTheories = []

		obj1 = self.spriteObjects[event[1]]
		obj2 = self.spriteObjects[event[2]]

		classPair = (self.getClass(obj1), self.getClass(obj2))
		# If object classes are currently being modified in the same timestep, obtain the same preconditions as before
		if classPair in self.inModification.keys():
			p = self.inModification[classPair]
			interpretation = self.interpret(event)
			interpretation.addPrecondition(p) #TODO: maybe you should be only doing this if interpreting worked in the line above.
			newTheory = self.createChild([interpretation, False])
			if newTheory:
				newTheories.append(newTheory)
		else:
			# Create possible preconditions
			concepts = []
			for k in timestep.agentState.keys():
				concepts.extend(self.generateNumberConcepts(k, timestep.agentState[k])) #TODO: Combine generateNumberConcpets and makePreconditions
			generatedPreconditions = self.makePreconditions(concepts)
			for p in generatedPreconditions:
				interpretation = self.interpret(event)
				interpretation.addPrecondition(p)

				# Find what rules you will need to negate
				relevantInteractionSetRules = self.findRelatedRules(classPair, self.interactionSet)
				relevantEvents = self.findRelatedRules(classPair, [self.interpret(e) for e in timestep.events])
				unfulfilledPredictions = set(relevantInteractionSetRules) - set(relevantEvents) # Will be negated
				
				newTheory = self.createChild([interpretation, False]) #TODO: make sure this is properly negating all other similar events

				newTheory.inModification[classPair] = p
				newTheory.negatePreconditions(unfulfilledPredictions) # Must be after classPair is added to inModification


				# TODO: See if you need to use these lines, or if newTheory = self.createChild(...) completes the task
				#Negate all interactionRules that didn't happen in this timestep.
				#Note: this only has to happen for the base case when you're recursing; after that these have already been negated and should not be touched.
				# for uP in unfulfilledPredictions:
				# 	uP.addPrecondition(precondition.negate())
				
				if newTheory:
					newTheories.append(newTheory)

		return newTheories

	


	"""Helper functions"""

	#TODO: Could be named "suggestRules"
	def interpret(self, event):
		"""
		Looks up objects by their corresponding class under the theory,
		returns a corresponding interactionRule.
		
		If those objects aren't known, returns false.

		Ex) Event is a tuple: ('bounceForward', 'ORANGE', 'DARKBLUE') or ('changeResource', 'BLUE', 'RED', 1)
		If we know that ORANGE=c1 and DARKBLUE=c2, returns the InteractionRule
		that corresponds to (bounceForward, c1, c2)
		"""
		# Check if there is an extra value argument in event
		try: 
			value = event[3]
			resource = event[4]

		except:
			value = 0
			resource = None

		# embed()
		obj1 = self.spriteObjects[event[1]]
		obj2 = self.spriteObjects[event[2]]

		c1, c2 = self.getClass(obj1), self.getClass(obj2)
		#print 'classes:', c1, c2
		if c1 and c2:
			#print 'new interaction rule!'
			return InteractionRule(event[0], c1, c2, value, resource)
		else:
			return False

	def findRelatedRules(self, classPair, interactionList):
		#needs to take a list of interpretations or a list of interaction rules
		#Note: PT changed this on 8/19; weird that we hadn't caught the bug before -- was checking interaction.asTuple()[1:].
		return [interaction for interaction in interactionList if classPair == interaction.asTuple()[1:3]]
	
	def negatePreconditions(self, unfulfilledPredictions):
		"""
		Given a list of Interaction rules, will add a negation to each rule, if rule is not in drying paint.
		"""
		# Iterate through relevant rules, negate them if they're not in the drying paint
		for r in unfulfilledPredictions:
			if r.asTuple() not in [new_r.asTuple() for new_r in self.dryingPaint]:
				precondition = self.inModification[r.asTuple()[1:]] # Single precondition object
				preconditionToNegate = copy.deepcopy(precondition)
				preconditionToNegate.negate()
				r.preconditions = [preconditionToNegate]
		
		# Generate new interaction set with new preconditioned rules
		newInteractionSet = []

		for r1 in self.interactionSet:
			for r2 in unfulfilledPredictions:
				if r1.asTuple()==r2.asTuple():
					newInteractionSet.append(r2)
				else:
					newInteractionSet.append(r1)

		self.interactionSet = newInteractionSet


	def makePreconditions(self, concepts):
		preconditions = []
		for c in concepts:
			text = c[0]
			item = c[1]
			num = c[2]
			
			f = lambda x: x[item]>num
			
			preconditions.append(Precondition(text, f, item))
		return preconditions


	def createChild(self, proposal):
		"""
		Spawns a new child theory with the new proposal incorporated
		"""
		newTheory = copy.deepcopy(self)
		newTheory.depth = self.depth + 1
		newTheory.parent = self
		newTheory.children = []

		#TODO: Could copy over the spriteSet and self.classes?

		generatedNewTheory = newTheory.addProposal(proposal)

		if generatedNewTheory:
			self.children.append(newTheory)
			return newTheory
		else:
			return False

	def addProposal(self, proposal):
		"""
		Adds proposal to theory; takes care of rule and assignments
		"""
		
		## Helper functions
		def assignClass(classObjectPair):
			'''
			Adds object-class assignments; avoids duplicates.
			'''
			c, o = classObjectPair[0], classObjectPair[1]
			if c in self.classes.keys():
				if o not in self.classes[c]:
					self.classes[c].append(o)
					return True
				return False
			else:
				self.classes[c] = [o]
				return True

		def addInteractionRule(rule):
			"""
			Adds interactionRule if it is not in interactionSet.
			"""
			if rule.interaction not in self.predicates:
				self.predicates.add(rule.interaction)
			if not self.findRule(rule, self.interactionSet):
				self.interactionSet.append(rule)
				self.dryingPaint.add(rule)
				return True
			return False

		rule, assignments = proposal[0], proposal[1]
		# Add the proposed rule to the Theory's InteractionSet
		if rule:
			addedRule = addInteractionRule(rule)
		else:
			addedRule = False
		# Add the proposed class assignments to the Theory 
		addedClass = False
		if assignments:
			addedClass = any([assignClass(assignment) for assignment in assignments])

		return (addedRule or addedClass)



	def findRule(self, rule, lst):
		"""
		Finds if a rule is in the interaction set.
		"""
		for interactionRule in lst:
			if interactionRule == rule:
				return True
		return False


	def getClass(self, obj):
		"""
		Obtains the classes of the object; otherwise returns False if class not found.
		"""
		for classNum, objList in self.classes.iteritems(): #TODO: The issue is here w/ objects not found in the classes list
			for obj2 in objList:
				if obj == obj2:
					return classNum
		return False

	

	def findRelevantRules(self, event, agentState, checkDryingPaint=False, sparse=False):
		"""
		If an event involves c1 and c2, returns rules that use c1 and c2 in those slots.
		"""
		relevantRules = []

		# If both classes exist (whether predicate already exists doesn't matter)
		obj1 = self.spriteObjects[event[1]]
		obj2 = self.spriteObjects[event[2]]
		class1 = self.getClass(obj1)
		class2 = self.getClass(obj2)

		if class1 and class2:

			# This should not include any rules that don't satisfy the current preconditions
			rules = [rule for rule in self.interactionSet]

			if not sparse:
				#Default behavior
				if not checkDryingPaint:
					relevantRules.extend([rule for rule in rules if rule.asTuple()[1]==class1 and rule.asTuple()[2]==class2 and all(p.check(agentState) for p in rule.preconditions)])
				else:
					# Here we only return rules that are not in the drying paint. 
					relevantRules.extend([rule for rule in rules if not self.findRule(rule, self.dryingPaint) and rule.asTuple()[1]==class1 and rule.asTuple()[2]==class2 and all(p.check(agentState) for p in rule.preconditions)])
			else:
				#'sparse' is passed when we check likelihood of lots of previous timesteps. The logic here is to
				#only check predictions for previous timesteps when the predictions may have changed. Meaning, only return rules that
				#are both relevant to the event *and* are new.
				relevantRules.extend([rule for rule in list(self.dryingPaint) if rule.asTuple()[1]==class1 and rule.asTuple()[2]==class2 and all(p.check(agentState) for p in rule.preconditions)])

		# If both classes don't exist
		else:
			return [False]

		return relevantRules



	def searchForPossibleClasses(self, obj_Sprite, newClasses=0):
		"""
		If the object has been assigned, return it. Otherwise return all
		possible classes. Optional argument can posit existence of a new class;
		user specifies whether to add 0, 1, or 2 new classes.
		"""
		gotNewClass = False
		
		# Get classes of sprites of the same VGDL Type 
		possibleClasses = []
		for s in self.spriteSet:
			s_class = self.getClass(s)
			if s.vgdlType == obj_Sprite.vgdlType and s_class:
				if s_class not in possibleClasses:
					possibleClasses.append(s_class)

		# Class exists
		if self.getClass(obj_Sprite):
			return [self.getClass(obj_Sprite)], gotNewClass

		# Propose new classes and classes with sprites of the same vgdlType
		elif newClasses > 0: 
			numClasses = len(self.classes.keys())
			for i in range(1, newClasses+1):
				possibleClasses.append('c'+str(numClasses+i)) # Classes that extend off number of existing classes
			gotNewClass = True
			return possibleClasses, gotNewClass

		else: return [], gotNewClass


	def searchForAssignments(self, event):
		obj1 = self.spriteObjects[event[1]]
		obj2 = self.spriteObjects[event[2]]

		x1, gotNewClass = self.searchForPossibleClasses(obj1, newClasses=1)
		if gotNewClass:
			x2 = self.searchForPossibleClasses(obj2, newClasses=2)[0]
		else:
			x2 = self.searchForPossibleClasses(obj2, newClasses=1)[0]

		if x1 and x2: # If both yielded possibilities
			classAssignments = []

			# If objects are the same type, any combo of classes is accepted
			if obj1.vgdlType == obj2.vgdlType:
				return list(itertools.product(x1,x2))

			 # If objects are diff type, want diff classes
			else:
				classAssignments = [(c1, c2) for c1 in x1 for c2 in x2 if c1!=c2]
				return classAssignments
		else: return False

	"""Prediction/generalization functions"""
	def findRuleClusters(self):
		ruleClusters = []
		uniquePairs = list(set([(rule.slot1, rule.slot2) for rule in self.interactionSet]))
		for pair in uniquePairs:
			rules = [(r.interaction, r.preconditions) for r in self.interactionSet if (r.slot1,r.slot2)==pair]
			ruleClusters.append(ruleCluster(rules, pair))
		return ruleClusters

	def predict(self, pair, lamda, tree, beta=1.,softmaxTemp=.1):

		#Takes a pair of object, generates a prediction (distribution over predicates) for what happens
		#if those collide.
		
		predicateList = ['killSprite', 'cloneSprite', 'stepBack', 'transformTo', 'undoAll',
		'bounceForward', 'conveySprite', 'windGust', 'slipForward', 'attractGaze', 'turnAround',
		'reverseDirection', 'flipDirection', 'bounceDirection', 'wallBounce', 'wallStop',
		'killIfSlow', 'killIfFromAbove', 'killIfAlive', 'collectResource', 'killIfHasMore',
		'killIfOtherHasMore', 'killIfHasLess', 'killIfOtherHasLess', 'wrapAround',
		'pullWithIt', 'teleportToExit']

		# print ""
		# print "predicting interactions for {} with parameters:".format(pair)
		# print "lambda = {}. beta = {}. tree = {}. softmax temp = {}".format(lamda, beta, tree.name, softmaxTemp)
		# print "(lambda: extrapolation (1) vs. guess (0) balance)"
		# print "(beta: ontology (1) vs. rule-similarity (0) balance)"
		# print ""

		#Get class memberships
		classes = (self.getClassFromColor(pair[0]), self.getClassFromColor(pair[1]))
		if False in classes:
			print "Can't make predictions; theory does not contain {}".format([el[0] for el in zip(pair, classes) if not el[1]])
			return False
		else:
			pair = classes

		inversePair = (pair[1], pair[0]) #a collision between cx and cy is the same as a collision between cy and cx. Locate both.
		# print 'making predictions for', pair[0], pair[1]

		knownRules = [rc for rc in self.findRuleClusters() if rc.pairs==pair or rc.pairs==inversePair]
		if len(knownRules)>0:
			#findRuleClusters will only return a single element if it works. It's a cluster, and contains all the matching rules.
			knownRules = knownRules[0].clusteredRules 
			restOfRules = [p for p in predicateList if p not in [k[0] for k in knownRules]]
			
			knownRules = [[k, 1.] for k in knownRules]
			allRules = knownRules + [[r, 0.] for r in restOfRules]

			return allRules
		extrapolatedRules = [[r[0], r[1]*lamda] for r in self.extrapolateRule(pair, tree, beta)]
		guessedRules = [[r[0], r[1]*(1-lamda)] for r in self.guessRule(predicateList)]
		
		allRules = extrapolatedRules + guessedRules
		scores = softmax([r[1] for r in allRules], softmaxTemp)
		outList = [list(z) for z in zip([e[0] for e in allRules], scores)]
		
		#merge original extrapolated rules if they use the same predicates
		mergedRules = [outList[0]]
		for i in range(1, len(extrapolatedRules)):
			rule = outList[i]
			for m in mergedRules:
				if m[0]==rule[0]:
					m[1] += rule[1]
			if all([rule[0]!=m for m in [mR[0] for mR in mergedRules]]):
				mergedRules.append(rule)

		#convert ruleCluster rules to simple predicate form for ease of reading.
		#TODO: figure out what format you really want eventually, if you're going to
		#take actions, rather than just get a distribution over actions.
		mergedRules = [[m[0].clusteredRules, m[1]] for m in mergedRules]
		outList = mergedRules + outList[len(extrapolatedRules)+1:]
		
		# for o in outList:
		# 	print o
		return outList

	def guessRule(self, predicateList):
		#Currently returns interactions (no preconditions, and not in the form of interactionRules)
		#TODO: changeResource, spawnifHasMore require another argument. Add these and figure out how
		#to pass those args. Maybe this is best done in the step that creates interactionRules
		#in predict(). Also decide how to deal with values of optional args. Right now you'll
		#just make predictions based on default args.

		remainingPredicates = list(set(predicateList)-set([rule.interaction for rule in self.interactionSet]))
		scores = [1./len(remainingPredicates)]*len(remainingPredicates)
		return zip(remainingPredicates, scores)

	def extrapolateRule(self, pair, tree, beta=1.,softmaxTemp=False):
		#returns interactionRules (including preconditions) that are already in the interactionSet
		#weighted by their similarity to the provided pair.
		#TODO: think about default softmaxTemp.
		if len(self.interactionSet)==0:
			print "Can't extrapolate; our theory has no rules in the interactionSet!"
			return
		classPairs = list(set([(rule.slot1, rule.slot2) for rule in self.interactionSet]))
		similarityScores = [self.pairSimilarity(pair, classPair, tree, beta) for classPair in classPairs]
		similarityScores = normalize(similarityScores)
		if softmaxTemp:
			similarityScores = softmax(similarityScores,softmaxTemp)


		classSimilarities = zip(classPairs, similarityScores)

		ruleClusters = self.findRuleClusters()
		for ruleCluster in ruleClusters:
			ruleCluster.score = [cS[1] for cS in classSimilarities if cS[0]==ruleCluster.pairs][0]

		return ([[rc, rc.score] for rc in ruleClusters])

	def levenshtein(self, source, target):
		source, target = list(source), list(target)
		if max(len(source), len(target)) == 0:
			return 1.
		else:
			z = 1.*max(len(source), len(target))
			return 1. - self.levenshteinDistance(source, target)/z

	def levenshteinDistance(self, source, target):
	    if len(source) < len(target):
	        return self.levenshteinDistance(target, source)

	    # So now we have len(source) >= len(target).
	    if len(target) == 0:
	        return len(source)

	    # print 'source', source
	    # We call tuple() to force strings to be used as sequences
	    # ('c', 'a', 't', 's') - numpy uses them as values by default.
	    source = np.array(tuple(source))
	    target = np.array(tuple(target))
	    # We use a dynamic programming algorithm, but with the
	    # added optimization that we only need the last two rows
	    # of the matrix.
	    previous_row = np.arange(len(target) + 1)
	    for s in source:
	        # Insertion (target grows longer than source):
	        current_row = previous_row + 1

	        # Substitution or matching:
	        # Target and source items are aligned, and either
	        # are different (cost of 1), or are the same (cost of 0).

	        current_row[1:] = np.minimum(
	                current_row[1:],
	               	np.add(previous_row[:-1], [(t!=s).any() for t in target]))

	        # Deletion (target grows shorter than source):
	        current_row[1:] = np.minimum(
	                current_row[1:],
	                current_row[0:-1] + 1)

	        previous_row = current_row

	    return previous_row[-1]  

	def levenshtein2(self, s1, s2):
		#Levenshtein (edit) distance. additions and deletions cost the same. No replacements.
		count = 0
		s1, s2 = list(s1), list(s2)
		for i in range(len(s1)):
			if s1[i] not in s2:
				s2.append(s1[i])
				count += 1
		to_remove = []
		for i in range(len(s2)):
			if s2[i] not in s1:
				to_remove.append(s2[i])
				count += 1
		for i in range(len(to_remove)):
			s2.remove(to_remove[i])
		return 1./(1+count)

	def ruleSimilarity(self, cx, cy):
		#Looks at rules in which cx participated in as slot 1, compares them to rules in which
		#cy participated as slot 1. Compares in terms of their edit distance.
		#Then does the same for slot 2.
		cxSlot1 = [(r.interaction, r.slot2, r.preconditions) for r in self.interactionSet 
		if r.slot1==cx]
		cySlot1 = [(r.interaction, r.slot2, r.preconditions) for r in self.interactionSet 
		if r.slot1==cy]

		cxSlot2 = [(r.interaction, r.slot1, r.preconditions) for r in self.interactionSet 
		if r.slot2==cx]
		cySlot2 = [(r.interaction, r.slot1, r.preconditions) for r in self.interactionSet 
		if r.slot2==cy]

		return .5*self.levenshtein(cxSlot1, cySlot1) + .5*self.levenshtein(cxSlot2, cySlot2)
	
	def pairSimilarity(self, pair1, pair2, tree, beta=1.):
		cx, cm, cy, cn = pair1[0], pair1[1], pair2[0], pair2[1]
		return (self.similarity(cx, cy, tree, beta) + self.similarity(cm, cn, tree, beta)) / 2.

	def similarity(self, cx, cy, tree, beta=1.):
		# Returns beta*treeSimilarity(c1,c2) + (1-beta)*ruleSimilarity(c1,c2)
		# Uses whatever tree is passed in. Currently we only have VGDLTree, which is
		# the original tree based on the VGDL ontology.
		n1, n2 = self.classes[cx][0].vgdlType, self.classes[cy][0].vgdlType
		treeSimilarity = tree.similarity(n1, n2)
		ruleSimilarity = self.ruleSimilarity(cx,cy)
		return beta*treeSimilarity + (1-beta)*ruleSimilarity

	def generateNumberConcepts(self, item, num): # TODO: Make this set of preconditions smaller
		"""
		Preconditions can be drawn from a pre-defined set of number concepts:
		n >= 0  --> any numbers from 0 to inf (having this amount of health is fine)
		n < 0 --> any negative numbers 		  (having this amount of health is bad)
		n >= 1 --> any numbers from 1 to inf  (having this amount of medicine and touching poison = safe)
		n < 1 --> any numbers from -inf to 0  (having this amount of medicine and touching poison = death)
		"""
		concepts = []
		for n in range(num):
			text = item+">"+str(n)
			concepts.append((text,item,n))
		return concepts 					# TODO: Should this return functions and text? (text, function) tuples?

	def getClassFromColor(self, color):
		for c in self.classes:
			if color in [cl.color for cl in self.classes[c]]:
				return c
		return False

	def displayRules(self):
		print ""
		print "InteractionSet:"
		for rule in self.interactionSet:
			rule.display()

	def displayClasses(self):
		print ""
		print "Class assignments:"
		for c in self.classes:
			class_list = [cl.color for cl in self.classes[c]]
			print "\t{}: {}".format(c, class_list)
		#print self.classes
		print

	def displayTerminationSet(self):
		print ""
		print "TerminationSet:"
		for tc in self.terminationSet:
			tc.display()

	def display(self):
		print "_______"
		self.displayRules()
		self.displayClasses()
		self.displayTerminationSet() #TODO: Figure out why this isn't printing
		return

	def __eq__(self, other):
		if isinstance(other, self.__class__):

			# Must check interactionSet in this way, to use overloaded equality of InteractionRules
			interactionSetEqual = all(any(i1==i2 for i2 in other.interactionSet) for i1 in self.interactionSet)

			return all([
				self.spriteSet == other.spriteSet, 
				self.levelMapping == other.levelMapping, 
				interactionSetEqual, # TODO: Check if this uses InteractionRule overloaded __eq__
				self.classes == other.classes,
				self.terminationSet == other.terminationSet #may want to delete this
				]) # TODO: Add in termination set later
		else:
			return False

	def __ne__(self, other):
		return not self.__eq__(other)


def softmax(w, t = 1.0):
    e = np.exp(np.array(w) / t)
    dist = e / np.sum(e)
    return dist	

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
	def __init__(self, vgdlString):
		# Game states #TODO: May not need these
		#self.backpack = {}
		#self.trace = [] # list of TimeStep objects that happened during a gameplay

		self.vgdlString = vgdlString

		# Induction states
		self.hypothesisSpace = []
		self.theoryCount = 0
		self.vgdlSpriteParse = self.makeSpriteParse()

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

	def posterior(self):
		#TODO: Consider allowing some amount of probability mass to uninstantiated hypotheses
		#The problem with this is it's not clear what the content of those hypotheses,
		#so it's unclear what you'd do with this new distribution.
		if len(self.hypothesisSpace)>0:
			z = 1.*sum([t.prior() for t in self.hypothesisSpace])
			for t in self.hypothesisSpace:
				t.posterior = t.prior()/z
			return [t.posterior for t in self.hypothesisSpace]
		else:
			print "Empty hypothesis space; can't give you a posterior."
	def entropy(self, theory):
		entropySum = 0
		numSpritesInClasses = float(sum([1 for c in theory.classes for i in c]))
		#print "\t num sprites total:", numSpritesInClasses
		for c in theory.classes:
			classLength = len(theory.classes[c])
			p = float(classLength/numSpritesInClasses)
			#print p
			entropySum += p * np.log2(p)
		return -1 * entropySum

	def orderHypotheses(self, hypotheses):
		temp_hypotheses = [(h, -1 * h.depth, self.entropy(h)) for h in hypotheses]
		temp_hypotheses = sorted(temp_hypotheses, key=operator.itemgetter(1,2))
		return [h[0] for h in temp_hypotheses]

	def completeTheory(self, theory, numSamples):

		def sampleCompletedTheory(game, theory):
			"""
			Assign all remaining sprites to a class for a given theory in a given game.
			This literally gives you a single *sample* from the possible ways you could extend the theory to include
			all seen objects.
			"""	
			# Find all remaining sprites
			spritesLeft = []
			for sprite in theory.spriteSet:
				if not theory.getClass(sprite):
					spritesLeft.append(sprite)

			# For each sprite, assign it to a random possible class 
			allClassAssignments = []			# Will save the class assignments here
			tempTheory = copy.deepcopy(theory) 	# Temporary theory
			for sprite in spritesLeft:
				possibleClasses,gotNewClass = tempTheory.searchForPossibleClasses(sprite, 1) # Second param is possible number of new classes
				sampledClass = choice(possibleClasses)

				classAssignments = [(sampledClass, sprite)]
				allClassAssignments.extend(classAssignments)
				tempTheory = tempTheory.createChild([None, classAssignments]) # Update the tempTheory; don't really want to save these theories

			# newHypothesisSpace = []
			# Finalize the temporary theory
			if tempTheory:
				newTheory = theory.createChild([None, allClassAssignments])
				# game.hypothesisSpace.append(newTheory)
				# newHypothesisSpace.append(newTheory)
			# return game.hypothesisSpace
			#used to return game.hypothesisSpace
			# return newHypothesisSpace
			return newTheory


		newHypothesisSpace = []
		for i in range(numSamples):
			newHypothesisSpace.append(sampleCompletedTheory(self, theory))
		return newHypothesisSpace

	def predict(self, pair, lamda, numCompletionSamples=10, tree=False, beta=1., softmaxTemp=.1):
		
		if not tree:
			tree = self.VGDLTree

		predictions = []

		# pairs = [(t.getClassFromColor(pair[0]), t.getClassFromColor(pair[1])) for t in self.hypothesisSpace]
		for theory in self.hypothesisSpace:
			prediction = theory.predict(pair, lamda, tree, beta, softmaxTemp)
			if prediction:
				predictions.append([prediction, theory.prior()])
			else: #prediction failed because we didn't have a complete theory
				newTheories = self.completeTheory(theory, numCompletionSamples)
				for t in newTheories:
					predictions.append([t.predict(pair, lamda, tree, beta, softmaxTemp), t.prior()])

		#TODO: The predicates are not always in the same order
		# and predicate list varies in size (becasue sometimes two things happen and
		#sometimes only one thing happens)

		embed()
		predicates = [p[0] for p in predictions[0][0]]
		weights = [prediction[1] for prediction in predictions]
		z = sum(weights)
		weights = weights/z
		predLists = [prediction[0] for prediction in predictions]
		probs = [[p[1]*weights[i] for p in predLists[i]] for i in range(len(predictions))]
		print len(weights), len(probs), len(probs[0])
		sums = [sum([p[i] for p in probs]) for i in range(len(predicates))]

		return zip(predicates, sums)


	def DFSinduction(self, theory, timesteps, maxNumTheories, verbose=True):
		"""
		DFS implementation of induction function to deal with very long induction time.
		"""

		if verbose:
			print "\nStart hyp space length:", len(self.hypothesisSpace)
			print "running induction on theory"
			theory.display()

		# If still have time to generate more theories
		if len(self.hypothesisSpace) - 1 < maxNumTheories: # Subtracting one because of the initial hypothesis we must start out with to do induction
			ts_index = theory.depth
			
			if verbose:
				print "Current theory depth: ", ts_index
				print "Explaining event", timesteps[ts_index].events
			
			# Explain current timestep
			newTheories = theory.explainTimeStep(timesteps[ts_index], timesteps[ts_index])
			self.nodes_generated += len(newTheories)
			if verbose:
				print "Possible new theories: ", len(newTheories)

			# If at the end of the timesteps list, add new theories to finalHypotheses
			if ts_index+1 == len(timesteps): # Need to add one, because you will create a theory of depth one greater than the length of the timesteps
				newTheoriesCount = 0
				for newTheory in newTheories:
					if all(newTheory.likelihood(ts)==1.0 for ts in timesteps):
						self.nodes_accepted +=1
						newTheoriesCount += 1
						self.hypothesisSpace.append(newTheory)
					else:
						self.nodes_eliminated +=1
				
				if verbose: 
					print "New theories that passed likelihood tests: ", newTheoriesCount
					print "New hyp space length: ", len(self.hypothesisSpace)
					print "Nodes created: {}. Nodes eliminated: {}. Nodes accepted: {}".format(self.nodes_generated, self.nodes_eliminated, self.nodes_accepted)


			# If in middle of timesteps, explain first timestep and add theories to final Hypotheses
			elif ts_index+1 != len(timesteps):
				acceptedTheories = []
				for t in newTheories:
					all_passed = True
					
					for ts in timesteps[:t.depth-1]: 			# Check that the theory can explain all timesteps
						if not t.likelihood(ts, sparse=True):
							self.nodes_eliminated +=1
							all_passed = False
							break
					
					if all_passed:
						self.nodes_accepted += 1
						acceptedTheories.append(t)
				newTheories = self.orderHypotheses(acceptedTheories)
				
				if verbose:
					print "New theories that passed likelihood tests: ", len(newTheories)
					for t in newTheories:
						t.display()
					print "Nodes created: {}. Nodes eliminated: {}. Nodes accepted: {}".format(self.nodes_generated, self.nodes_eliminated, self.nodes_accepted)
				
				for t in newTheories:
					t.dryingPaint = set()
				
				print [self.DFSinduction(t, timesteps, maxNumTheories, verbose) for t in newTheories]

		

	def runDFSInduction(self, trace, maxNumTheories, verbose=True):
		"""
		"""

		start = time.time()

		timesteps, result = trace
		temp_new_trace = ([timesteps[0]], None) # Just to run regular induction on first timestep

		# Analyze first timestep (to get some sprites in theory classes so that entropy doesn't face divide by zero error)
		self.induction(temp_new_trace, verbose=True)

		self.cleanHypothesisSpace([timesteps[0]], 1)
		init_hypotheses = self.orderHypotheses(self.hypothesisSpace) 
		
		
		self.hypothesisSpace = [] # Refresh the hypothesis space before DFS induction

		# This does DFS induction x times; not sure how to make it more like the behavior we want.
		for theory in init_hypotheses: 	# each of these theories has depth 1
			theory.display()
			self.DFSinduction(theory, timesteps, maxNumTheories, verbose=True)
		

		# Termination set induction
		if result:
			hypothesisSpaceWithTermConditions = []
			for theory in self.hypothesisSpace:
				theory.explainTermination(timesteps[-1], timesteps[:-1], result)
				hypothesisSpaceWithTermConditions.append(theory)

			self.hypothesisSpace = hypothesisSpaceWithTermConditions

		print "initial hypothesis space: ", len(self.hypothesisSpace)

		end = time.time()
	
		print "generated {} hypotheses in {} seconds".format(len(self.hypothesisSpace), end-start)

		return self.hypothesisSpace



	def induction(self, trace, verbose=True, allTraces=None):
		"""
		Iterates through trace, performing theory induction on each timestep
		"""
		T = Theory(self)
		T.initializeSpriteSet(self.vgdlSpriteParse)

		self.hypothesisSpace = [T]
		newTheories = []

		# For every timestep
		timesteps, result = trace
		for i in range(len(timesteps)): 
			timestep = timesteps[i]

			if verbose:
				print "explaining events {}".format(timestep.events)
				print "___________________________________________________________________"

			# For every theory
			for theory in self.hypothesisSpace:
				if theory.likelihood(timestep) < 1.0: 	# Theory needs to be changed
					newTheories.extend(theory.explainTimeStep(timestep, timestep))
			# Make sure only to add unique theories
			#print "Iterating through new theories"
			for theory in newTheories:
				# theory.display()
				theoryIsNew = True
				for existingTheory in self.hypothesisSpace:
					if theory==existingTheory:
						theoryIsNew = False
				if theoryIsNew:
					#print "ADDING NEW THEORIES IN INDUCTION --> now {} theories".format(len(self.hypothesisSpace))
					self.hypothesisSpace.append(theory) #TODO: numbering of theories should take place here.	

			# if allTraces:
			# 	for theory in self.hypothesisSpace:
			# 		for timesteps,result in allTraces:
			# 			if result:
			# 				theory.explainTermination(timesteps[-1], timesteps[:-1], result)
							
			# 		badTerminationSet = theory.getBadTerminationConditions(allTraces)
			# 		for t in badTerminationSet:
			# 			theory.terminationSet.remove(t)


			self.cleanHypothesisSpace(timesteps[0:i+1], 1) #All timesteps up to now should be fully explained
			
			#if verbose:
			print "{} hypotheses:".format(len(self.hypothesisSpace))
			
			# Sort hypotheses (right now by simple length metric), then print.
			hypotheses = sorted(self.hypothesisSpace, key=lambda x:len(x.interactionSet)*len(x.classes.keys()))
			
			if verbose:
				for h in hypotheses:
					h.display()
				print "___________________________________________________________________"
				print ""
		
		# Termination set induction
		if result:
			hypothesisSpaceWithTermConditions = []
			for theory in self.hypothesisSpace:
				theory.explainTermination(timesteps[-1], timesteps[:-1], result)
				hypothesisSpaceWithTermConditions.append(theory)

			self.hypothesisSpace = hypothesisSpaceWithTermConditions
		
		return self.hypothesisSpace

	def cleanHypothesisSpace(self, subtrace, threshold):
		"""
		Removes theories from hypothesisSpace if their likelihood for the timesteps
		passed in 'subtrace' is below threshold.
		"""
		# print "In cleanHypothesisSpace..."
		newHypothesisSpace = []

		#print "hypothesis space", self.hypothesisSpace
		for t in self.hypothesisSpace:
			#print "CHECKING THEORY:"
			#print " --> will check likelihood to see if the theory explains all of the timesteps (final check)"
			
			# print subtrace
			# for s in subtrace:
			# 	print "timestep: "
			# 	s.display()
			# 	print "likelihood:", t.likelihood(s)

			if all(t.likelihood(s)>=threshold for s in subtrace): #TODO: Issue might be here ?
				t.dryingPaint = set()
				newHypothesisSpace.append(t)
			

		self.hypothesisSpace = newHypothesisSpace
		# print "Done cleanHypothesisSpace...\n"
		return



