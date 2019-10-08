import os
from IPython import embed
import argparse
import csv
from vgdl.util import str2bool
import cPickle
import os
from shutil import copy2
import numpy as np
import random


## python -m process_EMPA_data --date oct6
## python -m process_EMPA_data --date vgdl ## for local stuff

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--date', type=str, default='apr4', help='date') ##date whose data you want to process
parser.add_argument('--game', type=str, default='', help='game') ##game whose data you want to process

## add argument options for each of the different analyses?
args = parser.parse_args()

date = args.date
game = args.game if args.game!='' else None
relative_path = '../data_files/EMPA_data_files'

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
	data_path = '{}/{}/{}'.format(relative_path, date, 'csv_data')
 	if 'csv_data' not in os.listdir('{}/{}'.format(relative_path, date)):
	# data_path = '{}/{}'.format(date, 'csv_data')
	# if 'csv_data' not in os.listdir('{}'.format(date)):
		os.makedirs(data_path)

	if 'merged_data' not in os.listdir(data_path):
		g = open('{}/merged_data'.format(data_path), 'w+')
		mergedfilewriter = csv.writer(g)
		mergedfilewriter.writerow(('agent_type', 'subject_ID', 'modelrun_ID', 'condition', 'exploration_burn_ins', 'game_name', 'level_number', 
								'timestep', 'cumulative_timestep', 'time_elapsed', 'entropy', 'score', 'level_max_score', 'cumulative_max_score', 
							'sparse_score', 'level_accumulated_score', 'episode_end', 'win', 'cumulative_wins', 'sparse_levels_won', 'planner_settings', 'planner_nodes', 'cumulative_planner_nodes'))
	else:
		g = open('{}/merged_data'.format(data_path), 'a+')	
		mergedfilewriter = csv.writer(g)

	game_name = data['gameInfo']['gameName']

	if game_name not in os.listdir(data_path):
		f = open('{}/{}'.format(data_path, game_name), 'w+') #newfile and write
		gamefilewriter = csv.writer(f)
		gamefilewriter.writerow(('agent_type', 'subject_ID', 'modelrun_ID', 'condition', 'exploration_burn_ins', 'game_name', 'level_number', 
								'timestep', 'cumulative_timestep', 'time_elapsed', 'entropy', 'score', 'level_max_score', 'cumulative_max_score', 
								'sparse_score','level_accumulated_score', 'episode_end', 'win', 'cumulative_wins', 'sparse_levels_won', 'planner_settings', 'planner_nodes', 'cumulative_planner_nodes'))
	else:
		f = open('{}/{}'.format(data_path, game_name), 'a+') #append and read
		gamefilewriter = csv.writer(f)
	
	agent_type = data['modelParams']
	subject_ID = generate_subject_ID()
	exploration_burn_ins = data['exploration_burn_ins'] if 'exploration_burn_ins' in data.keys() else 'NA'
	# if 'exploration_burn_ins' in data.keys():
	# 	agent_type = 'lesion'
	# else:
	# 	agent_type = 'normal'
	# print "you've modified agent_type to test a single thing, but you need to remove this modification"
	condition = data['condition'] if 'condition' in data.keys() else 'full'
	game_name = data['gameInfo']['gameName']
	cumulative_timestep, cumulative_max_score, sparse_score, cumulative_wins, cumulative_planner_nodes = 0,0,0,0,0
	prev_level_number = 0
	accumulated_score = 0 ## at end of each level, you keep whatever score you've picked up.
	for level_number,level in enumerate(data['episodes']):
		level_max_score = 0
		for episode in level:
			for t, state in enumerate(episode):
				timestep, entropy, score, planner_nodes, episode_end, win, planner_settings = state['timestep'], state['entropy'], state['score'], state['planner_nodes'], state['ended'], state['win'], state['planner_settings']
				time_elapsed = float("{0:6.3f}".format(state['time_elapsed'])) if 'time_elapsed' in state else 'NA'
				entropy = round(entropy,4) if entropy is not None else 'NA'
				score=round(score,2)
				
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
					sparse_levels_won = cumulative_wins
				else:
					## first level, first round: sparse_levels_won has to be 0
					if level_number==0 and t==0:
						sparse_levels_won = 0
					else:
						sparse_levels_won = 'NA'
				cumulative_timestep += 1

				mean_burn_in = np.mean(exploration_burn_ins) if type(exploration_burn_ins)==list else 'NA'

				row = (agent_type, subject_ID, modelrun_ID, condition, mean_burn_in, game_name, level_number, t, cumulative_timestep, time_elapsed, entropy, score, level_max_score, cumulative_max_score,
						sparse_score, level_accumulated_score, episode_end, win, cumulative_wins, sparse_levels_won, planner_settings, planner_nodes, cumulative_planner_nodes)
				gamefilewriter.writerow(row)
				mergedfilewriter.writerow(row)

				prev_level_number = level_number

	f.close()
	g.close()

def make_csvs(path, game=None):
	for folder in open_folder(path):
		for gamefolder in open_folder("{}/{}".format(path,folder)):
			if game==None or game==gamefolder:
				print gamefolder
				for modelrun_ID in open_folder("{}/{}/{}".format(path, folder, gamefolder)):
					print modelrun_ID
					modelrun_path = "{}/{}/{}/{}".format(path, folder, gamefolder, modelrun_ID)
					with open(modelrun_path, 'r') as o:
						try:
							data = cPickle.load(o)
							process_model_run(data, modelrun_ID)
						except:
							print "error with {}, {}, {}...".format(path, folder, modelrun_ID)
							# embed()
						o.close()
					# embed()

def generate_subject_ID(length=7):
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

merge_results(date)
make_csvs(path)
