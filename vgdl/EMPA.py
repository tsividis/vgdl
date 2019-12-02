from util import *
"""
TODO:

Move all classes but Agent to their own files.
"""

"""
rle fields and methods currently used:

_game
_obstypes
outdim
step()
show()


_game:
.sprite_groups
.kill_list

"""

class Environment:
	def __init__(self):
		pass
	def get_actions(self):
		pass
	def get_observation(self):
		pass
	def print_observation_to_screen(self):
		pass
	def step(self, actions):
		pass
	def copy(self):
		pass

class Agent:
    def __init__(self):
    	self.sensors = None
    	self.hypothesis_space = None ## {hypothesis:posterior}

    	self.curiosity_module = None
    	self.inference_module = None
    	self.planning_module = None

    	self.metacontroller = None

class Planner:
	def __init__(self):
		self.model_description = None
		self.environment = None
		self.best_actions = None
		self.predicted_states = None

	def plan(self):
		
		## get available actions

		## plan according to specified algorithm (this probably should be done with overloading) and heuristics if they're available for the DSL (unless you're lesioning)

		## TODO
		return self.best_actions, self.predicted_states

class InferenceModule(self):
	self.hypothesis_space = None

	def run_inference(self):
		## TODO
		return self.hypothesis_space

	def select_hypothesis(self, method='MAP'):
		if method=='MAP':
			sorted_hypotheses = sort_dictionary_by_key(self.hypothesis_space)
			return sorted_hypotheses.items()[0]

class DSL:
	def __init__(self):
		self.ontology = None
		self.heuristics = None
		self.hypothesis_space = None

	def likelihood(self, hypothesis, states, actions):
		pass

	def prior(self, hypothesis):
		pass


	def posterior(self, hypothesis):
		pass
