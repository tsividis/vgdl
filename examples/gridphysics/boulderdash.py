'''
VGDL example: Boulder Dash.

@author: Julian Togelius and Tom Schaul
'''


# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwww
# w ..o.  .o.              w
# w ..oooo  .   A          w
# w...wwww.w               w
# w    xxx     E.          w
# wwwwwwwwwwwwwwwwwwwwwwwwww
# w                        w
# w                        w
# w                        w
# w                        w
# w                        w
# w                        w
# wwwwwwwwwwwwwwwwwwwwwwwwww
# """

# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwww
# w ..o.  .o.              w
# w x.oxx  o.   A          w
# w.x.wwwww.               w
# w x      .   E.          w
# wwwwwwwwwwwwwwwwwwwwwwwwww
# w                        w
# w                        w
# w                        w
# w                        w
# w                        w
# w                        w
# wwwwwwwwwwwwwwwwwwwwwwwwww
# """


# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwww
# w ..o.xx.o.  w           w
# w ..oooooo. Aw           w
# w...wxxx..   w           w
# wx   w      Ew           w
# wwwwwwwwwwwwwwwwwwwwwwwwww
# w                        w
# w                        w
# w                        w
# w                        w
# w                        w
# w                        w
# wwwwwwwwwwwwwwwwwwwwwwwwww
# """


 ##the level we were testing.
# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwww
# w ..o.xx.o.              w
# w ..oooooo.   A          w
# w....xxx..               w
# wx           E.          w
# wwwwwwwwwwwwwwwwwwwwwwwwww
# w                        w
# w                        w
# w                        w
# w                        w
# w                        w
# w                        w
# wwwwwwwwwwwwwwwwwwwwwwwwww
# """


# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwww
# w   o.xx.o      o  xoxx. w
# w   oooooo      . o..o.. w
# w   .xxx..       o.oxoo.ow
# wx  .....        oxo...oow
# wwwwwwwwww       .o.  wxxw
# wb .  co.        ..   wxxw
# w  .  ..   Ao....o    wxxw
# wooo.....   .    .    w..w
# w.... .x....wwwwx x.oow  w
# w    ....x..ooxxo ....w  w
# w    .E.    .....        w
# wwwwwwwwwwwwwwwwwwwwwwwwww
# """


# level = """
# wwwwwwwwwwwwwwwwwwwwwwwwww
# w...o.xx.o......o..xoxx..w
# w...oooooo........o..o...w
# w....xxx.........o.oxoo.ow
# wx...............oxo...oow
# wwwwwwwwww........o...wxxw
# wb ...co..............wxxw
# w  ........Ao....o....wxxw
# wooo............. ....w..w
# w......x....wwwwx x.oow..w
# wc  .....x..ooxxo ....w..w
# w   ..E..........b     ..w
# wwwwwwwwwwwwwwwwwwwwwwwwww
# """


# level0 = """
# wwwwwwwwwwwwwwwwwwwwwwwwww
# w...o.xx.o......o..xoxx..w
# w...oooooo........o..o...w
# w....xxx.........o.oxoo.ow
# wx...............oxo...oow
# wwwwwwwwww........o...wxxw
# wb ...co..............wxxw
# w  ........Ao....o....wxxw
# wooo............. ....w..w
# w......x....wwwwx x.oow..w
# wc  .....x....xxo ....w..w
# w   ..E..........b     ..w
# wwwwwwwwwwwwwwwwwwwwwwwwww
# """


# level = """
# wwwwwwww
# wwxo   w
# ww    Aw
# w w    w
# w.     w
# w.     w
# wE     w
# wwwwwwww
# """

# level0 = """
# wwwwwwww
# wwxo   w
# ww....Aw
# w w....w
# w.x....w
# w......w
# wE.....w
# wwwwwwww
# """

level0 = """
wwwwwwwwwwwwwwwwwwwwwwwwww
wwxxx                 w  w
www.                  wx w
w w                   wxww
w                     wx w
w   . .               wE w
w                     wA w
wwwwwwwwwwwwwwwwwwwwwwwwww
"""

level1 = """
wwwwwwwwwwwwwwwwwwwwwwwwww
wwxxx                    w
www.                    Ew
w w                     ww
w                        w
w                        w
w                      A w
wwwwwwwwwwwwwwwwwwwwwwwwww
"""

