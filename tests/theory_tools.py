from collections import namedtuple
from itertools import combinations

from IPython import embed
from vgdl.theory_template import Theory, Game, InteractionRule, TerminationRuleConstructor
from vgdl.class_theory_template import SpriteParser
from vgdl.core import VGDLParser, EOS

Interaction = namedtuple('Interaction', 'slot1, slot2,  interaction, args')
ClassAssignment = namedtuple('ClassAssignment', 'vgdlType, args')

def getColorAssignments(hypothesis):
	'''Returns class assignments where class names are converted to their respective color names'''
	color_assignments = {}
	for class_name, vgdl_classes in hypothesis.classes.iteritems():
		color_name = vgdl_classes[0].colorName
		sprite_object = hypothesis.spriteObjects[color_name]
		args = getColorArgs(hypothesis, sprite_object.args if sprite_object.args else {})
		color_assignments[color_name] = ClassAssignment(sprite_object.vgdlType, args)
	return color_assignments

def getColorName(hypothesis, class_name):
	'''Returns the the color of a given class in a given hypothesis'''
	assert class_name in hypothesis.classes, 'Key Error: class name %s not in classes: %r' % (class_name, hypothesis.classes.keys())
	return hypothesis.classes[class_name][0].colorName

def getColorArgs(hypothesis, args):
	new_args = args.copy()
	for key, value in args.iteritems():
		try:
			if value in hypothesis.classes:
				new_args[key] = getColorName(hypothesis, value)
		except TypeError:
			if hasattr(value, '__iter__'):
				new_value = []
				for v in value:
					if v in hypothesis.classes:
						new_value.append(getColorName(hypothesis, v))
				new_args[key] = new_value
			else:
				new_args[key] = value
	return new_args


def getColorInteraction(rule, hypothesis):
	color1 = getColorName(hypothesis, rule.slot1)
	color2 = getColorName(hypothesis, rule.slot2)
	args = getColorArgs(hypothesis, rule.args)
	return InteractionRule(rule.interaction, color1, color2, args)

def getColorInteractionSet(hypothesis, ignore_nothing=True):
	'''Reterns interaction set where class names are converted to their respective color names'''
	color_interaction_set = set()
	for rule in hypothesis.interactionSet:
		if rule.interaction == 'nothing' or rule.slot1 == 'EOS':
			continue
		color_interaction_set.add(getColorInteraction(rule, hypothesis))
	return color_interaction_set

def getColorTermination(term, hypothesis):
	name = term.ruleType
	args = getColorArgs(hypothesis, term.termination.get_args())
	return TerminationRuleConstructor(name, **args)

def getColorTerminationSet(hypothesis, ignore_novelty_terminations=True):
	'''Returns termination set where class names are converted to their respective color names'''
	color_termination_set = set()
	for term in hypothesis.terminationSet:
		if term.ruleType == 'NoveltyRule':
			continue
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

	sprite_types = sprite_parser.parseGame(game_string, remove_singleton=False)
	vgdl_game = vgdl_parser.parseGame(game_string)
	# Add classes
	class_names = []
	for class_name, sprite in sprite_parser.sprite_types.iteritems():
		# print class_name, sprite

		theory.classes[class_name] = [sprite]
		theory.spriteSet.append(sprite)
		if class_name == 'EOS':
			sprite.vgdlType = EOS
			sprite.colorName = 'ENDOFSCREEN'
		else:
			class_names.append(class_name)
			rule1 = InteractionRule('stepBack', class_name, class_name, {})
			rule2 = InteractionRule('stepBack', class_name, 'EOS', {})
			theory.interactionSet.append(rule1)
			theory.interactionSet.append(rule2)

		theory.spriteObjects[sprite.colorName] = sprite


	# Add interaction Rules
	interacting_sprites = set()
	for c1, c2, effect, args in vgdl_game.collision_eff:
		interacting_sprites.add(frozenset([c1, c2]))
		rule = InteractionRule(effect.__name__, c1, c2, args)
		theory.interactionSet.append(rule)

	for c1, c2 in combinations(class_names, 2):
		combination = set([c1, c2])
		if set([c1, c2]) not in interacting_sprites:
			rule1 = InteractionRule('stepBack', c1, c2, {})
			rule2 = InteractionRule('stepBack', c2, c1, {})
			theory.interactionSet.append(rule1)
			theory.interactionSet.append(rule2)

	# Add termination Rules
	for termination in vgdl_game.terminations:
		rule_type = termination.name+'Rule'
		try:
			term_rule = TerminationRuleConstructor(rule_type, **termination.get_args())
			for key, value in term_rule.__dict__.iteritems():
				if value == EOS:
					setattr(term_rule, key, value)
			theory.terminationSet.add(term_rule)
		except NameError:
			# pass
			print 'WARNING: EXCEPTION RAISED'
			print 'NameError: could not create termination rule %s' % rule_type

	return theory

