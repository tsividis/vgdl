level="""
4444444444444444444444
435   4    6       0 4
44  5 4      6       4
4     6      1  4   44
44444445        4   44
44            2      4
4    6    2        5 4
4     1              4
4         1          4
4444444444444444444444
"""
game = """
BasicGame
	SpriteSet
		goal > ResourcePack color=PINK
		wall > Immovable color=DARKGRAY
		poison3 > ResourcePack color=PURPLE
		poison2 > ResourcePack color=GOLD
		poison1 > ResourcePack color=ORANGE
		avatar > MovingAvatar color=DARKBLUE
		box1 > ResourcePack color=GREEN
		box2 > ResourcePack color=LIGHTBLUE
	InteractionSet
		avatar wall > stepBack
		avatar poison1 > killSprite
		box1 avatar > bounceForward
		poison2 box1 > bounceForward
		box1 box2 > nothing
		box2 avatar > killSprite
		poison1 box1 > killSprite
		avatar poison3 > killSprite
		avatar poison2 > killSprite
		goal avatar > killSprite
		poison2 box2 > stepBack
		poison1 wall > stepBack
		goal wall > stepBack
		poison3 wall > stepBack
		goal box1 > stepBack
		goal box2 > stepBack
		box1 wall > stepBack
		goal poison1 > stepBack
		poison2 wall > stepBack
		box2 wall > stepBack
		poison1 box2 > stepBack
		box1 box1 > stepBack
		goal poison2 > stepBack
	TerminationSet
		SpriteCounter stype=goal limit=0 win=True
		SpriteCounter stype=avatar limit=0 win=True
	LevelMapping
		0 > goal
		1 > box2
		2 > poison2
		3 > avatar
		4 > wall
		5 > box1
		6 > poison1
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
