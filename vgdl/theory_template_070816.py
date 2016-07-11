import itertools, random, copy

"""
Theory induction on VGDL Games
"""

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
		self.hypothesisSpace = []
		self.theoryCount = 0
	
	def display(self):
		print self.theoryCount

	def induction(self, trace):
		"""
		Iterates through trace, performing theory induction on each timestep
		"""
		self.hypothesisSpace = [Theory(self)]

		for i in range(len(trace)): #iterate through each timestep
			timestep = trace[i]
			print "explaining events {}".format(timestep.events)
			for theory in self.hypothesisSpace: 			# Iterate through each theory
				if theory.likelihood(timestep) < 1.0: 	# Theory needs to be changed
					newTheories = theory.explainTimeStep(timestep)
					self.hypothesisSpace.extend(newTheories) #TODO: numbering of theories should take place here.
			self.cleanHypothesisSpace(trace[0:i+1], 1) #All timesteps up to now should be fully explained
			print "{} hypotheses".format(len(self.hypothesisSpace))
			print "_______"
		return self.hypothesisSpace

	def cleanHypothesisSpace(self, subtrace, threshold):
		"""
		Removes theories from hypothesisSpace if their likelihood for the timesteps
		passed in 'subtrace' is below threshold.
		"""
		self.hypothesisSpace = [t for t in self.hypothesisSpace if all([t.likelihood(s)>=threshold for s in subtrace])]
		return


