from multiprocessing import Process, Pool, Manager
from rlenvironmentnonstatic import *
import sys
import WBP

#def g(x):
#	return x*x

#def f(rle, gameFilename, args):
#	p = WBP.WBP(rle,gameFilename, limit=args)
#	#return p.BFS()
#	return args


if __name__ == '__main__':



	gameFilename = "examples.continuousphysics.avoid_goomba"
	gameString, levelString = defInputGame(gameFilename, randomize=True)
	rleCreateFunc = lambda: createRLInputGame(gameFilename)
	rle = rleCreateFunc()
	
	#pool = Pool(processes = 4)
	#results = pool.map(f,[(rle,gameFilename,i) for i in [1,2]])
	#print pool.map(g,range(10))
	#embed()
	'''
	p = WBP.WBP(rle, gameFilename)
	p1 = Process(target = p.BFS)
	x = p1.start()
	p2 = Process(target = count)
	p2.start()
	embed()
	'''
	manager = Manager()
	results = manager.dict()
	results[1] = 1
	results[2] = 2
	plan1 = WBP.WBP(rle,gameFilename,limit=2)
	p1 = Process(target = plan1.BFS, args=(1,results))

	plan2 = WBP.WBP(rle,gameFilename,limit=1)
	p2 = Process(target = plan2.BFS, args=(2,results))

	p1.start()
	p2.start()
	#p1.join()
	#p2.join()

	#print(results)
