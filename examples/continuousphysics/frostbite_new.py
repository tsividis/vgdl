game = """
BasicGame
    SpriteSet    
    	avatar > MarioAvatar strength=25 vx_max=6 physicstype=GravityPhysics color=WHITE
    	rplatform > Missile orientation=RIGHT color=BLACK speed=0.1 width=2.0
    	# rplatform > Immovable color=BLACK
    	lplatform > Missile orientation=LEFT color=GRAY speed=0.1 width=2.0
    	rbplatform > Missile orientation=RIGHT color=BLACK speed=0.1
    	lbplatform > Missile orientation=LEFT color=GRAY speed=0.1
    	gold > Resource limit=9 color=GOLD height=1.1
    	igloo > Immovable color=GREEN
    	water > Immovable color=BLUE

    TerminationSet
        SpriteCounter stype=avatar win=False
        SpriteCounter stype=igloo   win=True 


    InteractionSet
        rplatform EOS > wrapAround
        lplatform EOS > wrapAround
        gold EOS > wrapAround
        # avatar EOS > killSprite
        avatar water > killSprite
        igloo avatar > killIfOtherHasMore resource=gold limit=9
        avatar gold > changeResource resource=gold value=1
        gold avatar > killSprite
        gold rplatform > pullWithIt
        gold lplatform > pullWithIt
        avatar rplatform > platformInteraction
        avatar lplatform > platformInteraction
        avatar rplatform > killIfTooFast speed=40
        avatar lplatform > killIfTooFast speed=40

    LevelMapping
		r > rplatform
		l > lplatform
		b > rbplatform
		k > lbplatform
		g > gold
		I > igloo
		w > water
"""

level = """
               I            
                            
                            
     A                      
     g         g         g  
     r         r         r  
                            
                            
      g     g         g     
  l         l         l     
                            
                            
 g         g        g       
r         r         r       
                            
                            
wwwwwwwwwwwwwwwwwwwwwwwwwwww
"""
level_game_pairs = [[game, level]]
if __name__ == "__main__":
    from vgdl.core import VGDLParser
    VGDLParser.playGame(game, level)