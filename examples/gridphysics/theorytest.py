level="""
555555555
5 32 2 25
555555555
"""
game = """
BasicGame
	SpriteSet
		c3 > Chaser color=BLACK fleeing=True cooldown=5
		c2 > Chaser color=BLUE fleeing=True cooldown=5
		avatar > MovingAvatar color=DARKBLUE
	InteractionSet
		c2 avatar > bounceForward
		c2 c3 > bounceForward
		c3 c2 > nothing
		c2 c2 > bounceForward
		c3 c3 > killSprite
		avatar EOS > stepBack
		c2 EOS > undoAll
		c3 EOS > bounceForward
		c3 avatar > nothing
	TerminationSet
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c3 s2=c2 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		2 > c2
		3 > avatar
		5 > c3
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
