level="""
<<<<<<< HEAD
<<<<<<< HEAD
1  2   2    2   2   2    2   2
888         2   2        2    
888                           
                              
                              
              0               
              9               
    888                       
   888                        
   8                          
                7             
=======
=======
>>>>>>> parent of f7cb177... Debugging second-order novelty bonus transferrence for flicker
4444444444444444444
4   4 b      46  74
49314        45   4
44444      9 444444
4     48 2     4 94
4  b  4444444    44
4  2   58b        4
44444     444     4
4         1       4
44404        5  444
4444444444444444444
<<<<<<< HEAD
>>>>>>> parent of f7cb177... Debugging second-order novelty bonus transferrence for flicker
=======
>>>>>>> parent of f7cb177... Debugging second-order novelty bonus transferrence for flicker
"""
game = """
BasicGame
	SpriteSet
<<<<<<< HEAD
<<<<<<< HEAD
		sam > Missile color=PINK singleton=True orientation=UP
		avatar > FlakAvatar color=DARKBLUE stype=sam
		c3 > ResourcePack color=LIGHTGRAY
		c6 > Missile color=RED speed=0.5 orientation=DOWN cooldown=1
		c5 > Missile color=GOLD speed=0.8 orientation=RIGHT cooldown=3
		c4 > ResourcePack color=WHITE
	InteractionSet
		c5 c3 > nothing
		c3 c5 > nothing
		sam sam > nothing
		sam c3 > nothing
		c3 sam > nothing
		avatar c6 > killSprite
		c5 c4 > nothing
		c4 c5 > nothing
		c3 avatar > killSprite
		c5 sam > killSprite
		c6 sam > nothing
		sam c6 > nothing
		avatar EOS > stepBack
		c3 c4 > nothing
		c4 c3 > nothing
		c5 EOS > turnAround
		c4 sam > killSprite
		sam c4 > killSprite
		c4 c6 > killSprite
		c6 c4 > killSprite
		c6 c5 > nothing
		c5 c6 > nothing
		c4 avatar > killSprite
		sam EOS > killSprite
		c6 c3 > nothing
		c3 c6 > nothing
		c6 EOS > killSprite
		c5 avatar > killSprite
		c3 c3 > nothing
		sam avatar > nothing
		c4 c4 > nothing
		c4 EOS > stepBack
=======
		c9 > Missile color=PINK speed=0.5 orientation=UP cooldown=1
		c8 > RandomNPC color=GREEN speed=1.5 cooldown=8
		avatar > MovingAvatar color=DARKBLUE
		c3 > RandomNPC color=LIGHTBLUE speed=1.5 cooldown=8
		c2 > RandomNPC color=BLUE speed=1.5 cooldown=8
		c11 > Missile color=LIGHTRED speed=0.5 orientation=LEFT cooldown=1
		c10 > RandomNPC color=ORANGE speed=1.5 cooldown=8
		c7 > RandomNPC color=LIGHTORANGE speed=1.5 cooldown=8
		c6 > RandomNPC color=LIGHTGREEN speed=1.5 cooldown=8
		c5 > RandomNPC color=DARKGRAY speed=1.5 cooldown=8
		c4 > Missile color=BROWN speed=0.2 orientation=DOWN cooldown=5
	InteractionSet
		c2 avatar > killSprite
		c6 c7 > nothing
		c7 c6 > nothing
		c11 avatar > killSprite
		c8 c8 > nothing
		c2 c4 > nothing
		c4 c2 > nothing
		c4 c8 > nothing
		c8 c4 > nothing
		c6 c11 > nothing
		c11 c6 > nothing
		c2 c10 > nothing
		c10 c2 > nothing
		c6 avatar > killSprite
		c10 c11 > nothing
		c11 c10 > nothing
		c7 c9 > nothing
		c9 c7 > nothing
		c9 c5 > reverseDirection
		c3 c5 > nothing
		c5 c3 > nothing
		c3 avatar > killSprite
		c8 c9 > nothing
		c9 c8 > nothing
		c2 c5 > nothing
		c5 c2 > nothing
		c3 c9 > nothing
		c9 c3 > nothing
		c4 c9 > nothing
		c9 c4 > nothing
		c3 c10 > nothing
		c10 c3 > nothing
		c7 c10 > nothing
		c10 c7 > nothing
		c7 avatar > killSprite
		c2 c8 > nothing
		c8 c2 > nothing
		c8 c10 > nothing
		c10 c8 > nothing
		c5 c7 > nothing
		c7 c5 > nothing
		c5 c11 > nothing
		c11 c5 > nothing
		avatar EOS > stepBack
=======
		c9 > Missile color=PINK speed=0.5 orientation=UP cooldown=1
		c8 > RandomNPC color=GREEN speed=1.5 cooldown=8
		avatar > MovingAvatar color=DARKBLUE
		c3 > RandomNPC color=LIGHTBLUE speed=1.5 cooldown=8
		c2 > RandomNPC color=BLUE speed=1.5 cooldown=8
		c11 > Missile color=LIGHTRED speed=0.5 orientation=LEFT cooldown=1
		c10 > RandomNPC color=ORANGE speed=1.5 cooldown=8
		c7 > RandomNPC color=LIGHTORANGE speed=1.5 cooldown=8
		c6 > RandomNPC color=LIGHTGREEN speed=1.5 cooldown=8
		c5 > RandomNPC color=DARKGRAY speed=1.5 cooldown=8
		c4 > Missile color=BROWN speed=0.2 orientation=DOWN cooldown=5
	InteractionSet
		c2 avatar > killSprite
		c6 c7 > nothing
		c7 c6 > nothing
		c11 avatar > killSprite
		c8 c8 > nothing
		c2 c4 > nothing
		c4 c2 > nothing
		c4 c8 > nothing
		c8 c4 > nothing
		c6 c11 > nothing
		c11 c6 > nothing
		c2 c10 > nothing
		c10 c2 > nothing
		c6 avatar > killSprite
		c10 c11 > nothing
		c11 c10 > nothing
		c7 c9 > nothing
		c9 c7 > nothing
		c9 c5 > reverseDirection
		c3 c5 > nothing
		c5 c3 > nothing
		c3 avatar > killSprite
		c8 c9 > nothing
		c9 c8 > nothing
		c2 c5 > nothing
		c5 c2 > nothing
		c3 c9 > nothing
		c9 c3 > nothing
		c4 c9 > nothing
		c9 c4 > nothing
		c3 c10 > nothing
		c10 c3 > nothing
		c7 c10 > nothing
		c10 c7 > nothing
		c7 avatar > killSprite
		c2 c8 > nothing
		c8 c2 > nothing
		c8 c10 > nothing
		c10 c8 > nothing
		c5 c7 > nothing
		c7 c5 > nothing
		c5 c11 > nothing
		c11 c5 > nothing
		avatar EOS > stepBack
>>>>>>> parent of f7cb177... Debugging second-order novelty bonus transferrence for flicker
		c3 c4 > nothing
		c4 c3 > nothing
		c5 c8 > nothing
		c8 c5 > nothing
		c4 c10 > nothing
		c10 c4 > nothing
		c8 avatar > killSprite
		c6 c8 > nothing
		c8 c6 > nothing
		c9 c11 > nothing
		c11 c9 > nothing
		c2 c6 > nothing
		c6 c2 > nothing
		c3 c8 > nothing
		c8 c3 > nothing
		c4 c6 > nothing
		c6 c4 > nothing
		c3 c7 > nothing
		c7 c3 > nothing
		c2 c9 > nothing
		c9 c2 > nothing
		c9 c10 > nothing
		c10 c9 > nothing
		c9 c9 > nothing
		c2 c2 > nothing
		c5 c6 > nothing
		c6 c5 > nothing
		c4 c11 > nothing
		c11 c4 > nothing
		c3 c3 > nothing
		c10 c10 > nothing
		c5 c10 > nothing
		c10 c5 > nothing
		c11 c11 > nothing
		c6 c9 > nothing
		c9 c6 > nothing
		c8 c11 > nothing
		c11 c8 > nothing
		c2 c7 > nothing
		c7 c2 > nothing
		c7 c8 > nothing
		c8 c7 > nothing
		c4 c7 > nothing
		c7 c4 > nothing
		c3 c11 > nothing
		c11 c3 > nothing
		c3 c6 > nothing
		c6 c3 > nothing
		c6 c6 > nothing
		avatar c10 > nothing
		c2 c3 > nothing
		c3 c2 > nothing
		c7 c7 > nothing
		c7 c11 > nothing
		c11 c7 > nothing
		avatar c5 > stepBack
		c4 avatar > killSprite
		c5 c5 > nothing
		c9 avatar > killSprite
		c4 c4 > nothing
		c2 c11 > nothing
		c11 c2 > nothing
		c6 c10 > nothing
		c10 c6 > nothing
		c8 EOS > stepBack
		c4 c5 > stepBack
		c5 EOS > stepBack
		c7 EOS > stepBack
		c10 EOS > stepBack
<<<<<<< HEAD
>>>>>>> parent of f7cb177... Debugging second-order novelty bonus transferrence for flicker
=======
>>>>>>> parent of f7cb177... Debugging second-order novelty bonus transferrence for flicker
		c3 EOS > stepBack
		c11 EOS > stepBack
		c6 EOS > stepBack
		c9 EOS > stepBack
		c2 EOS > stepBack
		c4 EOS > stepBack
	TerminationSet
<<<<<<< HEAD
<<<<<<< HEAD
		NoveltyTermination s1=sam s2=sam win=True
		NoveltyTermination s1=sam s2=c3 win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c3 s2=c3 win=True
		NoveltyTermination s1=c3 s2=c4 win=True
		NoveltyTermination s1=c4 s2=avatar win=True
		NoveltyTermination s1=c4 s2=c4 win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=c5 s2=avatar win=True
		NoveltyTermination s1=c5 s2=c3 win=True
		NoveltyTermination s1=c5 s2=c4 win=True
		NoveltyTermination s1=c6 s2=sam win=True
		NoveltyTermination s1=c6 s2=c3 win=True
		NoveltyTermination s1=c6 s2=c5 win=True
=======
		NoveltyTermination s1=c2 s2=avatar win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c4 s2=avatar win=True
		NoveltyTermination s1=c4 s2=c4 win=True
=======
		NoveltyTermination s1=c2 s2=avatar win=True
		NoveltyTermination s1=c3 s2=avatar win=True
		NoveltyTermination s1=c4 s2=avatar win=True
		NoveltyTermination s1=c4 s2=c4 win=True
>>>>>>> parent of f7cb177... Debugging second-order novelty bonus transferrence for flicker
		NoveltyTermination s1=c4 s2=c9 win=True
		NoveltyTermination s1=c4 s2=c11 win=True
		NoveltyTermination s1=c6 s2=avatar win=True
		NoveltyTermination s1=c7 s2=avatar win=True
		NoveltyTermination s1=c8 s2=avatar win=True
		NoveltyTermination s1=c9 s2=avatar win=True
		NoveltyTermination s1=c9 s2=c9 win=True
		NoveltyTermination s1=c9 s2=c11 win=True
		NoveltyTermination s1=c11 s2=avatar win=True
		NoveltyTermination s1=c11 s2=c11 win=True
		NoveltyTermination s1=c2 s2=EOS win=True
		NoveltyTermination s1=c3 s2=EOS win=True
		NoveltyTermination s1=c4 s2=EOS win=True
		NoveltyTermination s1=c5 s2=EOS win=True
		NoveltyTermination s1=c6 s2=EOS win=True
		NoveltyTermination s1=c7 s2=EOS win=True
		NoveltyTermination s1=c8 s2=EOS win=True
		NoveltyTermination s1=c9 s2=EOS win=True
		NoveltyTermination s1=c10 s2=EOS win=True
		NoveltyTermination s1=c11 s2=EOS win=True
		NoveltyTermination s1=avatar s2=EOS win=True
>>>>>>> parent of f7cb177... Debugging second-order novelty bonus transferrence for flicker
		SpriteCounter stype=avatar limit=0 win=False
		SpriteCounter stype=c4 limit=0 win=True
	LevelMapping
<<<<<<< HEAD
<<<<<<< HEAD
		0 > sam
		1 > c3
		2 > c5
		c > avatar sam
		b > c5 c3
		7 > avatar
		e > c5 c6 c3
		8 > c4
		d > c5 c6
		9 > c6
=======
=======
>>>>>>> parent of f7cb177... Debugging second-order novelty bonus transferrence for flicker
		0 > c2
		1 > c3
		c > avatar c10
		2 > c4
		3 > avatar
		4 > c5
		5 > c6
		6 > c7
		7 > c8
		8 > c9
		9 > c10
		b > c11
<<<<<<< HEAD
>>>>>>> parent of f7cb177... Debugging second-order novelty bonus transferrence for flicker
=======
>>>>>>> parent of f7cb177... Debugging second-order novelty bonus transferrence for flicker
"""
if __name__ == "__main__":
	from vgdl.core import VGDLParser
	VGDLParser.playGame(game, level)
