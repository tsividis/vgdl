'''
Video game description language -- ontology of concepts.

@author: Tom Schaul
'''
import random
from random import choice
from copy import deepcopy
from colors import *
import itertools
from math import sqrt, cos, sin
import pygame
import numpy as np
import scipy.stats
from tools import triPoints, unitVector, vectNorm, oncePerStep
from ai import AStarWorld
from IPython import embed
from util import normalizeVec
import core
import copy
import ipdb
# from line_profiler import LineProfiler
from pygame.locals import K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT


UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
NONE = (0,0)

BASEDIRS = [UP, LEFT, DOWN, RIGHT]

actionToDir = {K_UP:UP, K_DOWN:DOWN, K_LEFT:LEFT, K_RIGHT:RIGHT, K_SPACE:NONE, NONE:NONE}

keyPressToAction = {273: K_UP, 274: K_DOWN, 276: K_LEFT, 275: K_RIGHT, 32: K_SPACE, 0:NONE}


spriteToParams = {
                ## Any sprite not in this dict has params=[]
                'RandomNPC':         ['cooldown', 'speed'], \
                'Chaser':            ['cooldown', 'fleeing', 'stype'],\
                'AStarChaser':       ['fleeing', 'speed', 'stype'], \
                'SpawnPoint':        ['spawnCooldown', 'stype'],\
                'Bomber':            ['cooldown', 'spawnCooldown', 'stype', 'speed'],\
                'OrientedSprite':    ['orientation'], \
                'Conveyor':          ['strength'],\
                'Missile':           ['speed', 'orientation', 'cooldown', 'singleton'],\
                'FlakAvatar':        ['stype'],\
                'AimedAvatar':       ['stype', 'angle_diff'],\
                'AimedFlakAvatar':   ['stype', 'angle_diff'],\
                'ShootAvatar':       ['stype'],
                'RotatingFlippingAvatar':      ['noiseLevel'],\
                'NoisyRotatingFlippingAvatar': ['noiseLevel'],\
                'Flicker':           ['timeout'],\
                }

avatarActions = {
                'HorizontalAvatar':              [K_LEFT, K_RIGHT],\
                'VerticalAvatar':                [K_UP, K_DOWN],\
                'MovingAvatar':                  [K_UP, K_DOWN, K_LEFT, K_RIGHT],\
                'OrientedAvatar':                [K_UP, K_DOWN, K_LEFT, K_RIGHT],\
                'RotatingAvatar':                [K_UP, K_DOWN, K_LEFT, K_RIGHT],\
                'RotatingFlippingAvatar':        [K_UP, K_DOWN, K_LEFT, K_RIGHT],\
                'NoisyRotatingFlippingAvatar':   [K_UP, K_DOWN, K_LEFT, K_RIGHT],\
                'IntertialAvatar':               [K_UP, K_DOWN, K_LEFT, K_RIGHT],\
                'FlakAvatar':                    [K_SPACE, K_LEFT, K_RIGHT],\
                'AimedAvatar':                   [K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT],\
                'AimedFlakAvatar':               [K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT],\
                'ShootAvatar':                   [K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT],\
                }


# ---------------------------------------------------------------------
#     Types of physics
# ---------------------------------------------------------------------
class GridPhysics():
    """ Define actions and key-mappings for grid-world dynamics. """
    def passiveMovement(self, sprite):
        # if sprite.colorName=='BLACK':
            # print "passive movement for", sprite
        if sprite.speed is None:
            speed = 1
        else:
            speed = sprite.speed
        if speed != 0 and hasattr(sprite, 'orientation'):
            sprite._updatePos(sprite.orientation, speed * self.gridsize[0])

    def calculatePassiveMovement(self, sprite, allMovement=False):
        """
        Calculate where the sprite would end up in a timestep, without actually updating its position.
        """
        
        if allMovement:
            lastMove = sprite.lastdisplacement
        else:
            lastMove = sprite.lastmove

        if sprite.speed is None:
            speed = 1
        else:
            speed = sprite.speed
        if speed != 0 and hasattr(sprite, 'orientation'):
            orientation = sprite.orientation
            speed = speed * self.gridsize[0]
            if not((lastMove+1)%sprite.cooldown!=0 or abs(orientation[0])+abs(orientation[1])==0):
            # if not(sprite.cooldown > sprite.lastmove+1 or abs(orientation[0])+abs(orientation[1])==0):
                pos = sprite.rect.move((orientation[0]*speed, orientation[1]*speed))
                return pos.left, pos.top
        else:   # If object has speed = 0 or no 'orientation' attribute
            return None

    def calculatePassiveMovementGivenParams(self, sprite, speed, orientation, allMovement=False):
        """
        Calculate where the sprite would end up in a timestep, without actually updating its position.
        """

        if allMovement:
            lastMove = sprite.lastdisplacement
        else:
            lastMove = sprite.lastmove

        if speed is None:
            speed = 1

        if speed != 0:
            speed = speed * self.gridsize[0]
            if not((lastMove+1)%sprite.cooldown!=0 or abs(orientation[0])+abs(orientation[1])==0):
            # if not(sprite.cooldown > sprite.lastmove+1 or abs(orientation[0])+abs(orientation[1])==0):
                pos = sprite.rect.move((orientation[0]*speed, orientation[1]*speed))
                return pos.left, pos.top
            else:
                return sprite.rect.left, sprite.rect.top
        else:
            return None

    def activeMovement(self, sprite, action, speed=None):
        if speed is None:
            if sprite.speed is None:
                speed = 1.0
            else:
                speed = float(sprite.speed)

        if speed != 0 and action is not None:
            sprite._updatePos(action, speed * self.gridsize[0])

    def calculateActiveMovement(self, sprite, action, speed=None, allMovement=False):
        """
        Calculate where the sprite would end up in a timestep, without actually updating its position.
        """

        if allMovement:
            lastMove = sprite.lastdisplacement
        else:
            lastMove = sprite.lastmove

        if action is not None:
            orientation = action
        if (lastMove+1)%sprite.cooldown==0 and abs(orientation[0])+abs(orientation[1])!=0:

            if speed is None:
                if sprite.speed is None:
                    speed = 1
                else:
                    speed = sprite.speed
            if speed != 0:# and action is not None:
                speed = float(speed) * self.gridsize[0]
                # if speed is None:
                #     speed = sprite.speed

                # orientation = action

        # if not(sprite.cooldown > sprite.lastmove+1 or abs(orientation[0])+abs(orientation[1])==0):
            # if sprite.colorName=='LIGHTORANGE':
                # embed()
            pos = sprite.rect.move((orientation[0]*speed, orientation[1]*speed))
            return pos.left, pos.top
        return(sprite.rect.left, sprite.rect.top)

    # using euclidian distance is also used here because it just works better
    # who uses hamming distance for anything where actual distance is needed?
    # No, seriously... I don't want to break anything
    def distance(self, r1, r2):
        """Euclidean distances. """
        return sqrt((r1.top - r2.top) ** 2
                    + (r1.left - r2.left) ** 2)

    # def distance(self, r1, r2):
    #     """ Grid physics use Hamming distances. """
    #     return (abs(r1.top - r2.top)
    #             + abs(r1.left - r2.left))

def distance(r1, r2):
    """Euclidean distances. """
    return sqrt((r1.top - r2.top) ** 2
                + (r1.left - r2.left) ** 2)

class ContinuousPhysics(GridPhysics):
    gravity = 0.
    friction = 0.02
    #friction = 0.

    def passiveMovement(self, sprite):

        if (sprite.speed != 0 or hasattr(sprite,'jumping') and sprite.jumping) and hasattr(sprite, 'orientation'):#(why was this 0 to begin with???)
            sprite._updatePos(sprite.orientation, sprite.speed)
            if self.gravity > 0 and sprite.mass > 0 and (sprite.gravity or sprite.jumping):
                self.activeMovement(sprite, (0, self.gravity * sprite.mass))
            sprite.speed *= (1 - self.friction)

           

    def calculatePassiveMovement(self, sprite, allMovement=False):
        if allMovement:
            lastMove = sprite.lastdisplacement
        else:
            lastMove = sprite.lastmove

        if (sprite.speed != 0 or hasattr(sprite,'jumping') and sprite.jumping) and hasattr(sprite, 'orientation'):
            pos = sprite.rect.move((sprite.orientation, sprite.speed))
            if self.gravity > 0 and sprite.mass > 0:
                return self.calculateActiveMovement(sprite, (0, self.gravity * sprite.mass))
        else:
            pos = rect
        return pos.left, pos.top


    def activeMovement(self, sprite, action, speed=None):

        if speed is None:
            speed = sprite.speed


        if sprite.gravity or sprite.rope:
            v2 = action[1] / float(sprite.mass) + sprite.orientation[1] * speed
        else:
            v2 = action[1]*sprite.vy_max
        
        if ((hasattr(sprite,'jumping') and sprite.jumping) or action[1]) and (sprite.gravity or sprite.rope):
            v1 = sprite.orientation[0] * speed
        else:
            v1 = action[0]*sprite.vx_max

        if not (hasattr(sprite,'jumping') and sprite.jumping):
            v2 += sprite.speed_bonus[1]
            v1 += sprite.speed_bonus[0]

        sprite.speed_bonus = [0,0]

        sprite.orientation = unitVector((v1, v2))

        
        sprite.speed = vectNorm((v1, v2)) / vectNorm(sprite.orientation)
 

    def calculateActiveMovement(self, sprite, action, speed=None, allMovement=False):
        """ Here the assumption is that the controls determine the direction of
        acceleration of the sprite. """
        
        if allMovement:
            lastMove = sprite.lastdisplacement
        else:
            lastMove = sprite.lastmove

        if speed is None:
            speed = sprite.speed

        v2 = action[1] / float(sprite.mass) + sprite.orientation[1] * speed
        
        if (hasattr(sprite,'jumping') and sprite.jumping) or action[1]:
            v1 = sprite.orientation[0] * speed
        else:
            v1 = action[0]*sprite.vx_max

        if not (hasattr(sprite,'jumping') and sprite.jumping):
            v2 += sprite.speed_bonus[1]
            v1 += sprite.speed_bonus[0]

        sprite.speed_bonus = [0,0]
        sprite.orientation = unitVector((v1, v2))
        sprite.speed = vectNorm((v1, v2)) / vectNorm(sprite.orientation)

        return sprite.rect.left, sprite.rect.top

    def distance(self, r1, r2):
        """ Continuous physics use Euclidean distances. """
        return sqrt((r1.top - r2.top) ** 2
                    + (r1.left - r2.left) ** 2)

class NoFrictionPhysics(ContinuousPhysics):
    friction = 0

class GravityPhysics(ContinuousPhysics):
    gravity = 2.0
    friction = 0


# ---------------------------------------------------------------------
#     Sprite types
# ---------------------------------------------------------------------
# from core import VGDLSprite, Resource
VGDLSprite = core.VGDLSprite
Resource = core.Resource

class Immovable(VGDLSprite):
    """ A gray square that does not budge. """
    color = GRAY #TODO: can these be commented out?
    is_static = True

class Passive(VGDLSprite):
    """ A square that may budge. """
    color = RED

class ResourcePack(Resource):
    """ Can be collected, and in that case adds/increases a progress bar on the collecting sprite.
    Multiple resource packs can refer to the same type of base resource. """
    is_static = True

class Flicker(VGDLSprite):
    """ A square that persists just a few timesteps. """
    color = RED
    timeout = 20
    def __init__(self, **kwargs):
        self._age = 0
        VGDLSprite.__init__(self, **kwargs)

    def update(self, game):
        VGDLSprite.update(self, game)
        if self._age >= self.timeout:
            game.kill_list.append(self)
            # killSprite(self, None, game)
        else:
            self._age += 1

class Spreader(Flicker):
    """ Spreads to its four canonical neighbor positions, and replicates itself there,
    if these are unoccupied. """
    spreadprob = 1.
    def update(self, game):
        Flicker.update(self, game)
        if self._age == 2:
            for u in BASEDIRS:
                if random.random() < self.spreadprob:
                    game._createSprite([self.name], (self.lastrect.left + u[0] * self.lastrect.size[0],
                                                     self.lastrect.top + u[1] * self.lastrect.size[1]))

class SpriteProducer(VGDLSprite):
    """ Superclass for all sprites that may produce other sprites, of type 'stype'. """
    stype = None

