level="""
1111111111111111111111
13            1     11
1                    1
12            0      1
1111111111111111111111
"""
game = """
BasicGame
	SpriteSet
		c3 > RandomNPC color=DARKGRAY speed=1.6 cooldown=10
		c2 > RandomNPC color=PINK speed=1.6 cooldown=10
		avatar > MovingAvatar color=DARKBLUE
		c4 > RandomNPC color=LIGHTBLUE speed=1.6 cooldown=10
	InteractionSet
		c2 avatar > killSprite
		c2 c4 > nothing
		c4 c2 > nothing
		c2 c3 > nothing
		c3 c2 > nothing
		c2 c2 > nothing
		c3 c3 > nothing
		avatar EOS > stepBack
		avatar c3 > stepBack
		c4 avatar > nothing
		c4 c4 > nothing
		c3 c4 > nothing
		c4 c3 > nothing
		c4 EOS > stepBack
		c2 EOS > stepBack
		c3 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=avatar win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		0 > c2
		1 > c3
		2 > avatar
		4 > avatar c4
		3 > c4
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
