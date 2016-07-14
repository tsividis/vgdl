import itertools, random, copy

"""
Theory induction on VGDL Games
"""

'''

TODO: 7/14/16:
	debug
	other cleanup


AddPreconditions:
	Numerical preconditions:
		Make precondition generator make: >=1, <1, >0, <=0 
Current assumptions:
	no grammar over preconditions
	preconditions limited to claims about a SINGLE object
	preconditions limited to simple comparison operators.
	Events that take place at same timestep can only be because of the same preconditions.

Change generateNumberConcepts to make the simpler possibilities.

You're debugging the case where 2 interactions with the same classes happen in a single timestep.
You need to rethink your cases with a clear head. Case 1 is definitely wrong; probably so are the others.

	make preconditions for current state.
	heath:1, sword:1
	health>0, s>0

add preconditions to any unexplained events
add negations of preconditions to any unfulfilled predictions.

'''

class Game(object):
	"""
	VGDL Game and Induction State.
	"""
	def __init__(self):
		# Game states #TODO: May not need these
		#self.backpack = {}
		#self.trace = [] # list of TimeStep objects that happened during a gameplay

		# Induction states
		self.hypothesisSpace = set()
		self.theoryCount = 0
	
	def display(self):
		print self.theoryCount

	def induction(self, trace):
		"""
		Iterates through trace, performing theory induction on each timestep
		"""
		self.hypothesisSpace = set([Theory(self)])
		newTheories = []

		# For every timestep
		for i in range(len(trace)): 
			timestep = trace[i]
			print "explaining events {}".format(timestep.events)

			# For every theory
			for theory in self.hypothesisSpace: 			
				if theory.likelihood(timestep) < 1.0: 	# Theory needs to be changed
					print "likelihood", theory.likelihood(timestep)
					newTheories.extend(theory.explainTimeStep(timestep, timestep))

			for theory in newTheories:
				if theory not in self.hypothesisSpace:
					self.hypothesisSpace.add(theory) #TODO: numbering of theories should take place here.	
			
			self.cleanHypothesisSpace(trace[0:i+1], 1) #All timesteps up to now should be fully explained
			print "{} hypotheses".format(len(self.hypothesisSpace))
			print "_______"
		
		return self.hypothesisSpace

	def cleanHypothesisSpace(self, subtrace, threshold):
		"""
		Removes theories from hypothesisSpace if their likelihood for the timesteps
		passed in 'subtrace' is below threshold.
		"""
		newHypothesisSpace = []

		for t in self.hypothesisSpace:
			if all([t.likelihood(s)>=threshold for s in subtrace]):
				t.dryingPaint = set()
				newHypothesisSpace.append(t)

		# for t in self.hypothesisSpace:
		# 	t.dryingPaint = set()
		# 	newHypothesisSpace.append(t)

		self.hypothesisSpace = set(newHypothesisSpace)

		return


class TimeStep: 
	"""
	Everything that happened in a time step in the game.
	
	Ex.)
	TimeStep.agentAction = 'up'
	TimeStep.agentState = {'health':1, 'treasure':2}
	TimeStep.events = [(bounceForward, BLUE, ORANGE), (undoAll, ORANGE, BLACK)]
	TimeStep.t = 4  --> meaning all of this took place at t_4
	"""

	def __init__(self, agentAction, agentState, events):
		self.agentAction = agentAction 
		self.agentState = agentState # agent's backpack
		self.events = events 
		self.t = False # Number timestep


class Precondition(object):
	def __init__(self, text, fn):
		self.text = text
		self.fn = fn
		self.negate = False

	def check(self, arg):	# TODO: Is 'arg' most likely 'backpack'?
		if len(arg.keys())>0:
			if not self.negate:
				return self.fn(arg) # Need to pass in backpack into this function to get updated values
			else:
				return not self.fn(arg)
		else: return True

	def negate(self):
		self.negate = not self.negate
		self.text = 'not '+ self.text

	def display(self):
		print self.text

	def __eq__(self, other):
		print "Using Precondition new equality function."
		return self.text == other.text

	def __ne__(self, other):
		return not self.__eq__(other)


