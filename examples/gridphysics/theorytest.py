level="""
                              
                        2     
                              
                              
                              
                              
                              
                              
                              
                              
                      9       
"""
game = """
BasicGame
	SpriteSet
		sam > Missile color=PINK singleton=True orientation=UP
		avatar > FlakAvatar color=DARKBLUE stype=sam
		c3 > ResourcePack color=LIGHTGRAY
		c5 > Missile color=RED speed=0.5 orientation=DOWN cooldown=1
		c4 > Missile color=GOLD speed=0.8 orientation=RIGHT cooldown=3
	InteractionSet
		sam EOS > killSprite
		c5 c3 > nothing
		c3 c5 > nothing
		c4 sam > killSprite
		c4 EOS > turnAround
		sam sam > nothing
		sam c3 > nothing
		c3 sam > nothing
		avatar c5 > killSprite
		c3 c3 > nothing
		avatar EOS > stepBack
		c4 c3 > nothing
		c3 c4 > nothing
		c5 EOS > killSprite
		sam avatar > nothing
		c4 avatar > killSprite
		c5 c4 > nothing
		c4 c5 > nothing
		c3 avatar > killSprite
		c5 sam > nothing
		sam c5 > nothing
		c3 EOS > stepBack
	TerminationSet
		MultiSpriteCounter stype0=c4 stype1=c3 limit=0 win=True
		MultiSpriteCounter stype0=c5 stype1=c3 stype2=c4 limit=0 win=True
		NoveltyTermination s1=sam s2=sam win=True
		NoveltyTermination s1=sam s2=c3 win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=avatar win=True
		NoveltyTermination s1=c4 s2=c3 win=True
		NoveltyTermination s1=c5 s2=sam win=True
		NoveltyTermination s1=c5 s2=c3 win=True
		NoveltyTermination s1=c5 s2=c4 win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		0 > sam
		1 > c3
		2 > c4
		3 > avatar
		9 > avatar sam
		8 > c4 c3
		b > c4 c5 c3
		c > c4 c5
		7 > c5
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
