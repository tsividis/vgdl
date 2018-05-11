level="""
1111111111111111111111
1           2 1     11
1                    1
1             0      1
1111111111111111111111
"""
game = """
BasicGame
	SpriteSet
		c3 > ResourcePack color=DARKGRAY
		c2 > ResourcePack color=PINK
		avatar > MovingAvatar color=DARKBLUE
	InteractionSet
		c2 avatar > killSprite
		c2 c3 > nothing
		c3 c2 > nothing
		c2 c2 > nothing
		c3 c3 > nothing
		avatar EOS > stepBack
		avatar c3 > stepBack
		c2 EOS > stepBack
		c3 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c2 limit=0 win=True
	LevelMapping
		0 > c2
		1 > c3
		2 > avatar
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
