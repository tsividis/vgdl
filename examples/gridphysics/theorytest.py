level="""
1  2    2   2   2    2        
88                            
88             9              
                              
                              
                              
         9                    
             88  8      888   
   8888      8889      88888  
   8        88  9    0 88888  
                     7        
"""
game = """
BasicGame
	SpriteSet
		sam > Missile color=PINK singleton=True orientation=UP
		avatar > FlakAvatar color=DARKBLUE stype=sam
		c3 > ResourcePack color=LIGHTGRAY
		c6 > Missile color=RED speed=0.5 orientation=DOWN cooldown=1
		c5 > Missile color=GOLD speed=0.8 orientation=RIGHT cooldown=3
		c4 > ResourcePack color=WHITE
	InteractionSet
		c5 c3 > nothing
		c3 c5 > nothing
		sam sam > nothing
		sam c3 > nothing
		c3 sam > nothing
		c6 avatar > killSprite
		c5 c4 > nothing
		c4 c5 > nothing
		c3 avatar > killSprite
		c5 sam > nothing
		sam c5 > nothing
		c6 sam > nothing
		sam c6 > nothing
		avatar EOS > stepBack
		c3 c4 > nothing
		c4 c3 > nothing
		c4 sam > killSprite
		sam c4 > killSprite
		c4 c6 > killSprite
		c6 c4 > killSprite
		c6 c5 > nothing
		c5 c6 > nothing
		c4 avatar > killSprite
		sam EOS > killSprite
		c6 c3 > nothing
		c3 c6 > nothing
		c6 EOS > killSprite
		c5 avatar > killSprite
		c3 c3 > nothing
		sam avatar > nothing
		c4 c4 > nothing
		c4 EOS > stepBack
		c5 EOS > stepBack
		c3 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=sam s2=sam win=True
		NoveltyTermination s1=sam s2=c3 win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c4 s2=avatar win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		NoveltyTermination s1=c5 s2=avatar win=True
		NoveltyTermination s1=c5 s2=EOS win=True
		NoveltyTermination s1=c5 s2=sam win=True
		NoveltyTermination s1=c5 s2=c3 win=True
		NoveltyTermination s1=c5 s2=c4 win=True
		NoveltyTermination s1=c6 s2=avatar win=True
		NoveltyTermination s1=c6 s2=sam win=True
		NoveltyTermination s1=c6 s2=c3 win=True
		NoveltyTermination s1=c6 s2=c5 win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c4 limit=0 win=True
	LevelMapping
		0 > sam
		1 > c3
		2 > c5
		c > avatar sam
		b > c5 c3
		7 > avatar
		8 > c4
		d > c5 c6
		9 > c6
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
