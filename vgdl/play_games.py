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
from colors import LIGHTGRAY

import pdb

"""

Run a random agent for 10 steps per episode, for a max of 'num_episodes' episodes, on all levels of game 0:
This outputs per-frame .png images to ../vgdl_data/game_name/level_number/episode_number/
python -m vgdl.play_games --game_number 0

"""

'''#######   USAGE ########
>>> import vgdl.play_games
In [1]: im, _, _ = init_game('portals')
In [2]: im, reward, ended = step(K_DOWN)
# etc.
# ...
# game ends for one reason or another: final frame (victory or death) returned
# 	to proceed to the next frame (beginning of next level or retry of current level as approprate)
In [23]: im, reward, ended = step('next_episode')
# <continue entering step commands as before>
# ...
# when you want to export the results from this game (results cleared every time you call init_game)
In [82]: writeResults('path/to/wherever/filename.csv') # will overwrite whatever's there
'''

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

def initializeEnvironment(gameString, levelString, headless=True):
	rleCreateFunc = lambda: createRLInputGameFromStrings(gameString, levelString)
	rle = rleCreateFunc()
	rle.visualize = not headless
	if headless:
		os.environ["SDL_VIDEODRIVER"] = "dummy"
	pygame.init()

	# Initialize keystate for games with orientation
	# rle._game.keystate = list(pygame.key.get_pressed())
	# rle.reset()
	return rle

def playEpisode(filename, level_name, gameString, levelString, episode_num):
	
	if not os.path.exists("../vgdl_data/%s/%s/%s" % (filename, level_name, episode_num)):
		os.makedirs("../vgdl_data/%s/%s/%s" % (filename, level_name, episode_num))

	steps = 0
	actions = [K_RIGHT, K_LEFT, K_UP, K_DOWN, K_SPACE]
	rle = initializeEnvironment(gameString, levelString, headless=False)
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
MAX_STEPS = 100
WINS_REQUIRED = 3 # in the last 2*WINS_REQUIRED games
wins = 0 #ignore the above one now I guess
level_game_pairs = []
steps = 0
rle = None
ended = True
levelNum = 0
gameName = ''
episodeResults = []

def init_game(path, isLocal=None, gvgai_path = "gvgai/mturk_games/"):
	global level_game_pairs , rle , ended , steps , levelNum , gameName , episodeResults , wins

	#if '/' in path:
	#	gameName = path[path.rfind('/')+1:]
	#elif '.' in path:
	#	gameName = path[path.rfind('.')+1:]
	#else:
	#	gameName = path

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
		level_game_pairs = load_gvgai_game(path, path=gvgai_path)

	steps = 0
	levelNum = 0
	wins = 0
	episodeResults = []

	rle = initializeEnvironment(level_game_pairs[0][0], level_game_pairs[0][1])

	ended = False

	# image , reward , game_has_ended
	return generateImage(rle._game) , 0 , ended

def step(action):
	# takes the step provided and returns the new state, reward, and whether the game has ended
	global steps , wins , rle , levelNum , ended , episodeResults

	if action == 'next_episode':
		if levelNum < len(level_game_pairs):
			rle = initializeEnvironment(level_game_pairs[levelNum][0], level_game_pairs[levelNum][1])
			steps = 0
			ended = False
			return generateImage(rle._game), 0 , ended

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
	print rle

	if steps > MAX_STEPS: 
		print "MAX_STEPS threshold exceeded, ending game."
		ended = True

	if ended:
		episodeResults.append((gameName, levelNum, steps, win, score))

	if win:
		# if they've won half of the last 2*WINS_REQUIRED games
		wins += 1
		if wins >= 2: #sum(1 if tup[3] else 0 for tup in episodeResults[-2*WINS_REQUIRED:]) >= WINS_REQUIRED:
			# next level
			levelNum += 1

	# image , reward , game_has_ended
	return generateImage(rle._game) , score-lastscore , ended

def writeResults(path='results.csv'):
	out = open(path, 'w')
	out.write( 'game name,level number,steps,win,score\n' ) 
	for tup in episodeResults:
		out.write('{},{},{},{},{}\n'.format(*tup))

def screenToNumpyArray(screen):
	arr = pygame.surfarray.array3d(screen)
	ret = np.copy(arr.transpose(1, 0, 2))
	return ret

def generateImage(game):
	# returns numpy array of pixel values based on the sprites in the game
	im = np.empty([game.screensize[1], game.screensize[0], 3], dtype=np.uint8)
	bg = np.array(LIGHTGRAY, dtype=np.uint8) # background
	im[:] = bg

	for className in game.sprite_order:
		if className in game.sprite_groups:
			for sprite in game.sprite_groups[className]:
				r, c, h, w = sprite.rect.top , sprite.rect.left , sprite.rect.height , sprite.rect.width
				im[r:r+h, c:c+w, :] = np.array(sprite.color, dtype=np.uint8)

	return im



# if len(sys.argv) > 1:
# 	play_trainset()

# embed()
