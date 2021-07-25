'''
Created on 2014 4 02

@author: Dylan Banarse (dylski@google.com)

Wrappers for games to interface them with artificial players.
This interface is a generic one for interfacing with RL agents.
'''
import numpy as np
from numpy import zeros
import pygame
from ontology import BASEDIRS
from core import VGDLSprite, pauseForDuration
from stateobsnonstatic import StateObsHandlerNonStatic
from collections import defaultdict
import argparse
from IPython import embed
import random
import math
import importlib
from colors import *
from util import factorize, assign_symbols_to_objects, quickcopy
from pygame.locals import K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT
from termcolor import colored
import time
import cPickle
import bisect


OBSERVATION_LOCAL = 'local'
OBSERVATION_GLOBAL = 'global'

class RLEnvironmentNonStatic( StateObsHandlerNonStatic):
    """ Wrapping a VGDL game with a generic interface suitable for reinforcement learning.
    """

    name = "VGDL-RLEnvironment"
    description = "RLEnvironment interface to VGDL."

    # If the visualization is enabled, all actions will be reflected on the screen.
    visualize = False
    # visualize = True
    # In that case, optionally wait a few milliseconds between actions?
    actionDelay = 0

    # Recording events (in slightly redundant format state-action-nextstate)
    recordingEnabled = False

    def __init__(self, gameDef, levelDef, observationType=OBSERVATION_GLOBAL, visualize=False, screensize=None, actionset=BASEDIRS, **kwargs):
        game = _createVGDLGame( gameDef, levelDef, screensize )
        StateObsHandlerNonStatic.__init__(self, game, **kwargs)
        self._actionset = actionset
        self.visualize = visualize
        self._initstate = self.getState()
        #
        # Total output dimensions are:
        #   #object_types * ( #neighbours + center )
        #
        # Note that _obstypes is an array of arrays for object types and their positions, e.g.
        # {
        #  'wall': [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0)],
        #  'goal': [(4, 1)]
        # }
        self.observationType=observationType
        if observationType == OBSERVATION_LOCAL:
            # Array of grid indices around the agent
            ns = self._stateNeighbors(self._initstate)
            self.outdim = [(len(ns) + 1) * len(self._obstypes), 1]
        else:
            self.nsAllCells = []
            self.outdim = [game.height, game.width]
            for y in range(0, game.height):
                for x in range(0, game.width):
                    self.nsAllCells.append( (x, y) )
        self._postInitReset()
        self._game.reset()
        self._game.all_objects = self._game.getObjects() # Save all objects, some which may be killed in game
        self._game.exceptedObjects = []
        self.makeSymbolDict()
        self._game.ignoreList = [] ## another way to mark objects that shouldn't be processed when doing induction (that is, collision objects)
        self._game.keystate = defaultdict(bool)
        self._game.metabolic_score = 0
        self.game_name = None
        self.width = self._game.width
        self.height = self._game.height
        self.screensize = self._game.screensize if screensize is None else screensize

    # Get definition of the observation data expected
    def observationSpec(self):
        return{ 'scheme':'Doubles', 'size':self.outdim }

    def getObjectsFromNumber(self, n):
        indices = factorize(self, n)
        allItems = ['avatar']+sorted(self._obstypes.keys())[::-1]
        return [allItems[i] for i in indices]

    def makeSymbolDict(self):
        inverseMapping = dict()
        colorMapping = dict()
        numbers = '0123456789'
        alnum = numbers + 'abcdefghijklmnopqrstuvwxyz'
        idx = 0
        OLD_GOAL = "oldGl"
        # embed()
        for s in self._obstypes.keys():
            colorMapping[s] = colorDict[str(self._game.sprite_constr[s][1]['color'])].lower()
            if not s == "goal":
                inverseMapping[s] = alnum[idx]
                idx+=1
            elif s=="goal":
                inverseMapping["goal"] = "G"
            else:
                inverseMapping[OLD_GOAL] = "O" # old goal

        inverseMapping['avatar'] = 'A'
        # if "goal" in self._obstypes:
        #     inverseMapping["goal"] = "G"

        self.symbolDict = inverseMapping
        self.colorMapping = colorMapping
        return

    def show_binary(self, thingWeShoot):
        """
        symbolDict = a dict mapping each sprite name to its symbol.
        If there's no sprite overlap, then returns a string. Else returns numpy array.
        """        
        mappedState = np.ones((self.outdim[1]*self.outdim[0]))
        kl_set = set(self._game.kill_list)
        for k, lst in self._game.sprite_groups.items():
            if k!= thingWeShoot:
                for sprite in lst:
                    if sprite not in kl_set:
                        y,x = sprite.rect.top/30, sprite.rect.left/30
                        try:
                            mappedState[x+self.outdim[1]*y] = 0
                        except:
                            pass
        return mappedState

    def show(self, indent=False, showArrays=False, binary=False, color='grey'):
        """
        symbolDict = a dict mapping each sprite name to its symbol.
        If there's no sprite overlap, then returns a string. Else returns numpy array.
        """
        ## faster version, but need to figure out how to display 

        # momchil
        print self._game.getFullStateColorized()['objects']['DARKBLUE']

        locs = defaultdict(lambda:[])
        if binary:
            mappedState = [[1 for x in range(self.outdim[1])] for y in range(self.outdim[0])]
        else:
            mappedState = [[' ' for x in range(self.outdim[1])] for y in range(self.outdim[0])]

        for lst in self._game.sprite_groups.values():
            for sprite in lst:
                if sprite not in self._game.kill_list:
                    y,x = sprite.rect.top/20, sprite.rect.left/20
                    locs[(y,x)].append(sprite.name)

        for k,v in locs.iteritems():
            if binary:
                symbol = 0
            else:
                if len(v)>1:
                    if 'avatar' in v:
                        symbol = 'X'
                    else:
                        symbol = '$'
                else:
                    if 'avatar' in v:
                        symbol = 'A'
                        # momchil
                        print 'loc avatar = ', k
                    else:
                        #symbol = assign_symbols_to_objects(self, v, self.symbolDict)
                        symbol = assign_symbols_to_objects(self, v, self.colorMapping) # momchil
                
                if symbol in ['A', 'X']:
                    symbol = colored(symbol, 'red')
                else:
                    if color != 'grey':
                        symbol = colored(symbol, color)

            try:
                mappedState[k[0]][k[1]] = symbol
            except:
                # print "mappedState problem in rlenvironmentNonStatic"
                ## if you define rules poorly, objects can go off screen, in which case they can't be assigned to an on-screen loc!
                continue

        if binary:
            gameString = []
            for mappedRow in mappedState:
                gameString.extend(mappedRow)
        else:
            gameString = ""
            for mappedRow in mappedState:
                gameString += reduce(lambda a,b: a+b, mappedRow) + "\n"
        return gameString

    # Get definition of the actions that are accepted
    def actionSpec(self):
        return{ 'scheme':'Integer', 'N':4 }

    # Reset the game between episodes.
    # Currently it is not recommended that this is called hundreds of times
    # cause things start to slow down exponentially (being looked at). The
    # recommended process is to re-create this class for each episode
    # (i.e. call the constructor for this class each episode) and call softReset
    # to get the starting observations.
    def reset(self):
        self._postInitReset(True)
        return self.step(None)

    # Reset after constructor
    # Like reset() but does not re-initialise state. This can be called after the
    # class has been constructed to get the starting observations
    def softReset(self):
        self._postInitReset(False)
        return self.step(None)

    # Reset game data and optionally the state
    def _postInitReset(self, performStateResetTesting=False):
        if self.visualize:
            self._game._initScreen(self.screensize, not self.visualize)

        # Calling self.setState(self._initstate) hundreds of times causes massive slowdown.
        if performStateResetTesting:
            self.setState(self._initstate)

        # if no avatar starting location is specified, the default one will be to place it randomly
        self._game.randomizeAvatar()

        self._game.kill_list = []
        if self.visualize:
            pygame.display.flip()
            self._game.frame_rate = 20
        if self.recordingEnabled:
            self._last_state = self.getState()
            self._allEvents = []

    def close():
        pass

    def getAvatars(self):
        return self._game.getAvatars()

    def find_projectile_if_new(self, projectile):
        potentialProjectiles = [s for s in self._game.sprite_groups[projectile] if self._game.sprite_groups[projectile] and s.lastmove==0]
        new_projectile = potentialProjectiles[0] if potentialProjectiles else None
        return new_projectile

    def getObjects(self):
        return self._game.getObjects()

    def getFullState(self, as_string=False, observe_state=False):
        return self._game.getFullState(as_string, observe_state)

    def getTime(self):
        return self._game.time

    def getScore(self):
        return self._game.score

    def getSpriteGroups(self):
        return self._game.sprite_groups

    def getResourceLimits(self):
        return self._game.resources_limits

    def getEffectListByColor(self):
        return self._game.effectListByColor

    def getEffectListByClass(self):
        return self._game.effectListByClass

    def getAliveSprites(self):
        if self._game.time == self._game.alive_sprites_update_time:
            return self._game.alive_sprites

        aliveSprites = []
        for spriteList in self.getSpriteGroups().values():
            for sprite in spriteList:
                if sprite not in self.getDeadSprites():
                    aliveSprites.append(sprite)

        self._game.alive_sprites = aliveSprites
        self._game.alive_sprites_update_time = self._game.time
        return aliveSprites

    def getAliveSpritesByName(self, spriteName):
        if spriteName in self.getSpriteGroups():
            return [sprite for sprite in self.getSpriteGroups()[spriteName] if sprite not in self.getDeadSprites()]
        else:
            return []

    def getDeadSprites(self):
        return self._game.kill_list

    def findObjectsInRLE(self, objName):
        try:
            objLocs = [self._rect2pos(sprite.rect) for sprite in self.getAliveSprites() if sprite.name==objName]
        except:
            return []
        return objLocs

    def findAvatarInRLE(self):
        avatar_loc = self._rect2pos(self._game.sprite_groups['avatar'][0].rect)
        return avatar_loc

    def fastcopy(self):
        ## Method for rapid copying of a simulator environment (the self)
        newRle = empty_copy(self)
        for k,v in self.__dict__.iteritems():
            ctype = str(type(getattr(self,k)))
            if 'defaultdict' in ctype or 'dict' in ctype:
                newRle.__dict__[k] = v.copy()
            elif 'list' in ctype:
                newRle.__dict__[k] = v[:]
            else:
                newRle.__dict__[k] = v

        newRle._game = empty_copy(self._game)
        ignoreKeys = ['spriteDistribution',
                      'object_token_spriteDistribution',
                      'spriteUpdateDict',
                      'movement_options',
                      'object_token_movement_options',
                      'uiud']
        sprite_attrs = ['ID', 'name','rect','x','y','orientation','stypes',
                        'lastrect','lastmove','stypes', 'lastdisplacement',
                        'speed','cooldown','direction','color','colorName']

        for k,v in self._game.__dict__.iteritems():
            if k in ignoreKeys: continue

            ctype = str(type(getattr(self._game,k)))

            if 'list' in ctype:
                if k != 'kill_list':
                    newRle._game.__dict__[k] = v[:]
                else:
                    newRle._game.kill_list = v[:]
            elif 'defaultdict' in ctype or 'dict' in ctype:
                if k != 'sprite_groups':
                    newRle._game.__dict__[k] = quickcopy(v)
                else:
                    new_sprite_groups = defaultdict(list)
                    for group_name, group in self._game.sprite_groups.iteritems():
                        for sprite in group:
                            if sprite.colorName == 'DARKGRAY':
                                new_sprite_groups[group_name].append(sprite)
                            else:
                                new_sprite = empty_copy(sprite)
                                try:
                                    for attr in sprite.__dict__.keys():
                                        if hasattr(sprite, attr):
                                            setattr(new_sprite, attr, getattr(sprite, attr))
                                    setattr(new_sprite, 'resources', quickcopy(sprite.__dict__['resources']))
                                except:
                                    embed()
                                new_sprite_groups[group_name].append(new_sprite)
                    newRle._game.sprite_groups = new_sprite_groups
            elif 'vgdl' in ctype:
                newRle._game.__dict__[k] = quickcopy(v)
            else:
                setattr(newRle._game, k, quickcopy(v))
        return newRle

    def _isDone(self, getTermination=False):
        # remember reward if the final state ends the game
        # self._game.terminations.sort(key=lambda x: 0 if (x.name=='SpriteCounter' and x.stype=='avatar' and x.win==  False) else 1 if x.name=='SpriteCounter' else 2)
        self._game.terminations.sort(key=lambda x: 0 if (x.name=='NoveltyTermination') else 1 if (x.name=='SpriteCounter' and x.stype=='avatar' and x.win==  False) else 2 if x.name=='SpriteCounter' else 3)
        for t in self._game.terminations:
            # Convention: the first criterion is for keyboard-interrupt termination
            # Breaking convention here
            ended, win = t.isDone(self._game)
            if ended:
                # if t.name=='NoveltyTermination':
                #     print t.s1, t.s2
                # elif t.name=='SpriteCounter':
                #     print t.stype
                # elif t.name=='MultiSpriteCounter':
                #     print t.stypes
                if getTermination:
                    return ended, win, t
                else:
                    return ended, win
        if getTermination:
            return False, False, None
        else:
            return False, False

    def _getSensors(self, state=None):

        # Get position and orientation
        if state is None:
            # state = { x, y, (rot?) }
            state = self.getState()
        if self.orientedAvatar:
            pos = (state[0], state[1])
        else:
            pos = state

        res = zeros(self.outdim[0]*self.outdim[1])

        # Get sensor data given current state (i.e. position)
        # and whether local state or whole game state is required
        if self.observationType == OBSERVATION_LOCAL:
            # A 1D array of ints, each representing presence or absense of
            # object type at local positions (e.g. Centre, Top, Left, Down,
            # Right) around avatar. First set of ints represent the first
            # object type in _obstypes, the next len(BASEDIRS) ints are for
            # the next object type, etc.
            # e.g. where object type A is present left and below,
            # and object type B is not visible, the observation would be:
            # 00110 00000
            ns = [pos] + self._stateNeighbors(state)
            for i, n in enumerate(ns):
                os = self._rawSensor(n)
                # slice os (e.g. [True,False]) into 'res' at position i and i+len(ns)
                # where len(ns) is number of sensor areas per sensor
                #print("i="+str(i)+" res="+str(res)+" res[..]="+str(res[i::len(ns)]))
                res[i::len(ns)] = os
        else:
            # OBSERVATION_GLOBAL
            # Returns 2D array of ints where bits set represent object types
            # present at that position. Bit 1 = Avatar. The other bits are set
            # in order that they are set in _obstypes (stateobs.py)
            # e.g. for avatar (1) in walled area (2) with goal at top right (4)
            # 222222
            # 200042
            # 200002
            # 210002
            # 222222
            ns = self.nsAllCells
            for i, n in enumerate(ns):
                # check if the avatar is here
                if n[0]==pos[0] and n[1]==pos[1]:
                    res[i] = 1
                os = self._rawSensor(n)
                for s in range(0,len(os)):
                    if os[s]==True:
                        res[i] = int(res[i]) | (2<<s)

        return res

    def _performAction(self, action=[], onlyavatar=False, regressors=None):

        """ Action is an index for the actionset.  """
        # take action and compute consequences
        # replace the method that reads multiple action keys with a fn that just
        # returns the currently desired action
        # if action == (0,0) or action == None:
        #     return

        # if action != (0,0) and self._avatar:
        #     self._avatar._readMultiActions = lambda *x: [action]

        # self._avatar._readMultiActions = lambda *x: [self._actionset[action]] # old
        possible_actions = [K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT]
        revActionDict = {'spacebar': K_SPACE, 'up': K_UP, 'down': K_DOWN, 'left': K_LEFT, 'right': K_RIGHT, 'none': 0}

        if self.visualize:
            pygame.time.Clock().tick(self._game.frame_rate)
            pauseForDuration(0.1) 
            self._game._fMRI_clearAll(self.visualize)


        # momchil fMRI replay shenanighans
        if self._game.playback_states:
            # off-policy learning from human action/state replay
            # 

            emptyKeyState = [0]*323 #keyState when no keys are pressed
            self._game.keystate = emptyKeyState # momchil: important to reset keystate

            # the full game state, for full state replay
            state = self._game.playback_states[self._game.playback_index]
            # just the action and related stuff for action replay
            keystate = self._game.playback_keystates[self._game.playback_index]

            # when this action was actually taken by subject; important for fMRI regressor onsets
            self._game.playback_ts = keystate['ts']

            if self._game.action_playback_only:
                # action replay -- choose action from replay & let EMPA do the updates / event handling
                #

                assert keystate['keyPressType'] == state['keyPressType']
                keyPressType = keystate['keyPressType']
                action = (0,0) # by default, nothing momchil TODO: action == 'space' case (see step())

                #print keyPressType, ' -------------------------------- keyPressType '

                # set the keystate from replay
                assert keystate['keystate'] == state['keystate']
                self._game.keystate = keystate['keystate']

                # set the new sprite IDs TODO do same for state replay
                # this makes sure newly created sprites have the right UUIDs
                # important for sprite induction I think (or maybe not; good to be
                # consistent tho)
                self._game.new_sprites_ID = state['new_sprites_ID']
                self._game.new_sprites_ID_idx = 0

                # sanity check that pressed key matches keystate (we need to return correct action I think)
                if keyPressType:
                    action = revActionDict[keyPressType] 
                    #self._game.keystate[action] = True # we used to set the keystate here; now we just sanity check
                    assert self._game.keystate[action], 'Replayed keystate differs from action based on keyPressType'


                # set RNG state to what it was exactly at the same spot in startGame
                x = keystate['RNG_state']
                x = (x[0], tuple(x[1]), x[2])
                random.setstate(x)

                # sprite update & event handling
                # momchil TODO dedupe w/ below potentially, also compare with startGame
                self._game.new_sprites = [] 

                # update sprites
                # same logic as in startGame
                assert not onlyavatar
                for s in list(self._game):
                    if s not in self._game.kill_list: 
                        s.update(self._game)

                events = self._game._eventHandling()

            else:
                # full state replay -- replay both states and actions
                #

                self._game.new_sprites = [] # momchil: taken care of? TODO no....
    
                try:
                    self._game.setFullState(self._game.playback_states[self._game.playback_index], cheap=False, default_colors=True)
                except:
                    print "agent playback is failing!"
                    embed()
    
                keyPressType = self._game.playback_states[self._game.playback_index]['keyPressType']
                action = (0,0) # by default, nothing momchil TODO: action == 'space' case (see step())
                if keyPressType:
                    action = revActionDict[keyPressType] 
                    assert self._game.keystate[action] 
   
                # load events from replay
                events = self._game.effectList
  

            # move to next state
            self._game.playback_index += 1

        else:

            # no replay (default case): agent is playing
            #
            if action in possible_actions:
                self._game.keystate[action] = True  #TODO momchil wtf is this

            self._game.new_sprites = [] 
            # update sprites
            if onlyavatar:
                if action != 0:
                    self._avatar.update(self._game)

            else:
                for s in self._game:
                    if action == 0 and s == self._avatar: # momchil is this necessary? differs from startGame logic
                            continue
                    if s not in self._game.kill_list: # shit -- the killed ones don't get updated here... TODO momchil 
                            s.update(self._game)

            events = self._game._eventHandling()



        if self.visualize:
            self._game.screen.blit(self._game.background, self._game.offset) # TODO momchil super inefficient
            self._game._drawAll()
            # TODO momchil somehow make sure only one RLE is visualizing at a time, b/c VGDLSprite is shared
            pygame.display.update(VGDLSprite.dirtyrects)
            VGDLSprite.dirtyrects = []

            # plotting fMRI regressors TODO momchil dedupe w/ startGame
            if regressors:
                self._game.fMRI_plotStuff(regressors)
                


        # fMRI sanity check code
        if self._game.playback_states and self._game.playback_index < len(self._game.playback_states): # last state might differ b/c we don't update in startGame but we do update here; TODO momchil maybe make consistent

            state = self._game.playback_states[self._game.playback_index - 1]
            #self._game.setFullState(state, cheap=False, default_colors=True) # for sanity checks
            s = self._game.getFullState()

            #print 'kill list: ', self._game.kill_list

            '''
            if len(self._game.effectList) != state['effectListLen']:
                print 'wrong effectListLen!'
                embed()
            print len(self._game.kill_list), ' {--------------} ',state['kill_listLen'] 
            # in startGame, we call _clearAll which empties kill_list and actually removes sprites from the game
            # here, we cannot clear kill_list b/c spriteInduction relies on it (I think) TODO 
            if len(self._game.kill_list) != state['kill_listLen']: 
                print 'wrong kill_listLen!'
                embed()
            if len(self._game.collision_eff) != state['collision_effLen']: 
                print 'wrong collision_eff!'
                embed()
            if len(self._game.sprite_groups) != state['sprite_groupsLen']: 
                print 'wrong sprite_groupsLen!'
                embed()
            if len(self._game.effectListByColor) != len(state['effectListByColor']): 
                print 'wrong effectListByColor!'
                embed()
            if len(self._game.effectListByClass) != len(state['effectListByClass']): 
                print 'wrong effectListByClass!'
                embed()
            # momchil: seems like we pre-define them in BasicGame based on desc/level so can't compare TODO confirm
            if len(self._game.new_sprites) != state['new_spritesLen']:
                print 'wrong new_spritesLen!'
                embed()
            # TODO momchil different; weird
            #if self._game.keystate != state['keystate']:
            #    print 'wrong keystate'
            #    embed()
            '''

            if s['list'] != state['list']:
                print 'incorrect sprite list!'
                embed()

            # state = replayed human state, s = current state from action replay
            for sname, sprites in state['objects'].iteritems():

                assert sname in s['objects'].keys(), 'sname not found'
                if len(state['objects'][sname]) != len(s['objects'][sname]):
                    embed()
                for pos, attrs in sprites.iteritems():

                    p = tuple(map(int, pos[1:-1].split(', ')))
                    if sname == 'avatar':
                        o = s['objects'][sname]
                        #print '============ avatar coords: ', o.keys()[0], '  action = ', action
                    
                    if str(p) not in s['objects'][sname].keys():
                        print 'pos not found -- could be b/c we used to restore the rect from x,y, which is wrong b/c sometimes they diverge -- see getFullState'
                        embed()

                    attrs_c = s['objects'][sname][str(p)] # current attrs

                    for attr, val in attrs.iteritems():
                        assert attr in attrs_c.keys(), 'attr not found'

                        # symbol b/c none here
                        # color & colorName b/c randomized there but not here
                        # colorName is set to the default for the game
                        # TODO check lastdisplacement and deathage

                        # (de)serialization & storage makes tuples into lists
                        if isinstance(attrs_c[attr], tuple):
                            val = tuple(val)
                        if attr == 'rect':
                            val['pos'] = tuple(val['pos'])
                            val['size'] = tuple(val['size'])

                        if val != attrs_c[attr] and attr not in ['lastdisplacement', 'deathage', 'symbol', 'colorName', 'color']:
                            print 'wrong attr value'
                            embed()
                            time.sleep(1000)


        # momchil: save event, destroy self.game, re-init self.game (.reset, etc) from saved state => make sure still works

        ## get events (e.g., (stepBack obj1ID, obj2ID))

        # self._gravepoints[(skey, self._rect2pos(s.rect))] = True


        ## Added 5/2, to correct for the fact that some gmaes don't have _gravepoints by default
        if not hasattr(self, '_gravepoints'):
            self._gravepoints = {}

        # ### BEGINNING OF CHANGES
        for skey in self._other_types:
            ss = self._game.sprite_groups[skey]
            self._obstypes[skey] = [self._sprite2state(sprite, oriented=False)
                                        for sprite in ss]

        ## Added 4/31
        ## Logic (I think) was to make sure everything that could exist was in gravepoints because
        ## getState (defined in stateobsnonstatic) uses it to populate getState, getSensors, etc.
        for k in self._game.sprite_groups:
            for sprite in self._game.sprite_groups[k]:
                if (k, self._rect2pos(sprite.rect)) not in self._gravepoints.keys():
                    self._gravepoints[(k, self._rect2pos(sprite.rect))] = True
        # print "after adding gravepoints"
        # embed()
        return events, action

    def step(self, action, return_obs=False, getTermination=False, getEffectList=False, regressors=None):
        if action == ('space'):
            self._game.keystate[32] = True
            action = (0,0)
        pre_step_score = self._game.score

        self._game.time+=1 # momchil: important to do it before updates in _performAction, consistent with StartGame (to make sure regressors & game times match up)
        #print 'time = ', self._game.time, '           game = ', self._game, '      self = ', self

        events, action = self._performAction(action, regressors=regressors)

        observation = self._getSensors() if return_obs else None
        if getTermination:
            (ended, won, termination) = self._isDone(getTermination=True)
        else:
            (ended, won) = self._isDone()
            termination = []
        
        self._game.ended, self._game.win = ended, won

        dScore = self._game.score - pre_step_score
        if ended:
            pcontinue = 0
            if won:
                reward = 1
            else:
                reward = -1
        else:
            pcontinue = 1
            ## this is where you need to give the reward for doing non-terminal actions, and then your agent can process this.
            reward = dScore
        for k in self._game.keystate:
            self._game.keystate[k] = False


        # momchil: TODO rm ?
        if self._game.playback_states and self._game.playback_index == len(self._game.playback_states):
            ended = True
            won = True
            self._game.ended = ended
            self._game.win = won
            print 'ENDED'
            #embed()

        return{'observation':observation, 'reward':reward, 'pcontinue':pcontinue, 'effectList':events, 'ended':ended, 'win':won, 'termination':termination}

    def check_that_avatar_is_alive(self):
        return len(self._game.sprite_groups['avatar']) > 0

