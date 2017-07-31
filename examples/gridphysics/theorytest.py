level="""
55555555555555555555555555
55444                    5
5552                    65
5 5                     55
5                        5
5                        5
5                      7 5
55555555555555555555555555
"""
game = """
BasicGame
	SpriteSet
		avatar > ShootAvatar color=WHITE stype=sword
		sword > Flicker color=BLUE singleton=True
		c3 > ResourcePack color=BROWN
		c6 > ResourcePack color=YELLOW
		c5 > ResourcePack color=GREEN
		c4 > ResourcePack color=BLACK
		diamond > Resource color=RESOURCETOADD limit=3
	InteractionSet
		c3 c5 > killSprite
		c5 c3 > killSprite
		c5 EOS > stepBack
		c6 avatar > changeScore value=5
		avatar c6 > changeResource limit=3 resource=diamond value=1
		c6 avatar > killSprite
		c6 avatar > killIfOtherHasMore resource=diamond limit=3
		sword EOS > stepBack
		c4 c5 > killSprite
		c5 c4 > killSprite
		c3 avatar > killSprite
		c3 avatar > killIfOtherHasMore resource=diamond limit=0
		c3 avatar > killIfOtherHasMore resource=diamond limit=3
		c4 EOS > stepBack
		sword avatar > nothing
		c5 sword > nothing
		c3 c4 > killSprite
		c4 c3 > killSprite
		sword c3 > killSprite
		c3 sword > killSprite
		c4 c6 > killSprite
		c6 c4 > killSprite
		c5 c6 > killSprite
		c6 c5 > killSprite
		c6 sword > nothing
		c4 sword > nothing
		c3 c3 > killSprite
		c3 EOS > stepBack
		c3 c6 > killSprite
		c6 c3 > killSprite
		c6 c6 > killSprite
		sword sword > killSprite
		c6 EOS > stepBack
		c5 avatar > killIfOtherHasMore resource=diamond limit=3
		c5 avatar > nothing
		avatar c4 > stepBack
		c5 c5 > killSprite
		c4 c4 > killSprite
	TerminationSet
		NoveltyTermination s1=sword s2=sword win=True
		NoveltyTermination s1=sword s2=c3 win=True
		NoveltyTermination s1=c3 s2=avatar win=True
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
		NoveltyTermination s1=c6 s2=avatar win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c6 limit=0 win=True
		SpriteCounter stype=c5 limit=0 win=True
	LevelMapping
		1 > sword
		9 > avatar c5
		2 > c3
		d > sword c4
		4 > c6
		e > c5 sword
		5 > c4
		b > c6 sword
		c > avatar sword
		6 > c5
		7 > avatar
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
