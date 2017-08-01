level="""
55555555555555555555555555
55444                 56 5
5552                  53 5
5 5                   5155
5           0         5755
5   2 2               5 55
5                     5 55
55555555555555555555555555
"""
game = """
BasicGame
	SpriteSet
		c8 > ResourcePack color=GREEN
		avatar > ShootAvatar color=WHITE stype=sword
		sword > Flicker color=BLUE singleton=True
		c3 > Missile color=PINK speed=1.0 orientation=RIGHT
		c7 > ResourcePack color=BLACK
		c6 > ResourcePack color=YELLOW
		c5 > Missile color=DARKGRAY speed=0.2 orientation=DOWN
		c4 > ResourcePack color=BROWN
	InteractionSet
		c3 c5 > killSprite
		c5 c3 > killSprite
		c6 c7 > killSprite
		c7 c6 > killSprite
		c8 c8 > killSprite
		c6 c8 > killSprite
		c8 c6 > killSprite
		c4 c8 > killSprite
		c8 c4 > killSprite
		c6 avatar > killSprite
		sword EOS > stepBack
		c8 EOS > stepBack
		c5 c4 > stepBack
		c3 c4 > killSprite
		c4 c3 > killSprite
		c4 EOS > stepBack
		sword avatar > nothing
		avatar c7 > stepBack
		c7 sword > nothing
		c5 sword > nothing
		sword c5 > nothing
		c5 c7 > killSprite
		c7 c5 > killSprite
		c3 avatar > killSprite
		c5 EOS > stepBack
		c5 c8 > killSprite
		c8 c5 > killSprite
		sword c3 > killSprite
		c3 sword > killSprite
		c3 c8 > killSprite
		c8 c3 > killSprite
		c4 c6 > killSprite
		c6 c4 > killSprite
		c3 c7 > killSprite
		c7 c3 > killSprite
		c5 c6 > killSprite
		c6 c5 > killSprite
		c7 EOS > stepBack
		sword c6 > killSprite
		c6 sword > killSprite
		c4 sword > killSprite
		c3 c3 > killSprite
		c7 c8 > killSprite
		c8 c7 > killSprite
		c3 EOS > stepBack
		c8 avatar > killSprite
		c4 c7 > killSprite
		c7 c4 > killSprite
		c3 c6 > killSprite
		c6 c3 > killSprite
		c6 c6 > killSprite
		sword sword > killSprite
		c7 c7 > killSprite
		c6 EOS > stepBack
		avatar c5 > killIfFromAbove
		avatar c5 > stepBack
		sword c8 > killSprite
		c8 sword > killSprite
		c5 c5 > killSprite
		c4 c4 > killSprite
	TerminationSet
		NoveltyTermination s1=sword s2=sword win=True
		NoveltyTermination s1=sword s2=c3 win=True
		NoveltyTermination s1=sword s2=c6 win=True
		NoveltyTermination s1=sword s2=c8 win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c3 s2=c6 win=True
		NoveltyTermination s1=c3 s2=c7 win=True
		NoveltyTermination s1=c3 s2=c8 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c6 win=True
		NoveltyTermination s1=c4 s2=c7 win=True
		NoveltyTermination s1=c4 s2=c8 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c5 s2=c6 win=True
		NoveltyTermination s1=c5 s2=c7 win=True
		NoveltyTermination s1=c5 s2=c8 win=True
		NoveltyTermination s1=c6 s2=avatar win=True
		NoveltyTermination s1=c6 s2=c6 win=True
		NoveltyTermination s1=c6 s2=c7 win=True
		NoveltyTermination s1=c6 s2=c8 win=True
		NoveltyTermination s1=c7 s2=c7 win=True
		NoveltyTermination s1=c7 s2=c8 win=True
		NoveltyTermination s1=c8 s2=avatar win=True
		NoveltyTermination s1=c8 s2=c8 win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c4 limit=0 win=True
	LevelMapping
		0 > c3
		1 > sword
		2 > c4
		3 > c5
		9 > sword c7
		4 > c6
		5 > c7
		b > avatar sword
		6 > c8
		7 > avatar
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
