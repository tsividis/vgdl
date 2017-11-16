game = """
BasicGame
    SpriteSet
        background > Immovable color=LIGHTGRAY
        goomba > Missile orientation=LEFT color=BROWN speed=0.2 width=0.7 height=0.7
        goal > Immovable color=GREEN width=0.7 height=0.9
        key > Resource limit=1 color=GOLD width=0.7 height=0.9
        wall > Immovable color=BLACK
        ladder > Immovable color=YELLOW height=3.0
        rope > Immovable color=RED width=0.25
        floor > Immovable color=BLACK height=0.25
        avatar > MarioAvatar strength=15 physicstype=GravityPhysics color=WHITE width=0.75
        conveyor > Conveyor strength=3 height=0.25
    TerminationSet
        SpriteCounter stype=goal      win=True
        SpriteCounter stype=avatar      win=False
    InteractionSet
        avatar goomba > killSprite
        avatar EOS  > killSprite
        goomba EOS > killSprite
        avatar ladder > onLadder
        avatar rope > onRope
        
        goal avatar > killIfOtherHasMore resource=key
        key avatar > killSprite
        avatar key > changeResource resource=key value=1
        avatar wall > killIfTooFast speed=23
        avatar wall > wallStop
        goomba wall > wallBounce
        
        
        avatar conveyor > killIfTooFast speed=23
        avatar conveyor > conveySprite
        avatar conveyor > wallStop
        avatar floor > killIfTooFast speed=23
        avatar floor > wallStop
        goomba floor > wallBounce
    LevelMapping
        . > background
        w > background wall
        G > background goal
        1 > background goomba
        l > background ladder
        k > background key
        A > background avatar
        c > background conveyor
        r > background rope
        f > background floor
        F > background floor rope
"""



#ropeavatar offrope > transformTo stype=avatar
#avatar rope > transformTo stype=ropeavatar


level = """
wwwwwwwwwwwwwwwwwwwwwwwww
w.......................w
w.......................w
wG...........A..........w
wfffffff...flf...Fffffffw
wk..........l..$.r$.....w
w...........l..$.r$.....w
w..............$.r$.....w
wflff.....ccccc$..$.fflfw
w.l............$$$$...l.w
w.l...................l.w
w............1..........w
wwwwwwwwwwwwwwwwwwwwwwwww
"""

dims = (25,13)
pos = {}
pos['background'] = [(i,j) for i in range(dims[0]) for j in range(dims[1])]
pos['wall'] = [(i,j) for i in range(dims[0]) for j in range(dims[1]) if i in [0,dims[0]-1] or j in [0,dims[1]-1]]
pos['avatar'] = [(13,3)]
#pos['ladder'] = [(12,3.9),(12,4.9),(12,5.9),(2,7.9),(2,8.9),(2,9.9),(22,7.9),(22,8.9),(22,9.9)]
pos['ladder'] = [(12,3.75),(22,7.75),(2,7.75)]
pos['conveyor'] = [(10,8),(11,8),(12,8),(13,8),(14,8)]
pos['rope'] = [(17.375,i) for i in range(4,8)]
pos['key'] = [(1.5,5)]
#pos['key'] = [(22,7)]
pos['goal'] = [(1,3.1)]
#pos['goal'] = [(23,7.1)]
floor_locs = range(1,8)
floor_locs.extend(range(17,24))
floor_locs.extend([11,13])
pos['floor'] = [(i,4) for i in floor_locs]
pos['floor'].extend([(i,8) for i in [1,3,4,20,21,23]])
#pos['offrope'] = [(16.625,5),(16.625,6),(16.625,7),(16.625,8),(17.625,8),(17.625,7),(17.625,6),(17.625,5)]
#pos['goomba'] = [(13,11.3)]
positions = [dims,pos]
level_game_pairs = [[game, level]]
if __name__ == "__main__":

    from vgdl.core import VGDLParser
    '''
    dims = (25,13)
    pos = {}
    pos['background'] = [(i,j) for i in range(dims[0]) for j in range(dims[1])]
    pos['wall'] = [(i,j) for i in range(dims[0]) for j in range(dims[1]) if i in [0,dims[0]-1] or j in [0,dims[1]-1]]
    pos['avatar'] = [(13,3)]
    pos['ladder'] = [(12,4),(12,5),(12,6),(2,8),(2,9),(2,10),(22,8),(22,9),(22,10)]
    pos['conveyor'] = [(10,8),(11,8),(12,8),(13,8),(14,8)]
    pos['rope'] = [(17.375,i) for i in range(4,8)]
    #pos['key'] = [(1.5,5)]
    pos['key'] = [(22,7)]
    #pos['goal'] = [(1,3.1)]
    pos['goal'] = [(23,7.1)]
    floor_locs = range(1,8)
    floor_locs.extend(range(17,24))
    floor_locs.extend([11,13])
    pos['floor'] = [(i,4) for i in floor_locs]
    pos['floor'].extend([(i,8) for i in [1,3,4,20,21,23]])
    pos['offrope'] = [(16.625,5),(16.625,6),(16.625,7),(16.625,8),(17.625,8),(17.625,7),(17.625,6),(17.625,5)]
    #pos['goomba'] = [(13,11.3)]
    pos_set = [dims,pos]
    '''
    VGDLParser.playGame(game, None, positions = positions)
