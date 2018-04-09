from collections import namedtuple
from pygame.locals import K_UP, K_RIGHT, K_LEFT, K_DOWN, K_SPACE

TestCase = namedtuple('TestCase', 'game, level, action_sequences, expected_theory')
TestCase.__new__.__defaults__ = ("", "", [], None)

set_names = {'SpriteSet', 'LevelMapping', 'InteractionSet', 'TerminationSet'}

def args(**kwargs):
	args = ""
	for key, value in kwargs.iteritems():
		assert isinstance(value, str), "argument values must be strings (this isn't that fancy)"
		args += "%s=%s " % (key, value)
	args.strip()
	return args

def classDef(class_name, vgdl_type, **kwargs):
	return "%s > %s %s"  % (class_name, vgdl_type, args(**kwargs))

def mapping(class_name, char):
	assert len(char) == 1, "Char must be single character"
	return "%s > %s" % (char, class_name)

def ruleDef(class1, class2, rule_name, **kwargs):
	return "%s %s > %s %s" % (class1, class2, rule_name, args(**kwargs))

def catDescriptions(*desc_sets):
	game_description = "BasicGame\n"

	for desc_set in desc_sets:
		game_description += '\t%s\n' % '\t'.join(desc_set.strip().splitlines(True))
	return game_description

def joinDescs(*desc_sets):
	assert desc_sets, "joinDescs takes at least 1 argument"
	# grabs the name of the set
	new_set = desc_sets[0].strip().splitlines(True)[0]
	for desc_set in desc_sets:
		new_set += '%s\n' % ''.join(desc_set.strip().splitlines(True)[1:])
	return new_set
	
def add2Set(desc_set, *descs):
	new_desc_set = desc_set
	for desc in descs:
		new_desc_set += '\n\t%s\n' % desc
	return new_desc_set


if __name__ == '__main__':
	sprite_set = """
SpriteSet
	box    > Passive color=BROWN # orientation=RIGHT cooldown=1
	box2 > Immovable color=PURPLE
"""
	sprite_set2 = """
SpriteSet
	box    > Passive color=BROWN # orientation=RIGHT cooldown=1
    box2 > Immovable color=PURPLE
"""

	level_mapping = """
LevelMapping
	b > box
	2 > box2"""
	interaction_set = """
InteractionSet
	avatar box > killSprite"""

	termination_set = """
TerminationSet
	SpriteCounter stype=box limit=0 win=True"""

	print catDescriptions(sprite_set, level_mapping, interaction_set, termination_set)

	avatar = 'avatar > MovingAvatar'
	print add2Set(sprite_set, avatar)
	print classDef('avatar', 'Immovable', color='GREEN')
	print mapping('avatar', 'A')
	print args(color='GREEN')
	print joinDescs(sprite_set, sprite_set2)