class Portal(SpriteProducer):
    is_static = True
    color = BLUE

class SpawnPoint(SpriteProducer):
    prob = None
    total = None
    color = BLACK
    spawnCooldown = None
    is_static = True
    
    def __init__(self, spawnCooldown=1, prob=1, total=None, **kwargs):
        SpriteProducer.__init__(self, **kwargs)
        if prob:
            self.prob = prob
            self.is_stochastic = (prob > 0 and prob < 1)
        if spawnCooldown:
            self.spawnCooldown = spawnCooldown
        if total:
            self.total = total
        self.counter = 0

    def update(self, game):
        if self.total and self.counter >= self.total:
            killSprite(self, None, game)
            return
        self.lastrect = self.rect.copy()

        if self.spawnCooldown < 11:
            if ((game.time+1) % self.spawnCooldown == 0 and random.random() < self.prob):
                game._createSprite([self.stype], (self.rect.left, self.rect.top))
                self.counter += 1
        else:
             if ((game.time+1) % self.spawnCooldown == 3 and random.random() < self.prob):
                game._createSprite([self.stype], (self.rect.left, self.rect.top))
                self.counter += 1
        self.lastmove += 1
        self.lastdisplacement += 1


class RandomNPC(VGDLSprite):
    """ Chooses randomly from all available actions each step. """
    speed = 1
    is_stochastic = True

    def update(self, game):
        self.lastmove -= 1
        VGDLSprite.update(self, game, random_npc=True)
        self.orientation = random.choice(BASEDIRS) #TODO: Make work with random direction
        self.physics.activeMovement(self, self.orientation)
        self.lastmove += 1


class OrientedSprite(VGDLSprite): ##
    """ A sprite that maintains the current orientation. """
    draw_arrow = False
    orientation = RIGHT

    def _draw(self, game):
        """ With a triangle that shows the orientation. """
        VGDLSprite._draw(self, game)
        if self.draw_arrow:
            col = (self.color[0], 255 - self.color[1], self.color[2])
            pygame.draw.polygon(game.screen, col, 
                                triPoints(self.rect, unitVector(self.orientation)))


class Conveyor(OrientedSprite):
    """ A static object that used jointly with the 'conveySprite' interaction to move
    other sprites around."""
    is_static = True
    color = BLUE
    strength = 1
    draw_arrow = True

class Missile(OrientedSprite): ##
    """ A sprite that constantly moves in the same direction. """
    speed = 1
    color = PURPLE

class BreakoutBall(Missile):
    def __init__(self, **kwargs):
        Missile.__init__(self,**kwargs)
        self.rect.width = 0.5*self.rect.width
        self.rect.height = 0.5*self.rect.height



class Switch(VGDLSprite):
    activated = False
    wait_for_release = False
    can_switch = False
    def __init__(self, **kwargs):
        VGDLSprite.__init__(self, **kwargs)

    def update(self, game):
        if not self.can_switch: return
        from pygame.locals import K_SPACE

        if game.keystate[K_SPACE] and not self.wait_for_release:
            self.activated = True
            self.wait_for_release = True
        else:
            self.activated = False

        if not game.keystate[K_SPACE]:
            self.wait_for_release = False

class OrientedFlicker(OrientedSprite, Flicker):
    """ Preserves directionality """
    draw_arrow = True
    speed = 0

class Walker(Missile):
    """ Keep moving in the current horizontal direction. If stopped, pick one randomly. """
    airsteering = False
    is_stochastic = True
    def update(self, game):
        if self.airsteering or self.lastdirection[0] == 0:
            if self.orientation[0] > 0:
                d = 1
            elif self.orientation[0] < 0:
                d = -1
            else:
                d = random.choice([-1, 1])
            self.physics.activeMovement(self, (d, 0))
        Missile.update(self, game)

class WalkJumper(Walker):
    prob = 0.1
    strength = 10
    def update(self, game):
        if self.lastdirection[0] == 0:
            if self.prob < random.random():
                self.physics.activeMovement(self, (0, -self.strength))
        Walker.update(self, game)

class RandomInertial(OrientedSprite, RandomNPC):
    physicstype = ContinuousPhysics

class RandomMissile(Missile):
    def __init__(self, **kwargs):
        Missile.__init__(self, orientation=random.choice(BASEDIRS),
                         speed=random.choice([0.1, 0.2, 0.4]), **kwargs)

class ErraticMissile(Missile):
    """ A missile that randomly changes direction from time to time.
    (with probability 'prob' per timestep). """
    def __init__(self, prob=0.1, **kwargs):
        Missile.__init__(self, orientation=random.choice(BASEDIRS), **kwargs)
        self.prob = prob
        self.is_stochastic = (prob > 0 and prob < 1)

    def update(self, game):
        Missile.update(self, game)
        if random.random() < self.prob:
            self.orientation = random.choice(BASEDIRS)

class Bomber(SpawnPoint, Missile):
    color = ORANGE
    is_static = False
    #lastmove = 0
    def update(self, game):
        self.lastmove -= 1
        Missile.update(self, game)
        SpawnPoint.update(self, game)


class Chaser(RandomNPC): ##
    """ Pick an action that will move toward the closest sprite of the provided target type. """
    stype = None
    fleeing = False

    # is_stochastic=False
    def _closestTargets(self, game):
        bestd = 1e100
        res = []
        if type(self.stype)==tuple:
            targets = getSpritesByColor(game, colorDict[str(self.stype)])
        else:
            targets = game.getSprites(self.stype)
        for target in targets:
            d = self.physics.distance(self.rect, target.rect)
            if d < bestd:
                bestd = d
                res = [target]
            elif d == bestd:
                res.append(target)
        return res

    def _movesToward(self, game, target):
        """ Find the canonical direction(s) which move toward
        the target. """
        res = []
        basedist = self.physics.distance(self.rect, target.rect)
        for a in BASEDIRS:
            r = self.rect.copy()
            r = r.move(a)
            newdist = self.physics.distance(r, target.rect)
            if self.fleeing and basedist < newdist:
                res.append(a)
            if not self.fleeing and basedist > newdist:
                res.append(a)
        return res


    def update(self, game):
        VGDLSprite.update(self, game, random_npc=True) # This increments self.lastmove by 1

        options = []

        for target in self._closestTargets(game):
            options.extend(self._movesToward(game, target))
        if len(options) == 0:
            options = [(0,0)]
        self.physics.activeMovement(self, random.choice(options))


class Fleeing(Chaser):
    """ Just reversing directions"""
    fleeing = True

class AStarChaser(VGDLSprite): ##
    """ Move towards the character using A* search. """
    stype = None
    speed = .1
    fleeing = False
    drawpath = None
    walkableTiles = None
    neighborNodes = None
    path = []
    next_move = None
    last_move = None

    def update(self, game):
        VGDLSprite.update(self, game)
        world = AStarWorld(game)
        error = 10

        # Will not update AStarChaser if there is nothing to chase
        killed = [s.name for s in game.kill_list]
        if 'avatar' in killed:
            print "avatar is dead"
            return

        if game.time % 5 == 0:
            self.path = world.getMoveFor(self, self.target)
        # print path
        # print 'in astar', [world.get_sprite_tile_position(p.sprite) for p in path]
        # Uncomment below to draw debug paths.
        # # self._setDebugVariables(world,path)
        # print 'updating'
        # print len(self.path)
        if self.path:
            # n = min(5, len(self.path)-1)


            if self.next_move == None:
                print 'popping off next path node'
                # self.path.pop(0)
                self.next_move = self.path.pop(0)
                print self.next_move.sprite.rect, self.rect

            next_x, next_y = self.next_move.sprite.rect.x, self.next_move.sprite.rect.y
            self_x, self_y = self.rect.x, self.rect.y


            # print next_x, next_y
            # print self_x, self_y

            dx = abs(next_x - self_x)
            dy = abs(next_y - self_y)

            if dx >= dy:
                movement = [LEFT, RIGHT][next_x > self_x]
            else:
                movement = [UP, DOWN][next_y > self_y]

            if dx < error and dy < error:
                self.last_move = self.next_move
                self.next_move = None
            # print dx, dy, movement

            self.physics.activeMovement(self, movement)


##some montezuma specific objects:
class ThinImmovable(Immovable):
    width = 1.0
    height = 1.0
    def __init__(self, **kwargs):
        Immovable.__init__(self, **kwargs)
        self.rect.width = self.width*self.rect.width
        self.rect.height = self.height*self.rect.height

class ThinConveyor(Conveyor,ThinImmovable):
    width = 1.0
    height = 1.0





# ---------------------------------------------------------------------
#     Avatars: player-controlled sprite types
# ---------------------------------------------------------------------
# from core import Avatar
Avatar = core.Avatar

class MovingAvatar(VGDLSprite, Avatar):
    """ Default avatar, moves in the 4 cardinal directions. """
    color = WHITE
    speed = 1
    is_avatar = True
    alternate_keys=False
    last_gravity=False
    last_rope=False
    availableActions = [K_UP, K_DOWN, K_LEFT, K_RIGHT]

    def declare_possible_actions(self):
        from pygame.locals import K_LEFT, K_RIGHT, K_UP, K_DOWN
        actions = {}
        actions["UP"] = K_UP
        actions["DOWN"] = K_DOWN
        actions["LEFT"] = K_LEFT
        actions["RIGHT"] = K_RIGHT
        return actions

    def _readAction(self, game):
        actions = self._readMultiActions(game)
        if actions:
            return actions[0]
        else:
            return None

    def _readMultiActions(self, game):
        """ Read multiple simultaneously pressed button actions. """
        from pygame.locals import K_LEFT, K_RIGHT, K_UP, K_DOWN, K_a, K_s, K_d, K_w
        res = []
        # res += [RIGHT]
        if self.alternate_keys:
            if   game.keystate[K_d]: res += [RIGHT]
            elif game.keystate[K_a]:  res += [LEFT]
            if   game.keystate[K_w]:    res += [UP]
            elif game.keystate[K_s]:  res += [DOWN]
        else:
            if   game.keystate[K_RIGHT]: res += [RIGHT]
            elif game.keystate[K_LEFT]:  res += [LEFT]
            if   game.keystate[K_UP]:    res += [UP]
            elif game.keystate[K_DOWN]:  res += [DOWN]
        return res

    def update(self, game):

        VGDLSprite.update(self, game)
        
        action = self._readAction(game)
        if action:
            self.physics.activeMovement(self, action)


class HorizontalAvatar(MovingAvatar):
    """ Only horizontal moves.  """
    availableActions = [K_LEFT, K_RIGHT]
    def declare_possible_actions(self):
        from pygame.locals import K_LEFT, K_RIGHT
        actions = {}
        actions["LEFT"] = K_LEFT
        actions["RIGHT"] = K_RIGHT
        return actions


    def update(self, game):
        #print self.rect
        VGDLSprite.update(self, game)
        action = self._readAction(game)
        if action in [RIGHT, LEFT]:
            self.physics.activeMovement(self, action)

class BreakoutAvatar(HorizontalAvatar):
    def __init__(self,**kwargs):
        HorizontalAvatar.__init__(self,**kwargs)
        #print self.rect
        self.rect.width = 2*self.rect.width
        #print self.rect

class Paddle(HorizontalAvatar):
    last_action = None
    c1 = 0.2 #None, move
    c2 = 0.1 #move, none
    c3 = 0.3 #same move
    c4 = -0.1 #opposite move
    def update(self, game):
        VGDLSprite.update(self, game)
        action = self._readAction(game)
        if action in [RIGHT,LEFT]:
            if self.last_action == None:
                self.speed = self.c1
            elif self.last_action == action:
                self.speed = self.c3
            else: 
                self.speed = self.c4
        elif self.last_action in [RIGHT, LEFT]:
            self.speed = self.c2
        #print action
        #print self.last_action
        self.last_action = action
        self.physics.activeMovement(self, action)    

class VerticalAvatar(MovingAvatar):
    """ Only vertical moves.  """

    availableActions = [K_UP, K_DOWN]
    def declare_possible_actions(self):
        from pygame.locals import K_UP, K_DOWN
        actions = {}
        actions["UP"] = K_UP
        actions["DOWN"] = K_DOWN
        return actions

    def update(self, game):
        VGDLSprite.update(self, game)
        action = self._readAction(game)
        if action in [UP, DOWN]:
            self.physics.activeMovement(self, action)