'''
game = """
BasicGame
    SpriteSet
        background > Immovable color=LIGHTGRAY
        offrope > Immovable color=LIGHTGRAY width=0.75
        goomba > Missile orientation=LEFT color=BROWN speed=0.2 width=0.7 height=0.7
        goal > Immovable color=GREEN width=0.7 height=0.9
        key > Resource limit=1 color=GOLD width=0.7 height=0.9
        wall > Immovable color=BLACK
        ladder > Immovable color=YELLOW height=0.25
        rope > Immovable color=RED width=0.25
        floor > Immovable color=BLACK height=0.25

        avatar > MarioAvatar strength=15 physicstype=GravityPhysics color=WHITE width=0.75
        ladderavatar > VerticalAvatar speed=0.3 color=WHITE width=0.8
        ropeavatar > RopeAvatar physicstype=ContinuousPhysics color=WHITE width=0.8

        conveyor > Conveyor strength=3 height=0.25


    TerminationSet
        SpriteCounter stype=goal      win=True
        MultiSpriteCounter stype1=avatar stype2=ladderavatar stype3=ropeavatar win=False

    InteractionSet

        avatar goomba > killSprite
        avatar EOS  > killSprite
        goomba EOS > killSprite
        ladderavatar goomba > killSprite

        
        goal avatar > killIfOtherHasMore resource=key
        key avatar > killSprite
        avatar key > changeResource resource=key value=1
        avatar wall > killIfTooFast speed=23
        avatar wall > wallStop
        ropeavatar wall > wallStop
        goomba wall > wallBounce
        avatar goal > stepBack
        
        avatar conveyor > killIfTooFast speed=23
        avatar conveyor > conveySprite
        avatar conveyor > wallStop

        avatar floor > killIfTooFast speed=23
        avatar floor > wallStop
        ropeavatar floor > wallStop
        goomba floor > wallBounce

        ladderavatar background > transformTo stype=avatar
        avatar ladder > transformTo stype=ladderavatar

        ropeavatar offrope > transformTo stype=avatar
        avatar rope > transformTo stype=ropeavatar


    LevelMapping
        . > background
        w > background wall
        G > background goal
        1 > background goomba
        l > background ladder
        k > background key
        A > background avatar
        c > background conveyor
        r > background rope
        $ > background offrope
        W > background wall offrope
        f > background floor
        F > background floor rope

"""

level = """
wwwwwwwwwwwwwwwwwwwwwwwww
w.......................w
w.......................w
wG...........A..........w
wfffffff...flf...Fffffffw
wk..........l..$.r$.....w
w...........l..$.r$.....w
w..............$.r$.....w
wflff.....ccccc$..$.fflfw
w.l............$$$$...l.w
w.l...................l.w
w............1..........w
wwwwwwwwwwwwwwwwwwwwwwwww
"""

dims = (25,13)
pos = {}
pos['background'] = [(i,j) for i in range(dims[0]) for j in range(dims[1])]
pos['wall'] = [(i,j) for i in range(dims[0]) for j in range(dims[1]) if i in [0,dims[0]-1] or j in [0,dims[1]-1]]
pos['avatar'] = [(13,3)]
pos['ladder'] = [(12,4),(12,5),(12,6),(2,8),(2,9),(2,10),(22,8),(22,9),(22,10)]
pos['conveyor'] = [(10,8),(11,8),(12,8),(13,8),(14,8)]
pos['rope'] = [(17.375,i) for i in range(4,8)]
pos['key'] = [(1.5,5)]
#pos['key'] = [(22,7)]
pos['goal'] = [(1,3.1)]
#pos['goal'] = [(23,7.1)]
floor_locs = range(1,8)
floor_locs.extend(range(17,24))
floor_locs.extend([11,13])
pos['floor'] = [(i,4) for i in floor_locs]
pos['floor'].extend([(i,8) for i in [1,3,4,20,21,23]])
pos['offrope'] = [(16.625,5),(16.625,6),(16.625,7),(16.625,8),(17.625,8),(17.625,7),(17.625,6),(17.625,5)]
#pos['goomba'] = [(13,11.3)]
positions = [dims,pos]
'''
# if __name__ == "__main__":

#     from vgdl.core import VGDLParser
#     '''
#     dims = (25,13)
#     pos = {}
#     pos['background'] = [(i,j) for i in range(dims[0]) for j in range(dims[1])]
#     pos['wall'] = [(i,j) for i in range(dims[0]) for j in range(dims[1]) if i in [0,dims[0]-1] or j in [0,dims[1]-1]]
#     pos['avatar'] = [(13,3)]
#     pos['ladder'] = [(12,4),(12,5),(12,6),(2,8),(2,9),(2,10),(22,8),(22,9),(22,10)]
#     pos['conveyor'] = [(10,8),(11,8),(12,8),(13,8),(14,8)]
#     pos['rope'] = [(17.375,i) for i in range(4,8)]
#     #pos['key'] = [(1.5,5)]
#     pos['key'] = [(22,7)]
#     #pos['goal'] = [(1,3.1)]
#     pos['goal'] = [(23,7.1)]
#     floor_locs = range(1,8)
#     floor_locs.extend(range(17,24))
#     floor_locs.extend([11,13])
#     pos['floor'] = [(i,4) for i in floor_locs]
#     pos['floor'].extend([(i,8) for i in [1,3,4,20,21,23]])
#     pos['offrope'] = [(16.625,5),(16.625,6),(16.625,7),(16.625,8),(17.625,8),(17.625,7),(17.625,6),(17.625,5)]
#     #pos['goomba'] = [(13,11.3)]
#     pos_set = [dims,pos]
#     '''
#     VGDLParser.playGame(game, None, positions = positions)
