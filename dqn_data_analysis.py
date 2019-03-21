import json
from IPython import embed
from collections import defaultdict
import os, csv
import pickle
from vgdl.plotting import featurePlot
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator
import numpy as np

path = 'dqn_interaction_data/state_data'
if 'ddqn' not in os.listdir('heatmaps'):
	os.makedirs('heatmaps/ddqn')
agent_type = 'DDQN'
dqn_state_files = [f for f in os.listdir(path) if 'DS_Store' not in f]


def makeHeatmap(statesEncountered, filename):
	from vgdl.plotting import featurePlot
	import matplotlib.pyplot as plt
	from matplotlib.ticker import NullLocator
	import numpy as np

	## Hard-coding this for now, but will add dims for each level to the new script
	## for getting state data from DDQN.
	if 'bait' in filename:
		if statesEncountered[0][3]==0:
			width, height = 4, 5
		elif statesEncountered[0][3]==1:
			width, height = 12, 9
		else:
			print "warning -- you don't have dimensions for this level"
			embed()
	elif 'boulderdash' in filename:
		width, height = 26, 13
	elif 'butterflies' in filename:
		width, height = 28, 12
	elif 'expt_ee' in filename:
		width, height = 26, 10
	elif 'frogs' in filename:
		width, height = 28, 11
		if statesEncountered[0][3]==4: ## level 4 is smaller
			width, height = 28, 10
	elif 'relational' in filename:
		width, height = 22, 10
	elif 'portals' in filename:
		width, height = 19, 11
	elif 'zelda' in filename:
		width, height = 13, 9
	else:
		"You don't have dimensions for this game"
		embed()

	m = np.zeros((width+1, height+1))
	Xs, Ys = [],[]
	block_size = 30
	prev_state = (None, None)
	set_first_frame = False

	for s in statesEncountered:
		frame = s[2]
		x = int(round(s[0]/block_size))
		y = int(round(s[1]/block_size))
		if (x,y) != prev_state and (frame!=0 or not set_first_frame):
			m[x, y] += 1

		prev_state = (x,y)
		if frame == 0:
			set_first_frame = True
	# embed()
	plt.imshow(m.T, cmap='viridis')
	plt.gca().set_axis_off()
	plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0,
		hspace = 0, wspace = 0)
	plt.margins(0, 0)
	plt.gca().xaxis.set_major_locator(NullLocator())
	plt.gca().yaxis.set_major_locator(NullLocator())
	plt.savefig(filename, bbox_inches='tight', pad_inches=0)
	plt.close()

## you need to get info about the correct level by opening the game somewhere else :/

# for filename in dqn_state_files:
# 	game_name = filename[:filename.find('.csv')]
# 	if '101' in filename:
# 		agent_type = agent_type+'_1k'
# 	elif '102' in filename:
# 		agent_type = agent_type+'_10k'
# 	elif '103' in filename:
# 		agent_type = agent_type+'_100k'
# 	else:
# 		#normal case
# 		agent_type = agent_type+'_200'
# 	f = open(path+'/'+filename)
# 	state_data = pickle.load(f)
# 	## state_data['gameInfo']: x,y size of game.
# 	## state_data['episodes']: all the episodes. Expect many. Each is a (left, top, time, level) tuple.

# 	levels = [[],[],[],[],[],[]]
# 	prev_level = state_data['episodes'][0][0][3]
# 	for episode in state_data['episodes']:
# 		curr_level = episode[0][3]
# 		levels[curr_level].extend(episode)

# 	for i, statesEncountered in enumerate(levels):
# 		outfilename = 'heatmaps/ddqn/{}_level{}_{}'.format(game_name, i, agent_type)
# 		if statesEncountered:
# 			try:
# 				makeHeatmap(statesEncountered, outfilename)
# 			except:
# 				print "problem w/ heatmap"
# 				embed()

	# break

	## break these up into unique levels (just looks at last element of the tuple for each episode)
	## then put all those together into a single list
	## then plot

	## later you can play with plotting beginnings and ends of an episode.

embed()
