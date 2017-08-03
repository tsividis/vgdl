level="""
55555555555
57  3     5
5         5
5       685
55555555555
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=GREEN
		c2 > ResourcePack color=ORANGE
		c5 > RandomNPC color=RED cooldown=9
		c4 > ResourcePack color=BLACK
	InteractionSet
		c2 avatar > killSprite
		c5 c2 > nothing
		c2 c4 > killSprite
		c4 c2 > killSprite
		c2 c3 > killSprite
		c3 c2 > killSprite
		c2 c2 > killSprite
		avatar c4 > stepBack
		c5 avatar > killSprite
		c3 c3 > killSprite
		c3 c4 > killSprite
		c4 c3 > killSprite
		c5 c5 > killSprite
		c5 c4 > reverseDirection
		c3 c5 > killSprite
		c5 c3 > killSprite
		c4 c4 > killSprite
		c3 avatar > killSprite
		c4 EOS > stepBack
		c5 EOS > stepBack
		c2 EOS > stepBack
		c3 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=avatar win=True
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c5 s2=avatar win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		3 > avatar
		9 > c5 c4
		5 > c4
		6 > c2
		7 > c3
		8 > c5
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
