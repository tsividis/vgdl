from collections import namedtuple
from vgdl.theory_template import Theory, Game

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

def getColorInteractionSet(hypothesis):
	'''Reterns interaction set where class names are converted to their respective color names'''
	color_interaction_set = []
	for rule in hypothesis.interactionSet:
		color1 = getColorName(hypothesis, rule.slot1)
		color2 = getColorName(hypothesis, rule.slot2)
		interaction = Interaction(color1, color2, rule.interaction, rule.args.copy())
		color_interaction_set.append(interaction)
	return color_interaction_set

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
	game = Game(vgdlString=game_string)
	theory = Theory(game)
	theory.initializeSpriteSet(game.vgdlSpriteParse)
	for sprite in theory.spriteSet:
		print sprite.colorName, sprite


def TheoriesEqual(theory1, theory2):
	'''Compares if two theories are equal. Class assignments based on color.'''

	return False

if __name__ == '__main__':
	from tests.games import simple
	generateTheoryFromGameString(simple.game)
