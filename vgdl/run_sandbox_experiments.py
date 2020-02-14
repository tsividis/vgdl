from generative_model import *
# from ggplot import *
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt



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


condition_false_negative_ranges = np.array(range(0,3,1))/10.
condition_false_positive_ranges = np.array(range(0,3,1))/10.
effect_false_negative_ranges = np.array(range(0,3,1))/10.
effect_false_positive_ranges = np.array(range(0,3,1))/10.

data = []

for params in itertools.product(*[condition_false_negative_ranges, condition_false_positive_ranges]):
	# , effect_false_negative_ranges, effect_false_positive_ranges]):


	parameters['condition_false_negative_rates'] = params[0]
	parameters['condition_false_positive_rates'] = params[1]
	# parameters['effect_false_negative_rates'] = params[2]
	# parameters['effect_false_positive_rates'] = params[3]

	param_name = str([(k[0:3], v) for k,v in parameters.items()])

	print param_name

	for i in range(50,1000,50):
		score = run_experiments(rules, i, parameters, 5)
		data.append((param_name, i, score))


df = pd.DataFrame(data, 
               columns =['Params', 'Timesteps', 'Score']) 


dirname = '../plots/sanbdox_plots/'
if not os.path.isdir(dirname):
	os.makedirs(dirname)


sns.set(style="whitegrid")

f, ax = plt.subplots(figsize=(8, 6))
sns.despine(f, left=True, bottom=True)

sns.lineplot(x="Timesteps", y="Score",
                hue="Params", #size="depth",
                palette="ch:r=-.2,d=.3_r",
                # hue_order=clarity_ranking,
                #sizes=(1, 8), linewidth=0,
                data=df, ax=ax)
lgd = plt.legend(loc='upper center',bbox_to_anchor=(.5, -.2), borderaxespad=0.)

plt.savefig(dirname+'foo.png',bbox_extra_artists=(lgd,),bbox_inches='tight', dpi=500)


# Draw a scatter plot while assigning point colors and sizes to different
# # variables in the dataset
# f, ax = plt.subplots(figsize=(6.5, 6.5))
# sns.despine(f, left=True, bottom=True)

# sns.scatterplot(x="Timesteps", y="Score",
#                 hue="Params", #size="depth",
#                 palette="ch:r=-.2,d=.3_r",
#                 # hue_order=clarity_ranking,
#                 sizes=(1, 8), linewidth=0,
#                 data=df, ax=ax)
# plt.show()

