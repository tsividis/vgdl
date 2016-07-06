from theory_template import *

if __name__ == "__main__":
    g = Game()
    e = ('killSprite', 'WHITE', 'DARKBLUE')
    e2 = ('killSprite', 'WHITE', 'PURPLE')
    e3 = ('bounceForward', 'BLUE', 'PINK')
    e4 = ('bounceForward', 'RED', 'ORANGE')
    events = [e,e2,e3,e4] 
    
    hypotheses = induction(events)
    for h in hypotheses:
        h.display()



    '''
    g.hypothesisSpace.append(t)
    print hypothesisSpace[0].likelihood(g.backpack, e)
    proposals = hypothesisSpace[0].generateProposals(g.backpack, e)
    hypothesisSpace[0].extend(proposals, [e])
    print hypothesisSpace[0].likelihood(g.backpack, e)
    print "____"
    print len(hypothesisSpace), "hypotheses"
    proposals = hypothesisSpace[0].generateProposals(g.backpack, e2)
    hypothesisSpace[0].extend(proposals, [2])
    print len(hypothesisSpace), "hypotheses"
    print hypothesisSpace[0].likelihood(g.backpack, e2)
    print "____"
    print [h.likelihood(g.backpack, e3) for h in hypothesisSpace]

    proposals = hypothesisSpace[0].generateProposals(g.backpack, e3)
    hypothesisSpace[0].extend(proposals)
    print [h.likelihood(g.backpack, e3) for h in hypothesisSpace]

    [h.interpret(e3) for h in hypothesisSpace]
    [h.interpret(e4) for h in hypothesisSpace]

    for h in hypothesisSpace:
        proposals = h.generateProposals(g.backpack, e4)
        print len(proposals), "proposals. extending now"
        if len(proposals)>0:
            h.extend(proposals)
        print ""

    print "___"
    for h in hypothesisSpace:
        h.display()
        print [h.likelihood(g.backpack,e) for e in events]
        print "___"



    print ""
    print "trying to interpret event", e
    print "result:", t.interpret(e) #False
    print "likelihood", t.likelihood(g.backpack, e) #0
    proposals = t.generateProposals(g.backpack, e) #proposals is a list of proposals
    t.addProposal(proposals[0])
    print "likelihood", t.likelihood(g.backpack, e) #1
    t.displayRules() #one rule
    t.displayClasses()

    # h1 = Hypothesis(None, t)
    print ""
    print "likelihood of new event", e2, t.likelihood(g.backpack, e2)
    proposals = t.generateProposals(g.backpack, e2)
    t.addProposal(proposals[0])
    print "likelihood", t.likelihood(g.backpack, e2)
    proposal = proposals[0]

    t.displayRules() #one rule
    t.displayClasses()
    print ""

    print "likelihood of new event", e3, t.likelihood(g.backpack, e3)
    proposals = t.generateProposals(g.backpack, e3) #
    print "generated", len(proposals), "proposals in total"
    proposal = random.choice(proposals)
    print "Randomly selecting one of these"
    t.addProposal(proposal)
    t.displayRules()
    t.displayClasses()
    print "likelihood", t.likelihood(g.backpack, e3)
    print ""

    g.backpack = {'health':0, 'treasure':1, 'coin':3}


    """tests for preconditions"""
    print "Now let's explicitly call keepAssignmentsAddPreconditions() on e2", e2
    proposals = t.keepAssignmentsAddPreconditions(g.backpack, e2)
    print "this generates the following proposals:"
    [p.display() for p in proposals]
    print "notice that because health was 0 when this was called, it doesn't generate any health-related hypotheses"
    print "specifically checking proposal", proposals[3].display()
    print "result:", proposals[3].checkPreconditions(g.backpack) #False --> Should be True
    p = Precondition('health>1','health',1)
    print "adding", p.text, "to those preconditions"
    proposals[3].addPrecondition(p) # Adds p to the fourth precondition
    [p.display() for p in proposals]
    print "result", proposals[3].checkPreconditions(g.backpack) #False
    print "Now adding 2 health to backpack"
    g.backpack['health'] = 2
    print "And re-checking preconditions:", proposals[3].checkPreconditions(g.backpack) #True
    '''

