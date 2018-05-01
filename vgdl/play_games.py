from rlenvironmentnonstatic import createRLInputGameFromStrings, defInputGame
from IPython import embed
import pygame
from pygame.locals import K_RIGHT, K_LEFT, K_UP, K_DOWN, K_SPACE
from random import choice
import os
import time
import importlib
import argparse
import sys
import numpy as np
"""

Run a random agent for 10 steps per episode, for a max of 'num_episodes' episodes, on all levels of game 0:
This outputs per-frame .png images to ../vgdl_data/game_name/level_number/episode_number/
python -m vgdl.play_games --game_number 0


"""
gvggames = ['aliens', 'boulderdash', 'butterflies', 'chase', 'frogs',  				# 0-4
			'missilecommand', 'portals', 'sokoban', 'survivezombies', 'zelda']  	# 5-9

local_games = ['expt_antagonist', 'expt_exploration_exploitation', 'expt_helper',   # 10-12
	'expt_preconditions', 'expt_push_boulders', 'expt_relational']  				# 13-15 to play a "local" game

def gen_color():
	from vgdl.colors import colorDict
	color_list = colorDict.values()
	color_list = [c for c in color_list if c not in ['UUWSWF']]
	for color in color_list:
		yield color

def load_gvgai_game(gameName, path="gvgai/mturk_games/"):
	filename = path + gameName + '.txt'

	new_doc = ''
	with open(filename, 'r') as f:
		new_doc = []
		g = gen_color()
		for line in f.readlines():
			new_line = (" ".join([string if string[:4]!="img="
				else "color={}".format(next(g))
				for string in line.split(" ")]))
			new_doc.append(new_line)
		new_doc = "\n".join(new_doc)

	gameString = new_doc

	level_game_pairs = []
	for level_number in range(5):
		try:
			with open('{}_lvl{}.txt'.format(path + gameName, level_number), 'r') as level:
				level_game_pairs.append([gameString, level.read()])
		except:
			pass
	return level_game_pairs

def load_local_game(path):
	# path should be formatted like: 'examples.gridphysics.{}'
	gameFile = importlib.import_module(path)
	return gameFile.level_game_pairs

def play_trainset():
	parser = argparse.ArgumentParser(description='Process game number.')
	parser.add_argument('--game_number', type=int, default=0, help='game number')

	args = parser.parse_args()
	game_number = args.game_number

	start_time = time.time()


	# playing GVG-AI games
	if game_number < 10:
		gameName = gvggames[game_number]  # to play a gvgai game

		level_game_pairs = load_gvgai_game(gameName)

	# running local games
	else:
		gameName = 'examples.gridphysics.{}'.format(local_games[game_number-10])
		level_game_pairs = load_local_game(gameName)

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

#############################################################################
#																			#
# 					API (if you could call it that)							#
#																			#
#############################################################################
# globals
ACTIONS = [0, K_RIGHT, K_LEFT, K_UP, K_DOWN, K_SPACE]
MAX_STEPS = 10
WINS_REQUIRED = 2
level_game_pairs = []
steps = 0
rle = None
ended = True
episode_num = 0
wins = [0]
lastscore = 0

def init_game(path, isLocal=None):
	global level_game_pairs , rle , ended , steps , episode_num , wins

	if isLocal == None:
		# maybe we can still figure it out
		if 'gvgai' in path or path in gvggames:
			isLocal = False
		elif path in local_games:
			isLocal = True
			path = 'examples.gridphysics.{}'.format(path)
		else:
			print "please specify game type"
			return

	if isLocal:
		level_game_pairs = load_local_game(path)
	else:
		level_game_pairs = load_gvgai_game(path)

	steps = 0
	episode_num = 0
	wins = [0]

	rle = initializeEnvironment(level_game_pairs[0][0], level_game_pairs[0][1])
	rle._game._drawAll()

	ended = False

	# image , reward , game_has_ended
	return screenToNumpyArray(rle._game.screen) , 0 , ended

def step(action):
	# takes the step provided and returns the new state, reward, and whether the game has ended
	global steps , wins , rle , episode_num , ended

	if ended:
		print "No actions possible. Game has ended."
		return
	if not action in ACTIONS:
		print "Invalid action."
		return

	lastscore = rle._game.score
	rle.step(action)
	ended, win = rle._isDone()
	score = rle._game.score
	steps += 1
	rle._game._drawAll()

	if win:
		wins[episode_num] += 1
		if wins[episode_num] >= WINS_REQUIRED:
			# next level
			episode_num += 1
			if episode_num < len(level_game_pairs):
				rle = initializeEnvironment(level_game_pairs[episode_num][0], level_game_pairs[episode_num][1])
				wins.append(0)
				steps = 0
				ended = False

	if steps > MAX_STEPS: 
		print "MAX_STEPS threshold exceeded, ending game."
		ended = True

	# image , reward , game_has_ended
	return screenToNumpyArray(rle._game.screen) , score-lastscore , ended

def screenToNumpyArray(screen):
	arr = pygame.surfarray.array3d(screen)
	ret = np.copy(arr.transpose(1, 0, 2))
	# screen.unlock()
	return ret

# def displaySurface(surf):
# 	screen = pygame.display.set_mode(surf.get_size())
# 	background = pygame.Surface(screen.get_size())
#     background = background.convert()
#     background.fill((250, 250, 250))


'''#######   USAGE ########
>>> import vgdl.play_games
In [1]: arr, _, _ = init_game('portals')
In [2]: arr, reward, ended = step(K_DOWN)
# etc.
'''

if len(sys.argv) > 1:
	play_trainset()

embed()