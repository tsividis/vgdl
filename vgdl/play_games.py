from rlenvironmentnonstatic import createRLInputGameFromStrings, defInputGame
from IPython import embed
import pygame
from pygame.locals import K_RIGHT, K_LEFT, K_UP, K_DOWN, K_SPACE
from random import choice
import os
import time
import importlib
import argparse

"""

Run a random agent for 10 steps per episode, for a max of 'num_episodes' episodes, on all levels of game 0:
This outputs per-frame .png images to ../vgdl_data/game_name/level_number/episode_number/
python -m vgdl.play_games --game_number 0


"""
parser = argparse.ArgumentParser(description='Process game number.')
parser.add_argument('--game_number', type=int, default=0, help='game number')

args = parser.parse_args()
game_number = args.game_number

gvggames = ['aliens', 'boulderdash', 'butterflies', 'chase', 'frogs',  				# 0-4
			'missilecommand', 'portals', 'sokoban', 'survivezombies', 'zelda']  	# 5-9

local_games = ['expt_antagonist', 'expt_exploration_exploitation', 'expt_helper',   # 10-12
	'expt_preconditions', 'expt_push_boulders', 'expt_relational']  				# 13-15 to play a "local" game

def play_trainset():
	start_time = time.time()


	# playing GVG-AI games
	if game_number < 10:
		gameName = gvggames[game_number]  # to play a gvgai game
		def read_gvgai_game(filename):
			with open(filename, 'r') as f:
				new_doc = []
				g = gen_color()
				for line in f.readlines():
					new_line = (" ".join([string if string[:4]!="img="
						else "color={}".format(next(g))
						for string in line.split(" ")]))
					new_doc.append(new_line)
				new_doc = "\n".join(new_doc)
			return new_doc

		def gen_color():
			from vgdl.colors import colorDict
			color_list = colorDict.values()
			color_list = [c for c in color_list if c not in ['UUWSWF']]
			for color in color_list:
				yield color


		gvgname = "gvgai/mturk_games/{}".format(gameName)

		gameString = read_gvgai_game('{}.txt'.format(gvgname))

		level_game_pairs = []
		for level_number in range(5):
			try:
				with open('{}_lvl{}.txt'.format(gvgname, level_number), 'r') as level:
					level_game_pairs.append([gameString, level.read()])
			except:
				pass
	# running local games
	else:
		level_game_pairs = None
		gameName = 'examples.gridphysics.{}'.format(local_games[game_number-10])
		gameFile = importlib.import_module(gameName)
		level_game_pairs = gameFile.level_game_pairs

	##then pass this down for multiple episodes
	# gameObject = None
	playCurriculum(gameName, level_game_pairs=level_game_pairs)

	return

def initializeEnvironment(gameString, levelString):
	rleCreateFunc = lambda: createRLInputGameFromStrings(gameString, levelString)
	rle = rleCreateFunc()
	rle.visualize = True
	pygame.init()
	# Initialize keystate for games with orientation
	rle._game.keystate = list(pygame.key.get_pressed())
	rle.reset()
	return rle

def playEpisode(filename, level_name, gameString, levelString, episode_num):
	
	if not os.path.exists("../vgdl_data/%s/%s/%s" % (filename, level_name, episode_num)):
		os.makedirs("../vgdl_data/%s/%s/%s" % (filename, level_name, episode_num))

	steps = 0
	actions = [K_RIGHT, K_LEFT, K_UP, K_DOWN, K_SPACE]
	rle = initializeEnvironment(gameString, levelString)
	ended = False

	fn = "../vgdl_data/%s/%s/%s/tmp%05d.png" % (filename, level_name, episode_num, 0)
	pygame.image.save(rle._game.screen, fn)
	
	for i in range(1, 11):
		if not ended:
			action = choice(actions)
			rle.step(action)
			rle._game._drawAll()

			fn = "../vgdl_data/%s/%s/%s/tmp%05d.png" % (filename, level_name, episode_num, i)
			pygame.image.save(rle._game.screen, fn)

			steps += 1
			ended, win = rle._isDone()
			score = rle._game.score

	return win, score, steps

def playCurriculum(gameName, level_game_pairs, num_episodes=10):
	""" Plays a game level until it wins or exceeds num_episodes, then moves to the next one until
	completion. """

	if not level_game_pairs:
		level_game_pairs = importlib.import_module(gameName).level_game_pairs

	total_game_steps, levels_won = 0, 0
	# embed()
	for n_level, level_game in enumerate(level_game_pairs):
		episodes = []
		(gameString, levelString) = level_game
		wins = 0
		gameObject = None
		i=0
		while wins < 2 and i<num_episodes:
			win, score, steps = playEpisode(gameName, n_level, gameString, levelString, i)
			if win:
				wins += 1
			total_game_steps += steps
			episodes.append((n_level, steps, win, score))
			i+=1

		levels_won +=1
	return


play_trainset()