def classAssignmentsDiff(theory1, theory2):

	color_type_tuples = (set(), set())

	for color_type_tuple, theory in zip(color_type_tuples, (theory1, theory2)):
		for color, assignment in theory.spriteObjects.iteritems():
			color_type_tuple.add((color, assignment.vgdlType))

	c1, c2 = color_type_tuples

	return c1-c2, c2-c1

def classAssignmentsEqual(theory1, theory2):
	'''Check if class assignments are the same (based on color)'''
	colors1, colors2 = set(theory1.spriteObjects), set(theory2.spriteObjects)

	# Check if same colors used for class definitions
	if colors1 != colors2:
		return False

	# Check if class definitions are the same
	for color in colors1:
		# print
		vgdl_type1 = theory1.spriteObjects[color].vgdlType
		vgdl_type2 = theory2.spriteObjects[color].vgdlType
		if vgdl_type1 != vgdl_type2:
			return False

	return True

def interactionSetsEqual(theory1, theory2):
	'''Check if interactions are equal (in terms of color, not class name)'''
	interactions1 = getColorInteractionSet(theory1)
	interactions2 = getColorInteractionSet(theory2)

	if len(interactions1) != len(interactions2):
		return False
	if interactions1 != interactions2:
		return False

	return True

def interactionSetsDiff(theory1, theory2):
	i1 = getColorInteractionSet(theory1)
	i2 = getColorInteractionSet(theory2)

	return i1-i2, i2-i1

def terminationSetsEqual(theory1, theory2, ignore_novelty_terminations=True):
	'''Check if terminations are equal (in terms of color, not class name)'''
	terminations1 = getColorTerminationSet(theory1, ignore_novelty_terminations)
	terminations2 = getColorTerminationSet(theory2, ignore_novelty_terminations)

	if len(terminations1) != len(terminations2):
		return False
	if terminations1 != terminations2:
		return False

	return True

def terminationSetsDiff(theory1, theory2, ignore_novelty_terminations=True):
	t1 = getColorTerminationSet(theory1, ignore_novelty_terminations)
	t2 = getColorTerminationSet(theory2, ignore_novelty_terminations)

	return t1-t2, t2-t1

def theoriesEqual(theory1, theory2, ignore_novelty_terminations=True):
	'''Compares if two theories are equal where class assignments are based on color.'''
	if not classAssignmentsEqual(theory1, theory2):
		return False

	if not interactionSetsEqual(theory1, theory2):
		return False

	if not terminationSetsEqual(theory1, theory2, ignore_novelty_terminations):
		return False

	return True

def theoryInHypotheses(theory, hypotheses):
	for h in hypotheses:
		if theoriesEqual(h, theory):
			return True
	return False

if __name__ == '__main__':
	from tests.games import simple, inference
	t1 = generateTheoryFromGameString(simple.game)
	t2 = generateTheoryFromGameString(simple.game2)
	# assert TheoriesEqual(t1, t2), 'Theories not equal'
	print 'TheoriesEqual(t12, t2) = %s' % theoriesEqual(t1, t2)

	t4_expected = generateTheoryFromGameString(inference.test4.expected_theory)
	t4_real = generateTheoryFromGameString(inference.test4.game)
	d1, d2 = interactionSetsDiff(t4_real, t4_expected)
	# print getColorInteractionSet(t4_real)
	# print d2

	print generateTheoryFromGameString(inference.test2.expected_theory)

	# print 
	# print classAssignmentsDiff(t4_real, t4_expected)


	# print getColorAssignments(generateTheoryFromGameString(inference.test2))