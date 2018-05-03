level="""
33333333333333333333333333333333
3  0                           3
3     0            0      0    3
3       0                      3
3               0              3
3         5    2   4           3
3     0     0            1111113
3     0   0              1     3
333                  0   1     3
33333333333333333333333333333333
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=DARKGRAY
		c2 > ResourcePack color=PINK
		c6 > ResourcePack color=LIGHTBLUE
		c5 > Chaser color=LIGHTGREEN fleeing=False cooldown=1 stype=c4
		c4 > ResourcePack color=YELLOW
	InteractionSet
		c3 c5 > nothing
		c5 c3 > nothing
		c2 c4 > killSprite
		avatar c6 > nothing
		c4 c5 > killSprite
		avatar c3 > stepBack
		c2 c5 > nothing
		c5 c2 > nothing
		avatar EOS > stepBack
		c6 c2 > nothing
		c2 c6 > nothing
		c4 c6 > nothing
		c2 c2 > nothing
		c3 c3 > nothing
		c6 c3 > nothing
		c3 c6 > nothing
		c2 c3 > nothing
		c3 c2 > nothing
		avatar c5 > nothing
		c4 avatar > bounceForward
		c5 c5 > nothing
		c2 avatar > killSprite
		c4 c4 > nothing
		c5 EOS > stepBack
		c4 EOS > stepBack
		c4 c3 > stepBack
		c5 c6 > stepBack
		c3 EOS > stepBack
		c6 EOS > stepBack
		c2 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c5 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=c5 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		NoveltyTermination s1=c6 s2=EOS win=True
		NoveltyTermination s1=c6 s2=c2 win=True
		NoveltyTermination s1=c6 s2=c3 win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c4 limit=0 win=False
		SpriteCounter stype=c2 limit=0 win=True
	LevelMapping
		0 > c2
		1 > c6
		2 > avatar
		3 > c3
		4 > c4
		5 > c5
		9 > avatar c6
		b > c4 c6
		8 > avatar c5
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
