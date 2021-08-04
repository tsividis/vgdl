# DQN agent# DQN agent# DQN agent# DQN agent
# TODO ideally, there should be an abstract agent class; in practice, it is easiest to just inherit from EMPA

# TODO copy pasted from https://github.com/ACampero/RC_RL and then adapted (necessary because of small differences)

# import gym
# import gym_gvgai
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as T
import random
from collections import namedtuple, defaultdict
import numpy as np
from PIL import Image
import pdb
from scipy import misc
import imageio
import sys
from VGDLEnv import VGDLEnv
import csv
import cloudpickle
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
from EMPA import Agent, actionDict, availableActions, AvatarTypes
from theory_template import TimeStep, Theory, Game, writeTheoryToTxt, generateSymbolDict, getPosterior
from theory_template import TimeoutRule, SpriteCounterRule, MultiSpriteCounterRule
from metacontroller import Metacontroller
from dynamic_type_inference import dynamicTypeDistribution_VGDL1, getKL
import WBP
from IPython import embed
from rlenvironmentnonstatic import createRLInputGame, createRLInputGameFromStrings, defInputGame, createMindEnv
from bookkeeping import Bookkeeping
from pprint import pprint
from EMPA import Agent, actionDict, availableActions, AvatarTypes, NOOP
from vgdl.hyperparameters import hyperparameter_sets
import os
from pygame.locals import K_RIGHT, K_LEFT, K_UP, K_DOWN, K_SPACE


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)

# colors from VGDL?

LAYER_TO_LAYER_NAME = {
 'Conv2d(3, 32, kernel_size=(8, 8), stride=(4, 4))': 'conv1',
 'Conv2d(32, 64, kernel_size=(4, 4), stride=(2, 2))': 'conv2',
 'Conv2d(64, 64, kernel_size=(3, 3), stride=(1, 1))': 'conv3',
 'Linear(in_features=1024, out_features=512, bias=True)': 'linear1',
 'Linear(in_features=512, out_features=6, bias=True)': 'linear2',
}

class DQN(nn.Module):
    def __init__(self, input_size, output_size):
        super(DQN, self).__init__()
        self.input_size = input_size
        self.output_size = output_size
        self.cnn = nn.Sequential(
            nn.Conv2d(self.input_size, 32, kernel_size=8, stride=4),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=4, stride=2),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=1),
            nn.BatchNorm2d(64),
            nn.ReLU())
        self.classifier = nn.Sequential(
            nn.Linear(64 * 4 * 4, 512),
            nn.ReLU(),
            nn.Linear(512, self.output_size))

    def forward(self, x):
        # assert(list(x.size()[-3]) == self.input_size)
        # debug_here()
        #pdb.set_trace()
        x = self.cnn(x)
        x = x.view(x.size(0), -1)
        x = self.classifier(x)
        return x

