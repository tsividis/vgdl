from IPython import embed
from planner import *
import itertools

from pygame.locals import K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT
NONE = 0
ACTIONS = [K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT, NONE]
actionDict = {K_SPACE: 'space', K_UP: 'up', K_DOWN: 'down', K_LEFT: 'left', K_RIGHT: 'right', NONE: 'wait'}

## Base class for width-based planners (IW(k) and 2BFS)
class WBP(Planner):
	def __init__(self, rle, gameString, levelString, gameFilename):
		Planner.__init__(self, rle, gameString, levelString, gameFilename, display=1)
		self.T = len(rle._obstypes.keys())+1 #number of object types. Adding avatar, which is not in obstypes.
		self.vecDim = [rle.outdim[0]*rle.outdim[1], 2, self.T]
		self.trueAtoms = defaultdict(lambda:0) #set() ## set of atoms that have been true at some point thus far in the planner.
		self.objectTypes = rle._game.sprite_groups.keys()
		self.objectTypes.sort()
		self.phiSize = sum([len(rle._game.sprite_groups[k]) for k in rle._game.sprite_groups.keys() if k not in ['wall', 'avatar']])
		self.objIDs = {}
		self.maxNumObjects = 6
		self.trackTokens = False
		self.vecSize = None
		self.addWaitAction = False
		self.padding = 5  ##5 is arbitrary; just to make sure we don't get overlap when we add positions
		i=1
		for k in rle._game.all_objects.keys():
			self.objIDs[k] = i * (rle.outdim[0]*rle.outdim[1]+self.padding)
			i+=1
		self.addSpaceBarToActions()

	def addSpaceBarToActions(self):
		## Note: if an object that isn't instantiated in the beginning is of a class that 
		## spacebar applies to, we won't pick up on it here.
		shootingClasses = ['MarioAvatar', 'ClimbingAvatar', 'ShootAvatar', 'Switch', 'FlakAvatar']
		classes = [str(o[0].__class__) for o in self.rle._game.sprite_groups.values() if len(o)>0]
		spacebarAvailable = False
		for sc in shootingClasses:
			if any([sc in c for c in classes]):
				spacebarAvailable = True
				break
		if spacebarAvailable:
			self.actions = [K_SPACE, K_UP, K_DOWN, K_LEFT, K_RIGHT]
		else:
			self.actions = [K_UP, K_DOWN, K_LEFT, K_RIGHT]
		if self.addWaitAction:
			self.actions.append(NONE)
		return

	def calculateAtoms(self, rle):
		lst = []
		for k in rle._game.sprite_groups.keys():
			for o in rle._game.sprite_groups[k]:
				if o not in rle._game.kill_list:
					## turn location into vector posd2[ition (rows appended one after the other.)
					pos = rle._rect2pos(o.rect) #x,y
					vecValue = pos[1] + pos[0]*rle.outdim[0] + 1
				else:
					vecValue = 0
				objPosCombination = self.objIDs[o.ID] + vecValue
				lst.append(objPosCombination)
		present = []
		for k in [t for t in self.objectTypes if t not in ['wall', 'avatar']]: ##maybe add the avatar to this global state
			# for o in rle._game.sprite_groups[k]:
			for o in sorted(rle._game.sprite_groups[k], key=lambda s:s.ID):
				if o not in rle._game.kill_list:
					present.append(1)
				else:
					present.append(0)
		ind = sum([present[i]*2**i for i in range(len(present))])
		lst.append(ind)
		if not self.vecSize:
			self.vecSize = len(lst)
			print "Vector is length {}".format(self.vecSize)
		return set(lst)
	
	def compareDicts(self, d1,d2):
		## only tells us what is in d2 that isn't in d1, as well as differences in values between shared keys
		return [k for k in d2.keys() if (k not in d1.keys() or d1[k]!=d2[k])]

	def delta(self, node1, node2):
		if node1 is None:
			diff = node2.state
		else:
			diff = node2.state-node1.state
		return diff

	# def initNovelty(self, node, k):
	# 	# Returns number of k-tuples of atoms that are newly true in node.
	# 	newAtoms = self.delta(node.parent, node)
	# 	# print "in novelty fn"
	# 	# embed()
	# 	if len(self.trueAtoms) > 0:
	# 		trueAtoms = node.state
	# 		oldTrueAtoms = set(trueAtoms)-set(newAtoms)
	# 		candidates = []
	# 		for i in range(1,k+1):
	# 			newPart = list(itertools.combinations(newAtoms, i))
	# 			oldPart = list(itertools.combinations(oldTrueAtoms, k-i))
	# 			unflattened = list(itertools.product(newPart, oldPart))
	# 			flattened = [frozenset((u[0]+u[1])) for u in unflattened]	
	# 			candidates.extend(flattened)
	# 	else:
	# 		candidates = [frozenset(p) for p in list(itertools.combinations(newAtoms, k))]
	# 	node.candidates = candidates
	# 	newTuples = set()
	# 	for aT in candidates:
	# 		if aT not in self.trueAtoms:
	# 			# if update:
	# 			# 	self.trueAtoms.add(aT)
	# 			newTuples.add(aT)
	# 	return len(newTuples)

