import json
from IPython import embed
from collections import defaultdict
import os, csv
import pickle
from vgdl.plotting import featurePlot
import matplotlib.pyplot as plt
from matplotlib.ticker import NullLocator
import numpy as np


"""
Generates heatmaps from ddqn data
Sample usage:
make_heatmaps(['aliens', 'zelda'])
make_heatmaps() ## will make them for all games
"""


path = '../data_files/dqn_interaction_data/state_data'
if 'heatmaps' not in os.listdir('.'):
	os.makedirs('heatmaps')
if 'ddqn' not in os.listdir('heatmaps'):
	os.makedirs('heatmaps/ddqn')
dqn_state_files = [f for f in os.listdir(path) if 'DS_Store' not in f]


def makeHeatmap(statesEncountered, filename, newformat=False):
	from vgdl.plotting import featurePlot
	import matplotlib.pyplot as plt
	from matplotlib.ticker import NullLocator
	import numpy as np

	if newformat:
		width, height = statesEncountered['game_info']
		width = width-1
		height = height-1
		statesEncountered = statesEncountered['episodes']
	else:
		## Have to hard-code level info for games where ddqn was run before we started storing level info in the ddqn data itself
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
		elif 'sokoban' in filename:
			if statesEncountered[0][3] in [0,1]:
				width, height = 19, 11
			else:
				print "You don't have dimensions for this game"
				embed()
		elif 'zelda' in filename:
			width, height = 13, 9
		else:
			print "You don't have dimensions for this game"
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
	filename = filename+'_max='+str(int(np.max(m)))
	plt.savefig(filename, bbox_inches='tight', pad_inches=0)
	plt.close()

def make_heatmaps(requested_games='all'):

	for filename in dqn_state_files:
		agent_type = 'DDQN'
		agent_seed = '0'
		if '.csv' in filename:	
			if '101' in filename:
				agent_type = agent_type+'_1k'
			elif '102' in filename:
				agent_type = agent_type+'_10k'
			elif '103' in filename:
				agent_type = agent_type+'_100k'
			else:
				#normal case
				agent_type = agent_type+'_200'
			game_name = filename[:filename.find('.csv')]
		elif '.pkl' in filename:
			if '100k' in filename:
				agent_type = agent_type+'_100k'
			elif '10k' in filename:
				agent_type = agent_type+'_10k'
			elif '1k' in filename:
				agent_type = agent_type+'_10k'
			else:
				print "loading dqn data. didn't recognize eps_decay value in filename: {}".format(filename)
				embed()
			agent_seed = filename[filename.find('seed')+len('seed'):filename.find('_decay')]
			game_name = filename[:filename.find('_DDQN')]

		if requested_games=='all' or game_name in requested_games:
			
			f = open(path+'/'+filename)
			try:
				state_data = pickle.load(f)
				if 'episodes' in state_data.keys():
					## state_data['gameInfo']: x,y size of game.
					## state_data['episodes']: all the episodes. Expect many. Each is a (left, top, time, level) tuple.
					levels = [[],[],[],[],[],[]]
					prev_level = state_data['episodes'][0][0][3]
					for episode in state_data['episodes']:
						curr_level = episode[0][3]
						levels[curr_level].extend(episode)

					for i, statesEncountered in enumerate(levels):
						outfilename = 'heatmaps/ddqn/{}_level{}_{}_{}'.format(game_name, i, agent_type, agent_seed)
						if statesEncountered:
							try:
								makeHeatmap(statesEncountered, outfilename)
							except:
								print "problem w/ heatmap in {}, level {}".format(game_name, i)
				else:
					for i,level_data in enumerate(state_data.values()):
						outfilename = 'heatmaps/ddqn/{}_level{}_{}_{}'.format(game_name, i, agent_type, agent_seed)
						if level_data:
							try:
								makeHeatmap(level_data, outfilename, newformat=True)
							except:
								print "problem w/ heatmap in {}, level {}".format(game_name, i)
			except:
				print "problem loading pickle data for {}".format(filename)