class Property(object):
	"""
	TODO: 
	Incorporate properties into theory induction loop.
	"""
	def __init__(self, vgdlType, color, args):
		self.vgdlType = vgdlType
		self.color = color 
		self.args = args

	# TODO: Should enforce proper syntax for properties
	def display():
		pass



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
		if precondition.text not in [p.text for p in self.preconditions]:
			self.preconditions.append(precondition)
		return

	def checkPreconditions(self, agentState):
		return all([p.check(agentState) for p in self.preconditions])

	def __eq__(self, other):
		print "Using Precondition new equality function"
		if isinstance(other, self.__class__):
			return all([
				self.asTuple()==other.asTuple(),
				self.preconditions==other.preconditions
				])
		else:
			return False

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

		self.classes = {} # Maps classes -> objects
		self.predicates = set() # Types of possible interactions

		self.dryingPaint = set()
		self.inModification = {}
	"""Main functions"""

	#FLAG: Potential problem with passing in preconditions=False..
	def explainTimeStep(self, timestep, fullTimestep, currTheories=False):
		"""
		Returns a set of theories that explain all the events that took place at timestep.
		Hypotheticals can be passed as args to enable the explanation of multiple events in a single timestep.
		"""
		# Base Case
		print "events:", timestep.events
		if len(timestep.events) == 1:
			print "in base case. currTheories:", currTheories
			theories = []
			if not currTheories:
				theories.extend(self.explainEvent(timestep.events[0], fullTimestep))
			else: # Generate theories based on hypothetical theories
				for theory in currTheories:
					print "explaining", timestep.events
					print "trying to expand:"
					theory.display()
					newTheory = theory.explainEvent(timestep.events[0], fullTimestep)
					print "Expansions:"
					for n in newTheory:
						n.display()
					print ""
					theories.extend(newTheory)
			return theories

		# Recursive case
		else:
			print "in recursive case"
			theories = self.explainEvent(timestep.events[0], fullTimestep)
			updatedTimeStep = TimeStep(timestep.agentAction, timestep.agentState, timestep.events[1:])
			return self.explainTimeStep(updatedTimeStep, fullTimestep, theories)

	def explainEvent(self, event, timestep):
		"""
		Returns theories that explain the event, which is a tuple like:
		(bounceForward, BLUE, ORANGE)
		"""

		theories = []

		likelihood = self.likelihood(timestep)
		if likelihood == 1:
			theories.append(self)
		else:
			failCase = self.getFailCases(event, timestep, verbose=True)
			if failCase in [1,2,3]:
				theories.extend(self.addPreconditions(event, timestep))
			elif failCase == 4: 
				theories.extend(self.addRules(event))

		print "added {} theories in total".format(len(theories))

		return theories

	#TODO: Fix names for these functions or collapse them.
	def checkIfEventsAreInRules(self, timestep):
		interpretations = [self.interpret(event) for event in timestep.events]
		return all([self.checkInterpretation(i, timestep) for i in interpretations])

	def checkIfAllPredictionsHappened(self, timestep):
		interpretations = [self.interpret(event) for event in timestep.events if self.interpret(event) is not False]
		if False not in interpretations:
			interpretations = [interpretation.asTuple() for interpretation in interpretations]
		else:
			return False
		relevantRules = []
		for event in timestep.events:
			relevantRules.extend(self.findRelevantRules(event, timestep.agentState))
		return all([rule in interpretations for rule in relevantRules])

	def checkEvents(self, event, timestep):
		return self.checkInterpretation(self.interpret(event), timestep)

	def checkPredictions(self, event, timestep):
		print "timestep events", timestep.events
		interpretations = [self.interpret(e) for e in timestep.events if self.interpret(e) is not False]
		if False not in interpretations:
			interpretations = [interpretation.asTuple() for interpretation in interpretations]
			relevantRules = self.findRelevantRules(event, timestep.agentState, checkDryingPaint=True)
			if relevantRules:
				print "relevant rules:",[r for r in relevantRules]
				print "checking those rules:", all([rule in interpretations for rule in relevantRules])
				print "interpretations", interpretations
				return all([rule in interpretations for rule in relevantRules])
			else:
				return () #There were no relevant rules; need to create new rule.
		else:
			# print "relevant rules: False was in interpretations"
			return ()

	def likelihood(self, timestep, verbose=False):
		'''
		Makes sure that:
			-all events in the timestep were covered by the ruleset 
			-everything predicted in the ruleset happened.

		Right now returns only 1 or 0.
		'''

		if self.checkIfEventsAreInRules(timestep) and self.checkIfAllPredictionsHappened(timestep):
			likelihood = 1.
		else:
			likelihood = 0.

		return likelihood

	def getFailCases(self, event, timestep, verbose=False):

		'''
		Note: the only predictions we care about checking for here are the ones that are in the original theory.
		Predictions made by 'drying-paint' theories shouldn't be taken into account in the sense that all of these should receive
		the same treatment. That is, if we have (bf c1 c2) in the original theory, and are currently explaining the events:
		(ks c1 c2) (uA c1 c2),
		what we want to do is realize that (ks c1 c2) needs a precondition on it. Then we add this to a theory (as drying paint)
		and when we explain (uA c1 c2), we want to do exactly what we did with (ks c1 c2); recognize that it needs a single precondition.
		So checkPredictions only checks for theories that are not in dryingPaint.
		'''

		failCases = {(True, True): 	 [0, "Event likelihood = 1"],
					 (True, False):  [1, "Event likelihood failed because the interactionSet predicts things that didn't happen. "+
					 "Solution: Add preconditions to subset of interactionSet."],
					 (False, True):  [2, "Event likelihood failed because interpreted event is not in interactionSet. "+
					 "Solution: Add new rule with precondition on it."],
					 (False, False): [3, "Event likelihood failed both ways."+
					 "Solution: Add new rule with precondition on it; negate that precondition for other relevant rules."],
					 (False, ()):    [4, "Event likelihood failed because interactionSet hasn't seen the event."+
					 "Solution: AddRule()"]}

		(eventInRules, predictionsHappened) = self.checkEvents(event, timestep), self.checkPredictions(event, timestep)
		
		if verbose:
			print failCases[(eventInRules, predictionsHappened)][1]

		return failCases[(eventInRules, predictionsHappened)][0]


	def getClassPair(self, event):
		return (event[1], event[2])

	def findRelatedRules(self, classPair, interactionList):
		#needs to take a list of interpretations or a list of interaction rules
		if type(interactionList[0]) == tuple:
			return [interaction for interaction in interactionList if classPair == self.getclassPair(interaction)]
		elif type(interactionList[0] == InteractionRule):
			return [interaction for interaction in interactionList if classPair == self.getclassPair(interaction.asTuple())]

	def addPreconditions(self, event, timestep):
		'''
		Creates preconditions based on the agentState that might help to explain the event.
		Returns a list of theories.
		'''

		newTheories = []

		classPair = self.getClassPair(event)

		if classPair in self.inModification.keys():
			precondition = self.inModification[classPair]
			interpretation = self.interpret(event)
			interpretation.addPrecondition(p) #TODO: maybe you should be only doing this if interpreting worked in the line above.
			newTheory = self.createChild([interpretation, False])
			if newTheory:
				newTheories.append(newTheory)
		else:
			concepts = []
			for k in timestep.agentState.keys():
				concepts.extend(generateNumberConcepts(k, timestep.agentState[k]))
			preconditions = self.makePreconditions(concepts)
			for precondition in preconditions:
				interpretation = self.interpret(event)
				interpretation.addPrecondition(p)
				newTheory = self.createChild([interpretation, False]) #TODO: make sure this is properly negating all other similar events

				#Find what rules you will need to negate
				relevantInteractionSetRules = self.findRelatedRules(classPair, newTheory.interactionSet)
				relevantEvents = self.findRelatedRules(classPair, [self.interpret(e) for e in timestep.events])
				unfulfilledPredictions = set(relevantInteractionSetRules) - set(relevantEvents)
				newTheory.inModification[classPair] = precondition

				#Negate all interactionRules that didn't happen in this timestep.
				#Note: this only has to happen for the base case when you're recursing; after that these have already been negated and should not be touched.
				for uP in unfulfilledPredictions:
					uP.addPrecondition(precondition.negate())

				if newTheory:
					newTheories.append(newTheory)

		return newTheories


	def makePreconditions(self, concepts):
		preconditions = []
		for c in concepts:
			def f(x):
				if c[1] in x.keys():
					return x[c[1]]>c[2]
				else:return True
			preconditions.append(Precondition(c[0], f))
		return preconditions

	def addRules(self, event):
		'''
		Search over possible assignments for classes; posit new classes if necessary
		Return theories that have either 
		Try to make it fit according to the current rules by searching
		over possible class assignments for the objects.
		Returns a list of theories.
		'''
		newTheories = []

		possibleAssignments = self.searchForAssignments(event)

		if possibleAssignments:
			for assignment in possibleAssignments:
				interaction = InteractionRule(event[0], assignment[0], assignment[1]) #This isn't strictly necessary, but follows createChild requirements.
				classAssignments = [(assignment[0], event[1]), (assignment[1],event[2])]
				newTheory = self.createChild([interaction, classAssignments])
				#Checks and only adds to newTheories if the created theory was actually different.
				if newTheory:
					newTheories.append(newTheory)

		# print "adding {} theories with new assignments".format(len(newTheories))
		return newTheories

	"""Helper functions"""


	def createChild(self, proposal, negatePreconditions=False):
		newTheory = copy.deepcopy(self)
		newTheory.depth = self.depth + 1
		newTheory.parent = self
		newTheory.children = []
		generatedNewTheory = newTheory.addProposal(proposal, negatePreconditions)
		if generatedNewTheory:
			self.children.append(newTheory)
			return newTheory
		else:
			return False

	def addProposal(self, proposal, negatePreconditions=False):
		'''
		Adds proposal to theory; takes care of rule and assignments
		'''
		rule, assignments = proposal[0], proposal[1]
		addedRule = self.addInteractionRule(rule, negatePreconditions)
		# if added:
			# print "Added", rule.asTuple()
		addedClass = False
		if assignments:
			addedClass = any([self.assignClass(assignment) for assignment in assignments])
		return (addedRule or addedClass)

	def getClass(self, obj):
		for c, o in self.classes.iteritems():
			if obj in o:
				return c
		return False

	def assignClass(self, classObjectPair):
		'''
		Adds object-class assignments; avoids duplicates.
		'''
		c, o = classObjectPair[0], classObjectPair[1]
		if c in self.classes.keys():
			if o not in self.classes[c]:
				self.classes[c].append(o)
				return True
			return False
				# print "added", o, "to class", c
		else:
			self.classes[c] = [o]
			return True
			# print "added", o, "to class", c

	def addInteractionRule(self, rule, negatePreconditions=False):
		'''
		Adds interactionRule if it is not in interactionSet.
		'''
		if rule.interaction not in self.predicates:
			self.predicates.add(rule.interaction)
		if not self.findRule(rule, self.interactionSet):
			self.interactionSet.append(rule)
			self.dryingPaint.add(rule)
			#Iterate through relevant rules, negate them if they're not in the drying paint
			if negatePreconditions:
				for r in self.interactionSet:
					if all([
							r.slot1==rule.slot1, 
							r.slot2==rule.slot2,
						 	r.asTuple() not in [paint.asTuple() for paint in self.dryingPaint],
						 	r.preconditions==[]
					 	]):
						r.preconditions = rule.preconditions.deepcopy()
						r.preconditions[0].negate()
			return True
		return False

	def findRule(self, rule, lst):
		'''
		Finds if a rule is in the interaction set.
		'''
		# print ""
		# print "looking for rule:", rule.asTuple(), rule.preconditions
		# print "in"
		# self.display()
		for interactionRule in lst:
			# print interactionRule.asTuple()
			if interactionRule.asTuple()==rule.asTuple() and set([r.text for r in interactionRule.preconditions]) == set([r.text for r in rule.preconditions]):
				# print "found it"
				return True
		# print "didn't find it"
		return False
	
	def interpret(self, event): 
		'''
		Looks up objects by their corresponding class under the theory,
		returns a corresponding interactionRule.
		
		If those objects aren't known, returns false.

		Ex) Event is a tuple: ('bounceForward', 'ORANGE', 'DARKBLUE')
		If we know that ORANGE=c1 and DARKBLUE=c2, returns the InteractionRule
		that corresponds to (bounceForward, c1, c2)
		'''
		# print "in interpret:"
		# self.display()
		c1, c2 = self.getClass(event[1]), self.getClass(event[2])
		if c1 and c2:
			return InteractionRule(event[0], c1, c2)
		else:
			return False

	def findRelevantRules(self, event, agentState, checkDryingPaint=False):
		'''
		Helper function for likelihood. If an event involves c1 and c2, 
		returns rules that use c1 and c2 in those slots.
		'''
		# print "event", event
		interpretation = self.interpret(event)
		relevantRules = []
		if interpretation:
			class1, class2 = interpretation.asTuple()[1], interpretation.asTuple()[2]
			
			rules = [rule for rule in self.interactionSet]
			if not checkDryingPaint:
				relevantRules.extend([rule.asTuple() for rule in rules if rule.asTuple()[1]==class1 and rule.asTuple()[2]==class2 and all(p.check(agentState) for p in rule.preconditions)])
			else:
				#here we only return rules that are not in the drying paint. 
				relevantRules.extend([rule.asTuple() for rule in rules if not self.findRule(rule, self.dryingPaint) and rule.asTuple()[1]==class1 and rule.asTuple()[2]==class2 and all(p.check(agentState) for p in rule.preconditions)])
		else:
			# print "interpretation", interpretation
			relevantRules.append(False)
		if False not in relevantRules:
			return relevantRules
		else:
			return False

	def checkInterpretation(self, interpretation, timestep):
		'''
		Helper function for likelihood(). Checks whether everything in the interpretation is 
		accounted for by the interactionSet.
		'''
		if interpretation:
			interpretation = interpretation.asTuple()
			print "interpretation", interpretation
			for rule in self.interactionSet:
				if rule.asTuple()==interpretation:
					if rule.preconditions == False:
						return True # TODO: Should this be False? or should line above be True? 
									#Pedro's comment: Should be as is; the interpretation is fine if it matches the rule
									#and there were no preconditions to check.
					elif all([p.check(timestep.agentState) for p in rule.preconditions]):
						return True
			return False 			# If we've checked everything and found no matching rule or rule+precondition, reutrn false.
		else:
			print "interpetation: False"
		return False 				# Uninterpretable interpretation returns False, too.


	def searchForPossibleClasses(self, o, newClasses=0): # TODO: Seems to add an extra class
		'''
		If the object has been assigned, return it. Otherwise return all
		possible classes. Optional argument can posit existence of a new class;
		user specifies whether to add 0, 1, or 2 new classes.
		'''
		gotNewClass = False
		if self.getClass(o):
			return [self.getClass(o)], gotNewClass
		elif len(self.classes.keys())>0 and newClasses==0:
			return self.classes.keys(), gotNewClass
		elif newClasses>0:
			numClasses = len(self.classes.keys())
			classes = self.classes.keys()
			for i in range(1, newClasses+1):
				classes.append('c'+str(numClasses+i))
			gotNewClass = True
			return classes, gotNewClass
		else: return [], gotNewClass

	def searchForAssignments(self, event):
		x1, gotNewClass = self.searchForPossibleClasses(event[1], newClasses=1)
		if gotNewClass:
			x2 = self.searchForPossibleClasses(event[2], newClasses=2)[0]
		else:
			x2 = self.searchForPossibleClasses(event[2], newClasses=1)[0]

		if x1 and x2: #if both yielded possibilities
			return list(itertools.product(x1,x2))
		else: return False

	def generateNumberConcepts(self, item, num):
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
		print "Current rule set:"
		for rule in self.interactionSet:
			rule.display()

	def displayClasses(self):
		# print ""
		print "Current class assignments:"
		print self.classes

	def display(self):
		self.displayRules()
		self.displayClasses()
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





