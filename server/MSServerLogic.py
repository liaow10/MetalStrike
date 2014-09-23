
import sys
import time

import MSService
import MSSession
import MSModule
import MSModuleAccount
import MSModuleGameEntrance

import MSModuleTreasureMode
import MSModuleAdventureMode

import MSModuleStore

import MSMessage

class MSServerLogic(MSService.Service):
	def __init__(self, network, dbMgr, svrDispatcher):
		super(MSServerLogic,self).__init__(MSService.SERVICE_PLAYER_CONNECTION)
		print 'Game server started'
		self.network = network
		self.database = dbMgr

		self.spiritGenTime = None
		try:
			timeFile = open('LastSpiritGenDay.txt')
			t = timeFile.readline()
			t = float(t)
			self.spiritGenTime = time.localtime(t)
			timeFile.close()
		except:
			timeFile = open('LastSpiritGenDay.txt','w')
			timeFile.write(str(time.time()))
			timeFile.close()
			self.spiritGenTime = time.localtime(time.time())

		self.rankUpdateDay = None
		try:
			weekFile = open('LastRankUpdateDay.txt')
			t = weekFile.readline()
			t = int(t)
			self.rankUpdateDay = t
			weekFile.close()
		except:
			weekFile = open('LastRankUpdateDay.txt','w')
			t = time.localtime(time.time())
			weekFile.write(str(t.tm_yday))
			weekFile.close()
			self.rankUpdateDay = t.tm_yday




		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_CONNECT, 
			self.serviceID,
			MSService.ACTION_PLAYER_CONNECT)
		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_BEAT,
			self.serviceID,
			MSService.ACTION_PLAYER_BEAT)
		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_DISCONNECT,
			self.serviceID,
			MSService.ACTION_PLAYER_DISCONNECT)

		####################
		# common requrest, such as store.
		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_ENTER_STORE,
			self.serviceID,
			MSService.ACTION_PLAYER_ENTER_STORE)


		self.registerHandler(MSService.ACTION_PLAYER_CONNECT, self.onClientConnected)
		self.registerHandler(MSService.ACTION_PLAYER_BEAT, self.onClientBeat)
		self.registerHandler(MSService.ACTION_PLAYER_DISCONNECT, self.onClientDisconnected)
		self.registerHandler(MSService.ACTION_PLAYER_ENTER_STORE, self.onPlayerEnterStore)

		svrDispatcher.register(self.serviceID, self)

		self.modules = {
			MSModule.MSPLAYER_STAGE_ACCOUNT : MSModuleAccount.MSModuleAccount(network, dbMgr, svrDispatcher, self.transferSession),
			MSModule.MSPLAYER_STAGE_GAME_ENTRANCE : MSModuleGameEntrance.MSModuleGameEntrance(network, dbMgr, svrDispatcher, self.transferSession),
			
			# MSModule.MSPLAYER_STAGE_GEAR_EVOLUTION : MSModuleGearEvolution.MSModuleGearEvolution(network, dbMgr, svrDispatcher, self.transferSession),
			# MSModule.MSPLAYER_STAGE_GEAR_UPGRADE : MSModuleGearUpgrade.MSModuleGearUpgrade(network, dbMgr, svrDispatcher, self.transferSession),
			
			# MSModule.MSPLAYER_STAGE_ACTOR : MSModuleActor.MSModuleActor(network, dbMgr, svrDispatcher, self.transferSession),

			MSModule.MSPLAYER_STAGE_GAME_TREASURE_MODE : MSModuleTreasureMode.MSModuleTreasureMode(network, dbMgr, svrDispatcher, self.transferSession),
			MSModule.MSPLAYER_STAGE_GAME_ADVENTURE_MODE : MSModuleAdventureMode.MSModuleAdventureMode(network, dbMgr, svrDispatcher, self.transferSession),

			MSModule.MSPLAYER_STAGE_STORE : MSModuleStore.MSModuleStore(network, dbMgr, svrDispatcher, self.transferSession),
		}

		#svrDispatcher.registerHandler()

		self.sessionCache = {
			
		}

	def onClientConnected(self, rqst, owner):
		ses = self.sessionCache.get(owner, None)
		if ses == None:
			ses = MSSession.MSSession(owner)
			data = {'msg':'welcome', 'time':time.time()}
			self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_WELCOME, data))
			self.modules[MSModule.MSPLAYER_STAGE_ACCOUNT].openSession(ses)
			self.sessionCache[owner] = self.modules[MSModule.MSPLAYER_STAGE_ACCOUNT]

	def onClientBeat(self, rqst, owner):
		pass

	def onClientDisconnected(self, rqst, owner):
		ses = self.sessionCache.get(owner, None)
		if ses != None:
			session = ses.getSession(owner)
			ses.closeSession(owner)
			self.modules[MSModule.MSPLAYER_STAGE_ACCOUNT].handlePlayerDisconnected(session)
			del self.sessionCache[owner] 

	def onPlayerEnterStore(self, rqst, owner):
		ses = self.sessionCache.get(owner, None)
		if ses != None:
			session = ses.getSession(owner)
			self.transferSession(session, MSModule.MSPLAYER_STAGE_STORE)


	def transferSession(self, session, stage):
		stg = self.modules[stage]
		if stg != None:
			prevStage = self.sessionCache.get(session.getNetHandle(), None)
			if prevStage != None:
				for k, v in self.modules.items():
					if v == prevStage:
						session.setPrevStage(k)
						break
				
				prevStage.closeSession(session.getNetHandle())
				del self.sessionCache[session.getNetHandle()] 
				session.setCurStage(stage)
				stg.openSession(session)
				self.sessionCache[session.getNetHandle()] = stg


	def updateGame(self):
		curTime = time.localtime(time.time())
		if curTime.tm_mday != self.spiritGenTime.tm_mday:
			try:
				timeFile = open('LastSpiritGenDay.txt', 'w')
				timeFile.write(str(time.time()))
				timeFile.close()
				self.database.restoreSpiritPurchaseChanse()

			except:
				pass

		isLeapYear = False
		if ((curTime.tm_year % 4) == 0 and (curTime.tm_year % 100 != 0)) and (curTime.tm_year % 400 == 0):
			isLeapYear = True

		dayBase = 365 if isLeapYear else 366


		if (dayBase + curTime.tm_yday) - (dayBase + self.rankUpdateDay) > 7: 
			try:
				weekFile = open('LastRankUpdateDay.txt','w')
				weekFile.write(str(curTime.tm_yday))
				weekFile.close()
				self.rankUpdateDay = curTime.tm_yday
				self.database.updateTreasureRank([])
			except:
				pass

		self.spiritGenTime = curTime
		


