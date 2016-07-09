"""
Theory induction on VGDL Games
"""

class Game:
	"""
	VGDL Game and Induction State.
	"""
	def __init__(self):
		# Game states #TODO: May not need these
		#self.backpack = {}
		#self.trace = [] # list of TimeStep objects that happened during a gameplay

		# Induction states
		self.hypothesisSpace = []
		self.theoryCount = 0
	
	def induction(trace):
		"""
		Iterates through trace 
		"""
		self.hypothesisSpace = [Theory()]

		for timestep in trace:						# Iterate through each timestep
			for theory in self.hypothesisSpace: 			# Iterate through each theory
				if theory.likelihood(timestep) < 1.0: 	# Theory needs to be changed
					newTheories = theory.explainTimeStep(timestep)
					self.hypothesisSpace.extend(newTheories)
			cleanHypothesisSpace()
		
		return hypothesisSpace

	def cleanHypothesisSpace():
		"""
		"""
		pass

class Theory:
	"""
	A VGDL description of a game
	"""
	def __init__(self, game):
		self.game = game
		self.parent = None
		self.children = []
		self.depth = 0

		# Following VGDL structure
		self.spriteSet = [] # Includes properties of sprites/objects
		self.levelMapping = [] # Map of the game
		self.interactionSet = [] # Interaction rules
		self.terminationSet = [] # Conditions that lead to game termination

		self.classes = {} # Maps classes -> objects
		self.predicates = set() # Types of possible interactions

	def explainTimeStep(timestep, currTheories):
		"""
		Returns a set of theories that explain all the events that took place at timestep.
		Hypotheticals can be passed as args to enable the explanation of multiple events in a single timestep.
		"""
		# Base Case
		if len(timestep.events) == 1:
			theories = []
			if not currTheories:
				theories.extend(self.explainEvent(timestep.events[0]))
			else: # Generate theories based on each hypothetical theory
				for theory in currTheories:
					theories.extend(self.explainEvent(timestep.events[0]))
			return theories

		# Recursive case
		else:
			theories = self.explainEvent(timestep.events[0])
			updatedTimeStep = TimeStep(timestep.agentAction, timestep.agentState, timestep.events[1:])
			return self.explainTimeStep(updatedTimeStep, currTheories)

	def explainEvent(event):
		"""
		"""
		pass



class TimeStep: 
	"""
	Everything that happened in a time step in the game.
	
	Ex.)
	TimeStep.agentAction = 'up'
	TimeStep.agentState = {'health':1, 'treasure':2}
	TimeStep.events = [(bounceForward, BLUE, ORANGE), (undoAll, ORANGE, BLACK)]
	TimeStep.t = 4  --> meaning all of this took place at t_4
	"""

	def __init__(self, agentAction, agentState, events):
		self.agentAction = agentAction 
		self.agentState = agentState # agent's backpack
		self.events = events 
		self.t = False # Number timestep




		
		