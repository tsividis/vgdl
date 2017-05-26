level1 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
a          2                   a
a                              a
a                              a
a                              a
a                 A            a
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

level2 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
a          2                   a
a                        3     a
a                              a
a                              a
a                              a
a                 A            a
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

level3 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
a1                             a
a          2                   a
a                        3     a
a                              a
a                              a
a                              a
a                 A            a
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

level4 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
a1                             a
a          2                   a
a                        3     a
a                              a
a        5                     a
a                              a
a                              a
a                 A            a
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

level5 = """
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
a1                             a
a          2                   a
a                        3     a
a                              a
a        5                     a
a                 4            a
a                              a
a                              a
a                 A            a
wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww
"""

game= """
BasicGame frame_rate=42
    SpriteSet
        fakewall   > Immovable    color=LIGHTGRAY
        avatar  > FlakAvatar stype=sam
        missile > Missile
            sam  > orientation=UP    color=BLUE speed=0.3 singleton=True
            bomb > orientation=DOWN  color=RED  speed=0.5
        alien   > Bomber       stype=bomb   prob=0  cooldown=3 speed=0.75
            alien1   > Bomber       stype=bomb   prob=0  cooldown=3 speed=1
            alien2   > Bomber       stype=bomb   prob=0  cooldown=3 speed=1.5
            alien3   > Bomber       stype=bomb   prob=0  cooldown=3 speed=.5
            alien4   > Bomber       stype=bomb   prob=0  cooldown=3 speed=.75
            alien5   > Bomber       stype=bomb   prob=0  cooldown=3 speed=.25
        portal  > SpawnPoint   stype=alien  cooldown=10   total=3

    LevelMapping
        0 > portal
        1 > alien1
        2 > alien2
        3 > alien3
        4 > alien4
        5 > alien5
        a > fakewall

    InteractionSet
        avatar  EOS  > stepBack
        alien   EOS > reverseDirection
        missile EOS  > killSprite
        missile base > killSprite
        base missile > killSprite
        base   alien > killSprite
        avatar alien > killSprite
        avatar bomb  > killSprite
        alien  sam   > killSprite

    TerminationSet
        SpriteCounter      stype=avatar               limit=0 win=False
        MultiSpriteCounter stype1=portal stype2=alien limit=0 win=True
"""

level_game_pairs = [[game, level1], [game, level2], [game, level3],
                    [game, level4], [game, level5]]

if __name__ == "__main__":
    from vgdl.core import VGDLParser
    # parse, run and play.
    import random
    level_game = random.choice(level_game_pairs)
    VGDLParser.playGame(*level_game)
