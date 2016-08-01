import itertools, random, copy, numpy.random, scipy.misc
import numpy as np
from class_theory_template_071916 import *
from taxonomy import *
from IPython import embed
from ontology import *
"""
Theory induction on VGDL Games
"""

'''
TODO: 7/14/16:
	Debug
	Other cleanup
	Change generateNumberConcepts to make the simpler possibilities:  >=1, <1, >0, <=0 


NOTES:
Current assumptions:
	no grammar over preconditions
	preconditions limited to claims about a SINGLE object
	preconditions limited to simple comparison operators.
	Events that take place at same timestep can only be because of the same preconditions.

'''
# TODO: Make a dictionary mapping the colors to a sprite object.

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
		# print (self.agentAction, self.agentState, self.events, self.gameState)
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
	def __init__(self, interaction, c1, c2, preconditions=set()):
		self.interaction = interaction
		self.slot1 = c1
		self.slot2 = c2
		self.preconditions = preconditions

	def display(self):
		if not self.preconditions:
			print self.interaction, self.slot1, self.slot2
		else:
			print self.interaction, self.slot1, self.slot2, [p.text for p in self.preconditions]
		return

	def asTuple(self):
		return (self.interaction, self.slot1, self.slot2)

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
		self.ruleType = "TimeoutRule"

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
		print (self.termination.stype, self.termination.limit, self.termination.win)
		return 

	def asTuple(self):
		return (self.ruleType, self.termination.stype, self.termination.limit, self.termination.win)