# def BFS(rle, WBP):
# 	Q = Queue()
# 	visited, rejected = [], []
# 	start = Node(rle, WBP, [], None)
# 	start.lastState = rle
# 	win = start.eval()
# 	if win: return start, visited, rejected
# 	# visited.append(start)
# 	Q.put(start)
# 	while not Q.empty():
# 		current = Q.get()
# 		# win = current.eval()
# 		# nov = current.novelty
# 		print current.novelty
# 		print current.lastState.show()
# 		visited.append(current)
# 		# embed()
# 		current.updateNoveltyDict()
# 		# if nov > 0:		
# 		# if current.state not in visited:
# 			# visited.append(current)
# 			# if win:
# 				# return current, visited, rejected
# 		for a in WBP.actions:
# 			child = Node(rle, WBP, current.actionSeq+[a], current)
# 			win = child.eval()
# 			if win: 
# 				return child, visited, rejected
# 			elif child.novelty>0:
# 				Q.put(child)
# 			else:
# 				rejected.append(child)
# 	print "no more states in queue"
# 	embed()
# 	return Q, visited, rejected

def noveltySelection(QNovelty, QReward):
	bestNodes = sorted(QNovelty, key=lambda n: (n.novelty, -n.metabolic_reward))
	current = bestNodes.pop(0)
	QNovelty.remove(current)
	try:
		QReward.remove(current)
	except:
		pass
	return current

def rewardSelection(QReward, QNovelty):
	acceptableNodes = filter(lambda n:n.novelty<3, QReward)
	bestNodes = sorted(acceptableNodes, key=lambda n: (-n.metabolic_reward, n.novelty))
	current = bestNodes.pop(0)
	QReward.remove(current)
	try:
		QNovelty.remove(current)
	except:
		pass
	return current


# def updateNoveltyDict(node, WBP, QNovelty, QReward):
# 	for c in node.candidates:
# 		if 
# 		self.WBP.trueAtoms[c] = 1
# 	# for i in range(1,3):
# 	# 	for k in itertools.combinations(self.state, i):
# 	# 		self.WBP.trueAtoms[k] = 1
# 	return

"""
First: don't store anything for walls.

For a given state, you want to know what is the smallest tuple it makes true for the first time.
So you should look at the atoms in the state, and check if any are new.
if none are, then check if any tuples are true.
if none are, check if any 3-tuples are.
etc.


"""
def BFS3(rle, WBP):
	QNovelty, QReward = [], []
	visited, rejected = [], []
	start = Node(rle, WBP, [], None)
	start.lastState = rle
	visited.append(start)
	start.eval()
	QNovelty.append(start)
	QReward.append(start)
	i=0

	while len(QNovelty)>0 or len(QReward)>0:
		if i%2==0:
			current = noveltySelection(QNovelty, QReward)
		else:
			current = rewardSelection(QReward, QNovelty)

		print current.novelty, current.metabolic_reward, current.heuristicVal
		print len(QNovelty), len(QReward)
		# if current==None:
		# 	pass
		# else:
		print current.novelty
		print current.lastState.show()

		current.updateNoveltyDict(QNovelty, QReward)
		# embed()
		visited.append(current)

		# if current.win:
			# return current, visited, rejected ##revisit
		# else:
		for a in WBP.actions:
			child = Node(rle, WBP, current.actionSeq+[a], current)
			child.eval()
			if child.win:
				return child, visited, rejected ##revisit
			else:
				# print child.novelty
				# print child.lastState.show()
				# if child.novelty>0:
				QNovelty.append(child)		
				# if child.metabolic_reward>0:
				QReward.append(child)
		i+=1
	return None, visited, rejected			


