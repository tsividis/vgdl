level="""
33333333333333333333333333333333
3                              3
3                              3
3                              3
3                              3
3                              3
3   5                          3
3              2               3
333           4               03
33333333333333333333333333333333
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=DARKGRAY
		c2 > ResourcePack color=PINK
		c5 > Chaser color=LIGHTGREEN fleeing=False cooldown=1 stype=c4
		c4 > ResourcePack color=YELLOW
	InteractionSet
		c2 avatar > killSprite
		c2 c5 > nothing
		c5 c2 > nothing
		c2 c4 > nothing
		c4 c2 > nothing
		c4 c5 > killSprite
		c2 c3 > nothing
		c3 c2 > nothing
		c2 c2 > nothing
		avatar c5 > nothing
		c3 c3 > nothing
		avatar EOS > stepBack
		avatar c3 > stepBack
		c5 c5 > nothing
		c4 avatar > bounceForward
		c3 c5 > nothing
		c5 c3 > nothing
		c4 c4 > nothing
		c4 EOS > stepBack
		c5 EOS > stepBack
		c2 EOS > stepBack
		c3 EOS > stepBack
		c4 c3 > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=avatar win=True
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
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
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c4 limit=0 win=False
	LevelMapping
		0 > c2
		2 > avatar
		3 > c3
		4 > c4
		5 > c5
		8 > avatar c5
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
