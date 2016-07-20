import theory_template_071416 as tt
from sampleVGDLString import *
from class_theory_template_071916 import *


g = tt.Game(push_game)

# Testing preconditions
rawTrace = [ 
{'agentAction': None, 'agentState': {}, 'effectList': [('killSprite', 'DARKBLUE', 'BLUE')]}, 
{'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('collectResource', 'DARKBLUE', 'RED'), ('killSprite', 'DARKBLUE', 'RED')]}, 
{'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('bounceForward', 'DARKBLUE', 'BLUE')]}, 
{'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('bounceForward', 'DARKBLUE', 'ORANGE')]}, 
{'agentAction': None, 'agentState': {'trap': 1}, 'effectList': [('killSprite', 'DARKBLUE', 'GOLD')]}
]


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

trace = [tt.TimeStep(tr['agentAction'], tr['agentState'], tr['effectList']) for tr in rawTrace]

hypotheses=list(g.induction(trace))
