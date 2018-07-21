level="""
88888888888888888888888888888888
8b                             8
8                              8
8                              8
8                              8
8                              8
8    c                         8
8  9                          d8
888                            8
88888888888888888888888888888888
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=PINK
		c2 > ResourcePack color=DARKGRAY
		c5 > Chaser color=LIGHTGREEN cooldown=1 stype=c4 fleeing=False
		c4 > ResourcePack color=YELLOW
	InteractionSet
		avatar c2 > stepBack
		c2 avatar > stepBack
		avatar avatar > stepBack
		c4 EOS > nothing
		c5 EOS > nothing
		c2 c3 > nothing
		c3 c2 > nothing
		c2 c2 > nothing
		c4 avatar > bounceForward
		avatar c5 > nothing
		c3 c3 > nothing
		avatar EOS > stepBack
		c3 c4 > killSprite
		c4 c3 > nothing
		c5 c5 > nothing
		c2 EOS > nothing
		c4 c5 > killSprite
		c5 c4 > nothing
		c3 EOS > nothing
		c3 c5 > nothing
		c5 c3 > nothing
		c4 c4 > nothing
		c3 avatar > killSprite
		avatar c3 > stepBack
		c2 c5 > stepBack
		c5 c2 > stepBack
		c2 c4 > stepBack
		c4 c2 > stepBack
	TerminationSet
		MultiSpriteCounter stype0=c4 stype1=c3 limit=0 win=True
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=avatar s2=avatar win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c5 s2=EOS win=True
		SpriteCounter stype=c4 limit=0 win=False
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		d > c3
		c > c4
		9 > avatar
		b > c5
		8 > c2
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
