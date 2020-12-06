
class Pattern:
	def __init__(self, pattern: dict):
		self.pattern = pattern

	def getVuln(self):
		''' return name of vulnerability'''
		return self.pattern['vulnerability']

	def getSources(self):
		''' return list of sources'''
		return self.pattern['sources']

	def getSinks(self):
		''' return list of sinks'''
		return self.pattern['sinks']

	def getSanitizers(self):
		''' return list of sanitizers'''
		return self.pattern['sanitizers']

class Graph:
	def __init__(self):
		self.nodes = {}
		self.memberNodes = {}
		self.abstractNodes = {}

	def addNode(self, identifier, rightIdentifier=None):
		if not identifier in self.nodes:
			if rightIdentifier == None:
				self.nodes[identifier] = identifier
			else:
				self.nodes[identifier] = rightIdentifier
	
	def addAbstractNode(self, identifier):
		if not identifier in self.abstractNodes:
			self.abstractNodes[identifier] = []

	def addMemberNode(self, identifier):
		self.memberNodes[identifier] = identifier
		
