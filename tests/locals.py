from collections import namedtuple
from pygame.locals import K_UP, K_RIGHT, K_LEFT, K_DOWN, K_SPACE
TestCase = namedtuple('TestCase', 'game, level, action_sequences')

def catDescriptions(*description_sets):
	game_description = "BasicGame\n"
	for desc_set in description_sets:
		game_description += '\t'+'\t'.join(desc_set.splitlines(True))
		game_description += '\n'
	return game_description


if __name__ == '__main__':
	sprite_set = """SpriteSet
    box    > Passive color=BROWN # orientation=RIGHT cooldown=1
    box2 > Immovable color=PURPLE"""

	level_mapping = """LevelMapping
	b > box
	2 > box2"""
	interaction_set = """InteractionSet
	avatar box > killSprite"""

	termination_set = """TerminationSet
	SpriteCounter stype=box limit=0 win=True"""

	print catDescriptions(sprite_set, level_mapping, interaction_set, termination_set)