import itertools, random


class Game(object):
	def __init__(self):
		self.backpack = {}


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
		return backpack[self.item]>self.num 

	def display(self):
		print self.text

'''
class Precondition(object):
	def __init__(self, text, fn):
		self.text = text
		self.fn = fn

	def check(self, arg):
		return self.fn(arg) #1 is dummy arg

	def display(self):
		print self.text
'''

class Property(object):
	def __init__(self, vgdlType, color, args):
		self.vgdlType = vgdlType
		self.color = color 
		self.args = args

	#should enforce proper syntax for properties
	def display():
		pass

class InteractionRule(object):
	def __init__(self, interaction, c1, c2, preconditions=False):
		self.interaction = interaction
		self.slot1 = c1
		self.slot2 = c2
		self.preconditions = preconditions

	#should enforce proper syntax for interaction rules

	def display(self):
		if not self.preconditions:
			print self.interaction, self.slot1, self.slot2
		else:
			print self.interaction, self.slot1, self.slot2, [p.text for p in self.preconditions]
		return
	def asTuple(self):
		return (self.interaction, self.slot1, self.slot2)

	def addPrecondition(self, precondition):
		if self.preconditions == False:
			self.preconditions = [precondition]
		else:
			if precondition not in self.preconditions:
				self.preconditions.append(precondition)
		return

	def checkPreconditions(self, backpack):
		return all([p.check(backpack) for p in self.preconditions])




#each hypothesis is a full theory. If you need to improve a theory and
#this yields multiple theories, then return all of them and store them in your
#hypothesis space.
class Theory(object):
	def __init__(self):
		self.spriteSet = [] #property rules
		self.levelMapping = []
		self.interactionSet = [] #interaction rules
		self.terminationSet = []
		self.classes = {} #k:classes, v:objects
		self.predicates = []

	def displayRules(self):
		print ""
		print "Current rule set:"
		for rule in self.interactionSet:
			rule.display()

	def displayClasses(self):
		print ""
		print "Current class assignments:"
		print self.classes

	def assignClass(self, classObjectPair):
		#Adds object-class assignments; avoids duplicates
		c, o = classObjectPair[0], classObjectPair[1]
		if c in self.classes.keys():
			if o not in self.classes[c]:
				self.classes[c].append(o)
				print "added", o, "to class", c
		else:
			self.classes[c] = [o]
			print "added", o, "to class", c

	def addRule(self, rule):
		#Adds rule if it is not in interactionSet
		if rule.interaction not in self.predicates:
			self.predicates.append(rule.interaction)
		if rule.asTuple() not in [i.asTuple() for i in self.interactionSet]:
			self.interactionSet.append(rule)
			return True
		return False

	def addProposal(self, proposal):
		#Adds proposal to theory; takes care of rule and assignments
		rule, assignments = proposal[0], proposal[1]
		if self.addRule(rule):
			print "Added", rule.asTuple()
		for assignment in assignments:
			self.assignClass(assignment)

	def getClass(self, o):
		for k,v in self.classes.iteritems():
			if o in v:
				return k
		return False

	def interpret(self, event): 
		#looks up objects by their corresponding class under the theory,
		#returns a corresponding interactionRule.
		#If those objects aren't known, returns false.
		#Example: event is a tuple: ('bounceForward', 'ORANGE', 'DARKBLUE')
		#if we know that ORANGE=c1 and DARKBLUE=c2, returns the InteractionRule
		#that corresponds to (bounceForward, c1, c2)
		c1, c2 = self.getClass(event[1]), self.getClass(event[2])
		if c1 and c2:
			return InteractionRule(event[0], c1, c2)
		else:
			return False

	def likelihood(self, backpack, event):
		interpretation = self.interpret(event)
		if interpretation is not False:
			if any([self.checkRule(backpack, i, event) for i in self.interactionSet]):
				return 1.
		return 0.

	def checkRule(self, backpack, rule, event):
		interpretation = self.interpret(event)
		if interpretation is not False:
			if rule.preconditions == False:
				if rule.asTuple() == interpretation.asTuple():
					return True
				else: return False
			else:
				if rule.asTuple() == interpretation.asTuple() and all([p.check(backpack) for p in rule.preconditions]):
					return True
				else: return False
		return False

	def searchForPossibleClasses(self, o, newClasses=0):
		#if the object has been assigned, return it. Otherwise return all
		#possible classes. Optional argument can posit existence of a new class;
		#user specifies whether to add 0, 1, or 2 new classes.
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
		if x1 is not False and x2 is not False: #if both yielded possibilities
			return list(itertools.product(x1,x2))
		else: return False

	def keepRulesAddAssignments(self, event):
		"""
		Try to make it fit according to the current rules by searching
		over possible class assignments for the objects
		Returns list of proposals
		Each proposal is a [rule, assignments] pair.
		"""
		possibleAssignments = self.searchForAssignments(event)
		if possibleAssignments is not False:
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
		#In response to a new predicate: Generates new rule
		#that applies either to combinations of existing classes, or adds new classes
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
		for b in backpack.keys():
			concepts.extend(generateNumberConcepts(b, backpack[b]))
		preconditions = [Precondition(c[0], c[1], c[2]) for c in concepts]
		possibleRules = []
		for p in preconditions:
			interpretation = self.interpret(event)
			if interpretation:
				interpretation.addPrecondition(p)
				possibleRules.append(interpretation)
		return possibleRules

	def generateProposals(self, backpack, event):
		"""Right now this is mostly greedy. If no rules in ruleset, adds
		rules necessary to explain current event.
		Otherwise:
			-Check for new assignments that fit with current rule set
			-Add preconditions to existing rules but don't change assignments
			-Add totally new rule
		"""
		print "generating proposals..."
		if self.likelihood(backpack, event) == 1.:
			print "no proposals needed; event already fully explained!"
			return
		proposals = []
		#The below should not be if/else; it should do all but the first 
		#condition simultaneously.
		if len(self.interactionSet) == 0:
			#base case: no theory yet.
			interaction = InteractionRule(event[0], 'c1', 'c2')
			classAssignments = [('c1', event[1]), ('c2', event[2])]
			print "no theory yet. Proposing", interaction.asTuple(), "with class assignments:", classAssignments
			proposals.append([interaction, classAssignments])
		else:
			if event[0] in self.predicates and not (self.getClass(event[1]) and self.getClass(event[2])):
				#known predicate, but current assignments don't fit
				print event[0], "is a known predicate, but current assignments don't fit. Proposing:"
				new_proposals = self.keepRulesAddAssignments(event)
				for p in new_proposals:
					print p[1]
				proposals.extend(new_proposals)
			if event[0] in self.predicates and (self.getClass(event[1]) and self.getClass(event[2])) and len(backpack.keys())>0:
				#if we know the predicate and the classes but for some reason we've been sent to generate proposals,
				#generate precondition proposals:
				print "known predicate and classes. Proposing extensions:"
				new_proposals = self.keepAssignmentsAddPreconditions(event)
				for p in new_proposals:
					p.display()
				proposals.extend(new_proposals)
			if event[0] not in self.predicates:
				#new predicate. propose new predicate with all possible new assignments.
				print "encountered new predicate", event[0]+". Proposing new predicate + new assignments:"
				new_proposals = self.keepAssignmentsAddRules(event)
				for p in new_proposals:
					p[0].display(), p[1]
				proposals.extend(new_proposals)
		return proposals


