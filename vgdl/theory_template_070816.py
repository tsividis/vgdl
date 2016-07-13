import itertools, random, copy
"""
Theory induction on VGDL Games
"""
'''
TODO: 7/13/16:
	What this returns needs to be a function of BOTH checkIfEventsAreInRules and checkIfAllPredictionsHappened.
	checkIfAllPredictionsHappened needs to return False, True, or [] (for rules that succeeded because there were not relevant rules)
	You will need to change checkIfAllPredictionsHappened, to deal with what happens
	when any of relevantRules are empty. It needs to return three different potential values:
		-relevant rules exist and all are fulfilled
		-no relevant rules exist
		-relevant rules exist and are not fulfilled

	See photo, for appropriate failCase and corresponding addPreconditions(), addRules(), addPreconditions(newrules) behavior.

'''


"""TODO: Likelihood now explaining events, not timesteps? Clean up."""
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
					newTheories.extend(theory.explainTimeStep(timestep))

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
		# self.hypothesisSpace = [t for t in self.hypothesisSpace if all([t.likelihood(s)>=threshold for s in subtrace])]
		newHypothesisSpace = []
		for t in self.hypothesisSpace:
			if all([t.likelihood(s)>=threshold for s in subtrace]):
				t.dryingPaint = set()
				newHypothesisSpace.append(t)
		self.hypothesisSpace = newHypothesisSpace
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
		# print "about to add precondition to this rule:"
		# self.display()
		# print "preconditions before adding:", [p.text for p in self.preconditions]
		if precondition.text not in [p.text for p in self.preconditions]:
			self.preconditions.append(precondition)
		# print "preconditions after adding:", [p.text for p in self.preconditions]
		# self.display()
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
	"""Main functions"""

	#FLAG: Potential problem with passing in preconditions=False..
	def explainTimeStep(self, timestep, currTheories=False):
		"""
		Returns a set of theories that explain all the events that took place at timestep.
		Hypotheticals can be passed as args to enable the explanation of multiple events in a single timestep.
		"""
		# Base Case
		if len(timestep.events) == 1:
			print "in base case. currTheories:", currTheories
			theories = []
			if not currTheories:
				theories.extend(self.explainEvent(timestep.events[0], timestep.agentState))
			else: # Generate theories based on hypothetical theories
				for theory in currTheories:
					print "explaining", timestep.events
					print "trying to expand:"
					theory.display()
					newTheory = theory.explainEvent(timestep.events[0], timestep.agentState)
					print "Expansions:"
					for n in newTheory:
						n.display()
					print ""
					theories.extend(newTheory)
			return theories

		# Recursive case
		else:
			print "in recursive case"
			theories, newInteractionRules = self.explainEvent(timestep.events[0], timestep.agentState)
			updatedTimeStep = TimeStep(timestep.agentAction, timestep.agentState, timestep.events[1:])
			# print len(updatedTimeStep.events)
			return self.explainTimeStep(updatedTimeStep, theories)

	def explainEvent(self, event, agentState):
		"""
		Returns theories that explain the event, which is a tuple like:
		(bounceForward, BLUE, ORANGE)
		"""

		eventName, obj1, obj2 = event[0], event[1], event[2]

		theories = []
		timestep = TimeStep(False, agentState, [event]) #hacked this rather than making a more complex likelihood function

		likelihood, failCase = self.likelihood(timestep)

		if likelihood == 1:
			theories.append(self)
		else:
			if failCase == 1:
				theories.extend(self.addRules(event))
			if failCase == 2:
				theories.extend(self.addPreconditions(event))

		# else:
		# 	if self.case1(event, timestep.agentState):
		# 		'''
		# 		Case 1: 	Predicted interaction is different from actual interaction.
		# 					(e.g., we observe killSprite BLUE RED, which is parsed as killSprite c1 c3 
		# 					(because we know those assignments), and interactionSet = bounceForward c1 c3).
		# 		Solution: 	Consider adding preconditions to explain the difference.
		# 		'''
		# 		print "case1"
		# 		theories.extend(self.addPreconditions(event, agentState))
		# 	elif self.case2(event):
		# 		'''
		# 		Case 2: 	We know the event name and the object classes, but the interpetation is not in the 
		# 					interactionSet (e.g., we observe bounceForward BLUE RED, interactionSet = bounceForward c1 c2 
		# 					assignments = {c1:BLUE, c2:ORANGE, c3:RED}, but bounceForward c1 c3 is not in the interactionSet.)
		# 					This will also work if the predicate is new  -- change the way you're testing for it.
		# 		Solution:	Add bounceForward c1 c3 to interactionSet via addRules().
		# 		'''
		# 		print "case2"
		# 		theories.extend(self.addRules(event))
		# 	elif self.case3(event):
		# 		'''
		# 		Case 3: 	We know the event name, but don't know at least one of the object classes.
		# 		Solution: 	Search for possible assignments, including old and new ones.
		# 					This will take care of both adding assignments and keeping existing interactionRules
		# 					and of adding new interactionRule if new assignments happen.
		# 		'''
		# 		print "case3"
		# 		theories.extend(self.addAssignments(event))
		# 	elif self.case4(event):
		# 		'''
		# 		Case 4: 	We don't know event name.
		# 		Solution:	In response to a new predicate: Generates new rules that apply either to combinations 
		# 					of existing classes, or adds new classes.
		# 		'''
		# 		print "case4"
		# 		theories.extend(self.addRules(event))


		print "added {} theories in total".format(len(theories))
		# for t in theories:
			# t.display()
		# print ""
		# print ""
		return theories
	

	"""TODO:

	Check whether the case-checking functions are working properly.

	AddPreconditions:
		Numerical preconditions:
		Make precondition generator make: >=1, <1, >0, <=0 
		x Make negation operator
		x And anytime you add the precondition, add the negation to any other rule about the same classes.
	For now:
		no grammar over preconditions
		preconditions limited to claims about a SINGLE object
		preconditions limited to simple comparison operators.
		Events that take place at same timestep can only be because of the same preconditions.

	Change generateNumberConcepts to make the simpler possibilities.

	You're debugging the case where 2 interactions with the same classes happen in a single timestep.
	You need to rethink your cases with a clear head. Case 1 is definitely wrong; probably so are the others.
	"""

	def case1(self, event, agentState):
		'''
		Case 1: 	Predicted interaction is different from actual interaction.
					(e.g., we observe killSprite BLUE RED, which is parsed as killSprite c1 c3 
					(because we know those assignments), and interactionSet = bounceForward c1 c3).
		Solution: 	Consider adding preconditions to explain the difference.
		'''
		interpretation = self.interpret(event)
		if interpretation:
			if (interpretation.asTuple() in [rule.asTuple() for rule in self.interactionSet]): #or (interpretation not in self.findRelevantRules(event, agentState)):
				print interpretation.asTuple()
				print "case 1"
				return True
		return False



	def case2(self, event):
		'''
		Interpreted event is not in the interactionSet even though we know event name and object classes.
		Solution: addRule() <<?
		'''
		interpretation = self.interpret(event)
		if interpretation:
			if not interpretation.asTuple() in [rule.asTuple() for rule in self.interactionSet]:
				return True
		return False

	def case3(self, event):
		'''
		We know the event name but don't know at least one of the object classes
		Solution: addAssignments()
		'''
		if event[0] in self.predicates and not (self.getClass(event[1]) and self.getClass(event[2])):
			return True
		else:
			return False

	def case4(self, event):
		'''
		We don't know the event predicate
		Solution: addRules()
		'''
		if event[0] not in self.predicates:
			return True
		else: return False

	def addPreconditions(self, event, agentState):
		'''
		Creates preconditions based on the agentState that might help to explain the event.
		Returns a list of theories.
		'''
		copiedPreconditions = False

		for rule in self.dryingPaint:
			if rule.slot1 == self.getClass(event[1]) and rule.slot2 == self.getClass(event[2]):
				#We've found the rule covering the same classes. Let's copy its precondition.
				preconditions = rule.preconditions
				copiedPreconditions = True		

		if not copiedPreconditions:
			newTheories = []
			concepts = []
			for k in agentState.keys():
				concepts.extend(self.generateNumberConcepts(k, agentState[k]))
			preconditions = []
			for c in concepts:
				def f(x):
					if c[1] in x.keys():
						return x[c[1]]>c[2]
					else:return True
				preconditions.append(Precondition(c[0], f))
			# preconditions = [Precondition(c[0], lambda x: (x[c[1]] > c[2]) if c[1] in x.keys() else True) for c in concepts] # TODO: Add flexible operator
		
		for p in preconditions:
			interpretation = self.interpret(event)

			if interpretation:
				interpretation.addPrecondition(p)
				newTheory = self.createChild([interpretation, False], negatePreconditions=True)
				#Checks and only adds to newTheories if the created theory was actually different.
				if newTheory:
					newTheories.append() #second slot is for new assignments
		# print "adding {} theories with new preconditions".format(len(newTheories))
		# print "addPreconditions theories:", newTheories
		return newTheories

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

	def likelihood(self, timestep, verbose=False):
		'''
		Makes sure that:
			-all events in the timestep were covered by the ruleset 
			-everything predicted in the ruleset happened.

		Right now returns only 1 or 0.
		'''
		failCases = {0: "Likelihood = 1.",
					 1: "Likelihood failed because some aspect of the event was not in the interactionSet -- either due to interaction or preconditions",\
					 2: "Likelihood failed because theory predicts things that didn't happen",\
					 3: "Likelihood failed because event was not interpretable."}

		def checkIfEventsAreInRules(self, timestep):
			interpretations = [self.interpret(event) for event in timestep.events]
			return all([self.checkInterpretation(i, timestep) for i in interpretations])

		def checkIfAllPredictionsHappened(self, timestep):
			interpretations = [self.interpret(event) for event in timestep.events]
			relevantRules = []
			for event in timestep.events:
				relevantRules.extend(self.findRelevantRules(event, timestep.agentState))
			return all([rule in interpretations for rule in relevantRules])

		if self.checkIfEventsAreInRules(timestep):
			if self.checkIfAllPredictionsHappened(timestep):
				likelihood = 1.
				failCase = 0
			else:
				likelihood = 0.
				failCase = 2
		else:
			likelihood = 0.
			failCase = 1

		if verbose:
			print failCases[failCase]

		return likelihood, failCase

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
		if not self.findRule(rule):
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

	def findRule(self, rule):
		'''
		Finds if a rule is in the interaction set.
		'''
		# print ""
		# print "looking for rule:", rule.asTuple(), rule.preconditions
		# print "in"
		# self.display()
		for interactionRule in self.interactionSet:
			# print interactionRule.asTuple()
			if interactionRule.asTuple()==rule.asTuple() and set([r.text for r in interactionRule.preconditions]) == set([r.text for r in rule.preconditions]):
				# print "found it"
				return True
		# print "didn't find it"
		return False

	def addChild(self, theory):
		'''
		'''
		self.children.append(theory)
		self.game.hypothesisSpace.append(theory)
	
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

	def findRelevantRules(self, event, agentState):
		'''
		Helper function for likelihood. If an event involves c1 and c2, 
		returns rules that use c1 and c2 in those slots.
		'''
		interpretation = self.interpret(event)
		relevantRules = []
		if interpretation:
			class1, class2 = interpretation.asTuple()[1], interpretation.asTuple()[2]
			
			rules = [rule for rule in self.interactionSet]
			relevantRules.extend([rule.asTuple() for rule in rules if rule.asTuple()[1]==class1 and rule.asTuple()[2]==class2 and all(p.check(agentState) for p in rule.preconditions)])
		else:
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
			for rule in self.interactionSet:
				if rule.asTuple()==interpretation:
					if rule.preconditions == False:
						return True # TODO: Should this be False? or should line above be True? 
									#Pedro's comment: Should be as is; the interpretation is fine if it matches the rule
									#and there were no preconditions to check.
					elif all([p.check(timestep.agentState) for p in rule.preconditions]):
						return True
			return False 			# If we've checked everything and found no matching rule or rule+precondition, reutrn false.
		return False 				# Uninterpretable interpretation returns False, too.


	def searchForPossibleClasses(self, o, newClasses=0): #TODO: Seems to add an extra class
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
		# elif len(self.classes.keys())>0 and newClasses>0:
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

	def generateNumberConcepts(self, c, n):
		concepts = []
		for i in range(n):
			text = c+">"+str(i)
			concepts.append((text,c,i))
		return concepts

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





#g = Game()

rawTrace = [
{'agentAction': 'up', 'agentState': {}, 'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE')]}, 
{'agentAction': 'up', 'agentState': {}, 'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE'), ('undoAll', 'ORANGE', 'BLACK')]}, 
{'agentAction': 'right', 'agentState': {}, 'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE')]}, 
{'agentAction': 'up', 'agentState': {}, 'effectList': [('changeResource', 'DARKBLUE', 'WHITE', 1), ('killSprite', 'DARKBLUE', 'WHITE')]}
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


#trace = [TimeStep(tr['agentAction'], tr['agentState'], tr['effectList']) for tr in rawTrace]


#=g.induction([trace[3]])