class FlakAvatar(HorizontalAvatar, SpriteProducer):
    """ Hitting the space button creates a sprite of the
    specified type at its location. """
    availableActions = [K_SPACE, K_LEFT, K_RIGHT]
    def declare_possible_actions(self):
        from pygame.locals import K_SPACE
        actions = HorizontalAvatar.declare_possible_actions(self)
        actions["SPACE"] = K_SPACE
        return actions

    color = GREEN
    def update(self, game):
        HorizontalAvatar.update(self, game)
        self._shoot(game)

    def _shoot(self, game):
        from pygame.locals import K_SPACE
        if self.stype and game.keystate[K_SPACE]:
            spawn = game._createSprite([self.stype], (self.rect.left, self.rect.top))


class OrientedAvatar(OrientedSprite, MovingAvatar):
    """ Avatar retains its orientation, but moves in cardinal directions. """
    draw_arrow = True
    availableActions = [K_UP, K_DOWN, K_LEFT, K_RIGHT]
    def update(self, game):
        tmp = self.orientation
        self.orientation = (0, 0)
        VGDLSprite.update(self, game)
        action = self._readAction(game)
        if action:
            self.physics.activeMovement(self, action)
        d = self.lastdirection
        if sum(map(abs, d)) > 0:
            # only update if the sprite moved.
            self.orientation = d
        else:
            self.orientation = tmp

class RotatingAvatar(OrientedSprite, MovingAvatar):
    """ Avatar retains its orientation, and moves forward/backward or rotates
    relative to that. """
    draw_arrow = True
    speed = 0
    availableActions = [K_UP, K_DOWN, K_LEFT, K_RIGHT]
    def update(self, game):
        actions = self._readMultiActions(game)
        if UP in actions:
            self.speed = 1
        elif DOWN in actions:
            self.speed = -1
        if self.orientation in BASEDIRS:
            if LEFT in actions:
                i = BASEDIRS.index(self.orientation)
                self.orientation = BASEDIRS[(i + 1) % len(BASEDIRS)]
            elif RIGHT in actions:
                i = BASEDIRS.index(self.orientation)
                self.orientation = BASEDIRS[(i - 1) % len(BASEDIRS)]
        VGDLSprite.update(self, game)
        self.speed = 0

class RotatingFlippingAvatar(RotatingAvatar):
    """ Uses a different action set: DOWN makes it spin around 180 degrees.
    Optionally, a noise level can be specified
    """

    noiseLevel = 0
    availableActions = [K_UP, K_DOWN, K_LEFT, K_RIGHT]

    def update(self, game):
        actions = self._readMultiActions(game)
        if len(actions) > 0 and self.noiseLevel > 0:
            # pick a random one instead
            if random.random() < self.noiseLevel*4:
                actions = [random.choice([UP, LEFT, DOWN, RIGHT])]
        if UP in actions:
            self.speed = 1
        if self.orientation in BASEDIRS:
            if DOWN in actions:
                i = BASEDIRS.index(self.orientation)
                self.orientation = BASEDIRS[(i + 2) % len(BASEDIRS)]
            elif LEFT in actions:
                i = BASEDIRS.index(self.orientation)
                self.orientation = BASEDIRS[(i + 1) % len(BASEDIRS)]
            elif RIGHT in actions:
                i = BASEDIRS.index(self.orientation)
                self.orientation = BASEDIRS[(i - 1) % len(BASEDIRS)]
        VGDLSprite.update(self, game)
        self.speed = 0

    @property
    def is_stochastic(self):
        return self.noiseLevel > 0

class NoisyRotatingFlippingAvatar(RotatingFlippingAvatar):
    noiseLevel = 0.1

class ShootAvatar(OrientedAvatar, SpriteProducer):
    """ Produces a sprite in front of it (e.g., Link using his sword). """
    ammo=None
    availableActions = [K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT]
    def __init__(self, stype=None, **kwargs):
        self.stype = stype
        OrientedSprite.__init__(self, **kwargs)

    def update(self, game):

        OrientedAvatar.update(self, game)
        if self._hasAmmo():
            self._shoot(game)

    def _hasAmmo(self):
        if self.ammo is None:
            return True
        elif self.ammo in self.resources:
            return self.resources[self.ammo] > 0
        return False

    def _reduceAmmo(self):
        if self.ammo is not None and self.ammo in self.resources:
            self.resources[self.ammo] -= 1

    def _shoot(self, game):

        from pygame.locals import K_SPACE
        if self.stype and game.keystate[K_SPACE]:

            u = unitVector(self.orientation)
            newones = game._createSprite([self.stype], (self.lastrect.left + u[0] * self.lastrect.size[0],
                                                       self.lastrect.top + u[1] * self.lastrect.size[1]))
            if len(newones) > 0  and isinstance(newones[0], OrientedSprite):
                newones[0].orientation = unitVector(self.orientation)
            self._reduceAmmo()


class AimedAvatar(ShootAvatar):
    """ Can change the direction of firing, but not move. """
    speed=0
    angle_diff=0.05
    availableActions = [K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT]
    def update(self, game):
        VGDLSprite.update(self, game)
        self._aim(game)
        self._shoot(game)

    def _aim(self, game):
        action = self._readAction(game)
        if action in [UP, DOWN]:
            if action == DOWN:
                angle = self.angle_diff
            else:
                angle = -self.angle_diff
            self.orientation = unitVector((self.orientation[0]*cos(angle)-self.orientation[1]*sin(angle),
                                           self.orientation[0]*sin(angle)+self.orientation[1]*cos(angle)))

class AimedFlakAvatar(AimedAvatar):
    """ Can move left and right """
    only_active=True
    speed=1
    availableActions = [K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT]

    def update(self, game):
        AimedAvatar.update(self, game)
        action = self._readAction(game)
        if action in [RIGHT, LEFT]:
            self.physics.activeMovement(self, action)

class InertialAvatar(OrientedAvatar):
    speed = 1
    physicstype = ContinuousPhysics
    availableActions = [K_UP, K_DOWN, K_LEFT, K_RIGHT]

    def update(self, game):
        #MovingAvatar.update(self, game)

        action = MovingAvatar._readAction(self,game)
        if action:
            self.physics.activeMovement(self, action)
        VGDLSprite.update(self, game)

class MarioAvatar(InertialAvatar):
    physicstype = GravityPhysics
    draw_arrow = False
    strength = 15
    movestrength = sqrt(strength)
    vx_max = 8
    vy_max = 8
    airsteering = False
    last_vy = 0
    jumping = False
    wait_step = 0
    airstrength = 1
    speed_bonus = [0,0]
    gravity = True
    rope = False
    last_gravity = True
    last_rope = False
    #decay = .5
    decay = 0

    def declare_possible_actions(self):
        from pygame.locals import K_LEFT, K_RIGHT, K_UP, K_DOWN
        actions = {}
        actions["UP"] = K_UP
        actions["DOWN"] = K_DOWN
        actions["LEFT"] = K_LEFT
        actions["RIGHT"] = K_RIGHT
        return actions

    def update(self, game):

        from pygame.locals import K_SPACE


        if self.lastrect == self.rect and not self.jumping:
            self.speed = self.speed * self.orientation[0]
            self.orientation = (1,0)

        action = self._readAction(game)
        #print "initial action:"
        #print action

        if action == None:
            action = [0, 0]
        action = list(action)


        if self.rope:
            #print action[0] != 0
            #print game.keystate[K_SPACE]
            #print self.jumping
            if action[0] != 0 and game.keystate[K_SPACE] and not self.jumping:
                print "JUMP OFF ROPE"
                action[1] = -self.strength
                self.jumping = True
                self.wait_step = 0
                self.airstrength = 1

        if self.gravity:
            action[1]=0

        # presumibly, this means the sprite is 'landed'
            self.airstrength *= (1-self.decay)

            if self.last_vy == self.lastrect.y - self.rect.y:
            #print "are equal"
                self.wait_step += 1
                if not self.jumping:
                #print "no"
                #action[0] = action[0] * self.movestrength
                    action = [action[0] * self.movestrength,0]
                    if game.keystate[K_SPACE] and not self.jumping:
                        action[1] = -self.strength
                        self.jumping = True
                        self.wait_step = 0
                        self.airstrength = 1
                else:
                #print "yes"
                    action[0] = action[0] * self.movestrength * self.airstrength
                #action[0] = 0

            else:
                self.wait_step = 0
                action[0] = 0

        # this is pretty hacky. What if sprite doesn't move very fast?
            if self.wait_step > 1:
                self.jumping = False
        
        #print action
        self.physics.activeMovement(self, action)
        #changes speed


        vx = self.orientation[0]*self.speed

        #print((vx,self.orientation[1]*self.speed))

        if abs(vx) > self.vx_max:
            # vx always greater than zero at this point
            sign = abs(vx)/vx
            vx = sign*self.vx_max
            vy = self.orientation[1]*self.speed
            self.orientation = unitVector((vx, vy))
            self.speed = vectNorm((vx, vy))/ vectNorm(self.orientation)

        #print (self.orientation[0]*self.speed, self.orientation[1]*self.speed)

        # a less precise vy, but this is useful


        #two_ago = self.lastrect.y
        
        #if self.rect.y == self.lastrect.y and self.rect.y == two_ago:
        #    self.jumping = False

        
        self.last_vy = self.lastrect.y-self.rect.y
        VGDLSprite.update(self, game)
        self.last_gravity = self.gravity
        self.gravity = True
        self.last_rope = self.rope
        self.rope = False


        #print self.orientation
        #print (self.orientation[0]*self.speed, self.orientation[1]*self.speed)

        #print self.orientation[0]*self.speed

class RopeAvatar(InertialAvatar):

    max_speed = 5
    vx_max = 1
    jumping = False
    speed_bonus = [0,0]

    def declare_possible_actions(self):
        from pygame.locals import K_LEFT, K_RIGHT, K_UP, K_DOWN
        actions = {}
        actions["UP"] = K_UP
        actions["DOWN"] = K_DOWN
        actions["LEFT"] = K_LEFT
        actions["RIGHT"] = K_RIGHT
        return actions

    def update(self,game):
        action = self._readAction(game)
        if action==None:
            action=[0,0]
        action=list(action)
        self.speed = 0
        action = [self.max_speed*action[0],self.max_speed*action[1]]
        
        self.physics.activeMovement(self,action)
        #print(self.rect)
        VGDLSprite.update(self, game)
        

class ClimbingAvatar(MarioAvatar, MovingAvatar):
    climbing = False
    saved_gravity = GravityPhysics.gravity
    saved_steering = MarioAvatar.airsteering
    jumping = False
    def update(self, game):
        action = self._readAction(game)
        if action is None:
            action = (0, 0)
        from pygame.locals import K_SPACE, K_UP, K_DOWN

        if self.climbing:
            self.physics.gravity = 0
            self.airsteering = True
        else:
            self.physics.gravity = self.saved_gravity
            self.airsteering = self.saved_steering

        if game.keystate[K_SPACE] and self.orientation[1] == 0:
            self.climbing = False
            self.jumping = True
            self.physicstype = GravityPhysics
            action = (action[0] * sqrt(self.strength), -self.strength)
        elif game.keystate[K_UP] and self.climbing:
            climbing = True
        elif game.keystate[K_DOWN] and self.climbing:
            climbing = True
        elif self.orientation[1] == 0 or self.airsteering:
            action = (action[0] * sqrt(self.strength), 0)
        else:
            action = (0, 0)
            if self._velocity()[1] > 0:
                self.jumping = False
        self.climbing = False
        self.physics.activeMovement(self, action)
        VGDLSprite.update(self, game)


class FrostBiteAvatar(HorizontalAvatar, InertialAvatar):
    physicstype = GravityPhysics
    draw_arrow = False
    strength = 6
    airsteering = True
    speed = .25
    solid = True
    jumping = False

    def update(self, game):
        action = self._readAction(game)
        if action is None:
            action = (0, 0)
        from pygame.locals import K_UP, K_DOWN
        if game.keystate[K_UP] and self.orientation[1] == 0:
            action = (action[0] * sqrt(self.strength), -self.strength)
            self.jumping = True
        elif game.keystate[K_DOWN] and self.orientation[1] == 0:
            self.solid = False
        elif self.orientation[1] == 0 or self.airsteering:
            action = (action[0] * sqrt(self.strength), 0)
        else:
            action = (0, 0)
        if self._velocity()[1] > 0:
            self.jumping = False

        self.physics.activeMovement(self, action)
        HorizontalAvatar.update(self, game)
        VGDLSprite.update(self, game)

