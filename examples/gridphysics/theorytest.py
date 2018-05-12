level="""
1 2   2   2   2       2    2  
666                           
666  7                        
                              
          6      7            
          6                   
                              
                              
  6                      66   
  6        6             6    
                          3   
"""
game = """
BasicGame
	SpriteSet
		sam > Missile color=PINK singleton=True orientation=UP
		avatar > FlakAvatar color=DARKBLUE stype=sam
		c3 > ResourcePack color=LIGHTGRAY
		c7 > Missile color=LIGHTGREEN speed=0.8 orientation=RIGHT cooldown=3
		c6 > Missile color=RED speed=0.5 orientation=DOWN cooldown=1
		c5 > Missile color=GOLD speed=0.8 orientation=RIGHT cooldown=3
		c4 > ResourcePack color=WHITE
	InteractionSet
		sam EOS > killSprite
		c7 c6 > nothing
		c6 c7 > nothing
		c5 c3 > nothing
		c3 c5 > nothing
		sam c3 > nothing
		c3 sam > nothing
		avatar c6 > killSprite
		c4 c5 > killSprite
		c3 avatar > killSprite
		c5 sam > killSprite
		c6 sam > nothing
		sam c6 > nothing
		c7 avatar > killSprite
		sam sam > nothing
		c7 c5 > nothing
		c5 c7 > nothing
		avatar EOS > stepBack
		c3 c4 > nothing
		c4 c3 > nothing
		c5 EOS > turnAround
		c4 sam > killSprite
		sam c4 > killSprite
		c4 c6 > killSprite
		c6 c4 > killSprite
		c7 c3 > nothing
		c3 c7 > nothing
		c6 c5 > nothing
		c5 c6 > nothing
		c7 EOS > turnAround
		c4 avatar > killSprite
		c7 c4 > nothing
		c4 c7 > nothing
		c6 c3 > nothing
		c3 c6 > nothing
		c6 EOS > killSprite
		c7 sam > killSprite
		c5 avatar > killSprite
		c3 c3 > nothing
		sam avatar > nothing
		c4 c4 > nothing
		c4 EOS > stepBack
		c3 EOS > stepBack
	TerminationSet
		MultiSpriteCounter stype0=c7 stype1=c3 limit=0 win=True
		MultiSpriteCounter stype0=c7 stype1=c3 stype2=c5 limit=0 win=True
		MultiSpriteCounter stype0=c7 stype1=c3 stype2=c6 limit=0 win=True
		MultiSpriteCounter stype0=c7 stype1=c3 stype2=c6 stype3=c5 limit=0 win=True
		NoveltyTermination s1=sam s2=sam win=True
		NoveltyTermination s1=sam s2=c3 win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c4 s2=avatar win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=c5 s2=avatar win=True
		NoveltyTermination s1=c5 s2=c3 win=True
		NoveltyTermination s1=c6 s2=sam win=True
		NoveltyTermination s1=c6 s2=c3 win=True
		NoveltyTermination s1=c6 s2=c5 win=True
		NoveltyTermination s1=c7 s2=avatar win=True
		NoveltyTermination s1=c7 s2=c6 win=True
		NoveltyTermination s1=c7 s2=c5 win=True
		NoveltyTermination s1=c7 s2=c3 win=True
		NoveltyTermination s1=c7 s2=c4 win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c4 limit=0 win=True
	LevelMapping
		0 > sam
		1 > c3
		2 > c5
		3 > avatar
		d > c7 c6
		9 > avatar sam
		c > c7 c3
		8 > c5 c3
		5 > c7
		6 > c4
		b > c5 c6
		7 > c6
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
