level="""
44444444444444444444
44           2    04
44 2  2    2       4
44   2  2     2    4
44      2    2     4
44   2  2  3   2   4
44444444444444444444
44                 4
44   b 8 b 8 b  8  4
446               74
44444444444444444444
4444444A444444444444
"""
game = """
BasicGame
	SpriteSet
		c8 > Missile color=LIGHTRED speed=0.5 orientation=LEFT
		avatar > MovingAvatar color=DARKBLUE
		c3 > Missile color=PINK speed=0.5 orientation=DOWN
		c2 > Portal color=BLUE stype=c6
		c7 > ResourcePack color=GREEN
		c6 > Portal color=LIGHTORANGE
		c5 > ResourcePack color=DARKGRAY
		c4 > RandomNPC color=BROWN cooldown=1
	InteractionSet
		c3 c5 > reverseDirection
		c6 c7 > killSprite
		c7 c6 > killSprite
		c8 c8 > nothing
		avatar c3 > killSprite
		c6 c8 > killSprite
		c8 c6 > killSprite
		c4 c8 > killSprite
		c8 c4 > killSprite
		avatar c6 > nothing
		c3 c4 > killSprite
		c4 c3 > killSprite
		c2 c5 > killSprite
		c5 c2 > killSprite
		c7 avatar > killSprite
		c2 c8 > killSprite
		c8 c2 > killSprite
		c5 c7 > killSprite
		c7 c5 > killSprite
		avatar EOS > stepBack
		c7 c8 > killSprite
		c8 c7 > killSprite
		c8 c5 > reverseDirection
		c2 c6 > killSprite
		c6 c2 > killSprite
		c8 c3 > nothing
		c4 c6 > killSprite
		c6 c4 > killSprite
		c3 c7 > killSprite
		c7 c3 > killSprite
		c2 c2 > killSprite
		c5 c6 > killSprite
		c6 c5 > killSprite
		c3 c3 > killSprite
		c2 c7 > killSprite
		c7 c2 > killSprite
		avatar c8 > killSprite
		c4 c7 > killSprite
		c7 c4 > killSprite
		c3 c6 > killSprite
		c6 c3 > killSprite
		c6 c6 > killSprite
		c2 c3 > killSprite
		c3 c2 > killSprite
		c7 c7 > killSprite
		avatar c5 > stepBack
		avatar c4 > killSprite
		c5 c5 > killSprite
		avatar c2 > teleportToExit
		c4 c4 > nothing
		c4 c2 > stepBack
		c8 EOS > stepBack
		c4 c5 > stepBack
		c4 EOS > stepBack
		c5 EOS > stepBack
		c7 EOS > stepBack
		c3 EOS > stepBack
		c6 EOS > stepBack
		c2 EOS > stepBack
	TerminationSet

		NoveltyTermination s1=avatar s2=EOS win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		0 > c2
		d > avatar c6
		2 > c4
		3 > avatar
		4 > c5
		6 > c6
		c > c8 c3
		7 > c7
		8 > c3
		e > c3 c5
		b > c8
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
