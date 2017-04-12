

box_level = """

wwwwwwwwwwwww
w m      w  w
w2  1  3    w
w   A 1    gw
wwwn    wwwww
w c     w   w
w 1      4  w
w  2 c 3   ww
wwwwwwwwwwwww

"""

"""
'YELLOW'       > Missile   orientation=RIGHT speed=0.2
'GREY'         > Missile   orientation=RIGHT speed=0.2
"""

push_game = """
BasicGame
    SpriteSet





    InteractionSet





    
    TerminationSet


    
    LevelMapping
        m > 'YELLOW'
        G > 'GOLD'
        c > 'BLUE'
        1 > 'ORANGE'
        2 > 'PINK'
        3 > 'LIGHTBLUE'
        4 > 'RED'
        w > 'BLACK'
        A > 'DARKBLUE'

"""

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(frog_game, frog_level)    