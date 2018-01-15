level="""
111111111111111111111111
1    2  0              1
1      1      1        1
1   1         11       1
1     1            1   1
12          1          1
1     1    1   1  1    1
1       1       1      1
1   1     1     1      1
12    2               21
111111111111111111111111
"""
game = """
BasicGame
	SpriteSet
		c3 > Chaser color=RED fleeing=True cooldown=1 stype=avatar
		c2 > ResourcePack color=DARKGRAY
		avatar > MovingAvatar color=DARKBLUE
	InteractionSet
		avatar c2 > stepBack
		c2 c2 > nothing
		c3 c3 > nothing
		avatar EOS > stepBack
		c3 avatar > killSprite
		c3 c2 > stepBack
		c2 EOS > stepBack
		c3 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		0 > avatar
		1 > c2
		2 > c3
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
