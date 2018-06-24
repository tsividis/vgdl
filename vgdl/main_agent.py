# from IPython import embed
from util import *
from core import colorDict, VGDLParser, sys, keyPresses
from ontology import *
from theory_template import TimeStep, Precondition, InteractionRule, TerminationRule, TimeoutRule, \
SpriteCounterRule, MultiSpriteCounterRule, ruleCluster, Theory, Game, writeTheoryToTxt, generateSymbolDict, \
generateTheoryFromGame
import os, subprocess, shutil
from collections import defaultdict
import WBP
import importlib
import numpy as np
import ipdb, time
import copy
from metaplanner import translateEvents, observe
from rlenvironmentnonstatic import createRLInputGame, createRLInputGameFromStrings, defInputGame, createMindEnv
from termcolor import colored
from pygame import K_LEFT, K_UP, K_RIGHT, K_DOWN, K_SPACE

# from line_profiler import LineProfiler

MAX_STEPS = 1000
actionDict = {K_SPACE: 'space', K_UP: 'up', K_DOWN: 'down', K_LEFT: 'left', K_RIGHT: 'right', 0:'none'}
AvatarTypes = [MovingAvatar, HorizontalAvatar, VerticalAvatar, FlakAvatar, AimedFlakAvatar, OrientedAvatar,
RotatingAvatar, RotatingFlippingAvatar, NoisyRotatingFlippingAvatar, ShootAvatar, AimedAvatar,
AimedFlakAvatar, InertialAvatar, MarioAvatar]

# orientationPairs = {(0, 1):(0, -1), DOWN:UP, LEFT:RIGHT, RIGHT:LEFT}

def playCurriculum(agent, level_game_pairs):
    # Necessary to define a top-level function for playCurriculum so that
    # hyperopt.mongoexpt can correctly pickle the objective function
    start_time = time()
    agent.playCurriculum(level_game_pairs)
    end_time = time() - start_time

    return end_time


