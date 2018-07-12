level="""
88888888888888888888888888888888
8                              8
8                              8
8                              8
8                              8
8                              8
8                           b d8
8             c   c            8
888                           d8
88888888888888888888888888888888
"""
game = """
BasicGame
	SpriteSet
		avatar > MovingAvatar color=DARKBLUE
		c3 > ResourcePack color=PINK
		c2 > ResourcePack color=DARKGRAY
		c5 > Chaser color=LIGHTGREEN cooldown=1 stype=c4 fleeing=False
		c4 > ResourcePack color=YELLOW
	InteractionSet
		c2 avatar > killSprite
		avatar c2 > stepBack
		c2 c5 > nothing
		c5 c2 > nothing
		avatar avatar > stepBack
		c4 c5 > nothing
		c5 c4 > nothing
		c2 c4 > nothing
		c4 c2 > nothing
		c5 EOS > nothing
		c2 c3 > nothing
		c3 c2 > nothing
		c2 c2 > nothing
		c5 avatar > killSprite
		avatar c5 > stepBack
		c4 avatar > killSprite
		avatar c4 > stepBack
		avatar EOS > stepBack
		c3 c4 > nothing
		c4 c3 > nothing
		c5 c5 > nothing
		c2 EOS > nothing
		c4 EOS > nothing
		c3 c3 > nothing
		c3 EOS > nothing
		c3 c5 > nothing
		c5 c3 > nothing
		c4 c4 > nothing
		c3 avatar > killSprite
		avatar c3 > stepBack
	TerminationSet
		NoveltyTermination s1=c2 s2=c2 win=True
		NoveltyTermination s1=avatar s2=c3 win=True
		NoveltyTermination s1=avatar s2=c4 win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=avatar s2=avatar win=True
		NoveltyTermination s1=avatar s2=EOS win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c2 s2=c3 win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=avatar s2=c5 win=True
		NoveltyTermination s1=avatar s2=c2 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c2 s2=c4 win=True
		NoveltyTermination s1=c5 s2=EOS win=True
		SpriteCounter stype=avatar limit=0 win=False
	LevelMapping
		d > c3
		8 > c2
		c > c4
		9 > c5
		b > avatar
"""
level_game_pairs = [[game, level]]
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
