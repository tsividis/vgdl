level= """
wwwwwwwww
w  A    w
w    4  w
w 3  w2ww
w    w ww
wwwwwwwww
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > Immovable color=BROWN
		c2 > Immovable color=ORANGE
		c6 > ResourcePack color=GOLD
		c5 > Passive color=RED
	InteractionSet
		c3 avatar > bounceForward
		c5 avatar > bounceForward
		c6 avatar > bounceForward
		c2 avatar > killSprite
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		A > avatar
		1 > c2
		2 > c6
		3 > c3
		4 > c5
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