class MultiSpriteCounterRule(TerminationRule):
	""" Game ends when the sum of all sprites of types 'stypes' hits 'limit'. """
	def __init__(self, limit=0, win=True, stypes = []):
		self.termination = MultiSpriteCounter(limit=limit,win=win,stypes=stypes)
		self.ruleType = "MultiSpriteCounterRule"

	def display(self):
		print (self.termination.stypes, self.termination.limit, self.termination.win)
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


	def initializeSpriteSet(self, vgdlSpriteParse):
		self.spriteSet = vgdlSpriteParse

		# Get mapping from sprite color to Sprite object
		for s in self.spriteSet:
			self.spriteObjects[s.color] = s

	def addNewTerminationConditions(self, newTermConditions):
		self.terminationSet.extend(newTermConditions)

	"""Main functions"""

	def explainTimeStep(self, timestep, fullTimestep, currTheories=False):
		"""
		Returns a set of theories that explain all the events that took place at timestep.
		Hypotheticals can be passed as args to enable the explanation of multiple events in a single timestep.
		"""
		#print "in explainTimeStep..."
		# Base Case
		if len(timestep.events) == 1:
			theories = []
			if not currTheories:
				theories.extend(self.explainEvent(timestep.events[0], fullTimestep))
			else: # Generate theories based on hypothetical theories
				for theory in currTheories:
					newTheory = theory.explainEvent(timestep.events[0], fullTimestep)
					theories.extend(newTheory)
			#print "DONE EXPLAINTIMESTEP"
			return theories

		# Recursive Case
		else:
			theories = self.explainEvent(timestep.events[0], fullTimestep)
			updatedTimeStep = TimeStep(timestep.agentAction, timestep.agentState, timestep.events[1:], timestep.gameState)
			return self.explainTimeStep(updatedTimeStep, fullTimestep, theories)

	def explainEvent(self, event, timestep):
		"""
		Returns theories that explain the event, which is a tuple like:
		(bounceForward, BLUE, ORANGE)
		"""
		#print "in explainEvent..."
		theories = []

		#print " --> will check likelihood to get failCase (or just add the theory if the event is explained)"
		likelihood = self.likelihood(timestep)
		#print '\tlikelihood', likelihood

		if likelihood == 1:
			theories.append(self)
		else:
			failCase = self.getFailCases(event, timestep)
			#print "\tFail case: ", failCase
			if failCase in [1,2,3]:
				#print "ADD PRECONDITIONS"
				theories.extend(self.addPreconditions(event, timestep))
			elif failCase == 4: 
				#print "ADD RULE"
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
		time = result["time"]
		timeoutRule = TimeoutRule(limit=time, win=win)
		if not timeoutRule in self.terminationSet:
			self.terminationSet.append(timeoutRule)

	def likelihood(self, timestep, verbose=False):
		"""
		Makes sure that:
			-all events in the timestep were covered by the ruleset 
			-everything predicted in the ruleset happened.

		Right now returns only 1 or 0.
		"""
		#CE = self.checkEventsInTimeStep(timestep)
		#CP = self.checkPredictionsInTimeStep(timestep)
		
		#print "events in timestep {} | predictions in timestep {}".format(self.checkEventsInTimeStep(timestep), self.checkPredictionsInTimeStep(timestep))
		if self.checkEventsInTimeStep(timestep) and self.checkPredictionsInTimeStep(timestep):
			likelihood = 1.
		else:
			likelihood = 0.
		#print "Initial check", CE, CP
		#print "Second check", self.checkEventsInTimeStep(timestep), self.checkPredictionsInTimeStep(timestep)
		#print "\n"
		return likelihood


	def checkEventsInTimeStep(self, timestep):
		"""
		Check if all events in the timestep are covered by the interaction rule set.
		"""
		interpretations = [self.interpret(event) for event in timestep.events]
		return all([self.checkEvents(i, timestep) for i in interpretations])


	def checkPredictionsInTimeStep(self, timestep):
		"""
		Check if all predictions for the timestep actually occurred. 
		"""
		#Note: This fn cannot be exactly like checkPredictions(), becase here we don't care whether 'drying paint' is 
		#T or F. We need to actually check all the predictions.
		interpretations = [self.interpret(event).asTuple() for event in timestep.events if self.interpret(event) is not False]

		relevantRules = []
		for event in timestep.events:
			relevantRules.extend(self.findRelevantRules(
				event, timestep.agentState))

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
		#print 'in addRules...'
		newTheories = []
		possibleAssignments = self.searchForAssignments(event)

		obj1 = self.spriteObjects[event[1]]
		obj2 = self.spriteObjects[event[2]]


		if possibleAssignments:
			for assignment in possibleAssignments:
				interaction = InteractionRule(event[0], assignment[0], assignment[1]) #This isn't strictly necessary, but follows createChild requirements.
				
				classAssignments = [(assignment[0], obj1), (assignment[1], obj2)]
				newTheory = self.createChild([interaction, classAssignments])

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

		Ex) Event is a tuple: ('bounceForward', 'ORANGE', 'DARKBLUE')
		If we know that ORANGE=c1 and DARKBLUE=c2, returns the InteractionRule
		that corresponds to (bounceForward, c1, c2)
		"""
		obj1 = self.spriteObjects[event[1]]
		obj2 = self.spriteObjects[event[2]]

		c1, c2 = self.getClass(obj1), self.getClass(obj2)
		#print 'classes:', c1, c2
		if c1 and c2:
			#print 'new interaction rule!'
			return InteractionRule(event[0], c1, c2)
		else:
			return False

	def findRelatedRules(self, classPair, interactionList):
		#needs to take a list of interpretations or a list of interaction rules
		return [interaction for interaction in interactionList if classPair == interaction.asTuple()[1:]]
	
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
		addedRule = addInteractionRule(rule)
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

	

	def findRelevantRules(self, event, agentState, checkDryingPaint=False):
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

			if not checkDryingPaint:
				relevantRules.extend([rule for rule in rules if rule.asTuple()[1]==class1 and rule.asTuple()[2]==class2 and all(p.check(agentState) for p in rule.preconditions)])
			else:
				# Here we only return rules that are not in the drying paint. 
				relevantRules.extend([rule for rule in rules if not self.findRule(rule, self.dryingPaint) and rule.asTuple()[1]==class1 and rule.asTuple()[2]==class2 and all(p.check(agentState) for p in rule.preconditions)])

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
			if s.vgdlType == obj_Sprite.vgdlType and self.getClass(s):
				possibleClasses.append(self.getClass(s))

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
		print ""
		print "predicting interactions for {} with parameters:".format(pair)
		print "lambda = {}. beta = {}. tree = {}. softmax temp = {}".format(lamda, beta, tree.name, softmaxTemp)
		print "(lambda: extrapolation (1) vs. guess (0) balance)"
		print "(beta: ontology (1) vs. rule-similarity (0) balance)"
		print ""

		extrapolatedRules = [[r[0], r[1]*lamda] for r in self.extrapolateRule(pair, tree, beta)]
		guessedRules = [[r[0], r[1]*(1-lamda)] for r in self.guessRule()]
		
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
		
		for o in outList:
			print o
		return outList

	def guessRule(self):
		#Currently returns interactions (no preconditions, and not in the form of interactionRules)
		#TODO: changeResource, spawnifHasMore require another argument. Add these and figure out how
		#to pass those args. Maybe this is best done in the step that creates interactionRules
		#in predict(). Also decide how to deal with values of optional args. Right now you'll
		#just make predictions based on default args.
		predicateList = ['killSprite', 'cloneSprite', 'stepBack', 'transformTo', 'undoAll',
		'bounceForward', 'conveySprite', 'windGust', 'slipForward', 'attractGaze', 'turnAround',
		'reverseDirection', 'flipDirection', 'bounceDirection', 'wallBounce', 'wallStop',
		'killIfSlow', 'killIfFromAbove', 'killIfAlive', 'collectResource', 'killIfHasMore',
		'killIfOtherHasMore', 'killIfHasLess', 'killIfOtherHasLess', 'wrapAround',
		'pullWithIt', 'teleportToExit']
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

	def levenshtein(self, s1, s2):
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
		self.hypothesisSpace = set()
		self.theoryCount = 0
		self.vgdlSpriteParse = self.makeSpriteParse()

		#inherit ontology from VGDL
		self.VGDLTree = VGDLTree

	def makeSpriteParse(self):
		s = SpriteParser()
		return s.parseGame(self.vgdlString)

	def display(self):
		print self.theoryCount

	def induction(self, trace, verbose=True, allTraces = None):
		"""
		Iterates through trace, performing theory induction on each timestep
		"""
		if allTraces == None:
			allTraces = [trace]

		if len(self.hypothesisSpace) == 0:
			T = Theory(self)
			T.initializeSpriteSet(self.vgdlSpriteParse)
			self.hypothesisSpace = set([T])

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
				#print "In induction..."
				#print " --> will check likelihood to see if we need to extend our theory to explain the new TimeStep"
				if theory.likelihood(timestep) < 1.0: 	# Theory needs to be changed
					#print "likelihood", theory.likelihood(timestep)
					print "THEORY SHOULD CHANGE"
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
					# print "ADDING NEW THEORIES IN INDUCTION --> now {} theories".format(len(self.hypothesisSpace))
					self.hypothesisSpace.add(theory) #TODO: numbering of theories should take place here.	
				# else:
				# 	print "THEORY exists IN HYPOTHESIS SPACE"
				# 	theory.display()


			self.cleanHypothesisSpace(timesteps[0:i+1], 1) #All timesteps up to now should be fully explained
			
			#if verbose:
			print "{} hypotheses:".format(len(self.hypothesisSpace))
			
			# Sort hypotheses (right now by simple length metric), then print.
			hypotheses = sorted(list(self.hypothesisSpace), key=lambda x:len(x.interactionSet)*len(x.classes.keys()))
			
			if verbose:
				for h in hypotheses:
					h.display()
				print "___________________________________________________________________"
				print ""
		
		# Termination set induction
		hypothesisSpaceWithTermConditions = set()
		for timesteps,result in allTraces:

			if result:
				for theory in self.hypothesisSpace:
					print result, len(allTraces)
					theory.explainTermination(timesteps[-1], timesteps[:-1], result)
					hypothesisSpaceWithTermConditions.add(theory)

		self.hypothesisSpace = hypothesisSpaceWithTermConditions
		return self.hypothesisSpace


	def inductionOverMultipleTraces(self, traces, verbose=True):
		for i in range(len(traces)):
			trace = traces[i]
			self.induction(trace,verbose=verbose,allTraces=traces[:i+1])

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
			

		self.hypothesisSpace = set(newHypothesisSpace)
		# print "Done cleanHypothesisSpace...\n"
		return
