from pymongo import MongoClient
import pprint

# see db_api.py

import json
import sys
import csv
from collections import defaultdict
from vgdl import core
from IPython import embed

# from https://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-from-json
#
def json_load_byteified(file_handle):
    return _byteify(
        json.load(file_handle, object_hook=_byteify),
        ignore_dicts=True
    )

def json_loads_byteified(json_text):
    return _byteify(
        json.loads(json_text, object_hook=_byteify),
        ignore_dicts=True
    )

def _byteify(data, ignore_dicts = False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [ _byteify(item, ignore_dicts=True) for item in data ]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {
            _byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
            for key, value in data.iteritems()
        }
    # if it's anything else, return it in its original form
    return data


# TODO hardcoded -- incompatible! investigate
sokoban_desc = '''
BasicGame square_size=20
         SpriteSet
             hole   > Immovable color=RED
             avatar > MovingAvatar color=DARKBLUE
             box    > Passive color=GREEN
             wall > Immovable color=DARKGRAY autotiling=True
         LevelMapping
             0 > hole
             1 > box
             w > wall
         InteractionSet
             avatar wall > stepBack
             box avatar  > bounceForward
             box wall > stepBack
             box box > stepBack
             avatar hole > nothing
             box hole    > killSprite
         box hole > scoreChange value=1
         TerminationSet
             SpriteCounter stype=box    limit=0 win=True
             Timeout  win=False'''


helper_desc = '''
BasicGame frame_rate=30
         SpriteSet
             avatar > MovingAvatar color=DARKBLUE cooldown=0
             mover > VGDLSprite
                 chaser > Chaser
                     chaser1 > stype=box1 color=ORANGE  cooldown=12
                     chaser2 > stype=box3 color=LIGHTBLUE cooldown=12
             wall > Immovable color=BLACK
             forcefield > Passive color=PURPLE
             box > Passive
                 box1 > color=WHITE
                 box2 > color=GREEN
                 box3 > color=YELLOW
         LevelMapping
             w > wall
             a > box1
             b > box2
             c > box3
             f > forcefield
             x > chaser1
             z > chaser2
             r > rand
             z > chaser2
             1 > missile1
             2 > missile2
         InteractionSet
             avatar wall > stepBack
             mover wall > stepBack
             box wall > stepBack
             rand wall > stepBack
             box1 avatar > bounceForward
             box1 box2 > stepBack
             box1 box1 > stepBack
             avatar chaser > nothing
             box2 avatar > killSprite
             box1 chaser > killSprite
             box1 rand > killSprite
             box1 box3 > nothing
             avatar box3 > nothing
             box3 chaser > killSprite
             box2 forcefield > nothing
             rand forcefield > stepBack
             forcefield rand > stepBack
             chaser forcefield > stepBack
             avatar forcefield > nothing
             avatar rand > nothing
             chaser wall > stepBack
             chaser box2 > stepBack
             missile EOS > wrapAround
             missile avatar > killSprite
             missile missile > reverseDirection
             mover mover > stepBack
         TerminationSet
         Timeout limit=600 win=False
             SpriteCounter stype=avatar  limit=0 win=False
             SpriteCounter stype=box1 limit=0 win=True bonus=10
'''


chase_desc = '''
BasicGame
         SpriteSet
             carcass > Immovable color=BROWN
             goat > stype=avatar
                 angry  > Chaser cooldown=8 color=GOLD
                 scared > Fleeing cooldown=3 color=RED
             avatar > MovingAvatar color=DARKBLUE
             wall > Immovable color=DARKGRAY
     
         InteractionSet
             angry   wall   > stepBack
             scared   wall   > stepBack
             angry scared > nothing
             scared scared > nothing
             angry angry > nothing
             carcass avatar > nothing
             avatar wall    > stepBack
             avatar angry > scoreChange=-1
             avatar  angry  > killSprite 
             angry carcass > nothing
             carcass scared > killSprite
             scared avatar > scoreChange=1
             scared avatar  > transformTo stype=carcass
             scared carcass > transformTo stype=angry
     
         LevelMapping
             0 > scared
             w > wall
     
         TerminationSet
         Timeout limit=600 win=False
             SpriteCounter stype=scared win=True bonus=10
             SpriteCounter stype=avatar win=False
'''



client = MongoClient('localhost', 27017)
db = client['heroku_7lzprs54']

#game_name = 'vgfmri2_helper'
game_name = 'vgfmri3_aliens'
game = db.games.find_one({'name': game_name})

desc = game['descs'][0]
level = game['levels'][0] 


'''
exp_id = 'ry44FBXnr'
#game_name = 'vgfmri2_sokoban' % TODO don't forget to change the game desc
game_name = 'vgfmri2_helper'
#game_name = 'vgfmri2_chase'


#entries = db.states.find({'exp_id': exp_id, 'game_name': game_name, 'game_round': '2'})
entries = db.states.find({'exp_id': exp_id, 'game_name': game_name})

states = []
for entry in entries:
    #pprint.pprint(entry)
    #s = json.loads(entry['game_real_states'])
    s = json_loads_byteified(entry['game_real_states'])
    states.extend(s)

#pprint.pprint(states)
#for state in states:  # TODO assert +1
#    print state['frame']

# assert the same
#game = entry['game_level']['game'] # desc
#game = sokoban_desc
game = helper_desc 
#game = chase_desc

level = entry['game_level']['level']  # level
game_name = entry['game_name']
'''



core.VGDLParser.playGame(desc, level, None, persist_movie=True, make_images=False, make_movie=True, movie_dir="videos/"+game_name, padding=10)



