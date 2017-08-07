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
		self.states = []
		self.actions = [0]
		self.error = 40
		#self.speed_array = [[],[],[],[]]
		self.speed_array = []
		self.ball_array = []

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


	#general update function for all sprites
	
	def InitializeSprites(self,rle,objects):
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

							sprite.rect.x = new_locs[i][0]
							sprite.rect.y = new_locs[i][1]
							
							if not isinstance(sprite,vgdl.ontology.Immovable):
								vec = (sprite.rect.x-sprite.lastrect.x,sprite.rect.y-sprite.lastrect.y)
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
						rle._game.sprite_groups[k].append(new_sprite)
		return changed
	

	def updateSprites(self,rle,objects,ended = False):
		changed = False
		#ball:
		try:
			new =  objects['ball']
		except:
			new = []
		old = [o for o in rle._game.sprite_groups['ball'] if o not in rle._game.kill_list]
		if new and old:
			new_loc = new[0]
			old_loc = self.states[-2]['ball'][0]
			ball = old[0]
			vec = (new_loc[0] - old_loc[0], new_loc[1] - old_loc[1])
			self.ball_array.append(vectNorm(vec))
			if ended or abs(ball.rect.x - new_loc[0]) > self.error or abs(ball.rect.y - new_loc[1]) > self.error:
				ball.rect.x = new_loc[0]
				ball.rect.y = new_loc[1]
				ball.speed = mean(self.ball_array)
				ball.orientation = unitVector(vec)
				changed = True
		elif old:
			ball = old[0]
			rle._game.kill_list.append(ball)
			changed = True
		elif new:
			new_sprite = copy.deepcopy(rle._game.sprite_groups['ball'][0])
			loc = new[0]
			new_sprite.rect.x = loc[0]
			new_sprite.rect.y = loc[1]
			rle._game.sprite_groups['ball'].append(new_sprite)
			changed = True

		#avatar:
		new_loc = objects['avatar'][0]
		avatar = rle._game.sprite_groups['avatar'][0]
		old_loc = self.states[-2]['avatar'][0]
		speed = vectNorm((new_loc[0] - old_loc[0],new_loc[1] - old_loc[1]))/self.square_size
		if speed != 0:
			self.speed_array.append(speed)

		if ended or changed or abs(avatar.rect.x - new_loc[0]) > self.error or abs(avatar.rect.y - new_loc[1]) > self.error:
			avatar.rect.x = new_loc[0]
			avatar.rect.y = new_loc[1]
			if speed != 0 and self.actions[-1] != 0:
				print 'updating'
				avatar.speed = mean(self.speed_array)
				'''
				a1 = self.actions[-1]
				a0 = self.actions[-2]
				if a1 in [2,3]:
					if a0 == 0:
						self.speed_array[0].append(speed)
						avatar.c1 = mean(self.speed_array[0])
					elif a1 == a0:
						self.speed_array[2].append(speed)
						avatar.c3 = mean(self.speed_array[2])
					else: 
						self.speed_array[3].append(speed)
						avatar.c4 = -mean(self.speed_array[3])
				elif a0 in [2,3]:
					self.speed_array[1].append(speed)
					avatar.c2 = mean(self.speed_array[1])
				'''
			changed = True

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

		embed()
		
		p = WBP(self.rle,gameFilename,max_nodes=max_nodes)

		visualizer = ContinuousVisualizer({'agent': (0,1,0), 'ball': (0,0,1), 'goal': (1,0,0), 'wall':(0.33,0.33,0.33)})

		#updateSprites to initialize game
		#self.setDimensions(self.rle,objects)
		object_dict = self.makeDict(objects)
		self.states.append(object_dict)
		self.actions.append(0)
		self.InitializeSprites(self.rle,object_dict)
		#print object_dict['ball']
		#print self.rle._game.sprite_groups['ball']
		#embed()
		
		last, visited, length = p.BFS(return_best = True)
		print last.actionSeq
		path = self.getPath(last)
		#embed()
		i = 1

		for j in tqdm(range(200)):#FILL (handle later maybe)

			#if j >= 10:
				#embed()
			'''
			action = 276
			print("action = {}".format(action))
			objects, _raw = env.step(ACTIONS[action])
			object_dict = self.makeDict(objects)
			#print [i[1] for i in objects if i[0]=='agent']
			'''

			
			#embed()
			
			if len(path) > 1:
				self.rle = path[i].rle
				action = path[i].actionSeq[-1]
				print("action = {}".format(action))
				objects, _raw = env.step(ACTIONS[action])
				object_dict = self.makeDict(objects)
				self.states.append(object_dict)
				self.actions.append(ACTIONS[action])
				#print object_dict['avatar']
				#embed()
				#print object_dict['ball']
				#print self.rle._game.sprite_groups['ball']
			else:
				print("no action taken")
				env.step(1) #restart game
				#embed()

			print self.rle._game.sprite_groups['avatar']
			#print self.rle._game.sprite_groups['avatar'][0].speed
			print object_dict['avatar']

			try:
				print self.rle._game.sprite_groups['ball']
				print object_dict['ball']
			except:
				pass

			'''
			if i < len(path) -1 and i < 6:
				i+= 1
				print("NEXT")
			'''
				#self.updateSprites(self.rle,object_dict)
			if i >= len(path) - 1:
				ended = True
			else:
				ended = False
			if not self.updateSprites(self.rle,object_dict, ended):
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
			
def mean(array):
	return sum(array)/len(array)

if __name__ == '__main__':
	gameFilename = "examples.continuousphysics.breakout"
	rleCreateFunc = lambda: createRLInputGame(gameFilename)
	#rle = rleCreateFunc()

	ap = AtariPlanner()
	ap.plan(50)


			





