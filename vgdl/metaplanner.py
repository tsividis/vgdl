from ontology import distributionInitSetup, spriteInduction

def translateEvents(events, all_objects, rle):
	if events is None:
		return None
	# all_objects = rle._game.getObjects()

	def getObjectColor(objectID):
		if objectID is None:
			return None
		elif objectID == 'EOS':
			return 'ENDOFSCREEN'
		elif objectID in all_objects.keys():
			return all_objects[objectID]['type']['color']
		elif objectID in rle._game.getObjects().keys():
			return rle._game.getObjects()[objectID]['type']['color']
		elif objectID in [colorDict[k] for k in colorDict.keys()]:
			# If we were passed a color to begin with (i.e., in the case of EOS)
			return objectID
		elif objectID in rle._game.sprite_groups.keys():
			return colorDict[str(rle._game.sprite_groups[objectID][0].color)]
		elif objectID in [obj.ID for obj in rle._game.kill_list]:
			objectColor = [obj.color for obj in rle._game.kill_list
				if obj.ID==objectID][0]
			return colorDict[str(objectColor)]
		else:
			# for some reason we haven't been passed an ID but rather a sprite object
			objectName = objectID.name
			color = [all_objects[k]['type']['color'] for k in all_objects.keys() if all_objects[k]['sprite'].name==objectName][0]
			return color

	outlist = []
	for event in events:
		# if 'EOS' in event:
		# 	print "in translateEvents"
		# 	embed()
		try:
			# print 'in translateEvents', event
			if len(event) > 3:
				tmp = [event[0], getObjectColor(event[1]), getObjectColor(event[2])]
				for k in event[3].keys():
					if k=='stype':
						event[3][k] = getObjectColor(event[3][k])
				tmp.extend(event[3:])
				outlist.append(tuple(tmp))
			if len(event)==3:
				outlist.append((event[0], getObjectColor(event[1]), getObjectColor(event[2])))
			elif len(event)==2:
				outlist.append((event[0], getObjectColor(event[1])))
		except:
			print "translateEvents failed"
			embed()

	#Make sure events in timestep are unique (don't want to double-count things)
	uniqueEventList = []
	for o in outlist:
		if o not in uniqueEventList:
			uniqueEventList.append(o)
	if len(uniqueEventList)>0:
		print uniqueEventList
	return uniqueEventList


def observe(rle, obsSteps, bestSpriteTypeDict):
	print "observing for {} steps".format(obsSteps)
	if obsSteps>0:
		for i in range(obsSteps):
			# print rle.show()
			spriteInduction(rle._game, step=1, bestSpriteTypeDict=bestSpriteTypeDict, action=None)
			spriteInduction(rle._game, step=2, bestSpriteTypeDict=bestSpriteTypeDict, action=None)

			rle.step((0,0))

			rle._game.nextPositions = {}
			for k, v in rle._game.all_objects.iteritems():
				rle._game.nextPositions[k] = (int(rle._game.all_objects[k]['sprite'].rect.x), int(rle._game.all_objects[k]['sprite'].rect.y))
				try:
					if rle._game.previousPositions[k] != rle._game.nextPositions[k]:
						rle._game.objectMemoryDict[k] = copy.deepcopy(rle._game.previousPositions[k])
				except KeyError:
					pass
			rle._game.previousPositions = copy.deepcopy(rle._game.nextPositions)

			# pinkID = [k for k in rle._game.all_objects.keys() if rle._game.all_objects[k]['features']['color']=='PINK'][0]
			# print "prev position", rle._game.previousPositions[pinkID]
			# print "memoryDict", rle._game.objectMemoryDict[pinkID]
			# print "curr position", rle._game.all_objects[pinkID]['sprite'].rect

			spriteInduction(rle._game, step=3, bestSpriteTypeDict=bestSpriteTypeDict)
	else:
		spriteInduction(rle._game, step=1, bestSpriteTypeDict=bestSpriteTypeDict, action=None)
		spriteInduction(rle._game, step=2, bestSpriteTypeDict=bestSpriteTypeDict, action=None)
		# spriteInduction(rle._game, step=3)
	return