class Agent:
    def __init__(self, modelType, gameFilename, hyperparameters, parallel_planning=False):
        self.modelType = modelType
        self.gameFilename = gameFilename
        self.gameString = None
        self.levelString = None
        self.hyperparameters = hyperparameters
        self.parallel_planning = parallel_planning
        self.annealingFactor = 1.
        self.shortHorizon = hyperparameters['short_horizon']#False
        self.firstOrderHorizon = hyperparameters['first_order_horizon'] #True ## Makes you commit to a plan once first-order distances change (e.g., spritecounter values)        if self.shortHorizon == True:
        if self.shortHorizon == True:
            self.starting_max_nodes = 1000
            self.max_nodes_annealing = 1.05
        else:
            self.starting_max_nodes = 10000
            self.max_nodes_annealing = 10.
        self.regrounding = 1
        self.selective_regrounding = True
        self.avoid_danger = True
        self.safeDistance = 3
        self.emptyPlansLimit = 5
        self.longHorizonObservationLimit = 2
        self.hypotheses = []
        self.symbolDict = None
        self.finalEventList = []
        self.statesEncountered = []
        self.fakeInteractionRules = []
        self.all_objects = {}
        self.bestSpriteTypeDict = defaultdict(lambda : {})
        self.spriteUpdateDict = defaultdict(lambda : 0)
        self.best_params = None
        self.seen_resources = []
        self.seen_limits = []
        self.new_objects = {}
        self.extra_atom = False

        # Hyperopt output
        self.total_game_steps = 0
        self.total_planner_steps = 0
        self.levels_won = 0

        self.todo_delete = True

    def initializeEnvironment(self):
        if self.gameString==None or self.levelString==None:
            self.gameString, self.levelString = defInputGame(self.gameFilename, randomize=False)
        self.rleCreateFunc = lambda: createRLInputGameFromStrings(self.gameString, self.levelString)
        self.rle = self.rleCreateFunc()
        self.rle._game.spriteUpdateDict = self.spriteUpdateDict
        return

    def initializeRLEFromGame(self):
        gameString, levelString = self.gameString, self.levelString
        if gameString == None or levelString == None:
            gameString, levelString = defInputGame(self.gameFilename, randomize=False)
        rleCreateFunc = lambda: createRLInputGameFromStrings(gameString, levelString)
        rle = rleCreateFunc()
        return rle

    def fastcopy(self, rle):

        newRle = self.initializeRLEFromGame()
        newRle._obstypes = ccopy(rle._obstypes)
        if hasattr(rle, '_gravepoints'):
            newRle._gravepoints = ccopy(rle._gravepoints)
        newRle._game.sprite_groups = ccopy(rle._game.sprite_groups)
        newRle._game.kill_list = ccopy(rle._game.kill_list)
        # newRle._game.lastcollisions = ccopy(rle._game.lastcollisions)
        newRle._game.time = ccopy(rle._game.time)
        newRle._game.score = ccopy(rle._game.score)
        newRle._game.keystate = ccopy(rle._game.keystate)
        newRle.symbolDict = ccopy(rle.symbolDict)
        newRle._game.sprite_groups['avatar'][0].resources = ccopy(rle._game.sprite_groups['avatar'][0].resources)

        return newRle

    def getSpritesByColor(self, rle, color):
        outList = []
        for k in rle._game.sprite_groups.keys():
            if rle._game.sprite_groups[k] and rle._game.sprite_groups[k][0].colorName==color:
                outList.extend(rle._game.sprite_groups[k])
        if outList:
            return outList
        else:
            return None

    def findNearestSprite(self, sprite, spriteList):
        ## returns the sprite in spriteList whose location best matches the location of sprite.
        return sorted(spriteList, key=lambda x:abs(x.rect[0]-sprite.rect[0])+abs(x.rect[1]-sprite.rect[1]))[0]

    def setSpritePositions(self, rle, Vrle, hypothesis):
        ## Sets positions of objects in Vrle to what they were in the rle. Bypasses clunky VGDL level description.

        old_sprite_groups = Vrle._game.sprite_groups
        for k in old_sprite_groups.keys():
            if old_sprite_groups[k]:
                color = Vrle._game.sprite_groups[k][0].colorName
                matchingSpritesInRLE = self.getSpritesByColor(rle, color)
                for sprite in old_sprite_groups[k]:
                    matchingSprite = self.findNearestSprite(sprite, matchingSpritesInRLE)
                    sprite.rect = matchingSprite.rect
                    sprite.lastmove = matchingSprite.lastmove
                    if 'Missile' in str(hypothesis.classes[sprite.name][0].vgdlType) and self.best_params!=None:
                        try:
                            ## Enforce consistency: inferred value for individual orientations has to be consistent with what we're saying the horizontal/vertical orientation is of the entire group.
                            # embed()

                            orientation = tuple(np.sign(np.array(self.rle._game.previousPositions[matchingSprite.ID]) - np.array(self.rle._game.objectMemoryDict[matchingSprite.ID])))

                            if orientation == (0,0):
                                # print "found 0,0 orientation. Using generic missile orientation:", sprite.orientation, sprite.speed, sprite.cooldown
                                pass
                            #     embed()

                            else:
                                sprite.orientation = orientation

                        except KeyError:
                            print "Failed to get params for Missile in main_agent"
                            # embed()
                            pass
        return


    def initializeVrle(self, hypothesis):
        ## World in agent's head given 'hypothesis', including object goal
        gameString, levelString, symbolDict = writeTheoryToTxt(self.rle, hypothesis, self.symbolDict,\
                 "./examples/gridphysics/theorytest.py")
        Vrle = createMindEnv(gameString, levelString, output=False)

        self.setSpritePositions(self.rle, Vrle, hypothesis)

        try:
            Vrle._game.getAvatars()[0].resources = copy.deepcopy(self.rle._game.getAvatars()[0].resources)
            Vrle._game.getAvatars()[0].orientation = copy.deepcopy(self.rle._game.getAvatars()[0].orientation)
            # Vrle._game.getAvatars()[0].resources = ccopy(self.rle._game.getAvatars()[0].resources)
            # Vrle._game.getAvatars()[0].orientation = ccopy(self.rle._game.getAvatars()[0].orientation)
        except (IndexError, AttributeError) as e:
            pass
        # Vrle.immovables, Vrle.killerObjects = immovables, killerObjects
        return Vrle

    def VrleInitPhase(self, flexible_goals=False):
        ## Initialize multiple VRLEs, each corresponding to one hypothesis in self.hypotheses
        VRLEs = []
        # print "in VrleInitPhase.", len(self.hypotheses), "hypotheses"
        # if len(self.hypotheses)>1:
        #     print "more than one hypothesis"

        for hypothesis in self.hypotheses[0:1]:
            tempHypothesis = copy.deepcopy(hypothesis)
            tmpFakeInteractionRules = copy.deepcopy(self.fakeInteractionRules)
            # tmpFakeInteractionRules = ccopy(self.fakeInteractionRules)

            tempHypothesis.interactionSet.extend(tmpFakeInteractionRules)
            if not flexible_goals:
                tempHypothesis.updateTerminations()
            # print "fake hypotheses"
            # if self.fakeInteractionRules:/
                # tempHypothesis.display()
            VRLEs.append(self.initializeVrle(tempHypothesis))
        # print("wrote theory to text")


        return VRLEs

    def initializeHypotheses(self, allObjects, learnSprites=True):
        if learnSprites:
            observe(self.rle, 15, self.bestSpriteTypeDict)
            spriteTypeHypothesis, exceptedObjects, _, self.best_params = sampleFromDistribution(self.rle._game, \
                self.rle._game.spriteDistribution, allObjects, self.rle._game.spriteUpdateDict, self.bestSpriteTypeDict)
            self.rle._game.exceptedObjects = exceptedObjects
            gameObject = Game(spriteInductionResult=spriteTypeHypothesis)
            initialTheory = gameObject.buildGenericTheory(spriteTypeHypothesis)

        else:
            gameObject = Game(self.gameString)
            initialTheory = gameObject.buildGenericTheory(spriteSample=False, vgdlSpriteParse = gameObject.vgdlSpriteParse)

        # Handle wall vs. projectile interaction (hacky)
        avatar = [o for o in initialTheory.spriteSet if o.vgdlType in AvatarTypes][0]
        """
        if 'stype' in avatar.args.keys():
            # old_rule1 = InteractionRule('killSprite', avatar.args['stype'], 'c4', {}, set(), generic=True)
            # old_rule2 = InteractionRule('killSprite', avatar.args['stype'], 'avatar', {}, set(), generic=True)
            # new_rule = InteractionRule('nothing', avatar.args['stype'], 'avatar', {}, set())

            # initialTheory.interactionSet.remove(old_rule1)
            # initialTheory.interactionSet.remove(old_rule2)
            # initialTheory.interactionSet.append(new_rule)
            pass
        """

        self.hypotheses = [initialTheory]

        self.symbolDict = generateSymbolDict(self.rle)

        return gameObject

    def completeHypotheses(self, allObjects, first_time_playing_level):
        previous_colors = [o['type']['color'] for o in self.previous_objects.values()]
        current_colors = [o['type']['color'] for o in allObjects.values()]
        if all([c in previous_colors for c in current_colors]):
            observe(self.rle, 0, self.bestSpriteTypeDict) ## observe a couple steps so that you're not completely clueless about object movements when you're restarting a level.
        else:
            observe(self.rle, 5, self.bestSpriteTypeDict) ## observe many steps so that you're not completely clueless about object movements for the new level

        ## Make sure any objects that appeared while we were observing are reflected in allObjects
        for k,v in self.rle._game.getObjects().items():
            if k not in allObjects:
                allObjects[k] = v

        spriteTypeHypothesis, exceptedObjects, _, self.best_params= sampleFromDistribution(self.rle._game, self.rle._game.spriteDistribution, allObjects, self.rle._game.spriteUpdateDict, self.bestSpriteTypeDict, self.hypotheses[0].spriteSet)
        gameObject = Game(spriteInductionResult=spriteTypeHypothesis)
        newHypotheses = []
        for hypothesis in self.hypotheses:
            newHypotheses.append(gameObject.addNewObjectsToTheory(hypothesis, spriteTypeHypothesis))
        self.hypotheses = newHypotheses


    def playCurriculum(self, heatmap=False, level_game_pairs=None):
        """ Plays a game level until it wins, then moves to the next one until
        completion. """
        if not level_game_pairs:
            level_game_pairs = importlib.import_module(self.gameFilename).level_game_pairs
        episodes = []
        allEffectsEncountered = []
        # if 'images' in os.listdir('.') and 'tmp' in os.listdir('images'):
            # shutil.rmtree("images/tmp")
        # os.makedirs("images/tmp")
        j=0
        flexible_goals = False

        for n_level, level_game in enumerate(level_game_pairs):

            print("Playing level {}".format(n_level))
            (self.gameString, self.levelString) = level_game
            self.max_nodes = self.starting_max_nodes
            win = False
            gameObject = None
            i=0
            levelEffectsEncountered = []
            allStatesEncountered = []
            t1 = time.time()
            first_time_playing_level = True

            while not win and i<10:
                gameObject, win, score, steps, statesEncountered, effectsEncountered = self.playEpisode(gameObject, flexible_goals, win, first_time_playing_level)
                
                self.total_game_steps += steps

                episode_results = (n_level, steps, win, score, self.total_planner_steps)
                episodes.append(episode_results)

                # write progressively to file
                output = {'modelType':self.modelType,
                            'gameName': self.gameFilename,
                            'condition': 'normal',
                            'episodes' : [episode_results]}
                write_to_csv('hyperparameter_idx_'+str(self.hyperparameters['idx']), str(self.gameFilename)+'.csv', output)

                # allStatesEncountered.extend(statesEncountered)
                # levelEffectsEncountered.append(effectsEncountered)
                # VGDLParser.playGame(self.gameString, self.levelString, statesEncountered,
                # persist_movie=False, make_images=False, make_movie=False, movie_dir="videos/"+self.gameFilename, padding=10)
                
                # if self.total_game_steps > MAX_STEPS:
                    # return

                first_time_playing_level = False
                i += 1
                print "Finished in ", time.time() - t1
                # embed()
            # if i >=10:
            #     return
            if i < 10:
                self.levels_won += 1

            if heatmap:
                self.makeHeatmap(allStatesEncountered, '{}_{}_level{}_heatmap.pdf'.format(
                    # self.gameFilename[self.gameFilename.find('expt'):],
                    gvgname[gvgname.find('set_1/')+6:],
                    self.modelType, n_level))

            allEffectsEncountered.append(levelEffectsEncountered)

            ## Uncomment if you want to run flexible goals version.
            # j+=1
            # if j>0:
            #     flexible_goals=True

            if flexible_goals:
                ## When you embed, you can manually input changes in theory. See flexible_goals.py for an example.
                print "in main_agent; playing with flexible_goals"
                embed()

        # self.makeMovie()


        # output = {'modelType':self.modelType,
        #             # 'gameName': self.gameFilename[self.gameFilename.find('expt'):],
        #             'gameName': self.gameFilename,
        #             'condition': 'normal',
        #             'episodes' : episodes}
        #
        #
        # write_to_csv(str(self.gameFilename)+'.csv', output)

    def makeHeatmap(self, statesEncountered, filename):
        from vgdl.plotting import featurePlot
        import matplotlib.pyplot as plt
        from matplotlib.ticker import NullLocator
        import numpy as np

        states = [s['objects']['avatar'].keys()[0] for s in statesEncountered
                  if s['objects']['avatar'].keys()]
        width, height = self.rle._game.width, self.rle._game.height
        correction_factor = self.rle._game.screensize[0]/width
        corrected_states = [(s[0]/correction_factor, s[1]/correction_factor) for s in states]

        m = np.zeros((width, height))
        Xs, Ys = [],[]
        im = plt.imread('flexible_goals.png')
        implot = plt.imshow(im)
        w, h = implot.get_extent()[1], implot.get_extent()[2]
        block_size = w/width

        for s in corrected_states:
            x = s[0]
            y = s[1]
            m[x, y] += 1
            Xs.append(x*block_size+block_size/2.)
            Ys.append(y*block_size+block_size/2.)
        plt.scatter(x=Xs, y=Ys, alpha=.5, edgecolor='')
        # plt.imshow(m.T, cmap='viridis')
        plt.gca().set_axis_off()
        plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0,
            hspace = 0, wspace = 0)
        plt.margins(0, 0)
        plt.gca().xaxis.set_major_locator(NullLocator())
        plt.gca().yaxis.set_major_locator(NullLocator())
        plt.savefig(filename, bbox_inches='tight', pad_inches=0)
        plt.close()

    def makeSummaryPlot(self, allEffectsEncountered):
        import matplotlib.pyplot as plt
        import importlib

        mod = importlib('vgdl.colors')
        colors = [cl[0].color for cl in self.hypotheses[0].classes.values()]
        for color in colors:
            times_touched_per_level = []
            for level in allEffectsEncountered:
                times_touched = len([effect
                    for attempt in level
                    for effect in attempt
                    if ((effect[1]==color and effect[2]=='DARKBLUE')
                        or (effect[2]==color and effect[1]=='DARKBLUE'))])
                times_touched_per_level.append(times_touched)
            color_to_plot = [float(value)/255 for value in getattr(mod, color)]
            plt.plot(times_touched_per_level, color=color_to_plot)
        plt.show()


    def makeMovie(self):
        VGDLParser.playGame(self.gameString, self.levelString, self.statesEncountered, \
            persist_movie=True, make_images=True, make_movie=True, movie_dir="videos/"+self.gameFilename, padding=10)

        print "Creating Movie"
        movie_dir = "videos/"+self.gameFilename

        if not os.path.exists(movie_dir):
            print movie_dir, "didn't exist. making new dir"
            os.makedirs(movie_dir)
        round_index = len([d for d in os.listdir(movie_dir) if d != '.DS_Store'])
        video_dirname = movie_dir+"/round"+str(round_index)+".mp4"
        images_dir = "images/tmp/%09d.png"
        com = "ffmpeg -i " +images_dir+ " -pix_fmt yuv420p -filter:v 'setpts=4.0*PTS' "+ video_dirname
        command = "{}".format(com)
        subprocess.call(command, shell=True)
        # empty image directory
        shutil.rmtree("images/tmp")
        os.makedirs("images/tmp")
        return

    def playMultipleEpisodes(self, num_episodes):
        i=0
        gameObject = None
        wins, scores = [], []
        win = False
        while i<num_episodes:
            gameObject, win, score, statesEncountered, _ = self.playEpisode(gameObject, flexible_goals=False,first_time_playing_level=False)
            wins.append(win)
            scores.append(score)
            i+=1
        VGDLParser.playGame(self.gameString, self.levelString, self.statesEncountered, \
            persist_movie=True, make_images=True, make_movie=True, movie_dir="videos/"+self.gameFilename, padding=10)
        print "Won {} out of {} episodes.".format(sum(wins), i)

        """
        def playEpisodeProfiler(self, gameObject, flexible_goals=False, first_time_playing_level=False):
            lp = LineProfiler()
            lp_wrapper = lp(self.playEpisode)
            gameObject, win, score, steps, statesEncountered, effectsEncountered = lp_wrapper(gameObject, flexible_goals, first_time_playing_level)
            lp.print_stats()
            return gameObject, win, score, steps, statesEncountered, effectsEncountered
        """

    def playEpisode(self, gameObject, flexible_goals=False, win=False, first_time_playing_level=False, pool=None):
        from vgdl.util import manhattanDist

        ## Initialize external environment
        self.initializeEnvironment()
        print "initializing RLE"
        steps = 0
        self.quits = 0
        self.longHorizonObservations = 0
        self.previous_objects = self.all_objects if self.all_objects else {}
        self.all_objects= self.rle._game.getObjects()
        ended, win = self.rle._isDone()
        annealing = 1
        ## Start storing encountered states.
        effectsEncountered = []
        statesEncountered = [self.rle._game.getFullState()]
        self.statesEncountered.append(self.rle._game.getFullState())

        ## Initialize memory of object positions
        self.rle._game.objectMemoryDict, self.rle._game.previousPositions = {}, {}
        for k, v in self.rle._game.all_objects.iteritems():
            self.rle._game.objectMemoryDict[k] = (int(self.rle._game.all_objects[k]['sprite'].rect.x), int(self.rle._game.all_objects[k]['sprite'].rect.y))
            self.rle._game.previousPositions[k] = (int(self.rle._game.all_objects[k]['sprite'].rect.x), int(self.rle._game.all_objects[k]['sprite'].rect.y))

        ## initialize theory if necessary.
        if len(self.hypotheses) == 0:
            gameObject = self.initializeHypotheses(self.all_objects, learnSprites=True)
            print "initializing hypotheses"
        else:
            gameObject = self.completeHypotheses(self.all_objects, first_time_playing_level)
            print "had hypotheses -- completing them."
            # If theory is being carried over, falsify termination hypotheses
            # given new level state
            if not flexible_goals:
                [t.updateTerminations(rle=self.rle) for t in self.hypotheses]

        emptyPlans = 0
        while not ended:
            ## initialize one or many VRLEs according to hypothesis-selection method
            theoryRLEs = self.VrleInitPhase(flexible_goals)

            quitting = False

            planner_hyperparameters = dict((k, self.hyperparameters[k]) for k in self.hyperparameters.keys() if k not in ['idx', 'short_horizon', 'first_order_horizon'])

            ## Initialize planner
            p = WBP.WBP(theoryRLEs[0], self.gameFilename, theory=self.hypotheses[0], fakeInteractionRules = self.fakeInteractionRules,
                seen_limits = self.seen_limits, annealing=annealing, max_nodes=self.max_nodes, shortHorizon=self.shortHorizon,
                firstOrderHorizon=self.firstOrderHorizon, hyperparameters=planner_hyperparameters, extra_atom=self.extra_atom)
            
            p_quitting = p.quitting
            bestNode, gameStringArray, objectPositionsArray = p.BFS()
            self.total_planner_steps += p.total_nodes

            if bestNode is not None:
                solution = p.solution
                gameString_array = p.gameString_array
                objectPositionsArray = objectPositionsArray[::-1]
            else:
                solution = []

            if solution and not p.quitting:
                print "============================================="
                print "got solution of length", len(solution)
                print colored(p.gameString_array[0], 'green')
                for i,g in enumerate(p.gameString_array[1:]):
                    print actionDict[solution[i]]
                    print colored(g, 'green')
                print "============================================="

            if self.shortHorizon:
                if not solution:
                    emptyPlans +=1
                else:
                    emptyPlans = 0
            else:
                if (not solution) or p_quitting:
                    # Here we make a distinction between quitting because you've
                    # exhausted the number of nodes you can visit or because you
                    # ran out of novelty. In the first case, you only wait longer,
                    # in the second case, you also add a new atom to IW
                    if p.exhausted_novelty:
                        self.extra_atom = True
                    if self.longHorizonObservations<self.longHorizonObservationLimit:
                        print "Didn't get solution or decided to quit. Observing, then replanning."
                        print('passed here')
                        observe(self.rle, 5, self.bestSpriteTypeDict)
                        solution = [] ## You may have gotten p.quitting but also a solution; make sure you don't try to act on that if the planner decided it wasn't worth it.
                        self.longHorizonObservations += 1
                    else:
                        quitting = True

            # delete planner instance
            # del p

            if emptyPlans > self.emptyPlansLimit:
                observe(self.rle, 5, self.bestSpriteTypeDict)

            if not quitting:
                for i, action in enumerate(solution):
                    self.hypotheses[0].dryingPaint = set()

                    hypotheses, theory_change_flag, effects = self.executeStep(action, self.hypotheses, statesEncountered,
                        run_induction = not flexible_goals)

                    sys.stdout.flush()
                    self.rle._game.nextPositions = {}
                    for k, v in self.rle._game.all_objects.iteritems():
                        self.rle._game.nextPositions[k] = (int(self.rle._game.all_objects[k]['sprite'].rect.x), int(self.rle._game.all_objects[k]['sprite'].rect.y))
                        try:
                            if self.rle._game.previousPositions[k] != self.rle._game.nextPositions[k]:
                                self.rle._game.objectMemoryDict[k] = copy.deepcopy(self.rle._game.previousPositions[k])
                                # self.rle._game.objectMemoryDict[k] = ccopy(self.rle._game.previousPositions[k])

                        except KeyError:
                            pass
                    self.rle._game.previousPositions = copy.deepcopy(self.rle._game.nextPositions)

                    ID = [k for k in self.rle._game.all_objects.keys() if self.rle._game.all_objects[k]['sprite'].colorName=='BROWN']

                    effectsEncountered.extend(effects)
                    steps +=1
                    if theory_change_flag:
                        self.hypotheses = hypotheses
                        break
                    ended, win = self.rle._isDone()
                    if ended:
                        break
                    # if self.total_game_steps > MAX_STEPS:
                        # score = self.rle._game.score
                        # return gameObject, win, score, steps, statesEncountered, effectsEncountered
                    

                    ## Make sure you're far enough from unpredictable dangerous objects.

                    # Check for disparities between plan and reality
                    # (e.g. stochastic effects)
                    # if self.rle._game.is_stochastic and i>self.regrounding:
                    if (i+1)%self.regrounding==0:
                    # if True:
                        try:
                            rlePositions = sorted([(int(item.rect.x), int(item.rect.y), item) for sublist in self.rle._game.sprite_groups.values() for item in sublist])
                            hypPositions = sorted([(int(item.rect.x), int(item.rect.y), item) for sublist in objectPositionsArray[i+1]._game.sprite_groups.values() for item in sublist])
                            rlePositionsTuples, hypPositionsTuples = [(p[0], p[1]) for p in rlePositions], [(p[0], p[1]) for p in hypPositions]

                            killer_types = [inter.slot2 for inter in hypotheses[0].interactionSet if inter.slot1=='avatar' and inter.interaction in ['killSprite']]
                            # print "killer types", killer_types
                            regroundingFlag = False
                            for objPos in hypPositions:
                                if not regroundingFlag and (objPos[0], objPos[1]) not in rlePositionsTuples:
                                    # print "found object position difference", colored(objPos, 'white', 'on_magenta')
                                    # print 'regrounding because of', objPos[2].colorName, objPos[2], "position:", self.rle._rect2pos(objPos[2].rect)
                                    # try:
                                        # print "orientation:", objPos[2].orientation
                                    # except AttributeError:
                                        # pass
                                    nearest = self.findNearestSprite(objPos[2], [h[2] for h in rlePositions])
                                    # print "Nearest sprite:", nearest.colorName, nearest, "position:", self.rle._rect2pos(nearest.rect)
                                    # try:
                                        # print "orientation:", nearest.orientation
                                    # except AttributeError:
                                        # pass
                                    # print ""
                                    # embed()
                                    if self.selective_regrounding:
                                        if ((objPos[2].name=='avatar') or
                                            (objPos[2].name in killer_types and manhattanDist(self.rle._rect2pos(objPos[2].rect), self.rle._rect2pos(self.rle._game.getAvatars()[0].rect)) < self.safeDistance)):

                                            # if objPos[2].name=='avatar':
                                                # embed()
                                            regroundingFlag = True
                                            # embed()
                                            break
                                    else:
                                        regroundingFlag = True
                                        break

                            if regroundingFlag:
                                print "regrounding"
                                break
                            # if tuple(rlePositions) != tuple(hypPositions):
                            # # if any(np.where(list(gameString_array[i+1]))[0] !=
                            # #        np.where(list(self.rle.show()))[0]):
                            #     print 'regrounding'
                            #     embed()
                            #     # embed()
                            #     break
                        except:
                            # Mismatch in gamestring lengths
                            print ""
                            print 'regrounding problem'
                            embed()
                            break

                    if self.avoid_danger: ## this is just exercising caution when near random objects, irrespective of whether they kill us or not
                        try:
                            random_npc_colors = [self.hypotheses[0].classes[k][0].color for k in self.hypotheses[0].classes.keys() if self.hypotheses[0].classes[k] and 'Random' in str(self.hypotheses[0].classes[k][0].vgdlType)]
                            random_npc_classes = [k for k in self.rle._game.sprite_groups.keys() if self.rle._game.sprite_groups[k] and self.rle._game.sprite_groups[k][0].colorName in random_npc_colors]
                            random_npc_positions = []

                            for c in random_npc_classes:
                                for element in self.rle._game.sprite_groups[c]:
                                    if element not in self.rle._game.kill_list:
                                        random_npc_positions.append(self.rle._rect2pos(element.rect))

                            # random_npc_positions = [self.rle._rect2pos(element.rect)
                            #     for objName in self.rle._game.sprite_groups.keys()
                            #     for element in self.rle._game.sprite_groups[objName]
                            #     if element not in self.rle._game.kill_list and
                            #     'RandomNPC' in str(self.hypotheses[0].classes[
                            #         self.hypotheses[0].colorToClassMapper(
                            #         element.colorName)][0].__class__)]

                            avatar_positions = [self.rle._rect2pos(avatar.rect)
                                 for avatar in self.rle._game.getAvatars()]

                            possiblePairList = [manhattanDist(avatar, random)
                                for avatar in avatar_positions
                                for random in random_npc_positions]
                            # embed()
                            # print "random distances", min(possiblePairList)
                            if min(possiblePairList) < self.safeDistance:
                                print("Close to RandomNPC, regrounding")
                                break

                        except ValueError:
                            # print("error in avoid_danger: is the avatar dead?")
                            pass


                if self.shortHorizon:
                    self.max_nodes *= self.max_nodes_annealing
            else:
                ## You failed the game either because you made a mistake you couldn't recover from or because you timed out in your search.
                ## Search more deeply next time.
                self.max_nodes *= self.max_nodes_annealing
                # self.updateMemory(self.rle)

                return gameObject, False, self.rle._game.score, steps, statesEncountered, effectsEncountered


            annealing *= self.annealingFactor
            ended, win = self.rle._isDone()
            # if ended and not win:
            #     print "lost game. embedding"
            #     embed()


        ## Update global memory of updates
        # for k in game.spriteUpdateDict:
            # self.spriteUpdateDict[k] = game.spriteUpdateDict[k]

        score = self.rle._game.score
        # self.updateMemory(self.rle)

        output =          "ended episode. Win={}                                           ".format(win)
        if win:
            print colored('________________________________________________________________', 'white', 'on_green')
            print colored('________________________________________________________________', 'white', 'on_green')

            print colored(output, 'white', 'on_green')
            print colored('________________________________________________________________', 'white', 'on_green')
        else:
            print colored('________________________________________________________________', 'white', 'on_red')
            print colored(output, 'white', 'on_red')
            print colored('________________________________________________________________', 'white', 'on_red')


        return gameObject, win, score, steps, statesEncountered, effectsEncountered

    def matchEventToRuleByIDAndSpriteName(self, event, rule):
        # Check if the two objects involved in the
        # event are the same as those in the novelty
        # termination rule (invariant by order)
        hypSlot1 = self.hypotheses[0].spriteObjects[event[1]].className
        hypSlot2 = self.hypotheses[0].spriteObjects[event[2]].className
        if set([hypSlot1, hypSlot2]) == set([rule.slot1, rule.slot2]):
            if not rule.preconditions:
                return True
            else:
                if not all([p.check(self.rle.agentStatePrev) for p in list(rule.preconditions)]):
                    return False
                else:
                    return True
        else:
            return False

    def manageNewObjects(self, hypotheses):
        ## Add newly-seen objects.
        current_objects = self.rle._game.getObjects()
        for k in current_objects.keys():
            spriteName = current_objects[k]['sprite'].name
            if spriteName not in [self.all_objects[key]['sprite'].name for key in self.all_objects.keys()]:
                print "new object", spriteName
                self.all_objects[k] = current_objects[k]
                distributionInitSetup(self.rle._game, k)
                ## prevent spriteInduction from trying to infer anything about newly-appeared sprites in this timestep.
                self.rle._game.ignoreList.append(k)
                self.new_objects[spriteName] = 0


        # for k in self.new_objects.keys():
        #     self.new_objects[k] += 1

        # if any([self.new_objects[k]>5 for k in self.new_objects.keys()]):
        #     # if self.new_objects[k] > 5:
        #     spriteTypeHypothesis, exceptedObjects, _, self.best_params = sampleFromDistribution(self.rle._game, self.rle._game.spriteDistribution, self.all_objects, self.rle._game.spriteUpdateDict, self.bestSpriteTypeDict, self.hypotheses[0].spriteSet)
        #     gameObject = Game(spriteInductionResult=spriteTypeHypothesis)

        #     newHypotheses = []
        #     for hypothesis in hypotheses:
        #         newHypotheses.append(gameObject.addNewObjectsToTheory(hypothesis, spriteTypeHypothesis))
        #     hypotheses = newHypotheses

        # [self.new_objects.pop(k, None) for k in self.new_objects.keys() if self.new_objects[k]>5] ## don't track items once we've updated the theory
        return hypotheses

    """
    def executeStepProfiler(self, action, hypotheses, statesEncountered, run_induction=True):
        lp = LineProfiler()
        lp_wrapper = lp(self.executeStep)
        hypotheses, theory_change_flag, effects = lp_wrapper(action, hypotheses, statesEncountered, run_induction)
        lp.print_stats()
        return hypotheses, theory_change_flag, effects
    """


    def executeStep(self, action, hypotheses, statesEncountered, run_induction=True):

        theory_change_flag = False

        spriteInduction(self.rle._game, step=1, bestSpriteTypeDict=self.bestSpriteTypeDict, oldSpriteSet=hypotheses[0].spriteSet)
        spriteInduction(self.rle._game, step=2, bestSpriteTypeDict=self.bestSpriteTypeDict, oldSpriteSet=hypotheses[0].spriteSet)

        try:
            agentState = copy.deepcopy(self.rle._game.getAvatars()[0].resources)
            # agentState = ccopy(self.rle._game.getAvatars()[0].resources)

        except IndexError:
            agentState = defaultdict(lambda: 0)

        res = self.rle.step(action)

        print ""
        print keyPresses[action]

        try:
            agentState = copy.deepcopy(self.rle._game.getAvatars()[0].resources)
            # agentState = ccopy(self.rle._game.getAvatars()[0].resources)

            for e in res['effectList']:
                if 'changeResource' in e:
                    changes = e[3]
                    if changes['value'] < 0:
                        # ipdb.set_trace()
                        # undo one negative change to account for eventhandler ordering
                        agentState[changes['resource']] -= changes['value']
                        break
            self.rle.agentStatePrev = agentState
        # If agent is killed before we get agentState
        except (IndexError, AttributeError) as e:
            # agentState = defaultdict(lambda:0)
            ignored_negative_change = False
            for e in res['effectList']:
                if 'changeResource' in e:
                    changes = e[3]
                    if changes['value'] > 0 or ignored_negative_change:
                        agentState[changes['resource']] += changes['value']
                    else:
                        agentState[changes['resource']] += 0
                        ignored_negative_change = True
            self.rle.agentStatePrev = agentState


        # embed()
        hypotheses = self.manageNewObjects(hypotheses)

        statesEncountered.append(self.rle._game.getFullState())
        self.statesEncountered.append(self.rle._game.getFullState())
        terminal = self.rle._isDone()[0]

        distributionsHaveChanged = spriteInduction(self.rle._game, step=3, bestSpriteTypeDict=self.bestSpriteTypeDict, oldSpriteSet=hypotheses[0].spriteSet)

        effects = translateEvents(res['effectList'], self.all_objects, self.rle)
        print self.rle.show(color='blue')
        print self.rle._game.score

        all_effects = [item for sublist in [e['effectList'] for e in self.finalEventList] for item in sublist]

        event = {'agentState': agentState, 'agentAction': action, 'effectList': effects, \
            'gameState': self.rle._game.getFullStateColorized(), 'rle': self.rle}
        if event['effectList']:
            self.finalEventList.append(event)

        if (event['effectList'] and run_induction) or distributionsHaveChanged:

            print "event", (not all([e in all_effects for e in effects])), "distributions changed", distributionsHaveChanged

            ## Delete fake interaction rules for events that were witnessed in this time step.
            oldFakeInteractionRules = copy.deepcopy(self.fakeInteractionRules)
            # oldFakeInteractionRules = ccopy(self.fakeInteractionRules)

            self.fakeInteractionRules = [r for r in self.fakeInteractionRules if
                not any([self.matchEventToRuleByIDAndSpriteName(e, r) for e in event['effectList']])]

            if (not all([e in all_effects for e in effects])) or distributionsHaveChanged:
                theory_change_flag = True

            sample, exceptedObjects, _, self.best_params= sampleFromDistribution(self.rle._game, self.rle._game.spriteDistribution, self.all_objects, self.rle._game.spriteUpdateDict, self.bestSpriteTypeDict, self.hypotheses[0].spriteSet)

            # for s in sample:
                # s.display()
            # embed()
            game_object = Game(spriteInductionResult=sample)

            terminationCondition = {'ended': False, 'win':False, 'time':self.rle._game.time}
            trace = ([TimeStep(e['agentAction'], e['agentState'], e['effectList'], e['gameState'], e['rle']) \
                for e in self.finalEventList], terminationCondition)
            hypotheses = list(game_object.runInduction(game_object.spriteInductionResult, trace, 20, \
            verbose=False, existingTheories=hypotheses))

            if hypotheses[0].__dict__ != self.hypotheses[0].__dict__:
                theory_change_flag = True

            # if len(hypotheses)>1:
            #     print "more than one hypothesis"

            #  PRECONDITIONS HANDLING
            # Current assumptions:
             # - Only one resource can change for each timestep
            # - The first time a resource changes, it goes from 0 to a positive
            #   value
            for change_resource_effect in [e[3] for e in event['effectList'] if ('changeResource' in e)] + [e[3] for e in event['effectList'] if ('collectResource' in e)]:
                resource = change_resource_effect['resource']
                val = change_resource_effect['value']
                limit = change_resource_effect['limit']

                # print "adding fake rules"
                # import ipdb; ipdb.set_trace()
                # ipdb.set_trace()

                if (resource not in self.seen_resources and val>0):
                    self.fakeInteractionRules.extend(hypotheses[0].updateInteractionsPreconditions(resource))
                    self.fakeInteractionRules = list(set(self.fakeInteractionRules))
                    # resourceColor = self.rle._game.sprite_groups[resource][0].colorName
                    # Add resource change to seen_resources list
                    self.seen_resources.append(resource)


                    hypotheses[0].resource_limits[resource] = limit

                    ## go through everything that can be killed and add a SpriteCounterRule for it?
                    # spritecounter = SpriteCounterRule(limit=limit,
                                              # stype=resource,
                                              # win=True)
                    # hypotheses[0].terminationSet.append(spritecounter)

                elif agentState[resource]==limit and resource not in self.seen_limits:
                    self.fakeInteractionRules.extend(hypotheses[0].updateInteractionsPreconditions(resource, limit))
                    self.fakeInteractionRules = list(set(self.fakeInteractionRules))
                    # resourceColor = self.rle._game.sprite_groups[resource][0].colorName
                    self.seen_limits.append(resource)



                    theory_change_flag = True
                    # print "reached resource limit for", resource

        if event['effectList'] and run_induction:
            [t.updateTerminations(event=event) for t in hypotheses]
        if theory_change_flag and not distributionsHaveChanged:
            print "changed theory:"
            hypotheses[0].display()


        return hypotheses, theory_change_flag, effects



