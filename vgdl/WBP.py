from IPython import embed
from planner import *


## Base class for width-based planners (IW(k) and 2BFS)
class WBP(Planner):
	def __init__(self, rle, gameString, levelString, gameFilename, display):
		Planner.__init__(self, rle, gameString, levelString, gameFilename, display)
		self.T = len(rle._obstypes.keys())+1 #number of object types. Adding avatar, which is not in obstypes.
		self.vecDim = [rle.outdim[0]*rle.outdim[1], self.T]
		self.noveltyDict = defaultdict(lambda:0)

	def calculateAtoms(self, rle):
		## Converts rle state into a long list of atoms of length NxT (N: num of grid cells. T: Number of object types in the game).
		## For a 3x5 grid, we first flatten into a single column of len=15. (rle._getSensors() already has this representation)
		## atomList(m,n): whether object n is at location m.

		# TODO: Make implementation that considers avatar orientations. See p.3 of Geffner|Geffner paper.

		vec = np.empty(self.vecDim)
		state = rle._getSensors()
		for i in range(len(state)):
			vec[i] = self.factorizeBoolean(rle, state[i])
			objIndicesAtLoc = self.factorizeBoolean(rle, state[i])
		return vec

	def factorize(self, rle, n):
		## Decomposes into a list of numbers that are incides of [avatar, rle._obstypes.keys()]
		## that correspond to which indices are present in n
		## this follows the convention of rle._getSensors(), which won't report two of the same number as being in a location, so
		## the decomposition is unique (e.g., if n=4, this is because the decomposition is [4], rather than having to worry that it
		## would be [2,2]).
		orig_n = n
		decomposition = []
		if n%2==1:
			decomposition.append(0)
			n = n-1
		i = len(rle._obstypes.keys())
		while i>0:
			if n>=2**i:
				decomposition.append(i)
				n = n-2**i
			i = i-1

		return decomposition

	def indicesToBooleans(self, listLen, indices):
		##turns a list of indices into an expanded list that has 0 if that index wasn't in the list and 1 if it was.
		## e.g., indicesToBooleans(8, [1,3,5]) = [0,1,0,1,0,1,0,0]
		out = []
		for i in range(listLen):
			if i in indices:
				out.append(1)
			else:
				out.append(0)
		return out

	def factorizeBoolean(self, rle, n):
		listLen = len(rle._obstypes.keys())+1
		return self.indicesToBooleans(self.T, self.factorize(rle, n))

	def novelty(self, factoredState):
		## returns the number of atoms that have are newly true (in the tree)
		
class IW(WBP):
	def __init__(self, rle, gameString, levelString, gameFilename, display, k):
		WBP.__init__(self, rle, gameString, levelString, gameFilename, display)
		self.k = k


if __name__ == "__main__":
	
	# gameFilename = "examples.gridphysics.simpleGame_teleport"
	# gameFilename = "examples.gridphysics.waypointtheory" 
	# gameFilename = "examples.gridphysics.demo_teleport"
	# gameFilename = "examples.gridphysics.movers3c"
	# gameFilename = "examples.gridphysics.scoretest" 
	# gameFilename = "examples.gridphysics.portals" 
	# gameFilename = "examples.gridphysics.pick_apples" 
	# gameFilename = "examples.gridphysics.demo_transform_small" 

	# gameFilename = "examples.gridphysics.demo_dodge" 
	# gameFilename = "examples.gridphysics.rivercross" 
	# gameFilename = "examples.gridphysics.demo_chaser" 

	# gameFilename = "examples.gridphysics.simpleGame4_small"

	gameFilename = "examples.gridphysics.overlaptest"

	gameString, levelString = defInputGame(gameFilename, randomize=True)
	rleCreateFunc = lambda: createRLInputGame(gameFilename)
	rle = rleCreateFunc()

	p = IW(rle, gameString, levelString, gameFilename, True, 1)

	embed()
