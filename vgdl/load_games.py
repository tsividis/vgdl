from EMPA import Agent
from environment import Environment
from games_to_hyperparameters import *
import time
# import dill
import os
from IPython import embed
import argparse
from util import str2bool
from collections import defaultdict
from hyperparameters import *

parser = argparse.ArgumentParser(description='Process game number.')
parser.add_argument('--game_number', type=int, default=0, help='game number')
parser.add_argument('--game_name', type=str, default=str(0), help='game name')
parser.add_argument('--bfs_depth', type=int, default=3, help='number of tree levels to run bfs for')
parser.add_argument('--bfs_range', type=int, default=0, help="interval between 2 BFS'")
parser.add_argument('--boltz_init', type=float, default=8.0, help="initial boltz temp value")
parser.add_argument('--boltz_exploit', type=int, default=500, help='steps for boltz_temp to finally decay to boltz_min')
parser.add_argument('--boltz_min', type=float, default=0.1, help='residual boltz temp value')
parser.add_argument('--epsilon_init', type=float, default=1.0, help='initial epsilon value')
parser.add_argument('--epsilon_exploit', type=int, default=500, help='steps for epsilon to finally decay to epsilon_min')
parser.add_argument('--epsilon_min', type=int, default=0.1, help='residual epsilon value')
parser.add_argument('--empa_plan_nodes', type=int, default=50, help='number of nodes to open during empa search')
parser.add_argument('--win_bonus', type=int, default=1000000, help='intrinsic reward bonus on reaching goal')
parser.add_argument('--hyperparameter_index', type=str, default='short-term', help='hyperparameter_index')
parser.add_argument('--metacontroller_index', type=int, default=0, help='metacontroller_index')
parser.add_argument('--IW_k', type=int, default=1, help='IW_k')
parser.add_argument('--extra_atom_allowed', type=bool, default=True, help='extra_atom_allowed')
parser.add_argument('--task_ID', type=int, default=0, help='task_ID')
parser.add_argument('--heatmap', type=str2bool, default=False, help='heatmap')
parser.add_argument('--make_movie', type=str2bool, default=False, help='make_movie')
parser.add_argument('--produce_printout', type=str2bool, default=True, help='produce_printout')

args = parser.parse_args()
game_number = args.game_number
game_name = args.game_name

# constants relevant for curiosity ablation
boltz_hyps = {
    'bfs_depth': args.bfs_depth,
    'bfs_range': args.bfs_range,
    'boltz_init': args.boltz_init,
    'boltz_min': args.boltz_min,
    'boltz_exploit': args.boltz_exploit,
    'epsilon_init' : args.epsilon_init,
    'epsilon_min' : args.epsilon_min,
    'epsilon_exploit' : args.epsilon_exploit,
    'empa_plan_nodes': args.empa_plan_nodes,
    'win_bonus': args.win_bonus
}

print("HYPERPARAMS ARE")
print(boltz_hyps)

hyperparameter_index = args.hyperparameter_index
metacontroller_index = args.metacontroller_index
IW_k = args.IW_k
extra_atom_allowed = args.extra_atom_allowed
task_ID = str(args.task_ID)
make_movie = args.make_movie
heatmap = args.heatmap
produce_printout = args.produce_printout

if game_name==str(0):
    game_name = game_names[game_number]

# gameFileString = 'training_set_1'
# gameFileString = 'gvgai/games'
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

def play_trainset(hyperparameter_sets, hyperparameter_index, args=None, boltz_hyps = None):
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

    agent = Agent('full', game_name, hyperparameter_sets=hyperparameter_sets, hyperparameter_index=hyperparameter_index, metacontroller_index=metacontroller_index, IW_k=IW_k, extra_atom_allowed=extra_atom_allowed, task_ID=task_ID)
    
    environment = Environment(game_name, agent, task_ID=task_ID, produce_printout = produce_printout)

    ##then pass this down for multiple episodes
    gameObject = None
    # print game_levels

    estimated_time = defaultdict(lambda: 'unknown')
    estimated_time['aliens'] = '10 minutes'
    estimated_time['tiny_zelda'] = '1 minute'
    estimated_time['demo_bait'] = '3 minutes'
    estimated_time['zelda'] = '5 minutes'
    estimated_time['bait'] = '10 hours'
    print ""

    if args.make_movie:
        print "Playing and producing game-play video for {}".format(game_name)
    else: 
        print "Playing {}".format(game_name)
    print "Typical runtime for this game: {}".format(estimated_time[game_name])

    environment.playCurriculum(level_game_pairs=level_game_pairs, make_movie=make_movie, heatmap=heatmap, boltz_hyps = boltz_hyps)

    # print game_levels

    total_time = time.time() - start_time

    return total_time

play_trainset(hyperparameter_sets, hyperparameter_index, args, boltz_hyps)



