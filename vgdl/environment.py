from bookkeeping import Bookkeeping
from rlenvironmentnonstatic import createRLInputGame, createRLInputGameFromStrings, defInputGame, createMindEnv
from termcolor import colored
from pygame import K_LEFT, K_UP, K_RIGHT, K_DOWN, K_SPACE
import pygame
from core import fMRI_screensize
from core import VGDLParser
import cPickle, cloudpickle
from datetime import datetime
import os, subprocess, shutil
import time
from vgdl.dqn_agent import DQNAgent
from IPython import embed
import bson

"""
Environment class for running VGDL experiments
"""


MAX_STEPS_PER_LEVEL = 1 + 60 * 20 # momchil: fMRI max steps per instance (i.e. until end of level) = 60 s x 20 fps, + 1 for debugging
MAX_STEPS = MAX_STEPS_PER_LEVEL * 9 + 10000 # momchil: nine levels per game + some buffer
#MAX_STEPS = 100000000 #  ...jk override for DQN training

actionDict = {K_SPACE: 'space', K_UP: 'up', K_DOWN: 'down', K_LEFT: 'left', K_RIGHT: 'right', 0:'none', None: 'none'}

class Environment:
    def __init__(self, gameFilename, agent, task_ID, produce_printout=False, movieName=None):
        self.gameFilename = gameFilename
        self.gameString = None
        self.levelString = None
        self.display_text = False
        self.display_states = False
        self.saveMidEpisode = False
        self.timestamp = False
        self.task_ID = task_ID
        self.loaded_n_level = 0
        self.produce_printout = produce_printout
        self.movieName = movieName
        self.agent = agent
        self.record_fMRIRegressors = agent.record_fMRIRegressors
        self.agent.record_video_info = True
        self.agent.write_video_info = False

        ## used for time-stamping data related to this particular run of the model.
        timestamp = datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d__%H_%M__')+self.task_ID
        
        self.timestamp = timestamp

    # ---------------------------------------------------------------------
    #     Simulator initialization functions
    # ---------------------------------------------------------------------
    def initializeEnvironment(self):
        ## Initialize game environment

        if self.display_text:
            print "initializing RLE"

        if self.gameString==None or self.levelString==None:
            self.gameString, self.levelString = defInputGame(self.gameFilename, randomize=False)
        self.rleCreateFunc = lambda: createRLInputGameFromStrings(self.gameString, self.levelString, visualize=False, screensize=fMRI_screensize)
        self.environment = self.rleCreateFunc()

        # momchil: for DQN
        if isinstance(self.agent, DQNAgent):
            self.environment._game._initScreen(fMRI_screensize, True, None, self.environment._game.offset)
            pygame.display.flip()

        if self.playback_states: # fMRI theory induction from human replay
            self.environment._game.playback_states = self.playback_states
            self.environment._game.playback_keystates = self.playback_keystates
            self.environment._game.action_playback_only = True
            assert self.environment._game.playback_index == 0
            assert len(self.environment._game.playback_states) == len(self.environment._game.playback_keystates)
            # important to set the initial state now -- we getObjects() to initialize the theories in replayEpisode, and the UUIDs of the objects should match up, e.g. for proper event handling
            # important to use default colors -- EMPA relies on colors for stuff, e.g. to detect walls; kinda hacky but let's do that for now
            #print 'initializeEnvironment'
            #embed()
            self.environment._game.setFullState(self.environment._game.playback_states[0], cheap=False, default_colors=True)
            self.environment._game.playback_index += 1
        return

    def initializeRLEFromGame(self):
        ## Part of a method for faster state copying, used in planner, etc.
        gameString, levelString = self.gameString, self.levelString
        if gameString == None or levelString == None:
            gameString, levelString = defInputGame(self.gameFilename, randomize=False)
        rleCreateFunc = lambda: createRLInputGameFromStrings(gameString, levelString)
        environment = rleCreateFunc()
        return environment


    def makeHeatmap(self, statesEncountered, filename):
        from vgdl.plotting import featurePlot
        import matplotlib.pyplot as plt
        from matplotlib.ticker import NullLocator
        import numpy as np

        states = [s['objects']['avatar'].keys()[0] for s in statesEncountered
                  if (not s['observe_state']) and s['objects']['avatar'].keys()]
        width, height = self.environment.width, self.environment.height
        correction_factor = self.environment.screensize[0]/width
        corrected_states = [(s[0]/correction_factor, s[1]/correction_factor) for s in states]

        m = np.zeros((width, height))
        Xs, Ys = [],[]

        block_size=30
        for s in corrected_states:
            x = s[0]
            y = s[1]
            m[x, y] += 1
            Xs.append(x*block_size+block_size/2.)
            Ys.append(y*block_size+block_size/2.)

        plt.imshow(m.T, cmap='viridis')
        plt.gca().set_axis_off()
        plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0,
            hspace = 0, wspace = 0)
        plt.margins(0, 0)
        plt.gca().xaxis.set_major_locator(NullLocator())
        plt.gca().yaxis.set_major_locator(NullLocator())
        plt.savefig(filename, bbox_inches='tight', pad_inches=0)
        plt.close()


    def makeImages(self):
        ## Used for making videos. First we save all states from all episodes as images, then we stitch together into a video.
        # params_to_print_to_video = self.param_ID
        params_to_print_to_video = ''
        game_name_to_print_to_video = self.gameFilename
        VGDLParser.playGame(self.gameString, self.levelString, self.agent.bookkeeping.statesEncountered, \
            persist_movie=True, make_images=True, make_movie=False, movie_dir="videos/", gameName = game_name_to_print_to_video, parameter_string=params_to_print_to_video, padding=10, video_name=self.video_name)

    def makeMovie(self, play_movie=False, regressors=None):
        VGDLParser.playGame(self.gameString, self.levelString, self.agent.bookkeeping.statesEncountered, \
            headless=False, persist_movie=True, make_images=True, make_movie=True, movie_dir="videos/", padding=10, 
            regressors=regressors, screensize=fMRI_screensize, video_name=self.video_name)
 
        # TODO momchil fix -- right now, this uses the wrong images; also playGame already creates a video 
        '''
 
        print "Creating Movie"
        # movie_dir = "videos/{}/{}".format(self.param_ID, self.gameFilename)
        # movie_dir = "videos/"
        movie_dir = "videos/"+self.gameFilename
        if not os.path.exists(movie_dir):
            print movie_dir, "didn't exist. making new dir"
            os.makedirs(movie_dir)

        round_index = len([d for d in os.listdir(movie_dir) if d != '.DS_Store' and self.gameFilename in d])
        # video_dirname = movie_dir+"/round"+str(round_index)+".mp4"
        # video_dirname = movie_dir+"/"+self.gameFilename+'_'+str(round_index)+".mp4"
        video_dirname = movie_dir+"/"+str(self.movieName)+".mp4"
        # images_dir = "images/tmp/{}/%09d.png".format(self.gameFilename)
        images_dir = "images/tmp/%09d.png"
        com = "ffmpeg -i " +images_dir+ " -pix_fmt yuv420p -filter:v 'setpts=4.0*PTS' "+ video_dirname
        command = "{}".format(com)
        print "images/tmp contents:", os.getcwd()
        print "in main agent:", command
        subprocess.call(command, shell=True)
        # empty image directory
        shutil.rmtree("images/tmp/"+self.gameFilename)
        os.makedirs("images/tmp/"+self.gameFilename)

        if play_movie:
            command = ('open', '-a', 'Quicktime Player', video_dirname)
            subprocess.Popen(command)
        '''

        return

    def playCurriculum(self, heatmap=False, level_game_pairs=None, make_movie=False, play_movie=False, playback=False, 
        theory_playback=False, steps_per_level=None):
        """ Plays a game level until it wins, then moves to the next one until
        completion. """
        starttime = time.time()
        if not level_game_pairs:
            level_game_pairs = importlib.import_module(self.gameFilename).level_game_pairs
        episodes = []
        allEffectsEncountered = []

        self.make_movie = make_movie
        self.video_name = None
        self.theory_playback = theory_playback

        if self.make_movie:
            if 'images' in os.listdir('.') and 'tmp' in os.listdir('images') and self.gameFilename in os.listdir('images/tmp'):
                shutil.rmtree("images/tmp/"+self.gameFilename)
            os.makedirs("images/tmp/"+self.gameFilename)

        if self.record_fMRIRegressors:
            curriculumRegressors = [] # regressors from replay for analyzing fMRI data
        else:
            curriculumResults = [] # summary results from generative play for analyzing behavioral data

        loaded_n_level=0
        #curriculumSaveFile = 'curriculum_'+self.gameFilename+'_'+self.agent.param_ID+'_'+self.task_ID
        loadedState = self.agent.bookkeeping.loadCurriculumState(self.agent.bookkeeping.curriculumSaveFile)
        if loadedState is not None and not isinstance(self.agent, DQNAgent):
            # we only use the dqn agent in inference mode, we train it separately
            print '----------- loading curriculum state from ', self.agent.bookkeeping.curriculumSaveFile
            self.agent = loadedState['agent']

            # momchil: for fMRI playback, we give a completely new set of levels every time (b/c we split up the inference into batches on the cluster, b/c of memory issues w/ having all states in memory), and we start curriculum from "level 0" every time
            # so we want loaded_n_level to start from 0 (but still reuse the hypotheses from the previous batch)
            # to be safe, we also remove the loadedState (after getting agent from it) so we don't accidentally let other bookkeeping stuff get loaded later in the code silently
            if playback:
                loadedState = None 
                self.agent.quitting = False # momchil: need to reset this b/c it just never starts the episode TODO how is it not an issue for regular EMPA?
            else:
                loaded_n_level, within_level_iteration = loadedState['agent'].n_level, loadedState['agent'].within_level_iteration            # print "loaded a game"
            # embed()

        j=0
        fullStateEpisodes, episodeCompactStates = {}, {}

        # loop over episodes
        #
        for n_level, level_game in enumerate(level_game_pairs):

            if n_level < loaded_n_level: ## if we have a saved state that corresponds to us having played this level, skip it.
                assert not playback # should never happen in fMRI playback
                continue

            if playback:
                # fMRI playback from human play
                if theory_playback:
                    # replaying theories and states/actions
                    (self.gameString, self.levelString, self.playback_states, self.playback_keystates, self.video_name, reset_finalTimeStepList, self.theory, level_id) = level_game
                else:
                    # replaying states/actions only
                    (self.gameString, self.levelString, self.playback_states, self.playback_keystates, self.video_name, reset_finalTimeStepList, level_id) = level_game
                    self.theory = None
            else:
                assert not theory_playback

                (self.gameString, self.levelString, self.video_name, reset_finalTimeStepList, level_id) = level_game
                self.playback_states = None # TODO momchil undo
                self.playback_keystates = None # TODO momchil undo
                self.theory = None

            print '---------- game'
            print self.gameString
            print '---------- level'
            print self.levelString

            #print 'loop'
            #embed()

            if reset_finalTimeStepList:
                print 'resetting finalTimeStepList'
                self.agent.finalTimeStepList = []
                self.agent.finalEventList = []

            self.agent.level_id = level_id

            self.agent.max_nodes = self.agent.starting_max_nodes
            self.agent.stored_max_nodes = self.agent.max_nodes
            win = False
            gameObject = None
            
            i=0
            if loadedState:
                assert not self.record_fMRIRegressors, 'should never be here in fMRI mode'
                i=loadedState['agent'].within_level_iteration
                episodeCompactStates = loadedState['episodeCompactStates'] # momchil: why do we reload this for every level? not an issue for fMRI b/c we clear loadedState, but still...
            levelEffectsEncountered = []
            allStatesEncountered = []
            allCompactStates = []
            t1 = time.time()

            forfeit_level = False
            # momchil: if running in generative mode (i.e. not replay), # steps = # frames in 1 minute, just like in the fMRI design
            remaining_steps_for_level = None if self.record_fMRIRegressors else steps_per_level

            #while not win and not forfeit_level:# and i<15 :
            while remaining_steps_for_level is None or remaining_steps_for_level > 0: # momchil: emulate fMRI design
                self.n_level = n_level
                self.agent.n_level = n_level
                self.within_level_iteration = i
                self.agent.within_level_iteration = i
                
                print 'checkpoint 0'
                gameObject, win, score, steps, forfeit_level, episodeSteps, ended = self.playEpisode(gameObject, win, remaining_steps_for_level)

                # momchil: fMRI
                if not self.record_fMRIRegressors:
                    # generative play
                    assert episodeSteps <= remaining_steps_for_level
                    remaining_steps_for_level -= episodeSteps 
                    print '         steps, remaining ', episodeSteps, remaining_steps_for_level, len(self.agent.bookkeeping.statesEncountered)

                    zstates = VGDLParser.compress({'states': self.agent.bookkeeping.statesEncountered})

                    curriculumResults.append({
                        'game_name': self.gameFilename,
                        'level': level_id,
                        'win': win,
                        'score': score,
                        'ended': ended,
                        'steps': episodeSteps,
                        'agent': str(type(self.agent)),
                        'zstates': bson.binary.Binary(zstates)
                    })
                
                ## TODO: clean up below stuff, too.
                statesEncountered = self.agent.bookkeeping.statesEncountered
                compactStates = self.agent.bookkeeping.compactStates
                effectsEncountered = self.agent.bookkeeping.effectsEncountered

                self.agent.memory.totalGameSteps += steps
                allCompactStates.append(compactStates)
                episode_results = (n_level, steps, win, score, self.agent.total_planner_steps)
                episodes.append(episode_results)

                print 'checkpoint 1'

                if self.make_movie:
                    # self.statesEncountered = statesEncountered
                    #self.makeImages() # TODO momchil why is this necessary when we call makeMovie which does the same thing? also this doesn't really work it seems
                    pass
                
                if self.agent.record_video_info:
                    allStatesEncountered.extend(statesEncountered)

                i += 1
                print 'checkpoint 2'

                episodeCompactStates[n_level] = allCompactStates
                fullStateEpisodes[n_level] = allStatesEncountered

                # print "about to save state"
                # embed()

                #if not self.record_fMRIRegressors: # we save it later in fMRI mode -- see below
                #    self.agent.bookkeeping.saveCurriculumState(self.agent, episodeCompactStates, self.record_fMRIRegressors)
                # print "saved state"
                # embed()
                ## will write all previous episodes to the file at the end of each episode.
                if self.agent.record_states:
                    gameInfo = {'gameString':self.gameString, 'levelString':self.levelString, 'gameName':self.gameFilename}
                    episodeList = [v for k,v in sorted(episodeCompactStates.items())]

                    with open(self.agent.filename, 'wb') as f:
                        cPickle.dump({'gameInfo':gameInfo,'modelParams':self.agent.param_ID, 'episodes':episodeList, 'time_elapsed':time.time()-starttime}, f)

                print 'checkpoint 3'

                # momchil 2026_03_26: commented out to fix fMRI per-level invocation bug
                # (agent.n_level was being incremented on each win, causing loaded_n_level > 0
                # on subsequent invocations which then skipped the single level_game_pair)
                #if win:
                #    self.n_level += 1
                #    self.agent.n_level += 1
                #    self.within_level_iteration = 0
                #    self.agent.within_level_iteration = 0

                print 'checkpoint 4'
                    
                ## will write video data at the end of each episode
                if self.agent.record_video_info:
                    fullStateList = [v for k,v in sorted(fullStateEpisodes.items())]
                if self.agent.write_video_info:
                    videofilename = "{}{}_{}".format(self.agent.dirname_for_video, self.gameFilename, self.timestamp)
                    gameInfo = {'gameString':self.gameString, 'levelString':self.levelString, 'gameName':self.gameFilename}
                    with open(videofilename, 'wb') as f:
                        cPickle.dump({'gameInfo':gameInfo,'modelParams':self.agent.param_ID, 'episodes':fullStateList, 'time_elapsed':time.time()-starttime}, f)
                if self.agent.memory.totalGameSteps > MAX_STEPS:
                    if self.produce_printout:
                        print "reached max number of steps ({}>{}) in playCurriculum. Stopping experiment".format(self.agent.memory.totalGameSteps, MAX_STEPS)

                print 'checkpoint 5'
                self.agent.bookkeeping.deleteEpisodeFile()

                if self.record_fMRIRegressors:
                    # momchil: we only do 1 iteration for fMRI (b/c it's just replay; we can't "retry")
                    # TODO better way?
                    break

                print 'checkpoint 6'
            if heatmap:
                self.makeHeatmap(allStatesEncountered, 'heatmap_{}_{}_level{}.pdf'.format(self.gameFilename, n_level, self.agent.param_ID))

            # append after each episode 
            if self.record_fMRIRegressors:
                curriculumRegressors.append(self.agent.bookkeeping.regressors)

        # fMRI momchil: save state only after successfully completing all levels given
        # it is easier if we match the granularity at which we load/save curriculum, in case of errors during replay
        # e.g. if we replay each block as one set of levels, and if some part of replay fails, we want to restart the whole block,
        # but we won't be able to if curriculum states were being saved along the way; we have to start from the state as it was at the beginning
        #if self.record_fMRIRegressors:
        then = time.time()
        self.agent.bookkeeping.saveCurriculumState(self.agent, {}, self.record_fMRIRegressors)
        print 'saving curriculum state took', (time.time() - then)

        if make_movie:
            if self.record_fMRIRegressors:
                self.makeMovie(play_movie=play_movie, regressors=self.agent.bookkeeping.regressors)
            else:
                self.makeMovie(play_movie=play_movie)

        endtime = time.time()
        print "Game took {} seconds".format(endtime-starttime)

        if self.record_fMRIRegressors:
            return curriculumRegressors
        else:
            return curriculumResults

    def playEpisode(self, gameObject, win=False, max_steps=None):

        print 'playEpisode checkpoint 0'
        ## Initialize external environment
        self.initializeEnvironment()
        print 'playEpisode checkpoint 1'
        self.agent.environment = self.environment
        self.agent.make_movie = self.make_movie
        self.agent.theory = self.theory
        self.agent.theory_playback = self.theory_playback
        self.agent.theory_playback_index = 0
        print 'playEpisode checkpoint 2'
        
        print "Playing level {}".format(self.n_level + 1)

        if self.produce_printout:
            print ""
            print self.environment.show(color='blue')

        ended, win = self.environment._isDone()
        
        quitting = False
        self.agent.quitting = False # TODO what other stuff do we need to do from __init__() Agent?
        episodeSteps = 0
        env_results = {'reward': 0, 'ended': False, 'win': False}  # SARS tuples, for learning
        ## Main episode loop
        while not quitting:

            # momchil: rendering, for DQN; from core.py
            if isinstance(self.agent, DQNAgent):
                pygame.time.Clock().tick()
                from ontology import LIGHTGRAY
                self.environment._game.screen.fill(LIGHTGRAY)
                self.environment._game._fMRI_drawAll()

            ### ENVIRONMENT ###
            if self.agent.memory.totalGameSteps+episodeSteps > MAX_STEPS and not self.record_fMRIRegressors:
                score = self.environment.getScore()
                print '                  MAX_STEPS ', self.agent.memory.totalGameSteps+episodeSteps, MAX_STEPS
                return gameObject, win, score, episodeSteps, self.agent.forfeit_level

            action, quitting = self.agent.step(None, env_results)
            #print('============================== step ' , episodeSteps, ' agent action, quitting ', action, quitting)


            ### TODO: environment step should overload rle and produce a blue printout.
            if self.record_fMRIRegressors:
                # fMRI replay
                # notice that the _game "knows" it's replaying (from initializeEnvironment), so it handles stuff inside
                # TODO maybe be more explicit here about replay vs play
                # pass regressors for optional visualization
                env_results = self.environment.step(action, regressors=self.agent.bookkeeping.regressors)
                if self.environment._game.playback_index == len(self.environment._game.playback_states):
                    # interrupt episode if you run out of states to replay TODO momchil better alternative?
                    print '                   no more states to replay'
                    if isinstance(self.agent, DQNAgent) and not quitting:
                        # we need to do one extra step for the DQN on timeouts TODO better -- _isDone, ended, quitting, _game.ended
                        _, _ = self.agent.step(None, env_results)
                    break
            else:
                env_results = self.environment.step(action)

            if self.produce_printout:
                print ""
                print actionDict[action]
                print self.environment.show(color='blue')
            episodeSteps += 1

            ended, win = self.environment._isDone()

            if max_steps and episodeSteps >= max_steps:
                # momchil: for simulating fMRI subjects who have a limit per level
                print '                  max steps', episodeSteps, max_steps
                break

        score = self.environment.getScore()

        if win:
            display('win')
        else:
            display('loss')

        # momchil: rendering for DQN
        if isinstance(self.agent, DQNAgent):
            pygame.display.quit()
            pygame.quit()
        return gameObject, win, score, self.agent.memory.episodeSteps, self.agent.forfeit_level, episodeSteps, ended



def display(message):
    if message=='Quitting':
        output =          "Quitting.                                                       "
        print colored('________________________________________________________________', 'white', 'on_red')
        print colored(output, 'white', 'on_red')
        print colored('________________________________________________________________', 'white', 'on_red')
    if message=='win':
        output =          "ended episode. Win=True                                         "
        print colored('________________________________________________________________', 'white', 'on_green')

        print colored(output, 'white', 'on_green')
        print colored('________________________________________________________________', 'white', 'on_green')

    if message=='loss':
        output =          "ended episode. Win=False                                        "
        print colored('________________________________________________________________', 'white', 'on_red')
        print colored(output, 'white', 'on_red')
        print colored('________________________________________________________________', 'white', 'on_red')
