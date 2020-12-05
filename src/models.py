
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
