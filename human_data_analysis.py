import json
from IPython import embed
from collections import defaultdict
import os, csv
import cPickle

folder = "../human_gamestates/Group1"
data_path = "../"
modelrun_ID = 'NA'
agent_type = 'human'


games_to_folders = {
	'push_boulders_2': 'Group1',
	'closing_gates_1': 'Group1',
	'aliens_2': 'Group1',
	'ee_3': 'Group1',
	'plaqueattack_1': 'Group1',
	'missilecommand': 'Group1',

	'corridor_1': 'Group2',
	'butterflies': 'Group2',
	'zelda_3': 'Group2',
	'watergame_2': 'Group2',
	'avoidgeorge_1': 'Group2',
	'bees_and_birds': 'Group2',

	'survivezombies_1': 'Group3',
	'portals': 'Group3',
	'boulderdash': 'Group3',
	'surprise_2': 'Group3',
	'missilecommand_1': 'Group3',
	'avoidgeorge': 'Group3',

	'relational': 'Group4',
	'bait_1': 'Group4',
	'closing_gates': 'Group4',
	'helper_1': 'Group4',
	'chase_2': 'Group4',
	'sokoban': 'Group4',

	'survivezombies_2': 'Group5',
	'push_boulders_1': 'Group5',
	'ee_2': 'Group5',
	'zelda_1': 'Group5',
	'missilecommand_2': 'Group5',
	'avoidgeorge_3': 'Group5',

	'antagonist': 'Group6',
	'bait_2': 'Group6',
	'preconditions': 'Group6',
	'boulderdash_2': 'Group6',
	'ee': 'Group6',
	'sokoban_2': 'Group6',

	'chase_1': 'Group7',
	'preconditions_1': 'Group7',
	'aliens_4': 'Group7',
	'lemmings': 'Group7',
	'ee_1': 'Group7',
	'missilecommand_4': 'Group7',

	'lemmings_2': 'Group8',
	'plaqueattack_2': 'Group8',
	'missilecommand_3': 'Group8',
	'avoidgeorge_4': 'Group8',
	'relational_1': 'Group8',
	'bees_and_birds_1': 'Group8',

	'survivezombies': 'Group9',
	'portals_1': 'Group9',
	'surprise_1': 'Group9',
	'butterflies_2': 'Group9',
	'plaqueattack_3': 'Group9',
	'helper_2': 'Group9',

	'frogs': 'Group10',
	'myAliens_2': 'Group10',
	'aliens_3': 'Group10',
	'lemmings_3': 'Group10',
	'jaws_2': 'Group10',
	'butterflies_1': 'Group10',

	'frogs_3': 'Group11',
	'antagonist_1': 'Group11',
	'push_boulders': 'Group11',
	'aliens_1': 'Group11',
	'boulderdash_1': 'Group11',
	'avoidgeorge_2': 'Group11',

	'frogs_1': 'Group12',
	'antagonist_2': 'Group12',
	'portals_2': 'Group12',
	'myAliens_1': 'Group12',
	'corridor': 'Group12',
	'aliens': 'Group12',

	'frogs_2': 'Group13',
	'preconditions_2': 'Group13',
	'surprise': 'Group13',
	'plaqueattack': 'Group13',
	'zelda_2': 'Group13',
	'watergame': 'Group13',

	'relational_2': 'Group14',
	'chase_3': 'Group14',
	'jaws': 'Group14',
	'sokoban_1': 'Group14',
	'zelda': 'Group14',
	'watergame_1': 'Group14',

	'chase': 'Group15',
	'myAliens': 'Group15',
	'bait': 'Group15',
	'lemmings_1': 'Group15',
	'helper': 'Group15',
	'jaws_1': 'Group15',
}

