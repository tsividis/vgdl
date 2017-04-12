level="""
0000000000000
0A    0     0
0     0     0
000 000     1
0     0     0
0G          0
0000000000000
"""
game = """
BasicGame
	SpriteSet
		laog > OrientedSprite color=RED
		goal > OrientedSprite color=RED
		wall > Immovable color=DARKGRAY
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=BLACK
		c2 > Resource color=GREEN
		c5 > VGDLSprite color=ENDOFSCREEN
		c4 > OrientedSprite color=RED
		goal > OrientedSprite color=RED
	InteractionSet
		c5 avatar > killSprite
		c2 avatar > killSprite
		avatar c3 > stepBack
		goal avatar > killSprite
		avatar EOS > stepBack
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=goal limit=0 win=True
	LevelMapping
		A > avatar
		1 > c2
		0 > c3
		2 > c4
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
