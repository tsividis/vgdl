from EMPA import Agent
from games_to_hyperparameters import *
import time
# import dill
import os
from IPython import embed
import argparse
import subprocess
from util import str2bool
from make_gameplay_videos import *
from contextlib import contextmanager
import sys

@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout


parser = argparse.ArgumentParser(description='Process game number.')
parser.add_argument('--game_number', type=int, default=0, help='game number')
parser.add_argument('--game_name', type=str, default=str(0), help='game name')
parser.add_argument('--hyperparameter_index', type=int, default=3, help='hyperparameter_index')
parser.add_argument('--metacontroller_index', type=int, default=0, help='metacontroller_index')
parser.add_argument('--IW_k', type=int, default=1, help='IW_k')
parser.add_argument('--extra_atom_allowed', type=bool, default=True, help='extra_atom_allowed')
parser.add_argument('--task_ID', type=int, default=0, help='task_ID')
parser.add_argument('--heatmap', type=str2bool, default=False, help='heatmap')
parser.add_argument('--make_movie', type=str2bool, default=False, help='make_movie')
parser.add_argument('--play_movie', type=str2bool, default=False, help='play_movie')
parser.add_argument('--produce_printout', type=str2bool, default=False, help='produce_printout')
parser.add_argument('--color_only', type=str2bool, default=False, help='color_only')


args = parser.parse_args()
game_number = args.game_number
game_name = args.game_name
hyperparameter_index = args.hyperparameter_index
metacontroller_index = args.metacontroller_index
IW_k = args.IW_k
extra_atom_allowed = args.extra_atom_allowed
task_ID = str(args.task_ID)
make_movie = args.make_movie
play_movie = args.play_movie
heatmap = args.heatmap

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

def play_trainset(hyperparameter_sets, hyperparameter_index, args=None):
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

    agent = Agent('full', game_name, hyperparameter_sets=hyperparameter_sets, hyperparameter_index=hyperparameter_index, metacontroller_index=metacontroller_index, IW_k=IW_k, extra_atom_allowed=extra_atom_allowed, task_ID=task_ID, produce_printout=args.produce_printout)

    ##then pass this down for multiple episodes
    gameObject = None
    # print game_levels

    estimated_time = {
    'aliens': '40 minutes',
    'tiny_zelda': '1 minute',
    'demo_aliens': '5 minutes',
    'demo_bait': '4 minutes',
    'demo_butterflies': '5 minutes',
    'demo_sokoban': '20 minutes',
    'demo_zelda': '5 minutes',
    'zelda': '5 minutes',
    'bait': '10 hours'
    }
    print ""

    print "Playing {}".format(game_name)

    if game_name in estimated_time:
        print "Expected runtime for this game: {}".format(estimated_time[game_name])
    else:
        print "No estimated runtime for this game."

    print ""

    video_dirname = 'demo_data_files/EMPA/local/data_for_movies/all_agent_types/all_games'
    if not os.path.exists(video_dirname):
        os.makedirs(video_dirname)

    agent.playCurriculum(level_game_pairs=level_game_pairs, make_movie=False, play_movie=False, heatmap=heatmap)

    if make_movie:
        ## copy data file to temporary video directory
        com = "cp {} {}".format(agent.filename, video_dirname)
        command = "{}".format(com)
        subprocess.call(command, shell=True)
        # embed()
        ## Make movie and suppress terminal output

        if args.color_only:
            # com = "python ../vgdl-movies/vgdl/make_gameplay_videos.py --color_only True"

            com = "python ../vgdl-movies/vgdl/make_gameplay_videos.py --color_only True > /dev/null 2>&1"
        else:
            # com = "python ../vgdl-movies/vgdl/make_gameplay_videos.py --color_only False"

            com = "python ../vgdl-movies/vgdl/make_gameplay_videos.py --color_only False > /dev/null 2>&1"

        command = "{}".format(com)

        if args.make_movie:
            print "Producing game-play video."
            print "The video will open automatically in Quicktime after it is made. If it doesn't, please check the 'vgdl-movies/vgdl/videos' directory in this folder."

        with suppress_stdout():
            subprocess.call(command, shell=True)

        # if play_movie:
        #     video_dirname = "../vgdl-movies/vgdl/videos/" ## finish this
        #     command = ('open', '-a', 'Quicktime Player', video_dirname)
        #     subprocess.Popen(command)

        ## clear temporary video directory
        # com = "rm {}/*".format(video_dirname)
        # command = "{}".format(com)
        # subprocess.call(command, shell=True)


    # print game_levels

    total_time = time.time() - start_time

    print total_time

    return total_time

# embed()

print "This file needs to be modified before it can run. Look at load_games.py for the right structure."
# play_trainset(hyperparameter_sets, hyperparameter_index, args)



# fullData = processModelData(dirName,games_to_make=['tiny_zelda'])
# loadedData = loadEMPAData(fullData)
# makeEMPAMovies(loadedData)