game_dict = {

	('aliens', 0): (30,11),
	('aliens', 1): (30,11),
	('aliens', 2): (30,11),
	('aliens', 3): (30,11),
	('aliens', 4): (30,11),

	('antagonist', 0): (32,10),
	('antagonist', 1): (32,10),
	('antagonist', 2): (32,10),
	('antagonist', 3): (32,10),

	('avoidgeorge', 0): (24,11),
	('avoidgeorge', 1): (24,11),
	('avoidgeorge', 2): (24,11),
	('avoidgeorge', 3): (24,11),
	('avoidgeorge', 4): (24,11),

	('bait', 0):	(5,6),
	('bait', 1):	(13,9),
	('bait', 2):	(13,10),
	('bait', 3):	(7,9),
	('bait', 4):	(13,11),

	('bees_and_birds', 0):	(16,15),
	('bees_and_birds', 1):	(16,15),
	('bees_and_birds', 2):	(16,11),
	('bees_and_birds', 3):	(16,13),

	('boulderdash', 0):	(26,13),
	('boulderdash', 1):	(26,13),
	('boulderdash', 2):	(26,13),
	('boulderdash', 3):	(26,13),
	('boulderdash', 4):	(26,13),

	('butterflies', 0):	(28,11),
	('butterflies', 1):	(28,11),
	('butterflies', 2):	(28,11),
	('butterflies', 3):	(28,11),
	('butterflies', 4):	(28,12),

	('chase', 0):	(24,11),
	('chase', 1):	(24,11),
	('chase', 2):	(24,11),
	('chase', 3):	(24,11),
	('chase', 4):	(24,11),

	('closing_gates', 0):	(17,16),
	('closing_gates', 1):	(17,17),
	('closing_gates', 2):	(17,21),
	('closing_gates', 3):	(17,21),

	('corridor', 0):	(40,5),
	('corridor', 1):	(40,5),
	('corridor', 2):	(48,5),
	('corridor', 3):	(48,5),

	('ee', 0):	(26,10),
	('ee', 1):	(26,10),
	('ee', 2):	(26,10),
	('ee', 3):	(26,10),
	('ee', 4):	(26,10),

	('frogs', 0):	(28,11),
	('frogs', 1):	(28,11),
	('frogs', 2):	(28,11),
	('frogs', 3):	(28,11),
	('frogs', 4):	(28,10),

	('helper', 0):	(32,10),
	('helper', 1):	(32,10),
	('helper', 2):	(32,10),
	('helper', 3):	(32,10),

	('jaws', 0): (21,9),
	('jaws', 1): (21,9),
	('jaws', 2): (21,9),
	('jaws', 3): (21,9),
	('jaws', 4): (21,9),

	('lemmings', 0): (21,11),
	('lemmings', 1): (21,11),
	('lemmings', 2): (21,11),
	('lemmings', 3): (21,11),
	('lemmings', 4): (21,11),

	('missilecommand', 0): (24,13),
	('missilecommand', 1): (24,13),
	('missilecommand', 2): (24,13),
	('missilecommand', 3): (24,13),
	('missilecommand', 4): (24,13),

	('myAliens', 0): (32,14),
	('myAliens', 1): (32,14),
	('myAliens', 2): (32,14),
	('myAliens', 3): (32,14),
	('myAliens', 4): (32,14),

	('plaqueattack', 0): (24,22),
	('plaqueattack', 1): (24,22),
	('plaqueattack', 2): (24,22),
	('plaqueattack', 3): (24,22),
	('plaqueattack', 4): (23,22),

	('portals', 0): (19,11),
	('portals', 1): (19,11),
	('portals', 2): (19,11),
	('portals', 3): (19,11),
	('portals', 4): (19,11),

	('preconditions', 0): (18,10),
	('preconditions', 1): (18,5),
	('preconditions', 2): (18,7),
	('preconditions', 3): (18,10),
	('preconditions', 4): (18,10),

	('push_boulders', 0): (22,10),
	('push_boulders', 1): (22,10),
	('push_boulders', 2): (22,10),
	('push_boulders', 3): (22,10),

	('relational', 0): (22,10),
	('relational', 1): (22,10),
	('relational', 2): (22,10),
	('relational', 3): (22,10),

	('sokoban', 0):	(13,9),
	('sokoban', 1):	(13,9),
	('sokoban', 2):	(11,9),
	('sokoban', 3):	(9,8),

	('surprise', 0): (13,7),
	('surprise', 1): (13,7),
	('surprise', 2): (13,7),
	('surprise', 3): (13,7),

	('survivezombies', 0): (19,11),
	('survivezombies', 1): (19,11),
	('survivezombies', 2): (19,11),
	('survivezombies', 3): (19,11),
	('survivezombies', 4): (19,11),

	('watergame', 0): (7,6),
	('watergame', 1): (7,7),
	('watergame', 2): (7,9),
	('watergame', 3): (7,8),
	('watergame', 4): (7,8),

	('zelda', 0):	(13,9),
	('zelda', 1):	(13,9),
	('zelda', 2):	(13,9),
	('zelda', 3):	(13,9),
	('zelda', 4):	(13,9)
}

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
							# print "problem was with event", e
				events = event_list
				for e in events:
					if e in  [('changeResource', 'avatar', 'water')]:
						pass
					if e in [('changeResource', 'avatar', 'log')]:
						## pullWithIt didn't get recorded for human data, even though it's identical to changeResource.
						## overwriting it here and adding it.
						e = ('pullWithIt', 'avatar', 'log')
					# else:
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


