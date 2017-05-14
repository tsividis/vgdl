level="""
33333333333333333333
3                A 3
3              1G  3
3    7             3
3          333333333
3             8    3
3          6  8    2
3             8    3
33333333333333333333
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=LIGHTGREEN
		goal > ResourcePack color=LIGHTGREEN
		c2 > Missile color=PINK speed=1 orientation=RIGHT
		c7 > Resource color=RED
		c6 > ResourcePack color=BLACK
		c5 > ResourcePack color=GREEN
		c4 > RandomNPC color=LIGHTORANGE speed=0.4
	InteractionSet
		c2 c6 > stepBack
		c7 c6 > stepBack
		c4 c6 > stepBack
		goal c6 > stepBack
		c4 EOS > stepBack
		c5 EOS > stepBack
		c6 EOS > stepBack
		c5 c6 > stepBack
		c7 EOS > stepBack
		c2 EOS > stepBack
		goal EOS > stepBack
		goal avatar > killSprite
		avatar EOS > stepBack
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=goal limit=0 win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		1 > c2
		A > avatar
		8 > c3
		6 > c4
		3 > c6
		2 > c5
		7 > c7
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
