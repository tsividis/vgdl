level="""
333333333333333333
3 4 0   3    5   3
3   0   3 2  33333
3 1 0         0  3
333333333333333333
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=PINK
		c2 > ResourcePack color=ORANGE
		c6 > ResourcePack color=GOLD speed=1.2 orientation=LEFT cooldown=4
		c5 > ResourcePack color=BLACK speed=1.3 orientation=DOWN cooldown=10
		c4 > ResourcePack color=WHITE
	InteractionSet
		c2 avatar > nothing
		c2 c4 > nothing
		c4 c2 > nothing
		c6 avatar > killSprite
		c4 c5 > nothing
		c5 c4 > nothing
		c3 c5 > bounceForward
		c5 c3 > nothing
		c3 c4 > nothing
		c4 c3 > nothing
		c2 c5 > nothing
		c5 c2 > nothing
		c4 EOS > bounceForward
		avatar EOS > reverseDirection
		c3 avatar > reverseDirection
		c2 c6 > turnAround
		c6 c2 > bounceForward
		c4 c6 > nothing
		c6 c4 > nothing
		c2 c2 > nothing
		c6 c5 > killSprite
		c5 c6 > nothing
		c3 c3 > bounceForward
		c6 c3 > nothing
		c6 c6 > bounceForward
		c2 c3 > nothing
		c3 c2 > wrapAround
		c5 avatar > bounceForward
		c4 avatar > wrapAround
		c5 c5 > reverseDirection
		c2 EOS > turnAround
		c5 EOS > stepBack
		c3 EOS > stepBack
		c3 c6 > stepBack
		c6 EOS > stepBack
		c4 c4 > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=avatar win=True
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c2 s2=c5 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c5 win=True
		NoveltyTermination s1=c4 s2=c6 win=True
		NoveltyTermination s1=c5 s2=c3 win=True
		NoveltyTermination s1=c5 s2=c6 win=True
		NoveltyTermination s1=c6 s2=avatar win=True
		NoveltyTermination s1=c6 s2=c3 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=c5 s2=EOS win=True
		NoveltyTermination s1=c6 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		0 > c3
		1 > c6
		2 > avatar
		3 > c5
		4 > c2
		5 > c4
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
