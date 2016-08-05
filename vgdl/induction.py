import sys, ast, time
from theory_template_080116 import Game, TimeStep
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
    hypotheses=list(g.runDFSInduction(trace, verbose))
    # end = time.time()
    
    return hypotheses


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
        print output_tuple

    hypotheses = runInduction(vgdlString, output_tuple)
    embed()

