level="""
44444444444444444444444444444444
4                              4
4             6    7           4
4                      11111   4
4  6                   15  1   4
4                      1   1   4
4                  3   11111   4
4         7       6            4
444                            4
44444444444444444444444444444444
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=WHITE
		c2 > Chaser color=ORANGE fleeing=False cooldown=1 stype=c3
		c6 > ResourcePack color=PURPLE
		c5 > ResourcePack color=GREEN
		c4 > ResourcePack color=BLACK
	InteractionSet
		c2 avatar > killSprite
		c2 c4 > nothing
		c4 c2 > nothing
		c6 avatar > killSprite
		c5 c4 > nothing
		c4 c5 > nothing
		c5 c3 > nothing
		c3 c5 > nothing
		c3 avatar > killSprite
		c5 c2 > nothing
		c2 c5 > nothing
		avatar EOS > stepBack
		c3 c4 > nothing
		c4 c3 > nothing
		c6 c4 > nothing
		c4 c6 > nothing
		c2 c2 > nothing
		c6 c5 > nothing
		c5 c6 > nothing
		c3 c3 > nothing
		c6 c3 > nothing
		c3 c6 > nothing
		c3 c2 > killSprite
		c5 avatar > killSprite
		c4 avatar > killSprite
		c4 c4 > nothing
		c5 EOS > stepBack
		c4 EOS > stepBack
		c2 c6 > stepBack
		c3 EOS > stepBack
		c6 EOS > stepBack
		c2 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=avatar win=True
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c4 s2=avatar win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		NoveltyTermination s1=c5 s2=EOS win=True
		NoveltyTermination s1=c5 s2=c2 win=True
		NoveltyTermination s1=c5 s2=c3 win=True
		NoveltyTermination s1=c5 s2=c4 win=True
		NoveltyTermination s1=c6 s2=avatar win=True
		NoveltyTermination s1=c6 s2=EOS win=True
		NoveltyTermination s1=c6 s2=c4 win=True
		NoveltyTermination s1=c6 s2=c3 win=True
		NoveltyTermination s1=c6 s2=c5 win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c3 limit=0 win=True
		SpriteCounter stype=c5 limit=0 win=True
	LevelMapping
		1 > c6
		3 > avatar
		4 > c4
		5 > c2
		6 > c5
		7 > c3
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
