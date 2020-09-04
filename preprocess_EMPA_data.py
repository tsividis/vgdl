import os
from IPython import embed
import argparse
import csv
from vgdl.util import str2bool
import cPickle
import os
from shutil import copy2
from collections import defaultdict
import numpy as np
import random

"""
Preprocesses raw EMPA data into csv files where score/time data can be analyzed in R, or make heatmaps

Demo usage:
python -m process_EMPA_data --date local

Normal usage:
python -m process_EMPA_data --date apr4 ## preprocess
python -m process_EMPA_data --date apr4 --heatmap True ## heatmap. call this on a date for which state data were stored

"""

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--date', type=str, default='apr4', help='date') ##date whose data you want to process
parser.add_argument('--game', type=str, default='', help='game') ##game whose data you want to process
parser.add_argument('--heatmap',type=str2bool, default=False)

args = parser.parse_args()

date = args.date
game = args.game if args.game!='' else None
heatmap = args.heatmap

# relative_path = '../data/demo_data_files/EMPA'
relative_path = 'data_files/EMPA'

path = '{}/{}/results'.format(relative_path, date)

def open_folder(path):
	return [f for f in os.listdir(path) if 'DS_Store' not in f]

def process_model_run(data, modelrun_ID):
	## takes a cPickle file of a full model run
	## writes a csv

	## you need to count max_score differently, as you want to show the max points someone has gotten, but you don't want to give people
	## points for continually almost winning a level. 
	## you want to end up with one csv per game. if you want to look at things across games, you just have to merge those csvs, but this is the cleanest way to do it
	## and to avoid loading huge csv files.
	## also don't process a particular run multiple times. you need a way of storing the processed model_IDs so that you don't keep appending to a long csv.
	modelrun_ID = modelrun_ID[modelrun_ID.find('201'):modelrun_ID.find('201')+11]
	subject_ID = generate_subject_ID()

	data_path = '{}/{}/{}'.format(relative_path, date, 'csv_data')
	if 'csv_data' not in os.listdir('{}/{}'.format(relative_path, date)):
	# data_path = '{}/{}'.format(date, 'csv_data')
	# if 'csv_data' not in os.listdir('{}'.format(date)):
		os.makedirs(data_path)

	if 'merged_data' not in os.listdir(data_path):
		g = open('{}/merged_data'.format(data_path), 'w+')
		mergedfilewriter = csv.writer(g)
		mergedfilewriter.writerow(('agent_type', 'subject_ID', 'modelrun_ID', 'condition', 'exploration_burn_ins', 'game_name', 'level_number', 'timestep', 'cumulative_timestep', 
							'entropy', 'score', 'level_max_score', 'cumulative_max_score', 
							'sparse_score', 'level_accumulated_score', 'episode_end', 'win', 'cumulative_wins', 'planner_settings', 'planner_nodes', 'cumulative_planner_nodes'))
	else:
		g = open('{}/merged_data'.format(data_path), 'a+')	
		mergedfilewriter = csv.writer(g)

	if 'interaction_data' not in os.listdir(data_path):
		h = open('{}/interaction_data'.format(data_path), 'w+')
		interactionfilewriter = csv.writer(h)
		interactionfilewriter.writerow(('agent_type', 'subject_ID', 'modelrun_ID', 'game_name', 'level_number', 'episode_number', 'event_type', 'count'))
	else:
		h = open('{}/interaction_data'.format(data_path), 'a+')	
		interactionfilewriter = csv.writer(h)

	game_name = data['gameInfo']['gameName']

	if game_name not in os.listdir(data_path):
		f = open('{}/{}'.format(data_path, game_name), 'w+') #newfile and write
		gamefilewriter = csv.writer(f)
		gamefilewriter.writerow(('agent_type', 'subject_ID', 'modelrun_ID', 'condition', 'exploration_burn_ins', 'game_name', 'level_number', 'timestep', 'cumulative_timestep', 
							'entropy', 'score', 'level_max_score', 'cumulative_max_score', 
							'sparse_score','level_accumulated_score', 'episode_end', 'win', 'cumulative_wins', 'planner_settings', 'planner_nodes', 'cumulative_planner_nodes'))
	else:
		f = open('{}/{}'.format(data_path, game_name), 'a+') #append and read
		gamefilewriter = csv.writer(f)
	
	agent_type = data['modelParams']
	exploration_burn_ins = data['exploration_burn_ins'] if 'exploration_burn_ins' in data.keys() else 'NA'
	# if 'exploration_burn_ins' in data.keys():
	# 	agent_type = 'lesion'
	# else:
	# 	agent_type = 'normal'
	# print "you've modified agent_type to test a single thing, but you need to remove this modification"
	# embed()
	condition = data['condition'] if 'condition' in data.keys() else 'full'
	game_name = data['gameInfo']['gameName']

	all_event_types = set()
	cumulative_timestep, cumulative_max_score, sparse_score, cumulative_wins, cumulative_planner_nodes = 0,0,0,0,0
	prev_level_number = 0
	accumulated_score = 0 ## at end of each level, you keep whatever score you've picked up.
	episode_number = 0

	for level_number,level in enumerate(data['episodes']):
		unpacked_states = [item for sublist in level for item in sublist]
		level_max_score = 0
		for episode_num, episode in enumerate(level):
			episode_events = defaultdict(lambda:0)
			for t, state in enumerate(episode):
				timestep, score, planner_nodes, episode_end, win, planner_settings, events = state['timestep'], state['score'], state['planner_nodes'], state['ended'], state['win'], state['planner_settings'], state['events']
				entropy = 0
				# if events:
					# embed()
				timestep_events = set()

				for e in events:
					## because event handling is so weird in Frogs, we need to filter out these events.
					## Avatar-water and avatar-log collisions will still be reported from the (killSprite avatar water) interaction and (pullWithIt avatar log) interaction
					## which is what a player perceives when they play
					if e in  [('changeResource', 'avatar', 'water'),('changeResource', 'avatar', 'log')]:
						pass
					else:
						timestep_events.add(tuple(sorted((e[1], e[2]))))
						all_event_types.add(tuple(sorted((e[1], e[2]))))

				for e in timestep_events:
					episode_events[e] += 1
				# for e in events:
					# episode_events[tuple(sorted((e[1], e[2])))] += .5
					# all_event_types.add(tuple(sorted((e[1], e[2]))))
				entropy = round(entropy,4) if entropy is not None else 'NA'
				score = round(score,2)
				## All this weird stuff needs to be done because we don't have a single-stream game.
				if level_number > prev_level_number:
					level_max_score = 0
					cumulative_max_score = cumulative_max_score + score
					sparse_score = cumulative_max_score
					level_accumulated_score = accumulated_score
				else:
					if cumulative_timestep%5==0 or t==len(episode)-1:
						level_accumulated_score = accumulated_score + score
					else:
						level_accumulated_score = 'NA'
					# level_accumulated_score = accumulated_score + score
					if score > level_max_score:
						score_delta = score - level_max_score
						level_max_score = max(score, level_max_score)
						cumulative_max_score += score_delta
						if score_delta > 0:
							sparse_score = cumulative_max_score
						else:
							if cumulative_timestep%5 == 0:
								sparse_score = cumulative_max_score
							else:
								sparse_score = 'NA'
					else:
						if t>0:
							if cumulative_timestep%5 == 0:
								sparse_score = cumulative_max_score
							else:
								sparse_score = 'NA'

				cumulative_planner_nodes += planner_nodes
				if type(win)==tuple:
					win = win[0]
				cumulative_wins += win
				if win:
					accumulated_score = accumulated_score + score
					level_accumulated_score = accumulated_score
				cumulative_timestep += 1

				mean_burn_in = np.mean(exploration_burn_ins) if type(exploration_burn_ins)==list else 'NA'
				row = (agent_type, subject_ID, modelrun_ID, condition, mean_burn_in, game_name, level_number, t, cumulative_timestep, entropy, score, level_max_score, cumulative_max_score,
						sparse_score, level_accumulated_score, episode_end, win, cumulative_wins, planner_settings, planner_nodes, cumulative_planner_nodes)
				# gamefilewriter.writerow(row)
				mergedfilewriter.writerow(row)

				prev_level_number = level_number
			for event_name in all_event_types:
				if event_name not in episode_events:
					episode_events[event_name] = 0
			for event_name, count in episode_events.items():
				interactionfilewriter.writerow((agent_type, subject_ID, modelrun_ID, game_name, level_number, episode_number, event_name, count))

			episode_number += 1

		# if 'ee_3' in game_name:
		# 	try:
		# 		makeHeatmap(unpacked_states, agent_type, 'heatmap_{}_level_{}_{}.pdf'.format(game_name, level_number, agent_type))
		# 	except:
		# 		print "error with heatmaps"
		# 		embed()

	f.close()
	g.close()
	h.close()