class Floe(Missile, Switch):
    speed = 0.05
    def update(self, game):
        Missile.update(self, game)
        Switch.update(self, game)

class FrostbiteIgloo(SpawnPoint, Switch):
    offsets = [[-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0]]
    total = None
    triggered = False
    detriggered = False
    triggers = 0
    def __init__(self, platforms=8, **kwargs):
        SpawnPoint.__init__(self, **kwargs)
        Switch.__init__(self, **kwargs)
        self.total = 5
        self.platforms = platforms
        self.last_count = 0


    def update(self, game):
        Switch.update(self, game)
        new_count = (self.triggers * self.total) / (self.platforms)

        if new_count > self.last_count:
            self.last_count = new_count
            SpawnPoint.update(self, game)

        if new_count < self.last_count:
            game.kill_list.append(self.last_sprites.pop())
            self.counter -= 1
            self.last_count = new_count

        if self.triggered and self.counter < self.total:
            self.xoffset = self.offsets[new_count][0]
            self.yoffset = self.offsets[new_count][1]

            self.triggers += 1
            self.triggered = False

        if self.detriggered and self.triggers > 0:
            self.triggers -= 1
            self.detriggered = False

class MontezumaAvatar(MarioAvatar):
    width = 1.0
    height = 1.0
    def __init__(self, **kwargs):
        MarioAvatar.__init__(self, **kwargs)
        self.rect.width = self.width*self.rect.width
        self.rect.height = self.height*self.rect.height



# ---------------------------------------------------------------------
#     Conditional criteria
# ---------------------------------------------------------------------
# from core import Conditional
Conditional = core.Conditional

class SpriteCount(Conditional):
    ops = {'equ': lambda x, y: x == y,
           'lss': lambda x, y: x < y,
           'grt': lambda x, y: x > y,
           'leq': lambda x, y: x <= y,
           'geq': lambda x, y: x >= y,
           'neq': lambda x, y: x != y
           }
    def __init__(self, stype=None, count=0, op='equ'):
        self.stype = stype
        self.count = count
        self.op = op
    def condition(self, game):
        if self.ops[self.op](game.numSprites(self.stype), self.count):
            return True
        else:
            return False

class OnStart(Conditional):
    def condition(self, game):
        if game.started:
            return True
        return False

# ---------------------------------------------------------------------
#     Termination criteria
# ---------------------------------------------------------------------

Termination = core.Termination

class Timeout(Termination):
    def __init__(self, limit=0, win=False):
        self.limit = limit
        self.win = win
        self.name = 'Timeout'

    def isDone(self, game):
        if game.time >= self.limit:
            return True, self.win
        else:
            return False, None

class SpriteCounter(Termination):
    """ Game ends when the number of sprites of type 'stype' hits 'limit' (or below). """
    def __init__(self, limit=0, stype=None, win=True):
        self.limit = limit
        self.stype = stype
        self.win = win
        self.name = 'SpriteCounter'

    def isDone(self, game):
        if game.numSprites(self.stype) <= self.limit:
            # print "spritecounter rule", self.stype, self.limit
            return True, self.win
        else:
            return False, None

class MultiSpriteCounter(Termination):
    """ Game ends when the sum of all sprites of types 'stypes' hits 'limit'. """
    def __init__(self, limit=0, win=True, **kwargs):
        self.limit = limit
        self.win = win
        self.stypes = kwargs.values()
        self.name = 'MultiSpriteCounter'

    def isDone(self, game):
        if sum([game.numSprites(st) for st in self.stypes]) == self.limit:
            return True, self.win
        else:
            return False, None

class NoveltyTermination(Termination):
    def __init__(self, s1, s2, win=True, args=None):
        self.s1 = s1
        self.s2 = s2
        self.win = win
        self.name = 'NoveltyTermination'
        self.args = args
        if self.args is not None:
            # print "found args in noveltytermination"
            if type(self.args) == set:
                self.args = list(self.args)[0]
            elif type(self.args) == dict:
                # embed()
                pass    def isDone(self, game):

        ## self.args lets us do precondition-dependent terminations.
        if self.args:
            if type(self.args)==dict:
                item, num, negated, operator_name = self.args['item'], self.args['num'], eval(self.args['negated']), self.args['operator_name']
            else:
                item, num, negated, operator_name = self.args.item, self.args.num, self.args.negated, self.args.operator_name
            if negated:
                oppositeOperatorMap = {"<=": ">", ">=": "<", "<": ">=", ">": "<="}
                true_operator = oppositeOperatorMap[operator_name]
            else:
                true_operator = operator_name
            try:
                resource_str = str(game.getAvatars()[0].resources[item])
            except IndexError:
                return False, None

            if not eval(resource_str+true_operator+str(num)):
                return False, None

            # else:
            #     print "found correct preconditions"
                # embed()
        for e in game.effectList:

            id_not_found = False
            class1, class2 = 'none', 'none'
            if (e[0] in ['killSprite', 'transformTo', 'nothing']) and len(e) > 2:

                try:
                    name1 = game.getAllObjects()[e[1]].name
                    class1 = str(game.getAllObjects()[e[1]].__class__)
                    # if 'RandomNPC' in class1  and e[2]  != 'avatar':
                        # return False, None
                    # if 'Flicker' in class1  and e[2]  == 'avatar':
                        # return False, None       
                except KeyError:
                    if e[1]=='ENDOFSCREEN':
                        name1 = 'EOS'
                    elif e[1] in [obj.ID for obj in game.kill_list]:
                        name1 = [obj.name for obj in game.kill_list
                            if obj.ID==e[1]][0]
                        class1 = str([obj.__class__ for obj in game.kill_list
                            if obj.ID==e[1]][0])
                        # if 'RandomNPC' in class1  and e[2]  != 'avatar':
                            # return False, None
                        # if 'Flicker' in class1  and e[2]  == 'avatar':
                            # return False, None
                    elif e[1] in game.getObjects().keys():
                        name1 = game.getObjects()[e[1]]['sprite'].name
                        class1 =  str(game.getObjects()[e[1]]['sprite'].__class__)
                        # if 'RandomNPC' in class1  and e[2]  != 'avatar':
                            # return False, None
                        # if 'Flicker' in class1  and e[2]  == 'avatar':
                            # return False, None
                    else:
                        id_not_found = True
                        # print "id_not_found 1"
                        # embed()
                        ## This happens when we shoot an object and IDs are mismatched; default to the thing we shoot.
                        ## We've confirmed that this isn't due to other objects shot by other objects.
                        try:
                            name1 = game.getAvatars()[0].stype
                            if e[2] == 'avatar':
                                return False, None
                        except (AttributeError, IndexError) as err:
                            # Avatar dead or doesn't have stype
                            name1 = ''
                except IndexError:
                    print("IndexError in game.all_objects (1)")
                    embed()
                except TypeError:
                    print("TypeError in game.all_objects (1)")
                    embed()
                try:
                    name2 = game.getAllObjects()[e[2]].name
                    class2 = str(game.getAllObjects()[e[2]].__class__)
                    # if 'RandomNPC' in class2  and e[1]  != 'avatar':
                        # return False, None
                    # if 'Flicker' in class2  and e[1]  == 'avatar':
                        # return False, None   
                except KeyError:
                    if e[2]=='ENDOFSCREEN':
                        name2 = 'EOS'
                    elif e[2] in [obj.ID for obj in game.kill_list]:
                        # candidates = [obj for obj in game.kill_list]
                        name2 = [obj.name for obj in game.kill_list
                            if obj.ID==e[2]][0]
                        class2 = str([obj.__class__ for obj in game.kill_list
                            if obj.ID==e[2]][0])
                        # if 'RandomNPC' in class2  and e[1]  != 'avatar':
                            # return False, None
                        # if 'Flicker' in class2  and e[1]  == 'avatar':
                            # return False, None
                    elif e[2] in game.getObjects().keys():
                        name2 = game.getObjects()[e[2]]['sprite'].name
                        class2 =  str(game.getObjects()[e[2]]['sprite'].__class__)
                        # if 'RandomNPC' in class2  and e[1]  != 'avatar':
                            # return False, None
                        # if 'Flicker' in class2  and e[1]  == 'avatar':
                            # return False, None
                    else:
                        id_not_found = True
                        # print "id_not_found 2"
                        # embed()
                        ## This happens when we shoot an object and IDs are mismatched; default to the thing we shoot.
                        ## We've confirmed that this isn't due to other objects shot by other objects.
                        try:
                            name2 = game.getAvatars()[0].stype
                        except (AttributeError, IndexError) as err:
                            # Avatar dead or doesn't have stype
                            name2 = ''
                except IndexError:
                    print("IndexError in game.all_objects (2)")
                    embed()
                except TypeError:
                    print("TypeError in game.all_objects (2)")
                    embed()
                if name1==self.s1 and name2==self.s2:
                    # if id_not_found:
                        # print "id_not_found"
                        # embed()
                        # pass
                    print("NoveltyTermination with {} and {}".format(
                        name1, name2))
                    # if name1=='c7' and name2=='avatar':
                    #     ipdb.set_trace()
                    # print("Classes are {} and {}".format(class1, class2))
                    return True, self.win
            elif len(e) > 2 and e[2]=='ENDOFSCREEN':
                name2 = 'EOS'
                try:
                    name1 = game.getAllObjects()[e[1]].name
                    # Don't get a noveltyTermination from RandomNPCs
                    # if 'RandomNPC' in str(game.all_objects[e[1]]['sprite'].__class__) and e[2]  != 'avatar':
                        # return False, None
                    # if 'Flicker' in str(game.all_objects[e[1]]['sprite'].__class__)  and e[2]  == 'avatar':
                        # return False, None
                except KeyError:
                    if e[1]=='ENDOFSCREEN':
                        name1 = 'EOS'
                    elif e[1] in [obj.ID for obj in game.kill_list]:
                        name1 = [obj.name for obj in game.kill_list
                            if obj.ID==e[1]][0]
                    elif e[1] in game.getObjects().keys():
                        name1 = game.getObjects()[e[1]]['sprite'].name
                    else:
                        # print "Couldn't find object in NoveltyTermination"
                        id_not_found = True
                        # embed()
                        try:
                            name1 = game.getAvatars()[0].stype
                        except (AttributeError, IndexError) as err:
                            # Avatar dead or doesn't have stype
                            name1 = ''
                except IndexError:
                    print("IndexError in game.all_objects")
                    # embed()
                    pass
                except:
                    print("AttributeError in game.all_objects")
                    embed()
                # self.s2 returns a type for the EOS for some reason, so the
                # check has to be performed like this
                if name1==self.s1 and name2 in str(self.s2):
                    if id_not_found:
                        print "id_not_found"
                        embed()
                        pass
                    print("NoveltyTermination with {} and {}".format(
                        name1, name2))
                    # if name1=='c7' and name2=='avatar':
                    #     ipdb.set_trace()
                    return True, self.win
        return False, None


    # def isDone(self, game):
    #     ## self.args lets us do precondition-dependent terminations.
    #     if self.args:
    #         if type(self.args)==dict:
    #             item, num, negated, operator_name = self.args['item'], self.args['num'], eval(self.args['negated']), self.args['operator_name']
    #         else:
    #             item, num, negated, operator_name = self.args.item, self.args.num, self.args.negated, self.args.operator_name
    #         if negated:
    #             oppositeOperatorMap = {"<=": ">", ">=": "<", "<": ">=", ">": "<="}
    #             true_operator = oppositeOperatorMap[operator_name]
    #         else:
    #             true_operator = operator_name
    #         try:
    #             resource_str = str(game.getAvatars()[0].resources[item])
    #         except IndexError:
    #             return False, None

    #         if not eval(resource_str+true_operator+str(num)):
    #             return False, None

    #     for e in game.effectList:
    #         id_not_found = False
    #         if (e[0] in ['killSprite', 'transformTo', 'nothing']) and len(e) > 2:
    #             try:
    #                 name1 = game.all_objects[e[1]].name
    #             except KeyError:
    #                 if e[1]=='ENDOFSCREEN':
    #                     name1 = 'EOS'
    #                 elif e[1] in [obj.ID for obj in game.kill_list]:
    #                     name1 = [obj.name for obj in game.kill_list
    #                         if obj.ID==e[1]][0]
    #                 elif e[1] in game.getAllObjects().keys():
    #                     name1 = game.getAllObjects()[e[1]].name
    #                 else:
    #                     id_not_found = True
    #                     ## This happens when we shoot an object and IDs are mismatched; default to the thing we shoot.
    #                     ## We've confirmed that this isn't due to other objects shot by other objects.
    #                     try:
    #                         name1 = game.getAvatars()[0].stype
    #                     except (AttributeError, IndexError) as err:
    #                         # Avatar dead or doesn't have stype
    #                         name1 = ''
    #             except IndexError:
    #                 print("IndexError in game.all_objects")
    #                 embed()
    #             try:
    #                 name2 = game.all_objects[e[2]].name
    #             except KeyError:
    #                 if e[2]=='ENDOFSCREEN':
    #                     name2 = 'EOS'
    #                 elif e[2] in [obj.ID for obj in game.kill_list]:
    #                     name2 = [obj.name for obj in game.kill_list
    #                         if obj.ID==e[2]][0]
    #                 elif e[2] in game.getAllObjects().keys():
    #                     name2 = game.getAllObjects()[e[2]].name
    #                 else:
    #                     id_not_found = True
    #                     ## This happens when we shoot an object and IDs are mismatched; default to the thing we shoot.
    #                     ## We've confirmed that this isn't due to other objects shot by other objects.
    #                     try:
    #                         name2 = game.getAvatars()[0].stype
    #                     except (AttributeError, IndexError) as err:
    #                         # Avatar dead or doesn't have stype
    #                         name2 = ''
    #             except IndexError:
    #                 print("IndexError in game.all_objects")
    #                 embed()

    #             if (name1==self.s1 and name2==self.s2) or (name2==self.s1 and name1==self.s2):
    #                 if id_not_found:
    #                     pass
    #                 # print 'noveltyrule', self.s1, self.s2, self.args
    #                 return True, self.win
    #         elif len(e) > 2 and e[2]=='ENDOFSCREEN':
    #             name2 = 'EOS'
    #             try:
    #                 name1 = game.all_objects[e[1]].name
    #             except KeyError:
    #                 if e[1]=='ENDOFSCREEN':
    #                     name1 = 'EOS'
    #                 elif e[1] in [obj.ID for obj in game.kill_list]:
    #                     name1 = [obj.name for obj in game.kill_list
    #                         if obj.ID==e[1]][0]
    #                 elif e[1] in game.getAllObjects().keys():
    #                     name1 = game.getAllObjects()[e[1]].name
    #                 else:
    #                     # print "Couldn't find object in NoveltyTermination"
    #                     id_not_found = True
    #                     # embed()
    #                     try:
    #                         name1 = game.getAvatars()[0].stype
    #                     except (AttributeError, IndexError) as err:
    #                         # Avatar dead or doesn't have stype
    #                         name1 = ''
    #             except IndexError:
    #                 print("IndexError in game.all_objects")
    #                 # embed()
    #                 pass
    #             # self.s2 returns a type for the EOS for some reason, so the
    #             # check has to be performed like this
    #             # if (name1==self.s1 and name2 in str(self.s2) or name2==self.s1 and name1 in str(self.s2)):
    #             if name1==self.s1 and name2 in str(self.s2):
    #                 if id_not_found:
    #                     pass
    #                 # print 'noveltyrule', self.s1, self.s2, self.args
    #                 return True, self.win
    #     return False, None