class Theory:
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

	"""Main functions"""

	def explainTimeStep(self, timestep, currTheories=False):
		"""
		Returns a set of theories that explain all the events that took place at timestep.
		Hypotheticals can be passed as args to enable the explanation of multiple events in a single timestep.
		"""
		# Base Case
		if len(timestep.events) == 1:
			# print "in base case. currTheories:", currTheories
			theories = []
			if not currTheories:
				theories.extend(self.explainEvent(timestep.events[0], timestep.agentState))
			else: # Generate theories based on hypothetical theories
				for theory in currTheories:
					# print "explaining", timestep.events
					# print "trying to expand:"
					# theory.display()
					newTheory = theory.explainEvent(timestep.events[0], timestep.agentState)
					# print "Expansions:"
					# for n in newTheory:
						# n.display()
					# print ""
					theories.extend(newTheory)
			return theories

		# Recursive case
		else:
			theories = self.explainEvent(timestep.events[0], timestep.agentState)
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

		if self.likelihood(timestep) == 1:
			theories.append(self)
		else:
			if self.case1(event):
				theories.extend(self.addPreconditions(event, agentState))
			if self.case2(event):
				theories.extend(self.addRules(event))
			if self.case3(event):
				theories.extend(self.addAssignments(event))
			if self.case4(event):
				theories.extend(self.addRules(event))
		# print "added {} theories in total".format(len(theories))
		return theories
	
	def case1(self, event):
		'''
		Interpreted event is in the interactionSet, but theory didn't predict what happened.
		Solution: addPreconditions()
		'''
		interpretation = self.interpret(event)
		if interpretation:
			if interpretation.asTuple() in [rule.asTuple() for rule in self.interactionSet]:
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
		newTheories = []
		concepts = []
		for k in agentState.keys():
			concepts.extend(self.generateNumberConcepts(k, agentState[k]))
		preconditions = [Precondition(c[0], lambda x: x[c[1]] > c[2]) for c in concepts] # TODO: Add flexible operator
		for p in preconditions:
			interpretation = self.interpret(event)
			if interpretation:
				interpretation.addPrecondition(p)
				newTheories.append(self.createChild([interpretation, False])) #second slot is for new assignments
		# print "adding {} theories with new preconditions".format(len(newTheories))
		# print "addPreconditions theories:", newTheories
		return newTheories

	def addAssignments(self, event):
		'''
		Try to make it fit according to the current rules by searching
		over possible class assignments for the objects.
		Returns a list of theories.
		'''
		newTheories = []
		possibleAssignments = self.searchForAssignments(event)
		if possibleAssignments:
			for assignment in possibleAssignments:
				if (event[0], assignment[0], assignment[1]) in [i.asTuple() for i in self.interactionSet]:
					interaction = InteractionRule(event[0], assignment[0], assignment[1])
					classAssignments = [(assignment[0], event[1]), (assignment[1],event[2])]
					newTheories.append(self.createChild([interaction, classAssignments]))
		# print "adding {} theories with new assignments".format(len(newTheories))
		return newTheories

	def addRules(self, event):
		'''
		In response to a new predicate: Generates new rules
		that apply either to combinations of existing classes, or adds new classes.
		Returns a list of theories.
		'''
		newTheories = []

		x1, x2 = self.searchForPossibleClasses(event[1], newClasses=1), \
		self.searchForPossibleClasses(event[2], newClasses=2)
		combinations = list(itertools.product(x1,x2))
		for c in combinations:
			interaction = InteractionRule(event[0], c[0], c[1])
			classAssignments = [(c[0], event[1]), (c[1], event[2])]
			newTheories.append(self.createChild([interaction, classAssignments]))
		# print "adding {} theories with new rules".format(len(newTheories))
		return newTheories

	"""Helper functions"""

	def likelihood(self, timestep, verbose=False):
		'''
		Makes sure that:
			-all events in the timestep were covered by the ruleset 
			-everything predicted in the ruleset happened.

		Right now returns only 1 or 0.
		'''

		failCases = {0: "Likelihood failed because theory predicts things that didn't happen",\
					 1: "Likelihood failed because some aspect of the event was not in the interactionSet -- either due to interaction or preconditions",\
					 2: "Likelihood failed because event was not interpretable."}

		# List of everything that happened, according to current class assignments and interaction rules
		interpretations = [self.interpret(event) for event in timestep.events]
		
		if False not in interpretations:
			if verbose:
				print "Interpretation of event:"
				print [interpretation.asTuple() for interpretation in interpretations]
			interpretations = [interpretation.asTuple() for interpretation in interpretations]

			ruleSet = [rule.asTuple() for rule in self.interactionSet]
			
			if all([self.checkInterpretation(i, timestep) for i in interpretations]):
				#if everything in the interpretation is accounted for by the ruleset
				relevantRules = [self.findRelevantRules(event) for event in timestep.events]
				for rules in relevantRules:
					#Now ensure that everything predicted by the theory happened.
					if not all([r in interpretations for r in rules]):
						if verbose:
							print failCases[0]
						return 0.
				return 1.
			if verbose:
				print failCases[1]
			return 0.
		if verbose:
			print failCases[2]
		return 0.

	def createChild(self, proposal):
		newTheory = copy.deepcopy(self)
		newTheory.depth = self.depth + 1
		newTheory.parent = self
		newTheory.children = []
		newTheory.addProposal(proposal)
		return newTheory

	def addProposal(self, proposal):
		'''
		Adds proposal to theory; takes care of rule and assignments
		'''
		rule, assignments = proposal[0], proposal[1]
		# print "adding rule:"
		# rule.display()
		added = self.addInteractionRule(rule)
		# if added:
			# print "Added", rule.asTuple()
		if assignments:
			for assignment in assignments:
				self.assignClass(assignment)

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
				# print "added", o, "to class", c
		else:
			self.classes[c] = [o]
			# print "added", o, "to class", c

	def addInteractionRule(self, rule):
		'''
		Adds interactionRule if it is not in interactionSet.
		'''
		if rule.interaction not in self.predicates:
			self.predicates.add(rule.interaction)
		if not self.findRule(rule):
			self.interactionSet.append(rule)
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
		c1, c2 = self.getClass(event[1]), self.getClass(event[2])
		if c1 and c2:
			return InteractionRule(event[0], c1, c2)
		else:
			return False

	def findRelevantRules(self, event):
		'''
		Helper function for likelihood. If an event involves c1 and c2, 
		returns rules that use c1 and c2 in those slots.
		'''
		interpretation = self.interpret(event)
		relevantRules = []
		if interpretation:
			class1, class2 = interpretation.asTuple()[1], interpretation.asTuple()[2]
			rules = [rule.asTuple() for rule in self.interactionSet]
			relevantRules.extend([rule for rule in rules if rule[1]==class1 and rule[2]==class2])
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


	def searchForPossibleClasses(self, o, newClasses=0):
		'''
		If the object has been assigned, return it. Otherwise return all
		possible classes. Optional argument can posit existence of a new class;
		user specifies whether to add 0, 1, or 2 new classes.
		'''
		if self.getClass(o):
			return [self.getClass(o)]
		elif len(self.classes.keys())>0 and newClasses==0:
			return self.classes.keys()
		elif newClasses>0:
		# elif len(self.classes.keys())>0 and newClasses>0:
			numClasses = len(self.classes.keys())
			classes = self.classes.keys()
			for i in range(1, newClasses+1):
				classes.append('c'+str(numClasses+i))
			return classes
		else: return []

	def searchForAssignments(self, event):
		x1, x2 = self.searchForPossibleClasses(event[1]), self.searchForPossibleClasses(event[2])
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


class Precondition(object): # TODO: Icorporate into framework
	def __init__(self, text, fn):
		self.text = text
		self.fn = fn

	def check(self, arg):	# TODO: Is 'arg' most likely 'backpack'?
		return self.fn(arg) # Need to pass in backpack into this function to get updated values

	def display(self):
		print self.text



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
	'''
	Rule defining how 2 classes of objects interact with each other.
	# TODO: Should enforce proper syntax for interaction rules

	'''
	def __init__(self, interaction, c1, c2, preconditions=[]):
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


g = Game()
rawTrace = [{'agentAction': 'up', 'agentState': {}, 'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE')]}, 
{'agentAction': 'up', 'agentState': {}, 'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE'), ('undoAll', 'ORANGE', 'BLACK')]}, 
{'agentAction': 'right', 'agentState': {}, 'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE')]}, 
{'agentAction': 'up', 'agentState': {}, 'effectList': [('changeResource', 'DARKBLUE', 'WHITE', 1), ('killSprite', 'DARKBLUE', 'WHITE')]}]

#,{'agentAction': 'down', 'agentState': {'medicine': 1}, 'effectList': [('killSprite', 'DARKBLUE', 'GOLD')]}]
trace = [TimeStep(tr['agentAction'], tr['agentState'], tr['effectList']) for tr in rawTrace]
h=g.induction(trace[0:4])