g = Game()

rawTrace = [
{'agentAction': 'up', 'agentState': {}, 'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE')]}, 
{'agentAction': 'up', 'agentState': {}, 'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE'), ('undoAll', 'ORANGE', 'BLACK')]}, 
{'agentAction': 'right', 'agentState': {}, 'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE')]}, 
{'agentAction': 'up', 'agentState': {}, 'effectList': [('changeResource', 'DARKBLUE', 'WHITE'), ('killSprite', 'DARKBLUE', 'WHITE')]}
]

'''
eatApple BLUE WHITE
(bounceForward BLUE WHITE) If h>1

, (killSprite BLUE WHITE) 

eatApple Blue white if h<=1
bF blue WHITe if h>1
ks blue white if h>
'''

# {'agentAction': 'up', 'agentState': {}, 'effectList': [('changeResource', 'DARKBLUE', 'WHITE', 1), ('killSprite', 'DARKBLUE', 'WHITE')]}]

# ,{'agentAction': 'down', 'agentState': {'medicine': 1}, 'effectList': [('killSprite', 'DARKBLUE', 'GOLD')]}]

# rawTrace = [{'agentAction': 'up', 'agentState': {}, 'effectList': [('killSprite', 'DARKBLUE', 'ORANGE')]}, {'agentAction': 'up', 'agentState': {'medicine':1}, 'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE')]}]


trace = [TimeStep(tr['agentAction'], tr['agentState'], tr['effectList']) for tr in rawTrace]


hypotheses=list(g.induction(trace))
