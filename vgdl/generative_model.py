from collections import defaultdict
from IPython import embed
import itertools
import numpy as np
import random


classes_in_game = ['a','b','c']
avatar_states = [0,1,2]
conditions = ['collision']
effects = ['kill_a', 'kill_b', 'kill_c', 'bounceForward', 'cloneSprite', 'pickUp', 'stepBack']


class State:
	def __init__(self):
		self.assertions_about_state = defaultdict(lambda:0) ## Simple way of representing arbitrary things that may obtain in the state
		self.rules = [] ## If any rule has occurred in this state, both the condition and the effect occurred.


class Condition:
	def __init__(self, predicate=None, classes=None, assertion_about_state={}):

		## Conditions can either have predicates and classes (e.g., (collision a b) ), or can be truth statements about the game state.
		
		self.predicate = predicate
		self.classes = tuple(sorted(classes)) if classes is not None else None
		self.assertion_about_state = assertion_about_state

	def __repr__(self):
		if self.predicate:
			return str((self.predicate, self.classes))
		else:
			return str((self.assertion_about_state))

	def __hash__(self):
		return hash((self.predicate, self.classes, tuple(sorted(self.assertion_about_state.items()))))

	def __eq__(self, other):
		return hash(self)==hash(other)

	def __lt__(self, other):
		if self.classes is not None: 
			if other.classes is not None:
				return self.classes.__lt__(other.classes)
			else:
				return True
		else:
			return False


class Effect:
	def __init__(self, effect):
		self.effect = effect

	def __repr__(self):
		return str(self.effect)

	def __hash__(self):
		return hash(self.effect)
	
	def __eq__(self, other):
		return hash(self)==hash(other)


class Rule:
	def __init__(self, conditions, effect, occurrence_rate=.2):
		self.conditions = conditions
		self.effect = effect
		self.occurrence_rate = occurrence_rate

	def __repr__(self):
		return str((self.conditions, self.effect))

	def __hash__(self):
		return hash((tuple([hash(c) for c in sorted(self.conditions)]), hash(self.effect)))

	def __eq__(self, other):
		return hash(self)==hash(other)

	def apply(self, state):
		
		## We use 'apply' when sampling rules in states. If state assertions are met in a given state, then a rule can be applied (meaning its effect 'occurs').

		for condition in self.conditions:
			if condition.assertion_about_state:
				for assertion, val in condition.assertion_about_state.items():
					if state.assertions_about_state[assertion] != val:
						return None

		if self.occurrence_rate > random.random():
			return self

		return None