def make_csvs(path, heatmap, game_names = [], game=None):
	for folder in open_folder(path):
		for gamefolder in open_folder("{}/{}".format(path,folder)):
			if game==None or game==gamefolder:
				print gamefolder
				for modelrun_ID in open_folder("{}/{}/{}".format(path, folder, gamefolder)):
					print modelrun_ID
					modelrun_path = "{}/{}/{}/{}".format(path, folder, gamefolder, modelrun_ID)
					# embed()
					with open(modelrun_path, 'r') as o:
						try:
							data = cPickle.load(o)
						except:
							print "problem loading pickle for {}".format(modelrun_path)
						if heatmap:
							make_heatmaps(data, modelrun_ID, game_names)
						else:
							try:
								process_model_run(data, modelrun_ID)
							except:
								print "error..."
								embed()
						o.close()

def generate_subject_ID(length=7):
	## Generate random subject IDs so that you can refer to them in R analyses
	alphabet = "QWERTYUIOPASDFGHJKLZXCVBNM1234567890"
	string = ''
	for i in range(length):
		string += random.choice(alphabet)
	return string

def merge_results(date):
	## converts structure from
	## param_specification/game_name/game_pickle_file
	## to
	## param_specification/all_games/pickle_files
	# embed()
	if 'all' not in os.listdir('{}/{}/results'.format(relative_path, date)):
		os.makedirs('{}/{}/results/all'.format(relative_path, date))
		os.makedirs('{}/{}/results/all/all'.format(relative_path, date))

	target = '{}/{}/results/all/all'.format(relative_path, date)
	for mod in os.listdir('{}/{}/results'.format(relative_path, date)):
		if 'DS_Store' not in mod and 'all' not in mod:
			for d in os.listdir('{}/{}/results/{}/'.format(relative_path, date, mod)):
				if 'DS_Store' not in d and 'all' not in d:
					for r in os.listdir('{}/{}/results/{}/'.format(relative_path, date, mod)+d):
						if 'DS_Store' not in r:
							copy2('{}/{}/results/{}/'.format(relative_path, date, mod)+d+'/'+r,target)

