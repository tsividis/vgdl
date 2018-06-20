level="""
333333333333333333
3 4 0   3    2   3
3   0   3    33333
3 1 0         0  3
333333333333333333
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=ORANGE
		c2 > ResourcePack color=PINK
		c6 > ResourcePack color=GOLD
		c5 > ResourcePack color=BLACK
		c4 > ResourcePack color=WHITE
		medicine > Resource color=RESOURCETOADD limit=4
	InteractionSet
		c2 avatar > killSprite
		c2 avatar > killIfOtherHasMore resource=medicine limit=1
		c2 c4 > nothing
		c4 c2 > nothing
		c6 avatar > killSprite
		c6 avatar > killIfOtherHasMore resource=medicine limit=1
		c4 c5 > nothing
		c5 c4 > nothing
		c3 c5 > nothing
		c5 c3 > nothing
		c3 c4 > nothing
		c4 c3 > nothing
		c2 c5 > nothing
		c5 c2 > nothing
		avatar EOS > stepBack
		c3 avatar > killSprite
		c3 avatar > killIfOtherHasMore resource=medicine limit=1
		c2 c6 > nothing
		c6 c2 > nothing
		c4 c6 > nothing
		c6 c4 > nothing
		c2 c2 > nothing
		c5 c6 > nothing
		c6 c5 > nothing
		c3 c3 > nothing
		c3 c6 > nothing
		c6 c3 > nothing
		c6 c6 > nothing
		c2 c3 > nothing
		c3 c2 > nothing
		c5 avatar > killIfOtherHasMore resource=medicine limit=1
		avatar c5 > stepBack
		avatar c4 > changeResource limit=4 resource=medicine value=1
		c4 avatar > killSprite
		c4 avatar > killIfOtherHasMore resource=medicine limit=1
		c5 c5 > nothing
		c4 c4 > nothing
		c5 EOS > stepBack
		c4 EOS > stepBack
		c3 EOS > stepBack
		c6 EOS > stepBack
		c2 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=avatar win=True
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c2 s2=c5 win=True
		NoveltyTermination s1=c2 s2=c6 win=True
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
		NoveltyTermination s1=c6 s2=avatar win=True
		NoveltyTermination s1=c6 s2=c6 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=c5 s2=EOS win=True
		NoveltyTermination s1=c6 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		NoveltyTermination s1=c3 s2=avatar win=True args={item:medicine,num:0,negated:False,operator_name:>}
		NoveltyTermination s1=c6 s2=avatar win=True args={item:medicine,num:0,negated:False,operator_name:>}
		NoveltyTermination s1=c5 s2=avatar win=True args={item:medicine,num:0,negated:False,operator_name:>}
		NoveltyTermination s1=c2 s2=avatar win=True args={item:medicine,num:0,negated:False,operator_name:>}
		NoveltyTermination s1=c4 s2=avatar win=True args={item:medicine,num:0,negated:False,operator_name:>}
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		0 > c2
		1 > c6
		2 > avatar
		3 > c5
		4 > c3
		5 > c4
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