# ---------------------------------------------------------------------
#     Helper functions
# ---------------------------------------------------------------------
def getColor(sprite):
    try:
        color_tuple = str( sprite.color)
        try:
            return colorDict[color_tuple]
        except KeyError:
            return color_tuple

    except AttributeError:
        return None

# ---------------------------------------------------------------------
#     Effect types (invoked after an event).
# ---------------------------------------------------------------------
def nothing(sprite, partner, game):
    """ Returns no interaction """
    # print ("nothing", sprite.rect, partner.rect, sprite.name, partner.name)
    return ("nothing", sprite.ID, partner.ID)

def killSprite(sprite, partner, game):
    """ Kill command """
    game.kill_list.append(sprite)
    if not None in {sprite, partner}:
        return ("killSprite", sprite.ID, partner.ID) # partner = agent, sprite = what's being killed

def cloneSprite(sprite, partner, game):
    newones = game._createSprite([sprite.name], (sprite.rect.left, sprite.rect.top))
    # try:
    #     if len(newones) > 0:
    #         if isinstance(sprite, OrientedSprite) and isinstance(newones[0], OrientedSprite):
    #             newones[0].orientation = sprite.orientation
    #         game.kill_list.append(sprite)
    #         game.dead.append(sprite)
    # except:
    #     pass
    return ("cloneSprite", sprite.ID, partner.ID)

def transformTo(sprite, partner, game, stype='wall'):
    newones = game._createSprite([stype], (sprite.rect.left, sprite.rect.top))
    if len(newones) > 0:
        if isinstance(sprite, OrientedSprite) and isinstance(newones[0], OrientedSprite):
            #print("KEEPING ORIENTATION SPEED")
            newones[0].orientation = sprite.orientation
            newones[0].speed = sprite.speed
        newones[0].resources = sprite.resources
        game.kill_list.append(sprite)
    args = {'stype':stype}
    return ("transformTo", sprite.ID, partner.ID, args)

def transformToOnLanding(sprite, partner, game, stype='wall'):
    """sprite will be transformed to stype when partner (avatar) lands on it from above"""
    if partner.speed*partner.orientation[1] == 0 and partner.lastrect.y != partner.rect.y:
        transformTo(sprite, partner, game, stype)

    return ("transformToOnLanding", sprite.ID, partner.ID)

# def triggerOnLanding(sprite, partner, game, strigger=None):
#     '''triggers a triggerable sprite. triggerable is interesting. should change this?'''
#     if partner.speed*partner.orientation[1] == 0 and partner.lastrect.y != partner.rect.y:
#         trigger(sprite, partner, game, strigger)
#         args = {'strigger':strigger}
#         return ("trigger", sprite.ID, partner.ID, args)

def stepBack(sprite, partner, game):
    """ Revert last move. """
    sprite.rect = sprite.lastrect

    if partner:
        try:
            return ("stepBack", sprite.ID, partner.ID)
        except:
            ## happens most likely with EOS events.
            return ("stepBack", sprite.ID, partner)

def undoAll(sprite, partner, game):
    """ Revert last moves of all sprites. """
    for s in game:
        s.rect = s.lastrect

    return ('undoAll', sprite.ID , partner.ID)

def bounceForward(sprite, partner, game): # FLAG
    """ The partner sprite pushed, so if possible move in the opposite direction. """
    # print "in beginning of bounceForward"
    # print partner.lastdirection
    sprite.physics.activeMovement(sprite, unitVector(partner.lastdirection))
    game._updateCollisionDict(sprite)
    return ('bounceForward', sprite.ID, partner.ID)

def conveySprite(sprite, partner, game):
    """ Moves the sprite in target direction by some step size. """
    tmp = sprite.lastrect
    v = unitVector(partner.orientation)
    #print "CONVEYING"
    # sprite.physics.activeMovement(sprite, v, speed=partner.strength)
    sprite.speed_bonus = [v[0]*partner.strength,v[1]*partner.strength]
    sprite.lastrect = tmp
    game._updateCollisionDict(sprite)
    return ('conveySprite', sprite.ID, partner.ID)

def windGust(sprite, partner, game):
    """ Moves the sprite in target direction by some step size, but stochastically
    (step, step-1 and step+1 are equally likely) """
    s = random.choice([partner.strength, partner.strength + 1, partner.strength - 1])
    if s != 0:
        tmp = sprite.lastrect.copy()
        v = unitVector(partner.orientation)
        sprite.physics.activeMovement(sprite, v, speed=s)
        sprite.lastrect = tmp
        game._updateCollisionDict(sprite)
        return ('windGust', sprite.ID, partner.ID)

def slipForward(sprite, partner, game, prob=0.5):
    """ Slip forward in the direction of the current orientation, sometimes."""
    if prob > random.random():
        tmp = sprite.lastrect
        v = unitVector(sprite.orientation)
        sprite.physics.activeMovement(sprite, v, speed=1)
        sprite.lastrect = tmp
        game._updateCollisionDict(sprite)
        return ('slipForward', sprite.ID, partner.ID)

def attractGaze(sprite, partner, game, prob=0.5):
    """ Turn the orientation to the value given by the partner. """
    if prob > random.random():
        sprite.orientation = partner.orientation
        return ('attractGaze', sprite.ID, partner.ID)

def turnAround(sprite, partner, game):
    sprite.rect = sprite.lastrect
    sprite.lastmove = sprite.cooldown -1 ## Needed because updatePos looks for lastmove+1%cooldown==0
    # sprite.lastmove = 4
    sprite.physics.activeMovement(sprite, DOWN)
    # sprite.lastmove = sprite.cooldown
    # sprite.physics.activeMovement(sprite, DOWN)
    reverseDirection(sprite, partner, game)
    game._updateCollisionDict(sprite)
    if partner == None:
        return ('turnAround', sprite.ID)
    return ('turnAround', sprite.ID, partner.ID)

def turn(sprite, partner, game):
    sprite.rect = sprite.lastrect
    sprite.lastmove = sprite.cooldown -1 ## Needed because updatePos looks for lastmove+1%cooldown==0
    reverseDirection(sprite, partner, game)
    game._updateCollisionDict(sprite)
    if partner == None:
        return ('turn', sprite.ID)
    return ('turn', sprite.ID, partner.ID)

def reverseDirection(sprite, partner, game): # FLAG
    sprite.orientation = (-sprite.orientation[0], -sprite.orientation[1])
    if partner == None:
        return ('reverseDirection', sprite.ID)
    return ('reverseDirection', sprite.ID, partner.ID)

##TODO: add event labels for the below effects
# def reverseFloeIfActivated(sprite, partner, game, strigger=None):
#     '''sprite is Floe, partner is FrostbiteAvatar'''
#     if sprite.activated:
#         detrigger(sprite, partner, game, strigger)
#         reverseDirection(sprite, partner, game)
#         sprite.activated = False
#     ## returning the below is likely too much. Only adding this now for consistency of return statements.
#     args = {'strigger':strigger}
#     return ('reverseFloeIfActivated', sprite.ID, partner.ID, args)

# def trigger(sprite, partner, game, strigger=None):
#     if strigger == None:
#         triggers = [sprite]
#     else:
#         triggers = game.getSprites(strigger)

#     for sprite in triggers:
#         sprite.triggered = True
#     return ('trigger', sprite.ID, partner.ID, strigger)

# def detrigger(sprite, partner, game, strigger=None):
#     if strigger == None:
#         triggers = [sprite]
#     else:
#         triggers = game.getSprites(strigger)

#     for sprite in triggers:
#         sprite.detriggered = True
#     args = {'strigger':strigger}
#     return ('detrigger', sprite.ID, partner.ID, args)

def flipDirection(sprite, partner, game):
    sprite.orientation = random.choice(BASEDIRS)
    return ('flipDirection', sprite.ID, partner.ID)

def bounceDirection(sprite, partner, game, friction=0): # FLAG
    """ The centers of the objects determine the direction"""
    stepBack(sprite, partner, game)
    inc = sprite.orientation
    snorm = unitVector((-sprite.rect.centerx + partner.rect.centerx,
                        - sprite.rect.centery + partner.rect.centery))
    dp = snorm[0] * inc[0] + snorm[1] * inc[1]
    sprite.orientation = (-2 * dp * snorm[0] + inc[0], -2 * dp * snorm[1] + inc[1])
    sprite.speed *= (1. - friction)
    return ('bounceDirection', sprite.ID, partner.ID)

def wallBounce(sprite, partner, game, friction=0): # FLAG
    """ Bounce off orthogonally to the wall. """
    if not oncePerStep(sprite, game, 'lastbounce'):
        return ('wallBounce', sprite.ID, partner.ID)
    sprite.speed *= (1. - friction)
    stepBack(sprite, partner, game)
    if abs(sprite.rect.centerx - partner.rect.centerx) > abs(sprite.rect.centery - partner.rect.centery):
        sprite.orientation = (-sprite.orientation[0], sprite.orientation[1])
    else:
        sprite.orientation = (sprite.orientation[0], -sprite.orientation[1])
    return ('wallBounce', sprite.ID, partner.ID)

