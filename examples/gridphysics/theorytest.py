level="""
000000000000000000000000
0000    0   00A      000
0     0 0       00    00
0         00    000   20
0 0000 00000    00   000
02       0            00
00   02     00   000   0
00    00   0000    0   0
000              0    20
0000002     000000    00
000000000000000000000000
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=WHITE
		c3 > Resource color=DARKGRAY
		c2 > Resource color=BLUE
		c5 > ResourcePack color=ORANGE
		c4 > Resource color=BROWN
	InteractionSet
		c2 avatar > transformTo stype=c4
		c5 c2 > killSprite
		c2 c5 > killSprite
		c4 EOS > stepBack
		c5 c3 > killSprite
		c3 c5 > killSprite
		c5 EOS > stepBack
		c2 c3 > stepBack
		c4 c2 > killSprite
		c2 c4 > transformTo stype=c5
		c2 c2 > killSprite
		avatar c5 > killSprite
		c3 c3 > killSprite
		c4 c3 > killSprite
		c3 c4 > killSprite
		c2 EOS > stepBack
		c4 avatar > nothing
		c3 EOS > stepBack
		avatar c3 > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c4 s2=c3 win=True
		SpriteCounter stype=c2 limit=0 win=True
		NoveltyTermination s1=c5 s2=c2 win=True
		NoveltyTermination s1=c5 s2=c3 win=True
		SpriteCounter stype=c4 limit=0 win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		1 > c5
		0 > c3
		A > avatar
		2 > c2
		3 > c4
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
