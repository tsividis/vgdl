level="""
4444444444444444444444444444
           4 7 4            
0009900000099900009999900099
00000999900000000009999000c9
0009990009990009999000099909
444   44   444    444  44444
    6666   666   6  6666    
 6     555       555    55  
  6   666     6   6666 66   
4       3                  4
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
	InteractionSet
		c2 avatar > killSprite
		c6 c7 > nothing
		c7 c6 > nothing
		c2 c4 > nothing
		c4 c2 > nothing
		c5 EOS > wrapAround offset=0
		avatar c6 > killSprite
		c4 c5 > nothing
		c5 c4 > nothing
		c3 c5 > nothing
		c5 c3 > nothing
		c3 c4 > nothing
		c4 c3 > nothing
		c2 c5 > nothing
		c5 c2 > nothing
		c7 avatar > killSprite
		c5 c7 > nothing
		c7 c5 > nothing
		avatar EOS > stepBack
		c3 avatar > killSprite
		c2 c6 > nothing
		c6 c2 > nothing
		c4 c6 > nothing
		c6 c4 > nothing
		c3 c7 > nothing
		c7 c3 > nothing
		c2 c2 > nothing
		c5 c6 > nothing
		c6 c5 > nothing
		c3 c3 > nothing
		c2 c7 > nothing
		c7 c2 > nothing
		c4 c7 > nothing
		c7 c4 > nothing
		c3 c6 > nothing
		c6 c3 > nothing
		c6 c6 > nothing
		c2 c3 > nothing
		c7 c7 > nothing
		avatar c5 > killSprite
		avatar c4 > stepBack
		c5 c5 > nothing
		c4 c4 > nothing
		c4 EOS > stepBack
		c7 EOS > stepBack
		c3 EOS > stepBack
		c6 EOS > stepBack
		c2 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=avatar win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c2 s2=c5 win=True
		NoveltyTermination s1=c2 s2=c6 win=True
		NoveltyTermination s1=c2 s2=c7 win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c3 s2=c6 win=True
		NoveltyTermination s1=c3 s2=c7 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c5 win=True
		NoveltyTermination s1=c4 s2=c6 win=True
		NoveltyTermination s1=c4 s2=c7 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c5 s2=c6 win=True
		NoveltyTermination s1=c5 s2=c7 win=True
		NoveltyTermination s1=c6 s2=c6 win=True
		NoveltyTermination s1=c6 s2=c7 win=True
		NoveltyTermination s1=c7 s2=avatar win=True
		NoveltyTermination s1=c7 s2=c7 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=c6 s2=EOS win=True
		NoveltyTermination s1=c7 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		0 > c2
		1 > c3
		c > c2 c2
		3 > avatar
		4 > c4
		5 > c5
		6 > c6
		7 > c7
		9 > c3 c2
		b > c2 c3 c2
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
