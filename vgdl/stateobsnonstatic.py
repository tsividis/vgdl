'''
Created on 2013 3 13

@author: Tom Schaul (schaul@gmail.com)

Managing states and observations, for different types of games
'''

import pygame
from pybrain.utilities import setAllArgs
from ontology import RotatingAvatar, BASEDIRS, GridPhysics, ShootAvatar, kill_effects, getSpritesByColor
from core import VGDLSprite, Avatar
from tools import listRotate
from IPython import embed
from util import *
import numpy as np
from collections import defaultdict
import uuid
from colors import *




class StateObsHandlerNonStatic(object):
    """ Managing different types of state representations,
    and of observations.

    A state is always composed of a tuple, with the avatar position (x,y) in the first places.
    If the avatar orientation matters, the orientation is the third element of the tuple.
    """

    # is the avatar having an orientation or not?
    orientedAvatar = False

    # is the avatar a single persistent sprite, or can it be transformed?
    uniqueAvatar = True

    # can the avatar die?
    mortalAvatar = False

    # can other sprites die?
    mortalOther = False

    # can other sprites move
    staticOther = True

    def __init__(self, game, **kwargs):
        setAllArgs(self, kwargs)
        self._game = game
        self._avatar_types = []
        self._abs_avatar_types = []
        self._other_types = []
        self._mortal_types = []
        # print "beginning of stateObsHandler"
        # embed()
        for skey in sorted(game.sprite_constr):
            sclass, _, stypes = game.sprite_constr[skey]
            if issubclass(sclass, Avatar):
                self._abs_avatar_types += stypes[:-1]
                self._avatar_types += [stypes[-1]]
                if issubclass(sclass, RotatingAvatar) or issubclass(sclass, ShootAvatar):
                    self.orientedAvatar = True
            if skey not in game.sprite_groups:
                continue

            ss = game.sprite_groups[skey]
            if len(ss) == 0:
                self._other_types += [skey] ## Added 4/31/17
                continue
            if isinstance(ss[0], Avatar):
                assert issubclass(ss[0].physicstype, GridPhysics), \
                        'Not supported: Game must have grid physics, has %s'\
                        % (self._avatar.physicstype.__name__)
            else:
                self._other_types += [skey]
                if not ss[0].is_static:
                    self.staticOther = False
        # assert self.staticOther, "not yet supported: all non-avatar sprites must be static. "
        # print "after initial loop"
        # embed()
        self._avatar_types = sorted(set(self._avatar_types).difference(self._abs_avatar_types))
        self.uniqueAvatar = (len(self._avatar_types) == 1)
        #assert self.uniqueAvatar, 'not yet supported: can only have one avatar class'

        # determine mortality
        for skey, _, effect, _ in game.collision_eff:
            if effect in kill_effects:
                if skey in self._avatar_types+self._abs_avatar_types:
                    self.mortalAvatar = True
                if skey in self._other_types:
                    self.mortalOther = True
                    self._mortal_types += [skey]

        # print "in stateObsHandler"
        # embed()

        # retain observable features, and their colors
        self._obstypes = {}
        self._obscols = {}

        ## Added 4/31/17
        for skey in self._other_types:
            ss = game.sprite_groups[skey]
            if len(ss)>0:
                self._obstypes[skey] = [self._sprite2state(sprite, oriented=False) for sprite in ss]
                self._obscols[skey] = ss[0].color
            else:
                if type(skey)==str:
                    self._obstypes[skey] = []
        # for skey in self._other_types:
        #     ss = game.sprite_groups[skey]
        #     self._obstypes[skey] = [self._sprite2state(sprite, oriented=False) for sprite in ss]
        #     self._obscols[skey] = ss[0].color

        if self.mortalOther:
            self._gravepoints = {}
            for skey in self._mortal_types:
                for s in self._game.sprite_groups[skey]:
                    self._gravepoints[(skey, self._rect2pos(s.rect))] = True

    @property
    def _avatar(self):
        ss = self._game.getAvatars()
        #assert len(ss) <= 1, 'Not supported: Only a single avatar can be used, found %s' % ss
        if len(ss) == 0:
           return None
        return ss[0]

    def setState(self, state):
        pos = (state[0]*self._game.block_size, state[1]*self._game.block_size)

        # no avatar?
        if self._avatar is None:
            assert self.mortalAvatar
            if self.uniqueAvatar:
                atype = self._avatar_types[0]
            else:
                atype = state[-1]
            self._game._createSprite([atype], pos)

        # bad avatar?
        if not self.uniqueAvatar:
            atype = state[-1]
            if self._avatar.name != atype:
                self._game.kill_list.append(self._avatar)
                self._game._createSprite([atype], pos)

        if not self.uniqueAvatar:
            state = state[:-1]
        if self.mortalOther:
            self._setPresences(state[-1])
            state = state[:-1]
        self._setSpriteState(self._avatar, state)
        self._avatar.lastrect = self._avatar.rect
        self._avatar.lastmove = 0

    def getState(self):
        if self._avatar is None:
            return (-1,-1, 'dead')
        if self.mortalOther:
            if self.uniqueAvatar:
                return tuple(list(self._sprite2state(self._avatar)) + [self._getPresences()])
            else:
                return tuple(list(self._sprite2state(self._avatar))
                             + [self._getPresences()] + [self._avatar.name])
        else:
            if self.uniqueAvatar:
                return self._sprite2state(self._avatar)
            else:
                return tuple(list(self._sprite2state(self._avatar))
                             + [self._avatar.name])

    def _getPresences(self):
        """ Binary vector of which non-avatar sprites are present. """
        res = []
        for skey, pos in sorted(self._gravepoints):
            if pos in [self._rect2pos(s.rect) for s in self._game.sprite_groups[skey]
                       if s not in self._game.kill_list]:
                res.append(1)
            else:
                res.append(0)
        return tuple(res)

    def _setPresences(self, p):
        for i, (skey, pos) in enumerate(sorted(self._gravepoints)):
            target = p[i] != 0
            matches = [s for s in self._game.sprite_groups[skey] if self._rect2pos(s.rect)==pos]
            current = (not len(matches) == 0 and matches[0] not in self._game.kill_list)
            if current == target:
                continue
            elif current:
                #print 'die', skey, pos, matches
                self._game.kill_list.append(matches[0])
            elif target:
                #print 'live', skey, pos, matches
                pos = (pos[0]*self._game.block_size, pos[1]*self._game.block_size)
                self._game._createSprite([skey], pos)


    def _rawSensor(self, state):
        # modified to handle killed sprites
        kill_dict = defaultdict(list)
        for sprite in self._game.kill_list:
            kill_dict[sprite.name].append(self._sprite2state(sprite, oriented=False))
        return [(state in ostates and state not in kill_dict[name])
            for name, ostates in sorted(self._obstypes.items())[::-1]]

        # sprite_sensor = []
        # grid_kill_list = [(sprite.name, self._sprite2state(sprite, oriented=False)) for sprite in self._game.kill_list]
        # for o_type, ostates in sorted(self._obstypes.items())[::-1]:
        #     o_type_and_states = [(o_type, s) for s in ostates]
        #     alive_ostates = [s[1] for s in o_type_and_states if not s in grid_kill_list]
        #     sprite_sensor.append((state in alive_ostates))
        #
        # if out1 != sprite_sensor:
        #     embed()

        return sprite_sensor

        # return [(state in ostates) for _, ostates in sorted(self._obstypes.items())[::-1]]

    def _sprite2state(self, s, oriented=None):
        pos = self._rect2pos(s.rect)
        if oriented is None and self.orientedAvatar:
            return (pos[0], pos[1], s.orientation)
        else:
            return pos

    def _rect2pos(self, r):
        # return (round(float(r.left) / self._game.block_size), round(float(r.top) / self._game.block_size))
        return float(r.left) / self._game.block_size, float(r.top) / self._game.block_size

    def _rect2posFlipCoords(self, r):
        x, y = self._rect2pos(r)
        return (y, x)

    def _pos2rect(self, pos):
        return (pos[0]*self._game.block_size, pos[1]*self._game.block_size)

    def _setRectPos(self, s, pos):
        s.rect = pygame.Rect((pos[0] * self._game.block_size,
                              pos[1] * self._game.block_size),
                             (self._game.block_size, self._game.block_size))

    def _setSpriteState(self, s, state):
        if self.orientedAvatar:
            s.orientation = state[2]
        self._setRectPos(s, (state[0], state[1]))

    def _stateNeighbors(self, state):
        """ Can be different in subclasses...

        By default: current position and four neighbors. """
        pos = (state[0], state[1])
        ns = [(a[0] + pos[0], a[1] + pos[1]) for a in BASEDIRS]
        if self.orientedAvatar:
            # subjective perspective, so we rotate the view according to the current orientation
            ns = listRotate(ns, BASEDIRS.index(state[2]))
            return ns
        else:
            return ns


