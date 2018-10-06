import os
from IPython import embed
import argparse
import csv
from vgdl.util import str2bool
import cPickle

## python -m vgdl --date oct6
## python -m vgdl --date vgdl ## for local stuff

parser = argparse.ArgumentParser(description='.')
parser.add_argument('--date', type=str, default='oct6', help='date') ##date whose data you want to process
## add argument options for each of the different analyses?
args = parser.parse_args()

date = args.date
relative_path = '..'
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

	data_path = '{}/{}/{}'.format(relative_path, date, 'csv_data')
	if 'csv_data' not in os.listdir('{}/{}'.format(relative_path, date)):
		os.makedirs(data_path)

	if 'merged_data' not in os.listdir(data_path):
		g = open('{}/merged_data'.format(data_path), 'w+')
		mergedfilewriter = csv.writer(g)
		mergedfilewriter.writerow(('agent_type', 'subject_ID', 'modelrun_ID', 'condition', 'game_name', 'level_number', 'timestep', 'cumulative_timestep', 'score', 'level_max_score', 'cumulative_max_score', 
							'episode_end', 'win', 'cumulative_wins', 'planner_settings', 'planner_nodes', 'cumulative_planner_nodes'))
	else:
		g = open('{}/merged_data'.format(data_path), 'a+')	
		mergedfilewriter = csv.writer(g)

	game_name = data['gameInfo']['gameName']

	if game_name not in os.listdir(data_path):
		f = open('{}/{}'.format(data_path, game_name), 'w+') #newfile and write
		gamefilewriter = csv.writer(f)
		gamefilewriter.writerow(('agent_type', 'subject_ID', 'modelrun_ID', 'condition', 'game_name', 'level_number', 'timestep', 'cumulative_timestep', 'score', 'level_max_score', 'cumulative_max_score', 
							'episode_end', 'win', 'cumulative_wins', 'planner_settings', 'planner_nodes', 'cumulative_planner_nodes'))
	else:
		f = open('{}/{}'.format(data_path, game_name), 'a+') #append and read
		gamefilewriter = csv.writer(f)
	
	agent_type = data['modelParams']
	condition = data['condition'] if 'condition' in data.keys() else 'full'
	game_name = data['gameInfo']['gameName']
	cumulative_timestep, cumulative_max_score, cumulative_wins, cumulative_planner_nodes = 0,0,0,0
	prev_level_number = 0
	for level_number,level in enumerate(data['episodes']):
		level_max_score = 0
		for episode in level:
			for t, state in enumerate(episode):
				timestep, score, planner_nodes, episode_end, win, planner_settings = state['timestep'], state['score'], state['planner_nodes'], state['ended'], state['win'], state['planner_settings']
				
				## All this weird stuff needs to be done because we don't have a single-stream game.
				if level_number > prev_level_number:
					level_max_score = 0
					cumulative_max_score = cumulative_max_score + score
				else:
					if score > level_max_score:
						score_delta = score - level_max_score
						level_max_score = max(score, level_max_score)
						cumulative_max_score += score_delta

				cumulative_planner_nodes += planner_nodes
				cumulative_wins += win
				## for a particular model, the subject_ID is just the agent_type, i.e., its parameters.
				row = (agent_type, agent_type, modelrun_ID, condition, game_name, level_number, t, cumulative_timestep, score, level_max_score, cumulative_max_score,
						episode_end, win, cumulative_wins, planner_settings, planner_nodes, cumulative_planner_nodes)
				cumulative_timestep += 1

				prev_level_number = level_number
				gamefilewriter.writerow(row)
				mergedfilewriter.writerow(row)
	f.close()
	g.close()

def make_csvs(path):
	for folder in open_folder(path):
		for gamefolder in open_folder("{}/{}".format(path,folder)):
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

make_csvs(path)





