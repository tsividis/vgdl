from hyperopt import fmin, tpe, hp
from pathos.multiprocessing import ProcessingPool
from main_agent import Agent
import time
import dill


# NOTE: fmin seems to fail with the hyperopt version installed by default
# as of 01/2018: it is best to install directly from the github repo with
# the command 'pip install git+https://github.com/hyperopt/hyperopt'

gvggames = ['aliens', 'boulderdash', 'butterflies', 'chase', 'frogs',  # 0-4
            'missilecommand', 'portals', 'sokoban', 'survivezombies', 'zelda']  # 5-9

def play_trainset(hyperparameters, game_number):
    start_time = time.time()
    filename = "examples.gridphysics_2.expt_relational"

    level_game_pairs = None

    #uncomment this line to run local games
    gameName = filename

    agent = Agent('full', gameName, hyperparameter_sets=hyperparameters, parallel_planning=False)

    ##then pass this down for multiple episodes
    gameObject = None
    agent.playCurriculum(level_game_pairs=level_game_pairs)

    total_time = time.time() - start_time

    return total_time

hyperparameter_sets = [
    {
     'sprite_first_alpha': 1,
     'sprite_second_alpha': 1,
     'sprite_negative_mult': 1,
     'multisprite_first_alpha': 1,
     'multisprite_second_alpha': 1,
     'novelty_first_alpha': 1,
     'novelty_second_alpha': 1,
     },
    {
     'sprite_first_alpha': 10,
     'sprite_second_alpha': 1,
     'sprite_negative_mult': 1,
     'multisprite_first_alpha': 10,
     'multisprite_second_alpha': 1,
     'novelty_first_alpha': 10,
     'novelty_second_alpha': 1,
     },
     {
     'sprite_first_alpha': 1,
     'sprite_second_alpha': 10,
     'sprite_negative_mult': 1,
     'multisprite_first_alpha': 1,
     'multisprite_second_alpha': 10,
     'novelty_first_alpha': 1,
     'novelty_second_alpha': 10,
     }
]
play_trainset(hyperparameter_sets, None)
