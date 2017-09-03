level="""
5555555555555555
5   136631     5
5   111111   2 5
5   366633    75
5e4            5
5555555555555555
5          333 5
5555555555555555
"""
game = """
BasicGame
	SpriteSet
		c8 > ResourcePack color=GREEN
		avatar > ShootAvatar color=DARKBLUE stype=sword
		sword > Flicker color=PINK singleton=True limit=0
		c3 > Missile color=GRAY speed=0.2 orientation=DOWN cooldown=1
		c7 > ResourcePack color=YELLOW
		c6 > ResourcePack color=DARKGRAY
		c5 > ResourcePack color=BROWN
		c4 > ResourcePack color=GOLD
		diamond > Resource color=RESOURCETOADD limit=9
	InteractionSet
		c6 c7 > killSprite
		c7 c6 > killSprite
		c8 c8 > killSprite
		avatar c3 > killIfFromAbove
		avatar c3 > stepBack
		c6 c8 > killSprite
		c8 c6 > killSprite
		c4 c8 > killSprite
		c8 c4 > killSprite
		c6 avatar > killIfOtherHasMore resource=diamond limit=1
		avatar c6 > stepBack
		c4 c5 > killSprite
		c5 c4 > killSprite
		c7 c8 > killSprite
		c8 c7 > killSprite
		sword avatar > killSprite
		sword avatar > killIfOtherHasMore resource=diamond limit=1
		avatar c7 > changeScore value=5
		avatar c7 > changeResource limit=9 resource=diamond value=1
		c7 avatar > killSprite
		sword c7 > nothing
		c5 sword > killSprite
		c5 c7 > killSprite
		c7 c5 > killSprite
		avatar EOS > stepBack
		c3 c4 > killSprite
		c4 c3 > killSprite
		c5 c8 > killSprite
		c8 c5 > killSprite
		sword c3 > nothing
		c3 c8 > killSprite
		c8 c3 > killSprite
		c5 c6 > killSprite
		c6 c5 > killSprite
		sword c6 > nothing
		sword c4 > killSprite
		c4 sword > killSprite
		c8 avatar > changeScore value=100
		c8 avatar > killIfOtherHasMore resource=diamond limit=1
		c8 avatar > nothing
		c4 c7 > killSprite
		c7 c4 > killSprite
		c6 c6 > killSprite
		sword sword > killSprite
		c7 c7 > killSprite
		c5 avatar > killSprite
		avatar c4 > killSprite
		c4 avatar > killIfOtherHasMore resource=diamond limit=1
		sword c8 > nothing
		c5 c5 > killSprite
		c4 c4 > killSprite
		c3 c5 > stepBack
		sword EOS > stepBack
		c8 EOS > stepBack
		c4 EOS > stepBack
		c5 EOS > stepBack
		c4 c6 > stepBack
		c3 c7 > stepBack
		c7 EOS > stepBack
		c3 c3 > stepBack
		c3 EOS > stepBack
		c3 c6 > stepBack
		c6 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=sword s2=avatar win=True
		NoveltyTermination s1=sword s2=sword win=True
		NoveltyTermination s1=sword s2=c4 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c8 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c5 win=True
		NoveltyTermination s1=c4 s2=c7 win=True
		NoveltyTermination s1=c4 s2=c8 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c5 s2=c6 win=True
		NoveltyTermination s1=c5 s2=c7 win=True
		NoveltyTermination s1=c5 s2=c8 win=True
		NoveltyTermination s1=c6 s2=c6 win=True
		NoveltyTermination s1=c6 s2=c7 win=True
		NoveltyTermination s1=c6 s2=c8 win=True
		NoveltyTermination s1=c7 s2=c7 win=True
		NoveltyTermination s1=c7 s2=c8 win=True
		NoveltyTermination s1=c8 s2=c8 win=True
		NoveltyTermination s1=sword s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=c5 s2=EOS win=True
		NoveltyTermination s1=c6 s2=EOS win=True
		NoveltyTermination s1=c7 s2=EOS win=True
		NoveltyTermination s1=c8 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		NoveltyTermination s1=c4 s2=avatar win=True args={item:diamond,num:0,negated:False,operator_name:>}
		NoveltyTermination s1=c8 s2=avatar win=True args={item:diamond,num:0,negated:False,operator_name:>}
		NoveltyTermination s1=sword s2=avatar win=True args={item:diamond,num:0,negated:False,operator_name:>}
		NoveltyTermination s1=c6 s2=avatar win=True args={item:diamond,num:0,negated:False,operator_name:>}
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c5 limit=0 win=True
		SpriteCounter stype=c7 limit=0 win=True
	LevelMapping
		0 > sword
		1 > c3
		2 > c4
		3 > c5
		4 > avatar
		5 > c6
		6 > c7
		b > c8 sword
		7 > c8
		e > c7 sword
		9 > sword c6
		d > c3 sword
		c > avatar c8
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
