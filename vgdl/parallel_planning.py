from hyperopt import fmin, tpe, hp
from pathos.multiprocessing import ProcessingPool
from agent import Agent
import time
import dill


# NOTE: fmin seems to fail with the hyperopt version installed by default
# as of 01/2018: it is best to install directly from the github repo with
# the command 'pip install git+https://github.com/hyperopt/hyperopt'

gvggames = ['aliens', 'boulderdash', 'butterflies', 'chase', 'frogs',  # 0-4
            'missilecommand', 'portals', 'sokoban', 'survivezombies', 'zelda']  # 5-9

filename = "examples.gridphysics.avatar_inference"  # to play a "local" game
gameName = gvggames[2]  # to play a gvgai game

def play_trainset(hyperparameters, game_number):
    start_time = time.time()

    level_game_pairs = None

    # Start uncommenting here to play GVG-AI games
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


    # gvgname = "../gvgai/training_set_1/{}".format(gameName)

    # gameString = read_gvgai_game('{}.txt'.format(gvgname))


    # level_game_pairs = []
    # for level_number in range(5):
        # with open('{}_lvl{}.txt'.format(gvgname, level_number), 'r') as level:
            # level_game_pairs.append([gameString, level.read()])
    
    # stop uncommenting here to play GVGAI games
    #uncomment this line to run local games
    gameName = filename

    agent = Agent('full', gameName, hyperparameter_sets=hyperparameters, parallel_planning=False)

    ##then pass this down for multiple episodes
    gameObject = None
    # agent.playCurriculum(level_game_pairs=level_game_pairs)
    agent.playEpisodes(None,5)
    total_time = time.time() - start_time

    return total_time

hyperparameter_sets = [
    {
     'sprite_first_alpha': 10000,
     'sprite_second_alpha': 100,
     'sprite_negative_mult': .1,
     'multisprite_first_alpha': 10000,
     'multisprite_second_alpha': 100,
     'novelty_first_alpha': 5000,
     'novelty_second_alpha': 50,
     }
]
play_trainset(hyperparameter_sets, None)
