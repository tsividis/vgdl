import os
import argparse
from rlenvironmentnonstatic import createRLInputGame, createRLInputGameFromStrings, defInputGame, createMindEnv
from IPython import embed
from pygame import K_LEFT, K_UP, K_RIGHT, K_DOWN, K_SPACE
import random
from util import str2bool

actions = [K_LEFT, K_UP, K_RIGHT, K_DOWN, K_SPACE]

"""
Interface for loading and running a vgdl game. As a demo, runs a random agent on a specified game.

While running, it prints an ascii schematic of game (easy to remove), and prints list of effects that occur in any timestep.

Usage:
From top-level vgdl folder: python -m vgdl.agent_API --game_name [gamenamestring] --print_ascii [True/False] print_events [True/False] ## e.g., --game_name win_fast --print_ascii True --print_events True

"""


parser = argparse.ArgumentParser(description='')
parser.add_argument('--game_name', type=str, default=str(0), help='game name')
parser.add_argument('--print_ascii', type=str2bool, default=False, help='print_ascii')
parser.add_argument('--print_events', type=str2bool, default=False, help='print_events')

args = parser.parse_args()
game_name = args.game_name
print_ascii = args.print_ascii
print_events = args.print_events

gameFileString = 'all_games'

def gen_color():
    from vgdl.colors import colorDict
    color_list = colorDict.values()
    color_list = [c for c in color_list if c not in ['UUWSWF']]
    for color in color_list:
        yield color

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

def initializeEnvironment(gameString=None, levelString=None):
    if gameString==None or levelString==None:
        gameString, levelString = defInputGame(gameFilename, randomize=False)
    rleCreateFunc = lambda: createRLInputGameFromStrings(gameString, levelString)
    env = rleCreateFunc()
    return env

def grabLevelGamePairs(gameFileString, game_name):
	game_levels = [l for l in os.listdir(gameFileString) if l[0:len(game_name+'_lvl')] == game_name+'_lvl']

	if "{}.txt".format(game_name) in os.listdir(gameFileString):
	    gvgname = "./{}/{}".format(gameFileString, game_name)
	    game_description = read_gvgai_game('{}.txt'.format(gvgname))
	    game_descriptions = [game_description]*len(game_levels)
	else:
	    game_descriptions = [read_gvgai_game("./{}/{}".format(gameFileString, d)) for d in sorted([e for e in os.listdir(gameFileString) if (game_name in e and 'desc' in e)])]

	level_game_pairs = []
	gvgname = "./{}/{}".format(gameFileString, game_name)
	for level_number in range(len(game_levels)):
	    with open('{}_lvl{}.txt'.format(gvgname, level_number), 'r') as level:
	        level_game_pairs.append([game_descriptions[level_number], level.read()])
	return level_game_pairs

def playEpisode(level_game_pair):
	game_rules, level_description = level_game_pair
	env = initializeEnvironment(game_rules, level_description)
	ended, win = env._isDone()

	if print_ascii:
		print env.show()

	while not ended:
		action = random.choice(actions)
		env.step(action)
		if print_ascii:
			print env.show()
		if print_events and env.getEffectListByColor():
			print env.geteffectListByColor()
		ended, win = env._isDone()

	return win

def playCurriculum(level_game_pairs):
	for i, level_game_pair in enumerate(level_game_pairs):
		win = False
		while not win:
			win = playEpisode(level_game_pair)
			level_status = 'win' if win else 'loss'
			print "Level {} ended in {}".format(i, level_status)
	return


level_game_pairs = grabLevelGamePairs(gameFileString, game_name)
playCurriculum(level_game_pairs)


##Add image rendering and effects