def try_int(s):
    "Convert to integer if possible."
    try: return int(s)
    except: return s

def natsort_key(s):
    "Used internally to get a tuple by which s is sorted."
    import re
    return map(try_int, re.findall(r'(\d+|\D+)', s))

def natcmp(a, b):
    "Natural string comparison, case sensitive."
    return cmp(natsort_key(a), natsort_key(b))

def natcasecmp(a, b):
    "Natural string comparison, ignores case."
    return natcmp(a.lower(), b.lower())

def defInputGame(filename, randomize=False, index=None):
    game_file = importlib.import_module(filename)
    levels = [k for k in game_file.__dict__.keys() if 'level' in k]
    levels.sort(natcasecmp)
    # print levels
    if randomize:
        level = random.choice(levels)
        return (game_file.game, game_file.__dict__[level])
    elif index>=0:
        if index<len(levels):
            print index
            level = levels[index]
        else:
            level = random.choice(levels)
        return (game_file.game, game_file.__dict__[level])
    else:
        return (game_file.game, game_file.level)

def _createVGDLGame( gameSpec, levelSpec, fMRI_screensize=None):
    import uuid
    from vgdl.core import VGDLParser
    # parse, run and play.
    game = VGDLParser().parseGame(gameSpec)
    game.buildLevel(levelSpec, fMRI_screensize)
    game.uiud = uuid.uuid4()
    return game

