from generative_model import *
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

## expose rule occurrence parameter, too.

"""
Status summary:
Right now this is behaving reasonably. Given an expected failure rate,
it tries to explain events that exceed that failure rate.
As a result, this will sometimes provide more or fewer explanations than necessary and will not always find the correct ruleset.

Additional tuning can be done, but it might be worth, at this point, thinking more about how to shape the planner policy so that it generates interactions that are under its control, rather than tuning this more.

"""

#######################
#					  #
#	   EXPERIMENT     #
#					  #
#######################
dirname = '../plots/sanbdox_plots/'
if not os.path.isdir(dirname):
	os.makedirs(dirname)



r1 = Rule(conditions=[Condition('collision', ('a','b')), Condition(assertion_about_state={'avatar_state':0})], effect=Effect('kill_a'))

r2 = Rule(conditions=[Condition('collision', ('a','b')), Condition(assertion_about_state={'avatar_state':1})], effect=Effect('stepBack'))

r3 = Rule(conditions=[Condition('collision', ('c', 'd'))], effect=Effect('bounceForward'))

r4 = Rule(conditions=[Condition('collision', ('a', 'a'))], effect=Effect('kill_a'))

r5 = Rule(conditions=[Condition('collision', ('a', 'c'))], effect=Effect('kill_a'))

rulesets = {'set1': {r1, r2, r3, r4, r5},
			'set2': {r3, r4}
			}

parameters = {
	'timesteps_explained_by_combination_of_rules_threshold' : .8,
	'set_overlap_cutoff': .7,
	'condition_false_negative_rates': 0.,
	'condition_false_positive_rates': 0.,
	'effect_false_negative_rates': 0.0,
	'effect_false_positive_rates': 0.2
}


# condition_false_negative_ranges = np.array(range(0,1,1))/10.
# condition_false_positive_ranges = np.array(range(0,1,1))/10.
# effect_false_negative_ranges = np.array(range(0,3,1))/10.
# effect_false_positive_ranges = np.array(range(0,3,1))/10.

# data = []
# model_dict = defaultdict(lambda: [])
# for params in itertools.product(*[condition_false_negative_ranges, condition_false_positive_ranges, effect_false_negative_ranges, effect_false_positive_ranges]):


# 	parameters['condition_false_negative_rates'] = params[0]
# 	parameters['condition_false_positive_rates'] = params[1]
# 	parameters['effect_false_negative_rates'] = params[2]
# 	parameters['effect_false_positive_rates'] = params[3]

# 	condition_vals = str('cfn: {}, cfp: {}'.format(params[0], params[1])) 
# 	effect_vals = str('efn: {}, efp: {}'.format(params[2], params[3])) 
# 	param_name = condition_vals + ' ' + effect_vals
# 	print param_name

# 	for i in range(50,1000,50):
# 		score, models = run_experiments(rules, i, parameters, 10)
# 		data.append((param_name, condition_vals, effect_vals, i, score))
# 		# data.append((param_name, i, score))
# 		model_dict[param_name].append((score, models))



#########
data = []
model_dict = defaultdict(lambda: [])
condition_vals = str('cfp: {}, cfn: {}'.format(parameters['condition_false_positive_rates'], parameters['condition_false_negative_rates'])) 
effect_vals = str('efp: {}, efn: {}'.format(parameters['effect_false_positive_rates'], parameters['effect_false_negative_rates'])) 
param_name = condition_vals + ' ' + effect_vals

# print param_name

for ruleset_name,ruleset in rulesets.items():
	for i, steps in enumerate(range(0,500,20)):
		score, events, models = run_experiments(ruleset, steps, parameters, 10)
		data.append((ruleset_name, param_name, condition_vals, effect_vals, steps, score, events))
		model_dict[param_name].append((score, events, models))



# score, models = run_experiments(rules, 500, parameters, 10)

df = pd.DataFrame(data, 
               columns =['Ruleset', 'Param_name', 'Condition_vals', 'Effect_vals', 'Timesteps', 'Score', 'Events']) 
# df = pd.DataFrame(data, 
               # columns =['Param_name','Timesteps', 'Score']) 
filled_markers = ('o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'D', 'd', 'P', 'X')


### run the same stuff on larger sets of rulesets
### explore lots more parameters
### or make the experiments more complex, etc


sns.set_style("white")

for effect_val in df.Effect_vals.unique():
	effect_val_subset = df[df['Effect_vals']==effect_val]
	for ruleset_name in effect_val_subset.Ruleset.unique():
		subset = effect_val_subset[effect_val_subset['Ruleset']==ruleset_name]
		f, ax = plt.subplots(figsize=(8, 6))
		ax.set(ylim=(0, 1))
		ax.set_title('{}, {}'.format(ruleset_name, effect_val))

		sns.despine(f, left=True, bottom=True)

		sns.lineplot(x="Events", y="Score",
		                hue="Condition_vals", #size="depth",
		                palette="ch:r=-.2,d=.3_r",
		                data=subset, ax=ax)
		
		## If you want to plot against timesteps
		# ax2 = ax.twinx()
		# df.plot(x="Timesteps", y="Events", ax=ax2, legend=False)

		# sns.lineplot(x="Timesteps", y="Score",
		#                 hue="Condition_vals", #size="depth",
		#                 palette="ch:r=-.2,d=.3_r",
		#                 data=subset, ax=ax)
		# ax2 = ax.twinx()
		# df.plot(x="Timesteps", y="Events", ax=ax2, legend=False)


		lgd = plt.legend(loc='upper center',bbox_to_anchor=(.5, -.2), borderaxespad=0.)

		plt.savefig(dirname+'ruleset: {}'.format(ruleset_name) + 'effect_vals: {}.png'.format(effect_val),bbox_extra_artists=(lgd,),bbox_inches='tight', dpi=500)

embed()

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