def make_heatmaps(folder, game_name, level_number, only_grab_data=False):
	if 'human' not in os.listdir('heatmaps'):
		os.makedirs('human')

	## if we specified 'all', then make all games for the specified folder.
	## otherwise, find the folder that contains the game we care about
	if game_name !='all':
		folder = "../human_gamestates/" + games_to_folders[game_name]

	all_data = []
	for filename in os.listdir(folder):
		path = folder + "/" + filename
		data_path = '.'

		json_file = open(path, 'rb')
		subject_data = json.load(json_file)  ## WRONG. This is not single subject, single game. There are two games here.

		single_subject_single_game_dict = defaultdict(lambda:[])
		for episode in subject_data:
			gN, game_level, game_number, game_round = game_string_to_info(episode.keys()[0])
			single_subject_single_game_dict[gN].append(episode)

		# if 'closing_gates' in single_subject_single_game_dict.keys():
		# 	print "found closing gates"
		# 	embed()
		# if 'ryl' in filename or 'rya' in filename:
			# print "found nov12"
			# embed()
		all_data.append(single_subject_single_game_dict)
		# if 'ee_3' in single_subject_single_game_dict.keys():
		# 	print "found ee3"
		# 	embed()
		if not only_grab_data:
			for game in single_subject_single_game_dict.keys():
				single_subject_single_game = single_subject_single_game_dict[game]
				relevant_episodes = []
				game_states = None
				for i,episode in enumerate(single_subject_single_game):

					gN, game_level, game_number, game_round = game_string_to_info(episode.keys()[0])
					# print gN, game_level
					# if gN=='ee_3':
						# print "found ee_3"
						# embed()
					## accumulate all the episodes for this game and level and then pass them to makeHeatmap

					if (game_name=='all' or gN==game_name) and game_level==str(level_number):
						print 'found {}, level {}'.format(gN, game_level)
						outfilename = 'heatmaps/human/{}_{}_human_{}'.format(gN, game_level,filename)
						game_states = sorted(episode[episode.keys()[0]], key=lambda e:e['frame'])
						relevant_episodes.append(game_states)
						##make a filename for the heatmap
				
				if relevant_episodes:
					if game_name=='all':
						res = find_dimensions(folder, gN, level_number)
					else:
						res = find_dimensions(folder, game_name, level_number)
					if res!=False:
						width, height = res
						print "making heatmap"
						makeHeatmap(relevant_episodes, outfilename, width, height)
						relevant_episodes = []
					else:
						pass

	return all_data
# game_dimensions = dict()

def clear_dimensions(game_name):
	game_dimension_filename = '../game_dimensions'

	with open(game_dimension_filename, 'rb') as f:
		game_dimensions = cPickle.load(f)
	
	for k,v in game_dimensions.items():
		if game_name in k:
			game_dimensions.pop(k)
	with open(game_dimension_filename, 'wb') as f:
		cPickle.dump(game_dimensions, f)

	return


def find_dimensions(folder, game_name, level_number):
	if (game_name, level_number) in game_dict:
		return game_dict[(game_name, level_number)]
	else:
		non_variant_game_name = game_name[:game_name.rfind('_')]
		if (non_variant_game_name, level_number) in game_dict:
			return game_dict[(non_variant_game_name, level_number)]
		else:
			print "{} not in game_dict".format((game_name, level_number))
			return False

# def find_dimensions(folder, game_name, level_number):
# 	game_dimension_filename = '../game_dimensions'

# 	with open(game_dimension_filename, 'rb') as f:
# 		game_dimensions = cPickle.load(f)

# 	if (game_name, level_number) in game_dimensions:
# 		return game_dimensions[(game_name, level_number)]
# 	else:
# 		relevant_episodes = []
# 		for filename in os.listdir(folder):

# 			path = folder + "/" + filename
# 			data_path = '.'

# 			json_file = open(path, 'rb')
# 			single_subject_single_game = json.load(json_file)
# 			game_states = None
# 			for i,episode in enumerate(single_subject_single_game):
# 				gN, game_level, game_number, game_round = game_string_to_info(episode.keys()[0])
# 				if (game_name=='all' or gN==game_name) and game_level==str(level_number):
# 					print 'found {}, level {}'.format(gN, game_level)
# 					game_states = sorted(episode[episode.keys()[0]], key=lambda e:e['frame'])
# 					relevant_episodes.append(game_states)
# 		width, height = extract_dimensions_from_episodes(game_name, level_number, relevant_episodes)

