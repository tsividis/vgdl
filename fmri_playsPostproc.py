# post-processing of data to extract quantities for convenient analysis

from pymongo import MongoClient
import pprint
import random
from datetime import datetime
import time

import json
import sys
import uuid
import csv
import socket
from collections import defaultdict
from vgdl import core
from vgdl.core import VGDLParser, fMRI_screensize
from vgdl.core import keyPresses as keyNames
from IPython import embed
from vgdl.main_agent import Agent
import cPickle, cloudpickle
import utils
from vgdl.theory_template import TimeoutRule, SpriteCounterRule, MultiSpriteCounterRule, NoveltyRule, generateTheoryFromGame
from fmri_agentReplay import chelsea_fix_states_avatar_only

import pygame

# USAGE: python fmri_playsPostproc.py.py [subj_id] [run_id*] [block_id*] [instance_id*] [play_id*]
#        python fmri_playsPostproc.py.py [subj_id] [game_name]
#        python fmri_playsPostproc.py.py [subj_id] [run_id] [game_name]
# * - optional
# copied from fmri_makeMovie.py

client = utils.get_mongo_client()

db = client['heroku_7lzprs54']

def print_keystates(keystates):
    ts0 = keystates[1]['ts']
    for t in range(len(keystates)):
        if t == 0:
            continue
        keystate = keystates[t]['keystate']
        kk = []
        for key in range(len(keystate)):
            if keystate[key]:
                kk.append(key)
        print str(t) + ' -- ' + str(keystates[t]['ts'] - ts0) + ': ' + str(kk)



def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    assert False


def get_theory_stype_to_state_stype_dict(theory, state):
    color_to_theory_stype = {s.color: s.className for s in theory.spriteSet}
    color_to_state_stype = {list(ss.values())[0]['colorName']: key for key, ss in state['objects'].iteritems() if len(ss) > 0}
    theory_stype_to_state_stype = {}
    for color, theory_stype in color_to_theory_stype.iteritems():
        if color in color_to_state_stype:
            state_stype = color_to_state_stype[color]
            theory_stype_to_state_stype[theory_stype] = state_stype
    return theory_stype_to_state_stype


def get_active_sprites_from_objects(state, stype):
    # omits overlapping sprites -- see TODO in getFullState() in core.py...
    if stype in state['objects'].keys():
        objs = state['objects'][stype]
    else:
        objs = []
    return objs


def get_active_sprites_from_list(state, stype):
    # include sprites there were killed; no way to cross-reference them with the kill_list from here...
    objs = [s for s in state['list'] if s.startswith(stype)] 
    return objs


def get_sprite_counter_rule_sprite_count(stype, state, theory_stype_to_state_stype, get_active_sprites):
    if stype not in theory_stype_to_state_stype:
        # the sprite type is not present in the state -> 0 count
        return 0
    objs = get_active_sprites(state, theory_stype_to_state_stype[stype])
    return len(objs)


def get_multi_sprite_counter_rule_sprite_count(stypes, state, theory_stype_to_state_stype, get_active_sprites):
    #stypes = [theory_stype_to_state_stype[stype] for stype in term.termination.stypes if stype in theory_stype_to_state_stype.keys()]
    n_stypes = sum([len(get_active_sprites(state, theory_stype_to_state_stype[stype])) for stype in stypes if stype in theory_stype_to_state_stype])
    return n_stypes


def get_starting_stype_n(theory, state, get_active_sprites):
    theory_stype_to_state_stype = get_theory_stype_to_state_stype_dict(theory, state)

    # copy pasted from WBP.y __init__
	## Used to track subgoals. If we start planning in an episode with, say, 8 object tokens of a type we want to get to 0 of, subgoal progress occurs if any node we open has <8 of them.
    starting_stype_n = {}
    for term in theory.terminationSet:
        if isinstance(term, SpriteCounterRule):
            #stype = theory_stype_to_state_stype.get(term.termination.stype)
            stype = term.termination.stype
            n_stypes = get_sprite_counter_rule_sprite_count(stype, state, theory_stype_to_state_stype, get_active_sprites)
            starting_stype_n[stype] = n_stypes
        elif isinstance(term, MultiSpriteCounterRule):
            stypes = term.termination.stypes
            n_stypes = get_multi_sprite_counter_rule_sprite_count(stypes, state, theory_stype_to_state_stype, get_active_sprites)
            starting_stype_n[tuple(stypes)] = n_stypes

    return starting_stype_n


