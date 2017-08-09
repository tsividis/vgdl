level="""
4444444444444444444444444444
                   4 7 4    
0009900000099900009999900099
00000999900000000009999000b9
0009990009990009999000099909
444   44   444    444  44444
    8 8     88   8  8  8    
  66  66  66  66 6   66 6   
  88     8      88 8  8  88 
4       3                  4
4444444444444444444444444444
"""
game = """
BasicGame
	SpriteSet
		c8 > RandomNPC color=JIOQMO cooldown=2
		avatar > MovingAvatar color=DARKBLUE
		c3 > Missile color=BROWN speed=0.5 orientation=LEFT
		c2 > ResourcePack color=BLUE
		c7 > ResourcePack color=GREEN
		c6 > Missile color=YELLOW speed=0.2 orientation=RIGHT
		c5 > Missile color=DTIZDF speed=0.5 orientation=RIGHT
		c4 > ResourcePack color=DARKGRAY
		safety > Resource color=RESOURCETOADD limit=4
	InteractionSet
		c3 c5 > killSprite
		c5 c3 > killSprite
		c6 c7 > killSprite
		c7 c6 > killSprite
		c2 c4 > killSprite
		c4 c2 > killSprite
		c5 EOS > wrapAround offset=0
		avatar c6 > killSprite
		c6 avatar > killIfOtherHasMore resource=safety limit=1
		c4 c5 > killSprite
		c5 c4 > killSprite
		c3 c4 > killSprite
		c4 c3 > killSprite
		c2 c5 > killSprite
		c5 c2 > killSprite
		c7 avatar > changeScore value=1
		c7 avatar > killSprite
		c7 avatar > killIfOtherHasMore resource=safety limit=1
		c8 c2 > killSprite
		c2 c8 > killSprite
		c5 c7 > killSprite
		c7 c5 > killSprite
		avatar c3 > changeResource resource=safety limit=4 value=1
		avatar c3 > pullWithIt
		c8 c4 > killSprite
		c4 c8 > killSprite
		c8 c5 > killSprite
		c5 c8 > killSprite
		c8 c6 > killSprite
		c6 c8 > killSprite
		c2 c6 > killSprite
		c6 c2 > killSprite
		c8 c3 > killSprite
		c3 c8 > killSprite
		c4 c6 > killSprite
		c6 c4 > killSprite
		c3 c7 > killSprite
		c7 c3 > killSprite
		c2 c2 > nothing
		c5 c6 > nothing
		c3 c3 > nothing
		c8 c7 > killSprite
		c7 c8 > killSprite
		c3 EOS > wrapAround offset=0
		c2 c7 > killSprite
		c7 c2 > killSprite
		avatar c8 > killSprite
		c4 c7 > killSprite
		c7 c4 > killSprite
		c3 c6 > killSprite
		c6 c3 > killSprite
		c6 c6 > killSprite
		c2 c3 > nothing
		c7 c7 > killSprite
		c6 EOS > wrapAround offset=0
		avatar c5 > killSprite
		c5 avatar > killIfOtherHasMore resource=safety limit=1
		c4 avatar > killIfOtherHasMore resource=safety limit=1
		avatar c4 > stepBack
		c5 c5 > killSprite
		avatar c2 > changeResource resource=safety limit=4 value=-1
		c4 c4 > killSprite
		c8 EOS > stepBack
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
		NoveltyTermination s1=c8 s2=c2 win=True
		NoveltyTermination s1=c8 s2=c3 win=True
		NoveltyTermination s1=c8 s2=c4 win=True
		NoveltyTermination s1=c8 s2=c5 win=True
		NoveltyTermination s1=c8 s2=c6 win=True
		NoveltyTermination s1=c8 s2=c7 win=True
		NoveltyTermination s1=c5 s2=avatar win=True
		NoveltyTermination s1=c6 s2=avatar win=True
		NoveltyTermination s1=c4 s2=avatar win=True
		NoveltyTermination s1=c7 s2=avatar win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c7 limit=0 win=True
	LevelMapping
		0 > c2
		1 > c3
		b > c2 c2
		3 > avatar
		4 > c4
		e > avatar c2
		5 > c5
		6 > c6
		c > c5 c6
		f > avatar c3 c2
		7 > c7
		8 > c8
		9 > c3 c2
		d > c2 c3 c2
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