#ANDRES: Commented thing up and added everything until class ReplayMemory
'''
# Factorised NoisyLinear layer with bias
class NoisyLinear(nn.Module):
  def __init__(self, in_features, out_features, std_init=0.5):
    super(NoisyLinear, self).__init__()
    self.in_features = in_features
    self.out_features = out_features
    self.std_init = std_init
    self.weight_mu = nn.Parameter(torch.empty(out_features, in_features))
    self.weight_sigma = nn.Parameter(torch.empty(out_features, in_features))
    self.register_buffer('weight_epsilon', torch.empty(out_features, in_features))
    self.bias_mu = nn.Parameter(torch.empty(out_features))
    self.bias_sigma = nn.Parameter(torch.empty(out_features))
    self.register_buffer('bias_epsilon', torch.empty(out_features))
    self.reset_parameters()
    self.reset_noise()

  def reset_parameters(self):
    mu_range = 1 / math.sqrt(self.in_features)
    self.weight_mu.data.uniform_(-mu_range, mu_range)
    self.weight_sigma.data.fill_(self.std_init / math.sqrt(self.in_features))
    self.bias_mu.data.uniform_(-mu_range, mu_range)
    self.bias_sigma.data.fill_(self.std_init / math.sqrt(self.out_features))

  def _scale_noise(self, size):
    x = torch.randn(size)
    return x.sign().mul_(x.abs().sqrt_())

  def reset_noise(self):
    epsilon_in = self._scale_noise(self.in_features)
    epsilon_out = self._scale_noise(self.out_features)
    self.weight_epsilon.copy_(epsilon_out.ger(epsilon_in))
    self.bias_epsilon.copy_(epsilon_out)

  def forward(self, input):
    print ('entree')
    if self.training:
      return F.linear(input, self.weight_mu + self.weight_sigma * self.weight_epsilon, self.bias_mu + self.bias_sigma * self.bias_epsilon)
    else:
      return F.linear(input, self.weight_mu, self.bias_mu)


class DQN(nn.Module):
  def __init__(self, args, action_space):
    super().__init__()
    self.atoms = args.atoms
    self.action_space = action_space

    if args.architecture == 'canonical':
      self.convs = nn.Sequential(nn.Conv2d(args.history_length, 32, 8, stride=4, padding=0), nn.ReLU(),
                                 nn.Conv2d(32, 64, 4, stride=2, padding=0), nn.ReLU(),
                                 nn.Conv2d(64, 64, 3, stride=1, padding=0), nn.ReLU())
      self.conv_output_size = 3136
    elif args.architecture == 'data-efficient':
      self.convs = nn.Sequential(nn.Conv2d(args.history_length, 32, 5, stride=5, padding=0), nn.ReLU(),
                                 nn.Conv2d(32, 64, 5, stride=5, padding=0), nn.ReLU())
      self.conv_output_size = 576
    self.fc_h_v = NoisyLinear(self.conv_output_size, args.hidden_size, std_init=args.noisy_std)
    self.fc_h_a = NoisyLinear(self.conv_output_size, args.hidden_size, std_init=args.noisy_std)
    self.fc_z_v = NoisyLinear(args.hidden_size, self.atoms, std_init=args.noisy_std)
    self.fc_z_a = NoisyLinear(args.hidden_size, action_space * self.atoms, std_init=args.noisy_std)

  def forward(self, x, log=False):
    x = self.convs(x)
    x = x.view(-1, self.conv_output_size)
    v = self.fc_z_v(F.relu(self.fc_h_v(x)))  # Value stream
    a = self.fc_z_a(F.relu(self.fc_h_a(x)))  # Advantage stream
    v, a = v.view(-1, 1, self.atoms), a.view(-1, self.action_space, self.atoms)
    q = v + a - a.mean(1, keepdim=True)  # Combine streams
    if log:  # Use log softmax for numerical stability
      q = F.log_softmax(q, dim=2)  # Log probabilities with action over second dimension
    else:
      q = F.softmax(q, dim=2)  # Probabilities with action over second dimension
    return q

  def reset_noise(self):
    for name, module in self.named_children():
      if 'fc' in name:
        module.reset_noise()
'''
Transition = namedtuple('Transition',
                                     ('state', 'action', 'next_state', 'reward'))

class ReplayMemory(object):

    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
        self.position = 0

    def push(self, state, action, next_state, reward):
        """Saves a transition."""
        if len(self.memory) < self.capacity:
            self.memory.append(None)
        self.memory[self.position] = Transition(state, action, next_state, reward)
        self.position = (self.position + 1) % self.capacity

    def sample(self, batch_size):
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)

def rl_model(player):

    if player.config.model_name == 'DQN': return DQN(player.input_channels, player.n_actions).to(player.device)

    else: raise NotImplementedError('Model specified not implemented')



