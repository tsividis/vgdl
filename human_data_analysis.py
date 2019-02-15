import json
from IPython import embed
from collections import defaultdict
import os, csv

folder = "../GameStates/Group1"
data_path = "../"
modelrun_ID = 'NA'
agent_type = 'human'

### TODO:

### The current script only does group 1!!!

def write_interaction_file(single_subject_single_game, subject_ID):
	if 'human_interaction_data' not in os.listdir(data_path):
		h = open('{}/human_interaction_data'.format(data_path), 'w+')
		interactionfilewriter = csv.writer(h)
		interactionfilewriter.writerow(('agent_type', 'subject_ID', 'modelrun_ID', 'game_name', 'level_number', 'episode_number', 'event_type', 'count'))
	else:
		h = open('{}/human_interaction_data'.format(data_path), 'a+')	
		interactionfilewriter = csv.writer(h)


## .5
## sorted in keys

	game_dict = defaultdict(lambda: list())
	for i, episode in enumerate(single_subject_single_game):
		if len(episode.keys())>1:
			print "found more than one key in an episode. You were probably wrong about what the keys correspond to"
			embed()

		game_name, game_level, game_number, game_round = game_string_to_info(episode.keys()[0])

		if game_name in ['closing_gates_1', 'plaqueattack_1']:
			continue

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
		for j,frm in enumerate(frms):
			for object_type, object_instances in frm['objects'].items():
				for object_ID, object_details in object_instances.items():
					if str(object_ID) not in IDs_to_object_names:
						IDs_to_object_names[str(object_ID)] = str(object_type)


			step, events, score, win = frm['frame'], frm['events'], frm['score'], frm['win']
			# cumulative_steps += step
			timestep_events = set()
			for e in events:
				try:
					translated_event = tuple(sorted((IDs_to_object_names[str(e[1])], IDs_to_object_names[str(e[2])])))
					# print translated_event
					timestep_events.add(translated_event)
					# translated_event = tuple((IDs_to_object_names[str(e[1])], IDs_to_object_names[str(e[2])]))

				except:
					print "Key error", game_name, e
					pass

				# event_dict[translated_event] += 1
				# all_event_types.add(translated_event)

			for translated_event in timestep_events:
				event_dict[translated_event] += 1
		for event_name, count in event_dict.items():
			row = (agent_type, subject_ID, modelrun_ID, game_name, game_level, episode_number, event_name, count)
			# print episode.keys()[0]
			# print row
			interactionfilewriter.writerow(row)
		
		try:
			episode_number += 1
		except:
			print "episode-number problem with", game_name, game_level, game_round, "subject_ID", subject_ID, "single_subject_single_game counter:", i
			episode_number = 1 ##

	h.close()



	# previous_game = None
	# for i,episode in enumerate(single_subject_single_game):

	# 	game_name, game_level, game_number, game_round = game_string_to_info(episode.keys()[0])
	# 	if game_name in ['closing_gates_1', 'plaqueattack_1']:
	# 		continue
	# 	if game_level=='0' and game_round=='1' or previous_game!=game_name:
	# 		episode_number = 0
	# 		# all_event_types = set()
	# 	previous_game = game_name
	# 	for k, v in episode.items():
	# 		frms = sorted(v, key=lambda x: x['frame'])
	# 		objects = frms[0]['objects']
	# 		IDs_to_object_names = dict()
	# 		IDs_to_object_names['-1'] = 'EOS'
	# 		for object_type, object_instances in objects.items():
	# 			for object_ID, object_details in object_instances.items():
	# 				IDs_to_object_names[str(object_ID)] = str(object_type)
			
			
	# 		event_dict = defaultdict(lambda:0)
	# 		for j,frm in enumerate(frms):
	# 			for object_type, object_instances in frm['objects'].items():
	# 				for object_ID, object_details in object_instances.items():
	# 					if str(object_ID) not in IDs_to_object_names:
	# 						IDs_to_object_names[str(object_ID)] = str(object_type)


	# 			step, events, score, win = frm['frame'], frm['events'], frm['score'], frm['win']
	# 			# cumulative_steps += step
	# 			timestep_events = set()
	# 			for e in events:
	# 				try:
	# 					translated_event = tuple(sorted((IDs_to_object_names[str(e[1])], IDs_to_object_names[str(e[2])])))
	# 					# print translated_event
	# 					timestep_events.add(translated_event)
	# 					# translated_event = tuple((IDs_to_object_names[str(e[1])], IDs_to_object_names[str(e[2])]))

	# 				except:
	# 					print "Key error", game_name, e
	# 					pass

	# 				# event_dict[translated_event] += 1
	# 				# all_event_types.add(translated_event)

	# 			for translated_event in timestep_events:
	# 				event_dict[translated_event] += 1
	# 		for event_name, count in event_dict.items():
	# 			row = (agent_type, subject_ID, modelrun_ID, game_name, game_level, episode_number, event_name, count)
	# 			print episode.keys()[0]
	# 			print row
			
	# 		try:
	# 			episode_number += 1
	# 		except:
	# 			print "episode-number problem with", game_name, game_level, game_round, "subject_ID", subject_ID, "single_subject_single_game counter:", i
	# 			episode_number = 1 ##

				# interactionfilewriter.writerow(row)


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

for filename in os.listdir(folder):
# filename = 'Raw_Nov12th_B1c1RTP67'
	path = folder + "/" + filename
	data_path = '.'

	json_file = open(path, 'rb')
	single_subject_single_game = json.load(json_file)  ## WRONG. This is not single subject, single game. There are two games here.
	subject_ID = filename
	write_interaction_file(single_subject_single_game, subject_ID)


	##all you want is to count the events per episode. what the fuck else were you doing???