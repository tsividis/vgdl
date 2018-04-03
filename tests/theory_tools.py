from collections import namedtuple
from vgdl.theory_template import Theory, Game, InteractionRule, TerminationRuleConstructor
from vgdl.class_theory_template import SpriteParser
from vgdl.core import VGDLParser

Interaction = namedtuple('Interaction', 'slot1, slot2,  interaction, args')
ClassAssignment = namedtuple('ClassAssignment', 'vgdlType, args')

def getColorAssignments(hypothesis):
	'''Returns class assignments where class names are converted to their respective color names'''
	color_assignments = {}
	for class_name, vgdl_classes in hypothesis.classes.iteritems():
		color_name = vgdl_classes[0].colorName
		sprite_object = hypothesis.spriteObjects[color_name]
		color_assignments[color_name] = ClassAssignment(sprite_object.vgdlType, sprite_object.args)
	return color_assignments

def getColorName(hypothesis, class_name):
	'''Returns the the color of a given class in a given hypothesis'''
	assert class_name in hypothesis.classes, 'Key Error: class name not in hypothesis'
	return hypothesis.classes[class_name][0].colorName

def getColorInteraction(rule, hypothesis):
	color1 = getColorName(hypothesis, rule.slot1)
	color2 = getColorName(hypothesis, rule.slot2)
	return InteractionRule(rule.interaction, color1, color2, rule.args.copy())

def getColorInteractionSet(hypothesis):
	'''Reterns interaction set where class names are converted to their respective color names'''
	color_interaction_set = []
	for rule in hypothesis.interactionSet:
		color_interaction_set.append(getColorInteraction(rule, hypothesis))
	return color_interaction_set

def getColorTermination(term, hypothesis):
	args = term.termination.get_args()
	name = term.ruleType
	for key, value in args.iteritems():
		if value in hypothesis.classes:
			args[key] = getColorName(hypothesis, value)
	return TerminationRuleConstructor(name, **args)

def getColorTerminationSet(hypothesis):
	'''Returns termination set where class names are converted to their respective color names'''
	color_termination_set = set()
	for term in hypothesis.terminationSet:
		color_termination_set.add(getColorTermination(term, hypothesis))
	return color_termination_set

def argsEqual(args1, args2):
	if set(args1) == set(args2):
		for key in args1:
			if args1[key] != args2[key]:
				return False
		return True
	return False


def interactionsEqual(interaction1, interaction2):
	for i1, i2 in zip(interaction1[:-1], interaction2[:-1]):
		if i1 != i2:
			return False
	return argsEqual(interaction1.args, interaction2.args)

def hypothesisContainsInteraction(hypothesis, interaction):
	'''assert hypothesis contains a specific interaction 
	relating color1 and color2 with specific arguments'''

	rule = hypothesis.interactionSet[0]
	for i in getColorInteractionSet(hypothesis):
		if interactionsEqual(i, interaction):
			return True
	return False

def hypothesisAssignsVGDLType2Color(hypothesis, color_name, vgdl_type):
	return getColorAssignments(hypothesis)[color_name].vgdlType == vgdl_type

def generateTheoryFromGameString(game_string):
	vgdl_parser = VGDLParser()
	sprite_parser = SpriteParser()
	game = Game(game_string)
	theory = Theory(game)

	sprite_types = sprite_parser.parseGame(game_string)
	vgdl_game = vgdl_parser.parseGame(game_string)
	# Add classes
	for class_name, sprite in sprite_parser.sprite_types.iteritems():
		# print class_name, sprite
		theory.classes[class_name] = [sprite]
		theory.spriteSet.append(sprite)
		if class_name == 'EOS':
			sprite.colorName = 'ENDOFSCREEN'
		theory.spriteObjects[sprite.colorName] = sprite

	# Add interaction Rules
	for c1, c2, effect, args in vgdl_game.collision_eff:
		rule = InteractionRule(effect.__name__, c1, c2, args)
		theory.interactionSet.append(rule)

	# Add termination Rules
	for termination in vgdl_game.terminations:
		rule_type = termination.name+'Rule'
		try:
			term_rule = TerminationRuleConstructor(rule_type, **termination.get_args())
			theory.terminationSet.add(term_rule)
		except NameError:
			# pass
			print 'WARNING: EXCEPTION RAISED'
			print 'NameError: could not create termination rule %s' % rule_type

	return theory


def TheoriesEqual(theory1, theory2, ignore_novelty_terminations=True):
	'''Compares if two theories are equal where class assignments are based on color.'''
	colors1, colors2 = set(theory1.spriteObjects), set(theory2.spriteObjects)
	# Check if same colors used for class definition
	if colors1 != colors2:
		return False

	# Check if class definitions are the same
	for color in colors1:
		# print
		if theory1.spriteObjects[color] != theory2.spriteObjects[color]:
			return False

	# Check if interactions are equal (in terms of color, not class name)
	interactions1 = set(getColorInteractionSet(theory1))
	interactions2 = set(getColorInteractionSet(theory2))
	if interactions1 != interactions2:
		return False

	# Check if terminations are equal (in terms of color, not class name)
	terminations1 = getColorTerminationSet(theory1)
	terminations2 = getColorTerminationSet(theory2)
	if terminations1 != terminations2:
		return False

	return True

if __name__ == '__main__':
	from tests.games import simple
	t1 = generateTheoryFromGameString(simple.game)
	t2 = generateTheoryFromGameString(simple.game2)
	assert TheoriesEqual(t1, t2), 'Theories not equal'
	print 'theories equal'
