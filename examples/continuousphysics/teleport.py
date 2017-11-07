import WBP

class teleport_planner():
	def __init__(self):
		

if __name__ == '__main__':

	gameFilename = "examples.continuousphysics.montezuma_3"
	rleCreateFunc = lambda: createRLInputGameFromPositions(gameFilename)
	rle = rleCreateFunc()

	p = WBP(rle,gameFilename)

	avatar = p.getAliveAvatar(rle)