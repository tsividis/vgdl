import sys
from theory_template_072516 import Game, TimeStep
import ast
import time

def runInduction(vgdlString, gameOutput):
   
    verbose = True

    g = Game(vgdlString)
    trace = ([TimeStep(tr['agentAction'], tr['agentState'], tr['effectList'], tr['gameState']) for tr in gameOutput[0]],gameOutput[1])
    # start = time.time()
    hypotheses=list(g.induction(trace, verbose))
    # end = time.time()
    
    return hypotheses


if __name__ == "__main__":
    """
    Run: "python induction.py ../vgdl_text/aliens.txt ../output/aliens.txt" 
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

