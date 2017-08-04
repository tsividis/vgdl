from IPython import embed

import rlenvironmentnonstatic
from rlenvironmentnonstatic import createRLInputGameChangeLevel
from WBP import WBP
from tools import unitVector, vectNorm
import ontology
from ontology import GridPhysics, Immovable
import vgdl
import scipy.misc
from tqdm import tqdm
import sys
import random
import copy
import importlib
sys.path.append('/Users/eshaannichani/gameplay')
from perception.simple import Breakout, ContinuousVisualizer, BreakoutPolicy


ACTIONS = {0:0,275:2, 276:3}

class AtariPlanner():

	def __init__(self):
		self.rle = None
		self.square_size = None

	def createLevel(self, objects):
		height= max([i[1][0] for i in objects]) + 1
		width = max([i[1][1] for i in objects]) + 1
		string = ''
		for i in range(height):
			string += '\n'
			for j in range(width):
				string += ' '
		string = string[:-4]
		string += 'wgor'
		string += '\n'	
		return string

	def setDimensions(self,rle,objects):
		#embed()
		height= max([i[1][0] for i in objects]) + 1
		width = max([i[1][1] for i in objects]) + 1

		self.square_size = min(rle._game.screensize[0]/width,rle._game.screensize[1]/height)
		rle._game.block_size = self.square_size
		rle.outdim = [height,width]
		rle._game.screensize = (width*self.square_size,height*self.square_size)



	def updateSprites(self,rle,objects):
		changed = False
		#embed()
		for k in rle._game.sprite_groups.keys():
			#print k
			locs = set()
			for o in rle._game.sprite_groups[k]:
				if o not in rle._game.kill_list:
					locs.add((o.rect.x,o.rect.y))

			if k in objects:
				obj_locs = set(objects[k])
			else:
				obj_locs = set()

			if len(obj_locs ^ locs) != 0:
				changed = True
				new_locs = list(obj_locs - locs)
				i = 0
				can_change = True
				for sprite in rle._game.sprite_groups[k]:
					if i == len(new_locs):
						can_change = False
					if (sprite.rect.x,sprite.rect.y) not in obj_locs:
						if can_change:
							#print (sprite.rect.x,sprite.rect.y)
							#print (new_locs[i])
							sprite.rect.x = new_locs[i][0]
							sprite.rect.y = new_locs[i][1]
							#sprite.rect.width = self.square_size
							#sprite.rect.height = self.square_size
							#print isinstance(sprite,vgdl.ontology.Immovable)
							if not isinstance(sprite,vgdl.ontology.Immovable):
								vec = (sprite.rect.x-sprite.lastrect.x,sprite.rect.y-sprite.lastrect.y)
								
								#print isinstance(sprite.physics,vgdl.ontology.ContinuousPhysics)
								if not isinstance(sprite.physics,vgdl.ontology.ContinuousPhysics):
									sprite.speed = vectNorm(vec)/self.square_size
								else:
									sprite.orientation = unitVector(vec)
									sprite.speed = vectNorm(vec)
							i+=1
						else:
							rle._game.kill_list.append(sprite) #don't realize a sprite is killed
				if i < len(new_locs):
					for loc in new_locs[i:]: #accidentally kill a sprite that shouldn't have been / don't realize sprite appearing
						new_sprite = copy.deepcopy(rle._game.sprite_groups[k][0])
						new_sprite.rect.x = loc[0]
						new_sprite.rect.y = loc[1]
						#sprite.rect.width = self.square_size
						#sprite.rect.height = self.square_size
						rle._game.sprite_groups[k].append(new_sprite)
			

		return changed

	def getPath(self,last):
		node = last
		array = []
		while node is not None:
			array.insert(0,node)
			node = node.parent
			
		return array

	def makeDict(self,objects):
		objs = {}
		for obj, pos in objects:
			new_pos = (pos[1]*self.square_size,pos[0]*self.square_size)
			if obj in objs:
				objs[obj].append(new_pos)
			else:
				objs[obj] = [new_pos]

		##hardcoded in to get around there being 2 avatars for now, can remove when that is fixed
		avatars = objs['agent']
		objs['avatar'] = [(sum(i[0] for i in avatars)/len(avatars),sum(i[1] for i in avatars)/len(avatars))]
		objs['agent'] = []
		return objs

	def plan(self, max_nodes):

		gameFilename = "examples.continuousphysics.breakout"

		env = Breakout()

		objects, _raw = env.reset() 
		objects, _raw = env.step(1)


		level = self.createLevel(objects)

		rleCreateFunc = lambda: createRLInputGameChangeLevel(gameFilename,level)

		self.rle = rleCreateFunc()

		self.square_size = self.rle._game.block_size
		
		p = WBP(self.rle,gameFilename,max_nodes=max_nodes)

		visualizer = ContinuousVisualizer({'agent': (0,1,0), 'ball': (0,0,1), 'goal': (1,0,0), 'wall':(0.33,0.33,0.33)})

		#updateSprites to initialize game
		#self.setDimensions(self.rle,objects)
		object_dict = self.makeDict(objects)
		self.updateSprites(self.rle,object_dict)
		#print object_dict['ball']
		#print self.rle._game.sprite_groups['ball']
		#embed()
		
		last, visited, length = p.BFS(return_best = True)
		print last.actionSeq
		path = self.getPath(last)
		#embed()
		i = 1

		for j in tqdm(range(50)):#FILL (handle later maybe)

			if j >= 10:
				embed()
			'''
			action = 276
			print("action = {}".format(action))
			objects, _raw = env.step(ACTIONS[action])
			object_dict = self.makeDict(objects)
			#print [i[1] for i in objects if i[0]=='agent']
			print object_dict['avatar']
			'''
			#embed()
			
			if len(path) > 1:
				self.rle = path[i].rle
				action = path[i].actionSeq[-1]
				print("action = {}".format(action))
				objects, _raw = env.step(ACTIONS[action])
				object_dict = self.makeDict(objects)
				#print object_dict['avatar']
				#embed()
				#print object_dict['ball']
				#print self.rle._game.sprite_groups['ball']
			else:
				print("no action taken")
				#env.step(1) #restart game
				#embed()

			'''
			if i < len(path) -1 and i < 6:
				i+= 1
				print("NEXT")
			'''
				#self.updateSprites(self.rle,object_dict)
			if not self.updateSprites(self.rle,object_dict) and i < len(path)-1:
				i += 1
				print("NEXT")
			
			else:
				print("CHANGING")
				p = WBP(self.rle,gameFilename,max_nodes=max_nodes)
				last, visited, length = p.BFS(return_best = True)
				path = self.getPath(last)
				print last.actionSeq
				i = 1

			#if len(path) > 1:

			screen = visualizer.vis(objects, _raw)
			scipy.misc.imsave('observations/%05d.png' % j, screen)
			


if __name__ == '__main__':
	gameFilename = "examples.continuousphysics.breakout"
	rleCreateFunc = lambda: createRLInputGame(gameFilename)
	#rle = rleCreateFunc()

	ap = AtariPlanner()
	ap.plan(50)


			





