import psycopg2
import json
import sys
from vgdl import core


# Run with db_api.py [exp_id] [game_number] [round_number]

config = {'dbname'  : 'd9ahikn1rs4equ',
					'user'    : 'smcgqgjzpgenik',
					'host'    : 'ec2-54-235-85-65.compute-1.amazonaws.com',
					'password': 'mlKsdNWIVGgGEbO9-VwQ1S74c_'}

def get_exp(cursor, exp_id, game_number, round_number):
	cursor.execute("select * from experiments where id='%s'" % exp_id)
	rows = cursor.fetchall();
	for row in rows:
		game_data = eval(row[2])
		if game_data[2] == game_number and game_data[3] == round_number:
			return row
	
	return None

def get_game(cursor, game_name, level_number):
	cur.execute("select game, levels from games where name = '%s'" % game_name)
	rows = cur.fetchall()
	game = rows[0][0]
	level = rows[0][1][level_num]
	return game, level

if __name__ == '__main__':
	client = psycopg2.connect("dbname='{dbname}' user='{user}' host='{host}' password='{password}'".format(**config))

	cur = client.cursor()

	# print get_exp(cur, 'By_PlXRgW', 1, 1)
	assert(len(sys.argv) == 4)
	exp_id = sys.argv[1]
	game_number = int(sys.argv[2])
	round_number = int(sys.argv[3])

	exp = get_exp(cur, exp_id, game_number, round_number)

	if exp:
		game_data = eval(exp[2])
		game_name = game_data[0]
		level_num = game_data[1]

		game, level = get_game(cur, game_name, level_num)

		stateSeries = json.loads(exp[3])

		core.VGDLParser.playGame(game, level, stateSeries, persist_movie=True, make_images=True, make_movie=False, movie_dir="videos/"+game_name, padding=10)
	else:
		print 'no experiment found'
	
