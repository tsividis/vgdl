level="""
55555555555555555555555555
5   324423      3  43442 5
5   333333      2 322322 5
5   244422       323433235
54  22222        343222335
5555555555       232  5445
5  2 8 32        22   5445
50 2  22     22223    5445
533322222   3    2    5225
52222 242   55554 42335  5
5    222     3443 22225  5
5    1d     32222        5
55555555555555555555555555
"""
game = """
BasicGame
	SpriteSet
		dirt > ResourcePack color=BROWN
		exitdoor > ResourcePack color=GREEN
		diamond > ResourcePack color=YELLOW
		boulder > Missile color=DARKGRAY speed=0.2 orientation=DOWN
		avatar > ShootAvatar color=WHITE stype=sword
		crab > RandomNPC color=RED cooldown=8
		butterfly > RandomNPC color=PINK cooldown=7
		wall > ResourcePack color=BLACK
		sword > Flicker color=BLUE singleton=True
	InteractionSet
		dirt avatar > killSprite
		avatar boulder > stepBack

		boulder dirt > stepBack


		crab wall > stepBack
		diamond wall > killSprite
		wall diamond > killSprite
		exitdoor exitdoor > killSprite
		diamond exitdoor > killSprite
		exitdoor diamond > killSprite
		dirt exitdoor > killSprite
		exitdoor dirt > killSprite
		diamond avatar > changeScore value=5
		avatar diamond > changeResource limit=5 resource=diamond value=1
		diamond avatar > killSprite
		sword EOS > stepBack
		crab dirt > stepBack
		butterfly dirt > stepBack
		exitdoor EOS > stepBack
		crab boulder > stepBack
		butterfly boulder > stepBack
		wall exitdoor > killSprite
		exitdoor wall > killSprite
		exitdoor crab > killSprite
		crab exitdoor > killSprite
		sword crab > killSprite
		crab sword > killSprite
		diamond crab > killSprite
		crab diamond > killSprite
		butterfly crab > killSprite
		crab butterfly > killSprite
		dirt EOS > stepBack
		sword avatar > nothing
		avatar wall > stepBack
		wall sword > nothing
		boulder sword > nothing
		sword boulder > nothing
		boulder wall > stepBack
		butterfly avatar > killSprite
		butterfly avatar > killIfOtherHasMore resource=diamond limit=0
		butterfly avatar > killIfOtherHasMore resource=diamond limit=5
		boulder EOS > stepBack
		boulder exitdoor > killSprite
		exitdoor boulder > killSprite
		sword butterfly > killSprite
		butterfly sword > killSprite
		butterfly exitdoor > killSprite
		exitdoor butterfly > killSprite
		dirt diamond > killSprite
		diamond dirt > killSprite
		butterfly wall > stepBack
		boulder boulder > stepBack
		boulder diamond > stepBack
		wall EOS > stepBack
		diamond sword > nothing
		dirt sword > killSprite
		butterfly butterfly > killSprite
		butterfly EOS > stepBack
		exitdoor avatar > killIfOtherHasMore resource=diamond limit=5
		exitdoor avatar > nothing
		dirt wall > killSprite
		wall dirt > killSprite
		butterfly diamond > killSprite
		diamond butterfly > killSprite
		diamond diamond > killSprite
		sword sword > killSprite
		wall wall > killSprite
		diamond EOS > stepBack
		crab EOS > stepBack
		exitdoor sword > nothing
		crab crab > killSprite
		avatar crab > killSprite
		crab avatar > killIfOtherHasMore resource=diamond limit=5
		dirt dirt > killSprite
	TerminationSet
		NoveltyTermination s1=sword s2=sword win=True
		NoveltyTermination s1=sword s2=butterfly win=True
		NoveltyTermination s1=sword s2=crab win=True
		NoveltyTermination s1=butterfly s2=avatar win=True
		NoveltyTermination s1=butterfly s2=butterfly win=True
		NoveltyTermination s1=butterfly s2=diamond win=True
		NoveltyTermination s1=butterfly s2=exitdoor win=True
		NoveltyTermination s1=butterfly s2=crab win=True
		NoveltyTermination s1=dirt s2=dirt win=True
		NoveltyTermination s1=dirt s2=diamond win=True
		NoveltyTermination s1=dirt s2=wall win=True
		NoveltyTermination s1=dirt s2=exitdoor win=True
		NoveltyTermination s1=boulder s2=exitdoor win=True
		NoveltyTermination s1=diamond s2=diamond win=True
		NoveltyTermination s1=diamond s2=wall win=True
		NoveltyTermination s1=diamond s2=exitdoor win=True
		NoveltyTermination s1=diamond s2=crab win=True
		NoveltyTermination s1=wall s2=wall win=True
		NoveltyTermination s1=wall s2=exitdoor win=True
		NoveltyTermination s1=exitdoor s2=exitdoor win=True
		NoveltyTermination s1=exitdoor s2=crab win=True
		NoveltyTermination s1=crab s2=crab win=True
		NoveltyTermination s1=exitdoor s2=avatar win=True
		NoveltyTermination s1=crab s2=avatar win=True
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=dirt limit=0 win=True
		SpriteCounter stype=diamond limit=0 win=True
	LevelMapping
		2 > dirt
		6 > exitdoor
		3 > boulder
		4 > diamond
		8 > crab
		0 > butterfly
		5 > wall
		1 > sword
		9 > boulder sword
		d > avatar exitdoor
		b > sword wall
		e > exitdoor sword
		f > diamond sword
		c > avatar sword
		7 > avatar
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
