import itertools, random, copy
from sampleVGDLString import *
from class_theory_template_071916 import *
from IPython import embed
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

class TerminationCondition:
	"""
	TODO: eventually incorporate multiple sprite termination conditions and timeout termination conditions.
	At the moment, we assume single sprite condtions
	"""
	def __init__(self,sclass,snumber,win):
		"""sclass = sprite class, snumber = sprite number, win = whether termination is a win"""
		self.sclass = sclass
		self.snumber = snumber
		self.win = win

	def display(self):
		print self.sclass, self.snumber, self.win
		return

	def asTuple(self):
		return (self.sclass, self.snumber, self.win)

	def __eq__(self,other):
		return self.asTuple() == other.asTuple()

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
		for i in self.spriteSet:
			print i.color, i
		print 

		# Get mapping from sprite color to Sprite object
		for s in self.spriteSet:
			self.spriteObjects[s.color] = s

		# for i in range(len(self.spriteSet)): #TODO: Build this up from scratch, rather than initialize all objs into separate classes?
		# 	sprite = self.spriteSet[i]
		# 	sprite.className = 'c'+str(i)			# TODO: Use classes based on vgdl type?
		# 	self.classes[sprite.className] = [sprite]

	"""Main functions"""

	def explainTimeStep(self, timestep, fullTimestep, currTheories=False):
		"""
		Returns a set of theories that explain all the events that took place at timestep.
		Hypotheticals can be passed as args to enable the explanation of multiple events in a single timestep.
		"""
		# Base Case
		if len(timestep.events) == 1:
			theories = []
			if not currTheories:
				theories.extend(self.explainEvent(timestep.events[0], fullTimestep))
			else: # Generate theories based on hypothetical theories
				for theory in currTheories:
					newTheory = theory.explainEvent(timestep.events[0], fullTimestep)
					theories.extend(newTheory)

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

		likelihood = self.likelihood(timestep)
		#print '\tlikelihood', likelihood

		if likelihood == 1:
			theories.append(self)
		else:
			failCase = self.getFailCases(event, timestep)
			#print "\tFail case: ", failCase
			if failCase in [1,2,3]:
				theories.extend(self.addPreconditions(event, timestep))
			elif failCase == 4: 
				theories.extend(self.addRules(event))

		return theories

	def explainTermination(self, timestep, prevTimeSteps,result):
		"""
		adds all hypotheses about the termination conditions to the terminationSet
		params:
		timestep: the very last time step (at which termination occurs)
		prevTimeSteps: all time steps previous to the termination time step
		result: a dictionary for which the key 'win' is a boolean describing whether the game was won
		"""
		win = result['win']
		objsWithDiffAmounts = {} # objects which have different amounts in the termination time step from any previous timestep
		for obj in timestep.gameState['objects']:
			timestep_amt = len(timestep.gameState['objects'][obj])
			timestep_amt_unique = not timestep_amt in [len(prevTimeStep.gameState['objects'][obj]) for prevTimeStep in prevTimeSteps]
			if timestep_amt_unique:
				objsWithDiffAmounts[obj] = (win,timestep_amt)

			# timestep_amt_unique = True
			# for prevTimeStep in prevTimeSteps:
			# 	prev_timestep_amt = len(prevTimeStep['objects'][obj])
			# 	if timestep_amt == prev_timestep_amt:
			# 		timestep_amt_unique = False

		for event in timestep.events:
			for i in [1,2]:
				terminationClass = event[i] #self.getClass(event[i])
				if terminationClass in objsWithDiffAmounts:
					win,timestep_amt = objsWithDiffAmounts[terminationClass]
					terminationCondition = TerminationCondition(terminationClass,timestep_amt,win)
					self.terminationSet.append(terminationCondition)


	def likelihood(self, timestep, verbose=False):
		"""
		Makes sure that:
			-all events in the timestep were covered by the ruleset 
			-everything predicted in the ruleset happened.

		Right now returns only 1 or 0.
		"""
		#print "events in timestep {} | predictions in timestep {}".format(self.checkEventsInTimeStep(timestep), self.checkPredictionsInTimeStep(timestep))
		if self.checkEventsInTimeStep(timestep) and self.checkPredictionsInTimeStep(timestep):
			likelihood = 1.
		else:
			likelihood = 0.

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
			if not False in relevantRules:
				return all([rule.asTuple() in interpretations for rule in relevantRules])
			else:
				return () #There were no relevant rules; need to create new rule.
		else:
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
		interpretation = self.interpret(event)
		relevantRules = []
		if interpretation:
			class1, class2 = interpretation.asTuple()[1], interpretation.asTuple()[2]
			
			# This should not include any rules that don't satisfy the current preconditions
			rules = [rule for rule in self.interactionSet]


			if not checkDryingPaint:
				relevantRules.extend([rule for rule in rules if rule.asTuple()[1]==class1 and rule.asTuple()[2]==class2 and all(p.check(agentState) for p in rule.preconditions)])
			else:
				# Here we only return rules that are not in the drying paint. 
				relevantRules.extend([rule for rule in rules if not self.findRule(rule, self.dryingPaint) and rule.asTuple()[1]==class1 and rule.asTuple()[2]==class2 and all(p.check(agentState) for p in rule.preconditions)])
		else:
			relevantRules.append(False)
		if False not in relevantRules:
			return relevantRules
		else:
			return [False]



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
		print self.classes
		print

	def displayTerminationSet(self):
		print ""
		print "TerminationSet:"
		for rule in self.terminationSet:
			rule.display()

	def display(self):
		print "_______"
		self.displayRules()
		self.displayClasses()
		self.displayTerminationSet()
		return

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return all([
				self.spriteSet == other.spriteSet, 
				self.levelMapping == other.levelMapping, 
				self.interactionSet == other.interactionSet,
				self.terminationSet == other.terminationSet,
				self.classes == other.classes,
				self.predicates == other.predicates])
		else:
			return False

	def __ne__(self, other):
		return not self.__eq__(other)




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

	def makeSpriteParse(self):
		s = SpriteParser()
		return s.parseGame(self.vgdlString)

	def display(self):
		print self.theoryCount

	def induction(self, trace):
		"""
		Iterates through trace, performing theory induction on each timestep
		"""
		T = Theory(self)
		T.initializeSpriteSet(self.vgdlSpriteParse)

		self.hypothesisSpace = set([T])
		newTheories = []

		# For every timestep
		timesteps, result = trace
		for i in range(len(timesteps)): 
			timestep = timesteps[i]
			print "explaining events {}".format(timestep.events)
			print "___________________________________________________________________"

			# For every theory
			for theory in self.hypothesisSpace:
				if theory.likelihood(timestep) < 1.0: 	# Theory needs to be changed
					#print "likelihood", theory.likelihood(timestep)
					newTheories.extend(theory.explainTimeStep(timestep, timestep))

			for theory in newTheories:
				if theory not in self.hypothesisSpace:
					self.hypothesisSpace.add(theory) #TODO: numbering of theories should take place here.	

			self.cleanHypothesisSpace(timesteps[0:i+1], 1) #All timesteps up to now should be fully explained
			print "{} hypotheses:".format(len(self.hypothesisSpace))
			
			# Sort hypotheses (right now by simple length metric), then print.
			hypotheses = sorted(list(self.hypothesisSpace), key=lambda x:len(x.interactionSet)*len(x.classes.keys()))
			for h in hypotheses:
				h.display()
			print "___________________________________________________________________"
			print ""
		
		hypothesisSpaceWithTermConditions = set()
		for theory in self.hypothesisSpace:
			theory.explainTermination(timesteps[-1], timesteps[:-1], result)
			hypothesisSpaceWithTermConditions.add(theory)

		self.hypothesisSpace = hypothesisSpaceWithTermConditions
		
		return self.hypothesisSpace

	def cleanHypothesisSpace(self, subtrace, threshold):
		"""
		Removes theories from hypothesisSpace if their likelihood for the timesteps
		passed in 'subtrace' is below threshold.
		"""
		newHypothesisSpace = []
		for t in self.hypothesisSpace:
			if all(t.likelihood(s)>=threshold for s in subtrace):
				t.dryingPaint = set()
				newHypothesisSpace.append(t)
		self.hypothesisSpace = set(newHypothesisSpace)
		return

