from multiprocessing import Pool
#import sys
#import WBP
#from rlenvironmentnonstatic import *
 
def doubler(number):
    return number * 2

from rlenvironmentnonstatic import *
 
if __name__ == '__main__':
	gameFilename = "examples.continuousphysics.avoid_goomba"
	#gameString, levelString = defInputGame(gameFilename, randomize=True)
	#rleCreateFunc = lambda: createRLInputGame(gameFilename)
	#rle = rleCreateFunc()
	numbers = [5, 10, 20]
	pool = Pool(processes=3)
	result = pool.apply_async(doubler,numbers)

	print(result.get(timeout=1))