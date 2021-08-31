# random agent
# TODO ideally, there should be an abstract agent class; in practice, it is easiest to just inherit from EMPA

# TODO copy pasted from https://github.com/ACampero/RC_RL and then adapted (necessary because of small differences)

import os
import subprocess
import shutil
import numpy as np
import random
import time
import copy
from collections import defaultdict
from core import colorDict, VGDLParser, sys, fMRI_screensize
from datetime import datetime
from math import log
from pygame import K_LEFT, K_UP, K_RIGHT, K_DOWN, K_SPACE
from termcolor import colored
from util import *
from ontology import *
from hyperparameters import hyperparameter_sets, metacontroller_sets
from agent_utils import translate_events, findNearestSprite, getSpritesByColor
from theory_template import TimeStep, Theory, Game, writeTheoryToTxt, generateSymbolDict, getPosterior
from theory_template import TimeoutRule, SpriteCounterRule, MultiSpriteCounterRule
from metacontroller import Metacontroller
from dynamic_type_inference import dynamicTypeDistribution_VGDL1, getKL
import WBP
from rlenvironmentnonstatic import createRLInputGame, createRLInputGameFromStrings, defInputGame, createMindEnv
from bookkeeping import Bookkeeping
from pprint import pprint
from EMPA import Agent, actionDict, availableActions, AvatarTypes
from vgdl.hyperparameters import hyperparameter_sets

class RandomAgent(Agent):
    def __init__(self, gameFilename, task_ID):
        # initialize with default parameters 
        super(RandomAgent, self).__init__('full', gameFilename, hyperparameter_sets=hyperparameter_sets, hyperparameter_index='short-term', 
            metacontroller_index=0, IW_k=1, extra_atom_allowed=True, task_ID=task_ID, agent_name='Random')

    def step(self, action, env_results=None):
        ended, win = self.environment._isDone()

        # bookkeeping
        if self.environment.getTime() == 0:
            self.bookkeeping.statesEncountered = []
        if self.make_movie or self.record_video_info:
            state = self.environment.getFullState(as_string=True)
            self.bookkeeping.statesEncountered.append(state)

        action = random.choice(availableActions)
        return action, ended
