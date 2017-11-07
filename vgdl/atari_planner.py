from IPython import embed

import rlenvironmentnonstatic
from rlenvironmentnonstatic import createRLInputGameFromPositions
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
import math
sys.path.append('/Users/eshaannichani/gameplay')
from perception.simple import Breakout, ContinuousVisualizer, BreakoutPolicy

ACTIONS = {0:0,275:2, 276:3}
NODES_TO_SEARCH = 50

class AtariPlanner():

	def __init__(self):
		self.rle = None
		self.square_size = None
		self.states = []
		self.actions = [0]
		self.error = 28
		self.reground_threshhold = 120
		#self.speed_array = [[],[],[],[]]
		self.speed_array = []
		self.ball_array = []

	#initialize positions of sprites at beginning of game (NOT USED, since we create level from positions)
	def InitializeSprites(self,rle,objects):
		changed = False

		for k in rle._game.sprite_groups.keys():
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
							#dont want to modify speeds of objects cause they'll then be 0
							'''
							if not isinstance(sprite,vgdl.ontology.Immovable):
								vec = (sprite.rect.x-sprite.lastrect.x,sprite.rect.y-sprite.lastrect.y)
								if not isinstance(sprite.physics,vgdl.ontology.ContinuousPhysics):
									sprite.speed = vectNorm(vec)/self.square_size
								else:
									sprite.orientation = unitVector(vec)
									sprite.speed = vectNorm(vec)
							'''
							i+=1
						else:
							rle._game.kill_list.append(sprite) #don't realize a sprite is killed
				if i < len(new_locs):
					for loc in new_locs[i:]: #accidentally kill a sprite that shouldn't have been / don't realize sprite appearing
						new_sprite = copy.deepcopy(rle._game.sprite_groups[k][0])
						new_sprite.rect.x = loc[0]
						new_sprite.rect.y = loc[1]
						rle._game.sprite_groups[k].append(new_sprite)

		rle._game.sprite_groups['avatar'][0].speed = 2.0 #CHANGING SPEED
		rle._game.sprite_groups['ball'][0].speed = 20.0
		return changed
	
	#updating velocity + position of ball/avatar on each step, if we need to reground
	def updateSprites(self,rle,objects,ended = False):
		changed = False

		new_aloc = objects['avatar'][0]
		avatar = rle._game.sprite_groups['avatar'][0]
		old_aloc = self.states[-2]['avatar'][0]

		if abs(avatar.rect.x - new_aloc[0]) > self.error or abs(avatar.rect.y - new_aloc[1]) > self.error:
			changed = True

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
			#self.ball_array.append(vectNorm(vec))
			if changed or ended or abs(ball.rect.x - new_loc[0]) > self.error or abs(ball.rect.y - new_loc[1]) > self.error:
				ball.rect.x = new_loc[0]
				ball.rect.y = new_loc[1]
				#ball.speed = mean(self.ball_array)
				#ball.speed = 20.0
				ball.speed = (vectNorm(vec))
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
		
		#speed = vectNorm((new_loc[0] - old_loc[0],new_loc[1] - old_loc[1]))/self.square_size
		#if speed != 0:
		#	self.speed_array.append(speed)

		if ended or changed:
			avatar.rect.x = new_aloc[0]
			avatar.rect.y = new_aloc[1]
			#if speed != 0 and self.actions[-1] != 0:
				#print 'updating'
				#avatar.speed = mean(self.speed_array)
			changed = True

		return changed

	#return path from last node in BFS
	def getPath(self,last):
		node = last
		array = []
		while node is not None:
			array.insert(0,node)
			node = node.parent
			
		return array

	#turn list of (obj,pos) pairs into dictionary
	def makeDict(self,objects,grid=False):
		objs = {}
		for obj, pos in objects:
			#new_pos = (pos[1]*self.square_size,pos[0]*self.square_size)
			if grid:
				new_pos = (pos[1],pos[0])
			else:
				new_pos = (pos[1]*self.square_size,pos[0]*self.square_size)
			if obj in objs:
				objs[obj].append(new_pos)
			else:
				objs[obj] = [new_pos]

		
		avatars = objs['agent']
		#objs['avatar'] = [(sum(i[0] for i in avatars)/len(avatars),sum(i[1] for i in avatars)/len(avatars))]
		objs['avatar'] = [(min(i[0] for i in avatars),avatars[0][1])]
		objs['agent'] = []
		return objs

	#the loop between planning and ALE actions
	def plan(self, max_nodes):

		gameFilename = "examples.continuousphysics.breakout"
		env = Breakout()

		objects, _raw = env.reset()
		object_dict = {}
		i = 1
		while 'ball' not in object_dict.keys():
			print i
			objects, _raw = env.step(1)
			object_dict = self.makeDict(objects,grid=True)
			i += 1

		height= max([i[1][0] for i in objects]) + 1
		width = max([i[1][1] for i in objects]) + 1
		#create rle based on the objects returned from perception
		rleCreateFunc = lambda: createRLInputGameFromPositions(gameFilename, [(width,height),object_dict])
		self.rle = rleCreateFunc()

		self.square_size = self.rle._game.block_size

		p = WBP(self.rle,gameFilename,max_nodes=max_nodes)

		visualizer = ContinuousVisualizer({'agent': (0,1,0), 'ball': (0,0,1), 'goal': (1,0,0), 'wall':(0.33,0.33,0.33)})

		#Initialize the game
		object_dict = self.makeDict(objects)
		self.states.append(object_dict)
		self.actions.append(0)

		last, visited, length = p.BFS(return_best = True)
		print last.actionSeq
		path = self.getPath(last)
		i = 1
		no_ball = 0	
		pos = []

		#planning + updating rle loop
		for j in tqdm(range(20000)):
			
			if len(path) > 1:
				self.rle = path[i].rle
				action = path[i].actionSeq[-1]
				print("action = {}".format(action))
				objects, _raw = env.step(ACTIONS[action])
				object_dict = self.makeDict(objects)
				self.states.append(object_dict)
				self.actions.append(ACTIONS[action])

			else:
				print("no action taken")
				env.step(1) #restart game
			
			print self.rle._game.sprite_groups['avatar']
			print object_dict['avatar']
			try:
				print self.rle._game.sprite_groups['ball']
				print object_dict['ball']
				pos.append(object_dict['ball'][0])
				c = 1 - 0.5*self.rle._game.sprite_groups['ball'][0].width #for breakout
			except:
				no_ball += 1
				c = 0.75 #for breakout

			if no_ball > 1:
				print("restarting game")
				env.step(1)
				no_ball = 0
			
			#shift loc so we can line up center of squares
			avatar_loc = (object_dict['avatar'][0][0]+c*self.rle._game.block_size, object_dict['avatar'][0][1])
			
			#whether we reground or not
			if i >= len(path) - 1:
				ended = True
			elif 'ball' in object_dict.keys() and euclideanDist(object_dict['ball'][0],avatar_loc) < self.reground_threshhold:
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

			#visualizing gameplay
			screen = visualizer.vis(objects, _raw)
			scipy.misc.imsave('observations/%05d.png' % j, screen)
			
		
		

			
def mean(array):
	return sum(array)/len(array)

def euclideanDist(a,b):
	return math.sqrt(float((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2))

if __name__ == '__main__':
	ap = AtariPlanner()
	ap.plan(NODES_TO_SEARCH)


			





