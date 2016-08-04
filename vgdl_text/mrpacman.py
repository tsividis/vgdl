"""
BasicGame
    SpriteSet
        food > Immovable
            pellet > color=WHITE shrinkfactor=0.8
            power  > color=LIGHTGREEN shrinkfactor=0.5
        nest > SpawnPoint
            redspawn > stype=red
            orangespawn > stype=orange
            bluespawn > stype=blue
            pinkspawn > stype=pink
        moving >
            ghost > AStarChaser stype=hungry cooldown=3
                red    > color=LIGHTRED    singleton=True
                blue   > color=LIGHTBLUE   singleton=True
            ghost > Chaser stype=hungry cooldown=3
                pink   > color=PINK        singleton=True
                orange > color=LIGHTORANGE singleton=True
            pacman > OrientedAvatar 
                hungry  > color=YELLOW
                powered > color=ORANGE            
            
    InteractionSet
        hungry  power > transformTo stype=powered 
        powered ghost > transformTo stype=hungry
        power hungry  > killSprite
        ghost powered > killSprite
        hungry ghost  > killSprite
        food pacman > killSprite
        moving wall > stepBack        
        moving EOS  > wrapAround        
        
    LevelMapping
        0 > power
        . > pellet
        A > hungry
        1 > redspawn red
        2 > bluespawn blue
        3 > pinkspawn pink
        4 > orangespawn orange
        
    TerminationSet
        SpriteCounter stype=food   win=True     
        SpriteCounter stype=pacman win=False     
    
"""