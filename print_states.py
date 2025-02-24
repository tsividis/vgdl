from pymongo import MongoClient
import pprint
import random
from datetime import datetime

import json
import sys
import socket
import csv
from collections import defaultdict
from vgdl import core
from IPython import embed

STATE_KEYS_TO_PRINT = ["joystick_state",  "keyPressType", "trigger_play_clock"]

# USAGE: python print_states.py [subj_id] [run_id] [block_id] [instance_id] [play_id]
# * - optional

# Cedric: To make the code work in the same way as before when executed on the
# server, change the string 'harvard' below to match the server hostname
if 'harvard' not in socket.gethostname():
    # local 
    client = MongoClient('localhost', 27017)
else:
    # cluster
    client = MongoClient('holy7c22108.rc.fas.harvard.edu', 27017)

db = client['heroku_7lzprs54']

if __name__ == '__main__':
    subj_id = sys.argv[1]
    run_id = int(sys.argv[2])

    query = {'subj_id': subj_id, 'run_id': run_id}

    if len(sys.argv) > 3:
        query['block_id'] = int(sys.argv[3])
    if len(sys.argv) > 4:
        query['instance_id'] = int(sys.argv[4])
    if len(sys.argv) > 5:
        query['play_id'] = int(sys.argv[5])

    plays = db.plays.find(query)

    for i_play, play in enumerate(plays):
        subj = db.subjects.find_one({'subj_id': subj_id})
        game = subj['games'][play['game_id']]
        game_str = game['descs'][play['desc_id']]
        level_str = game['levels'][play['level_id']]
        assert game_str == play['game_str']
        assert level_str == play['level_str']

        zstates = play['zstates']
        states = core.VGDLParser.decompress(zstates)
        states = states['states'] # dummy dict
        print(list(states[20].keys()))
        for i_state in range(0, len(states), 20):
            print("play %d, state %d" % (i_play, i_state))
            state = states[i_state]
            for k in STATE_KEYS_TO_PRINT:
                if k in state:
                    print("state[%s]: %s" % (k, state[k]))
                else:
                    print("%s not in state" % k)

