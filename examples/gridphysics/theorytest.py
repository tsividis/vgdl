level="""
5555555555555
5    5    6 5
5   555     5
5 3  555    5
5  5555555  5
5      5    5
5    5   3  5
54   57   3 5
5555555555555
"""
game = """
BasicGame
	SpriteSet
		avatar > ShootAvatar color=DARKBLUE stype=sword
		sword > OrientedFlicker color=BLUE singleton=True
		c3 > ResourcePack color=ORANGE
		c6 > RandomNPC color=BROWN cooldown=4
		c5 > ResourcePack color=GREEN
		c4 > ResourcePack color=DARKGRAY
		key > Resource color=RESOURCETOADD limit=10
	InteractionSet
		c3 c5 > killSprite
		c5 c3 > killSprite
		avatar c6 > killSprite
		c4 c5 > killSprite
		c5 c4 > killSprite
		avatar c3 > changeResource resource=key limit=10 value=1
		c3 avatar > killSprite
		sword avatar > nothing
		sword c5 > nothing
		c3 c4 > killSprite
		c4 c3 > killSprite
		sword c3 > nothing
		c6 c5 > killSprite
		c5 c6 > killSprite
		c6 sword > killSprite
		sword c6 > killSprite
		sword c4 > nothing
		avatar c4 > stepBack
		c6 c3 > killSprite
		c3 c6 > killSprite
		sword sword > killSprite
		c5 avatar > killIfOtherHasMore resource=key limit=1
		avatar c5 > nothing
		c3 c3 > killSprite
		c5 c5 > killSprite
		c4 c4 > killSprite
		c5 EOS > stepBack
		sword EOS > stepBack
		c4 EOS > stepBack
		c6 c4 > stepBack
		c3 EOS > stepBack
		c6 c6 > stepBack
		c6 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=sword s2=sword win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c5 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c6 s2=sword win=True
		NoveltyTermination s1=c6 s2=c3 win=True
		NoveltyTermination s1=c6 s2=c5 win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c5 limit=0 win=True
	LevelMapping
		1 > sword
		3 > c6
		4 > avatar
		5 > c4
		b > avatar sword
		9 > avatar c5
		8 > sword c4
		6 > c5
		7 > c3
		c > c3 sword
		d > c5 sword
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
