
import MSService
import MSMessage
import MSSession
import MSModule
import MSServerLogic
import MSItems
import random
from bson.objectid import ObjectId

class MSModuleTreasureMode(MSModule.Module):
	def __init__(self, network, dbMgr, svrDispatcher, sesTransfer):
		super(MSModuleTreasureMode, self).__init__(MSService.SERVICE_PLAYER_TREASURE_MODE, network, dbMgr, svrDispatcher, sesTransfer)

		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_FETCH_TREASURE_MODE_DATA, self.serviceID,
			MSService.ACTION_PLAYER_FETCH_TREASURE_DATA)
		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_LEAVE_TREASURE_MODE, self.serviceID,
			MSService.ACTION_PLAYER_LEAVE_TREASURE_MODE)

		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_TREASURE_GAME_OVER,	self.serviceID,
			MSService.ACTION_PLAYER_TREASURE_GAME_OVER)
		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_START_TREASURE,	self.serviceID,
			MSService.ACTION_PLAYER_START_TREASURE)


		self.registerHandler(MSService.ACTION_PLAYER_FETCH_TREASURE_DATA, self.handlePlayerFetchData)
		self.registerHandler(MSService.ACTION_PLAYER_LEAVE_TREASURE_MODE, self.handlePlayerLeave)
		self.registerHandler(MSService.ACTION_PLAYER_TREASURE_GAME_OVER, self.handlePlayerGameOver)
		self.registerHandler(MSService.ACTION_PLAYER_START_TREASURE, self.handlePlayerStart)
		

		svrDispatcher.register(self.serviceID, self)
		

	# sub-class implement this method.
	def onSessionOpen(self, session):
		session.data['TreasureStarted'] = False
		#self.transferCallback(session, MSModule.MSPLAYER_STAGE_REGISTER)
		print ('session opened in TreasureMode %s')%(session.data['Nick'])
		
	# sub-class implement this method.
	def onSessionClose(self, session):
		del session.data['TreasureStarted']
		#self.transferCallback(session, MSModule.MSPLAYER_STAGE_REGISTER)
		print ('session closed in TreasureMode %s')%(session.data['Nick'])
	
	def handlePlayerFetchData(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_TREASURE_MODE_DATA, {}))

	def handlePlayerGameOver(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			try:
				pid = ObjectId(rqst.data['pid'])
				if pid != ses.data['_id']:
					return
				if ses.data['TreasureStarted'] == False:
					return

				itemTable = {
					'Main':[MSItems.MSWEAPON_TYPE_MACHINEGUN, MSItems.MSWEAPON_TYPE_SHOTGUN, MSItems.MSWEAPON_TYPE_LASERGUN],
					'Armor':[MSItems.MSARMOR_TYPE_STRIKE, MSItems.MSARMOR_TYPE_THUNDER, MSItems.MSARMOR_TYPE_GUARDIAN],
					'Secondary':[MSItems.MSWEAPON_TYPE_DESERT_FOX, MSItems.MSWEAPON_TYPE_DEATH_PULSE, MSItems.MSWEAPON_TYPE_MISSILE],
				}

				playerData = self.database.fetchPlayerData(pid)
				actorName = playerData['actorInUse']
				playerActor = playerData['Actor'][actorName]

				ret = {
					'Main':[],
					'Armor':[],
					'Secondary':[],
				}
				for i in rqst.data['chest']:
					part = random.randint(1,3)
					if part == 1:
						part = 'Main'
					elif part == 2:
						part = 'Secondary'
					else:
						part = 'Armor'

					qlt = random.uniform(0.0, 1.0)
					star = ''
					if qlt >= 0.0 and qlt < 0.75:
						star = '2'
					elif qlt >= 0.75 and qlt < 0.95:
						star = '3'
					else:
						star = '4'

					iid = self.database.generateItemID()
					itm = {
						'_id':iid,
						'type':itemTable[part][random.randint(0,2)],
						'star':star,
						'exp':0,
						'level':1,
					}


					self.database.addEquipToArsenal(pid, part, itm)
					ret[part].append(itm)

				if rqst.data['prop'].get('Coin',None) != None:
					pprop = self.database.fetchPlayerProperty(pid)
					pprop['Coins'] += max(0, rqst.data['prop']['Coin'])
					self.database.updatePlayerProperty(pid, pprop)

				ses.data['TreasureStarted'] = False
				curScore = rqst.data['score']
				historyHigh = playerData['HistoryHighScore']
				if historyHigh < curScore:
					self.database.updatePlayerHistoryHighScore(ses.data['_id'], curScore)

				rank = self.database.getTreasureRank()
				# record format
				rankItem = {
					'actor': actorName,
					'level': playerActor['level'],
					'nick': ses.data['Nick'],
					'score': curScore,
					'uid': playerData['uid'],
				}

				confirmInsert = True

				for i in rank:
					if i['uid'] == rankItem['uid']:
						if curScore > i['score']:
							rank.remove(i)
							confirmInsert = True
						else:
							confirmInsert = False
						break

				if confirmInsert:
					rank.append(rankItem)
					rank.sort(key = lambda x: x['score'])
					rank.reverse()

					self.database.updateTreasureRank(rank)

				self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_TREASURE_CASH_UP, ret))
			except:
				print ('tresure cash up failed %s')%(ses.data['Nick'])		


	def handlePlayerStart(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			try:
				pid = ObjectId(rqst.data['pid'])
				if pid != ses.data['_id']:
					return
				pprop = self.database.fetchPlayerProperty(ses.data['_id'])
				if pprop['Spirit'] >= 2:
					pprop['Spirit'] -= 2
					self.database.updatePlayerProperty(ses.data['_id'], pprop)
					ses.data['TreasureStarted'] = True
			except:
				print ('start treasure failed %s')%(ses.data['Nick'])	



	def handlePlayerLeave(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_LEAVE_TREASURE_MODE_CONFIRM, {}))
			self.transferCallback(ses, MSModule.MSPLAYER_STAGE_GAME_ENTRANCE)