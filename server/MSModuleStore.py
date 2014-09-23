
import MSService
import MSMessage
import MSSession
import MSModule
import MSServerLogic
import MSItems
import random
from bson.objectid import ObjectId


class MSModuleStore(MSModule.Module):
	def __init__(self, network, dbMgr, svrDispatcher, sesTransfer):
		super(MSModuleStore, self).__init__(MSService.SERVICE_STORE, network, dbMgr, svrDispatcher, sesTransfer)

		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_LEAVE_STORE, self.serviceID,
			MSService.ACTION_PLAYER_LEAVE_STORE)

		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_PURCHASE_SPIRIT, self.serviceID,
			MSService.ACTION_PLAYER_PURCHASE_SPIRIT)
		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_PURCHASE_COIN, self.serviceID,
			MSService.ACTION_PLAYER_PURCHASE_COIN)
		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_PURCHASE_GEM, self.serviceID,
			MSService.ACTION_PLAYER_PURCHASE_GEM)
		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_PURCHASE_ITEM, self.serviceID,
			MSService.ACTION_PLAYER_PURCHASE_ITEM)

		self.spiritCost = {
			1 : 200,
			2 : 150,
			3 : 100,
		}
		self.coinCost = {
			500 : 10,
			3000 : 50,
			6250 : 100,
			37500 : 500,
			80000 : 1000,
			180000 : 2000,
		}
		self.itemCost = {
			1 : 200,
			10 : 1800,
		}

		self.gemCost = {}

		self.registerHandler(MSService.ACTION_PLAYER_PURCHASE_SPIRIT, self.handlePlayerPurchaseSpirit)
		self.registerHandler(MSService.ACTION_PLAYER_PURCHASE_COIN, self.handlePlayerPurchaseCoin)
		self.registerHandler(MSService.ACTION_PLAYER_PURCHASE_GEM, self.handlePlayerPurchaseGem)
		self.registerHandler(MSService.ACTION_PLAYER_PURCHASE_ITEM, self.handlePlayerPurchaseItem)
		self.registerHandler(MSService.ACTION_PLAYER_LEAVE_STORE, self.handlePlayerLeave)

		svrDispatcher.register(self.serviceID, self)

	# sub-class implement this method.
	def onSessionOpen(self, session):
		try:
			#self.transferCallback(session, MSModule.MSPLAYER_STAGE_REGISTER)
			print ('session opened in Store %s')%(session.data['Nick'])
		except:
			pass
		
	# sub-class implement this method.
	def onSessionClose(self, session):
		try:
			#self.transferCallback(session, MSModule.MSPLAYER_STAGE_REGISTER)
			print ('session closed in Store %s')%(session.data['Nick'])
		except:
			pass

	def handlePlayerPurchaseSpirit(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			try:
				pid = rqst.data.get('pid', None)
				if pid != str(ses.data['_id']):
					return
				chance = self.database.getPlayerPurchaseSpiritChance(ses.data['_id'])
				if chance <= 0:
					return
				pprop = self.database.fetchPlayerProperty(ses.data['_id'])
				cost = self.spiritCost[chance]
				if cost == rqst.data['cost']:
					if pprop['Gems'] >= cost:
						pprop['Gems'] = pprop['Gems'] - cost
						pprop['Spirit'] = pprop['Spirit'] + 100
						self.database.updatePlayerProperty(ses.data['_id'], pprop)
						chance -= 1
						self.database.updatePlayerPurchaseSpiritChance(ses.data['_id'], chance)

			except:
				print '%d purchase spirit failed'%(owner)	

	def handlePlayerPurchaseCoin(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			try:
				pid = rqst.data.get('pid', None)
				if pid != str(ses.data['_id']):
					return
				pprop = self.database.fetchPlayerProperty(ses.data['_id'])
				cost = self.coinCost[rqst.data['count']]
				if pprop['Gems'] >= cost:
					pprop['Gems'] = pprop['Gems'] - cost
					pprop['Coins'] = pprop['Coins'] + rqst.data['count']
					self.database.updatePlayerProperty(ses.data['_id'], pprop)
				
			except:
				print '%d purchase coin failed'%(owner)	

	def handlePlayerPurchaseGem(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			pass

	def handlePlayerPurchaseItem(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			try:
				pid = ObjectId(rqst.data['pid'])
				if pid != ses.data['_id']:
					return
				pprop = self.database.fetchPlayerProperty(ses.data['_id'])
				cost = self.itemCost[rqst.data['count']]
				count = rqst.data['count']
				if ses.data.get('ItemLuck', None) == None:
					ses.data['ItemLuck'] = 0

				if count == 1 or count == 10:
					if pprop['Gems'] >= cost:
						pprop['Gems'] -= cost
						self.database.updatePlayerProperty(pid, pprop)

						itemTable = {
							'Main':[MSItems.MSWEAPON_TYPE_MACHINEGUN, MSItems.MSWEAPON_TYPE_SHOTGUN, MSItems.MSWEAPON_TYPE_LASERGUN],
							'Armor':[MSItems.MSARMOR_TYPE_STRIKE, MSItems.MSARMOR_TYPE_THUNDER, MSItems.MSARMOR_TYPE_GUARDIAN],
							'Secondary':[MSItems.MSWEAPON_TYPE_DESERT_FOX, MSItems.MSWEAPON_TYPE_DEATH_PULSE, MSItems.MSWEAPON_TYPE_MISSILE],
						}
						ret = {
							'Main':[],
							'Armor':[],
							'Secondary':[],
						}
						for i in range(count):
							part = random.randint(1,3)
							if part == 1:
								part = 'Main'
							elif part == 2:
								part = 'Secondary'
							else:
								part = 'Armor'

							qlt = random.uniform(0.0, 1.0)
							star = ''
							ses.data['ItemLuck'] += 1
							if ses.data['ItemLuck']%10 == 0:
								star = '5'
							else:
								if qlt >= 0.0 and qlt < 0.70:
									star = '3'
								elif qlt >= 0.70 and qlt < 0.95:
									star = '4'
								else:
									star = '5'
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

						self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_PURCHASE_ITEM_RESULT, ret))





			except:
				raise
				print '%d sync property failed'%(owner)	


	def handlePlayerLeave(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			try:
				pid = rqst.data.get('pid', None)
				if pid != str(ses.data['_id']):
					return
				# reset item luck
				ses.data['ItemLuck'] = 0

				pprop = self.database.fetchPlayerProperty(ses.data['_id'])
				if rqst.data['coins'] == pprop['Coins'] and rqst.data['gems'] == pprop['Gems']:
					self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_SYNC_STORE_CONFIRM, {}))
					self.transferCallback(ses, ses.getPrevStage())
				else:
					print rqst.data
					print pprop
					self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_SYNC_STORE_DENY, {}))
			except:
				print '%d sync property failed'%(owner)	
