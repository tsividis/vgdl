import os
from IPython import embed
import argparse
import csv
from vgdl.util import str2bool
import cPickle
import os
from shutil import copy2
import numpy as np
from collections import defaultdict
import random


## python -m vgdl --date oct6
## python -m vgdl --date vgdl ## for local stuff

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--date', type=str, default='oct6', help='date') ##date whose data you want to process
parser.add_argument('--game', type=str, default='', help='game') ##game whose data you want to process

## add argument options for each of the different analyses?
args = parser.parse_args()

date = args.date
game = args.game if args.game!='' else None
relative_path = '..'
path = '{}/{}/results'.format(relative_path, date)
# path = '{}/results'.format(date)

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
		interactionfilewriter.writerow(('agent_type', 'subject_ID', 'modelrun_ID', 'game_name', 'level_number', 'event_type', 'count'))
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

	# if game_name=='entropy':
		# print "embedded in process_model_run"
		# embed()

	cumulative_timestep, cumulative_max_score, sparse_score, cumulative_wins, cumulative_planner_nodes = 0,0,0,0,0
	prev_level_number = 0
	accumulated_score = 0 ## at end of each level, you keep whatever score you've picked up.
	episode_number = 0
	for level_number,level in enumerate(data['episodes']):
		episode_events = defaultdict(lambda:0)
		level_max_score = 0
		for episode_num, episode in enumerate(level):
			for t, state in enumerate(episode):
				timestep, entropy, score, planner_nodes, episode_end, win, planner_settings, events = state['timestep'], state['entropy'], state['score'], state['planner_nodes'], state['ended'], state['win'], state['planner_settings'], state['events']
				# if events:
					# embed()
				for e in events:
					episode_events[tuple(sorted((e[1], e[2])))] += .5
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
			for event_name, count in episode_events.items():
				interactionfilewriter.writerow((agent_type, subject_ID, modelrun_ID, game_name, episode_number, event_name, count))
			episode_number += 1
	f.close()
	g.close()
	h.close()

def generate_subject_ID(length=7):
	alphabet = "QWERTYUIOPASDFGHJKLZXCVBNM1234567890"
	string = ''
	for i in range(length):
		string += random.choice(alphabet)
	return string

def make_csvs(path, game=None):
	for folder in open_folder(path):
		for gamefolder in open_folder("{}/{}".format(path,folder)):
			if game==None or game==gamefolder:
				print gamefolder
				for modelrun_ID in open_folder("{}/{}/{}".format(path, folder, gamefolder)):
					print modelrun_ID
					modelrun_path = "{}/{}/{}/{}".format(path, folder, gamefolder, modelrun_ID)
					with open(modelrun_path, 'r') as o:
						data = cPickle.load(o)
						try:
							process_model_run(data, modelrun_ID)
						except:
							print "error..."
							embed()
						o.close()
					# embed()

def merge_results(date):
	## converts structure from
	## param_specification/game_name/game_pickle_file
	## to
	## param_specification/all_games/pickle_files
	if 'all' not in os.listdir('../{}/results'.format(date)):
		os.makedirs('../{}/results/all'.format(date))
		os.makedirs('../{}/results/all/all'.format(date))

	target = '../{}/results/all/all'.format(date)
	for mod in os.listdir('../{}/results'.format(date)):
		if 'DS_Store' not in mod and 'all' not in mod:
			for d in os.listdir('../{}/results/{}/'.format(date, mod)):
				if 'DS_Store' not in d and 'all' not in d:
					for r in os.listdir('../{}/results/{}/'.format(date, mod)+d):
						if 'DS_Store' not in r:
							copy2('../{}/results/{}/'.format(date, mod)+d+'/'+r,target)

## take things out one level; should be in results/all, rather than results/all/all
# merge_results(date)
make_csvs(path)
