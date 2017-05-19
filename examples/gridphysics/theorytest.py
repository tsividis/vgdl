level="""
000000000000000000000000
0000  3 03  00      2000
0     0 0       00    00
03        00    000    0
0 0000 00000    00   000
0        0            00
00   03     00   000  20
00    00   0000    0 A 0
000              0     0
0000002     000000    00
000000000000000000000000
"""
game = """
BasicGame
	SpriteSet
		c3 > Resource color=DARKGRAY
		c2 > Chaser color=BLUE speed=1 fleeing=True
		avatar > MovingAvatar color=WHITE
		c4 > Resource color=BROWN
	InteractionSet
		c2 avatar > transformTo stype=c4
		c4 EOS > stepBack
		c4 c2 > killSprite
		c2 c4 > killSprite
		c2 c3 > stepBack
		c2 c2 > killSprite
		c3 c3 > killSprite
		c4 c3 > killSprite
		c3 c4 > killSprite
		c2 EOS > stepBack
		c4 avatar > nothing
		c3 EOS > stepBack
		avatar c3 > stepBack
	TerminationSet
		SpriteCounter stype=avatar limit=0 win=False
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c4 s2=c2 win=True
		NoveltyTermination s1=c4 s2=c3 win=True
		SpriteCounter stype=c2 limit=0 win=True
	LevelMapping
		0 > c3
		A > avatar
		2 > c2
		3 > c4
		G > goal
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
