# -*- coding:utf-8 -*-
import csv
import MSService
import MSMessage
import MSSession
import MSModule
import MSServerLogic
import MSItems
import math
from bson.objectid import ObjectId


class MSModuleGameEntrance(MSModule.Module):
	def __init__(self, network, dbMgr, svrDispatcher, sesTransfer):
		super(MSModuleGameEntrance, self).__init__(MSService.SERVICE_GAME_ENTRANCE, network, dbMgr, svrDispatcher, sesTransfer)

		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_FETCH_PLAYER_DATA, 
			self.serviceID,
			MSService.ACTION_FETCH_ENTRANCE_DATA)


		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_ENTER_TREASURE_MODE, self.serviceID,
			MSService.ACTION_ENTER_TREASURE_MODE)
		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_ENTER_ADVENTURE_MODE, self.serviceID,
			MSService.ACTION_ENTER_ADVENTURE_MODE)

		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_PURCHASE_ACTOR,	self.serviceID,
			MSService.ACTION_PURCHASE_ACTOR)

		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_UPGRADE_ACTOR, self.serviceID,
			MSService.ACTION_UPGRADE_ACTOR)	

		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_SYNC_ACTOR,	self.serviceID,
			MSService.ACTION_SYNC_ACTOR)

		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_EQUIP, self.serviceID,
			MSService.ACTION_EQUIP)
		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_UNEQUIP, self.serviceID,
			MSService.ACTION_UNEQUIP)

		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_UPGRADE_EQUIP, self.serviceID,
			MSService.ACTION_UPGRADE_EQUIP)
		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_EVOLUTE_EQUIP, self.serviceID,
			MSService.ACTION_EVOLUTE_EQUIP)

		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_SELL_EQUIP, self.serviceID,
			MSService.ACTION_SELL_EQUIP)
		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_SELL_MATERIAL, self.serviceID,
			MSService.ACTION_SELL_MATERIAL)
		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_SELL_ITEM, self.serviceID,
			MSService.ACTION_SELL_ITEM)

		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_FETCH_WEEKLY_RANK, self.serviceID,
			MSService.ACTION_FETCH_WEEKLY_RANK)
		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_FETCH_FRIEND_RANK, self.serviceID,
			MSService.ACTION_FETCH_FRIEND_RANK)

		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_SYNC_ASSET, self.serviceID,
			MSService.ACTION_SYNC_ASSET)

		self.registerHandler(MSService.ACTION_FETCH_ENTRANCE_DATA, self.handlePlayerFetchData)
		self.registerHandler(MSService.ACTION_ENTER_TREASURE_MODE, self.handlePlayerEnterTreasureMode)
		self.registerHandler(MSService.ACTION_ENTER_ADVENTURE_MODE, self.handlePlayerEnterAdventureMode)
		self.registerHandler(MSService.ACTION_PURCHASE_ACTOR, self.handlePurchaseActor)
		self.registerHandler(MSService.ACTION_UPGRADE_ACTOR, self.handleUpgradeActor)
		self.registerHandler(MSService.ACTION_SYNC_ACTOR, self.handleSyncActor)

		self.registerHandler(MSService.ACTION_EQUIP, self.handleEquip)
		self.registerHandler(MSService.ACTION_UNEQUIP, self.handleUnequip)
		self.registerHandler(MSService.ACTION_UPGRADE_EQUIP, self.handleUpgradeEquip)
		self.registerHandler(MSService.ACTION_EVOLUTE_EQUIP, self.handleEvoluteEquip)
		self.registerHandler(MSService.ACTION_SELL_EQUIP, self.handleSellEquip)
		self.registerHandler(MSService.ACTION_SELL_MATERIAL, self.handleSellMaterial)
		self.registerHandler(MSService.ACTION_SELL_ITEM, self.handleSellItem)
		self.registerHandler(MSService.ACTION_SYNC_ASSET, self.handleSyncEquip)

		self.registerHandler(MSService.ACTION_FETCH_WEEKLY_RANK, self.handlePlayerFetchWeeklyRank)
		self.registerHandler(MSService.ACTION_FETCH_FRIEND_RANK, self.handlePlayerFetchFriendRank)

		svrDispatcher.register(self.serviceID, self)

		self.actorSetting = []
		with open('ActorSetting.csv', 'rb') as csvfile:
			spamreader = csv.reader(csvfile, delimiter=',')
			for row in spamreader:
				aset = {}
				aset['power'] = row[1].isdigit() and int(row[1]) or row[1]
				aset['hp'] = row[2].isdigit() and int(row[2]) or row[2]
				aset['upCost'] = row[4].isdigit() and int(row[4]) or row[4]
				self.actorSetting.append(aset)

		self.actorLimit = {
			"Marco" : {'max':60, 'purchase':0},
			"Eri" : {'max':60, 'purchase':80000},
			"Tarma" : {'max':80, 'purchase':200000},
			"Fio" : {'max':100, 'purchase':250000}
		}

		self.equipMax = {
			'2':25,
			'3':30,
			'4':60,
			'4+':65,
			'4++':70,
			'4+++':75,
			'5':75,
			'5+':80,
			'5++':85,
			'5+++':90,
			'5++++':90,
		}

		self.nextStar = {
			'2':'3',
			'3':'4',
			'4':'4+',
			'4+':'4++',
			'4++':'4+++',
			'4+++':'5',
			'5':'5+',
			'5+':'5++',
			'5++':'5+++',
			'5+++':'5++++',
		}
		
		self.equipExp = []
		with open('EquipExp.csv', 'rb') as csvfile:
			spamreader = csv.reader(csvfile, delimiter=',')
			for row in spamreader:
				exp = 0
				exp = row[1].isdigit() and int(row[1]) or 0
				self.equipExp.append(exp)


		self.equipM1Power = {2:[], 3:[], 4:[], 5:[]}
		with open('EquipPowerM1.csv', 'rb') as csvfile:
			spamreader = csv.reader(csvfile, delimiter=',')
			for row in spamreader:
				aset = {}
				self.equipM1Power[2].append(row[2].isdigit() and int(row[2]) or row[2])
				self.equipM1Power[3].append(row[3].isdigit() and int(row[3]) or row[3])
				self.equipM1Power[4].append(row[4].isdigit() and int(row[4]) or row[4])
				self.equipM1Power[5].append(row[5].isdigit() and int(row[5]) or row[5])
		self.equipM1Price = {2:[], 3:[], 4:[], 5:[]}
		with open('EquipPriceM1.csv', 'rb') as csvfile:
			spamreader = csv.reader(csvfile, delimiter=',')
			for row in spamreader:
				aset = {}
				self.equipM1Price[2].append(row[2].isdigit() and int(row[2]) or row[2])
				self.equipM1Price[3].append(row[3].isdigit() and int(row[3]) or row[3])
				self.equipM1Price[4].append(row[4].isdigit() and int(row[4]) or row[4])
				self.equipM1Price[5].append(row[5].isdigit() and int(row[5]) or row[5])


		self.equipM2Power = {2:[], 3:[], 4:[], 5:[]}
		with open('EquipPowerM2.csv', 'rb') as csvfile:
			spamreader = csv.reader(csvfile, delimiter=',')
			for row in spamreader:
				aset = {}
				self.equipM2Power[2].append(row[2].isdigit() and int(row[2]) or row[2])
				self.equipM2Power[3].append(row[3].isdigit() and int(row[3]) or row[3])
				self.equipM2Power[4].append(row[4].isdigit() and int(row[4]) or row[4])
				self.equipM2Power[5].append(row[5].isdigit() and int(row[5]) or row[5])
		self.equipM2Price = {2:[], 3:[], 4:[], 5:[]}
		with open('EquipPriceM2.csv', 'rb') as csvfile:
			spamreader = csv.reader(csvfile, delimiter=',')
			for row in spamreader:
				aset = {}
				self.equipM2Price[2].append(row[2].isdigit() and int(row[2]) or row[2])
				self.equipM2Price[3].append(row[3].isdigit() and int(row[3]) or row[3])
				self.equipM2Price[4].append(row[4].isdigit() and int(row[4]) or row[4])
				self.equipM2Price[5].append(row[5].isdigit() and int(row[5]) or row[5])

		self.equipM3Power = {2:[], 3:[], 4:[], 5:[]}
		with open('EquipPowerM3.csv', 'rb') as csvfile:
			spamreader = csv.reader(csvfile, delimiter=',')
			for row in spamreader:
				aset = {}
				self.equipM3Power[2].append(row[2].isdigit() and int(row[2]) or row[2])
				self.equipM3Power[3].append(row[3].isdigit() and int(row[3]) or row[3])
				self.equipM3Power[4].append(row[4].isdigit() and int(row[4]) or row[4])
				self.equipM3Power[5].append(row[5].isdigit() and int(row[5]) or row[5])
		self.equipM3Price = {2:[], 3:[], 4:[], 5:[]}
		with open('EquipPriceM3.csv', 'rb') as csvfile:
			spamreader = csv.reader(csvfile, delimiter=',')
			for row in spamreader:
				aset = {}
				self.equipM3Price[2].append(row[2].isdigit() and int(row[2]) or row[2])
				self.equipM3Price[3].append(row[3].isdigit() and int(row[3]) or row[3])
				self.equipM3Price[4].append(row[4].isdigit() and int(row[4]) or row[4])
				self.equipM3Price[5].append(row[5].isdigit() and int(row[5]) or row[5])

		self.matMgAl = {
			1 : (1000,100),
			2 : (1300,130),
			3 : (1600,160),
			4 : (1900,190),
			5 : (2200,220),
		}
		self.matTuSt = {
			1 : (2800,280),
			2 : (3400,340),
			3 : (4000,400),
			4 : (4600,460),
			5 : (5200,520),
		}
		self.matTicr = {
			1 : (6100,610),
			2 : (7000,700),
			3 : (7900,790),
			5 : (9700,880),
			4 : (8800,970),
		}


	# sub-class implement this method.
	def onSessionOpen(self, session):
		#self.transferCallback(session, MSModule.MSPLAYER_STAGE_REGISTER)
		print ('session opened in GameEntrance %s')%(session.data['Nick'])
		
	# sub-class implement this method.
	def onSessionClose(self, session):
		#self.transferCallback(session, MSModule.MSPLAYER_STAGE_REGISTER)
		print ('session closed in GameEntrance %s')%(session.data['Nick'])
	
	def packEquip(self, equip):
		return [equip['_id'], equip['type'],equip['level'],equip['star'],equip['exp']]

	def unpackEquip(self, equip):
		ret = {}
		ret['_id'] = equip[0]
		ret['type'] = equip[1]
		ret['level'] = equip[2]
		ret['star'] = equip[3]
		ret['exp'] = equip[4]
		return ret

	def packItem(self, item):
		ret = []
		for v in item:
			d = [v['type'], v['count']]
			ret.append(d)
		return ret


	def unpackItem(self, item):
		ret = []
		for v in item:
			d = {}
			d['type'] = v[0]
			d['count'] = v[1]
			ret.append(d)
		return ret

	def packMaterial(self, mat):
		ret = []
		for v in mat:
			d = []
			if MSItems.isExpMaterial(v['type']):
				d = [v['type'], v['level'], v['count']]
			else:
				d = [v['type'], v['count']]
			ret.append(d)
		return ret


	def unpackMaterial(self, mat):
		ret = []
		for v in mat:
			d = {}
			if MSItems.isExpMaterial(v[0]):
				d['type'] = v[0]
				d['level'] = v[1]
				d['count'] = v[2]
			else:
				d['type'] = v[0]
				d['count'] = v[1]
			ret.append(d)
		return ret

	def getEquipPower(self, typ, star, level):
		if typ == MSItems.MSWEAPON_TYPE_MACHINEGUN or typ == MSItems.MSARMOR_TYPE_STRIKE or typ == MSItems.MSWEAPON_TYPE_DESERT_FOX:
			return self.equipM1Power[star][level-1]			
		if typ == MSItems.MSWEAPON_TYPE_SHOTGUN or typ == MSItems.MSARMOR_TYPE_THUNDER or typ == MSItems.MSWEAPON_TYPE_DEATH_PULSE:
			return self.equipM2Power[star][level-1]			
		if typ == MSItems.MSWEAPON_TYPE_LASERGUN or typ == MSItems.MSARMOR_TYPE_GUARDIAN or typ == MSItems.MSWEAPON_TYPE_MISSILE:
			return self.equipM3Power[star][level-1]
	
	def getMaterialSetting(self, typ, level):
		if typ == MSItems.MSITEM_TYPE_MGALALLOY:
			return self.matMgAl[level]
		if typ == MSItems.MSITEM_TYPE_TUNGSTENSTEEL:
			return self.matTuSt[level]
		if typ == MSItems.MSITEM_TYPE_TICRALLOY:
			return self.matTicr[level]

	def handlePlayerFetchData(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			data = {}
			pdata = self.database.fetchPlayerData(ses.data['_id'])
			if pdata != None:
				# fetch data:
				data = pdata
				mainArs = []
				secArs = []
				armoArs = []
				for d in pdata['Arsenal']['Main']:
					mainArs.append(self.packEquip(d))
				data['Arsenal']['Main'] = mainArs
				for d in pdata['Arsenal']['Secondary']:
					secArs.append(self.packEquip(d))
				data['Arsenal']['Secondary'] = secArs
				for d in pdata['Arsenal']['Armor']:
					armoArs.append(self.packEquip(d))
				data['Arsenal']['Armor'] = armoArs

				if pdata['Equip']['Main'] != None:
					data['Equip']['Main'] = self.packEquip(pdata['Equip']['Main'])
				if pdata['Equip']['Secondary'] != None:
					data['Equip']['Secondary'] = self.packEquip(pdata['Equip']['Secondary'])
				if pdata['Equip']['Armor'] != None:
					data['Equip']['Armor'] = self.packEquip(pdata['Equip']['Armor'])

				data['Material'] = self.packMaterial(pdata['Material'])
				data['Items'] = self.packItem(pdata['Items'])

				# ranking
				ranking = self.database.getTreasureRank()
				data['Ranking'] = ranking
			


				data['_id'] = str(ses.data['_id'])
				data['Nick'] = ses.data['Nick']
				data['LastSpGenTime'] = ses.data['LastSpGenTime']
				
				self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_PLAYER_DATA, data))
			else:
				data['msg'] = 'Invalid player state'
				self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_FETCH_DENY, data))


		else:
			data = {}
			data['msg'] = 'Access denied'
			self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_FETCH_DENY, data))
			self.network.close(owner)

	def handlePurchaseActor(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			try:
				pid = rqst.data.get('pid', None)
				actor = rqst.data.get('actor')
				if pid == None or actor == None:
					return
				if pid != str(ses.data['_id']):
					return
				actorLimit = self.actorLimit.get(actor, None)
				if actorLimit == None:
					return
				pprop = self.database.fetchPlayerProperty(ses.data['_id'])
				if pprop['Coins'] < actorLimit['purchase']:
					return
				else:
					pprop['Coins'] = pprop['Coins'] - actorLimit['purchase']
					self.database.updatePlayerProperty(ses.data['_id'], pprop)
					self.database.unlockPlayerActor(ses.data['_id'], actor)
			except:
				print '%d purchase actor failed'%(owner)	


	def handleUpgradeActor(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			try:
				pid = rqst.data.get('pid', None)
				actor = rqst.data.get('actor')
				if pid == None or actor == None:
					return
				if pid != str(ses.data['_id']):
					return
				actorLimit = self.actorLimit.get(actor, None)
				if actorLimit == None:
					return
				adata = self.database.fetchPlayerActor(ses.data['_id'], actor)
				pprop = self.database.fetchPlayerProperty(ses.data['_id'])
				if adata == None or adata == {} or adata.get('Actor',None) == None:
					return
				else:
					adata = adata['Actor'][actor]
					if adata['level'] < actorLimit['max']:
						cost = self.actorSetting[adata['level']]['upCost']
						if pprop['Coins'] < cost:
							return
						else:
							pprop['Coins'] = pprop['Coins'] - cost
							adata['level'] = adata['level'] + 1
							adata['hp'] = self.actorSetting[adata['level']]['hp']
							adata['power'] = self.actorSetting[adata['level']]['power']
							self.database.updatePlayerProperty(ses.data['_id'], pprop)
							self.database.updatePlayerActor(ses.data['_id'], actor, adata)
			except:
				print '%d upgrade actor failed'%(owner)	
						
	def handleSyncActor(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			try:
				pid = rqst.data.get('pid', None)
				if pid == None:
					return
				if pid != str(ses.data['_id']):
					return
				abank = self.database.fetchPlayerActorBank(ses.data['_id'])
				data = rqst.data
				if data['Actor'] == abank:
					inUsed = abank.get(data['ActorInUse'], None)
					if inUsed != None and inUsed['unlocked'] == True:
						self.database.setActorInUse(ses.data['_id'], data['ActorInUse'])
						self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_SYNC_ACTOR_CONFIRM, {}))
						return
				self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_SYNC_ACTOR_DENY, {}))
				self.network.close(owner)
			except:
				print '%d sync actor failed'%(owner)	
				self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_SYNC_ACTOR_DENY, {}))




	def handleEquip(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			try:
				part = rqst.data['part']
				pid = ObjectId(rqst.data['pid'])
				if pid == ses.data['_id'] and part != '':
					eqp = self.database.takeEquipFromArsenel(pid, part, rqst.data['id'])
					#print eqp
					if eqp != None:
						self.database.equip(pid, part, eqp)
			except:
				print '%d equip failed'%(owner)	

	def handleUnequip(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			try:
				part = rqst.data['part']
				pid = ObjectId(rqst.data['pid'])
				if pid == ses.data['_id'] and part != '':
					eqp = self.database.unequip(pid, part)
					if eqp != None:
						self.database.addEquipToArsenal(pid, part, eqp)
			except:
				print '%d unequip failed'%(owner)	


	def handleUpgradeEquip(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			try:
				pid = ObjectId(rqst.data['pid'])
				if pid != ses.data['_id']:
					return

				matData = self.database.fetchPlayerItemData(pid)['Material']


				totalExp = 0
				for i in matData:
					for j in rqst.data['mat']:
						if j['type'] == i['type'] and j['level'] == i['level']:
							if j['count'] > i['count']:
								return
							else:
								totalExp += self.getMaterialSetting(j['type'], j['level'])[0] * j['count']
								i['count'] -= j['count']
				# remove whose count is 0:
				rev = range(len(matData))
				rev.reverse()
				for i in rev:
					if matData[i]['count'] == 0:
						del matData[i]


				part = rqst.data['p']
				lvlLimit = 0
				expectLvl = 0
				eqp = None
				if rqst.data['e']:
					eqp = self.database.unequip(pid, part)
				else:
					eqp = self.database.takeEquipFromArsenel(pid, part, rqst.data['t']['_id'])

				lvlLimit = self.equipMax[eqp['star']]
				curExp = eqp['exp'] + totalExp

				for i in range(eqp['level'], lvlLimit + 1):
					expectLvl = i
					if self.equipExp[i - 1] > curExp:
						expectLvl = i - 1
						break
				if expectLvl >= lvlLimit:
					expectLvl = lvlLimit
					curExp = self.equipExp[lvlLimit - 1]
				eqp['exp'] = curExp
				eqp['level'] = expectLvl

				if rqst.data['e']:
					self.database.equip(pid, part, eqp)
					self.database.updatePlayerMaterial(pid, matData)
				else:
					self.database.addEquipToArsenal(pid, part, eqp)
					self.database.updatePlayerMaterial(pid, matData)
			except:
				print '%d updrade equip failed'%(owner)


	def handleEvoluteEquip(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			try:
				pid = ObjectId(rqst.data['pid'])
				if pid != ses.data['_id']:
					return

				# 检查参数
				_s = rqst.data['s']
				_e = rqst.data['e']

				if _s != 0 and _s != 1:
					return

				part = rqst.data['p']

				eqp = None
				elemData = self.database.fetchPlayerItemData(pid)['Element']
				
				if rqst.data['e']:
					eqp = self.database.unequip(pid, part)
				else:
					eqp = self.database.takeEquipFromArsenel(pid, part, rqst.data['t']['_id'])

				# 检查材料合法性.
				if rqst.data['s'] == 1:
					# 升星
					try:
						elem = MSItems.getEvoElement(eqp['star'])
						for i in elem:
							for j in elemData:
								if i == j['type']:
									if j['count'] >= 1:
										j['count'] -= 1
									else:
										raise Exception()

						nextStar = self.nextStar[eqp['star']]
						eqp['star'] = nextStar
						self.database.updatePlayerElementData(pid, elemData)
					except:
						# 放回装备
						if rqst.data['e']:
							self.database.equip(pid, part, eqp)
						else:
							self.database.addEquipToArsenal(pid, part, eqp)

						self.database.updatePlayerElementData(pid, elemData)
						raise
				else:
					try:
						plus = eqp['star'][1:]
						eqCount = None
						if plus == '':
							eqCount = 1
						elif plus == '+':
							eqCount = 2
						elif plus == '++':
							eqCount = 1

						takedEqp = []
						if eqCount != len(rqst.data['src']):
							raise Exception()
						for i in rqst.data['src']:
							tmpEq = self.database.takeEquipFromArsenel(pid, part, i)
							if tmpEq['star'] != eqp['star'] or tmpEq['type'] != eqp['type']:
								raise Exception()
							takedEqp.append(tmpEq)

						nextStar = self.nextStar[eqp['star']]
						eqp['star'] = nextStar

					except:
						# 放回装备
						if rqst.data['e']:
							self.database.equip(pid, part, eqp)
						else:
							self.database.addEquipToArsenal(pid, part, eqp)
						for i in takedEqp:
							if i != None:
								self.database.addEquipToArsenal(pid, part, i)
						raise


				if rqst.data['e']:
					self.database.equip(pid, part, eqp)
				else:
					self.database.addEquipToArsenal(pid, part, eqp)

			except:
				print '%d evolute equip failed'%(owner)

	def handleSellEquip(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			try:
				part = rqst.data['part']
				pid = ObjectId(rqst.data['pid'])
				if pid != ses.data['_id']:
					return
				#print rqst.data
				if part != '':
					eqList = []
					for d in rqst.data['id']:
						eqList.append(self.database.takeEquipFromArsenel(pid, part, d))

					totalPrice = 0
					for e in eqList:
						if e != None:
							star = int(e['star'][0:1])
							typ = e['type']
							if typ == MSItems.MSWEAPON_TYPE_MACHINEGUN or typ == MSItems.MSARMOR_TYPE_STRIKE or typ == MSItems.MSWEAPON_TYPE_DESERT_FOX:
								totalPrice += self.equipM1Price[star][e['level']-1]
							elif typ == MSItems.MSWEAPON_TYPE_SHOTGUN or typ == MSItems.MSARMOR_TYPE_THUNDER or typ == MSItems.MSWEAPON_TYPE_DEATH_PULSE:
								totalPrice += self.equipM2Price[star][e['level']-1]
							elif typ == MSItems.MSWEAPON_TYPE_LASERGUN or typ == MSItems.MSARMOR_TYPE_GUARDIAN or typ == MSItems.MSWEAPON_TYPE_MISSILE:
								totalPrice += self.equipM3Price[star][e['level']-1]
							else:
								break
					if totalPrice == rqst.data['price']:
						pprop = self.database.fetchPlayerProperty(pid)
						pprop['Coins'] = pprop['Coins'] + totalPrice
						self.database.updatePlayerProperty(pid, pprop)
			except:
				print '%d sell equip failed'%(owner)

	def handleSellMaterial(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			try:
				pid = ObjectId(rqst.data['pid'])
				if not ObjectId.is_valid(pid):
					return

				matData = self.database.fetchPlayerItemData(pid)['Material']

				price = 0
				for i in matData:
					for j in rqst.data['mat']:
						if j['type'] == i['type'] and j['level'] == i['level']:
							if j['count'] > i['count']:
								return
							else:
								price += self.getMaterialSetting(j['type'], j['level'])[1] * j['count']
								i['count'] -= j['count']
				# remove whose count is 0:
				rev = range(len(matData))
				rev.reverse()
				for i in rev:
					if matData[i]['count'] == 0:
						del matData[i]

				if price == rqst.data['price']:	
					pprop = self.database.fetchPlayerProperty(pid)
					pprop['Coins'] = pprop['Coins'] + price
					self.database.updatePlayerProperty(pid, pprop)
					self.database.updatePlayerMaterial(pid, matData)

			except:
				print '%d sell material failed'%(owner)

	def handleSellItem(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			try:
				pass
			except:
				print '%d sell item failed'%(owner)

	def handleSyncEquip(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			try:
				pid = ObjectId(rqst.data['pid'])
				valid = True
				if pid != ses.data['_id']:
					self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_SYNC_ASSET_DENY,{}))
					return
				pprop = self.database.fetchPlayerProperty(pid)
				if pprop['Coins'] != rqst.data['coins']:
					valid = False
					self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_SYNC_ASSET_DENY,{}))
					self.network.close(owner)
					return 
				equip = self.database.fetchPlayerEquipData(pid)
				#print equip
				arsenal = self.database.fetchPlayerArsenalData(pid)
				#print arsenal
				ceqp = {'Armor':None, 'Secondary':None, 'Main':None}
				if rqst.data.get('Equip', None) != None and rqst.data['Equip'] != []:
					if rqst.data['Equip'].get('Armor', None) != None:
						ceqp['Armor'] = self.unpackEquip(rqst.data['Equip']['Armor'])
					if rqst.data['Equip'].get('Secondary', None) != None:
						ceqp['Secondary'] = self.unpackEquip(rqst.data['Equip']['Secondary'])
					if rqst.data['Equip'].get('Main', None) != None:
						ceqp['Main'] = self.unpackEquip(rqst.data['Equip']['Main'])
				
				cars = {'Armor':[], 'Secondary':[], 'Main':[]}
				for a in rqst.data['Arsenal']['Armor']:
					cars['Armor'].append(self.unpackEquip(a))
				for s in rqst.data['Arsenal']['Secondary']:
					cars['Secondary'].append(self.unpackEquip(s))
				for m in rqst.data['Arsenal']['Main']:
					cars['Main'].append(self.unpackEquip(m))
				
				equipValid = False
				arsValid = False
				if equip == ceqp:
					equipValid = True

				cdict = {
					'Main':{},
					'Secondary':{},
					'Armor':{},
				}
				for i in cars['Main']:
					cdict['Main'][i['_id']] = i
				for i in cars['Secondary']:
					cdict['Secondary'][i['_id']] = i
				for i in cars['Armor']:
					cdict['Armor'][i['_id']] = i

				sdict = {
					'Main':{},
					'Secondary':{},
					'Armor':{},
				}
				for i in arsenal['Main']:
					sdict['Main'][i['_id']] = i
				for i in arsenal['Secondary']:
					sdict['Secondary'][i['_id']] = i
				for i in arsenal['Armor']:
					sdict['Armor'][i['_id']] = i

				if cdict == sdict:	
					arsValid = True
				
				if equipValid and arsValid:
					self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_SYNC_ASSET_CONFIRM, {}))
				else:
					if not equipValid:
						print ceqp
						print equip
					if not arsValid:
						print cdict
						print sdict
					self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_SYNC_ASSET_DENY,{}))
					self.network.close(owner)
			except:
				print '%d sync equip failed'%(owner)
				self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_SYNC_ASSET_DENY,{}))
				self.network.close(owner)

			#print rqst.data



	def handlePlayerEnterTreasureMode(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			try:
				pid = ObjectId(rqst.data['pid'])
				valid = True
				if pid != ses.data['_id']:
					return
				equip = self.database.fetchPlayerEquipData(pid)
				if equip['Armor'] != None:
					star = int(equip['Armor']['star'][0:1])
					a = {
						'_id':equip['Armor']['_id'],
						'level':equip['Armor']['level'],
						'type':equip['Armor']['type'],
						'power':self.getEquipPower(equip['Armor']['type'], star, equip['Armor']['level']),
						'star':equip['Armor']['star'],
					}
					if a != rqst.data['Equip']['Armor']:
						raise Exception()

				if equip['Main'] != None:
					star = int(equip['Main']['star'][0:1])
					m = {
						'_id':equip['Main']['_id'],
						'level':equip['Main']['level'],
						'type':equip['Main']['type'],
						'power':self.getEquipPower(equip['Main']['type'], star, equip['Main']['level']),
						'star':equip['Main']['star'],
					}
					if m != rqst.data['Equip']['Main']:
						raise Exception()

				if equip['Secondary'] != None:
					star = int(equip['Secondary']['star'][0:1])
					s = {
						'_id':equip['Secondary']['_id'],
						'level':equip['Secondary']['level'],
						'type':equip['Secondary']['type'],
						'power':self.getEquipPower(equip['Secondary']['type'], star, equip['Secondary']['level']),
						'star':equip['Secondary']['star'],
					}
					if s != rqst.data['Equip']['Secondary']:
						raise Exception()

				self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_ENTER_TREASURE_MODE_CONFIRM, {}))
				self.transferCallback(ses, MSModule.MSPLAYER_STAGE_GAME_TREASURE_MODE)
										
			except:
				print '%d enter treasure failed'%(owner)
	
	def handlePlayerEnterAdventureMode(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			try:
				pid = ObjectId(rqst.data['pid'])
				valid = True
				if pid != ses.data['_id']:
					return
				equip = self.database.fetchPlayerEquipData(pid)
				if equip['Armor'] != None:
					star = int(equip['Armor']['star'][0:1])
					a = {
						'_id':equip['Armor']['_id'],
						'level':equip['Armor']['level'],
						'type':equip['Armor']['type'],
						'power':self.getEquipPower(equip['Armor']['type'], star, equip['Armor']['level']),
						'star':equip['Armor']['star'],
					}
					if a != rqst.data['Equip']['Armor']:
						raise Exception()

				if equip['Main'] != None:
					star = int(equip['Main']['star'][0:1])
					m = {
						'_id':equip['Main']['_id'],
						'level':equip['Main']['level'],
						'type':equip['Main']['type'],
						'power':self.getEquipPower(equip['Main']['type'], star, equip['Main']['level']),
						'star':equip['Main']['star'],
					}
					if m != rqst.data['Equip']['Main']:
						raise Exception()

				if equip['Secondary'] != None:
					star = int(equip['Secondary']['star'][0:1])
					s = {
						'_id':equip['Secondary']['_id'],
						'level':equip['Secondary']['level'],
						'type':equip['Secondary']['type'],
						'power':self.getEquipPower(equip['Secondary']['type'], star, equip['Secondary']['level']),
						'star':equip['Secondary']['star'],
					}
					if s != rqst.data['Equip']['Secondary']:
						raise Exception()

				self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_ENTER_ADVENTURE_MODE_CONFIRM, {}))
				self.transferCallback(ses, MSModule.MSPLAYER_STAGE_GAME_ADVENTURE_MODE)
									
			except:
				print '%d enter adventure failed'%(owner)

	def handlePlayerFetchWeeklyRank(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			try:
				pid = ObjectId(rqst.data['pid'])
				if pid != ses.data['_id']:
					return

				rank = self.database.getTreasureRank()
				uid = ses.data['uid']
				pIndex = 0
				for i in range(len(rank)):
					if rank[i]['uid'] == uid:
						pIndex = i
						break
				base = max(0, pIndex - 10)
				data = {
					'base':base,
					'rank':rank[base:base+20]
				}
				self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_WEEKLY_RANK, data))


			except:
				raise
				print ('fetch week rank failed %s')%(ses.data['Nick'])


	def handlePlayerFetchFriendRank(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses != None:
			try:
				pid = ObjectId(rqst.data['pid'])
				if pid != ses.data['_id']:
					return

				rank = self.database.getTreasureRank()
				uid = ses.data['uid']
				pFriend = self.database.getPlayerFriends(ses.data['_id'])

				fRank = []
				for i in pFriend:
					for j in rank:
						if j['uid'] == i:
							fRank.append(j)
							break

				pIndex = 0
				playerInRank = False
				for i in rank:
					if i['uid'] == uid:
						fRank.append(i)
						playerInRank = True
						break
				if not playerInRank:
					playerData = self.database.fetchPlayerData(pid)
					actorName = playerData['actorInUse']
					playerActor = playerData['Actor'][actorName]
					fRank.append({
						'actor': actorName,
						'level': playerActor['level'],
						'nick': ses.data['Nick'],
						'score': 0,
						'uid': uid,
					})

				fRank.sort(key = lambda x: x['score'])
				fRank.reverse()
				data = {
					'base':0,
					'rank':fRank
				}
				self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_FRIEND_RANK, data))


			except:
				print ('fetch friend rank failed %s')%(ses.data['Nick'])

