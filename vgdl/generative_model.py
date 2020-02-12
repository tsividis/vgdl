from collections import defaultdict
from IPython import embed
import random


### TODO: Allow for false positives and false negatives
### TODO: You want to be able to use a condition about the avatar state as an actual rule, and then evaluate its conditional probability.
### Probably the way to do this is not to iterate through all the conditions and effects separately, but to have a method that takes a given rule and can then evaluate its specific conditional probabilities.


INTERSECT_THRESHOLD = .5

avatar_states = [0,1,2]
conditions = ['collision']
effects = ['killSprite', 'bounceForward', 'cloneSprite', 'pickUp', 'stepBack']
condition_false_negative_rates = defaultdict(lambda: 0)
effect_false_negative_rates = defaultdict(lambda: 0)
condition_false_positive_rates = defaultdict(lambda: 0)
effect_false_positive_rates = defaultdict(lambda: 0)

for p in effects:
	effect_false_negative_rates[p] = .1
	effect_false_positive_rates[p] = .05

for c in conditions:
	condition_false_negative_rates[c] = .1
	condition_false_positive_rates[c] = .05

class State:
	def __init__(self):
		self.assertions_about_state = defaultdict(lambda:0) ## Simple way of representing arbitrary things that may obtain in the state
		self.rules = [] ## an entire rule has occurred in this state, meaning both the condition and the effect occurred.


class Condition:
	def __init__(self, condition=None, classes=None, assertion_about_state={}):
		self.condition = condition
		self.classes = classes
		self.assertion_about_state = assertion_about_state

	def __repr__(self):
		if self.condition:
			return str((self.condition, self.classes))
		else:
			return str((self.assertion_about_state))

class Effect:
	def __init__(self, effect):
		self.effect = effect

	def __repr__(self):
		return str(self.effect)

class Rule:
	def __init__(self, conditions, effect, occurrence_rate=.2):
		self.conditions = conditions
		self.effect = effect
		self.occurrence_rate = occurrence_rate

		## Add assert about having only one condition be about classes
	def __repr__(self):
		return str((self.conditions, self.effect))

	def apply(self, state):
		for condition in self.conditions:
			if condition.assertion_about_state:
				for assertion, val in condition.assertion_about_state.items():
					if state.assertions_about_state[assertion] != val:
						return None

		if self.occurrence_rate > random.random():
			return self

		return None

