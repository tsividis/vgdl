level="""
333333333333333333333333
3                      3
3                      3
3   02                 3
3                      3
3     1                3
3                  1   3
3                      3
3                      3
3                      3
3                      3
3   4              4   3
333333333333333333333333
"""
game = """
BasicGame
	SpriteSet
		explosion > Flicker color=PINK singleton=True limit=5
		avatar > ShootAvatar color=DARKBLUE stype=explosion
		c3 > ResourcePack color=DARKGRAY
		c6 > RandomNPC color=GOLD speed=0.3 cooldown=1
		c5 > RandomNPC color=RED speed=0.1 cooldown=1
		c4 > ResourcePack color=GREEN
	InteractionSet
		c3 c5 > nothing
		c5 c3 > nothing
		avatar c6 > nothing
		explosion c3 > nothing
		c5 explosion > killSprite
		c6 explosion > nothing
		explosion c6 > nothing
		c4 c5 > nothing
		c5 c4 > nothing
		avatar c3 > stepBack
		explosion explosion > killSprite
		avatar EOS > stepBack
		c3 c4 > nothing
		c4 c3 > nothing
		c6 c4 > nothing
		c4 c6 > nothing
		c4 explosion > nothing
		c6 c5 > nothing
		c5 c6 > nothing
		avatar c4 > nothing
		c6 c3 > nothing
		c3 c6 > nothing
		avatar c5 > nothing
		avatar explosion > nothing
		c3 c3 > nothing
		c5 c5 > nothing
		c4 c4 > nothing
		explosion EOS > stepBack
		c5 EOS > stepBack
		c4 EOS > stepBack
		c3 EOS > stepBack
		c6 EOS > stepBack
	TerminationSet
		NoveltyTermination s1=explosion s2=explosion win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=explosion s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=c5 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		NoveltyTermination s1=c6 s2=EOS win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		0 > explosion
		1 > c6
		2 > avatar
		3 > c3
		6 > avatar explosion
		7 > avatar c4
		b > avatar c5
		4 > c4
		8 > explosion c3
		9 > c4 explosion
		5 > c5
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
