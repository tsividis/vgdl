from theory_template import *
from rlenvironmentnonstatic import defInputGame, createRLInputGame, createRLInputGameFromStrings
from metaplanner import observe
from ontology import *
if __name__ == "__main__":

	filename = "examples.gridphysics.simpleGame_preconditions"
	gameString, levelString = defInputGame(filename, randomize=True)
	rleCreateFunc = lambda: createRLInputGameFromStrings(gameString, levelString)
	rle = rleCreateFunc()
	allObjects= rle._game.getObjects()

	observe(rle, 5)
	spriteTypeHypothesis = sampleFromDistribution(rle._game.spriteDistribution, allObjects)
	gameObject = Game(spriteInductionResult=spriteTypeHypothesis)
	initialTheory = gameObject.buildGenericTheory(spriteTypeHypothesis)

	event1 = {'agentState': {'medicine':0}, 'agentAction': (1,0), \
	'effectList': [('changeResource', 'DARKBLUE', 'WHITE', 'medicine', 1), ('killSprite', 'WHITE', 'DARKBLUE')],\
	 'gameState': None}
	event2 = {'agentState': {'medicine':1}, 'agentAction': (1,0), \
	'effectList': [('stepBack', 'DARKBLUE', 'BLACK')],\
	 'gameState': None}
	event3 = {'agentState': {'medicine':1}, 'agentAction': (1,0), \
	'effectList': [('changeResource', 'DARKBLUE', 'BROWN', 'medicine', -1), ('killSprite', 'BROWN', 'DARKBLUE')],\
	 'gameState': None}
	event4 = {'agentState': {'medicine':0}, 'agentAction': (1,0), \
	'effectList': [('changeResource', 'DARKBLUE', 'BROWN', 'medicine', -1), ('killSprite', 'BROWN', 'DARKBLUE'), \
	('killSprite', 'DARKBLUE', 'BROWN')],\
	 'gameState': None}

	# Testing the two ways in which you could be led to need preconditions
	# eventList = [event1, event2, event3, event4]
	eventList = [event4, event2, event3, event1]

	terminationCondition = {'ended': False, 'win':False, 'time':5}
	trace = ([TimeStep(e['agentAction'], e['agentState'], e['effectList'], e['gameState']) for e in eventList], terminationCondition)
	

	hypotheses = list(gameObject.runInduction(gameObject.spriteInductionResult, trace, 20, verbose=False)) ##if you resample or run sprite induction, this 

	print "found", len(hypotheses), "hypotheses"
	embed()