level="""
55555555555555555555555555
5 223244232  5           5
5 223333337  5           5
5222544422   5           5
54   5      65           5
55555555555555555555555555
5                        5
5                        5
5                        5
5                        5
5                        5
5                        5
55555555555555555555555555
"""
game = """
BasicGame
	SpriteSet
		avatar > ShootAvatar color=WHITE stype=sword
		sword > Flicker color=BLUE singleton=True
		c3 > ResourcePack color=BROWN
		c7 > Missile color=DARKGRAY speed=0.2 orientation=DOWN
		c6 > ResourcePack color=YELLOW
		c5 > ResourcePack color=GREEN
		c4 > ResourcePack color=BLACK
		diamond > Resource color=RESOURCETOADD limit=3
	InteractionSet
		c3 c5 > killSprite
		c5 c3 > killSprite
		c7 c6 > stepBack
		c5 EOS > stepBack
		avatar c6 > changeResource limit=3 resource=diamond value=1
		c6 avatar > killSprite
		sword EOS > stepBack
		c4 c5 > killSprite
		c5 c4 > killSprite
		c3 c4 > killSprite
		c4 c3 > killSprite
		c4 EOS > stepBack
		sword avatar > killIfOtherHasMore resource=diamond limit=0
		sword avatar > nothing
		avatar c7 > stepBack
		c7 sword > nothing
		sword c7 > nothing
		c5 sword > nothing
		c5 c7 > killSprite
		c7 c5 > killSprite
		c3 avatar > killSprite
		c3 sword > killSprite
		c4 c6 > killSprite
		c6 c4 > killSprite
		c7 c3 > stepBack
		c5 c6 > killSprite
		c6 c5 > killSprite
		c7 EOS > stepBack
		c6 sword > nothing
		c4 sword > nothing
		c3 c3 > killSprite
		c3 EOS > stepBack
		c7 c4 > stepBack
		c3 c6 > killSprite
		c6 c3 > killSprite
		c6 c6 > killSprite
		sword sword > killSprite
		c7 c7 > stepBack
		c6 EOS > stepBack
		c5 avatar > nothing
		avatar c4 > stepBack
		c5 c5 > killSprite
		c4 c4 > killSprite
	TerminationSet
		NoveltyTermination s1=sword s2=sword win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c3 s2=c6 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c5 win=True
		NoveltyTermination s1=c4 s2=c6 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c5 s2=c6 win=True
		NoveltyTermination s1=c5 s2=c7 win=True
		NoveltyTermination s1=c6 s2=c6 win=True
		NoveltyTermination s1=sword s2=avatar win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c3 limit=0 win=True
		SpriteCounter stype=c6 limit=0 win=True
	LevelMapping
		1 > sword
		d > c7 sword
		h > avatar c5
		2 > c3
		3 > c7
		9 > sword c4
		4 > c6
		b > c5 sword
		f > avatar sword
		5 > c4
		e > c6 sword
		c > avatar c5 sword
		6 > c5
		7 > avatar
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
