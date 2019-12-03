from pymongo import MongoClient
import pprint
import random
from datetime import datetime

import json
import sys
import csv
from collections import defaultdict
from vgdl import core
from IPython import embed

# USAGE: python fmri_replay.py [subj_id] [run_id] [block_id*] [instance_id*] [play_id*]
# * - optional

client = MongoClient('localhost', 27017)
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

    for play in plays:
        subj = db.subjects.find_one({'subj_id': subj_id})
        game = subj['games'][play['game_id']]
        game_str = game['descs'][play['desc_id']]
        level_str = game['levels'][play['level_id']]
        assert game_str == play['game_str']
        assert level_str == play['level_str']

        # TODO video name formatted 
        print 'Replaying subj %s, run %d, block %d, instance %d, play %d: %s (%s), desc %d, level %d' % (play['subj_id'], play['run_id'], play['block_id'], play['instance_id'], play['play_id'], game['name'], game['fake_name'], play['desc_id'], play['level_id'])

        zstates = play['zstates']
        states = core.VGDLParser.decompress(zstates)
        states = states['states'] # dummy dict

        core.VGDLParser.fMRI_replayGame(play['game_str'], play['level_str'], states)