def wallStop(sprite, partner, game, friction=0): # FLAG
    """ Stop just in front of the wall, removing that velocity component,
    but possibly sliding along it. """
    if not oncePerStep(sprite, game, 'laststop'):
        return ('wallStop', sprite.ID, partner.ID)
    stepBack(sprite, partner, game)
    if abs(sprite.rect.centerx - partner.rect.centerx) > abs(sprite.rect.centery - partner.rect.centery):
        sprite.orientation = (0, sprite.orientation[1] * (1. - friction))
    else:
        sprite.orientation = (sprite.orientation[0] * (1. - friction), 0)
    sprite.speed = vectNorm(sprite.orientation) * sprite.speed
    sprite.orientation = unitVector(sprite.orientation)
    return ('wallStop', sprite.ID, partner.ID)

def killIfSlow(sprite, partner, game, limitspeed=1):
    """ Take a decision based on relative speed. """
    if sprite.is_static:
        relspeed = partner.speed
    elif partner.is_static:
        relspeed = sprite.speed
    else:
        relspeed = vectNorm((sprite._velocity()[0] - partner._velocity()[0],
                             sprite._velocity()[1] - partner._velocity()[1]))
    if relspeed < limitspeed:
        return killSprite(sprite, partner, game)

def killIfFromAbove(sprite, partner, game):
    """ Kills the sprite, only if the other one is higher and moving down. """
    if (sprite.lastrect.top > partner.lastrect.top
        and partner.rect.top > partner.lastrect.top):

        game.kill_list.append(sprite)
        if not None in {sprite, partner}:
            return ('killIfFromAbove', sprite.ID, partner.ID)

def killIfAlive(sprite, partner, game):
    """ Perform the killing action, only if no previous collision effect has removed the partner. """
    if partner not in game.kill_list:
        return killSprite(sprite, partner, game)

def collectResource(sprite, partner, game): # FLAG
    """ Adds/increments the resource type of sprite in partner """
    assert isinstance(sprite, Resource)
    r = sprite.resourceType
    partner.resources[r] = max(-1, min(partner.resources[r]+sprite.value, game.resources_limits[r]))
    killSprite(sprite, partner, game)
    # args = {'resource':r, 'value':sprite.value, 'limit':game.resources_limits[r]}
    return ('collectResource' , sprite.ID, partner.ID)

def changeResource(sprite, partner, resourceColor, game, resource, value=1, limit=None):
    """ Increments a specific resource type in sprite """
    sprite.resources[resource] = max(-1, min(sprite.resources[resource]+value, game.resources_limits[resource]))
    # NOTE: partner is the color of the resource (see _eventHandling() in core.py)
    args = {'resource':resource, 'value':value, 'limit':game.resources_limits[resource]}
    return ('changeResource', sprite.ID, partner.ID, args)

def changeScore(sprite, partner, game, value):
    game.score += value
    # print "score", game.score
    args = {'value': value}
    return ('changeScore', sprite.ID, partner.ID, args)

def spawnIfHasMore(sprite, partner, game, resource, stype, limit=1):
    """ If 'sprite' has more than a limit of the resource type given, it spawns a sprite of 'stype'. """
    if sprite.resources[resource] >= limit:
        game._createSprite([stype], (sprite.rect.left, sprite.rect.top))
        # Note: returning the resource doesn't seem like something the agent should have access to, so we're not returning it.
        args = {'stype':stype}
        return ('spawnIfHasMore', sprite.ID, partner.ID, args) ### NOTE - there is no default 'spawn' function we could return instead, but we should then make one

def killIfHasMore(sprite, partner, game, resource, limit=1):
    """ If 'sprite' has more than a limit of the resource type given, it dies. """
    if sprite.resources[resource] >= limit:
        return killSprite(sprite, partner, game)

def killIfOtherHasMore(sprite, partner, game, resource, limit=1):
    """ If 'partner' has more than a limit of the resource type given, sprite dies. """
    if partner.resources[resource] >= limit:
        # print "should kill sprite"
        return killSprite(sprite, partner, game)

def killIfHasLess(sprite, partner, game, resource, limit=1):
    """ If 'sprite' has less than a limit of the resource type given, it dies. """
    if sprite.resources[resource] <= limit:
        return killSprite(sprite, partner, game)

def killIfOtherHasLess(sprite, partner, game, resource, limit=1):
    """ If 'partner' has less than a limit of the resource type given, sprite dies. """
    if partner.resources[resource] <= limit:
        return killSprite(sprite, partner, game)

def wrapAround(sprite, partner, game, offset=0):
    """ Move to the edge of the screen in the direction the sprite is coming from.
    Plus possibly an offset. """
    if sprite.orientation[0] > 0:
        sprite.rect.left = offset * sprite.rect.size[1]
    elif sprite.orientation[0] < 0:
        sprite.rect.left = game.screensize[0] - sprite.rect.size[0] * (1 + offset)
    if sprite.orientation[1] > 0:
        sprite.rect.top = offset * sprite.rect.size[1]
    elif sprite.orientation[1] < 0:
        sprite.rect.top = game.screensize[1] - sprite.rect.size[1] * (1 + offset)
    sprite.lastmove = 0
    args = {'offset':offset}
    return ('wrapAround', sprite.ID, partner.ID, args)

def pullWithIt(sprite, partner, game):
    """ The partner sprite adds its movement to the sprite's. """
    if not oncePerStep(sprite, game, 'lastpull'):
        return ('pullWithIt', sprite.ID, partner.ID)

    tmp = sprite.lastrect
    v = unitVector(partner.lastdirection)
    sprite._updatePos(v, partner.speed * sprite.physics.gridsize[0])

    if isinstance(sprite.physics, ContinuousPhysics):
        sprite.speed = partner.speed
        sprite.orientation = partner.lastdirection
    sprite.lastrect = tmp

    return ('pullWithIt', sprite.ID, partner.ID)

def collideFromAbove(sprite, partner, game):
    """ Allows the sprite to pass through the bottom and collide with the top."""
    if (sprite.lastrect.top < partner.lastrect.top
        and sprite.lastrect.bottom < partner.lastrect.bottom) and sprite.solid and not sprite.jumping:
        pullWithIt(sprite, partner, game)
    elif (sprite.lastrect.bottom > partner.lastrect.bottom or
        sprite.lastrect.right < partner.lastrect.left or
        sprite.lastrect.left > partner.lastrect.right) and not(sprite.solid):
        sprite.solid = True
    return ('collideFromAbove', sprite.ID, partner.ID)

def killSpriteOnLanding(sprite, partner, game):
    """ kills the sprite given the collision condition from collide from above"""
    if (sprite.lastrect.top < partner.lastrect.top
        and sprite.lastrect.bottom < partner.lastrect.bottom
         and sprite.solid and not sprite.jumping):
        killSprite(sprite, partner, game)
    return ('killSpriteOnLanding', sprite.ID, partner.ID)

def teleportToExit(sprite, partner, game):
    try:
        e = random.choice(game.sprite_groups[partner.stype])
        args = {'stype':partner.stype}
    except:
        ## If partner doesn't have stype (the teleport exits) just don't move. Teleport to self.
        e = sprite
        args = {'stype':sprite.name}
    sprite.rect = e.rect
    sprite.lastmove = 0
    return ('teleportToExit', sprite.ID, partner.ID, args)

def killIfTooFast(sprite,partner,game,speed):
    if sprite.speed is not None:
        if abs(sprite.speed*sprite.orientation[1]) > speed:
            return killSprite(sprite, partner, game)
    else:
        return

def onLadder(sprite, partner, game):

    sprite.gravity = False
    if sprite.last_gravity:
        sprite.speed = 0
    return ('onLadder', sprite.ID, partner.ID)

def onRope(sprite, partner, game):
    sprite.gravity = False
    if sprite.last_gravity:
        sprite.speed = 0
    sprite.rope = True
    if not sprite.last_rope:
        sprite.jumping = False
    return ('onRope', sprite.ID, partner.ID)


# this allows us to determine whether the game has stochastic elements or not
stochastic_effects = [teleportToExit, windGust, slipForward, attractGaze, flipDirection]

# this allows is to determine which effects might kill a sprite
kill_effects = [killSprite, killIfSlow, transformTo, killIfOtherHasLess, killIfOtherHasMore, killIfHasMore, killIfHasLess,
                killIfFromAbove, killIfAlive]


def canActivateSwitch(sprite, partner, game):
    sprite.can_switch = True
    return ('canActivateSwitch', sprite.ID, partner.ID)

def cannotActivateSwitch(sprite, partner, game):
    sprite.can_switch = False
    return ('cannotActivateSwitch', sprite.ID, partner.ID)

# ---------------------------------------------------------------------
#     Sprite Induction
# ---------------------------------------------------------------------

sprite_types = [ResourcePack, Missile, Chaser, RandomNPC, \
                HorizontalAvatar, VerticalAvatar, FlakAvatar, ShootAvatar,
                RotatingAvatar, OrientedAvatar, SpawnPoint] 
                ## removed Flicker!!
                #removed Resource, Immovable, Passive, AStarChaser,AimedAvatar, AimedFlakAvatar, RotatingFlippingAvatar, NoisyRotatingFlippingAvatar


def getSpeed(params):
    """
    params = a dict mapping sprite attributes to values
    sprite = the VGDL sprite.
    """
    if 'speed' in params:
        return params['speed']
    else:
        return 1
        # default speed value

def getFleeing(params):
    """
    params = a dict mapping sprite attributes to values
    sprite = the VGDL sprite.
    """
    if 'fleeing' in params:
        return params['fleeing']
    else:
        return False

def getOrientation(params):
    """
    params = a dict mapping sprite attributes to values
    sprite = the VGDL sprite.
    """
    if 'orientation' in params:
        return params['orientation']

def getStype(params):
    """
    params = a dict mapping sprite attributes to values
    sprite = the VGDL sprite.
    """
    if 'stype' in params:
        return params['stype']

def getAngle(params):
    if 'angle_diff' in params:
        return params['angle_diff']

def getCooldown(params):
    if 'cooldown' in params:
        return params['cooldown']
    else:
        return 1

def getNoiseLevel(params):
    if 'noiseLevel' in params:
        return params['noiseLevel']
    return 0

def getTimeOut(params):
    if 'timeout' in params:
        return params['timeout']
    return float('inf')

def getSpritesByColor(game, color):
    unflattened = [s for s in game.sprite_groups.values() if s and s[0].colorName==color]
    return [item for sublist in unflattened for item in sublist]

def getObservedSpritesByColor(game, color):
    unflattened = [s for s in game.observation['trackedObjects'].values() if s and s[0].colorName==color]
    return [item for sublist in unflattened for item in sublist]

def chaserClosestTargets(sprite, game):
    if type(sprite.stype)==tuple:
        targets = getSpritesByColor(game, colorDict[str(sprite.stype)])
    else:
        targets = game.getSprites(sprite.stype)
    bestd = 1e100
    res = []
    for target in targets:
        d = sprite.physics.distance(sprite.rect, target.rect)
        if d < bestd and d>0:
            bestd = d
            res = [target]
        elif d == bestd:
            res.append(target)
    return res

def chaserMovesToward(sprite, game, target, fleeing):
    """ Find the canonical direction(s) which move toward
    the target. """
    res = []
    basedist = distance(sprite.rect, target.rect)
    for a in BASEDIRS:
        r = sprite.rect.copy()
        r = r.move(a)
        newdist = distance(r, target.rect)
        if fleeing and basedist < newdist:
            res.append(a)
        if not fleeing and basedist > newdist:
            res.append(a)
    return res

def findChaserClosestTargets(sprite, spritePrev, game):
    if sprite.stype in colorDict.values():
        targets = getObservedSpritesByColor(game, sprite.stype)
    elif type(sprite.stype)==tuple:
        targets = getObservedSpritesByColor(game, colorDict[str(sprite.stype)])
    else:
        ## This is the default VGDL behavior; if it gets to this case
        ## it's being called to do normal game-playing stuff.
        targets = game.sprite_groups[sprite.stype]
    bestd = 1e100
    res = []
    for target in targets:
        d = distance(spritePrev.rect, target.rect)
        if d < bestd and d>0:
            bestd = d
            res = [target]
        elif d == bestd:
            res.append(target)
    return res

def findChaserOptions(sprite, spritePrev, game, fleeing=True):
    options = []
    for target in findChaserClosestTargets(sprite, spritePrev, game):
        options.extend(chaserMovesToward(spritePrev, game, target, fleeing))
    options = [(spritePrev.rect.left/30.+o[0], spritePrev.rect.top/30.+o[1]) for o in options]
    return options

