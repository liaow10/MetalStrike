# ah... session, indicating a connection to specified client.


class MSSession(object):
	def __init__(self, netHandle):
		#session ID?
		self.netHandle = netHandle
		self.prevStage = None
		self.curStage = None
		self.data = {}
		
	def getNetHandle(self):
		return self.netHandle

	def setPrevStage(self, stage):
		self.prevStage = stage

	def getPrevStage(self):
		return self.prevStage

	def setCurStage(self, stage):
		self.curStage = stage

	def getCurStage(self):
		return self.curStage
