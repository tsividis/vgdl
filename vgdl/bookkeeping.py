import cPickle, cloudpickle
from datetime import datetime
import os, subprocess, shutil
import time
from IPython import embed


"""
Class for supporting interrupted runs on cluster. Saves where we are in the curriculum as well as the agent state and allows for re-setting a run to a recent game/agent state.
"""

class Bookkeeping:
    def __init__(self, saveMidEpisode, task_ID, param_ID, gameFilename):
        self.saveMidEpisode = saveMidEpisode
        self.task_ID = task_ID
        self.param_ID = param_ID
        self.gameFilename = gameFilename
        self.episodeSaveFile = None
        self.curriculumDir = 'savedCurricula'
        self.curriculumSaveFile = 'curriculum_'+self.gameFilename+'_'+self.param_ID+'_'+self.task_ID
        self.effectsEncountered = []
        self.statesEncountered = []
        self.compactStates = []

        if self.curriculumDir not in os.listdir('.'):
            os.makedirs(self.curriculumDir)

    def saveCurriculumState(self, agent, episodeCompactStates, is_fMRI):
        if 'pedro' in os.getcwd():
            return

        #momchil: don't save these b/c they take too much space, and
        # we don't really need them cross-games / levels, b/c we do those in separate batches
        # JK WE DO! TODO discuss w / team -- people surely remember stuff that happened in last play, but probably not stuff across blocks...
        #if is_fMRI:
        #    finalTimeStepList = agent.finalTimeStepList
        #    finalEventList = agent.finalEventList
        #    agent.finalTimeStepList = []
        #    agent.finalEventList = []

        filename = self.curriculumDir+'/'+self.curriculumSaveFile
        savedState = {'agent':agent,
                      'episodeCompactStates': episodeCompactStates}
        with open(filename, 'wb') as f:
            cloudpickle.dump(savedState, f)

        #if is_fMRI:
        #    agent.finalTimeStepList = finalTimeStepList
        #    agent.finalEventList = finalEventList

    def loadCurriculumState(self, filename):
        ## For runs on cluster that may get interrupted -- if you find a saved state for this particular agent, load that and run from there.
        print "Curriculum directory:", self.curriculumDir
        print "Filename:", filename
        if filename in os.listdir(self.curriculumDir):
            path = self.curriculumDir+'/'+filename
            try:
                then = time.time()
                print "found saved curriculum state: ", (os.stat(path).st_size / 1024.0 / 1024.0 / 1024.0), ' GB'
                loadedState = self.loadState(path)
                print "loaded curriculum state; took ", (time.time() - then), "s"
                return loadedState
            except:
                os.remove(path)
                print "failed to load curriculum state. deleting corrupted file and starting from scratch"
                return None

    def saveEpisodeState(self, agent):
        if not self.saveMidEpisode:
            return

        # if 'pedro' in os.getcwd():
            # return

        filename = self.episodeSaveFile

        print "starting to save episode state"
        savedState = {'agent':agent,
                      'effectsEncountered': self.effectsEncountered,
                      'statesEncountered': self.statesEncountered,
                      'compactStates': self.compactStates,
                      'annealing': agent.annealing
                      }
        filepath = 'savedCurricula/'+filename
        with open(filepath, 'wb') as f:
            cloudpickle.dump(savedState, f)
        print "done saving state"

    def loadState(self, filename):
        with open(filename, 'r') as f:
            loadedState = cloudpickle.load(f)
        # f.close()
        return loadedState

    def saveState(self):
        filename = 'saved_state'
        with open(filename, 'wb') as f:
            cloudpickle.dump(self, f)
        return

    def deleteEpisodeFile(self):
        if self.saveMidEpisode:
            ## if the episode ends, delete the mid-episode file we were saving.
            self.episodeSaveFile = 'episode_'+self.gameFilename+'_'+self.task_ID
            os.remove(self.curriculumDir+'/'+self.episodeSaveFile)
            print "finished an episode; removing episodeSaveFile"
