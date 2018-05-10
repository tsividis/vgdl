level="""
               2              
666                           
666                           
                              
                              
                              
                              
      6      666666     666   
   66666     6  6666   66666  
   6   6    66    6    66666  
               3              
"""
game = """
BasicGame
	SpriteSet
		sam > Missile color=PINK singleton=True orientation=UP
		avatar > FlakAvatar color=DARKBLUE stype=sam
		c3 > ResourcePack color=LIGHTGRAY
		c7 > Missile color=GOLD speed=0.8 orientation=RIGHT cooldown=3
		c6 > Missile color=LIGHTGREEN speed=0.5 orientation=RIGHT cooldown=10
		c5 > Missile color=RED speed=0.5 orientation=DOWN cooldown=1
		c4 > ResourcePack color=WHITE
	InteractionSet
		c3 c5 > nothing
		c5 c3 > nothing
		c7 c6 > nothing
		c6 c7 > nothing
		sam sam > nothing
		sam c3 > nothing
		c3 sam > nothing
		c6 avatar > killSprite
		c4 c5 > killSprite
		c5 c4 > killSprite
		c3 avatar > killSprite
		sam c5 > nothing
		c5 sam > nothing
		sam EOS > killSprite
		c7 avatar > killSprite
		c7 c5 > nothing
		c5 c7 > nothing
		avatar EOS > stepBack
		c3 c4 > nothing
		c4 c3 > nothing
		c5 EOS > killSprite
		c6 sam > killSprite
		c4 sam > killSprite
		sam c4 > killSprite
		c4 c6 > nothing
		c6 c4 > nothing
		c7 c3 > nothing
		c3 c7 > nothing
		c5 c6 > nothing
		c6 c5 > nothing
		c3 c3 > nothing
		c7 c4 > nothing
		c4 c7 > nothing
		c3 c6 > nothing
		c6 c3 > nothing
		c6 c6 > nothing
		c7 sam > killSprite
		avatar c5 > killSprite
		c4 avatar > killSprite
		c5 c5 > nothing
		sam avatar > nothing
		c4 c4 > nothing
		c4 EOS > stepBack
		c7 EOS > stepBack
		c3 EOS > stepBack
		c6 EOS > stepBack
	TerminationSet
		MultiSpriteCounter stype0=c7 stype1=c3 limit=0 win=True
		MultiSpriteCounter stype0=c5 stype1=c7 limit=0 win=True
		MultiSpriteCounter stype0=c7 stype1=c3 stype2=c5 limit=0 win=True
		MultiSpriteCounter stype0=c7 stype1=c3 stype2=c6 limit=0 win=True
		MultiSpriteCounter stype0=c5 stype1=c7 stype2=c6 limit=0 win=True
		MultiSpriteCounter stype0=c7 stype1=c3 stype2=c6 stype3=c5 limit=0 win=True
		NoveltyTermination s1=sam s2=sam win=True
		NoveltyTermination s1=sam s2=c3 win=True
		NoveltyTermination s1=sam s2=c5 win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c3 s2=c5 win=True
		NoveltyTermination s1=c3 s2=c6 win=True
		NoveltyTermination s1=c4 s2=avatar win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c6 win=True
		NoveltyTermination s1=c5 s2=c5 win=True
		NoveltyTermination s1=c5 s2=c6 win=True
		NoveltyTermination s1=c6 s2=avatar win=True
		NoveltyTermination s1=c6 s2=c6 win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=c6 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		NoveltyTermination s1=c7 s2=avatar win=True
		NoveltyTermination s1=c7 s2=EOS win=True
		NoveltyTermination s1=c7 s2=c3 win=True
		NoveltyTermination s1=c7 s2=c4 win=True
		NoveltyTermination s1=c7 s2=c5 win=True
		NoveltyTermination s1=c7 s2=c6 win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c4 limit=0 win=True
	LevelMapping
		0 > sam
		1 > c3
		b > c5 sam
		2 > c7
		3 > avatar
		8 > avatar sam
		c > c7 c3
		5 > c6
		6 > c4
		9 > c7 c5
		7 > c5
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