class Node():
	def __init__(self, rle, WBP, actionSeq, parent):
		self.rle = rle
		self.WBP = WBP
		self.actionSeq = actionSeq
		self.parent = parent
		self.state = {}
		self.candidates = []
		self.novelty = None
		self.reward = None
		self.children = None
		self.lastState = None
		self.reconstructed=False
		self.expanded = False

	# try to copy parent lastState. Then take action and store as current lastState.
	## if that fails, replay from beginning and store as current lastState
	def eval(self):
		if self.parent and self.parent.lastState is not None:
			try:
				vrle = copy.deepcopy(self.parent.lastState)
				if len(self.actionSeq)>0:
					vrle.step(self.actionSeq[-1])
					terminal, win = vrle._isDone()
			except:
				print "conditions met but copy failed"
				embed()
		else:
			self.reconstructed=True
			print "copy failed; replaying from top"
			vrle = copy.deepcopy(rle)
			terminal, win = vrle._isDone()
			i=0
			while not terminal and len(self.actionSeq)>i:
				vrle.step(self.actionSeq[i])
				terminal, win = vrle._isDone()
				i += 1


		self.updateObjIDs(vrle)
		self.state = self.WBP.calculateAtoms(vrle)
		for i in range(1,3):
			for c in itertools.combinations(self.state, i):
				if self.WBP.trueAtoms[c] == 0:
					self.candidates.append(c)
			# self.candidates.extend(list(itertools.combinations(self.state, i)))
		self.updateNovelty()
		self.lastState = vrle
		self.win = win
		# self.novelty = self.WBP.initNovelty(self, self.WBP.k)
		self.reward = vrle._game.score
		try:
			heuristicVal = min([manhattanDist(self.WBP.findAvatarInRLE(self.lastState), o) for o in self.WBP.findObjectsInRLE(self.lastState, 'goal')])
			# heuristicVal = min([min([manhattanDist(box, goal) for goal in self.WBP.findObjectsInRLE(self.lastState, 'hole')]) \
			# 	for box in self.WBP.findObjectsInRLE(self.lastState, 'box')])
			# allVal = [min([manhattanDist(box, goal) for goal in self.WBP.findObjectsInRLE(self.lastState, 'hole')]) \
				# for box in self.WBP.findObjectsInRLE(self.lastState, 'box')]
			heuristicVal = sum([a**2 for a in allVal])
			# min([manhattanDist(b,o) for b,o in zip(self.findObjectsInRLE(self.lastState, 'box'), self.findObjectsInRLE, 'goal')])
		except:
			heuristicVal = 100000
			# print "didn't find goal"
			# embed()
		self.heuristicVal = heuristicVal
		self.metabolic_reward = vrle._game.metabolic_score - heuristicVal
		# embed()
		return win
	
	# def distanceHeuristic(self):
		# return manhattanDistance(self.WBP.findAvatarInRLE(self.lastState), self.WBP.findObjectInRLE(self.lastState, 'goal'))
	def updateNovelty(self):
		if len(self.candidates)==0:
			self.novelty = 3
		else:
			self.novelty = min([len(c) for c in self.candidates])
		return self.novelty
		# for c in self.candidates:
		# 	# if self.WBP.trueAtoms[c]==0:
		# 		self.candidates.remove(c)
		# 		self.novelty = len(c)
		# 		return self.novelty
		# return 3
		# for i in range(1,3):
		# 	for k in itertools.combinations(self.state, i):
		# 		if self.WBP.trueAtoms[k]==0:
		# 			self.novelty = i
		# 			return i		
		# 	self.novelty = 3
		# 	return 3


	def updateNoveltyDict(self, QNovelty, QReward):
		jointSet = list(set(QNovelty+QReward))
		for c in self.candidates:
			if self.WBP.trueAtoms[c] == 0:
				self.WBP.trueAtoms[c] = 1
				for n in jointSet:
					if c in n.candidates:
						n.candidates.remove(c)
		for n in jointSet:
			n.novelty = n.updateNovelty()
		# for i in range(1,3):
		# 	for k in itertools.combinations(self.state, i):
		# 		self.WBP.trueAtoms[k] = 1
		return

	def updateObjIDs(self, vrle):
		i = 0
		for objType in vrle._game.sprite_groups:
			for s in vrle._game.sprite_groups[objType]:
				if s.ID not in self.WBP.objIDs.keys():
					if s.name=='bullet':
						s.ID = len([o for o in vrle._game.sprite_groups[objType] if o not in vrle._game.kill_list])
					else:
						s.ID = len(vrle._game.sprite_groups[objType])
					self.WBP.objIDs[s.ID] = (len(self.WBP.objIDs.keys())+1) * (self.rle.outdim[0]*self.rle.outdim[1]+self.WBP.padding)
					i+=1
		return

	def isTerminal(self):
		return self.rle._isDone()[0]

	def isWin(self):
		return self.rle._isDone()[1]

	def playBack(self):
		vrle = copy.deepcopy(self.rle)
		terminal = vrle._isDone()[0]
		i=0
		print vrle.show()
		while not terminal:
			a = self.actionSeq[i]
			print actionDict[a]
			vrle.step(a)
			# vrle.step(0)
			print vrle.show()
			# print vrle.show()
			# embed()
			terminal = vrle._isDone()[0]
			i+=1

