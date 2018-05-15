level="""
4444444444444444444
43  4  b     46  74
49 14        45   4
44444  8   9 444444
4     42       4 94
4 2 b 4444444    44
4      58   b     4
44444     444     4
4         1       4
44404        5  444
4444444444444444444
"""
game = """
BasicGame
	SpriteSet
		c9 > Missile color=PINK speed=0.5 orientation=UP cooldown=1
		c8 > ResourcePack color=GREEN
		avatar > MovingAvatar color=DARKBLUE
		c3 > Missile color=BROWN speed=1.8 orientation=RIGHT cooldown=6
		c2 > ResourcePack color=BLUE
		c11 > Missile color=LIGHTRED speed=0.5 orientation=LEFT cooldown=1
		c10 > Portal color=ORANGE
		c7 > ResourcePack color=LIGHTORANGE
		c6 > ResourcePack color=LIGHTGREEN
		c5 > ResourcePack color=DARKGRAY
		c4 > Portal color=LIGHTBLUE stype=c10
	InteractionSet
		c2 avatar > killSprite
		c6 c7 > nothing
		c7 c6 > nothing
		c11 avatar > killSprite
		c8 c8 > nothing
		c2 c4 > nothing
		c4 c2 > nothing
		c11 c9 > nothing
		c4 c8 > nothing
		c8 c4 > nothing
		c6 c11 > nothing
		c2 c10 > nothing
		c10 c2 > nothing
		c6 avatar > killSprite
		c10 c11 > nothing
		c11 c10 > nothing
		c7 c9 > nothing
		c9 c7 > nothing
		c3 c9 > nothing
		c4 c5 > nothing
		c5 c4 > nothing
		c9 c5 > reverseDirection
		c7 c10 > nothing
		c10 c7 > nothing
		c3 avatar > killSprite
		c8 c9 > nothing
		c9 c8 > nothing
		c2 c5 > nothing
		c5 c2 > nothing
		c10 c10 > nothing
		c4 c9 > nothing
		c9 c4 > nothing
		c3 c10 > nothing
		c10 c3 > nothing
		c7 avatar > killSprite
		c2 c8 > nothing
		c8 c2 > nothing
		c8 c10 > nothing
		c10 c8 > nothing
		c5 c7 > nothing
		c7 c5 > nothing
		c11 c5 > reverseDirection
		avatar EOS > stepBack
		c3 c4 > nothing
		c4 c3 > nothing
		c5 c8 > nothing
		c8 c5 > nothing
		c4 c10 > nothing
		c10 c4 > nothing
		c8 avatar > killSprite
		c6 c8 > nothing
		c8 c6 > nothing
		c2 c6 > nothing
		c6 c2 > nothing
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
		c5 c6 > nothing
		c6 c5 > nothing
		c4 c11 > nothing
		c11 c4 > nothing
		c3 c3 > nothing
		c5 c10 > nothing
		c10 c5 > nothing
		c11 c11 > nothing
		c6 c9 > nothing
		c9 c6 > nothing
		c8 c11 > nothing
		c11 c8 > nothing
		c2 c7 > nothing
		c7 c2 > nothing
		c7 c8 > nothing
		c8 c7 > nothing
		c4 c7 > nothing
		c7 c4 > nothing
		c3 c11 > nothing
		c3 c6 > nothing
		c6 c3 > nothing
		c6 c6 > nothing
		avatar c10 > nothing
		c2 c3 > nothing
		c3 c2 > nothing
		c7 c7 > nothing
		c7 c11 > nothing
		c11 c7 > nothing
		avatar c5 > stepBack
		avatar c4 > teleportToExit
		c5 c5 > nothing
		c9 avatar > killSprite
		c4 c4 > nothing
		c2 c11 > nothing
		c11 c2 > nothing
		c6 c10 > nothing
		c10 c6 > nothing
		c8 EOS > stepBack
		c5 EOS > stepBack
		c11 EOS > stepBack
		c7 EOS > stepBack
		c3 c5 > stepBack
		c10 EOS > stepBack
		c3 EOS > stepBack
		c6 EOS > stepBack
		c9 EOS > stepBack
		c2 EOS > stepBack
		c4 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=avatar win=True
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c2 s2=c5 win=True
		NoveltyTermination s1=c2 s2=c6 win=True
		NoveltyTermination s1=c2 s2=c7 win=True
		NoveltyTermination s1=c2 s2=c8 win=True
		NoveltyTermination s1=c2 s2=c9 win=True
		NoveltyTermination s1=c2 s2=c10 win=True
		NoveltyTermination s1=c2 s2=c11 win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c6 win=True
		NoveltyTermination s1=c3 s2=c7 win=True
		NoveltyTermination s1=c3 s2=c8 win=True
		NoveltyTermination s1=c3 s2=c10 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c5 win=True
		NoveltyTermination s1=c4 s2=c6 win=True
		NoveltyTermination s1=c4 s2=c7 win=True
		NoveltyTermination s1=c4 s2=c8 win=True
		NoveltyTermination s1=c4 s2=c9 win=True
		NoveltyTermination s1=c4 s2=c10 win=True
		NoveltyTermination s1=c4 s2=c11 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c5 s2=c6 win=True
		NoveltyTermination s1=c5 s2=c7 win=True
		NoveltyTermination s1=c5 s2=c8 win=True
		NoveltyTermination s1=c5 s2=c10 win=True
		NoveltyTermination s1=c6 s2=avatar win=True
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
		NoveltyTermination s1=c7 s2=c11 win=True
		NoveltyTermination s1=c8 s2=avatar win=True
		NoveltyTermination s1=c8 s2=c8 win=True
		NoveltyTermination s1=c8 s2=c9 win=True
		NoveltyTermination s1=c8 s2=c10 win=True
		NoveltyTermination s1=c8 s2=c11 win=True
		NoveltyTermination s1=c9 s2=avatar win=True
		NoveltyTermination s1=c9 s2=c9 win=True
		NoveltyTermination s1=c9 s2=c10 win=True
		NoveltyTermination s1=c10 s2=c10 win=True
		NoveltyTermination s1=c10 s2=c11 win=True
		NoveltyTermination s1=c11 s2=avatar win=True
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
		0 > c2
		1 > c4
		e > avatar c10
		2 > c3
		3 > avatar
		4 > c5
		5 > c6
		6 > c7
		d > c11 c9
		7 > c8
		8 > c9
		c > c9 c5
		j > c11 c6
		9 > c10
		b > c11
		h > c3 c9
		i > c11 c5
		f > c11 c3
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