# level1 = """
# wwwwwwwwwwwwwwwwwwwwwwwwww
# w.................w      w
# wwxo............oxw      w
# ww............... w      w
# w w..A......E....w       w
# wwwwwwwwwwwwwwwwww       w
# w                        w
# w                        w
# w                        w
# w                        w
# w                        w
# w                        w
# w                        w
# wwwwwwwwwwwwwwwwwwwwwwwwww
# """

# level1 = """
# wwwwwwwwwww
# wwxo....oxw
# ww....... w
# w w..A...ww
# wwwwwwwwwww
# """

# level1 = """
# wwwwwwwwwww
# wwxo....oxw
# ww....... w
# w w......ww
# wxo.A...oxw
# w.....x...w
# ww ..... ww
# wwwwwwwwwww
# """

game = """
BasicGame
	SpriteSet
		dirt > Immovable color=BROWN
		exitdoor > Immovable color=GREEN
		diamond > Resource color=YELLOW limit=3 shrinkfactor=0.25
		boulder > Missile orientation=DOWN color=DARKGRAY speed=0.2
		avatar  > ShootAvatar   stype=sword
		crab > RandomNPC cooldown=5 color=RED
		butterfly > RandomNPC cooldown=5 color=PINK
		wall > Immovable color=BLACK
		sword > Flicker color=BLUE limit=0 singleton=True
	LevelMapping
		. > dirt
		E > exitdoor
		o > boulder
		x > diamond
		c > crab
		b > butterfly
		w > wall
		s > sword
	InteractionSet
		dirt sword  > killSprite
		dirt avatar > killSprite
		avatar diamond > changeResource resource=diamond value=1
		diamond avatar > killSprite
		diamond avatar > changeScore value=5
		# avatar diamond > collectResource
		avatar wall > stepBack
		avatar boulder > stepBack
		crab wall > stepBack
		crab boulder > stepBack
		butterfly wall > stepBack
		butterfly boulder > stepBack
		avatar boulder > killIfFromAbove
		avatar butterfly > killSprite
		avatar crab > killSprite
		boulder dirt > stepBack
		boulder wall > stepBack
		boulder diamond > stepBack
		boulder boulder > stepBack
		crab dirt > stepBack
		crab diamond > stepBack
		butterfly dirt > stepBack
		butterfly diamond > stepBack
		crab butterfly > killSprite
		wall sword > nothing
		boulder sword > nothing
		sword boulder > nothing
		boulder sword > nothing
		diamond sword > nothing
		sword avatar > nothing
		sword sword > nothing
		wall dirt > nothing
		butterfly crab > transformTo stype=diamond scoreChange=1
		#exitdoor avatar > killIfOtherHasMore resource=diamond limit=9 #scoreChange=100
		exitdoor boulder > nothing
		exitdoor sword > nothing
		exitdoor avatar > nothing
		exitdoor avatar > killIfOtherHasMore resource=diamond limit=3 #scoreChange=100
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=exitdoor limit=0 win=True

"""

level_game_pairs = [[game, level0], [game,level1]]

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    import random, sys, time
    import numpy as np
    import csv
    from IPython import embed

    levels = [l for l in locals().keys() if 'level' in l and len(l)<8]
    if len(sys.argv)==2:
        index = int(sys.argv[1])
        VGDLParser.playGame(*level_game_pairs[index])
    else:
        # index = random.choice(range(len(level_game_pairs)))
        for index, level in enumerate(level_game_pairs):
            wins = 0
            while wins<2:
                VGDLParser.playGame(*level)
                time.sleep(1)
                data = np.load("temp_data.npy")
                win = data[2]
                if win:
                    wins+=1
                levels_won = index*2 + wins
                # Save in format [subect, condition, gamename, levels won, steps taken, score, time elapsed]
                row = ['human', 'no_score', 'expt_preconditions', levels_won, data[1], data[3], data[0]]

                filename = "human_data.csv"
                f = open(filename, 'a+') ##append, but also read.
                g = open(filename, 'r')
                writer = csv.writer(f)
                if len(g.readlines())==0:
                    writer.writerow(('subject', 'condition', 'gameName', 'levels_won', 'steps', 'score', 'time'))
                writer.writerow(row)
                f.close()
                g.close()