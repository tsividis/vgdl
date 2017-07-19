'''
VGDL example: Boulder Dash.

@author: Julian Togelius and Tom Schaul
'''

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
level = """
wwwwwwww
wwxo   w
ww....Aw
w w....w
w.x....w
w......w
wE.....w
wwwwwwww
"""

game = """
BasicGame
	SpriteSet
		sword > Flicker color=LIGHTGRAY limit=1 singleton=True
		dirt > Immovable color=BROWN
		exitdoor > Immovable color=GREEN
		diamond > Resource color=YELLOW limit=10 shrinkfactor=0.25
		boulder > Missile orientation=DOWN color=DARKGRAY speed=0.2
		moving >
			avatar  > ShootAvatar   stype=sword
			enemy > RandomNPC cooldown=5
				crab > color=RED
				butterfly > color=PINK
		wall > Immovable color=BLACK
	LevelMapping
		. > dirt
		E > exitdoor
		o > boulder
		x > diamond
		c > crab
		b > butterfly
		w > wall
	InteractionSet
		dirt sword  > killSprite
		dirt avatar > killSprite

		diamond avatar > collectResource scoreChange=5
		diamond avatar > killSprite
		moving wall > stepBack
		moving boulder > stepBack
		avatar boulder > killIfFromAbove
		avatar butterfly > killSprite
		avatar crab > killSprite
		boulder dirt > stepBack
		boulder wall > stepBack
		boulder boulder > stepBack
		boulder diamond > stepBack
		enemy dirt > stepBack
		enemy diamond > stepBack
		crab butterfly > killSprite

		butterfly crab > transformTo stype=diamond scoreChange=1
		#exitdoor avatar > killIfOtherHasMore resource=diamond limit=9 scoreChange=100
		exitdoor avatar > killIfOtherHasMore resource=diamond limit=2 scoreChange=100

	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=exitdoor limit=0 win=True

"""

level_game_pairs = [[game, level]]


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)