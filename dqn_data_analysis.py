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

	## find dimensions:
	# max_x, max_y = max([s[0] for p in statesEncountered]), max([s[1] for p in statesEncountered])
	if 'bait' not in filename:
		print "warning -- you don't have dimensions for this game"
		embed()
	if statesEncountered[0][3]==0:
		width, height = 4, 5
	elif statesEncountered[0][3]==1:
		width, height = 12, 9
	else:
		print "warning -- you don't have dimensions for this level"
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

for filename in dqn_state_files:
	game_name = filename[:filename.find('.csv')]
	f = open(path+'/'+filename)
	state_data = pickle.load(f)

	## state_data['gameInfo']: x,y size of game.
	## state_data['episodes']: all the episodes. Expect many. Each is a (left, top, time, level) tuple.

	levels = []
	level_data = []
	prev_level = state_data['episodes'][0][0][3]
	for episode in state_data['episodes']:
		curr_level = episode[0][3]
		if curr_level == prev_level:
			# print "same level"
			level_data.extend(episode)
		else:
			print "new level"
			levels.append(level_data)
			level_data = [episode]
		prev_level = curr_level
	levels.append(level_data)

	for i, statesEncountered in enumerate(levels):
		outfilename = 'heatmaps/ddqn/{}_{}'.format(game_name, agent_type)
		try:
			makeHeatmap(statesEncountered, outfilename)
		except:
			print "problem w/ heatmap"
			embed()

	break

	## break these up into unique levels (just looks at last element of the tuple for each episode)
	## then put all those together into a single list
	## then plot

	## later you can play with plotting beginnings and ends of an episode.

embed()