# Test some of the observation and action specs
def testSpecs():
    game = _createVGDLGame( *defMaze() )
    rle = RLEnvironmentNonStatic( *defMaze() )
    if rle.actionSpec() != {'scheme': 'Integer', 'N': 4}:
        print "FAILED actionSpec"
        print rle.actionSpec()
    if rle.observationSpec() != {'scheme': 'Doubles', 'size': [10, 1]}:
        print "FAILED observationSpec"
        print rle.observationSpec()

# Verify that observation received matches target observation
def _verify( obs, targetObs ):
    if obs["pcontinue"] != targetObs["pcontinue"]:
        print "FAILED pcontinue"
        return False
    if obs["reward"] != targetObs["reward"]:
        print "FAILED reward"
        return False
    match = True
    i=0
    for ob in targetObs["observation"]:
        if float(obs["observation"][i]) != float(targetObs["observation"][i]):
            match = False
        i = i+1

    if match==False:
        print ""
        print "FAILED observation"
        print obs["observation"]
        print targetObs["observation"]
        print match
        return False
    return True

def createMindEnv(game, level, output=False, obsType=OBSERVATION_GLOBAL ):
    if output:
        print game
        print level
    return RLEnvironmentNonStatic( game, level, observationType=obsType )

def createRLInputGame(filename, obsType=OBSERVATION_GLOBAL):
    game_file = importlib.import_module(filename)
    return RLEnvironmentNonStatic(game_file.game, game_file.level, \
            observationType = obsType)

