import argparse, os

parser = argparse.ArgumentParser(description='Process game number.')
parser.add_argument('--game_name', type=str, default=str(0), help='game name')

args = parser.parse_args()
game_name = args.game_name
gameFileString = 'gvgai/games'

def read_gvgai_game(filename):
    with open(filename, 'r') as f:
        game=f.read()
    return game

def create_level_game_pairs(game_name):
    gvgname = "./{}/{}".format(gameFileString, game_name)
    gameString = read_gvgai_game('{}.txt'.format(gvgname))
    game_levels = [l for l in os.listdir(gameFileString) if l[0:len(game_name+'_lvl')] == game_name+'_lvl']

    level_game_pairs = []
    for level_number in range(len(game_levels)):
    	with open('{}_lvl{}.txt'.format(gvgname, level_number), 'r') as level:
    		level_game_pairs.append([gameString, level.read()])

    return level_game_pairs

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    import random, sys, time
    import numpy as np
    import csv
    from IPython import embed

    # if len(sys.argv)>=2:
    #     game_n = int(sys.argv[1])

    # else:
    #     game_n = 0

    level_game_pairs = create_level_game_pairs(game_name)
    # if len(sys.argv)>=3:
         # level_n = int(sys.argv[2])
         # level_game_pairs = [level_game_pairs[level_n]]
         
    for index, level in enumerate(level_game_pairs):
        wins = 0
        tries = 0
        while wins<1 and tries<3:
            VGDLParser.playGame(*level)
            time.sleep(1)
            data = np.load("temp_data.npy")
            win = data[2]
            if win:
                wins+=1
            tries += 1
            levels_won = index + wins
            # Save in format [subect, condition, gamename, levels won, steps taken, score, time elapsed]
            row = ['human', 'no_score', 'expt_preconditions', levels_won, data[1], data[3], data[0]]

            filename = "human_data_{}.csv".format(gvggames[game_n])
            f = open(filename, 'a+') ##append, but also read.
            g = open(filename, 'r')
            writer = csv.writer(f)
            if len(g.readlines())==0:
                writer.writerow(('subject', 'condition', 'gameName', 'levels_won', 'steps', 'score', 'time'))
            writer.writerow(row)
            f.close()
            g.close()
