from pymongo import MongoClient
import pprint
import random
from datetime import datetime

import json
import sys
import csv
from collections import defaultdict
from vgdl import core, agent
from IPython import embed
from vgdl.core import VGDLParser


chase_game = '''
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
        avatar angry > changeScore value=-1
        avatar  angry  > killSprite 
        angry carcass > nothing
        carcass scared > killSprite
        scared avatar > changeScore value=1
        scared avatar  > transformTo stype=carcass
        scared carcass > transformTo stype=angry

    LevelMapping
        0 > scared
        w > wall

    TerminationSet
        SpriteCounter stype=scared win=True 
        SpriteCounter stype=avatar win=False
'''

chase_level = '''
wwwwwwwwwwwwwwwwwwwwwwwwwwwwww
w.ww.........................w
wAww.......wwwwwww...........w
w.ww..................www....w
w............................w
w.............ww.............w
w.....w.......ww.............w
w.....w.......ww.......ww....w
w.....w.......wwwwww....w....w
w.....wwwwww.................w
w.....www.....0..............w
wwww....................wwwwww
w0..........w................w
w............................w
wwwwwwwwwwwwwwwwwwwwwwwwwwwwww
'''


chase_level = '''
wwwwwwww
w.w....w
wA.....w
w...0..w
w0.....w
wwwwwwww
'''


zelda_game = """
BasicGame
  SpriteSet         
    goal  > Immovable color=GREEN
    key   > Resource color=ORANGE limit=1
    sword > Flicker limit=5 singleton=True color=RED
    movable > 
      avatar  > ShootAvatar   stype=sword
    monster > Immovable color=PURPLE
  LevelMapping
    G > goal
    + > key        
    A > avatar
    1 > monster            
  InteractionSet
    movable wall  > stepBack
    goal avatar  > killSprite        
    monster sword > killSprite        
    avatar monster> killSprite
    key avatar    > collectResource scoreChange=1
    key avatar    > killSprite
  TerminationSet
    SpriteCounter stype=goal   win=True
    SpriteCounter stype=avatar win=False
"""



zelda_level = """
wwwwwwwwwwwww
wA       w  w
w  w        w
w   w   w +ww
www w1  wwwww
w       w G w
w 1        ww
w     1    ww
wwwwwwwwwwwww
"""


sokoban_game = '''
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
    box hole > changeScore value=1
    TerminationSet
        SpriteCounter stype=box    limit=0 win=True 
'''

sokoban_level = '''
wwwwwwwwww
w....0...w
w........w
w.A..1wwww
w........w
w..www1..w
w.....0..w
w........w
wwwwwwwwww
'''



#VGDLParser.playGame(chase_game, chase_level)
#VGDLParser.playGame(sokoban_game, sokoban_level)


level_game_pairs = [(chase_game, chase_level)]
level_game_pairs = [(sokoban_game, sokoban_level)]

level_game_pairs = [(zelda_game, zelda_level)]


agent = agent.Agent('full', None)
agent.testCurriculum(level_game_pairs=level_game_pairs)
