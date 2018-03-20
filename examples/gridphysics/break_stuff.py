

level = """
wwwwwwww
wV  M  w
wA    Nw
wwwwwwww
"""

game="""
BasicGame
	SpriteSet
		not_avatar > Immovable color=GREEN stype=blue
		avatar  > MovingAvatar color=DARKBLUE
		vatar > HorizontalAvatar
		missile > Missile stype=vatar 


	LevelMapping
		N > not_avatar
		M > missile
		V > vatar

	InteractionSet
		avatar vatar > killSprite

	TerminationSet
		Termination
"""
level_game_pairs = [[game, level]]


if __name__ == "__main__":
    from vgdl.core import VGDLParser
    # parse, run and play.
    VGDLParser.playGame(game, level)
