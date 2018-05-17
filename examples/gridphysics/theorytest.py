level="""
333333333333333333
3 4 0   3 2      3
3   0   3    33333
3 1 0         0  3
333333333333333333
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=ORANGE
		c2 > RandomNPC color=PINK speed=0.6 cooldown=3
		c6 > ResourcePack color=GOLD
		c5 > RandomNPC color=BLACK speed=0.7 cooldown=1
		c4 > Missile color=WHITE speed=2.1 orientation=LEFT cooldown=3
		medicine > Resource color=RESOURCETOADD limit=4
	InteractionSet
		c2 avatar > killIfOtherHasMore resource=medicine limit=1
		c2 avatar > nothing
		c2 c4 > nothing
		c4 c2 > turnAround
		c5 EOS > bounceForward
		c6 avatar > killIfOtherHasMore resource=medicine limit=1
		c6 avatar > turnAround
		c4 c5 > nothing
		c5 c4 > nothing
		c3 c5 > killSprite
		c5 c3 > nothing
		c3 c4 > nothing
		c4 c3 > nothing
		c2 c5 > wrapAround
		c5 c2 > nothing
		avatar EOS > stepBack
		c3 avatar > killSprite
		c3 avatar > killIfOtherHasMore resource=medicine limit=1
		c2 c6 > killSprite
		c6 c2 > nothing
		c4 c6 > nothing
		c6 c4 > nothing
		c2 c2 > nothing
		c5 c6 > nothing
		c6 c5 > nothing
		c3 c3 > nothing
		c3 c6 > nothing
		c6 c3 > turnAround
		c6 c6 > wrapAround
		c2 c3 > reverseDirection
		c3 c2 > nothing
		avatar c5 > stepBack
		avatar c4 > changeResource resource=medicine limit=4 value=1
		c4 avatar > killIfOtherHasMore resource=medicine limit=1
		c4 avatar > stepBack
		c5 c5 > nothing
		c4 EOS > stepBack
		c3 EOS > stepBack
		c6 EOS > stepBack
		c2 EOS > stepBack
		c4 c4 > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=c6 win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c3 s2=c6 win=True
		NoveltyTermination s1=c4 s2=c6 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=c5 s2=EOS win=True
		NoveltyTermination s1=c6 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		NoveltyTermination s1=c3 s2=avatar win=True args={item:medicine,num:0,negated:False,operator_name:>}
		NoveltyTermination s1=c6 s2=avatar win=True args={item:medicine,num:0,negated:False,operator_name:>}
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
