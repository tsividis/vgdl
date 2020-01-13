from bookkeeping import Bookkeeping
from rlenvironmentnonstatic import createRLInputGame, createRLInputGameFromStrings, defInputGame, createMindEnv
from termcolor import colored
from pygame import K_LEFT, K_UP, K_RIGHT, K_DOWN, K_SPACE
import cPickle, cloudpickle
from datetime import datetime
import os, subprocess, shutil
import time
from IPython import embed

"""
Environment class for running VGDL experiments
"""


MAX_STEPS = 10000
actionDict = {K_SPACE: 'space', K_UP: 'up', K_DOWN: 'down', K_LEFT: 'left', K_RIGHT: 'right', 0:'none', None: 'none'}

class Environment:
    def __init__(self, gameFilename, agent, task_ID, produce_printout=False, movieName=None):
        self.gameFilename = gameFilename
        self.gameString = None
        self.levelString = None
        self.display_text = False
        self.display_states = False
        self.record_states = True
        self.record_video_info = True
        self.write_video_info = True
        self.saveMidEpisode = False
        self.filename = None
        self.timestamp = False
        self.task_ID = task_ID
        self.loaded_n_level = 0
        self.produce_printout = produce_printout
        self.movieName = movieName
        self.agent = agent

        ## used for time-stamping data related to this particular run of the model.
        timestamp = datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d__%H_%M__')+self.task_ID
        
        self.timestamp = timestamp

        if self.record_states:
            # dirname = "results/{}/{}/".format(self.param_ID, self.gameFilename) # old data location
            # print "in main_agent"
            # print os.getcwd()
            dirname_for_results = "../data/demo_data_files/EMPA/local/results/{}/{}/".format(agent.param_ID, self.gameFilename)
            filename = "{}{}_{}".format(dirname_for_results, self.gameFilename, self.timestamp)
            self.filename = filename
            if not os.path.exists(dirname_for_results):
                try:
                    # print "path didn't exist; making", dirname
                    os.makedirs(dirname_for_results)
                except:
                    print "failed  to make dir {} in main_agent.py".format(dirname_for_results)
        if self.write_video_info:
            self.dirname_for_video = "raw_video_info/{}/{}/".format(agent.param_ID, self.gameFilename)
            if not os.path.exists(self.dirname_for_video):
                os.makedirs(self.dirname_for_video)

    # ---------------------------------------------------------------------
    #     Simulator initialization functions
    # ---------------------------------------------------------------------
    def initializeEnvironment(self):
        ## Initialize game environment

        if self.display_text:
            print "initializing RLE"

        if self.gameString==None or self.levelString==None:
            self.gameString, self.levelString = defInputGame(self.gameFilename, randomize=False)
        self.rleCreateFunc = lambda: createRLInputGameFromStrings(self.gameString, self.levelString)
        self.rle = self.rleCreateFunc()
        return

    def initializeRLEFromGame(self):
        ## Part of a method for faster state copying, used in planner, etc.
        gameString, levelString = self.gameString, self.levelString
        if gameString == None or levelString == None:
            gameString, levelString = defInputGame(self.gameFilename, randomize=False)
        rleCreateFunc = lambda: createRLInputGameFromStrings(gameString, levelString)
        rle = rleCreateFunc()
        return rle


    def makeHeatmap(self, statesEncountered, filename):
        from vgdl.plotting import featurePlot
        import matplotlib.pyplot as plt
        from matplotlib.ticker import NullLocator
        import numpy as np

        states = [s['objects']['avatar'].keys()[0] for s in statesEncountered
                  if (not s['observe_state']) and s['objects']['avatar'].keys()]
        width, height = self.rle.width, self.rle.height
        correction_factor = self.rle.screensize[0]/width
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
            persist_movie=True, make_images=True, make_movie=False, movie_dir="videos/"+self.gameFilename, gameName = game_name_to_print_to_video, parameter_string=params_to_print_to_video, padding=10)

    def makeMovie(self, play_movie=False):

        VGDLParser.playGame(self.gameString, self.levelString, self.agent.bookkeeping.statesEncountered, \
            persist_movie=True, make_images=True, make_movie=True, movie_dir="videos/"+self.gameFilename, padding=10)
 
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

        return

    def playCurriculum(self, heatmap=False, level_game_pairs=None, make_movie=False, play_movie=False):
        """ Plays a game level until it wins, then moves to the next one until
        completion. """
        starttime = time.time()
        if not level_game_pairs:
            level_game_pairs = importlib.import_module(self.gameFilename).level_game_pairs
        episodes = []
        allEffectsEncountered = []

        self.make_movie = make_movie
        if self.make_movie:
            if 'images' in os.listdir('.') and 'tmp' in os.listdir('images') and self.gameFilename in os.listdir('images/tmp'):
                shutil.rmtree("images/tmp/"+self.gameFilename)
            os.makedirs("images/tmp/"+self.gameFilename)

        loaded_n_level=0
        curriculumSaveFile = 'curriculum_'+self.gameFilename+'_'+self.agent.param_ID+'_'+self.task_ID
        loadedState = self.agent.bookkeeping.loadCurriculumState(curriculumSaveFile)
        if loadedState is not None:
            self.agent = loadedState['agent']
            loaded_n_level, within_level_iteration = loadedState['agent'].n_level, loadedState['agent'].within_level_iteration
            # print "loaded a game"
            # embed()
        j=0
        fullStateEpisodes, episodeCompactStates = {}, {}
        for n_level, level_game in enumerate(level_game_pairs):

            if n_level < loaded_n_level: ## if we have a saved state that corresponds to us having played this level, skip it.
                continue

            (self.gameString, self.levelString) = level_game
            self.agent.max_nodes = self.agent.starting_max_nodes
            self.agent.stored_max_nodes = self.agent.max_nodes
            win = False
            gameObject = None
            
            i=0
            if loadedState:
                i=loadedState['agent'].within_level_iteration
                episodeCompactStates = loadedState['episodeCompactStates']
            levelEffectsEncountered = []
            allStatesEncountered = []
            allCompactStates = []
            t1 = time.time()

            forfeit_level = False
            while not win and not forfeit_level:# and i<15:
                self.n_level = n_level
                self.agent.n_level = n_level
                self.within_level_iteration = i
                self.agent.within_level_iteration = i
                gameObject, win, score, steps, forfeit_level = self.playEpisode(gameObject, win)
                
                ## TODO: clean up below stuff, too.
                statesEncountered = self.agent.bookkeeping.statesEncountered
                compactStates = self.agent.bookkeeping.compactStates
                effectsEncountered = self.agent.bookkeeping.effectsEncountered

                self.agent.memory.totalGameSteps += steps
                allCompactStates.append(compactStates)
                episode_results = (n_level, steps, win, score, self.agent.total_planner_steps)
                episodes.append(episode_results)

                if self.make_movie:
                    # self.statesEncountered = statesEncountered
                    self.makeImages()
                
                if self.record_video_info:
                    allStatesEncountered.extend(statesEncountered)

                i += 1

                episodeCompactStates[n_level] = allCompactStates
                fullStateEpisodes[n_level] = allStatesEncountered

                # print "about to save state"
                # embed()
                self.agent.bookkeeping.saveCurriculumState(self.agent, episodeCompactStates)
                # print "saved state"
                # embed()
                ## will write all previous episodes to the file at the end of each episode.
                if self.record_states:
                    gameInfo = {'gameString':self.gameString, 'levelString':self.levelString, 'gameName':self.gameFilename}
                    episodeList = [v for k,v in sorted(episodeCompactStates.items())]

                    with open(self.filename, 'wb') as f:
                        cPickle.dump({'gameInfo':gameInfo,'modelParams':self.agent.param_ID, 'episodes':episodeList, 'time_elapsed':time.time()-starttime}, f)

                if win:
                    self.n_level += 1
                    self.agent.n_level += 1
                    self.within_level_iteration = 0
                    self.agent.within_level_iteration = 0
                    
                ## will write video data at the end of each episode
                if self.record_video_info:
                    fullStateList = [v for k,v in sorted(fullStateEpisodes.items())]
                if self.write_video_info:
                    videofilename = "{}{}_{}".format(self.dirname_for_video, self.gameFilename, self.timestamp)
                    gameInfo = {'gameString':self.gameString, 'levelString':self.levelString, 'gameName':self.gameFilename}
                    with open(videofilename, 'wb') as f:
                        cPickle.dump({'gameInfo':gameInfo,'modelParams':self.agent.param_ID, 'episodes':fullStateList, 'time_elapsed':time.time()-starttime}, f)
                if self.agent.memory.totalGameSteps > MAX_STEPS:
                    if self.produce_printout:
                        print "reached max number of steps ({}>{}) in playCurriculum. Stopping experiment".format(self.agent.memory.totalGameSteps, MAX_STEPS)

                self.agent.bookkeeping.deleteEpisodeFile()

            if heatmap:
                self.makeHeatmap(allStatesEncountered, 'heatmap_{}_{}_level{}.pdf'.format(self.gameFilename, n_level, self.agent.param_ID))

        if make_movie:
            self.makeMovie(play_movie=play_movie)

        endtime = time.time()

    def playEpisode(self, gameObject, win=False):

        ## Initialize external environment
        self.initializeEnvironment()
        self.agent.rle = self.rle
        self.agent.make_movie = self.make_movie
        
        print "Playing level {}".format(self.n_level + 1)

        if self.produce_printout:
            print ""
            print self.rle.show(color='blue')

        ended, win = self.rle._isDone()
        
        quitting = False
        episodeSteps = 0
        ## Main episode loop
        while not quitting:

            ### ENVIRONMENT ###
            if self.agent.memory.totalGameSteps+episodeSteps > MAX_STEPS:
                score = self.rle.getScore()

                return gameObject, win, score, episodeSteps, self.agent.forfeit_level

            action, quitting = self.agent.step(None)


            ### TODO: environment step should overload rle and produce a blue printout.
            self.rle.step(action)
            if self.produce_printout:
                print ""
                print actionDict[action]
                print self.rle.show(color='blue')
            episodeSteps += 1

            ended, win = self.rle._isDone()
            

        score = self.rle.getScore()
            
        if win:
            display('win')
        else:
            display('loss')

        return gameObject, win, score, self.agent.memory.episodeSteps, self.agent.forfeit_level

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
