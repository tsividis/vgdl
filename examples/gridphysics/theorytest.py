level="""
22222222
2      2
2    1 2
2     02
2   2222
222222 2
2      2
2      2
22222222
"""
game = """
BasicGame
	SpriteSet
		c3 > ResourcePack color=GREEN
		c2 > ResourcePack color=BLACK
		avatar > MarioAvatar color=WHITE
		c4 > ResourcePack color=GOLD
		key > Resource color=RESOURCETOADD limit=1
	InteractionSet
		c2 avatar > killIfOtherHasMore resource=key limit=1
		avatar c2 > wallStop
		c2 c4 > nothing
		c4 c2 > nothing
		c2 c3 > nothing
		c3 c2 > nothing
		c2 c2 > nothing
		c3 c3 > nothing
		avatar EOS > stepBack
		c3 avatar > killSprite
		c3 avatar > killIfOtherHasMore resource=key limit=1
		avatar c4 > changeResource limit=1 resource=key value=1
		c4 avatar > killSprite
		c4 avatar > killIfOtherHasMore resource=key limit=1
		c4 c4 > nothing
		c3 c4 > nothing
		c4 c3 > nothing
		c4 EOS > stepBack
		c2 EOS > stepBack
		c3 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		NoveltyTermination s1=c2 s2=avatar win=True args={item:key,num:0,negated:False,operator_name:>}
		NoveltyTermination s1=c3 s2=avatar win=True args={item:key,num:0,negated:False,operator_name:>}
		NoveltyTermination s1=c4 s2=avatar win=True args={item:key,num:0,negated:False,operator_name:>}
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		2 > c2
		1 > avatar
		0 > c3
		3 > c4
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
