"""Module for modifying hypotheses with alternative goals"""
import itertools
import numpy
from IPython import embed
from vgdl.ontology import Resource, ResourcePack, Passive
from vgdl.colors import colorDict
from vgdl.util import ALNUM
from vgdl.theory_template import (Precondition, InteractionRule, TerminationRule, TimeoutRule, SpriteCounterRule,
                                  MultiSpriteCounterRule, Theory, Game, writeTheoryToTxt, generateSymbolDict,
                                  generateTheoryFromGame, expandLine, expandSprites, proposePredicates,
                                  getRuleSetsForClassPairPredicate, interateThresholds)
from vgdl.agent import Agent, initializeVrle
from vgdl.rlenvironmentnonstatic import createRLInputGameFromStrings
from vgdl.stateobsnonstatic import buildTracker
from vgdl.WBP import WBP
from termcolor import colored
from pygame.locals import K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT

def printAllRules(theory):
    for rule in theory.interactionSet:
        rule.display()

def addNewSprite(rle, spriteType, loc):
    s = rle._game._createSprite([spriteType], loc)[0]
    rle._other_types.append(spriteType)
    rle._game.added_sprites.append(s)
    if spriteType not in rle.symbolDict:
        idx=len(rle.symbolDict.keys())
        rle.symbolDict[spriteType]=ALNUM[idx]
    
    for skey in rle._other_types:
        ss = rle._game.sprite_groups[skey]
        rle._obstypes[skey] = [rle._sprite2state(sprite, oriented=False) for sprite in ss]
    return


def createNewClassInfo(theory):
    """creates an unused class name and color"""
    existing_classes = [key for key in theory.classes if key[0] == 'c']
    max_num = max([int(c[1:]) for c in existing_classes])
    class_num = max_num+1
    new_class_name = 'c'+str(class_num)
    used_colors = theory.spriteObjects.keys()
    color = next((c for c in colorDict.itervalues() if c not in used_colors), None)
    return new_class_name, color

