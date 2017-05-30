level="""
222222222222222222
2   5   2    5  32
2 4     2 1  22222
25555      5     2
2     5 5       22
22            5552
25555       555552
244455      55  02
24445    5  55   2
222222222222222222
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=WHITE
		c2 > Resource color=ORANGE
		c6 > Resource color=RED
		c5 > ResourcePack color=GOLD
		c4 > Resource color=BLACK
		medicine > Resource color=RESOURCETOADD
	InteractionSet
		c3 c5 > killSprite
		c5 c3 > killSprite
		c2 c4 > killSprite
		c4 c2 > killSprite
		c5 EOS > stepBack
		avatar c6 > killIfHasLess resource=medicine limit=0
		c6 avatar > killSprite
		avatar c6 > changeResource resource=medicine value=-1
		c4 c5 > killSprite
		c5 c4 > killSprite
		c3 c4 > killSprite
		c4 c3 > killSprite
		c2 c5 > killSprite
		c5 c2 > killSprite
		c4 EOS > stepBack
		c3 avatar > killSprite
		avatar c3 > changeResource resource=medicine value=1
		c2 c6 > killSprite
		c6 c2 > killSprite
		c4 c6 > killSprite
		c6 c4 > killSprite
		c2 c2 > killSprite
		c5 c6 > killSprite
		c6 c5 > killSprite
		avatar c4 > stepBack
		c3 EOS > stepBack
		c3 c6 > killSprite
		c6 c3 > killSprite
		c6 c6 > killSprite
		c2 c3 > killSprite
		c3 c2 > killSprite
		c6 EOS > stepBack
		c5 avatar > killSprite
		c3 c3 > killSprite
		c5 c5 > killSprite
		c2 EOS > stepBack
		c2 avatar > killSprite
		c4 c4 > killSprite
	TerminationSet
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c2 s2=c5 win=True
		NoveltyTermination s1=c2 s2=c6 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c3 s2=c6 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c5 win=True
		NoveltyTermination s1=c4 s2=c6 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c5 s2=c6 win=True
		NoveltyTermination s1=c6 s2=c6 win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c6 limit=0 win=True
		SpriteCounter stype=c5 limit=0 win=True
	LevelMapping
		0 > c5
		1 > avatar
		2 > c4
		3 > c2
		4 > c3
		5 > c6
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
