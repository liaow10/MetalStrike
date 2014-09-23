
import MSService
import MSMessage
import MSSession
import MSModule
import MSServerLogic
import MSItems
import random
from bson.objectid import ObjectId

class MSModuleAdventureMode(MSModule.Module):
	def __init__(self, network, dbMgr, svrDispatcher, sesTransfer):
		super(MSModuleAdventureMode, self).__init__(MSService.SERVICE_PLAYER_ADVENTURE_MODE, network, dbMgr, svrDispatcher, sesTransfer)

		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_FETCH_ADVENTURE_MODE_DATA, 
			self.serviceID,
			MSService.ACTION_PLAYER_FETCH_ADVENTURE_DATA)
		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_LEAVE_ADVENTURE_MODE, 
			self.serviceID,
			MSService.ACTION_PLAYER_LEAVE_ADVENTURE_MODE)

		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_ADVENTURE_GAME_OVER,	self.serviceID,
			MSService.ACTION_PLAYER_ADVENTURE_GAME_OVER)
		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_START_ADVENTURE,	self.serviceID,
			MSService.ACTION_PLAYER_START_ADVENTURE)


		self.registerHandler(MSService.ACTION_PLAYER_FETCH_ADVENTURE_DATA, self.handlePlayerFetchData)
		self.registerHandler(MSService.ACTION_PLAYER_LEAVE_ADVENTURE_MODE, self.handlePlayerLeave)
		self.registerHandler(MSService.ACTION_PLAYER_ADVENTURE_GAME_OVER, self.handlePlayerGameOver)
		self.registerHandler(MSService.ACTION_PLAYER_START_ADVENTURE, self.handlePlayerStart)


		svrDispatcher.register(self.serviceID, self)
		
		self.chapterInfo = [
			[
				{
					'cost':5
				},
				{
					'cost':10
				},
				{
					'cost':15
				}
			]
		]
		self.chapterReward = [{
			1:{
				'Element':[MSItems.MSITEM_TYPE_SC,MSItems.MSITEM_TYPE_TI,MSItems.MSITEM_TYPE_V,MSItems.MSITEM_TYPE_CR,MSItems.MSITEM_TYPE_MN],
				'Material':MSItems.MSITEM_TYPE_MGALALLOY
			},
			2:{
				'Element':[MSItems.MSITEM_TYPE_FE,MSItems.MSITEM_TYPE_CO,MSItems.MSITEM_TYPE_NI,MSItems.MSITEM_TYPE_CU,MSItems.MSITEM_TYPE_ZN],
				'Material':MSItems.MSITEM_TYPE_TUNGSTENSTEEL
			},
			3:{
				'Element':[MSItems.MSITEM_TYPE_Y,MSItems.MSITEM_TYPE_ZR,MSItems.MSITEM_TYPE_NB,MSItems.MSITEM_TYPE_MO,MSItems.MSITEM_TYPE_TC],
				'Material':MSItems.MSITEM_TYPE_TICRALLOY
			},
		}]


	# sub-class implement this method.
	def onSessionOpen(self, session):
		#self.transferCallback(session, MSModule.MSPLAYER_STAGE_REGISTER)
		print ('session opened in AdventureMode %s')%(session.data['Nick'])
		
	# sub-class implement this method.
	def onSessionClose(self, session):
		#self.transferCallback(session, MSModule.MSPLAYER_STAGE_REGISTER)
		print ('session closed in AdventureMode %s')%(session.data['Nick'])
	
	def handlePlayerFetchData(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			try:
				pid = ObjectId(rqst.data['pid'])
				if pid != ses.data['_id']:
					return

				self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_ADVENTURE_MODE_DATA, self.chapterInfo))
			except:
				raise


	def handlePlayerGameOver(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			try:
				pid = ObjectId(rqst.data['pid'])
				if pid != ses.data['_id']:
					return
				if ses.data['AdventureStarted'] == False:
					return

				ret = {}
				ses.data['AdventureStarted'] = False
				if rqst.data['success']:


					# if rqst.data['prop'].get('Coin',None) != None:
					# 	pprop = self.database.fetchPlayerProperty(pid)
					# 	pprop['Coins'] += max(0, rqst.data['prop']['Coin'])
					# 	self.database.updatePlayerProperty(pid, pprop)

					ch = ses.data['AdventureMap']
					reward = self.chapterReward[ch[0]-1][ch[1]]


					newMatCount = random.randint(1,3)
					itemData = self.database.fetchPlayerItemData(pid)
					matData = itemData['Material']
					matAdded = False
					for i in matData:
						if i['type'] == reward['Material'] and i['level'] == 1:
							i['count'] += newMatCount
							matAdded = True
							break
					if not matAdded:
						matData.append({'type':reward['Material'], 'level':1, 'count':newMatCount})

					self.database.updatePlayerMaterial(pid, matData)

					elemData = itemData['Element']
					elemTable = {}
					for i in elemData:
						elemTable[i['type']] = i

					for i in reward['Element']:
						if elemTable.get(i, None) == None:
							elemTable[i] = {'type':i, 'count':1}
						else:
							elemTable[i]['count'] += 1

					newElemData = []
					for k, v in elemTable.items():
						newElemData.append(v)

					self.database.updatePlayerElementData(pid, newElemData)

					ret = {'Material':{'type':reward['Material'], 'level':1, 'count':newMatCount}}
				else:
					ch = ses.data['AdventureMap']
					cost = self.chapterInfo[ch[0]-1][ch[1]-1]['cost']
					pprop = self.database.fetchPlayerProperty(ses.data['_id'])
					if pprop['Spirit'] < 100:
						pprop['Spirit'] = min(100, pprop['Spirit'] + cost)
						self.database.updatePlayerProperty(ses.data['_id'], pprop)

				self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_ADVENTURE_CASH_UP, ret))
			except:
				print ('adventure cash up failed %s')%(ses.data['Nick'])		


	def handlePlayerStart(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			try:
				pid = ObjectId(rqst.data['pid'])
				if pid != ses.data['_id']:
					return
				pprop = self.database.fetchPlayerProperty(ses.data['_id'])
				cost = self.chapterInfo[rqst.data['Chapter']-1][rqst.data['Map']-1]['cost']
				if pprop['Spirit'] >= cost:
					pprop['Spirit'] -= cost
					self.database.updatePlayerProperty(ses.data['_id'], pprop)
					ses.data['AdventureStarted'] = True
					ses.data['AdventureMap'] = (rqst.data['Chapter'], rqst.data['Map'])

			except:
				print ('start adventure failed %s')%(ses.data['Nick'])	

			

	def handlePlayerLeave(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_LEAVE_ADVENTURE_MODE_CONFIRM, {}))
			self.transferCallback(ses, MSModule.MSPLAYER_STAGE_GAME_ENTRANCE)