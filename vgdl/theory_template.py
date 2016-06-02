#Template for theory file

class Theory(object):
	#theories are with respect to a base object. E.g., self ORANGE bounceForward
	def __init__(self, color):
		self.color = color
		self.oType = False #extend this to a set of types and a distribution over them?
		self.terms = [] #a list of 


	#def printToTxt(self):
		#creates relevant lines of interaction set, etc.