def check_for_subgoal_progress(theory, prev_state, state, get_active_sprites):
    # Get initial sprites type counts (from previous state)
    starting_stype_n = get_starting_stype_n(theory, prev_state, get_active_sprites)

    theory_stype_to_state_stype = get_theory_stype_to_state_stype_dict(theory, state)

    # Get current sprite type counts (from current state), see if any relevant counts decreased
    # copy pasted from WBP.py check_node_for_subgoal_progress
    for term in theory.terminationSet:
        if isinstance(term, SpriteCounterRule) and term.termination.win==True:
            stype = term.termination.stype
            n_stypes = get_sprite_counter_rule_sprite_count(stype, state, theory_stype_to_state_stype, get_active_sprites)
            if stype in starting_stype_n.keys() and starting_stype_n[stype] > n_stypes:
                return True

        elif isinstance(term, MultiSpriteCounterRule) and term.termination.win==True:
            stypes = term.termination.stypes
            n_stypes = get_multi_sprite_counter_rule_sprite_count(stypes, state, theory_stype_to_state_stype, get_active_sprites)
            if tuple(stypes) in starting_stype_n.keys() and starting_stype_n[tuple(stypes)] > n_stypes:
                return True

    return False


def playsPostproc(subj_id):
    query = {'subj_id': subj_id}

    if len(sys.argv) > 2:
        if is_int(sys.argv[2]):
            query['run_id'] = int(sys.argv[2])
        else:
            assert len(sys.argv) == 3
            query['game_name'] = sys.argv[2]
    if len(sys.argv) > 3:
        if is_int(sys.argv[3]):
            query['block_id'] = int(sys.argv[3])
        else:
            assert len(sys.argv) == 4
            query['game_name'] = sys.argv[3]
    if len(sys.argv) > 4:
        if is_int(sys.argv[4]):
            query['instance_id'] = int(sys.argv[4])
        else:
            assert len(sys.argv) == 5
            query['game_name'] = sys.argv[4]
    if len(sys.argv) > 5:
        if is_int(sys.argv[5]):
            query['play_id'] = int(sys.argv[5])
        else:
            assert len(sys.argv) == 6
            query['game_name'] = sys.argv[5]
    if len(sys.argv) > 6:
        query['game_name'] = sys.argv[6]

    plays = db.plays.find(query, no_cursor_timeout=True).sort('start_time')

    print 'Running fmri_playsPostproc.py with query:'
    print query

    # TODO dedupe with fmri_empaReplay

    all_pairs = {}
    all_regressors = {}
    all_movie_names = {}

    for play in plays:
        subj = db.subjects.find_one({'subj_id': subj_id})
        game = subj['games'][play['game_id']]
        game_str = game['descs'][play['desc_id']]
        level_str = game['levels'][play['level_id']]
        assert game_str == play['game_str']
        assert level_str == play['level_str']
        assert game['name'] == play['game_name']

        print 'Computing plays_post for subj %s, run %d, block %d, instance %d, play %d: %s (%s), desc %d, level %d' % (play['subj_id'], play['run_id'], play['block_id'], play['instance_id'], play['play_id'], game['name'], game['fake_name'], play['desc_id'], play['level_id'])

        q = {'play_key': play['_id']}
        print q
        print db.empa_plays_post.count(q)
        if db.empa_plays_post.count(q) > 0:
            print '..........skipping: already computed'
            continue

        # get regressors
        q = {'play_key': play['_id']}
        print q
        print db.empa_regressors.count(q)
        assert db.empa_regressors.count(q) <= 1, 'Too many regressors!' 
        if db.empa_regressors.count(q) == 0:
            print 'skipping (e.g. Sokoban)'
            continue
        regs = db.empa_regressors.find(q).sort('ts', -1)
        reg = None
        for reg in regs:
            break # just take the latest one

        # get states
        zstates = play['zstates']
        states = core.VGDLParser.decompress(zstates)
        states = states['states'] # dummy dict

        zkeystates = play['zkeystates']
        keystates = core.VGDLParser.decompress(zkeystates)
        keystates = keystates['keystates'] # dummy dict

        # Fix game & state colors for subjects 12..32  ...
        chelsea_fix_states_avatar_only(states, game, subj_id, play)

        # load theories from disk
        with open(reg['regressors']['theory_filename'], 'r') as f:
            reg['regressors']['theory'] = cloudpickle.load(f)

        # load newTimeSteps i.e. basically finalTimeStepList from disk
        with open(reg['regressors']['newTimeStep_filename'], 'r') as f:
            reg['regressors']['newTimeStep'] = cloudpickle.load(f)

        # create object to hold play postprocessing data
        # similar to regressors (see fmri_empaReplay.py)
        play_post = {
            'play_key': play['_id'],
            'subj_id': play['subj_id'],
            'run_id': play['run_id'],
            'block_id': play['block_id'],
            'instance_id': play['instance_id'],
            'play_id': play['play_id'],
            'game_name': play['game_name'],
            'level_id': play['level_id'],
            'type': 'fmri_playsPostproc'
        }

        # hack to fix interaction_change_flag TODO undo once we re-run it
        #
        assert len(reg['regressors']['interaction_change_flag']) == len(reg['regressors']['theory'])
        for i in range(1, len(reg['regressors']['theory'])):
            prev_theory = reg['regressors']['theory'][i-1][0]
            curr_theory = reg['regressors']['theory'][i][0]
            interactionSetEqual = all(any(i1==i2 for i2 in prev_theory.interactionSet) for i1 in curr_theory.interactionSet)

            #if interactionSetEqual == reg['regressors']['interaction_change_flag'][i][0]:
            #    print 'sheeeeit'
            #    embed()
            #    time.sleep(10)

            reg['regressors']['interaction_change_flag'][i][0] = not interactionSetEqual

            if reg['regressors']['interaction_change_flag'][i][0] and not reg['regressors']['theory_change_flag'][i][0]:
                print 'ASSERT FAIL: interactions changed but theory didnt!'
                #embed()
        interaction_change_flag = reg['regressors']['interaction_change_flag']

        play_post['interaction_change_flag'] = interaction_change_flag

        # hack to fix termination set ... TODO undo once we re-run
        #
        assert len(reg['regressors']['termination_change_flag']) == len(reg['regressors']['theory'])
        for i in range(1, len(reg['regressors']['theory'])):
            prev_theory = reg['regressors']['theory'][i-1][0]
            curr_theory = reg['regressors']['theory'][i][0]
            termination_change_flag = set(prev_theory.terminationSet) != set(curr_theory.terminationSet)

            #if termination_change_flag != reg['regressors']['termination_change_flag'][i][0]:
            #    print 'sheeeeitttttttttt'
            #    embed()
            #    time.sleep(10)

            reg['regressors']['termination_change_flag'][i][0] = termination_change_flag 

            if reg['regressors']['termination_change_flag'][i][0] and not reg['regressors']['theory_change_flag'][i][0]:
                print 'ASSERT FAIL: terminations changed but theory didnt!'
                #embed()
        termination_change_flag = reg['regressors']['termination_change_flag']

        play_post['termination_change_flag'] = termination_change_flag


        # debug code -- checks if theory_change_flag always corresponds to sprite, interaction, or termination change
        # (it doesn't but very rarely -- see how we set it)
        '''
        for i in range(1, len(reg['regressors']['theory'])):
            tc = reg['regressors']['theory_change_flag'][i][0]
            sc = reg['regressors']['sprite_change_flag'][i][0]
            ic = reg['regressors']['interaction_change_flag'][i][0]
            tec = reg['regressors']['termination_change_flag'][i][0]
            if tc and not (sc or ic or tec):
                prev_theory = reg['regressors']['theory'][i-1][0]
                curr_theory = reg['regressors']['theory'][i][0]

                print 'ssheeeeeeeeeeeeeit'
                print 'prev'
                prev_theory.display()
                print 'curr'
                curr_theory.display()
                embed()
        '''

        # hack to fix likelihood and sum_lik TODO fix in EMPA
        #
        newTimeStep_flag = [False]
        likelihood = [float('nan')]
        sum_lik_play = [float('nan')]
        surprise = [float('nan')]
        t = 0
        finalTimeStepList = []
        for i in range(1, len(reg['regressors']['theory'])):
            while t < len(reg['regressors']['newTimeStep']) and reg['regressors']['newTimeStep'][t][1] < reg['regressors']['theory'][i][1]:
                t += 1

            if t < len(reg['regressors']['newTimeStep']) and reg['regressors']['newTimeStep'][t][1] == reg['regressors']['theory'][i][1]:
                newTimeStep_flag.append(True)
                finalTimeStepList.append(reg['regressors']['newTimeStep'][t][0])
            else:
                newTimeStep_flag.append(False)

            prev_theory = reg['regressors']['theory'][i-1][0]
            if len(finalTimeStepList) > 0:
                likelihood.append(prev_theory.likelihood(finalTimeStepList[-1]))
                surprise.append(1 - likelihood[-1])
                sum_lik_play.append(sum([prev_theory.likelihood(ts) for ts in finalTimeStepList]))
            else:
                likelihood.append(float("nan"))
                surprise.append(float('nan'))
                sum_lik_play.append(float("nan"))

        play_post['newTimeStep_flag'] = newTimeStep_flag # same as len(effectListByColor) > 0
        play_post['likelihood'] = likelihood
        play_post['surprise'] = surprise # might be the same as theory_change_flag 
        play_post['sum_lik_play'] = sum_lik_play # notice for current episode only

        #
        # extract theory-based regressors
        #

        S_len = []
        I_len = []
        T_len = []
        Igen_len = []
        Tnov_len = []
        Ip_len = []
        for i in range(len(reg['regressors']['theory'])):
            theory = reg['regressors']['theory'][i][0]
            S_len.append(len(theory.spriteSet))
            I_len.append(len([r for r in theory.interactionSet if not r.generic]))
            T_len.append(len([t for t in theory.terminationSet if t.ruleType not in ['NoveltyRule']]))
            Ip_len.append(len([r for r in theory.interactionSet if not r.generic and r.interaction not in ['nothing']]))
            Igen_len.append(len([r for r in theory.interactionSet if r.generic]))
            Tnov_len.append(len([t for t in theory.terminationSet if t.ruleType in ['NoveltyRule']]))
        dS_len = [0] + [x2 - x1 for x1, x2 in zip(S_len[:-1], S_len[1:])]
        dI_len = [0] + [x2 - x1 for x1, x2 in zip(I_len[:-1], I_len[1:])]
        dT_len = [0] + [x2 - x1 for x1, x2 in zip(T_len[:-1], T_len[1:])]
        dIgen_len = [0] + [x2 - x1 for x1, x2 in zip(Igen_len[:-1], Igen_len[1:])]
        dTnov_len = [0] + [x2 - x1 for x1, x2 in zip(Tnov_len[:-1], Tnov_len[1:])]
        dIp_len = [0] + [x2 - x1 for x1, x2 in zip(Ip_len[:-1], Ip_len[1:])]

        play_post['S_len'] = S_len # size of sprite set 
        play_post['I_len'] = I_len # size of interaction set (non-generics)
        play_post['T_len'] = T_len # size of termination set (non-novelty rules)
        play_post['Igen_len'] = Igen_len # size of interaction set (generics)
        play_post['Tnov_len'] = Tnov_len # size of termination set (novelty rules)
        play_post['Ip_len'] = Ip_len # size of interaction set (non-generics and non-nothing)
        play_post['dS_len'] = dS_len # deltas
        play_post['dI_len'] = dI_len 
        play_post['dT_len'] = dT_len 
        play_post['dIgen_len'] = dIgen_len 
        play_post['dTnov_len'] = dTnov_len 
        play_post['dIp_len'] = dIp_len 

        # 
        # extract visual & sprite stuff recorded in the states 
        #

        # level size
        lines = [l for l in play['level_str'] if len(l) > 0] # from VGDLGame.buildLevel()
        width = len(lines[0])
        height = len(lines)
        play_post['grid_size'] = width * height

        g = VGDLParser().parseGame(play['game_str'])

        # other visual regressors
        keystate_timestamps = []
        state_timestamps = []
        new_sprites = []
        killed_sprites = []
        sprites = []
        non_walls = []
        avatar_moved = []
        moved = []
        movable = []
        collisions = []
        effects = []
        effectsByCol = []
        sprite_groups = []
        changed = []
        avatar_collision_flag = []
        win = []
        score = []
        ended = []
        subgoal_flag1 = []
        subgoal_flag2 = []

        state_default_colors = None
        prev_state_default_colors = None

        sprite_poss = [] # sprite positions in each state, as UUID => x, y
        grids = [] # grid squares in each state, as (x,y) => UUID
        assert(len(states) == len(keystates))
        for t in range(len(states)):
            state = states[t]
            keystate = keystates[t]
            state_timestamps.append(state['ts'])
            if keystate:
                keystate_timestamps.append(keystate['ts'])
            else:
                assert t == 0
                keystate_timestamps.append(state['ts']) # first keystate is dummy
            new_sprites.append(state['new_spritesLen'])
            if t > 0 and states[t]['kill_listLen'] != states[t - 1]['kill_listLen']:
                # b/c in fMRI mode we keep tally of all killed sprites, need to take delta here -- see _clearAll in core.py (which does not get called in fMRI mode, to be consistent with _performAction())
                assert states[t]['kill_listLen'] > states[t - 1]['kill_listLen']
                killed_sprites.append(states[t]['kill_listLen'] - states[t - 1]['kill_listLen'])
            else:
                killed_sprites.append(0)
            sprites.append(len(state['list']))
            collisions.append(state['collision_effLen'])
            effects.append(state['effectListLen'])
            effectsByCol.append(len(state['effectListByColor']))
            sprite_groups.append(state['sprite_groupsLen'])

            # set the game state, using default colors (just like EMPA -- see environment.py)
            #
            g.setFullState(state, cheap=False, default_colors=True)
            prev_state_default_colors = state_default_colors
            state_default_colors = g.getFullState() # used to cross reference EMPA and states sprites by color
            # IMPORTANT! use the sprite list from the original state;
            # This is because of a bug in getFullState() in core.py when as_string=True; overlapping sprites are not accounted for
            state_default_colors['list'] = state['list']

            # extract stuff from sprites themselves
            #

            nw = 0 # non wall count
            mv = 0 # moved sprites count
            amv = 0 # avatar moved?
            mb = 0 # movable sprites

            sprite_pos = {} # UUID => (x,y)
            # see setFullState() in core.py
            #print ' ------------------------ ', t
            for key, ss in state['objects'].iteritems():
                # key = sprite group, e.g. 'wall'
                if key != 'wall':
                    nw += len(ss)
                for pos, attrs in ss.iteritems():
                    # pos is str, e.g. '(140, 40)'
                    sprite_pos[attrs['ID']] = (attrs['x'], attrs['y'])

                    # see if sprite is movable
                    sclass = g.sprite_constr[key][0]
                    if not sclass.is_static:
                        mb += 1

                    # see if sprite moved from last frame
                    if t > 0 and attrs['ID'] in sprite_poss[t - 1] and sprite_poss[t - 1][attrs['ID']] != sprite_pos[attrs['ID']]:
                        #print key, ' moved from ', sprite_poss[t - 1][attrs['ID']], ' to ', sprite_pos[attrs['ID']]
                        mv += 1
                        if key == 'avatar':
                            amv = 1
            sprite_poss.append(sprite_pos)

            non_walls.append(nw)
            moved.append(mv)
            avatar_moved.append(amv)
            movable.append(mb)

            # extract stuff that depends on sprite drawing order
            #

            ch = 0 # changed grid squares

            grid = {}
            for key in g.sprite_order: # iterate over sprites in order in which they are drawn (see _drawAll() and __iter__() in BasicGame)
                if key not in state['objects']:
                    # abstract type
                    continue
                for pos, attrs in state['objects'][key].iteritems():
                    grid[pos] = attrs['ID']
            grids.append(grid)

            if t > 0: # in first frame, don't count any changes; let that be absorbed by play start regressor, who knows what else is going on; also this will dominate => not good (same for new sprites)
                # count squares that are now occupied by different sprites
                for pos, ID in grid.iteritems():
                    # see if topmost sprite in pos changed from last frame
                    if pos not in grids[t - 1] or grids[t - 1][pos] != grid[pos]:
                        ch += 1
                # don't forget squares that are no longer occupied by sprites!
                for pos, ID in grids[t - 1].iteritems():
                    if pos not in grid:
                        ch += 1
                    
            changed.append(ch)
    
            # extract effect stuff
            #

            acf = False
            for eff in state['effectListByClass']:
                if 'avatar' == eff[1] or 'avatar' == eff[2]:
                    acf = True
                    break

            avatar_collision_flag.append(acf)

            # extract rewards
            #

            win.append(state['win'])
            score.append(state['score'])
            ended.append(state['ended'])

            # extract subgoals
            #
            if t <= 1:
                # off-by-one from core.py vs. EMPA.py (skips initial state); also, need previous theory & state
                subgoal_flag1.append(False)
                subgoal_flag2.append(False)
            else:
                prev_theory = reg['regressors']['theory'][t - 2][0] # off-by-one

                # version 1: use state['list'] for sprites
                # Pro: includes all sprites, including overlapping ones
                # Con: includes dead sprites as well, and cannot cross reference with state['kill_list_ID'] (except when there are no sprites left of a given kind, in which case it correctly counts them as 0)
                # => useful for transforms, pretty conservative
                subgoal1 = check_for_subgoal_progress(
                        prev_theory, 
                        prev_state_default_colors, 
                        state_default_colors,
                        get_active_sprites_from_list)
                subgoal_flag1.append(subgoal1)

                # version 2: use state['objects'] for sprites
                # Pro: excludes dead sprites
                # Con: does not account for overlapping sprites
                # => might want to cross-reference with kill_list, to exclude false positives (e.g. sprite disappeared behind another sprite)
                subgoal2 = check_for_subgoal_progress(
                        prev_theory, 
                        prev_state_default_colors, 
                        state_default_colors,
                        get_active_sprites_from_objects)
                subgoal_flag2.append(subgoal2)


        new_sprites[0] = 0 # let that be absorbed by play start regressor; o/w, it will dominate GLM

        play_post['state_timestamps'] = state_timestamps
        play_post['keystate_timestamps'] = keystate_timestamps # for crossreferencing with the EMPA regressors
        play_post['timestamps'] = state_timestamps # backwards compatibility
        play_post['new_sprites'] = new_sprites # num new sprites
        play_post['killed_sprites'] = killed_sprites # num killed sprites
        play_post['sprites'] = sprites # num sprites
        play_post['collisions'] = collisions # num collisions
        play_post['effects'] = effects # num effects
        play_post['sprite_groups'] = sprite_groups # num sprite categories
        play_post['non_walls'] = non_walls # num non-wall sprites
        play_post['avatar_moved'] = avatar_moved  # did the avatar move?
        play_post['moved'] = moved # num sprites that just moved
        play_post['movable'] = movable  # num of sprites that can mave (i.e. are not static)
        play_post['changed'] = changed  # num changed grid squares
        play_post['avatar_collision_flag'] = avatar_collision_flag  # whether the avatar collided with an object 
        play_post['effectsByCol'] = effectsByCol # num effects; used in EMPA
        play_post['win'] = win 
        play_post['score'] = score
        play_post['ended'] = ended
        play_post['subgoal_flag1'] = subgoal_flag1 # whether we reached a subgoal (conservative, transforms only)
        play_post['subgoal_flag2'] = subgoal_flag2 # whether we reached a subgoal (liberal, includes false positives where sprites are overlapping)
        play_post['play_post_ts'] = time.time() # for sanity checks
        play_post['play_post_dts'] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S") # for sanity checks

        #
        # extract keypresses similar to keyholds, etc already recorded in plays (see startGame() in core.py)
        # also extract duplicates of keyholds, etc based on key presses
        # the purpose is to:
        # 1) sanity check key presses against keydowns, etc. recorded during game play (they're different pygame events)
        # 2) generate keyholds boxcars for subj #1 when we still didn't have proper keyhold logging
        #

        keypresses = {}
        keyups = {}
        keydowns = {}
        keyholds = {} # boxcars starting at keydown and ending at keyup
        for _, k in keyNames.iteritems():
            keypresses[k] = []
            keyups[k] = []
            keydowns[k] = []
            keyholds[k] = []

        # compute keypresses first
        # b/c of fMRI continuoun pressing shenanighans, those are the ones that actally resulted in movement, so confounded with visual
        # highly advised not to use
        #
        for t in range(len(keystates)): # for each state / pygame frame
            if keystates[t] is None:
                assert t == 0  # first one is blank
                continue

            keystate = keystates[t]['keystate']
            for key in range(len(keystate)): # for each key (potentially pressed) TODO only iterate over relevant keys
                if key not in keyNames.keys():
                    continue
                k = keyNames[key] # assumes fMRI_remap was used; see startGame() in core.py

                # update keypresses
                if keystate[key]:
                    keypresses[k].append(keystates[t]['ts'])


        #print '---------- BEFORE:'
        #print_keystates(keystates)

    
        # now, extend every key press into the next 0.15 s frames...
        # b/c fMRI continuous key press chicanery in startGame(), we end up with gaps in the logged keys
        # i.e. there are lots of frames when a key was being held but nothing was logged, so we can't reconstruct keyholds properly...
        # only an issue for subject 1 really
        for t in reversed(range(len(keystates))): # for each state / pygame frame
            if keystates[t] is None:
                assert t == 0  # first one is blank
                continue

            keystate = keystates[t]['keystate']
            for key in range(len(keystate)): # for each key (potentially pressed) TODO only iterate over relevant keys
                if key not in keyNames.keys():
                    continue

                if not keystate[key]:
                    tp = t - 1
                    while tp > 0 and keystates[t]['ts'] - keystates[tp]['ts'] <= 0.15:
                        if keystates[tp]['keystate'][key]:
                            keystates[t]['keystate'][key] = True
                            break
                        tp -= 1


        #print '\n\n\n\n ----------- AFTER:'
        #print_keystates(keystates)


        # compute keyholds based on the repeated keypresses
        # makes it more accurate (see GLM 1)
        # all of this is b/c we screwed up subj #1 ...
        #
        for t in range(len(keystates)): # for each state / pygame frame
            if keystates[t] is None:
                assert t == 0  # first one is blank
                continue

            keystate = keystates[t]['keystate']
            last_keystate = keystates[t - 1]['keystate'] if t - 1 > 0 else None 

            for key in range(len(keystate)): # for each key (potentially pressed) TODO only iterate over relevant keys
                if key not in keyNames.keys():
                    continue
                k = keyNames[key] # assumes fMRI_remap was used; see startGame() in core.py

                # update keypresses
                if keystate[key]:
                    keypresses[k].append(keystates[t]['ts'])

                if keystate[key] and (last_keystate is None or not last_keystate[key]):
                    # key just got pressed
                    # timestamp between frames, unless it's the first frame
                    ts = keystates[t]['ts'] if t - 1 == 0 else (keystates[t]['ts'] + keystates[t - 1]['ts']) / 2.0
                    keydowns[k].append(ts)

                if not keystate[key] and last_keystate is not None and last_keystate[key]:
                    # key was pressed but is now released
                    offset = (keystates[t]['ts'] + keystates[t - 1]['ts']) / 2.0
                    keyups[k].append(offset)
                    onset = keydowns[k][-1]
                    keyholds[k].append((onset, offset - onset))


        # from logLastKeyup() in startGame()
        for k in keydowns.keys():
            if len(keyups[k]) < len(keydowns[k]):
                if len(keyups[k]) + 1 != len(keydowns[k]):
                    print 'inconsistent keyups vs. keydowns'
                    embed()
                    assert False
                offset = keystates[-1]['ts'] + 1e-6 # so we don't accidentally get negative keyhold durations 
                keyups[k].append(offset)
                onset = keydowns[k][-1]
                keyholds[k].append((onset, offset - onset))

        play_post['keypresses'] = keypresses
        play_post['keyholds'] = keyholds
        play_post['keyups'] = keyups
        play_post['keydowns'] = keydowns

        db.empa_plays_post.insert_one(play_post)
        
    print 'done!'
    plays.close()



if __name__ == '__main__':
    subj_id = sys.argv[1]

    playsPostproc(subj_id)
    #for s in range(1,9):
    #    playsPostproc(str(s))