def generateNumberConcepts(c,n):
	concepts = []
	for i in range(n):
		text = c+">"+str(i)
		concepts.append((text,c,i))
	return concepts

'''
g = Game()
t = Theory()
e = ('killSprite', 'WHITE', 'DARKBLUE')
e2 = ('killSprite', 'WHITE', 'PURPLE')
e3 = ('bounceForward', 'BLUE', 'PINK')

print ""
print "trying to interpret event", e
print "result:", t.interpret(e) #False
print "likelihood", t.likelihood(g.backpack, e) #0
proposals = t.generateProposals(g.backpack, e) #proposals is a list of proposals
t.addProposal(proposals[0])
print "likelihood", t.likelihood(g.backpack, e) #1
t.displayRules() #one rule
t.displayClasses()

print ""
print "likelihood of new event", e2, t.likelihood(g.backpack, e2)
proposals = t.generateProposals(g.backpack, e2)
t.addProposal(proposals[0])
print "likelihood", t.likelihood(g.backpack, e2)
proposal = proposals[0]

t.displayRules() #one rule
t.displayClasses()
print ""

print "likelihood of new event", e3, t.likelihood(g.backpack, e3)
proposals = t.generateProposals(g.backpack, e3) #
print "generated", len(proposals), "proposals in total"
proposal = random.choice(proposals)
print "Randomly selecting one of these"
t.addProposal(proposal)
t.displayRules()
t.displayClasses()
print "likelihood", t.likelihood(g.backpack, e3)
print ""

g.backpack = {'health':0, 'treasure':1, 'coin':3}
e4 = ('bounceForward', 'RED', 'ORANGE')

"""tests for preconditions"""
print "Now let's explicitly call keepAssignmentsAddPreconditions() on e2", e2
proposals = t.keepAssignmentsAddPreconditions(g.backpack, e2)
print "this generates the following proposals:"
[p.display() for p in proposals]
print "notice that because health was 0 when this was called, it doesn't generate any health-related hypotheses"
print "specifically checking proposal", proposals[3].display()
print "result:", proposals[3].checkPreconditions(g.backpack) #False --> Should be True
p = Precondition('health>1','health',1)
print "adding", p.text, "to those preconditions"
proposals[3].addPrecondition(p) # Adds p to the fourth precondition
[p.display() for p in proposals]
print "result", proposals[3].checkPreconditions(g.backpack) #False
print "Now adding 2 health to backpack"
g.backpack['health'] = 2
print "And re-checking preconditions:", proposals[3].checkPreconditions(g.backpack) #True
'''
