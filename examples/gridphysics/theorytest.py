level="""
4444444444444444444
4   4 b      46  74
49 14   2    45   4
44444  8   93444444
4     4        4 94
4 b2  4444444    44
4      5   b      4
44444     444     4
4         1       4
44404   8    5  444
4444444444444444444
"""
game = """
BasicGame
	SpriteSet
		c9 > ResourcePack color=GREEN
		c8 > ResourcePack color=LIGHTORANGE
		avatar > MovingAvatar color=DARKBLUE
		c3 > Portal color=LIGHTBLUE stype=c10
		c2 > Missile color=PINK speed=0.5 orientation=DOWN cooldown=1
		c11 > Missile color=LIGHTRED speed=0.5 orientation=LEFT cooldown=1
		c10 > Portal color=ORANGE
		c7 > ResourcePack color=LIGHTGREEN
		c6 > ResourcePack color=DARKGRAY
		c5 > Missile color=BROWN speed=0.8 orientation=DOWN cooldown=7
		c4 > ResourcePack color=BLUE
	InteractionSet
		c2 avatar > killSprite
		c6 c7 > nothing
		c7 c6 > nothing
		avatar c11 > killSprite
		c8 c8 > nothing
		avatar c3 > teleportToExit
		c2 c4 > nothing
		c4 c2 > nothing
		c4 c8 > nothing
		c8 c4 > nothing
		c11 c6 > reverseDirection
		c2 c10 > nothing
		c10 c2 > nothing
		c10 c11 > nothing
		c11 c10 > nothing
		c7 c9 > nothing
		c9 c7 > nothing
		c4 c5 > nothing
		c5 c4 > nothing
		c5 c9 > nothing
		c9 c5 > nothing
		c3 c5 > nothing
		c5 c3 > nothing
		c3 c4 > nothing
		c4 c3 > nothing
		avatar c6 > stepBack
		c8 c9 > nothing
		c9 c8 > nothing
		c6 c9 > nothing
		c9 c6 > nothing
		c3 c9 > nothing
		c9 c3 > nothing
		c4 c9 > nothing
		c9 c4 > nothing
		c3 c10 > nothing
		c10 c3 > nothing
		c7 c10 > nothing
		c10 c7 > nothing
		c7 avatar > killSprite
		c2 c8 > nothing
		c8 c2 > nothing
		c8 c10 > nothing
		c10 c8 > nothing
		c5 c7 > nothing
		c7 c5 > nothing
		c5 c11 > nothing
		avatar EOS > stepBack
		c7 c8 > nothing
		c8 c7 > nothing
		c5 c8 > nothing
		c8 c5 > nothing
		c4 c10 > nothing
		c10 c4 > nothing
		c6 c8 > nothing
		c8 c6 > nothing
		c9 c11 > nothing
		c11 c9 > nothing
		c2 c6 > reverseDirection
		c3 c8 > nothing
		c8 c3 > nothing
		c4 c6 > nothing
		c6 c4 > nothing
		c3 c7 > nothing
		c7 c3 > nothing
		c2 c9 > nothing
		c9 c2 > nothing
		c9 c10 > nothing
		c10 c9 > nothing
		c9 c9 > nothing
		c2 c2 > nothing
		c4 c11 > nothing
		c11 c4 > nothing
		c3 c3 > nothing
		c10 c10 > nothing
		c11 c11 > nothing
		c5 c2 > nothing
		c8 c11 > nothing
		c11 c8 > nothing
		c2 c7 > nothing
		c7 c2 > nothing
		c8 avatar > killSprite
		c4 c7 > nothing
		c7 c4 > nothing
		c3 c11 > nothing
		c11 c3 > nothing
		c3 c6 > nothing
		c6 c3 > nothing
		c6 c6 > nothing
		avatar c10 > nothing
		c2 c3 > nothing
		c3 c2 > nothing
		c7 c7 > nothing
		c7 c11 > nothing
		avatar c5 > killSprite
		c4 avatar > killSprite
		c5 c5 > nothing
		c9 avatar > killSprite
		c4 c4 > nothing
		c11 c2 > nothing
		c6 c10 > nothing
		c10 c6 > nothing
		c8 EOS > stepBack
		c5 EOS > stepBack
		c5 c6 > stepBack
		c7 EOS > stepBack
		c10 EOS > stepBack
		c5 c10 > stepBack
		c3 EOS > stepBack
		c11 EOS > stepBack
		c6 EOS > stepBack
		c9 EOS > stepBack
		c2 EOS > stepBack
		c4 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=avatar win=True
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c2 s2=c7 win=True
		NoveltyTermination s1=c2 s2=c8 win=True
		NoveltyTermination s1=c2 s2=c9 win=True
		NoveltyTermination s1=c2 s2=c10 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c3 s2=c6 win=True
		NoveltyTermination s1=c3 s2=c7 win=True
		NoveltyTermination s1=c3 s2=c8 win=True
		NoveltyTermination s1=c3 s2=c9 win=True
		NoveltyTermination s1=c3 s2=c10 win=True
		NoveltyTermination s1=c3 s2=c11 win=True
		NoveltyTermination s1=c4 s2=avatar win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c5 win=True
		NoveltyTermination s1=c4 s2=c6 win=True
		NoveltyTermination s1=c4 s2=c7 win=True
		NoveltyTermination s1=c4 s2=c8 win=True
		NoveltyTermination s1=c4 s2=c9 win=True
		NoveltyTermination s1=c4 s2=c10 win=True
		NoveltyTermination s1=c4 s2=c11 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c5 s2=c7 win=True
		NoveltyTermination s1=c5 s2=c8 win=True
		NoveltyTermination s1=c5 s2=c9 win=True
		NoveltyTermination s1=c6 s2=c6 win=True
		NoveltyTermination s1=c6 s2=c7 win=True
		NoveltyTermination s1=c6 s2=c8 win=True
		NoveltyTermination s1=c6 s2=c9 win=True
		NoveltyTermination s1=c6 s2=c10 win=True
		NoveltyTermination s1=c7 s2=avatar win=True
		NoveltyTermination s1=c7 s2=c7 win=True
		NoveltyTermination s1=c7 s2=c8 win=True
		NoveltyTermination s1=c7 s2=c9 win=True
		NoveltyTermination s1=c7 s2=c10 win=True
		NoveltyTermination s1=c8 s2=avatar win=True
		NoveltyTermination s1=c8 s2=c8 win=True
		NoveltyTermination s1=c8 s2=c9 win=True
		NoveltyTermination s1=c8 s2=c10 win=True
		NoveltyTermination s1=c8 s2=c11 win=True
		NoveltyTermination s1=c9 s2=avatar win=True
		NoveltyTermination s1=c9 s2=c9 win=True
		NoveltyTermination s1=c9 s2=c10 win=True
		NoveltyTermination s1=c9 s2=c11 win=True
		NoveltyTermination s1=c10 s2=c10 win=True
		NoveltyTermination s1=c10 s2=c11 win=True
		NoveltyTermination s1=c11 s2=c11 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=c5 s2=EOS win=True
		NoveltyTermination s1=c6 s2=EOS win=True
		NoveltyTermination s1=c7 s2=EOS win=True
		NoveltyTermination s1=c8 s2=EOS win=True
		NoveltyTermination s1=c9 s2=EOS win=True
		NoveltyTermination s1=c10 s2=EOS win=True
		NoveltyTermination s1=c11 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		0 > c4
		1 > c3
		h > avatar c10
		2 > c5
		3 > avatar
		4 > c6
		5 > c7
		6 > c8
		d > c11 c2
		7 > c9
		8 > c2
		c > c2 c6
		i > c11 c7
		9 > c10
		b > c11
		f > c11 c6
		e > c11 c5
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