def make_heatmaps(data, modelrun_ID, game_names):
	## takes a cPickle file of a full model run
	## makes heatmaps for specified games
	modelrun_ID = modelrun_ID[modelrun_ID.find('201'):modelrun_ID.find('201')+11]
	subject_ID = generate_subject_ID()
	
	agent_type = data['modelParams']
	exploration_burn_ins = data['exploration_burn_ins'] if 'exploration_burn_ins' in data.keys() else 'NA'

	condition = data['condition'] if 'condition' in data.keys() else 'full'
	game_name = data['gameInfo']['gameName']

	if game_name in game_names or game_names=='all':
		for level_number,level in enumerate(data['episodes']):
			unpacked_states = [item for sublist in level for item in sublist]
			try:
				makeHeatmap(unpacked_states, agent_type, '{}_level_{}_{}.pdf'.format(game_name, level_number, agent_type))
			except:
				print "error with heatmaps"
				embed()

def makeHeatmap(statesEncountered, agent_type, filename):
	from vgdl.plotting import featurePlot
	import matplotlib.pyplot as plt
	from matplotlib.ticker import NullLocator
	import numpy as np

	if agent_type not in os.listdir('heatmaps'):
		os.makedirs('heatmaps/{}'.format(agent_type))

	avatar_color = 'DARKBLUE'
	if 'relational' in filename:
		avatar_color = 'WHITE'
	states = []
	for s in statesEncountered:
		avatar_list = [(o[1][0], o[1][1], s['timestep']) for o in s['objects'] if o[0]==avatar_color]
		if avatar_list:
			states.append(avatar_list[0])

	positions = [o[1] for o in statesEncountered[0]['objects']]
	width, height = max([p[0] for p in positions]), max([p[1] for p in positions])
	## check all avatar positions; maybe it moves somewhere outside the bounds of the original positions of objects on the screen
	## this happens in games like aliens
	width, height = max(width, max([s[0] for s in states])), max(height,max([s[1] for s in states]))

	m = np.zeros((width+1, height+1))
	Xs, Ys = [],[]
	block_size = 30
	prev_state = (None, None)
	set_first_frame = False

	for s in states:
		frame = s[2]
		x = int(round(s[0]))
		y = int(round(s[1]))
		if (x,y) != prev_state and (frame!=0 or not set_first_frame):
			m[x, y] += 1

		prev_state = (x,y)
		if frame == 0:
			set_first_frame = True

		# Xs.append(x*block_size+block_size/2.)
		# Ys.append(y*block_size+block_size/2.)
	# plt.scatter(x=Xs, y=Ys, alpha=.5, edgecolor='')
	plt.imshow(m.T, cmap='viridis')
	plt.gca().set_axis_off()
	plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0,
		hspace = 0, wspace = 0)
	plt.margins(0, 0)
	plt.gca().xaxis.set_major_locator(NullLocator())
	plt.gca().yaxis.set_major_locator(NullLocator())
	tmpfilename = filename[:filename.find('.pdf')]+'_max='+str(int(np.max(m)))
	filename = tmpfilename + '.pdf'
	# filename = filename+'_max='+str(int(np.max(m)))
	print filename
	plt.savefig('heatmaps/{}/{}'.format(agent_type, filename), bbox_inches='tight', pad_inches=0)
	plt.close()


if not heatmap:
	## To preprocess data
	merge_results(date)
	make_csvs(path, heatmap)
else:
	## To make all heatmaps (note -- this needs to be called with a date flag for which human data were stored)
	game_names = 'all'
	make_csvs(path, heatmap, game_names)
