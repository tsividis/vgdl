import psycopg2
import json
import sys
import csv
from collections import defaultdict
from vgdl import core


# Run with db_api.py [exp_id] [game_number] [round_number]

config = {'dbname'  : 'd9ahikn1rs4equ',
					'user'    : 'smcgqgjzpgenik',
					'host'    : 'ec2-54-235-85-65.compute-1.amazonaws.com',
					'password': 'mlKsdNWIVGgGEbO9-VwQ1S74c_'}

def get_exp(cursor, exp_id, game_number, round_number):
	cursor.execute("select * from experiments where id='%s'" % exp_id)
	rows = cursor.fetchall()
	for row in rows:
		game_data = json.loads(row[3])
		if game_data['number'] == game_number and game_data['round'] == round_number:
			return row
	
	return None

def get_game(cursor, game_name, level_number):
	cur.execute("select game, levels from games where name = '%s'" % game_name)
	rows = cur.fetchall()
	game = rows[0][0]
	level = rows[0][1][level_num]
	return game, level

def generate_csv(cursor, file_name):
	cursor.execute('select id, data, time_stamp from experiments')
	rows = cursor.fetchall()
	experiments = []
	exp_id = ''
	game = ''
	levels_won = 0
	for row in sorted(rows, key= lambda r: (r[0], json.loads(r[2])['start_time'])):
		new_exp_id = row[0]
		
		if exp_id != new_exp_id:
			exp_id = new_exp_id
			levels_won = 0

		data = json.loads(row[1])
		new_game = data['name']
		if game != new_game:
			game = new_game
			levels_won = 0
		if data['win']:
			levels_won += 1
		trial = {
			'subject': exp_id,
			'condition': 'no_score',
			'gameName': data['name'],
			'levels_won': levels_won,
			'steps': data['steps'],
			'score': data['score']
		}
		# print trial
		experiments.append(trial)
	# for experiment in experiments:

	with open(file_name, 'w') as csvfile:
	    fieldnames = ['subject', 'condition', 'gameName', 'levels_won', 'steps', 'score']
	    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
	    writer.writeheader()
	    for trial in experiments:
	    	writer.writerow(trial)


if __name__ == '__main__':
	client = psycopg2.connect("dbname='{dbname}' user='{user}' host='{host}' password='{password}'".format(**config))

	cur = client.cursor()

	# print get_exp(cur, 'By_PlXRgW', 1, 1)
	if len(sys.argv) == 4:
		exp_id = sys.argv[1]
		game_number = int(sys.argv[2])
		round_number = int(sys.argv[3])

		exp = get_exp(cur, exp_id, game_number, round_number)

		if exp:
			game_data = eval(exp[3])
			game_name = game_data['name']
			level_num = game_data['level']

			game, level = get_game(cur, game_name, level_num)

			stateSeries = json.loads(exp[4])
			core.VGDLParser.playGame(game, level, stateSeries, persist_movie=True, make_images=True, make_movie=False, movie_dir="videos/"+game_name, padding=10)
		else:
			print 'no experiment found'
	elif len(sys.argv) == 3 and sys.argv[1] == 'csv':
		generate_csv(cur, sys.argv[2])

	else:
		print '--------------------------------------------------------------'
		print 'python db_api.py [exp_id] [game_num] [round_num] \n\t to view an experiment playback'
		print
		print 'python db_api.py csv [file_name.csv] \n\t to generate a csv file from current data'
		print

	
