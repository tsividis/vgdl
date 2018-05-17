level="""
222222222222222222
2 0 4   2    1   2
2   4   2    22222
2 3 4         4  2
222222222222222222
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=BLACK
		c2 > ResourcePack color=ORANGE
		c6 > Chaser color=WHITE fleeing=True cooldown=9 stype=c5
		c5 > ResourcePack color=PINK
		c4 > ResourcePack color=GOLD
		medicine > Resource color=RESOURCETOADD limit=4
	InteractionSet
		c2 avatar > killSprite
		c2 avatar > killIfOtherHasMore resource=medicine limit=1
		c2 c4 > nothing
		c4 c2 > nothing
		avatar c6 > changeResource resource=medicine limit=4 value=1
		c6 avatar > killSprite
		c5 c4 > nothing
		c4 c5 > nothing
		c5 c3 > nothing
		c3 c5 > nothing
		c3 avatar > killIfOtherHasMore resource=medicine limit=1
		avatar c3 > stepBack
		c5 c2 > nothing
		c2 c5 > nothing
		avatar EOS > stepBack
		c3 c4 > nothing
		c4 c3 > nothing
		c6 c2 > nothing
		c2 c6 > nothing
		c6 c4 > nothing
		c4 c6 > nothing
		c2 c2 > nothing
		c3 c3 > nothing
		c6 c3 > nothing
		c3 c6 > nothing
		c2 c3 > nothing
		c3 c2 > nothing
		avatar c5 > changeResource resource=medicine limit=4 value=-1
		c5 avatar > killSprite
		avatar c5 > killSprite
		c4 avatar > killSprite
		c4 avatar > killIfOtherHasMore resource=medicine limit=1
		c4 c4 > nothing
		c5 EOS > stepBack
		c4 EOS > stepBack
		c3 EOS > stepBack
		c6 EOS > stepBack
		c2 EOS > stepBack
	TerminationSet
		MultiSpriteCounter stype0=c6 stype1=c2 limit=0 win=True
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		NoveltyTermination s1=c5 s2=EOS win=True
		NoveltyTermination s1=c5 s2=c2 win=True
		NoveltyTermination s1=c5 s2=c3 win=True
		NoveltyTermination s1=c5 s2=c4 win=True
		NoveltyTermination s1=c6 s2=EOS win=True
		NoveltyTermination s1=c6 s2=c2 win=True
		NoveltyTermination s1=c6 s2=c3 win=True
		NoveltyTermination s1=c6 s2=c4 win=True
		NoveltyTermination s1=c3 s2=avatar win=True args={item:medicine,num:0,negated:False,operator_name:>}
		NoveltyTermination s1=c4 s2=avatar win=True args={item:medicine,num:0,negated:False,operator_name:>}
		NoveltyTermination s1=c2 s2=avatar win=True args={item:medicine,num:0,negated:False,operator_name:>}
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c4 limit=0 win=True
		SpriteCounter stype=c5 limit=0 win=True
	LevelMapping
		4 > c5
		3 > c4
		1 > avatar
		2 > c3
		0 > c2
		5 > c6
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