class Detector:
	def __init__(self, rules, parameters):
		self.rules = rules ## the rules the detector knows about
		self.conditions_set = set()
		self.effects_set = set()

		self.timestep_to_rules = defaultdict(lambda:[])
		self.timestep_to_conditions = defaultdict(lambda:[])
		self.timestep_to_effects = defaultdict(lambda:[])
		self.conditions_to_timesteps = defaultdict(lambda:set())
		self.effects_to_timesteps = defaultdict(lambda:set())	
		self.effect_to_conditions = defaultdict(lambda:set())	
		self.effect_to_explanations = defaultdict(lambda:set())
		self.cond_intersect_pct = defaultdict(lambda:0)
		self.effect_intersect_pct = defaultdict(lambda:0)

		self.composite_rank = defaultdict(lambda:0)
		self.filtered_composite_rank = defaultdict(lambda:0)

		self.timesteps_explained_by_combination_of_rules_threshold = parameters['timesteps_explained_by_combination_of_rules_threshold']
		self.set_overlap_cutoff = parameters['set_overlap_cutoff']

		self.condition_false_negative_rates = defaultdict(lambda: parameters['condition_false_negative_rates'])
		self.effect_false_negative_rates = defaultdict(lambda: parameters['effect_false_negative_rates'])
		self.condition_false_positive_rates = defaultdict(lambda: parameters['condition_false_positive_rates'])
		self.effect_false_positive_rates = defaultdict(lambda: parameters['effect_false_positive_rates'])


	def detect_rule(self, state, rule):
		
		## Checks whether any of the conditions and effects in a rule occurred in a state
		## Produces both false negatives and false positives

		condition = None
		effect = None
		if rule in state.rules:
			## Detect rule if it's there, unless false negative
			false_negative_rate = 0.
			rule_condition, rule_classes = None, None
			for cond in rule.conditions:
				if cond.classes is not None and random.random() > self.condition_false_negative_rates[cond.predicate]:
					condition = cond

			if random.random() > self.effect_false_negative_rates[rule.effect]:
				effect = rule.effect
		else:
			## Produce false positives for conditions
			for cond in conditions:
				if random.random() < self.condition_false_positive_rates[cond]:
					classes_involved = tuple(sorted([random.choice(classes_in_game), random.choice(classes_in_game)]))
					condition = Condition(cond, (classes_involved))
			
		return condition, effect

	def detect_rules(self, state):
		
		## Detects occurrence of all conditions/effects we know about in a given game state

		conditions_set, effects_set = set(), set()
		for rule in self.rules:
			c, e = self.detect_rule(state, rule)
			if c is not None:
				conditions_set.add(c)
			if e is not None:
				effects_set.add(e)

		## detect false positives separately. TODO: separate conditions more explicitly in detect_rule().
		for effect in effects:
			e = self.detect_effect(effect)
			if e is not None:
				effects_set.add(e)

		## Add things we 'know' about the state (e.g., skip detectors for state assertions for now)
		conditions_set.add(Condition(assertion_about_state={'avatar_state':state.assertions_about_state['avatar_state']}))

		self.conditions_set = self.conditions_set.__or__(conditions_set)
		self.effects_set = self.effects_set.__or__(effects_set)
		return conditions_set, effects_set


	## just false positives
	def detect_effect(self, effect_name):
		if random.random() < self.effect_false_positive_rates[effect_name]:
			effect = Effect(effect_name)
		else:
			effect = None
		return effect


	def learn_theory(self):
		self.calculate_likelihoods()
		self.rank_rules()
		self.explain_effects()
		return


	def calculate_likelihoods(self):
		# calculates p(E|C) and p(C|E) for all C -- even for complex ones

		for effect in self.effects_set:
			max_cond_intersection_pct = 0
			max_effect_intersection_pct = 0

			curr_effect_timesteps = self.effects_to_timesteps[effect]
			condition_proposals = self.generate_condition_proposals(self.conditions_set)

			# loop through each effect-condition pairing
			for condition_proposal in condition_proposals:
				self.effect_to_conditions[effect].add(condition_proposal)

				curr_condition_timesteps = self.conditions_to_timesteps[condition_proposal]

				proposed_rule = (condition_proposal, effect)
				
				# calculates (|E intersect C| / |C|)
				if len(curr_condition_timesteps)>0:
					self.cond_intersect_pct[proposed_rule] = float(len(curr_condition_timesteps.intersection(curr_effect_timesteps))) / len(curr_condition_timesteps)

				# calculates (|E intersect C| / |E|)
				if len(curr_effect_timesteps)>0:
					self.effect_intersect_pct[proposed_rule] = float(len(curr_condition_timesteps.intersection(curr_effect_timesteps))) / len(curr_effect_timesteps)
		return 


	def rank_rules(self, prior_weight=.8):

		## Rank rules by a combination of 'likelihood' and 'prior'

		for rule, val in self.cond_intersect_pct.items():
			condition = rule[0]
			self.composite_rank[rule] = val * prior_weight**len(condition)
		self.filtered_composite_rank = dict(self.composite_rank)
		return


	def explain_effects(self):
		for effect in self.effects_set:
			if self.effects_to_timesteps[effect]:
				self.provide_explanations_until_threshold(effect)
		return


	def populate_dictionaries(self, states):

		## Iterate through state history, generate condition and effect proposals, populate dictionaries that store various key mappings used for inference

		for i,state in enumerate(states):
			conditions, effects = self.detect_rules(state)
			self.timestep_to_conditions[i] = conditions
			self.timestep_to_effects[i] = effects

			## Generate possibly complex condition proposals given the things we detected as occurring in the state
			## TODO: this shouldn't be done here, as you're calling the function over and over on different states,
			## and as you may not generate the correct proposal if a detector failed
			condition_proposals = self.generate_condition_proposals(conditions)

			for condition in condition_proposals:
				if condition is not None:
					self.conditions_to_timesteps[condition].add(i)
		
			for effect in effects:
				if effect is not None:
					self.effects_to_timesteps[effect].add(i)

		return


	def get_condition_timesteps(self, conditions):
		
		## Set overlap of timesteps at which all the conditions occurred

		intersecting_timesteps = self.conditions_to_timesteps[conditions[0]]
		if len(conditions)>1:
			for condition in conditions:
				intersecting_timesteps = intersecting_timesteps.intersection(self.conditions_to_timesteps[condition])
		return intersecting_timesteps


	def generate_condition_proposals(self, conditions):

		## For now, doing the simple/dumb thing: proposals are conjuncts of (normal_condition, avatar_state), or just (normal_condition,)

		normal_proposals = [c for c in conditions if not c.assertion_about_state]
		state_proposals = [c for c in conditions if c.assertion_about_state]

		return list(itertools.product(normal_proposals, state_proposals))+[(p,) for p in normal_proposals]


	def greedy_effect_explainer(self, effect, candidates):

		## Given the existing set of candidate explanations for an effect, returns the greedily next best explanation
		if not candidates:
			return None

		best_score = max(candidates.keys())
		best_candidate = candidates[best_score]
		return best_candidate


	def grow_explanation(self, effect):

		## Grab the greedily best explanation for the effect, and remove explanations that are sufficiently redundant with that from the set of available explanations for the next round

		candidates = dict([(self.composite_rank[k], k) for k in self.filtered_composite_rank.keys() if k[1].effect==effect])
		try:
			best_explanation = self.greedy_effect_explainer(effect, candidates)
		except:
			print "greedy effect explainer failed"
			embed()
		if best_explanation is None:
			return None
		best_explanation_cause = best_explanation[0]

		## Filter all candidates that overlap too much with the best explanation
		for pair in list(itertools.product([best_explanation_cause], [v for v in candidates.values()])):
			best_explanation_cause_timesteps = self.conditions_to_timesteps[pair[0]]
			comparison_cause_timesteps = self.conditions_to_timesteps[pair[1][0]]

			## Remove any rules whose explained timesteps overlap SET_OVERLAP_CUTOFF% with the new best explanation (i.e., remove redundancy)
			if get_set_overlap_percentage(best_explanation_cause_timesteps, comparison_cause_timesteps) > self.set_overlap_cutoff:
				self.filtered_composite_rank.pop(pair[1])
		
		return best_explanation


	def get_percentage_of_desired_timesteps_explained(self, effect, candidates):

		## How well do the candidate explanations explain the effect?
		
		total_timesteps = self.effects_to_timesteps[effect]
		num_total_timesteps = len(total_timesteps)

		effect_occurrence_percentage = num_total_timesteps / (1.0 * len(self.timestep_to_effects.keys()))

		# percentage_of_timesteps_we_should_explain = max(0.0, effect_occurrence_percentage - self.effect_false_positive_rates[effect])

		num_all_timesteps = len(self.timestep_to_effects.keys())
		num_timesteps_we_should_ignore = round(num_all_timesteps * self.effect_false_positive_rates[effect])

		explained_timesteps = set()
		for c in candidates:
			explained_timesteps = explained_timesteps.union(self.conditions_to_timesteps[c[0]])

		overlap = explained_timesteps.intersection(total_timesteps)
		
		num_timesteps_we_should_explain = max(num_total_timesteps-num_timesteps_we_should_ignore, 0)

		# print "overlap", 1.0 * len(overlap)
		# print "num_timesteps_we_should_explain", num_timesteps_we_should_explain
		# print ""

		if len(overlap)==0 and num_timesteps_we_should_explain==0:
			return 1.
		else:
			return min(1., 1.0 * len(overlap) / num_timesteps_we_should_explain) #len(total_timesteps)


	def provide_explanations_until_threshold(self, effect):

		## Keep (greedily) adding explanations until you're explaining the desired effect well enough

		candidates_so_far = self.effect_to_explanations[effect]

		percentage_of_timesteps_explained = self.get_percentage_of_desired_timesteps_explained(effect, candidates_so_far)

		# print "explaining", effect
		# print "candidates", candidates_so_far
		# print "percentage so far", percentage_of_timesteps_explained

		# if effect.effect in ['kill_b', 'kill_c', 'pickUp', 'cloneSprite']:
			# embed()
		# if effect.effect == 'kill_a':
			# embed()
		while percentage_of_timesteps_explained < self.timesteps_explained_by_combination_of_rules_threshold:
			best_explanation = self.grow_explanation(effect)
			if best_explanation is None:
				return
			# print "about to add", best_explanation
			self.effect_to_explanations[effect].add(best_explanation)
			candidates_so_far = self.effect_to_explanations[effect]
			percentage_of_timesteps_explained = self.get_percentage_of_desired_timesteps_explained(effect, candidates_so_far)
			# print "percentage now", percentage_of_timesteps_explained
			# print ""

		return

	def convert_explanation_to_rule_object(self, explanation):
		conditions, effect = explanation
		return Rule(conditions, effect)


	def calculate_rule_learning_score(self):
		rules = set()
		for effect, explanations in self.effect_to_explanations.items():
			for explanation in explanations:
				rules.add(self.convert_explanation_to_rule_object(explanation))
		
		try:
			score = get_set_overlap_percentage(rules, self.rules)
		except:
			print "score overlap problem"
			embed()
		return score


	def print_history(self, states):
		## Prep for formatting
		max_rule_length, max_condition_length, max_effect_length = 0, 0, 0
		for i in self.timestep_to_conditions.keys():
			# embed()
			rule_length = max([len(str(r)) for r in states[i].rules]) if states[i].rules else 0
			condition_length, effect_length = len(str(self.timestep_to_conditions[i])), len(str(self.timestep_to_effects[i]))
			
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
						print " "*5, "|", rule, " "*(max_rule_length-rule_length), "|", " "*(max_condition_length-condition_length), " |"
				except:
					embed()
		print ""


	def print_readout(self):
		# # ## Print all rules and their P(E|C)
		# print "Rules and their P(E|C):"
		# for k,v in sorted(self.cond_intersect_pct.items()):
		# 	print k,v
		# print ""

		# ### Print all rules and their P(C|E)
		# print "Rules and their P(C|E):"
		# for k,v in sorted(self.effect_intersect_pct.items()):
		# 	print k,v
		# print ""

		print "Rules and their P(E|C), sorted by E:"
		for effect in self.effects_set:
			effect_keys = [k for k in self.cond_intersect_pct.keys() if effect in k]
			for item in sorted([(k,self.cond_intersect_pct[k]) for k in effect_keys], key=lambda x:-x[1]):
				print item
			print ""

		print "Rules and their P(C|E), sorted by E:"
		for effect in self.effects_set:
			effect_keys = [k for k in self.effect_intersect_pct.keys() if effect in k]
			for item in sorted([(k,self.effect_intersect_pct[k]) for k in effect_keys], key=lambda x:-x[1]):
				print item
			print ""

		for effect in self.effects_set:
			effect_keys = [k for k in self.composite_rank.keys() if effect in k]
			for item in sorted([(k,self.composite_rank[k]) for k in effect_keys], key=lambda x:-x[1]):
				print item
			print ""

		print "Best learned rules"
		for effect in sorted(self.effect_to_explanations.keys(),reverse=True):
			for rule in self.effect_to_explanations[effect]:
				print rule
		print ""

		print "Actual rules"
		for rule in sorted(self.rules, key=lambda x:x.effect.effect, reverse=True):
			print rule
		print ""


def generate_states(rules, length):
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


def get_set_overlap_percentage(set1,set2):
	numerator = 1.0*len(set1&set2)
	return (numerator/len(set1) + numerator/len(set2))/2


def run_experiment(rules, num_timesteps, parameters):
	states = generate_states(rules, num_timesteps)
	d = Detector(rules, parameters)
	d.populate_dictionaries(states)
	d.learn_theory()

	### Print what actually happened and what the detectors found
	# d.print_history(states)
	# d.print_readout()

	score = d.calculate_rule_learning_score()
	# embed()
	return score, d

def run_experiments(rules, num_timesteps, parameters, n):
	## Runs experiment n times, returns average score
	scores, models = [], []
	for i in range(n):
		score, model = run_experiment(rules, num_timesteps, parameters)
		scores.append(score)
		models.append(model)
	return np.mean(scores), models



