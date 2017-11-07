
level="""
44444444444444444444
44   4  8 b3  46  74
449 14        45   4
444444      9 444444
44     4  2     4 94
44 2  b4444444    44
44    b 5          4
444444     444     4
44       8 1       4
444404        5  444
44444444444444444444
44444444444444444444
"""

game = """

BasicGame
	SpriteSet
		c9 > Portal color=ORANGE
		c8 > ResourcePack color=GREEN
		c1 > MovingAvatar color=DARKBLUE
		c3 > Missile color=PINK speed=0.5 orientation=DOWN cooldown=1
		c2 > ResourcePack color=BLUE
		c11 > Portal color=LIGHTBLUE stype=c9
		c10 > Missile color=LIGHTRED speed=0.5 orientation=LEFT cooldown=1
		c7 > ResourcePack color=LIGHTORANGE
		c6 > ResourcePack color=LIGHTGREEN
		c5 > ResourcePack color=DARKGRAY
		c4 > RandomNPC color=BROWN speed=0.3 cooldown=1
	InteractionSet
		c2 c1 > killSprite
		c1 c11 > teleportToExit
		c3 c1 > killSprite
		c1 c6 > killSprite
		c7 c1 > killSprite
		c1 EOS > stepBack
		c3 c5 > reverseDirection
		c10 c5 > reverseDirection
		c8 c1 > killSprite
		c10 c1 > killSprite
		c1 c5 > stepBack
		c4 c1 > killSprite
	TerminationSet
		SpriteCounter stype=c1 limit=0 win=False
		SpriteCounter stype=c6 limit=0 win=True

"""

if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