class TrackedSprite(object):
    """ Data structure for storing info about tracked sprites, given by perception module. """

    def __eq__(self, other):
        """Overrides the default implementation
            so that copies of an instance are considered equal"""
        if isinstance(self, other.__class__):
            return self.ID == other.ID
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.ID)

    def __init__(self, pos, color=None, size=(10,10)):
        self.name = None
        self.color = color
        self.rect = pygame.Rect(pos, size)
        self.lastrect = pygame.Rect(pos, size)
        # self.x = pos[0]
        # self.y = pos[1]
        self.orientation = (0,0)
        self.speed = None
        self.ID = uuid.uuid1()
        self.color = color or self.color or PURPLE
        if self.color == ENDOFSCREEN:
            self.ID = 'ENDOFSCREEN'
        if str(self.color) in colorDict.keys():
            self.colorName = colorDict[str(self.color)]
        else:
            self.colorName = str(self.color)
        self.lastmove = 0
        self.inventory = dict() # color: (num_things, max_capacity) # pulled from progress bars on avatar
        self.lastinventory = dict()
        self.name = self.colorName
    
    def __repr__(self):
        return str(self.name)+" at (%s,%s)"%(self.rect.left, self.rect.top)

    def inventoryDiff(self):
        diff = dict()
        for key in self.inventory:
            if not key in self.lastinventory:
                diff[key] = self.inventory[key][0]
            else:
                diff[key] = self.inventory[key][0] - self.lastinventory[key][0]
        for key in set(self.lastinventory.keys()) - set(self.inventory.keys()):
            diff[key] = -self.lastinventory[key][0]
        return diff

