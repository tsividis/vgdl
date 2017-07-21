level="""
55555555555555555555555555
52   22222222222225      5
557   2222222222345      5
55 32 22222222222 5      5
5 522 222222222225       5
555555555555555555       5
5                        5
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
		c3 > Missile color=DARKGRAY speed=0.2 orientation=DOWN
		c6 > ResourcePack color=BROWN
		c5 > ResourcePack color=YELLOW
		c4 > ResourcePack color=BLACK
	InteractionSet
		c3 c5 > killSprite
		c5 c3 > killSprite
		c5 EOS > stepBack
		c6 avatar > killSprite
		sword EOS > stepBack
		c4 c5 > killSprite
		c5 c4 > killSprite
		avatar c3 > stepBack
		c4 EOS > stepBack
		sword avatar > nothing
		c5 sword > nothing
		c3 c4 > killSprite
		c4 c3 > killSprite
		c3 sword > nothing
		sword c3 > nothing
		c4 c6 > killSprite
		c6 c4 > killSprite
		c5 c6 > killSprite
		c6 c5 > killSprite
		c6 sword > killSprite
		c4 sword > nothing
		avatar c4 > stepBack
		c3 EOS > stepBack
		c3 c6 > stepBack
		c6 c6 > killSprite
		sword sword > killSprite
		c6 EOS > stepBack
		c5 avatar > killSprite
		c5 avatar > collectResource
		c3 c3 > killSprite
		c5 c5 > killSprite
		c4 c4 > killSprite
	TerminationSet
		NoveltyTermination s1=sword s2=sword win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c5 win=True
		NoveltyTermination s1=c4 s2=c6 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c5 s2=c6 win=True
		NoveltyTermination s1=c6 s2=c6 win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c5 limit=0 win=True
	LevelMapping
		1 > sword
		d > c3 sword
		2 > c6
		3 > c3
		9 > sword c4
		4 > c5
		5 > c4
		c > c5 sword
		b > avatar sword
		7 > avatar
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
