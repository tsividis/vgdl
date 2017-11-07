import psycopg2
import json
import sys
import csv
from collections import defaultdict
from vgdl import core
from IPython import embed

# Run with db_api.py [exp_id] [game_number] [round_number]

config = {'dbname'  : 'd9ahikn1rs4equ',
					'user'    : 'smcgqgjzpgenik',
					'host'    : 'ec2-54-235-85-65.compute-1.amazonaws.com',
					'password': 'mlKsdNWIVGgGEbO9-VwQ1S74c_'}

def print_logs(cursor):
	cursor.execute('select * from logs')
	for row in cursor.fetchall():
		print row

def get_exp(cursor, exp_id, game_number, level_number, round_number):
	cursor.execute("select * from experiments where id='%s'" % exp_id)
	rows = cursor.fetchall()
	print 'finding game...'
	for row in rows:
		game_data = json.loads(row[3])
		if int(game_data['level']) == level_number and int(game_data['number']) == game_number and int(game_data['round']) == round_number:
			print 'game found\n'
			return row
	
	return None

def get_game(cursor, game_name, desc_number, level_number):
	cur.execute("select descs, levels from multigames where name = '%s'" % game_name)
	rows = cur.fetchall()
	game = rows[0][0][desc_num]
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
		if data['win'] == 'true':
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
	if len(sys.argv) >= 5:
		raw = False
		if (len(sys.argv) == 6):
			if sys.argv[5] == 'raw':
				raw = True
				print 'raw'
		exp_id = sys.argv[1]
		game_number = int(sys.argv[2])
		level_number = int(sys.argv[3])
		round_number = int(sys.argv[4])

			

		exp = get_exp(cur, exp_id, game_number, level_number, round_number)

		if exp:
			print 'loading game...'
			game_data = json.loads(exp[3])

			game_name = game_data['name']
			level_num = int(game_data['level'])
			desc_num = int(game_data['desc'])

			game, level = get_game(cur, game_name, desc_num, level_num)


			stateSeries = json.loads(exp[4])
			print 'running game\n'
			if raw:
				print stateSeries
			else:
				core.VGDLParser.playGame(game, level, stateSeries, persist_movie=True, make_images=True, make_movie=False, movie_dir="videos/"+game_name, padding=10)
		else:
			print 'no experiment found'
	elif len(sys.argv) == 3 and sys.argv[1] == 'csv':
		generate_csv(cur, sys.argv[2])
	elif len(sys.argv) == 2 and sys.argv[1] == 'logs':
		print_logs(cur)
	else:
		print '--------------------------------------------------------------'
		print 'python db_api.py [exp_id] [game_num] [level_num] [round_num] \n\t to view an experiment playback'
		print
		print 'python db_api.py csv [file_name.csv] \n\t to generate a csv file from current data'
		print

	
