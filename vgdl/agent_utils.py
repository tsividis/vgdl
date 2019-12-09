from ontology import distributionInitSetup
from WBP import *
import time
from termcolor import colored

def translate_events(events, all_objects, rle):
	if events is None:
		return None

	def get_object_color(objectID):
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
		try:
			if len(event) > 3:
				tmp = [event[0], get_object_color(event[1]), get_object_color(event[2])]
				for k in event[3].keys():
					if k=='stype':
						event[3][k] = get_object_color(event[3][k])
				tmp.extend(event[3:])
				outlist.append(tuple(tmp))
			if len(event)==3:
				outlist.append((event[0], get_object_color(event[1]), get_object_color(event[2])))
			elif len(event)==2:
				outlist.append((event[0], get_object_color(event[1])))
		except:
			print "translate_events failed"
			embed()

	#Make sure events in timestep are unique (don't want to double-count things)
	uniqueEventList = []
	for o in outlist:
		if o not in uniqueEventList:
			uniqueEventList.append(o)
	if len(uniqueEventList)>0:
		print uniqueEventList
	return uniqueEventList


def observe(rle, memory, obsSteps, bestSpriteTypeDict, display=False):
	if display:
		print "observing for {} steps".format(obsSteps)
	if obsSteps>0:
		for i in range(obsSteps):
			spriteInduction(rle._game, memory, step=1, bestSpriteTypeDict=bestSpriteTypeDict)
			spriteInduction(rle._game, memory, step=2, bestSpriteTypeDict=bestSpriteTypeDict)
			rle.step((0,0))
			if display:
				print "score: {}, game tick: {}".format(rle._game.score, rle._game.time)
				print rle.show(color='blue')

			rle._game.nextPositions = {}
			for k, v in rle._game.all_objects.iteritems():
				rle._game.nextPositions[k] = (int(rle._game.all_objects[k]['sprite'].rect.x), int(rle._game.all_objects[k]['sprite'].rect.y))
				try:
					if rle._game.previousPositions[k] != rle._game.nextPositions[k]:
						rle._game.objectMemoryDict[k] = copy.deepcopy(rle._game.previousPositions[k])
				except KeyError:
					pass
			rle._game.previousPositions = copy.deepcopy(rle._game.nextPositions)

			spriteInduction(rle._game, memory, step=3, bestSpriteTypeDict=bestSpriteTypeDict)
	else:
		spriteInduction(rle._game, memory, step=1, bestSpriteTypeDict=bestSpriteTypeDict)
		spriteInduction(rle._game, memory, step=2, bestSpriteTypeDict=bestSpriteTypeDict)
	return