# modified copy of Player()
#
class DQNAgent(Agent):
    def __init__(self, gameFilename, game_size):
        # initialize with default parameters 
        super(DQNAgent, self).__init__('full', gameFilename, hyperparameter_sets=hyperparameter_sets, hyperparameter_index='short-term', 
            metacontroller_index=0, IW_k=1, extra_atom_allowed=True, task_ID='0', agent_name='DQN')

        # momchil
        config = {
            'trial_num': 1,
            'batch_size': 32,
            'lr': .00025,
            'gamma': .999,
            'eps_start': 1,
            'eps_end': .1,
            'eps_decay': 200.,
            'target_update': 100,
            'img_size': 64,
            'num_episodes': 20000,
            'max_steps': 1e6,
            'max_mem': 50000,
            'model_name': 'DQN',
            'model_weight_path': '/tmp/dqn.tmp',  # TODO
            'test_mode': 0,
            'pretrain': 0,
            'cuda': 1,
            'doubleq': 1,
            'level_switch': 'sequential',
            'timeout': 2000,
            'criteria': '1/1',
            'game_name': 'aliens',
            'num_trials': 1,
            'random_seed': 7,
        }
        self.config = Struct(**config)

        # momchil
        #self.Env = VGDLEnv(self.config.game_name, 'all_games')
        #self.Env.set_level(0)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        print('DQN Training at seed = {}'.format(self.config.random_seed))

        #self.game_size = np.shape(self.Env.render())
        self.game_size = game_size # momchil

        self.input_channels = self.game_size[2]
        #self.n_actions = len(self.Env.actions)
        self.n_actions = len(availableActions)

        self.policy_net = DQN(self.input_channels, self.n_actions).to(self.device)
        self.target_net = DQN(self.input_channels, self.n_actions).to(self.device)
        self.target_net.load_state_dict(self.policy_net.state_dict())

        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=self.config.lr)
        self.replay_memory = ReplayMemory(self.config.max_mem)

        self.steps_done = 0
        self.ended = 0

        self.resize = T.Compose([T.ToPILImage(),
                                 T.Pad((np.max(self.game_size[0:2]) - self.game_size[1],
                                        np.max(self.game_size[0:2]) - self.game_size[0])),
                                 T.Resize((self.config.img_size, self.config.img_size), interpolation=Image.CUBIC),
                                 T.ToTensor()])

        self.episode_durations = []

        self.num_episodes = self.config.num_episodes

        self.screen_history = []

        # momchil: last state and action
        self.state = None
        self.action = None

        # momchil: from train_model()
        self.steps = 0
        self.episode_steps = 0
        self.episode = 0
        self.best_reward = 0
        self.episode_reward = 0

        torch.backends.cudnn.deterministic = True
        torch.manual_seed = (self.config.random_seed)


    def beginningOfEpisodeManagement(self):

        if self.record_fMRIRegressors:
          # add hooks for recording hidden layer activations

          self.bookkeeping.regressors = dict()

          self.last_recorded_step = dict()

          def save_hidden_layer_output(module, module_in, module_out):
            # record hidden layer activations at each forward pass
            if self.environment.getTime() == 0:  # record regressors after each frame, which means excluding the initial frame
              return
            regressor_name = 'layer_' + LAYER_TO_LAYER_NAME[str(module)] + '_output'
            # make sure we do not record the same regressor twice for the same step
            # because we call the forward pass multiple times per step during training
            if regressor_name not in self.last_recorded_step:
              self.last_recorded_step[regressor_name] = 1  # because we skip step 0
            if self.last_recorded_step[regressor_name] < self.steps:
              assert self.last_recorded_step[regressor_name] + 1 == self.steps
              self.last_recorded_step[regressor_name] = self.steps
              self.logfMRIRegressor(regressor_name, module_out[0].detach().cpu().numpy())

          self.hook_handles = []
          for layer in self.policy_net.modules():
              if isinstance(layer, torch.nn.modules.conv.Conv2d): # or isinstance(layer, torch.nn.modules.Linear):
                  handle = layer.register_forward_hook(save_hidden_layer_output)
                  self.hook_handles.append(handle)


    def logfMRIRegressor(self, name, val):
        if not self.record_fMRIRegressors:
            return
        if name not in self.bookkeeping.regressors:
            self.bookkeeping.regressors[name] = []
        self.bookkeeping.regressors[name].append((val, self.environment._game.time, self.environment._game.playback_ts))

    def get_screen(self):
        # imageio.imsave('sample.png', self.Env.render())
        #pdb.set_trace()
        screen = self.environment._game.render()

        from PIL import Image
        # TODO (momchil) comment out debug image saving
        #Image.fromarray(screen).save('/tmp/dqn_screen_' + str(self.steps) + '.png')
        #embed()

        screen = screen.transpose((2, 0, 1)) # CxHxW
        screen = np.ascontiguousarray(screen, dtype=np.float32) / 255
        screen = torch.from_numpy(screen)
        # Resize, and add a batch dimension (BCHW)
        return self.resize(screen).unsqueeze(0).to(self.device)


    def step(self, action, env_results=None):
        # from the inner loop of Player::train_model()
        # note that we pass the env_results for the previous action (self.action), taken at the previous state (self.state)
        self.steps += 1
        self.episode_steps += 1

        print 'self.environment.getTime()', self.environment.getTime()
        if self.environment.getTime() == 0:
            self.beginningOfEpisodeManagement()
      
        # episode over?
        self.ended, self.win = self.environment._isDone()
        #score = self.environment.getScore()

        # get current state
        if not self.ended:
          self.next_state = self.get_screen()  # TODO try diff ? like in player.py
        else:
          self.next_state = None

        # get reward
        self.reward = env_results['reward']
        self.episode_reward += self.reward
        self.reward = max(-1.0, min(self.reward, 1.0))
        self.reward = torch.tensor([self.reward], device=self.device)

        #print '                    state ', self.state

        # Store the (previous) transition in memory -- note that we are one transition behind always, because we can't look into the future
        if self.state is not None:
          assert self.action is not None
          self.replay_memory.push(self.state, self.action, self.next_state, self.reward)

        # Move to the next state
        self.state = self.next_state

        # Perform one step of the optimization (on the target network)
        self.optimize_model()  # TODO (momchil) enable on GPU; crashes locally sometimes

        # end of episode
        if self.ended or self.episode_steps > self.config.timeout:
          self.episode += 1
          self.episode_steps = 0
          self.episode_reward = 0
          
          # Update the target network
          self.model_update()

        # bookkeeping
        if self.environment.getTime() == 0:
            self.bookkeeping.statesEncountered = []
        if self.make_movie or self.record_video_info:
            self.bookkeeping.statesEncountered.append(self.environment.getFullState())

        # log hidden layer parameters
        '''
        if self.record_fMRIRegressors and self.environment.getTime() > 0: # record regressors after each frame, which means excluding the initial frame
          for layer in self.policy_net.modules():
            if isinstance(layer, torch.nn.modules.conv.Conv2d): # or isinstance(layer, torch.nn.modules.Linear):
              regressor_name = 'layer_' + LAYER_TO_LAYER_NAME[str(layer)] + '_params'
              params = [param.detach().cpu().numpy() for param in layer.parameters()]
              self.logfMRIRegressor(regressor_name, params)
        '''

        # Select and return an action
        if self.state is not None:
          self.action = self.select_action()
        else:
          self.action = torch.tensor([[availableActions.index(NOOP)]]) # NOOP if end of episode
        VGDL_action = availableActions[self.action.item()]

        if self.record_fMRIRegressors and self.environment.getTime() > 0: # record regressors after each frame, which means excluding the initial frame
          self.logfMRIRegressor('action', VGDL_action)

        print self.steps, ' --> ', self.action, VGDL_action, self.reward
        return VGDL_action, self.ended


    def model_update(self):

        if self.steps > 1000 and not self.steps % self.config.target_update:

            self.target_net.load_state_dict(self.policy_net.state_dict())

            if self.episode_reward > self.best_reward or self.steps % 50000:
                self.best_reward = self.episode_reward
                print("New Best Reward: {}".format(self.best_reward))
                self.save_model()

    def select_action(self):

        sample = np.random.uniform()
        eps_threshold = self.config.eps_end + (self.config.eps_start - self.config.eps_end) * \
                        np.exp(-1. * self.steps_done / self.config.eps_decay)
        self.steps_done += 1.
        with torch.no_grad():
          # do a forward pass each time, so we can get the hidden layer activations
          optimal_action = self.policy_net(self.state).max(1)[1].view(1, 1)
        if sample > eps_threshold:
            return optimal_action
        else:
            return torch.tensor([[np.random.choice(list(range(len(availableActions))))]], device=self.device, dtype=torch.long)

    def optimize_model(self):

        if len(self.replay_memory) < self.config.batch_size:
            return
        transitions = self.replay_memory.sample(self.config.batch_size)
        # Transpose the batch (see http://stackoverflow.com/a/19343/3343043 for
        # detailed explanation).
        batch = Transition(*zip(*transitions))

        # Compute a mask of non-final states and concatenate the batch elements
        non_final_mask = torch.tensor(tuple(map(lambda s: s is not None,
                                                batch.next_state)), device=self.device, dtype=torch.uint8)
        non_final_next_states = torch.cat([s for s in batch.next_state
                                           if s is not None])
        state_batch = torch.cat(batch.state)
        action_batch = torch.cat(batch.action)
        try:
            reward_batch = torch.cat([r.float() for r in batch.reward])
        except:
            pdb.set_trace()

        # Compute Q(s_t, a) - the model computes Q(s_t), then we select the
        # columns of actions taken
        state_action_values = self.policy_net(state_batch).gather(1, action_batch)

        # Compute V(s_{t+1}) for all next states.
        next_state_values = torch.zeros(self.config.batch_size, device=self.device)

        if self.config.doubleq:
            _, next_state_actions = self.policy_net(non_final_next_states).max(1, keepdim=True)
            # ()
            next_state_values[non_final_mask] = self.target_net(non_final_next_states).gather(1,
                                                                                              next_state_actions).squeeze(
                1)
            next_state_values = next_state_values.data
            # print("Double Q")
        else:
            next_state_values[non_final_mask] = self.target_net(non_final_next_states).max(1)[0].detach()
            # print("Single Q")
        # Compute the expected Q values

        # next_state_values[non_final_mask] = self.target_net(non_final_next_states).max(1)[0].detach()
        expected_state_action_values = (next_state_values * self.config.gamma) + reward_batch.float()
        # ()

        # Compute Huber loss
        loss = F.smooth_l1_loss(state_action_values, expected_state_action_values.unsqueeze(1))
        # ()
        self.loss_history = loss
        # print(loss)

        # Optimize the model
        self.optimizer.zero_grad()
        loss.backward()
        for param in self.policy_net.parameters():
            param.grad.data.clamp_(-1, 1)
        self.optimizer.step()