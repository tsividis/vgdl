level="""
1                             
888                           
888                           
                              
                              
                              
                              
    888      888888     888   
   88888    88888888   88888  
   8   8    88    88   88888  
                7             
"""
game = """
BasicGame
	SpriteSet
		c3 > ResourcePack color=LIGHTGRAY
		avatar > FlakAvatar color=DARKBLUE stype=sam
		sam > Missile color=PINK singleton=True orientation=UP
		c4 > ResourcePack color=WHITE
	InteractionSet
		sam c4 > nothing
		c4 sam > nothing
		sam sam > nothing
		sam c3 > nothing
		c3 sam > nothing
		c3 c3 > nothing
		avatar EOS > stepBack
		c3 c4 > nothing
		c4 c3 > nothing
		sam avatar > killSprite
		c4 avatar > killSprite
		c4 c4 > nothing
		c3 avatar > killSprite
		sam EOS > stepBack
		c4 EOS > stepBack
		c3 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=sam s2=avatar win=True
		NoveltyTermination s1=sam s2=sam win=True
		NoveltyTermination s1=sam s2=c3 win=True
		NoveltyTermination s1=sam s2=c4 win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c4 s2=avatar win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=sam s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		0 > sam
		1 > c3
		7 > avatar
		8 > c4
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
