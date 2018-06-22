	def fastcopy(self, rle):
		newRle = self.empty_copy(rle)
		#embed()
		newRle._obstypes = rle._obstypes.copy()
		if hasattr(rle, '_gravepoints'):
			newRle._gravepoints = rle._gravepoints.copy()
		newRle.outdim = rle.outdim
		#ipdb.set_trace()
		newRle.symbolDict = rle.symbolDict.copy()
		newRle._other_types = rle._other_types[:]
		newRle._game = self.empty_copy(rle._game)
		ignoreKeys = ['spriteDistribution',
					  'object_token_spriteDistribution',
					  'spriteUpdateDict',
					  'movement_options',
					  'object_token_movement_options',
					  #'all_objects',
					  'uiud']
		sprite_attrs = ['name','resources','rect','x','y',
						'lastrect','lastmove','stypes',
						'speed','cooldown','direction','color','colorName']
		for k,v in rle._game.__dict__.iteritems():

			if k in ignoreKeys: continue

			ctype = str(type(getattr(rle._game,k)))

			if 'list' in ctype:
				if k != 'kill_list':
					newRle._game.__dict__[k] = v[:]
				else:
					newRle._game.kill_list = v[:]
			elif 'defaultdict' in ctype or 'dict' in ctype:
				if k != 'sprite_groups':
					newRle._game.__dict__[k] = v.copy()
				else:
					#embed()
					new_sprite_groups = defaultdict(list)
					for group_name, group in rle._game.sprite_groups.iteritems():
						for sprite in group:
							if sprite.colorName == 'DARKGRAY':
								new_sprite_groups[group_name].append(sprite)
							else:
								new_sprite = self.empty_copy(sprite)
								new_sprite.__dict__ = sprite.__dict__.copy()
								new_sprite_groups[group_name].append(new_sprite)
					# newRle._game.sprite_groups = ccopy(v)
					newRle._game.sprite_groups = new_sprite_groups
			elif 'vgdl' in ctype:
				newRle._game.__dict__[k] = ccopy(v)
			elif 'dict' in ctype:
				#print k
				newRle._game.__dict__[k] = v.copy()
			else:
				newRle._game.__dict__[k] = v
		#newRle._game = ccopy(rle._game)
		return newRle
