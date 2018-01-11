
# level = """
# wwwwwwwww
# w  A b ww
# h       h
# p      ww
# wwwwwwhww
# """

# level = """
# wwwwwwwwwwww
# w          w
# w   Ab    hw
# w          w
# w  h    h  w
# wwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwww
# w     b    w
# w b Ab   bhw
# w b b b    w
# w  h    h  w
# wwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwww
# w     b    w
# w b Ab   bhw
# w b b b    w
# w       h  w
# wwwwwwwwwwww
# """

# level3 = """
# wwwwwwwww
# w  A    w
# p       g
# w b   w w
# wwwwgwhww
# """

# level = """
# wwwwwwwwwwwwwwwwwwww
# w  A             h w
# w                  w
# w                  w
# w            h     w
# w        p     wwwww
# w   p       p      w
# w       h      w  hw
# wwwwwwwwwwwwwwwwwwww
# """


# level = """
# wwwwwwwwwwwwwwwwwwww
# w         b      h w
# w         Ab       w
# w       bb b     b w
# w         b        w
# w        p     wwwww
# w   p       p      w
# w              w   w
# wwwwwwwwwwwwwwwwwwww
# """

level = """
wwwwwwwwwwwwwwwwwwww
w         b      h w
w         Ab       w
w          b   b b w
w         b     b  w
w        p     wwwww
w   p       p      w
w     h        w h w
wwwwwwwwwwwwwwwwwwww
"""

# level2 = """
# wwwwwwwwwwwwwwwwwwww
# w  A    w h  w     w
# w       w   w      w
# w       wwww       w
# w                  w
# w           p  w www
# w         b    w   w
# w              w  gw
# wwwwwwwwwwwwwwwwwwww
# """

# level3 = """
# wwwwwwwwwwwwwwwwwwww
# w  A         w    gw
# w         b        w
# w       wwww    b  w
# wp                 w
# wwwww       p  w www
# w  h      b    w   w
# w              w   w
# wwwwwwwwwwwwwwwwwwww
# """


game = """
BasicGame frame_rate=30
    SpriteSet
        avatar > MovingAvatar color=DARKBLUE
        box > Passive
            box1 > color=RED
            box2 > color=PINK
        mover > VGDLSprite
            rand > RandomNPC cooldown=10
                rand1 > color=LIGHTORANGE
                rand2 > color=BLUE
        wall > Immovable color=BLACK
        missile > Missile
            missile1 > color=YELLOW orientation=RIGHT
            missile2 > color=LIGHTBLUE orientation=RIGHT
        goal > Immovable color=GREEN
            # goal1 > color=GREEN
            # goal2 > color=PINK
        poison > Immovable color=WHITE
    LevelMapping
        w > wall   
        a > box1
        b > box2
        y > rand1
        z > rand2
        1 > missile1
        2 > missile2
        #g > goal1
        h > goal
        p > poison
    InteractionSet
        avatar wall > stepBack 
        mover wall > stepBack
        avatar poison > killSprite
        box avatar > bounceForward
        box goal > stepBack
        box box > stepBack
        box wall > stepBack
        avatar rand > killSprite
        rand wall > stepBack  
        missile wall > turn
        avatar missile > killSprite
        missile missile > reverseDirection
        mover avatar > undoAll
        mover mover > stepBack
        mover missile > stepBack
        mover box > stepBack
        goal avatar > changeScore value=100
        goal avatar > killSprite
    TerminationSet
        SpriteCounter stype=avatar  limit=0 win=False          
        SpriteCounter stype=goal limit=0 win=True
"""
"""
show agent killing a moving item.
same prediction should be highest for other moving items of same speed, then for non-moving items.
also vice-versa.
"""
if __name__ == "__main__":
    from vgdl.core import VGDLParser
    import random
    levels = [l for l in locals().keys() if 'level' in l]
    index = random.choice(range(len(levels)))
    VGDLParser.playGame(game, locals()[levels[index]])