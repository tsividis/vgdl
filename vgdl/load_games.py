from main_agent import Agent
from games_to_hyperparameters import *
import time
import dill
import os
from IPython import embed
import argparse
from util import str2bool

parser = argparse.ArgumentParser(description='Process game number.')
parser.add_argument('--game_number', type=int, default=0, help='game number')
parser.add_argument('--game_name', type=str, default=str(0), help='game name')
parser.add_argument('--hyperparameter_index', type=int, default=3, help='hyperparameter_index')
parser.add_argument('--IW_k', type=int, default=2, help='IW_k')
parser.add_argument('--extra_atom_allowed', type=bool, default=True, help='extra_atom_allowed')
parser.add_argument('--make_movie', type=str2bool, default=False, help='make_movie')
# parser.add_argument('--pickled_theory_path',type=str,default=str(0),help='pickled theory path')
parser.add_argument('--max_rand_steps',type=int,default=1000,help='MAX STEPS')
parser.add_argument('--use_pickled_theories',type=str2bool, default=False)

args = parser.parse_args()
game_number = args.game_number
game_name = args.game_name
hyperparameter_index = args.hyperparameter_index
IW_k = args.IW_k
extra_atom_allowed = args.extra_atom_allowed
make_movie = args.make_movie
# pickled_theory_path = args.pickled_theory_path
max_rand_steps = args.max_rand_steps
use_pickled_theories = args.use_pickled_theories
if use_pickled_theories:
    print "haven't implemented use_pickled_theories stuff in load_games.py"
    ## think about whether you want each run of vgdl.load_games to use a particular theory for each game,
    ## or to loop through all of them, etc.
    embed()

if game_name==str(0):
    game_name = game_names[game_number]

# gameFileString = 'training_set_1'
# gameFileString = 'gvgai/games'
gameFileString = 'all_games'

hyperparameter_sets = [
    {'idx'           : 0,
     'short_horizon' : False,
     'first_order_horizon': True,
     'sprite_first_alpha': 10000,
     'sprite_second_alpha': 100,
     'sprite_negative_mult': .1,
     'multisprite_first_alpha': 10000,
     'multisprite_second_alpha': 100,
     'novelty_first_alpha': 5000,
     'novelty_second_alpha': 50,
     },
    {'idx'           : 1,
     'short_horizon' : False,
     'first_order_horizon': False,
     'sprite_first_alpha': 10000,
     'sprite_second_alpha': 100,
     'sprite_negative_mult': 10.,
     'multisprite_first_alpha': 10000,
     'multisprite_second_alpha': 100,
     'novelty_first_alpha': 5000,
     'novelty_second_alpha': 50,
     },
    {'idx'           : 2,
     'short_horizon' : False,
     'first_order_horizon': False,
     'sprite_first_alpha': 10000,
     'sprite_second_alpha': 100,
     'sprite_negative_mult': .1,
     'multisprite_first_alpha': 10000,
     'multisprite_second_alpha': 100,
     'novelty_first_alpha': 5000,
     'novelty_second_alpha': 50,
     },
    {'idx'           : 3,
     'short_horizon' : True,
     'first_order_horizon': True,
     'sprite_first_alpha': 10000,
     'sprite_second_alpha': 100,
     'sprite_negative_mult': 10, #normally .1
     'multisprite_first_alpha': 10000,
     'multisprite_second_alpha': 100,
     'novelty_first_alpha': 5000,
     'novelty_second_alpha': 50,
     },
    {'idx'           : 4,
     'short_horizon' : True,
     'first_order_horizon': True,
     'sprite_first_alpha': 10000,
     'sprite_second_alpha': 100,
     'sprite_negative_mult': .1, #normally .1
     'multisprite_first_alpha': 10000,
     'multisprite_second_alpha': 100,
     'novelty_first_alpha': 5000,
     'novelty_second_alpha': 10,
     }
]

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

def play_trainset(hyperparameter_sets, hyperparameter_index, max_rand_steps, pickled_theory_path=None):
    start_time = time.time()

    game_levels = [l for l in os.listdir(gameFileString) if l[0:len(game_name+'_lvl')] == game_name+'_lvl']

    if "{}.txt".format(game_name) in os.listdir(gameFileString):
        gvgname = "./{}/{}".format(gameFileString, game_name)
        game_description = read_gvgai_game('{}.txt'.format(gvgname))
        game_descriptions = [game_description]*len(game_levels)
    else:
        game_descriptions = [read_gvgai_game("./{}/{}".format(gameFileString, d)) for d in sorted([e for e in os.listdir(gameFileString) if (game_name in e and 'desc' in e)])]
    # embed()

    level_game_pairs = []
    gvgname = "./{}/{}".format(gameFileString, game_name)
    for level_number in range(len(game_levels)):
        with open('{}_lvl{}.txt'.format(gvgname, level_number), 'r') as level:
            level_game_pairs.append([game_descriptions[level_number], level.read()])

# def play_trainset(hyperparameters_sets, hyperparameter_index):
#     start_time = time.time()

#     gvgname = "./{}/{}".format(gameFileString,game_name)
#     gameString = read_gvgai_game('{}.txt'.format(gvgname))
#     game_levels = [l for l in os.listdir(gameFileString) if l[0:len(game_name+'_lvl')] == game_name+'_lvl']
#     print game_levels
#     level_game_pairs = []
#     for level_number in range(len(game_levels)):
#     	with open('{}_lvl{}.txt'.format(gvgname, level_number), 'r') as level:
#     		level_game_pairs.append([gameString, level.read()])

    agent = Agent('full', game_name, hyperparameter_sets=hyperparameter_sets, hyperparameter_index=hyperparameter_index, IW_k=IW_k, 
            extra_atom_allowed=extra_atom_allowed, max_rand_steps=max_rand_steps, pickled_theory_path=pickled_theory_path)

    ##then pass this down for multiple episodes
    gameObject = None
    print game_levels

    agent.playCurriculum(level_game_pairs=level_game_pairs, make_movie=make_movie)

    print game_levels

    total_time = time.time() - start_time

    return total_time

if pickled_theory_path != str(0):
    play_trainset(hyperparameter_sets,max_rand_steps,pickled_theory_path)
else:
    play_trainset(hyperparameter_sets,max_rand_steps)





