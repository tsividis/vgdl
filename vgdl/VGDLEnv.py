from collections import namedtuple, defaultdict
from gym import spaces
from PIL import Image
from pygame.locals import K_RIGHT, K_LEFT, K_UP, K_DOWN, K_SPACE
from scipy import misc
from skimage.transform import resize
from vgdl import colors
from vgdl.rlenvironmentnonstatic import createRLInputGameFromStrings

from IPython import embed

import cloudpickle
import csv
import cv2
import imageio
import numpy as np
import os
import pdb
import pygame
import random
import sys

random.seed(42)
np.random.seed(42)

os.environ['SDL_AUDIODRIVER'] = 'dsp'


class VGDLEnvAndres(object):
    def __init__(self, game_name):

        ###CONFIGS
        self.game_name = game_name
        self.game_name_short = game_name[5:]
        self.level_switch = 'sequential'
        self.trial_num = 1003
        self.criteria = '1/1'
        self.timeout = 2000
        games_folder = 'all_games'

        ##FOR RECORDING
        self.record_flag = 0#1 #record_flag
        self.reward_histories_folder = 'reward_histories'
        self.object_interaction_histories_folder = 'object_interaction_histories'
        self.picklefilepath = 'pickleFiles/{}.csv'.format(self.game_name_short)

        self.Env = VGDLEnv(self.game_name_short, games_folder)
        self.Env.set_level(0)
        self.action_space = spaces.Discrete(len(self.Env.actions))
        self.observation_space = spaces.Box(low=0.0, high=1.0, shape=(84,84,3))

        self.game_over = 0
        self.screen_history = []
        self.steps = 0
        self.episode_steps = 0
        self.episode = 0
        self.episode_reward = 0
        self.event_dict = defaultdict(lambda: 0)
        self.recent_history = [0] * int(self.criteria.split('/')[1])

        if self.record_flag:
            with open('{}/{}_reward_history_{}_trial{}.csv'.format(self.reward_histories_folder,self.game_name_short,self.level_switch,self.trial_num), "ab") as file:
                writer = csv.writer(file)
                writer.writerow(["level", "steps", "ep_reward", "win", "game_name", "criteria"])

            with open('{}/{}_object_interaction_history_{}_trial{}.csv'.format(
                    self.object_interaction_histories_folder,self.game_name_short, self.level_switch, self.trial_num), "wb") as file:
                interactionfilewriter = csv.writer(file)
                interactionfilewriter.writerow(
                    ['agent_type', 'subject_ID', 'modelrun_ID', 'game_name', 'game_level', 'episode_number', 'event_name',
                     'count'])

    ### For Gym API
    def set_level(self, intended_level, intended_steps):
        self.Env.lvl = intended_level
        self.Env.set_level(self.Env.lvl)
        self.steps = intended_steps

    def get_level(self):
        return self.Env.lvl

    def check_that_avatar_is_alive(self):
    	return self.Env.check_that_avatar_is_alive()

    def step(self, action):
        if self.steps>= 1000000:
            sys.exit()
        self.steps += 1
        self.episode_steps += 1
        self.append_gif()
        self.reward, self.game_over, self.win = self.Env.step(action)

        if self.check_that_avatar_is_alive():
            self.avatar_position_data['episodes'][-1].append((self.Env.current_env._game.sprite_groups['avatar'][0].rect.left,
			self.Env.current_env._game.sprite_groups['avatar'][0].rect.top,
			self.Env.current_env._game.time,
			self.Env.lvl))
        else:
            print("AVATAR_ERROR_IGNORE")
            embed()
            self.game_over = True 
        ## PEDRO: 2. Store events that occur at each timestep
        timestep_events = set()
        for e in self.Env.current_env._game.effectListByClass:
            ## because event handling is so weird in Frogs, we need to filter out these events.
            ## Avatar-water and avatar-log collisions will still be reported from the (killSprite avatar water) interaction and (pullWithIt avatar log) interaction
            ## which is what a player perceives when they play
            if e in [('changeResource', 'avatar', 'water'), ('changeResource', 'avatar', 'log')]:
                pass
            else:
                timestep_events.add(tuple(sorted((e[1], e[2]))))
        for e in timestep_events:
            self.event_dict[e] += 1

        self.episode_reward += self.reward
        self.state = self.get_screen()

        if self.game_over or self.episode_steps > self.timeout:
            if self.episode_steps > self.timeout:
                print("Game Timed Out")
            ## PEDRO: 3. At the end of each episode, write events to csv
            if self.record_flag:
                with open('{}/{}_object_interaction_history_{}_trial{}.csv'.format(
                        self.object_interaction_histories_folder, self.game_name_short, self.level_switch, self.trial_num), "ab") as file:
                    interactionfilewriter = csv.writer(file)
                    for event_name, count in self.event_dict.items():
                        row = ('DDQN', 'NA', 'NA', self.game_name_short, self.Env.lvl, self.episode, event_name, count)
                        interactionfilewriter.writerow(row)
            self.episode += 1
            print("Level {}, episode reward at step {}: {}".format(self.Env.lvl, self.steps, self.episode_reward))
            sys.stdout.flush()
            episode_results = [self.Env.lvl, self.steps, self.episode_reward, self.win, self.game_name_short,
                                 int(self.criteria.split('/')[0])]

            self.recent_history.insert(0, self.win)
            self.recent_history.pop()
            if self.level_step():
                if self.record_flag:
                    with open('{}/{}_reward_history_{}_trial{}.csv'.format( self.reward_histories_folder,self.game_name_short,self.level_switch,self.trial_num),
                              "ab") as file:
                        writer = csv.writer(file)
                        writer.writerow(episode_results)
                    print('{{}'.format(1))
                    return self.state, self.reward, self.game_over, 0
            self.episode_reward = 0

            if self.episode % 2 == 0 and self.record_flag:
                with open(self.picklefilepath, 'wb') as f:
                    cloudpickle.dump(self.avatar_position_data, f)

            if self.record_flag:
                with open('{}/{}_reward_history_{}_trial{}.csv'.format(self.reward_histories_folder ,self.game_name_short,self.level_switch,self.trial_num),
                          "ab") as file:
                    writer = csv.writer(file)
                    writer.writerow(episode_results)
            self.screen_history = []
        return self.state, self.reward, self.game_over, 0

    def reset(self):
        self.Env.reset()
        self.avatar_position_data = {'game_info': (self.Env.current_env.width, self.Env.current_env.height),
                                'episodes': [[(self.Env.current_env._game.sprite_groups['avatar'][0].rect.left,
                                               self.Env.current_env._game.sprite_groups['avatar'][0].rect.top,
                                               self.Env.current_env._game.time,
                                               self.Env.lvl)]]}
        self.episode_steps = 0
        self.state = self.get_screen()
        return self.state

    ####Screen functions from player.py
    def save_screen(self):
        misc.imsave('original.png', self.Env.render())
        misc.imsave('altered.png', np.rollaxis(self.get_screen().cpu().numpy()[0], 0, 3))

    def get_screen(self):
        screen = self.Env.render()
        screen = np.ascontiguousarray(screen, dtype=np.float32) / 255
        screen = cv2.resize(screen, dsize=(84,84), interpolation=cv2.INTER_CUBIC)
        screen_1channel = np.mean(screen, axis=2)
        return screen_1channel

    def save_gif(self):
        imageio.mimsave('screens/{}_frame{}.gif'.format(self.game_name_short, self.steps), self.screen_history)

    def append_gif(self):
        frame = self.Env.render(gif=True)
        self.screen_history.append(frame)

	###Auxiliary functions from player.py
    def level_step(self):
        if self.level_switch == 'sequential':
            if sum(self.recent_history) == int(self.criteria.split('/')[0]):  # if level is 'won'
                if self.Env.lvl == len(self.Env.env_list) - 1:  # if this is the last training level
                    print("Learning Finished")
                    return 1
                else:  # if this isn't the last level
                    self.Env.lvl += 1
                    self.Env.set_level(self.Env.lvl)
                    print("Next Level!")
                    self.recent_history = [0] * int(self.criteria.split('/')[1])
                    return 0
        ##ANDRES Note that nothing happens otherwise
        elif self.level_switch == 'random':
            # else:
            self.Env.lvl = np.random.choice(range(len(self.Env.env_list) - 1))
            self.Env.set_level(self.Env.lvl)
            return 0
        else:
            raise Exception('level switch not specified.')