class Detector:
	def __init__(self):
		self.conditions_set = set()
		self.effects_set = set()

		self.timestep_to_rules = defaultdict(lambda:[])
		self.timestep_to_conditions = defaultdict(lambda:[])
		self.timestep_to_effects = defaultdict(lambda:[])
		self.conditions_to_timesteps = defaultdict(lambda:set())
		self.effects_to_timesteps = defaultdict(lambda:set())	
		self.effect_to_conditions = defaultdict(lambda:[])	

		self.cond_intersect_pct = defaultdict(lambda:0)
		self.effect_intersect_pct = defaultdict(lambda:0)

	def detect_rule(self, state, rule):
		condition = None
		effect = None
		if rule in state.rules:
			false_negative_rate = 0.
			rule_condition, rule_classes = None, None
			for cond in rule.conditions:
				false_negative_rate += condition_false_negative_rates[cond.condition]
				if cond.classes is not None:
					rule_condition = cond.condition
					rule_classes = cond.classes

			if random.random() > false_negative_rate:
				condition = (rule_condition, rule_classes)
			if random.random() > effect_false_negative_rates[rule.effect]:
				effect = rule.effect
		# else:
			## false positive stuff
		
		return condition, effect

	def detect_rules(self, state):
		conditions_set, effects_set = set(), set()
		for rule in rules:
			c, e = self.detect_rule(state, rule)
			if c is not None:
				conditions_set.add(c)
			if e is not None:
				effects_set.add(e)
		self.conditions_set = self.conditions_set.__or__(conditions_set)
		self.effects_set = self.effects_set.__or__(effects_set)
		return conditions_set, effects_set


	def populate_dictionaries(self, states):

		for i,state in enumerate(states):
			conditions, effects = d.detect_rules(state)
			self.timestep_to_conditions[i] = conditions
			self.timestep_to_effects[i] = effects

			for condition in conditions:
				if condition is not None:
					self.conditions_to_timesteps[condition].add(i)
		
				for effect in effects:
					if effect is not None:
						self.effects_to_timesteps[effect].add(i)
						self.effect_to_conditions[effect].append(condition)
		return

	def learn_theory(self):
		self.bindings = []
		for effect in self.effects_set:
			max_cond_intersection_pct = 0
			max_effect_intersection_pct = 0

			curr_effect_timesteps = self.effects_to_timesteps[effect]

			# loop through each effect-condition pairing
			for condition in self.conditions_set:
				curr_condition_timesteps = self.conditions_to_timesteps[condition]

				proposed_rule = (condition, effect)
				
				# calculates (|E intersect C| / |C|)
				if len(curr_condition_timesteps)>0:
					self.cond_intersect_pct[proposed_rule] = float(len(curr_condition_timesteps.intersection(curr_effect_timesteps))) / len(curr_condition_timesteps)

				# calculates (|E intersect C| / |E|)
				if len(curr_effect_timesteps)>0:
					self.effect_intersect_pct[proposed_rule] = float(len(curr_condition_timesteps.intersection(curr_effect_timesteps))) / len(curr_effect_timesteps)

				# check against threshold, append to bindings
				if self.cond_intersect_pct[proposed_rule] > INTERSECT_THRESHOLD:
					self.bindings.append(proposed_rule)

		return 

	def print_history(self, states):
		## Prep for formatting
		max_rule_length, max_condition_length, max_effect_length = 0, 0, 0
		max_line_length = 0
		for i in self.timestep_to_conditions.keys():
			line_length = len(states[i].rules)
			rule_length, condition_length, effect_length = len(str(states[i].rules)), len(str(self.timestep_to_conditions[i])), len(str(self.timestep_to_effects[i]))
			
			if rule_length > max_rule_length:
				max_rule_length = rule_length
			if condition_length > max_condition_length:
				max_condition_length = condition_length
			if effect_length > max_effect_length:
				max_effect_length = effect_length

		print ""
		for i in self.timestep_to_conditions.keys():
			conditions = list(self.timestep_to_conditions[i])
			effects = list(self.timestep_to_effects[i])
			condition_length = len(str(conditions))
			effect_length = len(str(effects))

			for j,rule in enumerate(states[i].rules):
				try:
					rule_length = len(str(rule))
					if j==0:
						print i, " "*(4-len(str(i))), "|", rule, " "*(max_rule_length-rule_length), "|", conditions, " "*(max_condition_length-condition_length), "|", effects
					else:
						condition_length, effect_length = 0, 0
						print " "*5, "|", rule, " "*(max_rule_length-rule_length), "|", " "*(max_condition_length-condition_length), "|"
				except:
					embed()
		print ""



r1 = Rule(conditions=[Condition('collision', ('a','b')), Condition(assertion_about_state={'avatar_state':0})], effect=Effect('killSprite'))

r2 = Rule(conditions=[Condition('collision', ('a','b')), Condition(assertion_about_state={'avatar_state':1})], effect=Effect('stepBack'))

r3 = Rule(conditions=[Condition('collision', ('c', 'd'))], effect=Effect('bounceForward'))

rules = [r1, r2, r3]

state = State()

def generate_states(length):
	states = []
	for i in range(length):
		s = State()
		s.assertions_about_state['avatar_state'] = random.choice([0,1])

		for rule in rules:
			r = rule.apply(s)
			if r is not None:
				s.rules.append(r)

		states.append(s)
	return states

def print_history(states):
	for i,state in enumerate(states):
		print i, state.rules


    # self.effect_intersect_pct[proposed_rule] = float(len(curr_condition_timesteps.intersection(curr_effect_timesteps))) / len(curr_effect_timesteps)



states = generate_states(500)
d = Detector()
d.populate_dictionaries(states)
d.learn_theory()

# ## Print what actually happened and what the detectors found
d.print_history(states)

# ## Print all rules and their P(E|C)
print "Rules and their P(E|C):"
for k,v in sorted(d.cond_intersect_pct.items()):
	print k,v
print ""

# ## Print all rules and their P(C|E)
print "Rules and their P(C|E):"
for k,v in sorted(d.effect_intersect_pct.items()):
	print k,v
print ""

embed()


