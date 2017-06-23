level="""
3333333333333333333333333333
3         3  5  3          3
3000077770000000000777700073
3007770007770007777000077773
333   33   333    333  33333
36     444       444   44  3
3 6   666     6   66   66  3
3 2                        3
3333333333333333333333333333
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > Missile color=BROWN speed=0.5 orientation=LEFT
		c2 > ResourcePack color=BLUE
		c7 > Missile color=RED speed=0.5 orientation=RIGHT
		c6 > Resource color=BLACK
		c5 > Missile color=ORANGE speed=0.5 orientation=RIGHT
		c4 > ResourcePack color=GREEN
		safety > Resource color=RESOURCETOADD
	InteractionSet
		c3 c5 > killSprite
		c5 c3 > killSprite
		c7 c6 > nothing
		c2 c4 > killSprite
		c4 c2 > killSprite
		c5 EOS > wrapAround offset=0
		avatar c6 > stepBack
		c4 c5 > killSprite
		c5 c4 > killSprite
		c3 c4 > killSprite
		c4 c3 > killSprite
		c2 c5 > killSprite
		c5 c2 > killSprite
		c4 EOS > stepBack
		avatar c7 > killSprite
		c5 c7 > killSprite
		c7 c5 > killSprite
		avatar c3 > changeResource resource=safety limit=4 value=1
		avatar c3 > pullWithIt
		c2 c6 > killSprite
		c6 c2 > killSprite
		c4 c6 > killSprite
		c6 c4 > killSprite
		c3 c7 > killSprite
		c7 c3 > killSprite
		c2 c2 > killSprite
		c5 c6 > nothing
		c7 EOS > wrapAround offset=0
		c3 c3 > killSprite
		c3 EOS > wrapAround offset=0
		c2 c7 > killSprite
		c7 c2 > killSprite
		c4 c7 > killSprite
		c7 c4 > killSprite
		c3 c6 > nothing
		c6 c6 > killSprite
		c2 c3 > nothing
		c7 c7 > killSprite
		c6 EOS > stepBack
		avatar c5 > killSprite
		c4 avatar > killSprite
		c4 avatar > killIfOtherHasMore resource=safety limit=0
		c5 c5 > killSprite
		c2 EOS > stepBack
		avatar c2 > changeResource limit=4 resource=safety value=-1
		avatar c2 > killIfHasLess resource=safety limit=0
		c4 c4 > killSprite
	TerminationSet
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c2 s2=c5 win=True
		NoveltyTermination s1=c2 s2=c6 win=True
		NoveltyTermination s1=c2 s2=c7 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c3 s2=c7 win=True
		NoveltyTermination s1=c4 s2=avatar win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c5 win=True
		NoveltyTermination s1=c4 s2=c6 win=True
		NoveltyTermination s1=c4 s2=c7 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c5 s2=c7 win=True
		NoveltyTermination s1=c6 s2=c6 win=True
		NoveltyTermination s1=c7 s2=c7 win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		0 > c2
		1 > c3
		2 > avatar
		b > c7 c6
		c > avatar c2
		d > avatar c3 c2
		5 > c4
		8 > c3 c6
		4 > c5
		3 > c6
		7 > c3 c2
		6 > c7
		9 > c5 c6
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