class VGDLEnv():

	def __init__(self, game_name, game_folder):

		self.game_name = game_name
		self.game_folder = game_folder
		self.env_list = self.load_game(game_name, game_folder)
		self.lvl = 0
		self.set_level(self.lvl)
		self.actions = [0, K_RIGHT, K_LEFT, K_UP, K_DOWN, K_SPACE]

	def set_level(self, lvl):
		self.current_env = self.env_list[lvl]
		self.current_env.softReset()

	def check_that_avatar_is_alive(self):
		return self.current_env.check_that_avatar_is_alive()

	def step(self, action):

		prev_score = self.current_env._game.score
		results = self.current_env.step(self.actions[action])
		reward = results['reward']
		ended = results['ended']
		win = results['win']

		return reward, ended, win

	def reset(self):

		self.env_list = self.load_game(self.game_name, self.game_folder)
		self.set_level(self.lvl)
		self.current_env.softReset()

	def render(self, gif = False):

		game = self.current_env._game
		# returns numpy array of pixel values based on the sprites in the game
		im = np.empty([game.screensize[1], game.screensize[0], 3], dtype=np.uint8)
		bg = np.array(colors.LIGHTGRAY, dtype=np.uint8) # background
		im[:] = bg

		for className in game.sprite_order:
			if className in game.sprite_groups:
				for sprite in game.sprite_groups[className]:
					r, c, h, w = sprite.rect.top , sprite.rect.left , sprite.rect.height , sprite.rect.width
					im[r:r+h, c:c+w, :] = np.array(sprite.color, dtype=np.uint8)

		if gif: im = resize(im, (64, 64, 3))
		return im

	def load_game(self, game_name, games_folder):
		def _load_level(gameString, levelString):

			headless = True

			rleCreateFunc = lambda: createRLInputGameFromStrings(gameString, levelString)

			rle = rleCreateFunc()
			rle.visualize = True
			if headless:
				os.environ["SDL_VIDEODRIVER"] = "dummy"
			pygame.init()

			return rle

		def _gen_color():
			from vgdl.colors import colorDict
			color_list = colorDict.values()
			color_list = [c for c in color_list if c not in ['UUWSWF']]
			for color in color_list:
				yield color

		file_list = {}
		for file in os.listdir(games_folder):
			if 'DS' not in file:

				if 'expt_ee' in game_name:
					if game_name in file:
						if 'lvl' not in file:
							level = file.split('desc_')[1][0]
							file_list['game_{}'.format(level)] = file
						else:
							level = file.split('_lvl')[1][0]
							file_list[int(level)] = file
				else:
					if game_name == file.split('.txt')[0] or game_name == file.split('_lvl')[0]:
						if 'lvl' not in file: 
							file_list['game'] = file
						else: 
							level = file.split('_lvl')[1][0]
							file_list[int(level)] = file

		if 'expt_ee' not in game_name:
			with open('{}/{}'.format(games_folder, file_list['game']), 'r') as game:
				gameString = game.read()

		env_list = {}

		num_levels = len(file_list.keys())-1
		
		if 'expt_ee' in game_name:
			num_levels = int(len(file_list.keys())/2)

		for lvl_idx in range(num_levels):

			if 'expt_ee' in game_name:
				with open('{}/{}'.format(games_folder, file_list['game_{}'.format(lvl_idx)]), 'r') as game:
					gameString = game.read()

			with open('{}/{}'.format(games_folder, file_list[lvl_idx]), 'r') as level:
				levelString = level.read()

			env_list[lvl_idx] = _load_level(gameString, levelString)

		return env_list



game_name = 'VGDL_tiny_zelda'
env = VGDLEnvAndres(game_name)
embed()