def createRLInputGameFromStrings(game, level, visualize=False, screensize=None):
    return RLEnvironmentNonStatic(game, level, \
            observationType = OBSERVATION_GLOBAL, visualize=visualize, screensize=screensize, fMRI_screensize=screensize)

def testMaze(numEpisodes, numJogOnSpot, verify, reuseGame, obsType):
    rle = createRLMaze( obsType )

    # uncomment following two lines to see the walk (causes internal warning)
    #rle.visualize = True
    for i in range(0,numEpisodes):

        if reuseGame:
            # Purely for testing: reuse the game and by calling _postInitReset(True).
            # This should be faster but self.setState(_initstate) in _postInitReset()
            # causes the game to slow down with hunreds of calls.
             rle._postInitReset(True)
        else:
            # Re-create the game.
            rle = createRLMaze( obsType )

        res = rle.step(0) #up
        if verify:
            _verify( res, {'pcontinue': 1, 'reward': 0, 'observation': [ 0.,  0.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.]} )
        res = rle.step(1) #left (there's a wall so expect no change in observations)
        if verify:
            _verify( res, {'pcontinue': 1, 'reward': 0, 'observation': [ 0.,  0.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.]} )
        res = rle.step(3) #right
        if verify:
            _verify( res, {'pcontinue': 1, 'reward': 0, 'observation': [ 0.,  0.,  0.,  1.,  0.,  0.,  0.,  0.,  0.,  0.]} )

        # Hop backwards and forwards
        for j in range (0,int(numJogOnSpot)):
            res = rle.step(1) #left
            if verify:
                _verify( res, {'pcontinue': 1, 'reward': 0, 'observation': [ 0.,  0.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.]} )
            res = rle.step(3) #right
            if verify:
                _verify( res, {'pcontinue': 1, 'reward': 0, 'observation': [ 0.,  0.,  0.,  1.,  0.,  0.,  0.,  0.,  0.,  0.]} )

        res = rle.step(3) #right
        if verify:
            _verify( res, {'pcontinue': 1, 'reward': 0, 'observation': [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.]} )
        res = rle.step(3) #right
        if verify:
            _verify( res, {'pcontinue': 1, 'reward': 0, 'observation': [ 0.,  0.,  0.,  0.,  1.,  0.,  1.,  0.,  0.,  0.]} )
        res = rle.step(0) #up
        if verify:
            _verify( res, {'pcontinue': 0, 'reward': 1, 'observation': [ 0.,  1.,  0.,  0.,  1.,  0.,  0.,  0.,  0.,  0.]} )

