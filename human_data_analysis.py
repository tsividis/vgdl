import json
from IPython import embed
from collections import defaultdict
import os, csv

folder = "../human_gamestates/Group14"
data_path = "../"
modelrun_ID = 'NA'
agent_type = 'human'

### TODO:

### The current script only does group 1!!!

def write_interaction_file(group, single_subject_single_game, subject_ID, games):
	if 'human_interaction_data_{}'.format(group) not in os.listdir(data_path):
		h = open('{}/human_interaction_data_{}'.format(data_path, group), 'w+')
		interactionfilewriter = csv.writer(h)
		interactionfilewriter.writerow(('agent_type', 'subject_ID', 'modelrun_ID', 'game_name', 'level_number', 'episode_number', 'event_type', 'count'))
	else:
		h = open('{}/human_interaction_data_{}'.format(data_path, group), 'a+')	
		interactionfilewriter = csv.writer(h)


	game_dict = defaultdict(lambda: list())
	for i, episode in enumerate(single_subject_single_game):
		if len(episode.keys())>1:
			print "found more than one key in an episode. You were probably wrong about what the keys correspond to"
			embed()

		game_name, game_level, game_number, game_round = game_string_to_info(episode.keys()[0])

		# if game_name in ['closing_gates_1', 'plaqueattack_1']:
			# continue
		# embed()
		if games!='all' and not any([g in game_name for g in games]):
			continue

		print "continuing; found game: {}".format(game_name)
		game_dict[(game_name, game_level, game_round)].append(episode)
	
	previous_game = None
	
	for ky in sorted(game_dict.keys(), key=lambda x:(x[0], int(x[1]), int(x[2]))):
		full_episode = game_dict[ky][0].values()[0]

		game_name, game_level, game_round = ky[0], ky[1], ky[2]
		
		if previous_game==None or previous_game!=game_name:
			episode_number = 0
		previous_game = game_name

		frms = sorted(full_episode, key=lambda x: x['frame'])

		objects = frms[0]['objects']
		IDs_to_object_names = dict()
		IDs_to_object_names['-1'] = 'EOS'
		for object_type, object_instances in objects.items():
			for object_ID, object_details in object_instances.items():
				IDs_to_object_names[str(object_ID)] = str(object_type)
		
		
		event_dict = defaultdict(lambda:0)
		previous_frame_events = set()
		for j,frm in enumerate(frms):
			for object_type, object_instances in frm['objects'].items():
				for object_ID, object_details in object_instances.items():
					if str(object_ID) not in IDs_to_object_names:
						IDs_to_object_names[str(object_ID)] = str(object_type)


			step, events, score, win = frm['frame'], frm['events'], frm['score'], frm['win']
			# cumulative_steps += step
			timestep_events = set()

			try:
				filtered_events = []
				for e in events:
					if e is not None and tuple(e) not in previous_frame_events:
						filtered_events.append(e)
				
				events = filtered_events
			except:
				print "problem with events"
				embed()
			if 'frogs' in game_name:
				event_list = []
				for e in events:
					if e is not None:
						try:
							event_list.append((e[0], IDs_to_object_names[str(e[1])], IDs_to_object_names[str(e[2])]))
						except:
							pass
							# print "key error in", game_name
				events = event_list
				for e in events:
					if e in  [('changeResource', 'avatar', 'water'),('changeResource', 'avatar', 'log')]:
						pass
					else:
						timestep_events.add(tuple(sorted((e[1], e[2]))))
			else:	
				for e in events:
					try:
						translated_event = tuple(sorted((IDs_to_object_names[str(e[1])], IDs_to_object_names[str(e[2])])))
						# print translated_event
						timestep_events.add(translated_event)
						# translated_event = tuple((IDs_to_object_names[str(e[1])], IDs_to_object_names[str(e[2])]))

					except:
						# print "Key error", game_name, e
						pass

					# event_dict[translated_event] += 1
					# all_event_types.add(translated_event)

			for translated_event in timestep_events:
				event_dict[translated_event] += 1

			previous_frame_events = set([tuple(e) for e in frm['events'] if e is not None])

		for event_name, count in event_dict.items():
			row = (agent_type, subject_ID, modelrun_ID, game_name, game_level, episode_number, event_name, count)
			interactionfilewriter.writerow(row)
		
		try:
			episode_number += 1
		except:
			print "episode-number problem with", game_name, game_level, game_round, "subject_ID", subject_ID, "single_subject_single_game counter:", i
			episode_number = 1 ##

	h.close()


def game_string_to_info(game_string):
	split_string = game_string.split('_')
	game_level, game_number, game_round = str(split_string[-3]), str(split_string[-2]), str(split_string[-1])
	game_name = str('_'.join([s for s in split_string[:-3] if s not in ['gvgai', 'expt', 'variant']]))
	
	return game_name, game_level, game_number, game_round


def find_subject_data(subject_ID):
	path = folder + '/' + subject_ID
	json_file = open(path, 'rb')
	single_subject_single_game = json.load(json_file)  ## WRONG. This is not single subject, single game. There are two games here.
	print "found ", subject_ID
	print "inspect 'episodes' object"
	episodes = single_subject_single_game[0][single_subject_single_game[0].keys()[0]]
	embed()

## we've lost all the info for various subjects after episode 5. e.g., for Raw_Nov12th_H1WZF6DaX

def write_interaction_files(folder, games):
	group = folder[folder.find('Group'):]
	for filename in os.listdir(folder):
	# filename = 'Raw_Nov12th_B1c1RTP67'
		path = folder + "/" + filename
		data_path = '.'
		json_file = open(path, 'rb')
		single_subject_single_game = json.load(json_file)  ## WRONG. This is not single subject, single game. There are two games here.
		subject_ID = filename
		write_interaction_file(group, single_subject_single_game, subject_ID, games)


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


# folder = "../human_gamestates/Group1"
# write_interaction_files(folder, ['bait_2'])
# make_heatmaps(folder, 'bait', 0)

# for i in range(1,16):
# 	folder = "../human_gamestates/Group{}".format(i)
# 	write_interaction_files(folder, 'all')

embed()