def setSpriteParams(param, sprite):
    """
    param = a dict mapping parameters to values
    sprite = the vgdl sprite
    """
    for p in param:
        if p == "speed":
            sprite.speed = param[p]
        elif p == "fleeing":
            sprite.fleeing = param[p]
        elif p == "orientation":
            sprite.orientation = param[p]
        elif p == "stype":
            sprite.stype = param[p]
        elif p == "cooldown":
            sprite.cooldown = param[p]

def updateOptions(game, sprite_type_tuple, current_sprite, action=None, params={}, missileOrientationClustering=False, allMovement=False):
    """
    This method gets all of the parameter information from the params variable
    instead of directly accessing the parameters in current_sprite.
    game - current game object
    sprite_type - the sprite type class hypothesis
    current_sprite - the current sprite object. Note: sometimes we use the actual sprite objects from the game,
        but we use it as a shell object so that we can run normal update functions using fake params we put in temporarily
    params - inferred params of the sprite. A dict mapping parameters (as strings) to their values.
    The default value of params is an empty dictionary - if that's the value passed, then the method will
    assume default values for each attribute.
    """
    appearance_predictions = []
    orientation_options = {(0, 0): 1.0}
    position_options = {(current_sprite.rect.left, current_sprite.rect.top): 1.0}
    sprite_type = sprite_type_tuple[1]
    if action==None:
        action=0

    if sprite_type in [Immovable, Passive, ResourcePack, Resource, 'OTHER']:
        return ({(current_sprite.rect.left, current_sprite.rect.top): 1.}, 
               {(current_sprite.rect.left, current_sprite.rect.top): 1.}, 
               orientation_options,
               appearance_predictions) ##object stays in position

    elif sprite_type == Flicker:
        timeout = getTimeOut(params)
        if game.time >= timeout:
            return {}, {}, {}, []
        return position_options, position_options, orientation_options, appearance_predictions

    # Chaser
    elif sprite_type == Chaser:
        speed = getSpeed(params)
        fleeing = getFleeing(params)
        targetColor = getStype(params)
        cooldown = getCooldown(params)
        realLastmove = int(current_sprite.lastmove)
        current_sprite.lastmove +=1 ## to account for the fact that the normal update() function for a sprite runs before the calculateActiveMovement fn
        realCooldown = int(current_sprite.cooldown)
        current_sprite.cooldown = cooldown
        try:
            targetName = [k for k in game.sprite_groups.keys() if game.sprite_groups[k] and game.sprite_groups[k][0].colorName==targetColor][0]
            targets = game.sprite_groups[targetName]
        except:
            targets = []

        options = []
        position_options = {}

        try:
            for target in targets:
                options.extend(chaserMovesToward(current_sprite, game, target, fleeing))
            if len(options) == 0:
                options = BASEDIRS

            for option in options:
                left, top = current_sprite.physics.calculateActiveMovement(current_sprite, option, speed=speed, 
                    allMovement=allMovement)
                if (left, top) in position_options.keys():
                    position_options[(left, top)] += 1.0/len(options)
                else:
                    position_options[(left, top)] = 1.0/len(options)

        except AttributeError: # deals with following error: 'Immovable' object has no attribute 'stype'
            position_options = {(current_sprite.rect.left, current_sprite.rect.top): 1.}

        current_sprite.cooldown = realCooldown
        current_sprite.lastmove = realLastmove
        return position_options, position_options, orientation_options, appearance_predictions

    # Random NPC
    elif sprite_type == RandomNPC:

        realCooldown = int(current_sprite.cooldown)
        speed, cooldown = getSpeed(params), getCooldown(params)
        current_sprite.cooldown = cooldown
        # current_sprite.lastmove -= 1 # see VGDL update function... this is actually necessary
        position_options = {}

        for option in BASEDIRS:
            left, top = current_sprite.physics.calculateActiveMovement(current_sprite, option, speed=speed, 
                allMovement=allMovement)

            if (left, top) in position_options.keys():
                position_options[(left, top)] += 1.0/len(BASEDIRS)
            else:
                position_options[(left, top)] = 1.0/len(BASEDIRS)

        current_sprite.cooldown = realCooldown
        # current_sprite.lastmove += 1
        return position_options, position_options, orientation_options, appearance_predictions

    # Missile or OrientedSprite
    elif sprite_type == Missile:
        # if not current_sprite.is_static and not current_sprite.only_active:
            # NOTE: we might want to consider having is_static and only_active be
            # parameters that we have to infer, rather than things we get for free.
            # (i.e. make these fields in the params variable)
        speed = getSpeed(params)
        orientation = getOrientation(params)
        cooldown = getCooldown(params)
        realCooldown = int(current_sprite.cooldown)
        current_sprite.cooldown = cooldown

        realLastmove = int(current_sprite.lastmove)
        current_sprite.lastmove +=1

        coords = current_sprite.physics.calculatePassiveMovementGivenParams(current_sprite, speed, orientation, 
            allMovement=allMovement)
        # If object has speed = 0 or no 'orientation' attribute
        position_options, clustered_position_options = {}, {}
        if coords == None:
            return position_options, position_options, orientation_options, appearance_predictions

        position_options[(coords[0], coords[1])] = 1.

        if missileOrientationClustering:

            epsilon_prob = 0.005
            clustered_position_options[(coords[0], coords[1])] = .5 + epsilon_prob
            #flip orientation
            orientation = (orientation[0]*-1, orientation[1]*-1)
            coords = current_sprite.physics.calculatePassiveMovementGivenParams(current_sprite, speed, orientation,
                allMovement=allMovement)
            if (coords[0], coords[1]) in clustered_position_options.keys():
                clustered_position_options[(coords[0], coords[1])] += .5 - epsilon_prob
            else:
                clustered_position_options[(coords[0], coords[1])] = .5 - epsilon_prob

        current_sprite.cooldown = realCooldown        
        current_sprite.lastmove = realLastmove
        return position_options, clustered_position_options, orientation_options, appearance_predictions

    elif sprite_type in [MovingAvatar, FlakAvatar, ShootAvatar, HorizontalAvatar, VerticalAvatar]:
        if action in sprite_type.availableActions:
            dx,dy = actionToDir[keyPressToAction[action]]
        else:
            dx,dy = (0,0)

        if current_sprite.speed is not None:
            speed = current_sprite.speed
        else:
            speed = 0

        next_pos = current_sprite.rect.left + speed*dx*game.block_size, current_sprite.rect.top + speed*dy*game.block_size
        position_options = {next_pos: 1.}
        
        if sprite_type in [FlakAvatar]:
            stype = getStype(params)
            ## get type of sprite that should appear and its location; return that as the third dict.
            ## then get the return val of this one and add it to the game.sprite_appearance_predictions
            appearance_predictions = [(stype, current_sprite.rect.left, current_sprite.rect.top)]
            return position_options, position_options, orientation_options, appearance_predictions
        elif sprite_type in [ShootAvatar]:
            stype = getStype(params)
            u = unitVector(current_sprite.orientation)
            left, top = current_sprite.lastrect.left+u[0]*current_sprite.lastrect.size[0], current_sprite.lastrect.top+u[1]*current_sprite.lastrect.size[1]
            appearance_predictions = [(stype, left, top)]

            ## ShootAvatar has orientation drawn on it, so we can query directly
            if not action:
                orientation_options = {current_sprite.orientation:1.}
            else:
                orientation_options = {(dx,dy):1.}

            return position_options, position_options, orientation_options, appearance_predictions

        else:
            return position_options, position_options, orientation_options, []

    elif sprite_type == AimedAvatar:
        stype = getStype(params)
        angle_diff = getAngle(params)
        action = actionToDir[keyPressToAction[action]]
        if action in [UP, DOWN]:
            if action == UP:
                angle = -angle_diff
            elif action == DOWN:
                angle = angle_diff

            orientation = (current_sprite.orientation[0]*cos(angle)-current_sprite.orientation[1]*sin(angle),
                           current_sprite.orientation[0]*sin(angle)+current_sprite.orientation[1]*cos(angle))
        else:
            orientation = current_sprite.orientation

        orientation_options = {normalizeVec(orientation): 1.0}
        position_options = {(current_sprite.rect.left, current_sprite.rect.top): 1.0}
        
        u = unitVector(orientation)
        left, top = current_sprite.lastrect.left+u[0]*current_sprite.lastrect.size[0], current_sprite.lastrect.top+u[1]*current_sprite.lastrect.size[1]
        appearance_predictions = [(stype, left, top)]
        return position_options, position_options, orientation_options, appearance_predictions

    elif sprite_type == AimedFlakAvatar:
        stype = getStype(params)
        angle_diff = getAngle(params)

        speed = current_sprite.speed
        if speed is None:
            speed = 0

        direction = actionToDir[keyPressToAction[action]]
        
        if direction in [LEFT, RIGHT]:
            dx, dy = direction
        else:
            dx, dy = (0, 0)

        if direction in [UP, DOWN]:
            if direction == UP:
                angle = -angle_diff
            elif direction == DOWN:
                angle = angle_diff

            orientation = (current_sprite.orientation[0]*cos(angle)-current_sprite.orientation[1]*sin(angle),
                           current_sprite.orientation[0]*sin(angle)+current_sprite.orientation[1]*cos(angle))
        else:
            orientation = current_sprite.orientation

        orientation_options = {normalizeVec(orientation): 1.0}

        next_pos = (current_sprite.rect.left + speed*dx*game.block_size, 
                        current_sprite.rect.top + speed*dy*game.block_size)
        position_options = {next_pos: 1.}

        u = unitVector(orientation)
        left, top = current_sprite.lastrect.left+u[0]*current_sprite.lastrect.size[0], current_sprite.lastrect.top+u[1]*current_sprite.lastrect.size[1]
        appearance_predictions = [(stype, left, top)]
        return position_options, position_options, orientation_options, appearance_predictions
    
    elif sprite_type == RotatingAvatar:
        direction = actionToDir[keyPressToAction[action]]
        speed = 0
        if direction == UP:
            speed = 1
        if direction == DOWN:
            speed = -1

        orientation = current_sprite.orientation
        if orientation in BASEDIRS:
            if direction == LEFT:
                i = BASEDIRS.index(orientation)
                orientation = BASEDIRS[(i + 1) % len(BASEDIRS)]
            if direction == RIGHT:
                i = BASEDIRS.index(orientation)
                orientation = BASEDIRS[(i - 1) % len(BASEDIRS)] 
            orientation_options = {normalizeVec(orientation): 1.0}

        next_pos = (current_sprite.rect.left+orientation[0]*speed*game.block_size, 
                        current_sprite.rect.top+orientation[1]*speed*game.block_size)
        position_options = {next_pos: 1.0}
        
        appearance_predictions = []

    ## If you add any more types, check when their self.lastmove is incremented and copy that logic here.
    ## See Chaser update for an example.
    
        return position_options, position_options, orientation_options, appearance_predictions

    elif sprite_type in [RotatingFlippingAvatar, NoisyRotatingFlippingAvatar]:
        noiseLevel = 0

        if sprite_type == NoisyRotatingFlippingAvatar:
            noiseLevel = getNoiseLevel(params)

        direction = actionToDir[keyPressToAction[action]]
        speed = 0
        if direction == UP:
            speed = 1

        orientation = current_sprite.orientation
        if orientation in BASEDIRS:
            if direction == LEFT:
                i = BASEDIRS.index(orientation)
                orientation = BASEDIRS[(i + 1) % len(BASEDIRS)]
            elif direction == RIGHT:
                i = BASEDIRS.index(orientation)
                orientation = BASEDIRS[(i - 1) % len(BASEDIRS)] 
            elif direction == DOWN:
                i = BASEDIRS.index(orientation)
                orientation = BASEDIRS[(i + 2) % len(BASEDIRS)]  
            orientation_options = {normalizeVec(d) : noiseLevel for d in [UP, DOWN, LEFT, RIGHT]}
            orientation_options[normalizeVec(orientation)] += 1-noiseLevel

        curr_pos = (current_sprite.rect.left, current_sprite.rect.top)
        next_pos = (current_sprite.rect.left+orientation[0]*speed*game.block_size, 
                        current_sprite.rect.top+orientation[1]*speed*game.block_size)
        position_options = {curr_pos: 3*noiseLevel/4., next_pos: noiseLevel/4.}
        position_options[next_pos] += 1-noiseLevel
        
        appearance_predictions = []

        return position_options, position_options, orientation_options, appearance_predictions

    elif sprite_type == OrientedAvatar:
        orientation = current_sprite.orientation
        next_pos = current_sprite.rect.left, current_sprite.rect.top
        speed = current_sprite.speed
        if speed is None:
            speed = 0

        if action:
            orientation = actionToDir[keyPressToAction[action]]
            next_pos = (current_sprite.rect.left+orientation[0]*speed*game.block_size, 
                            current_sprite.rect.top+orientation[1]*speed*game.block_size)
        orientation_options = {normalizeVec(orientation): 1.0}
        position_options = {next_pos: 1.0}
        appearance_predictions = []
        return position_options, position_options, orientation_options, appearance_predictions
    
    elif sprite_type in [SpawnPoint]:
        next_pos = current_sprite.rect.left, current_sprite.rect.top
        position_options = {next_pos: 1.}
        stype = getStype(params)
        cooldown = getCooldown(params)
        if (game.time+1)%cooldown==0:
            appearance_predictions = [(stype, current_sprite.rect.left, current_sprite.rect.top)]
        else:
            appearance_predictions = []
        return position_options, position_options, orientation_options, appearance_predictions

    # Catches objects that can't be Oriented Sprite and Missile types b/c fails the if-statement
    return {}, {}, {}, []

