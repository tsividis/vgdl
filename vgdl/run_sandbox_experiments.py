from generative_model import *

## function that takes rules, num_timesteps, error_rates, thresholds, and returns rule overlap
## function that calls that function N times

## plotting functions -- this time in python?
## function that iterates over some grid of parameters, gets data for all
## expose rule occurrence parameter, too.


#######################
#					  #
#	   EXPERIMENT     #
#					  #
#######################



r1 = Rule(conditions=[Condition('collision', ('a','b')), Condition(assertion_about_state={'avatar_state':0})], effect=Effect('kill_a'))

r2 = Rule(conditions=[Condition('collision', ('a','b')), Condition(assertion_about_state={'avatar_state':1})], effect=Effect('stepBack'))

r3 = Rule(conditions=[Condition('collision', ('c', 'd'))], effect=Effect('bounceForward'))

r4 = Rule(conditions=[Condition('collision', ('a', 'a'))], effect=Effect('kill_a'))

r5 = Rule(conditions=[Condition('collision', ('a', 'c'))], effect=Effect('kill_a'))

rules = {r1, r2, r3, r4, r5}

parameters = {
	'timesteps_explained_by_combination_of_rules_threshold' : .9,
	'set_overlap_cutoff': .7,
	'condition_false_negative_rates': .1,
	'condition_false_positive_rates': .05,
	'effect_false_negative_rates': 0.,
	'effect_false_positive_rates': 0.
}

scores = []
for i in range(10,1000, 50):
	scores.append(run_experiments(rules, i, parameters, 5))

embed()