g = Game(push_game)

# # Testing preconditions
# rawTrace = [ 
# {'agentAction': None, 'agentState': {}, 'effectList': [('killSprite', 'DARKBLUE', 'BLUE')]}, 
# {'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('collectResource', 'DARKBLUE', 'RED'), ('killSprite', 'DARKBLUE', 'RED')]}, 
# {'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('bounceForward', 'DARKBLUE', 'BLUE')]}, 
# {'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE')]}, 
# {'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('killSprite', 'DARKBLUE', 'GOLD')]}
# ]


# '''
# # Testing lots of different actions
# rawTrace = [
#         {'agentAction': None, 'agentState': {}, 'effectList': []}, 
#         {'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('collectResource', 'DARKBLUE', 'RED'), ('killSprite', 'DARKBLUE', 'RED')]}, 
#         {'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('killSprite', 'DARKBLUE', 'BLUE')]}, 
#         {'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE')]}, 
#         {'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE'), ('undoAll', 'ORANGE', 'BROWN')]}, 
#         {'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE')]}, 
#         {'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('bounceForward', 'DARKBLUE', 'PINK')]}, 
#         {'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('bounceForward', 'DARKBLUE', 'PINK')]},
#         {'agentAction': None, 'agentState': {'treasure': 1, 'trap': 1}, 'effectList': [('collectResource', 'DARKBLUE', 'GREEN'), ('killSprite', 'DARKBLUE', 'GREEN')]}, 
#         {'agentAction': 'down', 'agentState': {'treasure': 1, 'trap': 1}, 'effectList': [('changeResource', 'DARKBLUE', 'WHITE', -1), ('killSprite', 'DARKBLUE', 'BROWN')]}]
# '''
# trace = [TimeStep(tr['agentAction'], tr['agentState'], tr['effectList']) for tr in rawTrace]

