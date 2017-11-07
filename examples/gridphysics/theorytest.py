level="""
22222222
2     32
2      2
2      2
2 1 2222
22     2
2      2
2  0   2
22222222
"""
game = """
BasicGame
	SpriteSet
		c3 > RandomNPC color=GREEN speed=1.6 cooldown=5
		c2 > RandomNPC color=BLACK speed=1.6 cooldown=5
		avatar > MovingAvatar color=WHITE
		c4 > Missile color=GOLD speed=1.3 orientation=DOWN cooldown=9
	InteractionSet
		c2 avatar > killSprite
		c2 c4 > nothing
		c4 c2 > nothing
		c2 c3 > nothing
		c3 c2 > nothing
		c2 c2 > nothing
		c3 c3 > nothing
		avatar EOS > stepBack
		c3 c4 > nothing
		c4 c3 > nothing
		c4 avatar > killSprite
		c4 c4 > nothing
		c3 avatar > killSprite
		c4 EOS > stepBack
		c2 EOS > stepBack
		c3 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=avatar win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c4 s2=avatar win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		2 > c2
		1 > avatar
		0 > c3
		3 > c4
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