# 		game_dimensions[(game_name, level_number)] = (width, height)
# 		with open(game_dimension_filename, 'wb') as f:
# 			cPickle.dump(game_dimensions, f)

# 	return width, height

def extract_dimensions_from_episodes(game_name, level_number, statesEncountered):

	first_state = statesEncountered[0][0]

	## find dimensions:
	positions = []
	for object_instances in first_state['objects'].values():
		for object_info in object_instances.values():
			positions.append((object_info['x'], object_info['y']))
	max_x, max_y = max([p[0] for p in positions]), max([p[1] for p in positions])

	block_size = sorted(set([p[0] for p in positions]))[1]
	width, height = max_x/block_size, max_y/block_size
	
	episode_matrices = []
	## iterate once over everything to get the right size for all the matrices
	for episode in statesEncountered:
		## Warning: these states aren't in order. But since you're just amassing time spent in each location, it shouldn't matter.
		states = [(s['objects']['avatar'].values()[0]['x'],s['objects']['avatar'].values()[0]['y'], s['frame']) for s in episode if s['objects']['avatar']]
		shrunken_states = [(s[0]/block_size, s[1]/block_size, s[2]) for s in states]
		width, height = max(width, max([s[0] for s in shrunken_states])), max(height, max([s[1] for s in shrunken_states]))
		print width, height
	return width, height

def makeHeatmap(statesEncountered, filename, width, height):
	from vgdl.plotting import featurePlot
	import matplotlib.pyplot as plt
	from matplotlib.ticker import NullLocator
	import numpy as np

	# ## figure out how to call this for something easy,
	# ## and then change things so that it takes multiple episodes and makes a heatmap that reflects the average amount of time, per episode, spent in each position.
	first_state = statesEncountered[0][0]

	# ## find dimensions:
	positions = []
	for object_instances in first_state['objects'].values():
		for object_info in object_instances.values():
			positions.append((object_info['x'], object_info['y']))
	# max_x, max_y = max([p[0] for p in positions]), max([p[1] for p in positions])

	block_size = sorted(set([p[0] for p in positions]))[1]
	# width, height = width/block_size, height/block_size

	episode_matrices = []
	# ## iterate once over everything to get the right size for all the matrices
	# for episode in statesEncountered:
	# 	## Warning: these states aren't in order. But since you're just amassing time spent in each location, it shouldn't matter.
	# 	states = [(s['objects']['avatar'].values()[0]['x'],s['objects']['avatar'].values()[0]['y'], s['frame']) for s in episode if s['objects']['avatar']]
	# 	shrunken_states = [(s[0]/block_size, s[1]/block_size, s[2]) for s in states]
	# 	width, height = max(width, max([s[0] for s in shrunken_states])), max(height, max([s[1] for s in shrunken_states]))

	for episode in statesEncountered:

		## Warning: these states aren't in order. But since you're just amassing time spent in each location, it shouldn't matter.
		states = [(s['objects']['avatar'].values()[0]['x'],s['objects']['avatar'].values()[0]['y'], s['frame']) for s in episode if s['objects']['avatar']]

		shrunken_states = [(s[0]/block_size, s[1]/block_size, s[2]) for s in states]

		# width, height = max(width, max([s[0] for s in shrunken_states])), max(height, max([s[1] for s in shrunken_states]))
		
		# if 'portals' in filename:
			# m = np.zeros((width+2, height+2))
		# else:
		m = np.zeros((width, height))

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
					print "index error with m for filename {}. width, height= {},{}. x,y= {}, {}".format(filename, width, height, x, y)
					# embed()
			prev_state = (x,y)
			if frame == 0:
				set_first_frame = True
		episode_matrices.append(m)

	# embed()
	try:
		m = np.sum(episode_matrices,axis=0)
	except:
		print "problem with np.mean"
		embed()
	# m = np.maximum.reduce(episode_matrices)
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


# folder = "../human_gamestates/Group1"
# write_interaction_files(folder, ['frogs'])
# make_heatmaps(folder, 'bait', 0)
# write_interaction_files(folder, 'all')

for i in range(1,16):
	folder = "../human_gamestates/Group{}".format(i)
# 	# write_interaction_files(folder, 'all')
	make_heatmaps(folder, 'all', 0)
	make_heatmaps(folder, 'all', 1)
	make_heatmaps(folder, 'all', 2)

#find_dimensions(folder, 'portals', 0)
# all_data = make_heatmaps(folder, 'avoidgeorge_1', 0)
embed()