# hypotheses=list(g.induction(trace))

rawTrace2 = [
    [
        {'gameState': {'ended': False, 'score': 0, 'objects': {'BLUE': {(305, 427): {'speed': None}, (122, 305): {'speed': None}}, 'BROWN': {(488, 427): {'speed': None, 'limit': 3}, (488, 183): {'speed': None, 'limit': 3}}, 'GOLD': {(671, 183): {'speed': None}}, 'LIGHTBLUE': {(427, 244): {'speed': None}}, 'DARKBLUE': {(305, 305): {'speed': 1, 'resources': {'medicine': 1}}}, 'GREEN': {(671, 366): {'speed': None, 'limit': 5}}, 'PINK': {(183, 427): {'speed': None}, (183, 61): {'speed': None}}, 'ORANGE': {(244, 122): {'speed': None}, (122, 366): {'speed': None}, (366, 183): {'speed': None}}, 'BLACK': {(305, 488): {'speed': None}, (732, 305): {'speed': None}, (0, 122): {'speed': None}, (732, 427): {'speed': None}, (305, 0): {'speed': None}, (610, 244): {'speed': None}, (427, 488): {'speed': None}, (244, 0): {'speed': None}, (0, 305): {'speed': None}, (488, 305): {'speed': None}, (0, 427): {'speed': None}, (183, 0): {'speed': None}, (244, 488): {'speed': None}, (671, 244): {'speed': None}, (0, 61): {'speed': None}, (549, 488): {'speed': None}, (671, 427): {'speed': None}, (61, 488): {'speed': None}, (0, 244): {'speed': None}, (732, 61): {'speed': None}, (122, 0): {'speed': None}, (61, 0): {'speed': None}, (488, 244): {'speed': None}, (732, 244): {'speed': None}, (732, 366): {'speed': None}, (732, 0): {'speed': None}, (671, 0): {'speed': None}, (366, 488): {'speed': None}, (0, 183): {'speed': None}, (0, 0): {'speed': None}, (671, 488): {'speed': None}, (610, 488): {'speed': None}, (732, 183): {'speed': None}, (183, 488): {'speed': None}, (610, 0): {'speed': None}, (549, 0): {'speed': None}, (122, 244): {'speed': None}, (61, 244): {'speed': None}, (488, 0): {'speed': None}, (732, 488): {'speed': None}, (427, 0): {'speed': None}, (122, 488): {'speed': None}, (549, 244): {'speed': None}, (488, 488): {'speed': None}, (366, 0): {'speed': None}, (0, 366): {'speed': None}, (732, 122): {'speed': None}, (0, 488): {'speed': None}, (549, 61): {'speed': None}}, 'WHITE': {(305, 61): {'speed': None, 'limit': 3}}, 'RED': {(122, 183): {'speed': None, 'limit': 5}, (305, 366): {'speed': None, 'limit': 5}}}, 'win': None}, 'agentAction': None, 'agentState': {'medicine': 1}, 'effectList': [('changeResource', 'DARKBLUE', 'WHITE', 1), ('killSprite', 'DARKBLUE', 'WHITE')]},
        {'gameState': {'ended': False, 'score': 0, 'objects': {'BLUE': {(305, 427): {'speed': None}, (122, 305): {'speed': None}}, 'BROWN': {(488, 427): {'speed': None, 'limit': 3}, (488, 183): {'speed': None, 'limit': 3}}, 'GOLD': {(671, 183): {'speed': None}}, 'LIGHTBLUE': {(427, 244): {'speed': None}}, 'DARKBLUE': {(366, 183): {'speed': 1, 'resources': {'medicine': 1}}}, 'GREEN': {(671, 366): {'speed': None, 'limit': 5}}, 'PINK': {(183, 427): {'speed': None}, (183, 61): {'speed': None}}, 'ORANGE': {(244, 122): {'speed': None}, (122, 366): {'speed': None}, (427, 183): {'speed': None}}, 'BLACK': {(305, 488): {'speed': None}, (732, 305): {'speed': None}, (0, 122): {'speed': None}, (732, 427): {'speed': None}, (305, 0): {'speed': None}, (610, 244): {'speed': None}, (427, 488): {'speed': None}, (244, 0): {'speed': None}, (0, 305): {'speed': None}, (488, 305): {'speed': None}, (0, 427): {'speed': None}, (183, 0): {'speed': None}, (244, 488): {'speed': None}, (671, 244): {'speed': None}, (0, 61): {'speed': None}, (549, 488): {'speed': None}, (671, 427): {'speed': None}, (61, 488): {'speed': None}, (0, 244): {'speed': None}, (732, 61): {'speed': None}, (122, 0): {'speed': None}, (61, 0): {'speed': None}, (488, 244): {'speed': None}, (732, 244): {'speed': None}, (732, 366): {'speed': None}, (732, 0): {'speed': None}, (671, 0): {'speed': None}, (366, 488): {'speed': None}, (0, 183): {'speed': None}, (0, 0): {'speed': None}, (671, 488): {'speed': None}, (610, 488): {'speed': None}, (732, 183): {'speed': None}, (183, 488): {'speed': None}, (610, 0): {'speed': None}, (549, 0): {'speed': None}, (122, 244): {'speed': None}, (61, 244): {'speed': None}, (488, 0): {'speed': None}, (732, 488): {'speed': None}, (427, 0): {'speed': None}, (122, 488): {'speed': None}, (549, 244): {'speed': None}, (488, 488): {'speed': None}, (366, 0): {'speed': None}, (0, 366): {'speed': None}, (732, 122): {'speed': None}, (0, 488): {'speed': None}, (549, 61): {'speed': None}}, 'WHITE': {(305, 61): {'speed': None, 'limit': 3}}, 'RED': {(122, 183): {'speed': None, 'limit': 5}, (305, 366): {'speed': None, 'limit': 5}}}, 'win': None}, 'agentAction': None, 'agentState': {'medicine': 1}, 'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE')]},
        {'gameState': {'ended': False, 'score': 0, 'objects': {'BLUE': {(305, 427): {'speed': None}, (122, 305): {'speed': None}}, 'BROWN': {(488, 427): {'speed': None, 'limit': 3}}, 'GOLD': {(671, 183): {'speed': None}}, 'LIGHTBLUE': {(427, 244): {'speed': None}}, 'DARKBLUE': {(488, 183): {'speed': 1, 'resources': {'medicine': 0}}}, 'GREEN': {(671, 366): {'speed': None, 'limit': 5}}, 'PINK': {(183, 427): {'speed': None}, (183, 61): {'speed': None}}, 'ORANGE': {(244, 122): {'speed': None}, (122, 366): {'speed': None}, (427, 183): {'speed': None}}, 'BLACK': {(305, 488): {'speed': None}, (732, 305): {'speed': None}, (0, 122): {'speed': None}, (732, 427): {'speed': None}, (305, 0): {'speed': None}, (610, 244): {'speed': None}, (427, 488): {'speed': None}, (244, 0): {'speed': None}, (0, 305): {'speed': None}, (488, 305): {'speed': None}, (0, 427): {'speed': None}, (183, 0): {'speed': None}, (244, 488): {'speed': None}, (671, 244): {'speed': None}, (0, 61): {'speed': None}, (549, 488): {'speed': None}, (671, 427): {'speed': None}, (61, 488): {'speed': None}, (0, 244): {'speed': None}, (732, 61): {'speed': None}, (122, 0): {'speed': None}, (61, 0): {'speed': None}, (488, 244): {'speed': None}, (732, 244): {'speed': None}, (732, 366): {'speed': None}, (732, 0): {'speed': None}, (671, 0): {'speed': None}, (366, 488): {'speed': None}, (0, 183): {'speed': None}, (0, 0): {'speed': None}, (671, 488): {'speed': None}, (610, 488): {'speed': None}, (732, 183): {'speed': None}, (183, 488): {'speed': None}, (610, 0): {'speed': None}, (549, 0): {'speed': None}, (122, 244): {'speed': None}, (61, 244): {'speed': None}, (488, 0): {'speed': None}, (732, 488): {'speed': None}, (427, 0): {'speed': None}, (122, 488): {'speed': None}, (549, 244): {'speed': None}, (488, 488): {'speed': None}, (366, 0): {'speed': None}, (0, 366): {'speed': None}, (732, 122): {'speed': None}, (0, 488): {'speed': None}, (549, 61): {'speed': None}}, 'WHITE': {(305, 61): {'speed': None, 'limit': 3}}, 'RED': {(122, 183): {'speed': None, 'limit': 5}, (305, 366): {'speed': None, 'limit': 5}}}, 'win': None}, 'agentAction': None, 'agentState': {'medicine': 0}, 'effectList': [('changeResource', 'DARKBLUE', 'WHITE', -1), ('killSprite', 'DARKBLUE', 'BROWN')]},
        {'gameState': {'ended': False, 'score': 0, 'objects': {'BLUE': {(305, 427): {'speed': None}, (122, 305): {'speed': None}}, 'BROWN': {(488, 427): {'speed': None, 'limit': 3}}, 'GOLD': {}, 'LIGHTBLUE': {(427, 244): {'speed': None}}, 'DARKBLUE': {(671, 183): {'speed': 1, 'resources': {'medicine': 0}}}, 'GREEN': {(671, 366): {'speed': None, 'limit': 5}}, 'PINK': {(183, 427): {'speed': None}, (183, 61): {'speed': None}}, 'ORANGE': {(244, 122): {'speed': None}, (122, 366): {'speed': None}, (427, 183): {'speed': None}}, 'BLACK': {(305, 488): {'speed': None}, (732, 305): {'speed': None}, (0, 122): {'speed': None}, (732, 427): {'speed': None}, (305, 0): {'speed': None}, (610, 244): {'speed': None}, (427, 488): {'speed': None}, (244, 0): {'speed': None}, (0, 305): {'speed': None}, (488, 305): {'speed': None}, (0, 427): {'speed': None}, (183, 0): {'speed': None}, (244, 488): {'speed': None}, (671, 244): {'speed': None}, (0, 61): {'speed': None}, (549, 488): {'speed': None}, (671, 427): {'speed': None}, (61, 488): {'speed': None}, (0, 244): {'speed': None}, (732, 61): {'speed': None}, (122, 0): {'speed': None}, (61, 0): {'speed': None}, (488, 244): {'speed': None}, (732, 244): {'speed': None}, (732, 366): {'speed': None}, (732, 0): {'speed': None}, (671, 0): {'speed': None}, (366, 488): {'speed': None}, (0, 183): {'speed': None}, (0, 0): {'speed': None}, (671, 488): {'speed': None}, (610, 488): {'speed': None}, (732, 183): {'speed': None}, (183, 488): {'speed': None}, (610, 0): {'speed': None}, (549, 0): {'speed': None}, (122, 244): {'speed': None}, (61, 244): {'speed': None}, (488, 0): {'speed': None}, (732, 488): {'speed': None}, (427, 0): {'speed': None}, (122, 488): {'speed': None}, (549, 244): {'speed': None}, (488, 488): {'speed': None}, (366, 0): {'speed': None}, (0, 366): {'speed': None}, (732, 122): {'speed': None}, (0, 488): {'speed': None}, (549, 61): {'speed': None}}, 'WHITE': {(305, 61): {'speed': None, 'limit': 3}}, 'RED': {(122, 183): {'speed': None, 'limit': 5}, (305, 366): {'speed': None, 'limit': 5}}}, 'win': None}, 'agentAction': None, 'agentState': {'medicine': 0}, 'effectList': [('killSprite', 'DARKBLUE', 'GOLD')]},
    ],    
    {'ended': True, 'win': True}
]