class IW(WBP):
	def __init__(self, rle, gameString, levelString, gameFilename, k):
		WBP.__init__(self, rle, gameString, levelString, gameFilename)
		self.k = k

if __name__ == "__main__":
	
	# gameFilename = "examples.gridphysics.simpleGame4_small"

	## make better versions
	# gameFilename = "examples.gridphysics.demo_teleport" ##solved!!
	# gameFilename = "examples.gridphysics.movers3c" ##solved!!
	# gameFilename = "examples.gridphysics.rivercross" ## solved!!
	# gameFilename = "examples.gridphysics.demo_dodge"  ##solved!!
	# gameFilename = "examples.gridphysics.movers5" ##solved!!
	# gameFilename = "examples.gridphysics.demo_preconditions" ## k=2 works!
	# gameFilename = "examples.gridphysics.waterfall" ##solved!! 
	# gameFilename = "examples.gridphysics.frogs" ## worked with k=2.
	# gameFilename = "examples.gridphysics.pick_apples" ## worked with expanded phi!
	# gameFilename = "examples.gridphysics.scoretest" ##2BFS solves it!
	# gameFilename = "examples.gridphysics.demo_chaser"  ##easy version solved!
	# gameFilename = "examples.gridphysics.demo_helper"  ##easy version solved!
	# gameFilename = "examples.gridphysics.simpleGame_push_boulders" 
	# gameFilename = "examples.gridphysics.chase" #yes!!!
	# gameFilename = "examples.gridphysics.survivezombies" # solvable, just not very fast if long timeout.
	# gameFilename = "examples.gridphysics.demo_transform_small" ## works

	# gameFilename = "examples.gridphysics.demo_helper"  ##
	# gameFilename = "examples.gridphysics.demo_transform" ##
	# gameFilename = "examples.gridphysics.simpleGame_missile" #later.
	# gameFilename = "examples.gridphysics.simpleGame_push_boulders2"

	# gameFilename = "examples.gridphysics.waypointtheory"  ##easy version solved!

	# gameFilename = "examples.gridphysics.simpleGame_push_boulders_multigoal" ## k=2 works!
	# gameFilename = "examples.gridphysics.simpleGame4"

	# gameFilename = "examples.gridphysics.simpleGame4_small"

	# gameFilename = "examples.gridphysics.demo_multigoal_and_score"  ##easy version solved!
	# gameFilename = "examples.gridphysics.demo_sokoban" #later
	# gameFilename = "examples.gridphysics.demo_sokoban_score" #later
	# gameFilename = "examples.gridphysics.portals" ## stochasticity breaks it

	# gameFilename = "examples.gridphysics.demo_multigoal_and"  ##takes forever if you have many boxes and don't use 2BFS (with metabolic penalty)


	## Continuous physics games can't work right now. RLE is discretized, getSensors() relies on this, and a lot of the induction/planning
	## architecture depends on that. Will take some work to do this well. Best plan is to shrink the grid squares and increase speeds/strengths of 
	## objects.
	gameFilename = "examples.continuousphysics.mario"
	# gameFilename = "examples.gridphysics.boulderdash" #Game is buggy.
	# gameFilename = "examples.gridphysics.butterflies" #Game is buggy.


	gameString, levelString = defInputGame(gameFilename, randomize=True)
	rleCreateFunc = lambda: createRLInputGame(gameFilename)
	rle = rleCreateFunc()
	p = IW(rle, gameString, levelString, gameFilename, k=2)
	# embed()
	# p.trackTokens = True
	t1 = time.time()
	# last, visited, rejected = BFS_noNovelty(rle, p)
	# last, visited, rejected = BFS(rle, p)
	# last, visited, rejected = BFS2(rle, p)
	last, visited, rejected = BFS3(rle, p)

	print time.time()-t1
	print len(visited), len(rejected)
	embed()


# 