def initializeDistribution(sprite_types, objectColors):
    """
    Creates a uniform distribution over all parameter combinations
    """
    catch_all_prior = .000001
    outList = []
    for sprite_type in sprite_types:
            paramList = initializeDistributionArgs(sprite_type, objectColors)
            for element in itertools.product(*paramList):
                outList.append(tuple([('vgdlType', sprite_type)]+sorted(element)))
    initial_distribution = {k:1.0 for k in outList}
    initial_distribution[(('vgdlType', 'OTHER'), )] = catch_all_prior
    return initial_distribution


def initializeDistributionArgs(sprite_type, objectColors):
    """
    Given a sprite type, this returns a distribution over the kinds of args (parameters) belonging
    to that sprite type.
    """

    def initializeSpeed():
        # speedValues = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.,
        # 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1]
        speedValues = [.3, .5, .6, 1.0, 2.0]
        return [('speed', v) for v in speedValues]

    def initializeOrientation():
        orientationValues = [LEFT, RIGHT, UP, DOWN]
        return [('orientation', v) for v in orientationValues]
    
    def initializeFleeing():
        fleeingValues = [True, False]
        return [('fleeing', v) for v in fleeingValues]

    def initializeStype():
        stypeValues = objectColors
        return [('stype', v) for v in stypeValues]

    def initializeCooldown():
        stypeValues = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        return [('cooldown', v) for v in stypeValues]

    def initializeSpawnCooldown():
        stypeValues = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        return [('spawnCooldown', v) for v in stypeValues]

    def initializeSingleton():
        return [('singleton', v) for v in [True, False]]

    def initializeAngle():
        return [('angle_diff', v) for v in [0.05, 0.707]]

    def initializeNoiseLevel():
        return [('noiseLevel', v) for v in [0.0, 0.1]]

    def initializeTimeOut():
        return [('timeout', v) for v in [5]] #[1, 5, 10, 15, 20, 25]

    paramList = []
    if sprite_type.__name__ in spriteToParams.keys():
        spriteParams = spriteToParams[sprite_type.__name__]
    else:
        spriteParams = []

    for s in spriteParams:
        if s == "speed":
            paramList.append(initializeSpeed())
        elif s == "fleeing":
            paramList.append(initializeFleeing())
        elif s == "orientation":
            paramList.append(initializeOrientation())
        elif s=='stype':
            paramList.append(initializeStype())
        elif s=='cooldown':
            paramList.append(initializeCooldown())
        elif s=='spawnCooldown':
            paramList.append(initializeSpawnCooldown())
        elif s=='singleton':
            paramList.append(initializeSingleton())
        elif s=='angle_diff':
            paramList.append(initializeAngle())
        elif s=='noiseLevel':
            paramList.append(initializeNoiseLevel())
        elif s=='timeout':
            paramList.append(initializeTimeOut())

    return paramList

def distributionInitSetup(game, spriteID):
    """
    Does setup for initializing distribution
    """ 
    objectColors = list(set([s.colorName for sublist in game.sprite_groups.values() for s in sublist])) ## all visible colors
    game.spriteDistribution[spriteID] = initializeDistribution(sprite_types, objectColors) # Indexed by object ID
    game.object_token_spriteDistribution[spriteID] = initializeDistribution(sprite_types, objectColors) # Indexed by object ID

    # if spriteID not in game.all_objects.keys():
        # game.all_objects[spriteID] = game.getAllObjects()[spriteID]

    game.movement_options[spriteID] = {k:{} for k in game.spriteDistribution[spriteID].keys()}
    game.object_token_movement_options[spriteID] = {k:{} for k in game.spriteDistribution[spriteID].keys()}
    game.sprite_appearance_predictions[spriteID] = {k:[] for k in game.spriteDistribution[spriteID].keys() if 'Avatar' in str(k[0][1]) or 'SpawnPoint' in str(k[0][1])}
    # TODO: do we need to be specific to Avatar like this? Try not doing that and see if it breaks
    game.orientation_options[spriteID] = {k:{} for k in game.spriteDistribution[spriteID].keys() if 'Avatar' in str(k[0][1])}

def filterTheories(scoreAndTheoryTuples, percentile, max_num):
    import numpy as np
    ## Returns the max_num theories that are at percentile or greater, given their score.
    scoreAndTheoryTuples = sorted(scoreAndTheoryTuples, key=lambda x: x[0], reverse=True)
    cutoff = np.percentile([s[0] for s in scoreAndTheoryTuples], percentile)
    return [s for s in scoreAndTheoryTuples if s[0]>=cutoff][0:max_num]

def updateAllOptions(game, gamePrev, action=None):
    # was spriteInduction step 2
    ## See the update options for each sprite type the sprite could be
    if game.time==game.lastUpdateOptionsTime:
        return

    game.lastUpdateOptionsTime=game.time

    objects = gamePrev.getAllObjects()
    for sprite in [s for s in game.spriteDistribution.keys() if s in objects.keys()]: # Keys are the IDs of the game objects
        for param_combination in game.spriteDistribution[sprite].keys():              # Check each potential sprite type
            if game.spriteDistribution[sprite][param_combination]> 0:                 # Make sure sprite_type is an option for sprite, and sprite is not killed
                # sprite_obj = objects[sprite]["sprite"]
                sprite_obj = objects[sprite]

                sprite_type = param_combination[0]
                attributeDict = {k:v for k,v in param_combination[1:]}

                # Get potential next positions for sprite if it were that sprite type
                ##we are sprite_obj, and we are updating the options for where it could be next contingent on its being 'sprite_type'
                # given a set of potential attribute values, update the movement options
                # for this attribute tuple (i.e. candidate set of parameters)

                ## missileOrientationClustering: considers left/right and up/down to be equivalent options in the likelihood
                ## so that when objects bounce off walls it doesn't dramatically reduce the probability that they are straight-moving
                ## objects
                game.object_token_movement_options[sprite][param_combination], \
                game.movement_options[sprite][param_combination], \
                orientation_options, \
                appearance_prediction = \
                updateOptions(gamePrev, sprite_type, sprite_obj, action=action, params=attributeDict, missileOrientationClustering=True)
                if param_combination in game.orientation_options[sprite].keys():
                    game.orientation_options[sprite][param_combination] = orientation_options

                if param_combination in game.sprite_appearance_predictions[sprite].keys():
                    game.sprite_appearance_predictions[sprite][param_combination].extend(appearance_prediction)

def spriteInduction(game, step, action=None, specificSpritesToUpdate=[]):
    """
    An explanation of important data structures used in this function:
    game = a BasicGame object
    game.spriteDistribution is a dictionary of the following form:
    {sprite: {sprite_type: {'prob': PROBABILITY OF SPRITE TYPE, 'args': {'speed': {A VALUE OF SPEED: PROBABILITY OF THAT VALUE}}},
    ...}, ...}
    game.spriteDistribution tells you the probability of a sprite being being a particular type. It also
    tells you the probability distribution over values for each parameter (e.g. speed, orientation).
    game.movement_options is a dictionary of the following form:
    {sprite: {sprite_type: {attributeTuple: {sprite position: probability of that sprite position},...},
    ...}, ...}
    game.movement_options tells you the probability of a sprite being in a particular position, given a certain
    setting of its attributes (e.g. specific values for speed, orientation, etc.) and also given sprite type.
    """

    if action==None:
        action = 0

    if step==1:
        ## Sprite Induction Part 1:
        ## every time you act, make sure there aren't new objects
        ## if there are, update spriteDistribution etc.
        objects = game.getAllObjects()
        newSprites = []
        for spriteID in objects:
            # if spriteID not in game.spriteDistribution:
            newSprites.append(spriteID)
            game.all_objects[spriteID] = objects[spriteID]
            distributionInitSetup(game, spriteID)
    elif step==4:
        ## Get all parameterizations of sprite type that could have led to the sprites in specificSpritesToUpdate
        ## to their current positions
        scoreAndTheoryTuples = []

        for sprite in specificSpritesToUpdate:
            left, top = sprite.rect.left, sprite.rect.top
            neighbors = [(left, top), (left-30, top), (left+30, top), (left, top-30), (left, top+30)]
            try:
                if game.sprite_appearances and any([(s.rect.left, s.rect.top) in neighbors for s in game.sprite_appearances]) and \
                        sprite.ID in game.sprite_appearance_predictions:
                    # print "first case"
                    for k,v in game.sprite_appearance_predictions[sprite.ID].items():
                        if any([(appearance.colorName, appearance.rect.left, appearance.rect.top) in v for appearance in game.sprite_appearances]):
                            scoreAndTheoryTuples.append((0,k))
                else:
                    # print "normal case"
                    ## Normal case. Update hypotheses related to movement types.
                    for k in game.movement_options[sprite.ID]:
                        if len(game.observation['trackedObjects'][sprite.colorName])>1 and ( ('singleton', True) in k or 'Avatar' in str(k[0][1]) ):
                            # too many objects on the screen to be possible
                            continue
                        if (sprite.rect.left, sprite.rect.top) in game.movement_options[sprite.ID][k]: 
                            if k in game.orientation_options[sprite.ID]:
                                if normalizeVec(sprite.orientation) in game.orientation_options[sprite.ID][k]:
                                    scoreAndTheoryTuples.append((0,k))
                            else:
                                scoreAndTheoryTuples.append((0,k))
            except:
                print "something broke in spriteInduction (probably has to do with cannon)"
                embed()
                    
        reasonableHypotheses = list(set([s[1] for s in scoreAndTheoryTuples]))
        return reasonableHypotheses

    ## Reset ignoreList so that next time around you do inference.
    game.ignoreList = []
    return

def softmax(w, t = 1.0):
    e = np.exp(np.array(w) / t)
    dist = e / np.sum(e)
    return dist

def selectObjectGoal(rle, unknown_colors, all_colors, exclude_colors, method):
    def dist(a,b):
        return abs(a[0]-b[0])+abs(a[1]-b[1])

    epsilon = .2
    unknown_colors = [c for c in unknown_colors if c not in exclude_colors]
    safe_colors = [c for c in all_colors if c not in exclude_colors]
    if method=='random_then_nearest':
        if len(unknown_colors)>0 and random.random()>epsilon:
            print "selecting an unknown color"
            object_color = random.choice(unknown_colors)
        else:
            # in case we've interacted with everything once but want to randomly try things again
            print "sometimes with probability", epsilon, "we select randomly from all safe colors. This just happened."
            object_color = random.choice(safe_colors)
        choices = [item for sublist in rle._game.sprite_groups.values() for item in sublist if colorDict[str(item.color)]==object_color]
        avatar_loc = rle._rect2pos(rle._game.sprite_groups['avatar'][0].rect)
        choices = [(dist(rle._rect2pos(c.rect), avatar_loc), c) for c in choices]
        choices = sorted(choices, key=lambda c:c[0])
        nearest_dist = min([c[0] for c in choices])
        nearest = [c for c in choices if c[0]==nearest_dist]
        return random.choice(nearest)[1]
