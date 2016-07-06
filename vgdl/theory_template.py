import itertools, random, copy


class Game(object):
	def __init__(self):
		self.backpack = {}
		self.hypothesisSpace = []
		self.theoryCount = 0

class TimeStep(object): # TODO: Rename to "Event"?
	def __init__(self, agentAction, agentState, events):
		self.agentAction = agentAction
		self.agentState = agentState
		self.events = events
		self.t = False # TODO: What is self.t?
'''
class Precondition(object):
	"""
	Eventually, this needs to be extended to handle a logical grammar over preconditions
	e.g., [AND health>0, sword==1].
	"""
	def __init__(self, text, item, num):
		self.text = text
		self.item = item
		self.num = num

	def check(self, backpack):
		if self.item in backpack.keys():
			return backpack[self.item]>self.num 
		else: 
			print "agent has not encountered", self.item
			return False

	def display(self):
		print self.text
'''

class Precondition(object): # TODO: Icorporate into framework
	def __init__(self, text, fn):
		self.text = text
		self.fn = fn

	def check(self, arg):	# TODO: Is 'arg' most likely 'backpack'?
		return self.fn(arg) # Need to pass in backpack into this function to get updated values

	def display(self):
		print self.text
'''
class Precondition(object): # TODO: Icorporate into framework
	def __init__(self, text, fn, arg1, arg2): # TODO: Make the number of arguments optional?
		self.text = text
		self.fn = fn
		self.arg1 = arg1
		self.arg2 = arg2

	def check(self):
		return self.fn(self.arg1, self.arg2)

	def display(self):
		print self.text
'''