def defaultTest():
    print("testSpecs()")
    testSpecs()
    print("testMaze(1, 0, True, True, OBSERVATION_LOCAL)")
    testMaze(1, 0, True, True, OBSERVATION_LOCAL)
    print("testMaze(1, 0, True, False, OBSERVATION_LOCAL)")
    testMaze(1, 0, True, False, OBSERVATION_LOCAL)
    print("testMaze(2, 0, True, False, OBSERVATION_LOCAL)")
    testMaze(2, 0, True, False, OBSERVATION_LOCAL)
    print("testMaze(1, 2, True, False, OBSERVATION_LOCAL)")
    testMaze(1, 2, True, False, OBSERVATION_LOCAL)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--numEpisodes", default=1, help="Number of episodes to run",
                    type=int)
    parser.add_argument("--profile", help="profile a set of episode runs",
                    action="store_true")
    parser.add_argument("--reuse-game", help="EXPERIMENTAL: don't re-create game each episode, results in slow-down bug",
                    action="store_true")
    parser.add_argument("--jog-on-spot", type=int, default=0, help="half the extra number of steps to add")
    parser.add_argument("--test", help="run tests",
                    action="store_true")

    parser.add_argument("--observation-type", help="'local' for neighbors or 'global' for whole game area", default='local')
    parser.add_argument("--play-test", help="Interactively play the test maze", default=False, action='store_true')
    args = parser.parse_args()

    if args.profile:
        import cProfile
        command = 'testMaze('+str(args.numEpisodes)+','+str(args.jog_on_spot)+',False,'+str(args.reuse_game)+',"'+args.observation_type+'")'
        cProfile.run(command)
    elif args.play_test:
        playTestMaze()
    else:
        # defaultTest()
        # testMaze(args.numEpisodes, args.jog_on_spot, True, args.reuse_game, args.observation_type)
        # testMaze(1, 0, True, True, OBSERVATION_GLOBAL)
        testSimpleGame_missile(1, 0, True, True, OBSERVATION_GLOBAL)
        # testSimpleGame1(1, 0, True, True, OBSERVATION_GLOBAL) # to uncomment
        # testFrogs(1, 0, True, True, OBSERVATION_GLOBAL)
        # testAliens(1, 0, True, True, OBSERVATION_GLOBAL)


def empty_copy(obj):
    class Empty(obj.__class__):
        def __init__(self): pass
    newcopy = Empty()
    newcopy.__class__ = obj.__class__
    return newcopy
