import json
from IPython import embed
from collections import defaultdict
import os, csv
import pickle

path = 'dqn_interaction_data/state_data'
dqn_state_files = [f for f in os.listdir(path) if 'DS_Store' not in f]

for filename in dqn_state_files:
	f = open(path+'/'+filename)
	state_data = pickle.load(f)
	## state_data['gameInfo']: x,y size of game.
	## state_data['episodes']: all the episodes. Expect many. Each is a (left, top, time, level) tuple.

	## break these up into unique levels (just looks at last element of the tuple for each episode)
	## then put all those together into a single list
	## then plot

	## later you can play with plotting beginnings and ends of an episode.

data_path = "../"
modelrun_ID = 'NA'
agent_type = 'DDQN'


def make_heatmaps(folder, game_name, level_number):
	if 'human' not in os.listdir('heatmaps'):
		os.makedirs('human')
	for filename in os.listdir(folder):
		path = folder + "/" + filename
		data_path = '.'

		json_file = open(path, 'rb')
		single_subject_single_game = json.load(json_file)  ## WRONG. This is not single subject, single game. There are two games here.
		relevant_episodes = []
		game_states = None
		for i,episode in enumerate(single_subject_single_game):
			gN, game_level, game_number, game_round = game_string_to_info(episode.keys()[0])
			# print gN, game_level

			## accumulate all the episodes for this game and level and then pass them to makeHeatmap

			if gN==game_name and game_level==str(level_number):
				print 'found {}, level {}'.format(gN, game_level)
				outfilename = 'heatmaps/human/{}_{}_human_{}'.format(game_name, game_level,filename)
				game_states = sorted(episode[episode.keys()[0]], key=lambda e:e['frame'])
				relevant_episodes.append(game_states)
				##make a filename for the heatmap
		
		if relevant_episodes:
			# unpacked_states = [item for sublist in relevant_episodes for item in sublist]	
			# makeHeatmap(unpacked_states, outfilename)
			makeHeatmap(relevant_episodes, outfilename)
			relevant_episodes = []
			# embed()


def makeHeatmap(statesEncountered, filename):
	from vgdl.plotting import featurePlot
	import matplotlib.pyplot as plt
	from matplotlib.ticker import NullLocator
	import numpy as np

	## figure out how to call this for something easy,
	## and then change things so that it takes multiple episodes and makes a heatmap that reflects the average amount of time, per episode, spent in each position.
	# first_state = statesEncountered[0]
	first_state = statesEncountered[0][0]

	## find dimensions:
	positions = []
	for object_instances in first_state['objects'].values():
		for object_info in object_instances.values():
			positions.append((object_info['x'], object_info['y']))
	max_x, max_y = max([p[0] for p in positions]), max([p[1] for p in positions])

	block_size = sorted(set([p[0] for p in positions]))[1]
	shrunken_width, shrunken_height = max_x/block_size, max_y/block_size
	

	episode_matrices = []
	for episode in statesEncountered:

		## Warning: these states aren't in order. But since you're just amassing time spent in each location, it shouldn't matter.
		states = [(s['objects']['avatar'].values()[0]['x'],s['objects']['avatar'].values()[0]['y'], s['frame']) for s in episode if s['objects']['avatar']]

		shrunken_states = [(s[0]/block_size, s[1]/block_size, s[2]) for s in states]

		m = np.zeros((shrunken_width+1, shrunken_height+1))
		prev_state = (None, None)
		set_first_frame = False

		for s in shrunken_states:
			x = int(round(s[0]))
			y = int(round(s[1]))
			frame = s[2]
			if (x,y) != prev_state and (frame!=0 or not set_first_frame):
				try:
					m[x, y] += 1
				except:
					print "index error with m"
					embed()
			prev_state = (x,y)
			if frame == 0:
				set_first_frame = True
		episode_matrices.append(m)

	# embed()
	m = np.mean(episode_matrices,axis=0)
	# m = np.maximum.reduce(episode_matrices)
	plt.imshow(m.T, cmap='viridis')
	plt.gca().set_axis_off()
	plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0,
		hspace = 0, wspace = 0)
	plt.margins(0, 0)
	plt.gca().xaxis.set_major_locator(NullLocator())
	plt.gca().yaxis.set_major_locator(NullLocator())
	plt.savefig(filename, bbox_inches='tight', pad_inches=0)
	plt.close()


embed()
