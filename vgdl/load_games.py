from main_agent import Agent
import time
import dill
import os
from IPython import embed
import argparse

parser = argparse.ArgumentParser(description='Process game number.')
parser.add_argument('--game_number', type=int, default=0, help='game number')
parser.add_argument('--game_name', type=str, default=str(0), help='game name')
parser.add_argument('--hyperparameters', type=int, default=0, help='hyperparameters')

args = parser.parse_args()
game_number = args.game_number
game_name = args.game_name
hyperparameters = args.hyperparameters

# gameFileString = 'training_set_1'
gameFileString = 'gvgai/games'

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

def play_trainset(hyperparameters):
    start_time = time.time()

    gvgname = "./{}/{}".format(gameFileString,game_name)
    gameString = read_gvgai_game('{}.txt'.format(gvgname))
    game_levels = [l for l in os.listdir(gameFileString) if l[0:len(game_name+'_lvl')] == game_name+'_lvl']
    print game_levels

    level_game_pairs = []
    for level_number in range(len(game_levels)):
    	with open('{}_lvl{}.txt'.format(gvgname, level_number), 'r') as level:
    		level_game_pairs.append([gameString, level.read()])

    agent = Agent('full', game_name, hyperparameter_sets=hyperparameters, parallel_planning=False)

    ##then pass this down for multiple episodes
    gameObject = None

    agent.playCurriculum(level_game_pairs=level_game_pairs)

    total_time = time.time() - start_time

    return total_time

play_trainset([hyperparameters])
