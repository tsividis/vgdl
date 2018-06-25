level="""
3333333333333
3   00 00   3
3 310040013 3
3 3 00000 3 3
3    0600 1 3
3 3 33133 3 3
3     21    3
3 3333 3333 3
3      5    3
3333333333333
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=BLACK
		c2 > ResourcePack color=ORANGE
		c7 > ResourcePack color=RED
		c6 > ResourcePack color=BLUE
		c5 > ResourcePack color=BROWN
		c4 > ResourcePack color=GREEN
		key > Resource color=RESOURCETOADD limit=1
	InteractionSet
		c5 c3 > undoAll
		c7 c6 > nothing
		c6 c7 > nothing
		c2 c4 > nothing
		c4 c2 > nothing
		avatar c6 > killSprite
		c4 c5 > nothing
		c5 c4 > nothing
		c3 avatar > killIfOtherHasMore resource=key limit=1
		c3 avatar > killIfOtherHasMore resource=key limit=1
		avatar c3 > stepBack
		c2 c5 > nothing
		c5 c2 > nothing
		c7 avatar > killSprite
		c5 c7 > undoAll
		avatar EOS > stepBack
		c3 c4 > nothing
		c4 c3 > nothing
		c6 c2 > nothing
		c2 c6 > nothing
		c6 c4 > nothing
		c4 c6 > nothing
		c7 c3 > nothing
		c3 c7 > nothing
		c2 c2 > nothing
		c6 c5 > changeScore value=1
		c6 c5 > killSprite
		c5 c6 > killSprite
		c4 avatar > killIfOtherHasMore resource=key limit=1
		avatar c4 > undoAll
		c7 c2 > nothing
		c2 c7 > nothing
		c7 c4 > nothing
		c4 c7 > nothing
		c6 c3 > nothing
		c3 c6 > nothing
		c2 c3 > nothing
		c3 c2 > nothing
		c5 avatar > killIfOtherHasMore resource=key limit=1
		c5 avatar > killIfOtherHasMore resource=key limit=1
		c5 avatar > bounceForward
		c3 c3 > nothing
		c5 c5 > undoAll
		avatar c2 > changeScore value=1
		avatar c2 > changeResource resource=key limit=1 value=1
		c2 avatar > killSprite
		c4 c4 > nothing
		c5 EOS > stepBack
		c4 EOS > stepBack
		c7 EOS > stepBack
		c3 EOS > stepBack
		c6 EOS > stepBack
		c2 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c5 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=c5 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		NoveltyTermination s1=c6 s2=EOS win=True
		NoveltyTermination s1=c6 s2=c2 win=True
		NoveltyTermination s1=c6 s2=c3 win=True
		NoveltyTermination s1=c6 s2=c4 win=True
		NoveltyTermination s1=c7 s2=avatar win=True
		NoveltyTermination s1=c7 s2=EOS win=True
		NoveltyTermination s1=c7 s2=c2 win=True
		NoveltyTermination s1=c7 s2=c3 win=True
		NoveltyTermination s1=c7 s2=c4 win=True
		NoveltyTermination s1=c7 s2=c6 win=True
		NoveltyTermination s1=c3 s2=avatar win=True args={item:key,num:1,negated:False,operator_name:>=}
		NoveltyTermination s1=c5 s2=avatar win=True args={item:key,num:1,negated:False,operator_name:>=}
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c4 limit=0 win=True
	LevelMapping
		0 > c6
		1 > c5
		7 > c5 c2
		2 > avatar
		5 > c4
		4 > c2
		3 > c3
		6 > c7
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
