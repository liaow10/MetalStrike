# -*- coding:utf-8 -*-
import sys
import pymongo
import hashlib
import uuid
import time

import MSItems
from bson.objectid import ObjectId

class MSDatabaseManager:
	"""
	Initialize.
	"""
	def __init__(self):
		self._dbConnection = None
		self._db = None
		self._playerData = None
	
	"""
	Connect to a database 
	"""
	def openDatabase(self, destPath, port):
		self._dbConnection = pymongo.Connection(destPath, port)
		self._db = self._dbConnection.MetalStrike
		self._playerData = self._db.PlayerData
		self._itemCounter = self._db.ItemCounter
		self._accCounter = self._db.AccountCounter
		self._treasureRank = self._db.TreasureRank

	def registerPlayer(self, acc, pwd, nick):
		res = self._playerData.find({'$or':[{'Account':acc},{'Nick':nick}]})
		try:
			if res.count() == 0:
				salt = str(uuid.uuid4())
				hashPwd1 = hashlib.sha1(pwd).hexdigest()
				hashPwd = hashlib.sha256(salt + hashPwd1).hexdigest()
				result = None
				try:
					result = self._playerData.find_and_modify({'Account':acc},{"$set":{'Account':acc, 'Password':hashPwd, 'Nick':nick, 'salt':salt}}, upsert = True, new = True)
				except:
					return None 
				uid = self._accCounter.find_and_modify({'Account':None}, {'$inc':{'counter':1}})
				uid = uid['counter']
				self._playerData.update({'Account':acc}, {'$set':{'uid':uid}})
				return result
			else:
				return None
		except:
			return None

	def checkPlayer(self, acc, pwd):
		try:
			res = self._playerData.find_one({'Account':acc}, fields={'_id':True,  'Password':True, 'uid':True, 'Nick':True, 'Cookie':True, 'LastSpGenTime':True, 'salt':True})
			if res == None:
				return None
			if res.get('LastSpGenTime', None) == None:
				curTime = time.time()
				self._playerData.update({'Account':acc}, {'$set':{'LastSpGenTime': curTime}}, upsert=True)
				res['LastSpGenTime'] = curTime

			hashPwd1 = hashlib.sha1(pwd).hexdigest()
			salt = res['salt']
			tstPwd = hashlib.sha256(salt + hashPwd1).hexdigest()
			if tstPwd == res['Password']:
				newCookie = str(uuid.uuid4())
				newCookie = hashlib.sha256(newCookie).hexdigest()
				self._playerData.update({'_id':res['_id']}, {'$set':{'Cookie':newCookie}})
				res['Cookie'] = newCookie
				return res
			else:
				return None
		except:
			return None

	def checkCookie(self, cookie):
		try:
			res = self._playerData.find_one({'Cookie':cookie}, fields={'_id':True,  'Password':True, 'uid':True, 'Nick':True, 'LastSpGenTime':True, 'salt':True})
			if res == None:
				return None	
			if res.get('LastSpGenTime', None) == None:
				curTime = time.time()
				self._playerData.update({'Cookie':cookie}, {'$set':{'LastSpGenTime': time.time()}}, upsert=True)
				res['LastSpGenTime'] = curTime

			newCookie = str(uuid.uuid4())
			newCookie = hashlib.sha256(newCookie).hexdigest()
			self._playerData.update({'_id':res['_id']}, {'$set':{'Cookie':newCookie}})
			res['Cookie'] = newCookie
			return res
		except:
			raise


	def fetchPlayerData(self, pid):
		ret = {}
		try:
			pdata = self._playerData.find_one({'_id':pid})
			if pdata == None:
				return None
			ret['uid'] = pdata['uid']
			if pdata.get('Spirit', None) == None:
				self._playerData.update({'_id':pid}, {'$set':{'Spirit': 100}}, upsert=True)
				ret['spirit'] = 100
			else:
				ret['spirit'] = pdata['Spirit']

			if pdata.get('LastSpGenTime', None) == None:
				self._playerData.update({'_id':pid}, {'$set':{'LastSpGenTime': time.time()}}, upsert=True)

			if pdata.get('SpiritPurchase', None) == None:
				self._playerData.update({'_id':pid}, {'$set':{'SpiritPurchase':3}})
				ret['SpiritPurchase'] = 3
			else:
				ret['SpiritPurchase'] = pdata['SpiritPurchase']

			if pdata.get('HistoryHighScore', None) == None:
				self._playerData.update({'_id':pid}, {'$set':{'HistoryHighScore':0}})
				ret['HistoryHighScore'] = 0
			else:
				ret['HistoryHighScore'] = pdata['HistoryHighScore']

			if pdata.get('Friend', None) == None:
				self._playerData.update({'_id':pid}, {'$set':{'Friend': []}}, upsert=True)
				ret['Friend'] = []
			else:
				ret['Friend'] = pdata['Friend']


			if pdata.get('Coins', None) == None:
				self._playerData.update({'_id':pid}, {'$set':{'Coins': 0}}, upsert=True)
				ret['coins'] = 0
			else:
				ret['coins'] = pdata['Coins']

			if pdata.get('Gems', None) == None:
				self._playerData.update({'_id':pid}, {'$set':{'Gems': 20000}}, upsert=True)
				ret['gems'] = 20000
			else:
				ret['gems'] = pdata['Gems']

			if pdata.get('Equip', None) == None:
				initEquip = {
						'Main': None,
						'Secondary':None,
						'Armor': None,
					}
				self._playerData.update({'_id':pid}, {'$set':{'Equip': initEquip }}, upsert=True)
				ret['Equip'] = initEquip
			else:
				ret['Equip'] = pdata['Equip']

			if pdata.get('Arsenal', None) == None:
				initArsenal = {
						'Main':[],
						'Secondary':[],
						'Armor':[]
					}
				self._playerData.update({'_id':pid}, {'$set':{'Arsenal':initArsenal}}, upsert=True)
				ret['Arsenal'] = initArsenal
			else:
				ret['Arsenal'] = pdata['Arsenal']

			if pdata.get('Chapter', None) == None:
				initChapter = {}
				self._playerData.update({'_id':pid}, {'$set':{'Chapter':initChapter}}, upsert=True)


			if pdata.get('Items', None) == None:
				self._playerData.update({'_id':pid}, {'$set':{'Item':[]}}, upsert=True)
				ret['Items'] = []
			else:
				ret['Items'] = pdata['Items']

			if pdata.get('Element', None) == None:
				self._playerData.update({'_id':pid}, {'$set':{'Element':[]}}, upsert=True)
				ret['Element'] = []
			else:
				ret['Element'] = pdata['Element']

			if pdata.get('Material', None) == None:
				self._playerData.update({'_id':pid}, {'$set':{'Material':[]}}, upsert=True)
				ret['Material'] = []
			else:
				ret['Material'] = pdata['Material']
			
			if pdata.get('ActorInUse', None) == None:
				self._playerData.update({'_id':pid}, {'$set':{'ActorInUse':'Marco'}}, upsert=True)
				ret['actorInUse'] = 'Marco'
			else:
				ret['actorInUse'] = pdata['ActorInUse']

			if pdata.get('Actor', None) == None:
				# no actor data, insert a default one.
					initActor = {
							'Marco':{
								'unlocked':True,
								'level':1,
								'hp':1400,
								'power':280
							},
							'Tarma':{
								'unlocked':False,
								'level':1,
								'hp':1400,
								'power':280
							},
							'Eri':{
								'unlocked':False,
								'level':1,
								'hp':1400,
								'power':280
							},
							'Fio':{
								'unlocked':False,
								'level':1,
								'hp':1400,
								'power':280
							}}
					self._playerData.update({'_id':pid}, {'$set':{'Actor':
						initActor}}, upsert=True)
					ret['Actor'] = initActor
			else:
				ret['Actor'] = pdata['Actor']

			rank = self.getTreasureRank()
			ret['Rank'] = rank
		except:
			raise
		return ret

	def updateSpiritGenTime(self, pid, time):
		try:
			self._playerData.update({'_id':pid}, {'$set':{'LastSpGenTime':time}})
		except:
			raise

	def fetchPlayerProperty(self, pid):
		try:
			data = self._playerData.find_one({'_id':pid}, fields={'Spirit':True, 'Coins':True, 'Gems':True, '_id':False})
			return data
		except:
			raise

	def getPlayerPurchaseSpiritChance(self, pid):
		try:
			data = self._playerData.find_one({'_id':pid}, fields={'SpiritPurchase':True, '_id':False})
			return data['SpiritPurchase']
		except:
			raise
			
	def updatePlayerPurchaseSpiritChance(self, pid, count):
		try:
			self._playerData.update({'_id':pid}, {'$set':{'SpiritPurchase':count}})
		except:
			raise


	def updatePlayerProperty(self, pid, data):
		try:
			self._playerData.update({'_id':pid}, {'$set':{'Spirit':data['Spirit'], 'Coins':data['Coins'], 'Gems':data['Gems']}}, upsert=False)
		except:
			raise

	def fetchPlayerActorBank(self, pid):
		try:
			data = self._playerData.find({'_id':pid}, fields={'_id':False})
			if data.count() == 0:
				return None
			return data[0]['Actor']
		except:
			raise

	def fetchPlayerActor(self, pid, actorName):
		try:
			data = self._playerData.find_one({'_id':pid}, fields={'Actor.'+actorName:True, '_id':False})
			return data
		except:
			raise

	def updatePlayerActor(self, pid, actorName, data):
		try:
			# check existence
			if self._playerData.find_one({'_id':pid, 'Actor.' + actorName:{'$exists':True}}) == None:
				return
			self._playerData.update({'_id':pid}, {'$set':
				{'Actor.'+actorName : 
					{
						'unlocked' : data['unlocked'],
						'level' : data['level'],
						'hp' : data['hp'],
						'power' : data['power']
						}
					}
				}, upsert=False)
		except:
			raise

	def getPlayerFriends(self, pid):
		try:
			data = self._playerData.find_one({'_id':pid}, fields={'Friend':True, '_id':False})
			return data['Friend']
		except:
			raise

	def unlockPlayerActor(self, pid, actorName):
		try:
			# check existence
			if self._playerData.find_one({'_id':pid, 'Actor.' + actorName:{'$exists':True}}) == None:
				return
			self._playerData.update({'_id':pid}, {'$set':{'Actor.' + actorName + '.unlocked':True}}, upsert=False)
		except:
			raise

	def setActorInUse(self, pid, actorName):
		try:
			self._playerData.update({'_id':pid}, {'$set':{'ActorInUse':actorName}}, upsert = False)
		except:
			raise

	def getActorInUse(self, pid):
		try:
			ret = self._playerData.find_one({'_id':pid}, fields={'_id':False, 'ActorInUse':True, 'Actor':True})
			return ret
		except:
			raise


	def generateItemID(self):
		uid = self._itemCounter.find_and_modify({'Item':None}, {'$inc':{'counter':1}})
		return uid['counter']


	def equip(self, pid, part, equip):
		try:
			# check available.:
			player = self._playerData.find({'_id':pid, 'Equip.'+part:None})
			if player.count() == 0:
				return False
			self._playerData.update({'_id':pid}, {'$set':{'Equip.'+part: equip}})
			return True
		except:
			raise

	# return the equip.
	def unequip(self, pid, part):
		try:
			# check available.:
			player = self._playerData.find({'_id':pid, 'Equip.'+part:None})
			if player.count() != 0:
				return None
			ret = self._playerData.find_one({'_id':pid}, fields={'Equip.'+part:True, '_id':False})
			ret = ret['Equip'][part]
			self._playerData.update({'_id':pid}, {'$set':{'Equip.'+part:None}})
			return ret
		except:
			raise



	# return True if success, False otherwise.
	def addEquipToArsenal(self, pid, part, eqp):
		try:
			# check duplication:
			player = self._playerData.find_one({'_id':pid})
			if player == None:
				return False

			chk = self._playerData.find({'_id':pid, 'Arsenal': { part :{'$elemMatch':{'_id':eqp['_id']}}}})
			if chk.count() != 0:
				return False
			else:
				data = {}
				data['_id'] = eqp['_id']
				data['type'] = eqp['type']
				data['level'] = eqp['level']
				data['star'] = eqp['star']
				data['exp'] = eqp['exp']
				self._playerData.update({'_id':pid}, {'$push':{'Arsenal.' + part:data}})
		except:
			raise

	# take an equip from Arsenal
	def takeEquipFromArsenel(self, pid, part, eid):
		try:
			chk = self._playerData.find_one({'_id':pid, 'Arsenal.' + part: {'$elemMatch':{'_id':eid}}}, fields = {'Arsenal.%s.$'%(part) :True})
			if chk == None:
				return None
			obj = chk['Arsenal'][part][0]
			self._playerData.update({'_id':pid}, {'$pull':{'Arsenal.' + part : {'_id':eid}}})
			return obj
		except:
			raise		

	def fetchPlayerEquipData(self, pid):
		try:
			# equipment.
			equip = self._playerData.find_one({'_id':pid}, fields={'Equip':True, '_id':False})
			return equip['Equip']
		except:
			raise

	def fetchPlayerArsenalData(self, pid):
		try:
			ars = self._playerData.find_one({'_id':pid}, fields={'Arsenal':True, '_id':False})
			return ars['Arsenal']
		except:
			raise

	def fetchPlayerItemData(self, pid):
		try:
			itm = self._playerData.find_one({'_id':pid}, fields={'Item':True, 'Material':True, 'Element':True, '_id':False})
			return itm
		except:
			raise

	def updatePlayerMaterial(self, pid, mat):
		try:
			player = self._playerData.find_one({'_id':pid})
			if player == None:
				return None
			self._playerData.update({'_id':pid},{'$set':{'Material':mat}})
		except:
			raise

	def updatePlayerItemData(self, pid, itm):
		try:
			player = self._playerData.find_one({'_id':pid})
			if player == None:
				return None
			self._playerData.update({'_id':pid},{'$set':{'Item':itm}})
		except:
			raise

	def getPlayerHistoryHighScore(self, pid):
		try:
			player = self._playerData.find_one({'_id':pid}, fields={'HistoryHighScore':True, '_id':False})
			if player == None:
				return None
			return player['HistoryHighScore']
		except:
			raise

	def updatePlayerHistoryHighScore(self, pid, score):
		try:
			player = self._playerData.find_one({'_id':pid})
			if player == None:
				return None
			self._playerData.update({'_id':pid},{'$set':{'HistoryHighScore':score}})
		except:
			raise

	def updatePlayerElementData(self, pid, elm):
		try:
			player = self._playerData.find_one({'_id':pid})
			if player == None:
				return None
			self._playerData.update({'_id':pid},{'$set':{'Element':elm}})
		except:
			raise

	def getTreasureRank(self):
		try:
			rank = self._treasureRank.find_one({'Rank':None})
			return rank['list']
		except:
			raise

	def updateTreasureRank(self, rank):
		try:
			self._treasureRank.update({'Rank':None}, {'list':rank})
		except:
			raise

	def restoreSpiritPurchaseChanse(self):
		try:
			self._playerData.update({}, {'$set':{'SpiritPurchase':3}}, multi = True)
		except:
			raise
