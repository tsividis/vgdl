level="""
111111111
11   1  1
1       1
1   1 211
1   11111
1  01 2 1
1     A11
11     11
111111111
"""
game = """
BasicGame
	SpriteSet
		c3 > Resource color=DARKGRAY
		c2 > ResourcePack color=PINK
		avatar > MovingAvatar color=DARKBLUE
		c4 > Resource color=LIGHTBLUE
	InteractionSet
		c2 avatar > nothing
		c4 EOS > stepBack
		c4 c2 > killSprite
		c2 c3 > killSprite
		c3 c2 > killSprite
		c2 c2 > killSprite
		c3 c3 > killSprite
		c4 c3 > undoAll
		c2 EOS > stepBack
		c4 avatar > bounceForward
		c3 EOS > stepBack
		c4 c4 > undoAll
		avatar c3 > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		SpriteCounter stype=c4 limit=0 win=True
		SpriteCounter stype=c4 limit=0 win=True
	LevelMapping
		2 > c2
		0 > c4
		A > avatar
		1 > c3
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
