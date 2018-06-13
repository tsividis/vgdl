"""Module for modifying hypotheses with alternative goals"""
import itertools
from vgdl.ontology import Resource, ResourcePack
from vgdl.colors import colorDict
from util import ALNUM
from vgdl.theory_template import (Precondition, InteractionRule, TerminationRule, TimeoutRule,
                                  SpriteCounterRule, MultiSpriteCounterRule, Theory, Game, writeTheoryToTxt, generateSymbolDict,
                                  generateTheoryFromGame, expandLine, expandSprites, proposePredicates, getRuleSetsForClassPairPredicate,
                                  interateThresholds)


def createNewClassInfo(theory):
    """creates an unused class name and color"""
    existing_classes = [key for key in theory.classes if key[0] == 'c']
    max_num = max([int(c[1:]) for c in existing_classes])
    class_num = max_num+1
    new_class_name = 'c'+str(class_num)
    used_colors = theory.spriteObjects.keys()
    color = next((c for c in colorDict.itervalues() if c not in used_colors), None)
    return new_class_name, color


def constructTargetTheory(theory):
    """Creates a copy of the theory with a new class, where the avatar's goal is to collect all objects of this class"""
    h = theory.copy()
    new_name, color = createNewClassInfo(h)
    h.addSpriteToTheory(new_name, color, vgdlType=ResourcePack)
    h.interactionSet.append(InteractionRule('killSprite', new_name, 'avatar', {}, set()))
    h.terminationSet.append(SpriteCounterRule(new_name, 0, True))
    return h


def constructKillSelfTheory(theory):
    """Creates a copy of the theory with a new class, where the avatar's goal is to die"""
    h = theory.copy()
    h.terminationSet.remove(SpriteCounterRule('avatar', 0, False))
    h.terminationSet.append(SpriteCounterRule('avatar', 0, True))
    return h


def constructTouchNothingEverywhereTheory(theory):
    """Creates a copy of the theory with a new class, where the avatar's goal is to move everywhere but not touch anything"""
    #REVIEW: Does planner try and optimize score? I think it would be more interesting to instead have it try and touch as many 
    #        blank squares as possible but still win the original game
    h = theory.copy()

    new_name, color = createNewClassInfo(h)
    h.addSpriteToTheory(new_name, color, vgdlType=ResourcePack)
    h.interactionSet = [rule for rule in h.interactionSet 
                        if not(rule.slot1 == 'avatar' or rule.slot2 == 'avatar' or
                        rule.slot1 == 'EOS' and rule.slot2 == new_name)]
    for (o1, o2) in itertools.product(['avatar'], h.classes.keys()):
        if o2 == new_name:
            continue
        kill_rule = InteractionRule('killSprite', o1, o2, {}, set())
        h.interactionSet.append(kill_rule)

    h.interactionSet.append(InteractionRule('killSprite', new_name, 'avatar', {}, set()))

    h.terminationSet = [rule for rule in h.terminationSet if rule.termination.name != 'SpriteCounter' and
                        rule.termination.name != 'MultiSpriteCounter'] #FIXME: might not work
    h.terminationSet.append(SpriteCounterRule('avatar', 0, False))
    h.terminationSet.append(SpriteCounterRule(new_name, 0, True))

    #TODO: have to place new_name object everywhere

    return h

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
        rle._obstypes[skey] = [rle._sprite2state(sprite, oriented=False)
                                    for sprite in ss]
    return