def buildTracker(rle):
    gameObject = rle._game
    memory = dict()
    trackedObjects = defaultdict(list) # color: list_of_sprites # not sure why list arg, just copied from elsewhere
    memory['isGrid'] = True
    memory['score'] = rle._game.score
    memory['lastscore'] = rle._game.score
    for group in gameObject.sprite_groups.keys():
        if gameObject.sprite_groups[group] and gameObject.sprite_groups[group][0].colorName not in trackedObjects:
            trackedObjects[gameObject.sprite_groups[group][0].colorName] = []
        for sprite in gameObject.sprite_groups[group]:
            trackedObjects[sprite.colorName].append(copySpriteStingy(sprite))
    memory['trackedObjects'] = trackedObjects
    memory['kill_list'] = []
    return memory

def copySpriteStingy(sprite):
    # copies all the data from sprite that we could reasonably get from
    #   a real CV system into a new sprite, then returns it
    newSprite = TrackedSprite([sprite.rect.left, sprite.rect.top], color=sprite.color, size=(sprite.rect.width, sprite.rect.height)) # automatically does colorName
    newSprite.ID = sprite.ID # not sure if we need this
    newSprite.name = newSprite.colorName
    newSprite.orientation = sprite.orientation # just a tuple, no need to ccopy
    newSprite.lastmove = sprite.lastmove
    newSprite.rect = pygame.Rect(sprite.rect.left, sprite.rect.top, sprite.rect.width, sprite.rect.height)
    newSprite.lastrect = pygame.Rect(sprite.lastrect.left, sprite.lastrect.top, sprite.lastrect.width, sprite.lastrect.height)

    if type(sprite) == TrackedSprite:
        newSprite.speed = sprite.speed
        newSprite.inventory = dict(sprite.inventory) if sprite.inventory else dict()
        newSprite.lastinventory = dict(sprite.lastinventory)

    return newSprite

