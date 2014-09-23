#######################
# hello this file defines the region that hanles players
# players are dipatched into different modules, and can do limited actions
# defined by each module

import sys
import MSService
import MSSession


MSPLAYER_STAGE_ACCOUNT			= 0x0000
MSPLAYER_STAGE_GAME_ENTRANCE	= 0x0102
MSPLAYER_STAGE_ACTOR			= 0x0150
MSPLAYER_STAGE_GAME_TREASURE_MODE	= 0x0200
MSPLAYER_STAGE_GAME_ADVENTURE_MODE	= 0x0201
MSPLAYER_STAGE_GEAR_EVOLUTION	= 0x0300
MSPLAYER_STAGE_GEAR_UPGRADE		= 0x0301
MSPLAYER_STAGE_STORE			= 0x0303


class Module(MSService.Service):
	def __init__(self, svcID, network, dbMgr, svrDispatcher, sesTransfer):
		super(Module, self).__init__(svcID)
		self.network = network
		self.database = dbMgr
		self.transferCallback = sesTransfer

		self.sessions = {}
		
	def openSession(self, session):
		self.sessions[session.getNetHandle()] = session
		self.onSessionOpen(session)

	# sub-class implement this method.
	def onSessionOpen(self, session):
		raise NotImplementedError


	def closeSession(self, sessionHandle):
		if self.sessions[sessionHandle] != None:
			self.onSessionClose(self.sessions[sessionHandle])
			del self.sessions[sessionHandle]

	# sub-class implement this method
	def onSessionClose(self, session):
		raise NotImplementedError

	def update(self):
		pass

	def getSession(self, handle):
		return self.sessions[handle]