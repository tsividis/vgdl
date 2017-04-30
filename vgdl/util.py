
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