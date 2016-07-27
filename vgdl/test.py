import theory_template_072516 as tt
from sampleVGDLString import *
from class_theory_template_071916 import *
from IPython import embed


#TODO: If this is still an issue... Figure out issue where hypotheses only are found when you run this more than once; always breaks once the precondition event happens

def testTrace(rawTrace, expectedHypotheses, name, verbose):
	g = tt.Game(push_game)
	trace = ([tt.TimeStep(tr['agentAction'], tr['agentState'], tr['effectList'], tr['gameState']) for tr in rawTrace[0]],rawTrace[1])
	hypotheses=list(g.induction(trace, verbose))
	
	print "########################"
	print "Checking {}...".format(name)
	print "Expected number of hypotheses {} = actual number of hypotheses {}? {}".format(expectedHypotheses, len(hypotheses), expectedHypotheses==len(hypotheses))
	# TODO: Are there other parameters which we want to check?
	print "\n########################\n\n\n\n\n\n\n"
	return hypotheses



if __name__ == '__main__':

	"""
	Testing win termination conditions in simple game setting
	"""
	rawTrace_simple_win = [
		[
			{
			'gameState': 
				{
				'ended': False, 
				'score': 0, 
				'objects': {'BLUE': {(305, 427): {'speed': None}, (122, 305): {'speed': None}}, 'BROWN': {(488, 427): {'speed': None, 'limit': 3}, (488, 183): {'speed': None, 'limit': 3}}, 'GOLD': {(671, 183): {'speed': None}}, 'LIGHTBLUE': {(427, 244): {'speed': None}}, 'DARKBLUE': {(305, 305): {'speed': 1, 'resources': {'medicine': 1}}}, 'GREEN': {(671, 366): {'speed': None, 'limit': 5}}, 'PINK': {(183, 427): {'speed': None}, (183, 61): {'speed': None}}, 'ORANGE': {(244, 122): {'speed': None}, (122, 366): {'speed': None}, (366, 183): {'speed': None}}, 'BLACK': {(305, 488): {'speed': None}, (732, 305): {'speed': None}, (0, 122): {'speed': None}, (732, 427): {'speed': None}, (305, 0): {'speed': None}, (610, 244): {'speed': None}, (427, 488): {'speed': None}, (244, 0): {'speed': None}, (0, 305): {'speed': None}, (488, 305): {'speed': None}, (0, 427): {'speed': None}, (183, 0): {'speed': None}, (244, 488): {'speed': None}, (671, 244): {'speed': None}, (0, 61): {'speed': None}, (549, 488): {'speed': None}, (671, 427): {'speed': None}, (61, 488): {'speed': None}, (0, 244): {'speed': None}, (732, 61): {'speed': None}, (122, 0): {'speed': None}, (61, 0): {'speed': None}, (488, 244): {'speed': None}, (732, 244): {'speed': None}, (732, 366): {'speed': None}, (732, 0): {'speed': None}, (671, 0): {'speed': None}, (366, 488): {'speed': None}, (0, 183): {'speed': None}, (0, 0): {'speed': None}, (671, 488): {'speed': None}, (610, 488): {'speed': None}, (732, 183): {'speed': None}, (183, 488): {'speed': None}, (610, 0): {'speed': None}, (549, 0): {'speed': None}, (122, 244): {'speed': None}, (61, 244): {'speed': None}, (488, 0): {'speed': None}, (732, 488): {'speed': None}, (427, 0): {'speed': None}, (122, 488): {'speed': None}, (549, 244): {'speed': None}, (488, 488): {'speed': None}, (366, 0): {'speed': None}, (0, 366): {'speed': None}, (732, 122): {'speed': None}, (0, 488): {'speed': None}, (549, 61): {'speed': None}}, 'WHITE': {(305, 61): {'speed': None, 'limit': 3}}, 'RED': {(122, 183): {'speed': None, 'limit': 5}, (305, 366): {'speed': None, 'limit': 5}}}, 
				'win': None
				}, 
			'agentAction': None, 
			'agentState': {'medicine': 1}, 
			'effectList': [('changeResource', 'DARKBLUE', 'WHITE', 1), ('killSprite', 'DARKBLUE', 'WHITE')]
			},
			
			{
			'gameState': 
				{
				'ended': False, 
				'score': 0, 
				'objects': {'BLUE': {(305, 427): {'speed': None}, (122, 305): {'speed': None}}, 'BROWN': {(488, 427): {'speed': None, 'limit': 3}, (488, 183): {'speed': None, 'limit': 3}}, 'GOLD': {(671, 183): {'speed': None}}, 'LIGHTBLUE': {(427, 244): {'speed': None}}, 'DARKBLUE': {(366, 183): {'speed': 1, 'resources': {'medicine': 1}}}, 'GREEN': {(671, 366): {'speed': None, 'limit': 5}}, 'PINK': {(183, 427): {'speed': None}, (183, 61): {'speed': None}}, 'ORANGE': {(244, 122): {'speed': None}, (122, 366): {'speed': None}, (427, 183): {'speed': None}}, 'BLACK': {(305, 488): {'speed': None}, (732, 305): {'speed': None}, (0, 122): {'speed': None}, (732, 427): {'speed': None}, (305, 0): {'speed': None}, (610, 244): {'speed': None}, (427, 488): {'speed': None}, (244, 0): {'speed': None}, (0, 305): {'speed': None}, (488, 305): {'speed': None}, (0, 427): {'speed': None}, (183, 0): {'speed': None}, (244, 488): {'speed': None}, (671, 244): {'speed': None}, (0, 61): {'speed': None}, (549, 488): {'speed': None}, (671, 427): {'speed': None}, (61, 488): {'speed': None}, (0, 244): {'speed': None}, (732, 61): {'speed': None}, (122, 0): {'speed': None}, (61, 0): {'speed': None}, (488, 244): {'speed': None}, (732, 244): {'speed': None}, (732, 366): {'speed': None}, (732, 0): {'speed': None}, (671, 0): {'speed': None}, (366, 488): {'speed': None}, (0, 183): {'speed': None}, (0, 0): {'speed': None}, (671, 488): {'speed': None}, (610, 488): {'speed': None}, (732, 183): {'speed': None}, (183, 488): {'speed': None}, (610, 0): {'speed': None}, (549, 0): {'speed': None}, (122, 244): {'speed': None}, (61, 244): {'speed': None}, (488, 0): {'speed': None}, (732, 488): {'speed': None}, (427, 0): {'speed': None}, (122, 488): {'speed': None}, (549, 244): {'speed': None}, (488, 488): {'speed': None}, (366, 0): {'speed': None}, (0, 366): {'speed': None}, (732, 122): {'speed': None}, (0, 488): {'speed': None}, (549, 61): {'speed': None}}, 'WHITE': {(305, 61): {'speed': None, 'limit': 3}}, 'RED': {(122, 183): {'speed': None, 'limit': 5}, (305, 366): {'speed': None, 'limit': 5}}}, 
				'win': None
				}, 
			'agentAction': None, 
			'agentState': {'medicine': 1}, 
			'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE')]
			},
		   
			{'gameState': 
				{
				'ended': False, 
				'score': 0, 
				'objects': {'BLUE': {(305, 427): {'speed': None}, (122, 305): {'speed': None}},'BROWN': {(488, 427): {'speed': None, 'limit': 3}}, 'GOLD': {(671, 183): {'speed': None}}, 'LIGHTBLUE': {(427, 244): {'speed': None}}, 'DARKBLUE': {(488, 183): {'speed': 1, 'resources': {'medicine': 0}}}, 'GREEN': {(671, 366): {'speed': None, 'limit': 5}}, 'PINK': {(183, 427): {'speed': None}, (183, 61): {'speed': None}}, 'ORANGE': {(244, 122): {'speed': None}, (122, 366): {'speed': None}, (427, 183): {'speed': None}}, 'BLACK': {(305, 488): {'speed': None}, (732, 305): {'speed': None}, (0, 122): {'speed': None}, (732, 427): {'speed': None}, (305, 0): {'speed': None}, (610, 244): {'speed': None}, (427, 488): {'speed': None}, (244, 0): {'speed': None}, (0, 305): {'speed': None}, (488, 305): {'speed': None}, (0, 427): {'speed': None}, (183, 0): {'speed': None}, (244, 488): {'speed': None}, (671, 244): {'speed': None}, (0, 61): {'speed': None}, (549, 488): {'speed': None}, (671, 427): {'speed': None}, (61, 488): {'speed': None}, (0, 244): {'speed': None}, (732, 61): {'speed': None}, (122, 0): {'speed': None}, (61, 0): {'speed': None}, (488, 244): {'speed': None}, (732, 244): {'speed': None}, (732, 366): {'speed': None}, (732, 0): {'speed': None}, (671, 0): {'speed': None}, (366, 488): {'speed': None}, (0, 183): {'speed': None}, (0, 0): {'speed': None}, (671, 488): {'speed': None}, (610, 488): {'speed': None}, (732, 183): {'speed': None}, (183, 488): {'speed': None}, (610, 0): {'speed': None}, (549, 0): {'speed': None}, (122, 244): {'speed': None}, (61, 244): {'speed': None}, (488, 0): {'speed': None}, (732, 488): {'speed': None}, (427, 0): {'speed': None}, (122, 488): {'speed': None}, (549, 244): {'speed': None}, (488, 488): {'speed': None}, (366, 0): {'speed': None}, (0, 366): {'speed': None}, (732, 122): {'speed': None}, (0, 488): {'speed': None}, (549, 61): {'speed': None}}, 'WHITE': {(305, 61): {'speed': None, 'limit': 3}}, 'RED': {(122, 183): {'speed': None, 'limit': 5}, (305, 366): {'speed': None, 'limit': 5}}}, 
				'win': None
				}, 
			'agentAction': None, 
			'agentState': {'medicine': 0}, 
			'effectList': [('changeResource', 'DARKBLUE', 'WHITE', -1), ('killSprite', 'DARKBLUE', 'BROWN')]
			},
		   
			{
			'gameState': {
				'ended': False, 
				'score': 0, 
				'objects': {'BLUE': {(305, 427): {'speed': None}, (122, 305): {'speed': None}}, 'BROWN': {(488, 427): {'speed': None, 'limit': 3}}, 'GOLD': {}, 'LIGHTBLUE': {(427, 244): {'speed': None}}, 'DARKBLUE': {(671, 183): {'speed': 1, 'resources': {'medicine': 0}}}, 'GREEN': {(671, 366): {'speed': None, 'limit': 5}},'PINK': {(183, 427): {'speed': None}, (183, 61): {'speed': None}},'ORANGE': {(244, 122): {'speed': None}, (122, 366): {'speed': None}, (427, 183): {'speed': None}}, 'BLACK': {(305, 488): {'speed': None}, (732, 305): {'speed': None}, (0, 122): {'speed': None}, (732, 427): {'speed': None}, (305, 0): {'speed': None}, (610, 244): {'speed': None}, (427, 488): {'speed': None}, (244, 0): {'speed': None}, (0, 305): {'speed': None}, (488, 305): {'speed': None}, (0, 427): {'speed': None}, (183, 0): {'speed': None}, (244, 488): {'speed': None}, (671, 244): {'speed': None}, (0, 61): {'speed': None}, (549, 488): {'speed': None}, (671, 427): {'speed': None}, (61, 488): {'speed': None}, (0, 244): {'speed': None}, (732, 61): {'speed': None}, (122, 0): {'speed': None}, (61, 0): {'speed': None}, (488, 244): {'speed': None}, (732, 244): {'speed': None}, (732, 366): {'speed': None}, (732, 0): {'speed': None}, (671, 0): {'speed': None}, (366, 488): {'speed': None}, (0, 183): {'speed': None}, (0, 0): {'speed': None}, (671, 488): {'speed': None}, (610, 488): {'speed': None}, (732, 183): {'speed': None}, (183, 488): {'speed': None}, (610, 0): {'speed': None}, (549, 0): {'speed': None}, (122, 244): {'speed': None}, (61, 244): {'speed': None}, (488, 0): {'speed': None}, (732, 488): {'speed': None}, (427, 0): {'speed': None}, (122, 488): {'speed': None}, (549, 244): {'speed': None}, (488, 488): {'speed': None}, (366, 0): {'speed': None}, (0, 366): {'speed': None}, (732, 122): {'speed': None}, (0, 488): {'speed': None}, (549, 61): {'speed': None}}, 'WHITE': {(305, 61): {'speed': None, 'limit': 3}}, 'RED': {(122, 183): {'speed': None, 'limit': 5}, (305, 366): {'speed': None, 'limit': 5}}}, 
				'win': None
				}, 
			'agentAction': None, 
			'agentState': {'medicine': 0}, 
			'effectList': [('killSprite', 'DARKBLUE', 'GOLD')]
			},
		],    
		{'ended': True, 'win': True}
	]

	"""
	Testing for loss termination conditions in a simple game setting
	"""
	rawTrace_simple_loss = [
	[
	{
	'gameState': {
		'ended': False, 
		'score': 0, 
		'objects': {'BLUE': {(305, 427): {'speed': None}, (122, 305): {'speed': None}}, 'BROWN': {(488, 427): {'speed': None, 'limit': 3}}, 'GOLD': {(671, 183): {'speed': None}}, 'LIGHTBLUE': {(427, 244): {'speed': None}}, 'DARKBLUE': {}, 'GREEN': {(671, 366): {'speed': None, 'limit': 5}}, 'PINK': {(183, 427): {'speed': None}, (183, 61): {'speed': None}}, 'ORANGE': {(244, 122): {'speed': None}, (122, 366): {'speed': None}, (366, 183): {'speed': None}}, 'BLACK': {(305, 488): {'speed': None}, (732, 305): {'speed': None}, (0, 122): {'speed': None}, (732, 427): {'speed': None}, (305, 0): {'speed': None}, (610, 244): {'speed': None}, (427, 488): {'speed': None}, (244, 0): {'speed': None}, (0, 305): {'speed': None}, (488, 305): {'speed': None}, (0, 427): {'speed': None}, (183, 0): {'speed': None}, (244, 488): {'speed': None}, (671, 244): {'speed': None}, (0, 61): {'speed': None}, (549, 488): {'speed': None}, (671, 427): {'speed': None}, (61, 488): {'speed': None}, (0, 244): {'speed': None}, (732, 61): {'speed': None}, (122, 0): {'speed': None}, (61, 0): {'speed': None}, (488, 244): {'speed': None}, (732, 244): {'speed': None}, (732, 366): {'speed': None}, (732, 0): {'speed': None}, (671, 0): {'speed': None}, (366, 488): {'speed': None}, (0, 183): {'speed': None}, (0, 0): {'speed': None}, (671, 488): {'speed': None}, (610, 488): {'speed': None}, (732, 183): {'speed': None}, (183, 488): {'speed': None}, (610, 0): {'speed': None}, (549, 0): {'speed': None}, (122, 244): {'speed': None}, (61, 244): {'speed': None}, (488, 0): {'speed': None}, (732, 488): {'speed': None}, (427, 0): {'speed': None}, (122, 488): {'speed': None}, (549, 244): {'speed': None}, (488, 488): {'speed': None}, (366, 0): {'speed': None}, (0, 366): {'speed': None}, (732, 122): {'speed': None}, (0, 488): {'speed': None}, (549, 61): {'speed': None}}, 'WHITE': {(305, 61): {'speed': None, 'limit': 3}, (305, 305): {'speed': None, 'limit': 3}}, 'RED': {(122, 183): {'speed': None, 'limit': 5}, (305, 366): {'speed': None, 'limit': 5}}}, 
		'win': None}, 
	'agentAction': 'down', 
	'agentState': {}, 
	'effectList': [('changeResource', 'DARKBLUE', 'WHITE', -1), ('killSprite', 'DARKBLUE', 'BROWN')]}
	],
	{'ended': True, 'win': False}
	]


	"""
	Testing preconditions
	"""

	rawTrace_preconditions_simple = (
		[{'gameState': {
			'ended': False, 
			'score': 0, 
			'objects': {'BLUE': {(305, 427): {'speed': None}, (122, 305): {'speed': None}}, 'BROWN': {(488, 427): {'speed': None, 'limit': 3}, (488, 183): {'speed': None, 'limit': 3}}, 'GOLD': {(671, 183): {'speed': None}}, 'LIGHTBLUE': {(427, 244): {'speed': None}}, 'DARKBLUE': {(305, 61): {'speed': 1, 'resources': {'medicine': 1}}}, 'GREEN': {(671, 366): {'speed': None, 'limit': 5}}, 'ORANGE': {(244, 122): {'speed': None}, (122, 366): {'speed': None}, (366, 183): {'speed': None}}, 'BLACK': {(305, 488): {'speed': None}, (732, 305): {'speed': None}, (0, 122): {'speed': None}, (732, 427): {'speed': None}, (305, 0): {'speed': None}, (610, 244): {'speed': None}, (427, 488): {'speed': None}, (244, 0): {'speed': None}, (0, 305): {'speed': None}, (488, 305): {'speed': None}, (0, 427): {'speed': None}, (183, 0): {'speed': None}, (244, 488): {'speed': None}, (671, 244): {'speed': None}, (0, 61): {'speed': None}, (549, 488): {'speed': None}, (671, 427): {'speed': None}, (61, 488): {'speed': None}, (0, 244): {'speed': None}, (732, 61): {'speed': None}, (122, 0): {'speed': None}, (61, 0): {'speed': None}, (488, 244): {'speed': None}, (732, 244): {'speed': None}, (732, 366): {'speed': None}, (732, 0): {'speed': None}, (671, 0): {'speed': None}, (366, 488): {'speed': None}, (0, 183): {'speed': None}, (0, 0): {'speed': None}, (671, 488): {'speed': None}, (610, 488): {'speed': None}, (732, 183): {'speed': None}, (183, 488): {'speed': None}, (610, 0): {'speed': None}, (549, 0): {'speed': None}, (122, 244): {'speed': None}, (61, 244): {'speed': None}, (488, 0): {'speed': None}, (732, 488): {'speed': None}, (427, 0): {'speed': None}, (122, 488): {'speed': None}, (549, 244): {'speed': None}, (488, 488): {'speed': None}, (366, 0): {'speed': None}, (0, 366): {'speed': None}, (732, 122): {'speed': None}, (0, 488): {'speed': None}, (549, 61): {'speed': None}}, 'WHITE': {(305, 305): {'speed': None, 'limit': 3}}, 'RED': {(122, 183): {'speed': None, 'limit': 5}, (305, 366): {'speed': None, 'limit': 5}}}, 
			'win': None}, 
		'agentAction': None, 
		'agentState': {'medicine': 1}, 
		'effectList': [('changeResource', 'DARKBLUE', 'WHITE', 1), ('killSprite', 'DARKBLUE', 'WHITE')]}, 

		{'gameState': {
			'ended': False, 
			'score': 0, 
			'objects': {'BLUE': {(305, 427): {'speed': None}, (122, 305): {'speed': None}}, 'BROWN': {(488, 427): {'speed': None, 'limit': 3}}, 'GOLD': {(671, 183): {'speed': None}}, 'LIGHTBLUE': {(427, 244): {'speed': None}}, 'DARKBLUE': {(488, 183): {'speed': 1, 'resources': {'medicine': 0}}}, 'GREEN': {(671, 366): {'speed': None, 'limit': 5}}, 'ORANGE': {(244, 122): {'speed': None}, (122, 366): {'speed': None}, (366, 183): {'speed': None}}, 'BLACK': {(305, 488): {'speed': None}, (732, 305): {'speed': None}, (0, 122): {'speed': None}, (732, 427): {'speed': None}, (305, 0): {'speed': None}, (610, 244): {'speed': None}, (427, 488): {'speed': None}, (244, 0): {'speed': None}, (0, 305): {'speed': None}, (488, 305): {'speed': None}, (0, 427): {'speed': None}, (183, 0): {'speed': None}, (244, 488): {'speed': None}, (671, 244): {'speed': None}, (0, 61): {'speed': None}, (549, 488): {'speed': None}, (671, 427): {'speed': None}, (61, 488): {'speed': None}, (0, 244): {'speed': None}, (732, 61): {'speed': None}, (122, 0): {'speed': None}, (61, 0): {'speed': None}, (488, 244): {'speed': None}, (732, 244): {'speed': None}, (732, 366): {'speed': None}, (732, 0): {'speed': None}, (671, 0): {'speed': None}, (366, 488): {'speed': None}, (0, 183): {'speed': None}, (0, 0): {'speed': None}, (671, 488): {'speed': None}, (610, 488): {'speed': None}, (732, 183): {'speed': None}, (183, 488): {'speed': None}, (610, 0): {'speed': None}, (549, 0): {'speed': None}, (122, 244): {'speed': None}, (61, 244): {'speed': None}, (488, 0): {'speed': None}, (732, 488): {'speed': None}, (427, 0): {'speed': None}, (122, 488): {'speed': None}, (549, 244): {'speed': None}, (488, 488): {'speed': None}, (366, 0): {'speed': None}, (0, 366): {'speed': None}, (732, 122): {'speed': None}, (0, 488): {'speed': None}, (549, 61): {'speed': None}}, 'WHITE': {(305, 305): {'speed': None, 'limit': 3}}, 'RED': {(122, 183): {'speed': None, 'limit': 5}, (305, 366): {'speed': None, 'limit': 5}}}, 
			'win': None}, 
		'agentAction': None, 
		'agentState': {'medicine': 0}, 
		'effectList': [('changeResource', 'DARKBLUE', 'WHITE', -1), ('killSprite', 'DARKBLUE', 'BROWN')]}, 

		{'gameState': {
			'ended': False, 
			'score': 0, 
			'objects': {'BLUE': {(305, 427): {'speed': None}, (122, 305): {'speed': None}}, 'BROWN': {}, 'GOLD': {(671, 183): {'speed': None}}, 'LIGHTBLUE': {(427, 244): {'speed': None}}, 'DARKBLUE': {}, 'GREEN': {(671, 366): {'speed': None, 'limit': 5}}, 'ORANGE': {(244, 122): {'speed': None}, (122, 366): {'speed': None}, (366, 183): {'speed': None}}, 'BLACK': {(305, 488): {'speed': None}, (732, 305): {'speed': None}, (0, 122): {'speed': None}, (732, 427): {'speed': None}, (305, 0): {'speed': None}, (610, 244): {'speed': None}, (427, 488): {'speed': None}, (244, 0): {'speed': None}, (0, 305): {'speed': None}, (488, 305): {'speed': None}, (0, 427): {'speed': None}, (183, 0): {'speed': None}, (244, 488): {'speed': None}, (671, 244): {'speed': None}, (0, 61): {'speed': None}, (549, 488): {'speed': None}, (671, 427): {'speed': None}, (61, 488): {'speed': None}, (0, 244): {'speed': None}, (732, 61): {'speed': None}, (122, 0): {'speed': None}, (61, 0): {'speed': None}, (488, 244): {'speed': None}, (732, 244): {'speed': None}, (732, 366): {'speed': None}, (732, 0): {'speed': None}, (671, 0): {'speed': None}, (366, 488): {'speed': None}, (0, 183): {'speed': None}, (0, 0): {'speed': None}, (671, 488): {'speed': None}, (610, 488): {'speed': None}, (732, 183): {'speed': None}, (183, 488): {'speed': None}, (610, 0): {'speed': None}, (549, 0): {'speed': None}, (122, 244): {'speed': None}, (61, 244): {'speed': None}, (488, 0): {'speed': None}, (732, 488): {'speed': None}, (427, 0): {'speed': None}, (122, 488): {'speed': None}, (549, 244): {'speed': None}, (488, 488): {'speed': None}, (366, 0): {'speed': None}, (0, 366): {'speed': None}, (732, 122): {'speed': None}, (0, 488): {'speed': None}, (549, 61): {'speed': None}}, 'WHITE': {(305, 305): {'speed': None, 'limit': 3}}, 'RED': {(122, 183): {'speed': None, 'limit': 5}, (305, 366): {'speed': None, 'limit': 5}}}, 
			'win': None}, 
		'agentAction': 'right', 
		'agentState': {'medicine': 0}, 
		'effectList': [('changeResource', 'DARKBLUE', 'WHITE', -1), ('killSprite', 'DARKBLUE', 'BROWN')]}], 
		{'ended': True, 'win': False})



	#################################

	generatedHypotheses = {}

	traces = [
		(rawTrace_simple_win, 1, "rawTrace_simple_win", False), 
		(rawTrace_simple_loss, 2, "rawTrace_simple_loss", False),
		(rawTrace_preconditions_simple, 2, "rawTrace_preconditions_simple", True)
		]


	for trace, expectedHypotheses, name, verbose in traces:
		hypotheses = testTrace(trace, expectedHypotheses, name, verbose)
		generatedHypotheses[name] = hypotheses


	embed()



	#### From previous tests when there were no termination conditions

	# Testing preconditions: one item in backpack changes once
	# Expected: 2 hypotheses
	'''
	rawTrace = [ 
	{'agentAction': None, 'agentState': {}, 'effectList': [('killSprite', 'DARKBLUE', 'BLUE')]}, 
	{'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('killSprite', 'DARKBLUE', 'RED')]}, 
	{'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('bounceForward', 'DARKBLUE', 'BLUE')]}, 
	{'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE')]}, 
	{'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('killSprite', 'DARKBLUE', 'GOLD')]}
	]

	# Testing preconditions: one item in backpack changes twice
	rawTrace = [ 
	{'agentAction': None, 'agentState': {}, 'effectList': [('killSprite', 'DARKBLUE', 'BLUE')]}, 
	{'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('killSprite', 'DARKBLUE', 'RED')]}, 
	{'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('bounceForward', 'DARKBLUE', 'BLUE')]}, 
	{'agentAction': None, 'agentState': {'trap': 0}, 'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE')]}, 
	{'agentAction': None, 'agentState': {'trap': 0}, 'effectList': [('killSprite', 'DARKBLUE', 'GOLD')]}
	]
	'''

	'''
	# Testing lots of different actions
	rawTrace = [
		{'agentAction': None, 'agentState': {}, 'effectList': []}, 
		{'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('collectResource', 'DARKBLUE', 'RED'), ('killSprite', 'DARKBLUE', 'RED')]}, 
		{'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('killSprite', 'DARKBLUE', 'BLUE')]}, 
		{'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE')]}, 
		{'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE'), ('undoAll', 'ORANGE', 'BROWN')]}, 
		{'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE')]}, 
		{'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('bounceForward', 'DARKBLUE', 'PINK')]}, 
		{'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('bounceForward', 'DARKBLUE', 'PINK')]},
		{'agentAction': None, 'agentState': {'treasure': 1, 'trap': 1}, 'effectList': [('collectResource', 'DARKBLUE', 'GREEN'), ('killSprite', 'DARKBLUE', 'GREEN')]}, 
		{'agentAction': 'down', 'agentState': {'treasure': 1, 'trap': 1}, 'effectList': [('changeResource', 'DARKBLUE', 'WHITE', -1), ('killSprite', 'DARKBLUE', 'BROWN')]}]
	'''
	'''
	trace = [tt.TimeStep(tr['agentAction'], tr['agentState'], tr['effectList']) for tr in rawTrace]
	hypotheses=list(g.induction(trace))
	'''
