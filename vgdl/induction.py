import sys, ast, time
from theory_template import Game, TimeStep
from IPython import embed


def runInduction(vgdlString, gameOutput):
   
    verbose = True

    g = Game(vgdlString)
    trace = ([TimeStep(tr['agentAction'], tr['agentState'], tr['effectList'], tr['gameState']) for tr in gameOutput[0]],gameOutput[1])
    # start = time.time()
    hypotheses=list(g.induction(trace, verbose))
    # end = time.time()
    
    return hypotheses

def runInduction_DFS(vgdlString, gameOutput):

    verbose = True

    g = Game(vgdlString)
    trace = ([TimeStep(tr['agentAction'], tr['agentState'], tr['effectList'], tr['gameState']) for tr in gameOutput[0]],gameOutput[1])
    # start = time.time()
    hypotheses=list(g.runDFSInduction(trace, maxNumTheories=100, verbose=True))
    # end = time.time()
    
    return g, hypotheses


if __name__ == "__main__":
    """
    Run: "python induction.py ../vgdl_text/simpleGame1.txt ../output/simpleGame1.txt" 
    """
    vgdlFile = sys.argv[1]
    with open(vgdlFile, 'r') as vf:
        vgdlString = ast.literal_eval(vf.read())

    gameOutput = sys.argv[2]
    with open(gameOutput, 'r') as f:
        output = f.readline()
        output_tuple = ast.literal_eval(output)
        #print output_tuple

    game, hypotheses = runInduction_DFS(vgdlString, output_tuple)
    embed()

t = hypotheses[0]
cx='c1'
cy='c1'
self=t
cxSlot1 = [(r.interaction, r.slot2, r.preconditions) for r in self.interactionSet 
if r.slot1==cx]
cySlot1 = [(r.interaction, r.slot2, r.preconditions) for r in self.interactionSet 
if r.slot1==cy]

cxSlot2 = [(r.interaction, r.slot1, r.preconditions) for r in self.interactionSet 
if r.slot2==cx]
cySlot2 = [(r.interaction, r.slot1, r.preconditions) for r in self.interactionSet 
if r.slot2==cy]

b = ['1','2','3','4','5']
a = ['1','2','3','4','5']

self.levenshteinDistance(cxSlot1,cySlot1)