def processFrame(memory, gameObject):
    # eventual goal is to process the frame, not the gameObject...
    # creates a COPY of memory and returns updated copy
    newMemory = dict()
    newTrackedObjects = defaultdict(list)
    spriteIDDict = {sprite.ID: sprite for lst in memory['trackedObjects'].values() for sprite in lst}

    # print "in processFrame"
    # embed()
    newMemory['kill_list'] = [copySpriteStingy(s) for s in gameObject.kill_list]
    newMemory['isGrid'] = memory['isGrid']
    newMemory['lastscore'] = memory['score']
    newMemory['score'] = gameObject.score
    for key in gameObject.sprite_groups.keys():
        if gameObject.sprite_groups[key]:
            for sprite in gameObject.sprite_groups[key]:
                if sprite in gameObject.kill_list:
                    continue
                if not sprite.colorName in newTrackedObjects:
                    newTrackedObjects[sprite.colorName] = []
                if sprite.ID in spriteIDDict:
                    # not a new object
                    newSprite = copySpriteStingy(spriteIDDict[sprite.ID])
                    newSprite.lastmove += 1
                    if sprite.rect.left != newSprite.rect.left or sprite.rect.top != newSprite.rect.top:
                        # first check if this is actually continuous (default assumes grid)
                        # TODO: this way of checking whether it's a grid or not fails for projectiles and interesting bounce-forwards (like chains)
                        if memory['isGrid'] and False:# sprite.rect.left  != newSprite.rect.left  and sprite.rect.top != newSprite.rect.top and abs(sprite.rect.left  - newSprite.rect.left ) != abs(sprite.rect.top - newSprite.rect.top):
                            newMemory['isGrid'] = False
                        # it moved since last sighting!
                        if newMemory['isGrid']:
                            newSprite.speed = max(abs(sprite.rect.left - newSprite.rect.left), abs(sprite.rect.top - newSprite.rect.top)) * 1.0 / sprite.rect.width # TODO: don't depend on width
                            newSprite.orientation = (np.sign(sprite.rect.left - newSprite.rect.left), np.sign(sprite.rect.top - newSprite.rect.top))
                        else:
                            newSprite.speed = euclideanDist([sprite.rect.left, sprite.rect.top], [newSprite.rect.left, newSprite.rect.top])
                            newSprite.orientation = normalizeVec([sprite.rect.left - newSprite.rect.left, sprite.rect.top - newSprite.rect.top])
                        
                        newSprite.lastrect = pygame.Rect(newSprite.rect.left, newSprite.rect.top, newSprite.rect.width, newSprite.rect.height)
                        newSprite.rect = pygame.Rect(sprite.rect.left, sprite.rect.top, sprite.rect.width, sprite.rect.height)
                else:
                    # new, unseen object
                    newSprite = copySpriteStingy(sprite)
                
                # update inventory and inventory history
                newSprite.lastinventory = dict(newSprite.inventory) if newSprite.inventory else dict()

                if sprite.resources:
                    newSprite.inventory = {}
                    try:
                        for key in sprite.resources:
                            try:
                                if str(eval(key)) in colorDict:
                                    color = key
                            except:
                                try:
                                    ## Color and fraction of progress bar displayed from sprite are in principle calculable from pixels
                                    color = colorDict[str(gameObject.resources_colors[key])]
                                except:
                                    color = gameObject.sprite_groups[key][0].colorName
                            
                            limit = gameObject.resources_limits[key]
                            newSprite.inventory[color] = (sprite.resources[key], limit)
                    except:
                        print "in processFrame"
                        embed()
                else:
                    newSprite.inventory = dict()

                newTrackedObjects[sprite.colorName].append(newSprite)
    newMemory['trackedObjects'] = newTrackedObjects

    if not newMemory['isGrid']:
        print 'not GridPhysics!!'
        embed()

    return newMemory