if __name__ == "__main__":

    ##simpleGame_missile: no support for learning that it can shoot things.
    # filename = "examples.gridphysics.demo_helper"


    # filename = "examples.gridphysics.expt_physics_sharpshooter"
    # filename = "examples.gridphysics.demo_transform_relational"
    # filename = "examples.gridphysics.simpleGame_push_boulders"
    # filename = "examples.gridphysics.pick_apples"
    # filename = "examples.gridphysics.expt_exploration_exploitation_debugging"

    filename = "examples.gridphysics_new.expt_preconditions"

    level_game_pairs = None
    # Playing GVG-AI games
    def read_gvgai_game(filename):
        with open(filename, 'r') as f:
            new_doc = []
            g = gen_color()
            for line in f.readlines():
                new_line = (" ".join([string if string[:4]!="img="
                    else "color={}".format(next(g))
                    for string in line.split(" ")]))
                new_doc.append(new_line)
            new_doc = "\n".join(new_doc)
        return new_doc

    def gen_color():
        from vgdl.colors import colorDict
        color_list = colorDict.values()
        color_list = [c for c in color_list if c not in ['UUWSWF']]
        for color in color_list:
            yield color

    gvggames = ['aliens', 'boulderdash', 'butterflies', 'chase', 'frogs',  # 0-4
        'missilecommand', 'portals', 'sokoban', 'survivezombies', 'zelda']  # 5-9

    # gameName = gvggames[5]

    # gvgname = "../gvgai/training_set_1/{}".format(gameName)

    # gameString = read_gvgai_game('{}.txt'.format(gvgname))


    # level_game_pairs = []
    # for level_number in range(5):
        # with open('{}_lvl{}.txt'.format(    gvgname, level_number), 'r') as level:
            # level_game_pairs.append([gameString, level.read()])

    ##uncomment this line to run local games
    gameName = filename

    hyperparameter_sets = [{'sprite_first_alpha': 10000,
     'sprite_second_alpha': 100,
     'sprite_negative_mult': .1,
     'multisprite_first_alpha': 10000,
     'multisprite_second_alpha': 100,
     'novelty_first_alpha': 5000,
     'novelty_second_alpha': 50,
     }]

    agent = Agent('full', gameName, hyperparameter_sets[0])

    ##then pass this down for multiple episodes
    gameObject = None
    agent.playCurriculum(level_game_pairs=level_game_pairs)

    ##and use this line
    # agent.playCurriculum(level_game_pairs=None)