'''
rawTrace2 = [
    [
        {'gameState': {'ended': False, 'score': 0, 'objects': {'BLUE': {(305, 427): {'speed': None}, (122, 305): {'speed': None}}, 'BROWN': {(488, 427): {'speed': None, 'limit': 3}, (488, 183): {'speed': None, 'limit': 3}}, 'GOLD': {(671, 183): {'speed': None}}, 'LIGHTBLUE': {(427, 244): {'speed': None}}, 'DARKBLUE': {(305, 305): {'speed': 1, 'resources': {'medicine': 1}}}, 'GREEN': {(671, 366): {'speed': None, 'limit': 5}}, 'PINK': {(183, 427): {'speed': None}, (183, 61): {'speed': None}}, 'ORANGE': {(244, 122): {'speed': None}, (122, 366): {'speed': None}, (366, 183): {'speed': None}}, 'BLACK': {(305, 488): {'speed': None}, (732, 305): {'speed': None}, (0, 122): {'speed': None}, (732, 427): {'speed': None}, (305, 0): {'speed': None}, (610, 244): {'speed': None}, (427, 488): {'speed': None}, (244, 0): {'speed': None}, (0, 305): {'speed': None}, (488, 305): {'speed': None}, (0, 427): {'speed': None}, (183, 0): {'speed': None}, (244, 488): {'speed': None}, (671, 244): {'speed': None}, (0, 61): {'speed': None}, (549, 488): {'speed': None}, (671, 427): {'speed': None}, (61, 488): {'speed': None}, (0, 244): {'speed': None}, (732, 61): {'speed': None}, (122, 0): {'speed': None}, (61, 0): {'speed': None}, (488, 244): {'speed': None}, (732, 244): {'speed': None}, (732, 366): {'speed': None}, (732, 0): {'speed': None}, (671, 0): {'speed': None}, (366, 488): {'speed': None}, (0, 183): {'speed': None}, (0, 0): {'speed': None}, (671, 488): {'speed': None}, (610, 488): {'speed': None}, (732, 183): {'speed': None}, (183, 488): {'speed': None}, (610, 0): {'speed': None}, (549, 0): {'speed': None}, (122, 244): {'speed': None}, (61, 244): {'speed': None}, (488, 0): {'speed': None}, (732, 488): {'speed': None}, (427, 0): {'speed': None}, (122, 488): {'speed': None}, (549, 244): {'speed': None}, (488, 488): {'speed': None}, (366, 0): {'speed': None}, (0, 366): {'speed': None}, (732, 122): {'speed': None}, (0, 488): {'speed': None}, (549, 61): {'speed': None}}, 'WHITE': {(305, 61): {'speed': None, 'limit': 3}}, 'RED': {(122, 183): {'speed': None, 'limit': 5}, (305, 366): {'speed': None, 'limit': 5}}}, 'win': None}, 'agentAction': None, 'agentState': {'medicine': 1}, 'effectList': [('changeResource', 'DARKBLUE', 'WHITE', 1), ('killSprite', 'DARKBLUE', 'WHITE')]},
        {'gameState': {'ended': False, 'score': 0, 'objects': {'BLUE': {(305, 427): {'speed': None}, (122, 305): {'speed': None}}, 'BROWN': {(488, 427): {'speed': None, 'limit': 3}, (488, 183): {'speed': None, 'limit': 3}}, 'GOLD': {(671, 183): {'speed': None}}, 'LIGHTBLUE': {(427, 244): {'speed': None}}, 'DARKBLUE': {(366, 183): {'speed': 1, 'resources': {'medicine': 1}}}, 'GREEN': {(671, 366): {'speed': None, 'limit': 5}}, 'PINK': {(183, 427): {'speed': None}, (183, 61): {'speed': None}}, 'ORANGE': {(244, 122): {'speed': None}, (122, 366): {'speed': None}, (427, 183): {'speed': None}}, 'BLACK': {(305, 488): {'speed': None}, (732, 305): {'speed': None}, (0, 122): {'speed': None}, (732, 427): {'speed': None}, (305, 0): {'speed': None}, (610, 244): {'speed': None}, (427, 488): {'speed': None}, (244, 0): {'speed': None}, (0, 305): {'speed': None}, (488, 305): {'speed': None}, (0, 427): {'speed': None}, (183, 0): {'speed': None}, (244, 488): {'speed': None}, (671, 244): {'speed': None}, (0, 61): {'speed': None}, (549, 488): {'speed': None}, (671, 427): {'speed': None}, (61, 488): {'speed': None}, (0, 244): {'speed': None}, (732, 61): {'speed': None}, (122, 0): {'speed': None}, (61, 0): {'speed': None}, (488, 244): {'speed': None}, (732, 244): {'speed': None}, (732, 366): {'speed': None}, (732, 0): {'speed': None}, (671, 0): {'speed': None}, (366, 488): {'speed': None}, (0, 183): {'speed': None}, (0, 0): {'speed': None}, (671, 488): {'speed': None}, (610, 488): {'speed': None}, (732, 183): {'speed': None}, (183, 488): {'speed': None}, (610, 0): {'speed': None}, (549, 0): {'speed': None}, (122, 244): {'speed': None}, (61, 244): {'speed': None}, (488, 0): {'speed': None}, (732, 488): {'speed': None}, (427, 0): {'speed': None}, (122, 488): {'speed': None}, (549, 244): {'speed': None}, (488, 488): {'speed': None}, (366, 0): {'speed': None}, (0, 366): {'speed': None}, (732, 122): {'speed': None}, (0, 488): {'speed': None}, (549, 61): {'speed': None}}, 'WHITE': {(305, 61): {'speed': None, 'limit': 3}}, 'RED': {(122, 183): {'speed': None, 'limit': 5}, (305, 366): {'speed': None, 'limit': 5}}}, 'win': None}, 'agentAction': None, 'agentState': {'medicine': 1}, 'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE')]},
        {'gameState': {'ended': False, 'score': 0, 'objects': {'BLUE': {(305, 427): {'speed': None}, (122, 305): {'speed': None}}, 'BROWN': {(488, 427): {'speed': None, 'limit': 3}}, 'GOLD': {(671, 183): {'speed': None}}, 'LIGHTBLUE': {(427, 244): {'speed': None}}, 'DARKBLUE': {(488, 183): {'speed': 1, 'resources': {'medicine': 0}}}, 'GREEN': {(671, 366): {'speed': None, 'limit': 5}}, 'PINK': {(183, 427): {'speed': None}, (183, 61): {'speed': None}}, 'ORANGE': {(244, 122): {'speed': None}, (122, 366): {'speed': None}, (427, 183): {'speed': None}}, 'BLACK': {(305, 488): {'speed': None}, (732, 305): {'speed': None}, (0, 122): {'speed': None}, (732, 427): {'speed': None}, (305, 0): {'speed': None}, (610, 244): {'speed': None}, (427, 488): {'speed': None}, (244, 0): {'speed': None}, (0, 305): {'speed': None}, (488, 305): {'speed': None}, (0, 427): {'speed': None}, (183, 0): {'speed': None}, (244, 488): {'speed': None}, (671, 244): {'speed': None}, (0, 61): {'speed': None}, (549, 488): {'speed': None}, (671, 427): {'speed': None}, (61, 488): {'speed': None}, (0, 244): {'speed': None}, (732, 61): {'speed': None}, (122, 0): {'speed': None}, (61, 0): {'speed': None}, (488, 244): {'speed': None}, (732, 244): {'speed': None}, (732, 366): {'speed': None}, (732, 0): {'speed': None}, (671, 0): {'speed': None}, (366, 488): {'speed': None}, (0, 183): {'speed': None}, (0, 0): {'speed': None}, (671, 488): {'speed': None}, (610, 488): {'speed': None}, (732, 183): {'speed': None}, (183, 488): {'speed': None}, (610, 0): {'speed': None}, (549, 0): {'speed': None}, (122, 244): {'speed': None}, (61, 244): {'speed': None}, (488, 0): {'speed': None}, (732, 488): {'speed': None}, (427, 0): {'speed': None}, (122, 488): {'speed': None}, (549, 244): {'speed': None}, (488, 488): {'speed': None}, (366, 0): {'speed': None}, (0, 366): {'speed': None}, (732, 122): {'speed': None}, (0, 488): {'speed': None}, (549, 61): {'speed': None}}, 'WHITE': {(305, 61): {'speed': None, 'limit': 3}}, 'RED': {(122, 183): {'speed': None, 'limit': 5}, (305, 366): {'speed': None, 'limit': 5}}}, 'win': None}, 'agentAction': None, 'agentState': {'medicine': 0}, 'effectList': [('changeResource', 'DARKBLUE', 'WHITE', -1), ('killSprite', 'DARKBLUE', 'BROWN')]},
        {'gameState': {'ended': False, 'score': 0, 'objects': {'BLUE': {(305, 427): {'speed': None}, (122, 305): {'speed': None}}, 'BROWN': {(488, 427): {'speed': None, 'limit': 3}}, 'GOLD': {}, 'LIGHTBLUE': {(427, 244): {'speed': None}}, 'DARKBLUE': {(671, 183): {'speed': 1, 'resources': {'medicine': 0}}}, 'GREEN': {(671, 366): {'speed': None, 'limit': 5}}, 'PINK': {(183, 427): {'speed': None}, (183, 61): {'speed': None}}, 'ORANGE': {(244, 122): {'speed': None}, (122, 366): {'speed': None}, (427, 183): {'speed': None}}, 'BLACK': {(305, 488): {'speed': None}, (732, 305): {'speed': None}, (0, 122): {'speed': None}, (732, 427): {'speed': None}, (305, 0): {'speed': None}, (610, 244): {'speed': None}, (427, 488): {'speed': None}, (244, 0): {'speed': None}, (0, 305): {'speed': None}, (488, 305): {'speed': None}, (0, 427): {'speed': None}, (183, 0): {'speed': None}, (244, 488): {'speed': None}, (671, 244): {'speed': None}, (0, 61): {'speed': None}, (549, 488): {'speed': None}, (671, 427): {'speed': None}, (61, 488): {'speed': None}, (0, 244): {'speed': None}, (732, 61): {'speed': None}, (122, 0): {'speed': None}, (61, 0): {'speed': None}, (488, 244): {'speed': None}, (732, 244): {'speed': None}, (732, 366): {'speed': None}, (732, 0): {'speed': None}, (671, 0): {'speed': None}, (366, 488): {'speed': None}, (0, 183): {'speed': None}, (0, 0): {'speed': None}, (671, 488): {'speed': None}, (610, 488): {'speed': None}, (732, 183): {'speed': None}, (183, 488): {'speed': None}, (610, 0): {'speed': None}, (549, 0): {'speed': None}, (122, 244): {'speed': None}, (61, 244): {'speed': None}, (488, 0): {'speed': None}, (732, 488): {'speed': None}, (427, 0): {'speed': None}, (122, 488): {'speed': None}, (549, 244): {'speed': None}, (488, 488): {'speed': None}, (366, 0): {'speed': None}, (0, 366): {'speed': None}, (732, 122): {'speed': None}, (0, 488): {'speed': None}, (549, 61): {'speed': None}}, 'WHITE': {(305, 61): {'speed': None, 'limit': 3}}, 'RED': {(122, 183): {'speed': None, 'limit': 5}, (305, 366): {'speed': None, 'limit': 5}}}, 'win': None}, 'agentAction': None, 'agentState': {'medicine': 0}, 'effectList': [('killSprite', 'DARKBLUE', 'GOLD')]},
    ],    
    {'ended': True, 'win': True}
]
''' # this is incorporating game state
trace2 = [[TimeStep(tr['agentAction'], tr['agentState'], tr['effectList'], tr['gameState']) for tr in rawTrace2[0]],rawTrace2[1]]
hypotheses2=list(g.induction(trace2))
print hypotheses2
embed()





#sorted(hypotheses, key=lambda x:len(x.interactionSet)*len(x.classes.keys()))