class Property(object):
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

	'''
	def __init__(self, interaction, c1, c2, preconditions=[]):
		self.interaction = interaction
		self.slot1 = c1
		self.slot2 = c2
		self.preconditions = preconditions

	# TODO: Should enforce proper syntax for interaction rules
	def display(self):
		if not self.preconditions:
			print self.interaction, self.slot1, self.slot2
		else:
			print self.interaction, self.slot1, self.slot2, [p.text for p in self.preconditions]
		return

	def asTuple(self):
		return (self.interaction, self.slot1, self.slot2)

	def addPrecondition(self, precondition):
		if precondition not in self.preconditions:
			self.preconditions.append(precondition)
		return

	def checkPreconditions(self, backpack):
		return all([p.check(backpack) for p in self.preconditions])



# hypothesisSpace = []
'''
Each hypothesis is a full theory. If you need to improve a theory and
this yields multiple theories, then return all of them and store them in your
hypothesis space.
'''
class Theory(object):
	def __init__(self):
		self.spriteSet = [] # property rules
		self.levelMapping = []
		self.interactionSet = [] # interaction rules
		self.terminationSet = []
		self.classes = {} # k:classes, v:objects
		self.predicates = [] # types of possible interactions; TODO: Is it necessary to separate out? 
		self.parent = None
		self.children = []
		self.depth = 0
		self.theoryID = False

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
		print "ID:", self.theoryID
		self.displayRules()
		self.displayClasses()
		return

	def addChild(self, theory):
		self.children.append(theory)
		g.hypothesisSpace.append(theory)

	def extend(self, proposals, timesteps, hypothetical=False):
		"""
		Add new theories to hypothesis space. Can add hypothetical hypotheses.

		- If hypothetical is False: 
			Actually extends g.hypothesisSpace to include theories that are built by incorporating the proposals
		
		- If hypothetical is True:
			Generates theories that incorporate the proposals, but doesn't add them to g.hypothesisSpace. 
			This is so that if you have, say, [e1,e2,e3] at a single timestep, you can generate theories that can explain
			all three events. 
			This necessitates generating theories for e1, and then conditioning on those to generate theories for e2, and so on.
		"""
		hypotheticals = []
		for p in proposals:
			newTheory = copy.deepcopy(self)
			newTheory.depth = self.depth + 1
			newTheory.parent = self
			newTheory.addProposal(p)
			likelihoods = [newTheory.likelihood(timestep) for timestep in timesteps]
			# print likelihoods
			newTheory.display()

			if not hypothetical:
				if all(likelihoods):
					newTheory.theoryID = g.theoryCount
					# print 'theory', newTheory.theoryID, 'worked. adding it:'
					g.theoryCount = g.theoryCount + 1
					self.addChild(newTheory)
			elif hypothetical:
				#TODO: increment theoryID appropriately.
				hypotheticals.append(newTheory)

		if hypothetical:
			return hypotheticals
		else:
			return g.hypothesisSpace.index(self)

	def replace(self, hypotheses, timesteps):
		'''
		Eliminates current hypothesis from g.hypothesisSpace; replaces it with all the ones it spawned.
		'''
		madeChange = False
		for hypothesis in hypotheses:
			# print all([hypothesis.likelihood(timestep) for timestep in timesteps])
			likelihood = all([hypothesis.likelihood(timestep) for timestep in timesteps])
			if likelihood:
				madeChange=True
				# print "adding", hypothesis.display()
				# print ""
				g.hypothesisSpace.append(hypothesis)
		if madeChange:
			g.hypothesisSpace.remove(self)

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

	def addRule(self, rule):
		'''
		Adds rule if it is not in interactionSet.
		'''
		if rule.interaction not in self.predicates:
			self.predicates.append(rule.interaction)
		if not self.findRule(rule):
			self.interactionSet.append(rule)
			return True
		return False

	def findRule(self, rule):
		'''
		Finds if a rule is in the interaction set.
		'''
		for interactionRule in self.interactionSet:
			if interactionRule.asTuple()==rule.asTuple and interactionRule.preconditions==rule.preconditions:
				return True
		return False

	def addProposal(self, proposal):
		'''
		Adds proposal to theory; takes care of rule and assignments
		'''
		rule, assignments = proposal[0], proposal[1]
		# print "adding rule:"
		# rule.display()
		added = self.addRule(rule)
		# if added:
			# print "Added", rule.asTuple()
		if assignments:
			for assignment in assignments:
				self.assignClass(assignment)

	def getClass(self, obj):
		for k,v in self.classes.iteritems():
			if obj in v:
				return k
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
		# for interpretation in interpretations:
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

	def likelihood(self, timestep, verbose=False):
		'''
		Makes sure both that event was covered by the ruleset and that everything predicted in the ruleset happened.
		'''
		# List of everything that happened, according to current class assignments and interaction rules
		interpretations = [self.interpret(event) for event in timestep.events]
		
		if verbose:
			print "Interpretation of event:"
			print [interpretation.asTuple() for interpretation in interpretations if interpretation is not False]
		if False not in interpretations:
			interpretations = [interpretation.asTuple() for interpretation in interpretations]
			ruleSet = [rule.asTuple() for rule in self.interactionSet]
			if all([self.checkInterpretation(i, timestep) for i in interpretations]):
			# if all([i in ruleSet for i in interpretations]):
				#if everything in the interpretation is accounted for by the ruleset
				relevantRules = [self.findRelevantRules(event) for event in timestep.events]
				for rules in relevantRules:
					if not all([r in interpretations for r in rules]):
						if verbose:
							print "Likelihood failed because not all events predicted by the theory happened."
						return 0.
				return 1.
			if verbose:
				print "Likelihood failed because the event was parseable by the theory, but not in the theory. Likely due to preconditions"
			return 0.
		if verbose:
			print "Likelihood failed because some aspect of the event wasn't interpretable by the current theory."
		return 0.

	def checkInterpretation(self, interpretation, timestep):
		if interpretation:
			for rule in self.interactionSet:
				if rule.asTuple()==interpretation:
					if rule.preconditions == False:
						return True # TODO: Should this be False? or should line above be True?
					elif all([p.check(timestep.agentState) for p in rule.preconditions]):
						return True
			return False #If we've checked everything and found no matching rule or rule+precondition, reutrn false.
		return False #uninterpretable interpretation returns False, too.

	# def checkRule(self, backpack, rule, event):
	# 	interpretation = self.interpret(event)
	# 	if interpretation is not False:
	# 		if rule.preconditions == False:
	# 			if rule.asTuple() == interpretation.asTuple():
	# 				return True
	# 			else: return False
	# 		else:
	# 			if rule.asTuple() == interpretation.asTuple() and all([p.check(backpack) for p in rule.preconditions]):
	# 				return True
	# 			else: return False
	# 	return False

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
		elif len(self.classes.keys())>0 and newClasses>0:
			numClasses = len(self.classes.keys())
			classes = self.classes.keys()
			for i in range(1, newClasses+1):
				classes.append('c'+str(numClasses+i))
			return classes
		else: return False

	def searchForAssignments(self, event):
		x1, x2 = self.searchForPossibleClasses(event[1]), self.searchForPossibleClasses(event[2])
		if x1 and x2: #if both yielded possibilities
			return list(itertools.product(x1,x2))
		else: return False

	def keepRulesAddAssignments(self, event):
		'''
		Try to make it fit according to the current rules by searching
		over possible class assignments for the objects
		Returns list of proposals
		Each proposal is a [rule, assignments] pair.
		'''
		possibleAssignments = self.searchForAssignments(event)
		if possibleAssignments:
			possibleRules = []
			for assignment in possibleAssignments:
				if (event[0], assignment[0], assignment[1]) in [i.asTuple() for i in self.interactionSet]:
					interaction = InteractionRule(event[0], assignment[0], assignment[1])
					classAssignments = [(assignment[0], event[1]), (assignment[1],event[2])]
					possibleRules.append([interaction, classAssignments])
			if len(possibleRules)>0:
				# print "fits existing theories, needs new class assignment. Possible rules are:"
				# print possibleRules
				return possibleRules
			else: 
				print "Proposal failed. Can't fit into existing theory."
				return []

	def keepAssignmentsAddRules(self, event):
		'''
		In response to a new predicate: Generates new rule
		that applies either to combinations of existing classes, or adds new classes
		'''
		x1, x2 = self.searchForPossibleClasses(event[1], newClasses=1), \
		self.searchForPossibleClasses(event[2], newClasses=2)
		combinations = list(itertools.product(x1,x2))
		possibleRules = []
		for c in combinations:
			interaction = InteractionRule(event[0], c[0], c[1])
			classAssignments = [(c[0], event[1]), (c[1], event[2])]
			possibleRules.append([interaction, classAssignments])
		return possibleRules

	def keepAssignmentsAddPreconditions(self, backpack, event):
		concepts = []
		# print backpack
		for b in backpack.keys():
			concepts.extend(generateNumberConcepts(b, backpack[b]))
		print "concepts", concepts
		preconditions = [Precondition(c[0], lambda x: x[c[1]] > c[2]) for c in concepts] # TODO: Add flexible operator
		possibleRules = []
		for p in preconditions:
			interpretation = self.interpret(event)
			if interpretation:
				interpretation.addPrecondition(p)
				possibleRules.append([interpretation, False]) #second slot is for new assignments
		# for rule in possibleRules:
			# rule[0].display()
		return possibleRules

	def generateHypotheses(self, timestep, hypotheticals=False, verbose=False):
		# Count how many events are in the list. 
		#Base case: Only one tuple
		if len([e for e in timestep.events if type(e)==tuple])==1: # TODO: When would there be different event data types (i.e. not tuples?)
			if verbose:
				print "in base case"

			if hypotheticals==False:
				if verbose:
					print "generating proposals without appending them to hypotheticals"
				return self.generateProposals(timestep.agentState, timestep.events[0], hypothetical=True, verbose=verbose)
			else:
				proposals = []
				for h in hypotheticals:
					proposals.extend(h.generateProposals(timestep.agentState, timestep.events[0], hypothetical=True, verbose=verbose))
				if verbose:
					print "appending hypotheses to these hypotheticals:"
					print hypotheticals
					print proposals
				return proposals #which are instantiated as hypothetical theories because of the hypothetical=True argument just above.
		
		#Recursive case
		else:
			if verbose:
				print "in recursive case. First event", timestep.events[0]
			firstEvent = TimeStep(timestep.agentAction, timestep.agentState, [timestep.events[0]]) # TODO: Why splitting this into the first event, and all other events?
			allOtherEvents = TimeStep(timestep.agentAction, timestep.agentState, timestep.events[1:])
			if verbose:
				print "other events", timestep.events[1:]
			return self.generateHypotheses(allOtherEvents, self.generateHypotheses(firstEvent), verbose=verbose)

	def generateProposals(self, backpack, event, hypothetical=False, verbose=False):
		'''
		Right now this is mostly greedy. If no rules in ruleset, adds
		rules necessary to explain current event.
		Otherwise:
			-Check for new assignments that fit with current rule set
			-Add preconditions to existing rules but don't change assignments
			-Add totally new rule
		'''
		if verbose:
			print "In verbose mode."
			print "generating proposals..."

		timestep = TimeStep(False, backpack, [event]) #hacked this rather than making a more complex likelihood function
		if self.likelihood(timestep) == 1.:
			if verbose:
				print "no proposals needed; event", event, "already fully explained!"
			if hypothetical==True:
				return [self] #Returning a workable hypothesis (self) so that generateHypotheses can build on it.

		proposals = []
		
		#The below should not be if/else; it should do all but the first 
		#condition simultaneously.
		if len(self.interactionSet) == 0:
			#base case: no theory yet.
			interaction = InteractionRule(event[0], 'c1', 'c2')
			classAssignments = [('c1', event[1]), ('c2', event[2])]
			if verbose:
				print "no theory yet. Proposing", interaction.asTuple(), "with class assignments:", classAssignments
			proposals.append([interaction, classAssignments])
		
		else:
			if event[0] in self.predicates:
				relevantRules = [rule for rule in self.interactionSet if rule.interaction==event[0]]
				if not (self.getClass(event[1]) and self.getClass(event[2])):
					#known predicate, but current assignments don't fit
					if verbose:
						print event[0], "is a known predicate, but current assignments don't fit. Proposing extensions"
					new_proposals = self.keepRulesAddAssignments(event)
					proposals.extend(new_proposals)	

			 	elif not any([rule.slot1==self.getClass(event[1]) and rule.slot2==self.getClass(event[2]) for rule in relevantRules]):				
			 		if verbose:
						print event[0], "uses a known predicate, but current rules don't cover it. Proposing extensions"
			 		new_proposals = self.keepAssignmentsAddRules(event)
			 		proposals.extend(new_proposals)
			 	else:
			 		if verbose:
			 			print event[0], "is a known predicate and classes are known. Proposing preconditions."
			 		new_proposals = self.keepAssignmentsAddPreconditions(backpack, event)
					proposals.extend(new_proposals)
			elif event[0] in self.predicates and (self.getClass(event[1]) and self.getClass(event[2])) and len(backpack.keys())>0:
				#FIX: This is sketchy; it's not checking for predicates being in the right slots.
				#if we know the predicate and the classes but for some reason we've been sent to generate proposals,
				#generate precondition proposals:
				if verbose:
					print "known predicate and classes. Proposing preconditions:"
				new_proposals = self.keepAssignmentsAddPreconditions(backpack, event)
				proposals.extend(new_proposals)
			elif event[0] not in self.predicates:
				#new predicate. propose new predicate with all possible new assignments.
				if verbose:
					print "encountered new predicate", event[0]+". Proposing new predicate + new assignments:"
				new_proposals = self.keepAssignmentsAddRules(event)
				proposals.extend(new_proposals)
			else:
				if verbose:
					print "timestep doesn't match any theory-induction conditions."
		
		if verbose:
			print ""
			print "Proposals:"
			for p in proposals:
				p[0].display()
				print p[1]
			print "____"
			# print proposals
		if not hypothetical:
			return proposals
		elif hypothetical:
			return self.extend(proposals, [timestep], hypothetical=True)


def generateNumberConcepts(c,n):
	concepts = []
	for i in range(n):
		text = c+">"+str(i)
		concepts.append((text,c,i))
	return concepts

def induction(timesteps):
	theory = Theory()
	g.hypothesisSpace = [theory]
	print g.theoryCount, "theories"
	to_remove = []
	for i in range(len(timesteps)):
		timestep = timesteps[i]
		print "interpreting timestep", i, "events:", timestep.events
		print "(theory IDs, likelihoods):"
		print [(h.theoryID, h.likelihood(timestep)) for h in g.hypothesisSpace]
		for h in g.hypothesisSpace:
			if h.likelihood(timestep) < 1.0:
				newHypotheses = h.generateHypotheses(timestep)
				if len(newHypotheses)>0:
					# print newHypotheses
					print "generated", len(newHypotheses), "proposals. extending now"
					h.replace(newHypotheses, timesteps[0:i+1])
		g.hypothesisSpace = [h for h in g.hypothesisSpace if h.likelihood(timesteps[i])==1.]
		print "(theoryID, likelihood) for", timestep.events
		print [(h.theoryID, h.likelihood(timestep)) for h in g.hypothesisSpace]
		print "_____"
	return g.hypothesisSpace

if __name__ == "__main__":
	g = Game()
	trace = [{'agentAction': 'up', 'agentState': {}, 'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE')]}, {'agentAction': 'up', 'agentState': {}, 'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE'), ('undoAll', 'ORANGE', 'BLACK')]}, {'agentAction': 'right', 'agentState': {}, 'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE')]}, {'agentAction': 'up', 'agentState': {'medicine': 1}, 'effectList': [('changeResource', 'DARKBLUE', 'WHITE', 1), ('killSprite', 'DARKBLUE', 'WHITE')]}]
	#,{'agentAction': 'down', 'agentState': {'medicine': 1}, 'effectList': [('killSprite', 'DARKBLUE', 'GOLD')]}]
	timesteps = [TimeStep(tr['agentAction'], tr['agentState'], tr['effectList']) for tr in trace]


	"""Testing precondition machinery"""
	t = Theory()
	g.hypothesisSpace = [t]
	g.backpack = {'health':0, 'treasure':1, 'coin':3}

	i1 = InteractionRule('killSprite', 'c1', 'c2')
	
	p1 = Precondition('health>1', lambda x: x['health']>1) 
	p2 = Precondition('treasure>2', lambda x: x['treasure']>2)

	# p1 = Precondition('health>1','health',1)
	# p2 = Precondition('treasure>2', 'treasure',2)

	i1.addPrecondition(p2)
	a1 = [('c1', 'DARKBLUE'), ('c2', 'RED')]
	t.addProposal([i1,a1])
	e = TimeStep(False, {'health':2, 'treasure':1}, [('killSprite', 'DARKBLUE', 'RED')])
	print t.likelihood(e,verbose=True) #0.0
	e = TimeStep(False, {'health':2, 'treasure':3}, [('killSprite', 'DARKBLUE', 'RED')]) 
	print t.likelihood(e,verbose=True) #1.0
	#_________
	e1 = TimeStep(False, {'health':2, 'treasure':1}, [('killSprite', 'DARKBLUE', 'RED')])
	print t.likelihood(e1) #0.0
	e2 = TimeStep(False, {'health':0, 'treasure':0}, [('bounceForward', 'DARKBLUE', 'RED')])
	print t.likelihood(e2) #0.0
	nh = t.generateHypotheses(e2, hypotheticals=False, verbose=False)
	#Conditioned on the hypotheses it generated to explain *e2*, it can easily generate good ones for e1.
	nh2 = nh[0].generateHypotheses(e1, hypotheticals=False, verbose=True) 
	#But it currently can't do things in the other direction: conditioned on a simple hypothesis that ignored the
	#AgentState at e1, modify in a way that explains e2


	#TODO:
	#When you're explaining e2, you have to retroactively change rules that explained e1 for it to make sense.
	#fix generateHypotheses(): should iterate over and over until what it returns is useful.

