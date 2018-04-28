level="""
4444444444444444444444444444
     4 7 4                  
0900990099909909999909099999
00999900099009909999009999b9
0990009990009999099099909009
444 3 44   444    444  44444
  5       5 5     55   5  5 
6    66  66  66  66 6   66  
 5  55  55     5      55 5  
4                          4
4444444444444444444444444444
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > Missile color=BROWN speed=0.1 orientation=LEFT cooldown=1
		c2 > ResourcePack color=BLUE
		c7 > ResourcePack color=GREEN
		c6 > Missile color=YELLOW speed=0.1 orientation=RIGHT cooldown=1
		c5 > Missile color=DTIZDF speed=0.2 orientation=RIGHT cooldown=1
		c4 > ResourcePack color=DARKGRAY
		safety > Resource color=RESOURCETOADD limit=4
	InteractionSet
		c3 c5 > nothing
		c5 c3 > nothing
		c6 c7 > nothing
		c7 c6 > nothing
		c2 c4 > nothing
		c4 c2 > nothing
		c5 EOS > wrapAround offset=0
		avatar c6 > killSprite
		c6 avatar > killIfOtherHasMore resource=safety limit=4
		c6 avatar > killIfOtherHasMore resource=safety limit=1
		c4 c5 > nothing
		c5 c4 > nothing
		c3 c4 > nothing
		c4 c3 > nothing
		c2 c5 > nothing
		c5 c2 > nothing
		c7 avatar > killSprite
		c7 avatar > killIfOtherHasMore resource=safety limit=4
		c5 c7 > nothing
		c7 c5 > nothing
		avatar EOS > stepBack
		avatar c3 > changeResource resource=safety limit=4 value=1
		avatar c3 > pullWithIt
		c2 c6 > nothing
		c6 c2 > nothing
		c4 c6 > nothing
		c6 c4 > nothing
		c3 c7 > nothing
		c7 c3 > nothing
		c2 c2 > nothing
		c5 c6 > nothing
		c3 c3 > nothing
		c3 EOS > wrapAround offset=0
		c2 c7 > nothing
		c7 c2 > nothing
		c4 c7 > nothing
		c7 c4 > nothing
		c3 c6 > nothing
		c6 c3 > nothing
		c6 c6 > nothing
		c2 c3 > nothing
		c7 c7 > nothing
		c6 EOS > wrapAround offset=0
		avatar c5 > killSprite
		c5 avatar > killIfOtherHasMore resource=safety limit=1
		c5 avatar > killIfOtherHasMore resource=safety limit=4
		c4 avatar > killIfOtherHasMore resource=safety limit=1
		c4 avatar > killIfOtherHasMore resource=safety limit=4
		avatar c4 > stepBack
		c5 c5 > nothing
		avatar c2 > killIfHasLess resource=safety limit=0
		avatar c2 > changeResource limit=4 resource=safety value=-1
		c4 c4 > nothing
		c4 EOS > stepBack
		c7 EOS > stepBack
		c2 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c2 s2=c5 win=True
		NoveltyTermination s1=c2 s2=c6 win=True
		NoveltyTermination s1=c2 s2=c7 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c3 s2=c6 win=True
		NoveltyTermination s1=c3 s2=c7 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c5 win=True
		NoveltyTermination s1=c4 s2=c6 win=True
		NoveltyTermination s1=c4 s2=c7 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c5 s2=c7 win=True
		NoveltyTermination s1=c6 s2=c6 win=True
		NoveltyTermination s1=c6 s2=c7 win=True
		NoveltyTermination s1=c7 s2=c7 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=c7 s2=EOS win=True
		NoveltyTermination s1=c5 s2=avatar win=True args={item:safety,num:0,negated:False,operator_name:>}
		NoveltyTermination s1=c4 s2=avatar win=True args={item:safety,num:0,negated:False,operator_name:>}
		NoveltyTermination s1=c6 s2=avatar win=True args={item:safety,num:4,negated:False,operator_name:>=}
		NoveltyTermination s1=c7 s2=avatar win=True args={item:safety,num:4,negated:False,operator_name:>=}
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c7 limit=0 win=True
	LevelMapping
		0 > c2
		1 > c3
		3 > avatar
		4 > c4
		5 > c5
		6 > c6
		c > c5 c6
		d > avatar c3 c2
		7 > c7
		9 > c3 c2
		b > c2 c3 c2
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
