level="""
55555555555555555555555555555555
55555555555555555555555555555555
5555                        5555
5555                        5555
5555            7           5555
5555                        5555
5555                    7   5555
5555          3             5555
5555                        5555
5555                        5555
55555555555555555555555555555555
55555555555555555555555555555555
55555555555555555555555555555555
"""
game = """
BasicGame
	SpriteSet
		c3 > ResourcePack color=GREEN
		c2 > ResourcePack color=BLACK
		avatar > MovingAvatar color=DARKBLUE
	InteractionSet
		avatar c2 > stepBack
		c2 c3 > nothing
		c3 c2 > nothing
		c2 c2 > nothing
		c3 c3 > nothing
		avatar EOS > stepBack
		c3 avatar > killSprite
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
		SpriteCounter stype=c3 limit=0 win=True
	LevelMapping
		3 > avatar
		5 > c2
		7 > c3
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
