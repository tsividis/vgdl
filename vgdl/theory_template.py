#Template for theory file

class Theory(object):
	#theories are with respect to a base object. E.g., self ORANGE bounceForward
	def __init__(self, color):
		self.color = color
		self.oType = False #extend this to a set of types and a distribution over them?
		self.terms = [\
						#1	self wall undoAll
						#2	self box bounceForward
						#	[self mushroom killSprite, self mushroom killIfHasLess resource=medicine limit=-1
						] #a list of 

		self.discarded = [\
						# 
							]
	#def printToTxt(self):
		#creates relevant lines of interaction set, etc.

	#To prevent storing duplicate theories (e.g., box wall interactions in the box theories
	#and in the wall theories), have a checklist at the top of possible non-agent pairs and 
	#manage which new theories you create there? or just make everything but don't print twice?

