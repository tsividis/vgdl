from rlenvironmentnonstatic import createRLInputGame, createRLInputGameFromStrings, defInputGame, createMindEnv
from hyperopt import fmin, tpe, hp
from pathos.multiprocessing import ProcessingPool
import time
import dill

import argparse

"""
python -m vgdl.play_games --game_number 14
"""
parser = argparse.ArgumentParser(description='Process game number.')
parser.add_argument('--game_number', type=int, default=0, help='game number')

args = parser.parse_args()
game_number = args.game_number
# NOTE: fmin seems to fail with the hyperopt version installed by default
# as of 01/2018: it is best to install directly from the github repo with
# the command 'pip install git+https://github.com/hyperopt/hyperopt'

gvggames = ['aliens', 'boulderdash', 'butterflies', 'chase', 'frogs',  # 0-4
            'missilecommand', 'portals', 'sokoban', 'survivezombies', 'zelda']  # 5-9

local_games = ['expt_antagonist', 'expt_exploration_exploitation', 'expt_helper',  # 10-12
    'expt_preconditions', 'expt_push_boulders2', 'expt_relational']  # 13-15 to play a "local" game

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


        gvgname = "../gvgai/training_set_1/{}".format(gameName)

        gameString = read_gvgai_game('{}.txt'.format(gvgname))


        level_game_pairs = []
        for level_number in range(5):
        	with open('{}_lvl{}.txt'.format(gvgname, level_number), 'r') as level:
        		level_game_pairs.append([gameString, level.read()])

    # running local games
    else:
        level_game_pairs = None
        gameName = 'examples.gridphysics.{}'.format(local_games[game_number-10])


    # agent = Agent('full', gameName, hyperparameter_sets=hyperparameters, parallel_planning=False)

    ##then pass this down for multiple episodes
    # gameObject = None
    playCurriculum(level_game_pairs=level_game_pairs)
    # agent.playEpisodes(None,5)

    # total_time = time.time() - start_time

    return total_time

def initializeEnvironment(self, gameFileName):
    gameString, levelString = defInputGame(gameFilename, randomize=False)
    rleCreateFunc = lambda: createRLInputGameFromStrings(gameString, levelString)
    rle = rleCreateFunc()
    return rle

def playEpisode(self, gameObject, episode_num):
    steps = 0
    rle = initializeEnvironment()

    for i in range(10):
        if not ended:
            rle.step(0)
            steps += 1
            ended, win = rle._isDone()

    return win, rle._game.score, steps

def playCurriculum(level_game_pairs, num_episodes=10):
    """ Plays a game level until it wins or exceeds num_episodes, then moves to the next one until
    completion. """

    total_game_steps, levels_won = 0, 0
    for n_level, level_game in enumerate(level_game_pairs):
        win = False
        gameObject = None
        i=0
        first_time_playing_level = True
        allStatesEncountered = []
        while not win and i<num_episodes:
            win, score, steps = self.playEpisode(gameObject, i, win=win, first_time_playing_level=first_time_playing_level)
            total_game_steps += steps
            episodes.append((n_level, steps, win, score))
            i+=1
        if i>=num_episodes:
            return

        levels_won +=1

    return


play_trainset()
