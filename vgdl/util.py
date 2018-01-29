from IPython import embed
import itertools
import random
import csv
import cPickle

ALNUM = '0123456789bcdefhijklmnpqrstuvwxyzQWERTYUIOPSDFHJKLZXCVBNM,./;[]<>?:`-=~!@#$%^&*()_+'
CHARS = 'bcdefhijklmnpqrstuvwxyzQWERTYUIOPSDFHJKLZXCVBNM'
CAPCHARS = 'QWERTYUIOPSDFHJKLZXCVBNM'

def softmax(w, t = 1.0):
    e = np.exp(np.array(w) / t)
    dist = e / np.sum(e)
    return dist

def normalize(array):
	z = float(sum(array))
	if z == 0:
		return [1./len(array)]*len(array) #if all items have the same score of 0, return the same score for all.
	else:
		return [a/z for a in array]

def manhattanDist(a, b):
	return abs(a[0]-b[0])+abs(a[1]-b[1])

def manhattanDist2(s1, s2, d=30):
	"""
	Function giving the right decimal Manhattan distance (including non-integer)
	s1, s2: sprites
	d: grid spacing
	"""
	dist = 1.*abs(s1.rect.left-s2.rect.left)/d + \
		   1.*abs(s1.rect.top-s2.rect.top)/d
	return dist

def factorize(rle, n):
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

def objectsToSymbol(rle, objects, symbolDict):
	objects = [rle._game.sprite_groups[o][0].colorName for o in objects]
	try:
		if len(objects)==1:
			if objects[0] not in symbolDict.keys():
				idx = len(symbolDict.keys())
				symbolDict[objects[0]] = ALNUM[idx]
			return symbolDict[objects[0]]
		else:
			for item in itertools.permutations(objects):
				if tuple(item) in symbolDict.keys():
					return symbolDict[tuple(item)]

		if not any([tuple(k) in symbolDict.keys() for k in list(itertools.permutations(objects))]):
			idx = len(symbolDict.keys())
			symbolDict[tuple(objects)] = ALNUM[idx]
			return ALNUM[idx]
	except:
		import ipdb; ipdb.set_trace()
		print "objectsToSymbol problem."
		embed()

def extendColorDict(num):
	for i in range(num):
		colorName = make_random_name(CAPCHARS)
		color = (random.choice(range(256)), random.choice(range(256)), random.choice(range(256)))
		print colorName + '=' + str(color)
		colorDict[str(color)] = colorName
	print colorDict

def make_random_name(chars):
	import random
	name = ''
	for i in range(6):
		name+=random.choice(chars)
	return name

def write_to_csv(filename, game):
	
	f = open(filename, 'a+') ##append, but also read.
	writer = csv.writer(f)
	if len(f.readlines())==0:
		writer.writerow(('subject', 'condition', 'gameName', 'levels_won', 'steps', 'score'))
	episodes = game['episodes']
	steps, levels_won, score = 0, 0, 0
	for episode in episodes:
		steps += episode[1]
		levels_won += episode[2]
		if episode[3] is not None:
			score +=episode[3]
		else:
			score = None
		writer.writerow((game['modelType'], game['condition'], game['gameName'], levels_won, steps, score))
	f.close()

def ccopy(obj):
	return cPickle.loads(cPickle.dumps(obj))
