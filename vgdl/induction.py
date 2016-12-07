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

def runInduction_DFS(vgdlString, gameOutput, maxTheories):

    verbose = True

    g = Game(vgdlString) # Use specific game specifications
    trace = ([TimeStep(tr['agentAction'], tr['agentState'], tr['effectList'], tr['gameState']) for tr in gameOutput[0]],gameOutput[1])
    # start = time.time()


    hypotheses=list(g.runDFSInduction(trace, maxTheories, verbose))
    # end = time.time()
    
    return g, hypotheses


if __name__ == "__main__":
    """
    Run: "python induction.py simpleGame1.txt simpleGame1_game_output.txt" 
    """
    game = sys.argv[1]
    output = sys.argv[2]
    with open("../vgdl_text/{}".format(game), 'r') as vf:
        vgdlString = ast.literal_eval(vf.read())

    with open("../output/{}".format(output), 'r') as f:
        output = f.readline()
        output_tuple = ast.literal_eval(output)
        #print output_tuple

    maxTheories = 100
    game, hypotheses = runInduction_DFS(vgdlString, output_tuple, maxTheories)


    embed()


