level="""
2222222222222222222
2            1 3332
2              3 02
2222222222222222222
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=WHITE
		c3 > ResourcePack color=GREEN
		c2 > ResourcePack color=BLACK
		c5 > ResourcePack color=GOLD
		c4 > ResourcePack color=RED
		key > Resource color=RESOURCETOADD limit=1
	InteractionSet
		c3 c5 > nothing
		c5 c3 > nothing
		c2 c5 > nothing
		c5 c2 > nothing
		c2 c4 > nothing
		c4 c2 > nothing
		c2 c3 > nothing
		c3 c2 > nothing
		c2 c2 > nothing
		avatar c4 > killSprite
		c4 avatar > killIfOtherHasMore resource=key limit=1
		avatar c5 > changeResource limit=1 resource=key value=1
		c5 avatar > killSprite
		c5 avatar > killIfOtherHasMore resource=key limit=1
		c3 c3 > nothing
		avatar EOS > stepBack
		c3 c4 > nothing
		c4 c3 > nothing
		c5 c5 > nothing
		c4 c5 > nothing
		c5 c4 > nothing
		c2 avatar > killIfOtherHasMore resource=key limit=1
		avatar c2 > stepBack
		c4 c4 > nothing
		c3 avatar > killSprite
		c3 avatar > killIfOtherHasMore resource=key limit=1
		c4 EOS > stepBack
		c5 EOS > stepBack
		c2 EOS > stepBack
		c3 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c2 s2=c5 win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c5 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=c5 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		NoveltyTermination s1=c4 s2=avatar win=True args={item:key,num:0,negated:False,operator_name:>}
		NoveltyTermination s1=c2 s2=avatar win=True args={item:key,num:0,negated:False,operator_name:>}
		NoveltyTermination s1=c5 s2=avatar win=True args={item:key,num:0,negated:False,operator_name:>}
		NoveltyTermination s1=c3 s2=avatar win=True args={item:key,num:0,negated:False,operator_name:>}
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		2 > c2
		1 > avatar
		0 > c3
		4 > c5
		3 > c4
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
