level="""
44444444444444444444
443  4   b    46  74
449 14  8     45   4
444444      9 444444
44     4 2      4 94
44b    4444444    44
44   2  5   b      4
444444   8 444     4
44         1       4
444404        5  444
44444444444444444444
44444444444444444444
"""
game = """
BasicGame
	SpriteSet
		c9 > RandomNPC color=ORANGE speed=1.8 cooldown=10
		c8 > RandomNPC color=GREEN speed=1.8 cooldown=10
		avatar > MovingAvatar color=DARKBLUE
		c3 > Missile color=PINK speed=0.5 orientation=UP cooldown=1
		c2 > RandomNPC color=BLUE speed=1.8 cooldown=10
		c11 > RandomNPC color=BROWN speed=0.3 cooldown=1
		c10 > Missile color=LIGHTRED speed=0.5 orientation=LEFT cooldown=1
		c7 > RandomNPC color=LIGHTORANGE speed=1.8 cooldown=10
		c6 > RandomNPC color=LIGHTGREEN speed=1.8 cooldown=10
		c5 > RandomNPC color=DARKGRAY speed=1.8 cooldown=10
		c4 > RandomNPC color=LIGHTBLUE speed=1.8 cooldown=10
	InteractionSet
		c2 avatar > killSprite
		c6 c7 > nothing
		c7 c6 > nothing
		c11 avatar > killSprite
		c8 c8 > nothing
		c2 c4 > nothing
		c4 c2 > nothing
		c4 c8 > nothing
		c8 c4 > nothing
		c6 c11 > nothing
		c11 c6 > nothing
		c2 c10 > nothing
		c10 c2 > nothing
		c6 avatar > killSprite
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
		c3 avatar > killSprite
		c8 c9 > nothing
		c9 c8 > nothing
		c2 c5 > nothing
		c5 c2 > nothing
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
		c9 c11 > nothing
		c11 c9 > nothing
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
		c10 c10 > nothing
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
		c11 c3 > nothing
		c3 c6 > nothing
		c6 c3 > nothing
		c6 c6 > nothing
		c10 avatar > killSprite
		c2 c3 > nothing
		c3 c2 > nothing
		c7 c7 > nothing
		c7 c11 > nothing
		c11 c7 > nothing
		avatar c5 > stepBack
		c4 avatar > killSprite
		c5 c5 > nothing
		c9 avatar > killSprite
		c4 c4 > nothing
		c2 c11 > nothing
		c11 c2 > nothing
		c6 c10 > nothing
		c10 c6 > nothing
		c8 EOS > stepBack
		c11 c5 > stepBack
		c5 EOS > stepBack
		c7 EOS > stepBack
		c10 EOS > stepBack
		c3 EOS > stepBack
		c11 EOS > stepBack
		c6 EOS > stepBack
		c9 EOS > stepBack
		c2 EOS > stepBack
		c4 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=avatar win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c10 win=True
		NoveltyTermination s1=c4 s2=avatar win=True
		NoveltyTermination s1=c6 s2=avatar win=True
		NoveltyTermination s1=c7 s2=avatar win=True
		NoveltyTermination s1=c8 s2=avatar win=True
		NoveltyTermination s1=c9 s2=avatar win=True
		NoveltyTermination s1=c10 s2=avatar win=True
		NoveltyTermination s1=c10 s2=c10 win=True
		NoveltyTermination s1=c11 s2=avatar win=True
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
		2 > c11
		3 > avatar
		4 > c5
		5 > c6
		6 > c7
		7 > c8
		8 > c3
		9 > c9
		b > c10
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
