from main_agent import Agent
from games_to_hyperparameters import *
import time
import pickle
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
parser.add_argument('--pickled_theory_path',type=str,default=str(0),help='pickled theory path')
parser.add_argument('--max_rand_steps',type=int,default=0,help='MAX STEPS')
parser.add_argument('--use_pickled_theories',type=str2bool, default=False)

args = parser.parse_args()
game_number = args.game_number
game_name = args.game_name
hyperparameter_index = args.hyperparameter_index
IW_k = args.IW_k
extra_atom_allowed = args.extra_atom_allowed
make_movie = args.make_movie
pickled_theory_path = args.pickled_theory_path
max_rand_steps = args.max_rand_steps
use_pickled_theories = args.use_pickled_theories
if use_pickled_theories:
    print "haven't implemented use_pickled_theories stuff in load_games.py"
    ## think about whether you want each run of vgdl.load_games to use a particular theory for each game,
    ## or to loop through all of them, etc.
    embed()
burn_in_episodes_per_game = 1

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

def play_trainset(hyperparameter_sets, hyperparameter_index, max_rand_steps):
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

    agent = Agent('full', game_name, hyperparameter_sets=hyperparameter_sets, hyperparameter_index=hyperparameter_index, IW_k=IW_k, 
            extra_atom_allowed=extra_atom_allowed, max_rand_steps=max_rand_steps)

    ##then pass this down for multiple episodes
    gameObject = None
    print game_levels

    agent.playCurriculum(level_game_pairs=level_game_pairs, make_movie=make_movie)

    print game_levels

    total_time = time.time() - start_time

    return total_time

def play_trainset_with_learned_theories(hyperparameter_sets, hyperparameter_index, max_rand_steps, pickled_theory_path=None):
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


    if pickled_theory_path:
        all_theories = []
        for folder in os.listdir(pickled_theory_path):
            if 'DS_Store' not in folder:
                theories = os.listdir('{}/{}'.format(pickled_theory_path, folder))
                for t in theories:
                    if 'DS_Store' not in t:
                        file = open('{}/{}/{}'.format(pickled_theory_path,folder,t),'r')
                        burn_in = int(t[:t.rfind('steps.pkl')])
                        initialTheory = pickle.load(file)
                        file.close()
                        all_theories.append((initialTheory, burn_in))

        set_theories = list(set([t[0] for t in all_theories]))
        ## tag each theories with the burn-ins that correspond to it.
        for t in set_theories:
            t.burn_ins = []
            for a in all_theories:
                if t==a[0]:
                    t.burn_ins.append(a[1])
    print [t.burn_ins for t in set_theories]
    for i,t in enumerate(set_theories):
        agent = Agent('full', game_name, hyperparameter_sets=hyperparameter_sets, hyperparameter_index=hyperparameter_index, IW_k=IW_k, 
                extra_atom_allowed=extra_atom_allowed, max_rand_steps=max_rand_steps, init_hypothesis=t)
        ##then pass this down for multiple episodes
        gameObject = None
        print "running curriculum for theory number {} of {}".format(i, len(set_theories))
        print game_levels
        agent.playCurriculum(level_game_pairs=level_game_pairs, make_movie=make_movie)
        print game_levels

    total_time = time.time() - start_time

    return total_time

#######
## To generate burn-in data, call with max_rand_steps>0 and no pickled_theory_path
## To generate normal behavior using a pickled theory, call with a pickled_theory_path
## To run with epsilon_greedy call w/o max_rand_steps and w/o pickled_theory_path but w/ epsilon_greedy=True
#######
## normal play
if pickled_theory_path==str(0) and max_rand_steps==0:
    print "you actually haven't implemented things such that you can run normal mode in this branch"
    embed()
    play_trainset(hyperparameter_sets, hyperparameter_index, max_rand_steps)
##explore randomly to make theories
elif pickled_theory_path == str(0) and max_rand_steps>0:
    for i in range(burn_in_episodes_per_game):
        play_trainset(hyperparameter_sets, hyperparameter_index, max_rand_steps)
##use learned theories
elif pickled_theory_path != str(0):
    pickled_theory_path = './lesions/rand_exploration/{}'.format(game_name)
    max_rand_steps = 0 ## don't do random exploration if you're using a previously-acquired theory
    play_trainset_with_learned_theories(hyperparameter_sets, hyperparameter_index, max_rand_steps, pickled_theory_path)




