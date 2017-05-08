level="""
33333333333333
3    A     5 3
3            3
3            3
3    5       3
3            3
3            3
3            3
3    G       3
33333333333333
"""
game = """
BasicGame
	SpriteSet
		laog > Resource color=GREEN
		goal > Resource color=GREEN
		wall > Immovable color=DARKGRAY
		avatar > MovingAvatar color=DARKBLUE
		c3 > Resource color=GREEN
		goal > Resource color=GREEN
		c2 > Chaser color=BLUE speed=0.4 fleeing=False
		c4 > Resource color=BLACK
	InteractionSet
		avatar c2 > killSprite
		c4 EOS > stepBack
		c2 c4 > stepBack
		goal EOS > stepBack
		avatar c4 > stepBack
		avatar EOS > stepBack
		c2 EOS > stepBack
		goal c4 > stepBack
		goal avatar > killSprite
		avatar EOS > stepBack
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=goal limit=0 win=True
	LevelMapping
		5 > c2
		A > avatar
		3 > c4
		2 > c3
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