class GoalAgent(Agent):
    """An agent that runs games based on another agent's understandning of the game, but
        with modified theories and RLEs to achieve different goals within the game"""
    def __init__(self, agent):
        Agent.__init__(self, agent.modelType, agent.gameFilename, agent.hyperparameter_sets, agent.parallel_planning)
        self.shortHorizon = agent.shortHorizon
        self.starting_max_nodes = agent.starting_max_nodes
        self.max_nodes_annealing = agent.max_nodes_annealing
        self.seen_limits = agent.seen_limits
        self.firstOrderHorizon = agent.firstOrderHorizon
        self.longHorizonObservations = agent.longHorizonObservations
        self.longHorizonObservationLimit = agent.longHorizonObservationLimit


    def constructTargetTheory(self, theory, rle, loc):
        """Creates a copy of the theory with a new class, where the avatar's goal is to collect all objects of this class"""
        h = theory.copy()
        new_name, color = createNewClassInfo(h)
        h.addSpriteToTheory(new_name, color, vgdlType=ResourcePack)
        h.interactionSet.append(InteractionRule('killSprite', new_name, 'avatar', {}, set()))
        h.terminationSet.append(SpriteCounterRule(new_name, 0, True))

        newenv = initializeVrle(h, rle)
        addNewSprite(newenv, new_name, (loc[0], loc[1]))
        return h


    def constructKillSelfTheory(self, theory):
        """Creates a copy of the theory with a new class, where the avatar's goal is to die"""
        h = theory.copy()
        h.terminationSet.remove(SpriteCounterRule('avatar', 0, False))
        h.terminationSet.append(SpriteCounterRule('avatar', 0, True))
        return h


    def constructTouchNothingEverywhereTheory(self, theory, rle):
        """Creates a copy of the theory and rle with a new class object that is placed everywhere that didn't previously have an object.
            In the new theory, the avatar's goal is to collect all of the new objects but not touch anything old"""
        #REVIEW: Does planner try and optimize score? I think it would be more interesting to instead have it try and touch as many 
        #        blank squares as possible but still win the original game
        h = theory.copy()

        new_name, color = createNewClassInfo(h)
        h.addSpriteToTheory(new_name, color, vgdlType=Passive)
        h.interactionSet = [rule for rule in h.interactionSet 
                            if not(rule.slot1 == 'avatar' or rule.slot2 == 'avatar' or
                            rule.slot1 == 'EOS' and rule.slot2 == new_name)]
        for (o1, o2) in itertools.product(['avatar'], h.classes.keys()):
            if o2 == new_name:
                continue
            kill_rule = InteractionRule('killSprite', o1, o2, {}, set())
            h.interactionSet.append(kill_rule)

        h.interactionSet.append(InteractionRule('killSprite', new_name, 'avatar', {}, set()))

        h.terminationSet = [r for r in h.terminationSet if r.ruleType != 'SpriteCounterRule' and
                            r.ruleType != 'MultiSpriteCounterRule']
        h.terminationSet.append(SpriteCounterRule('avatar', 0, False))
        h.terminationSet.append(SpriteCounterRule(new_name, 0, True))

        newenv = initializeVrle(h, rle, writeFile=True)
        board = numpy.zeros(newenv.outdim)
        for locs in newenv._game.sprite_groups.itervalues():
            for loc in locs:
                board[loc.y / 30, loc.x / 30] = 1
        for i in xrange(newenv.outdim[1]):
            for j in xrange(newenv.outdim[0]):
                if board[j][i] == 0:
                    addNewSprite(newenv, new_name, (i * 30, j * 30))

        return h, newenv

    def playGoalCurriculum(self, agent, level_game_pairs=None, num_episodes_per_level=10):
        """ Plays a game with modified goals based on the agent's understanding of the original game """
        print("-----------------------------------------------------------------------")
        print("-----------------------------------------------------------------------")
        print("----------------------------GOAL CURRICULUM----------------------------")
        print("-----------------------------------------------------------------------")
        print("-----------------------------------------------------------------------")
        if not level_game_pairs:
            level_game_pairs = importlib.import_module(self.gameFilename).level_game_pairs
        episodes = []
        
        num_levels = len(level_game_pairs)
        ## for inference
        self.rleHistory = [[] for i in range(num_levels*num_episodes_per_level)]
        self.actionHistory = [[] for i in range(num_levels*num_episodes_per_level)]
        self.all_objects = [{} for i in range(num_levels*num_episodes_per_level)]

        
        episodes_played = 0
        for n_level, level_game in enumerate(level_game_pairs):
            self.gameString = level_game[0]
            self.levelString = level_game[1]
            if self.gameString == None or self.levelString == None:
                self.gameString, self.levelString = defInputGame(self.gameFilename, randomize=False)
            self.rle = createRLInputGameFromStrings(self.gameString, self.levelString)
            self.rle._game.observation = buildTracker(self.rle)
            self.rle._game.spriteUpdateDict = self.spriteUpdateDict
            self.theory, self.rle = self.constructTouchNothingEverywhereTheory(agent.hypotheses[0], self.rle)
            # embed()
            episodes = []

            self.max_nodes = self.starting_max_nodes
            win = False
            i = 0
            while not win and i < num_episodes_per_level:
                win, score, steps = self.playGoalEpisode(n_level, episodes_played, win=win)
                episodes.append((n_level, steps, win, score))
                episodes_played += 1
                if win:
                    print 'won'
                    break
                i += 1
            if i < num_episodes_per_level:
                self.levels_won += 1

        return

    def playGoalEpisode(self, n_level, episode_num, flexible_goals=False, win=False):
        steps, self.quits, self.longHorizonObservations = 0,0,0
        self.all_objects[episode_num] = self.rle._game.getAllObjects()
        ended, win = self.rle._isDone()
        annealing = 1

        self.statesEncountered.append(self.rle._game.getFullState())
        
        envReal = self.fastcopy(self.rle)

        self.rleHistory[episode_num].append(envReal)

        emptyPlans = 0
        while not ended:
            quitting = False
            avatarColor = self.theory.classes['avatar'][0].colorName

            p = WBP(self.rle, self.gameFilename, theory=self.theory, fakeInteractionRules = self.fakeInteractionRules,
                seen_limits = self.seen_limits[avatarColor], annealing=annealing, max_nodes=self.max_nodes, shortHorizon=self.shortHorizon,
                firstOrderHorizon=self.firstOrderHorizon, hyperparameters=self.hyperparameter_sets[0])

            # embed()

            bestNode, gameStringArray, predictedEnvs = p.BFS()

            # best_index = np.argmin([p.total_nodes for p in res._value])
            # bestNode, gameStringArray, predictedEnvs = res._value[best_index].BFS()
            self.total_planner_steps = p.total_nodes

            if bestNode is not None:
                solution = p.solution
                gameString_array = p.gameString_array
                predictedEnvs = predictedEnvs[::-1]
            else:
                solution = []

            if solution and not p.quitting:
                print "============================================="
                print "got solution of length", len(solution)
                for g in p.gameString_array:
                    print colored(g, 'green')
                print "============================================="

            if self.shortHorizon:
                if not solution:
                    emptyPlans +=1
                else:
                    emptyPlans = 0
            else:
                if (not solution) or p.quitting:
                    if self.longHorizonObservations<self.longHorizonObservationLimit:
                        print "Didn't get solution or decided to quit. Observing, then replanning."
                        # embed()
                        self.wait(episode_num, num_steps=5)
                        solution = [] ## You may have gotten p.quitting but also a solution; make sure you don't try to act on that if the planner decided it wasn't worth it.
                        self.longHorizonObservations += 1
                    else:
                        quitting = True

            if emptyPlans > self.emptyPlansLimit:
                print "observing"
                # embed()
                self.wait(episode_num, num_steps=5)

            if not quitting:
                for action_num, action in enumerate(solution):
                    self.executeStep(episode_num, action)
                    
                    _, regroundForKillerTypes, _ = self.regroundOrNot(action_num, predictedEnvs, self.theory)

                    steps +=1

                    ended, win = self.rle._isDone()
                    if regroundForKillerTypes: 
                        print "got reground for killer type. Replanning"
                        break

                    if ended:
                        break

                if self.shortHorizon:
                    self.max_nodes *= self.max_nodes_annealing
            else:
                ## You failed the game either because you made a mistake you couldn't recover from or because you timed out in your search.
                ## Search more deeply next time.
                self.max_nodes *= self.max_nodes_annealing
                print "You got quitting==True from planner. Embedding to debug."
                # embed()
                return False, self.rle._game.score, steps
        
            annealing *= self.annealingFactor
            ended, win = self.rle._isDone()

        score = self.rle._game.score
        output = "ended episode. Win={}                   						  ".format(win)
        if win:
            print colored('________________________________________________________________', 'white', 'on_green')
            print colored('________________________________________________________________', 'white', 'on_green')

            print colored(output, 'white', 'on_green')
            print colored('________________________________________________________________', 'white', 'on_green')
        else:
            print colored('________________________________________________________________', 'white', 'on_red')
            print colored(output, 'white', 'on_red')
            print colored('________________________________________________________________', 'white', 'on_red')

        return win, score, steps

    def executeStep(self, episode_num, action):
        self.actionHistory[episode_num].append(action)
        self.rle.step(action)
        envReal = self.fastcopy(self.rle)
        self.rleHistory[episode_num].append(envReal)
        self.statesEncountered.append(self.rle._game.getFullState())

    def wait(self, episode_num, num_steps=1):
        for i in range(num_steps):
            self.executeStep(episode_num, 0)

                
    # #TEMP: start
    # from goal_programming import *
    # target_theory = constructTargetTheory(self.hypotheses[0], rle, (30, 30))
    # killself_theory = constructKillSelfTheory(self.hypotheses[0])
    # move_theory, newenv = constructTouchNothingEverywhereTheory(self.hypotheses[0], rle)
    # embed()
    # #TEMP: end