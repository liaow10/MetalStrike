# -*- coding:utf-8 -*-
import MSService
import MSMessage
import MSSession
import MSModule
import MSTaskManager
import time
import math

class MSModuleAccount(MSModule.Module):
	def __init__(self, network, dbMgr, svrDispatcher, sesTransfer):
		super(MSModuleAccount, self).__init__(MSService.SERVICE_PLAYER_ACCOUNT, network, dbMgr, svrDispatcher, sesTransfer)

		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_REGISTER, 
			self.serviceID,
			MSService.ACTION_PLAYER_REGISTER)
		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_LOGIN, 
			self.serviceID,
			MSService.ACTION_PLAYER_LOGIN)
		MSMessage.RequestManager.defineRequest(MSMessage.MSG_CS_COOKIE_LOGIN, 
			self.serviceID,
			MSService.ACTION_PLAYER_COOKIE_LOGIN)

		self.registerHandler(MSService.ACTION_PLAYER_REGISTER, self.handleRegister)
		self.registerHandler(MSService.ACTION_PLAYER_LOGIN, self.handleLogin)
		self.registerHandler(MSService.ACTION_PLAYER_COOKIE_LOGIN, self.handleCookieLogin)

		svrDispatcher.register(MSService.SERVICE_PLAYER_ACCOUNT, self)

		self.loginPlayer = []
		

	# sub-class implement this method.
	def onSessionOpen(self, session):
		#self.transferCallback(session, MSModule.MSPLAYER_STAGE_REGISTER)
		print ('session opened in Account %d')%(session.getNetHandle())
		


	# sub-class implement this method
	def onSessionClose(self, session):
		print ('session closed in Account %d')%(session.getNetHandle())

	def handleRegister(self, rqst, owner):
		if self.sessions.get(owner, None) == None:
			return
		try:
			# do account validation.
			acc = rqst.data.get('acc',None)
			acc = acc.encode('utf-8')
			pwd = rqst.data.get('pwd', None)
			pwd = pwd.encode('utf-8')
			nick = rqst.data.get('nick', None)
			for c in acc:
				if ord(c) > 128 or ord(c) == 32:
					data = {'msg':'账号必须为英文数字组合'}
					self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_REGISTER_DENIED, data))
					return
			for c in pwd:
				if ord(c) > 128 or ord(c) == 32:
					data = {'msg':'密码必须为英文数字组合'}
					self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_REGISTER_DENIED, data))
					return
			if nick == None:
				data = {'msg':'昵称不能为空'}
				self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_REGISTER_DENIED, data))
				return

			if len(acc) < 6 or len(acc) > 15:
				data = {'msg':'账号长度不合法'}
				self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_REGISTER_DENIED, data))
				return
			if len(pwd) < 6 or len(pwd) > 15:
				data = {'msg':'密码长度不合法'}
				self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_REGISTER_DENIED, data))
				return
			if len(nick) < 4 or len(nick) > 15:
				data = {'msg':'昵称长度不合法'}
				self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_REGISTER_DENIED, data))
				return


			# defensive operations on sql inception
			result = self.database.registerPlayer(acc, pwd, nick)
			if result == None:
				data = {'msg':'账号或昵称重复'}
				self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_REGISTER_DENIED, data))
			else:
				data = {'msg':'Success'}
				self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_REGISTER_CONFIRM, data))
		except:
			data = {'msg':'注册失败, 未知错误'}
			self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_REGISTER_DENIED, data))

	def handleLogin(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses == None:
			return
		try:
			# do account validation.
			acc = rqst.data.get('acc',None)
			pwd = rqst.data.get('pwd', None)
			if acc == None or pwd == None:
				data = {'msg':'账号或密码不能为空'}
				self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_LOGIN_DENIED, data))
				return
			if len(acc) < 6 or len(acc) > 15:
				data = {'msg':'账号长度不合法'}
				self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_LOGIN_DENIED, data))
				return
			if len(pwd) < 6 or len(pwd) > 15:
				data = {'msg':'密码长度不合法'}
				self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_LOGIN_DENIED, data))
				return
			# 
			result = self.database.checkPlayer(acc, pwd)
			if result == None:
				data = {'msg':'密码不匹配'}
				self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_LOGIN_DENIED, data))
			else:
				for v in self.loginPlayer:
					if v == result['_id']:
						data = {'msg':'当前玩家已经在线'}
						self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_LOGIN_DENIED, data))
						return
				self.onConfirmLogin(result, ses, owner)
		except:
			raise
			data = {'msg':'登录失败, 未知错误'}
			self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_LOGIN_DENIED, data))

	def handleCookieLogin(self, rqst, owner):
		ses = self.sessions.get(owner, None)
		if ses == None:
			return
		try:
			# do account validation.
			cookie = rqst.data['cookie']
			result = self.database.checkCookie(cookie)
			if result == None:
				data = {'msg':'Cookie 已过期'}
				self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_LOGIN_DENIED, data))
			else:
				for v in self.loginPlayer:
					if v == result['_id']:
						data = {'msg':'当前玩家已经在线'}
						self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_LOGIN_DENIED, data))
						return
				self.onConfirmLogin(result, ses, owner)
		except:
			raise
			data = {'msg':'登录失败, 未知错误'}
			self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_LOGIN_DENIED, data))

	def onConfirmLogin(self, result, ses, owner):
		data = {'msg':'Login accepted', 'pid':str(result['_id']), 'uid':result['uid'], 'nick':result['Nick'], 'cookie':result['Cookie']}
		self.network.send(owner, MSMessage.packMessage(MSMessage.MSG_SC_LOGIN_CONFIRM, data))
		ses.data['_id'] = result['_id']
		ses.data['Nick'] = result['Nick']
		ses.data['uid'] = result['uid']
		ses.data['LastSpGenTime'] = result['LastSpGenTime']
		self.loginPlayer.append(result['_id'])

		# do spirit gen.
		curTime = time.time()
		minutes = (curTime - result['LastSpGenTime'])/60
		genSp = math.floor(minutes/5)
		if genSp >= 1:
			prop = self.database.fetchPlayerProperty(ses.data['_id'])
			if prop['Spirit'] < 100:
				if prop['Spirit'] + genSp >= 100:
					genSp = 100 - prop['Spirit']
				prop['Spirit'] = genSp + prop['Spirit']
				self.database.updateSpiritGenTime(ses.data['_id'], curTime)
				ses.data['LastSpGenTime'] = curTime
				self.database.updatePlayerProperty(ses.data['_id'], prop)
			else:
				self.database.updateSpiritGenTime(ses.data['_id'], curTime)
				ses.data['LastSpGenTime'] = curTime
			ses.data['SpiritGenTick'] = MSTaskManager.TaskManager.addSustainTask(300, self.onGenSpirit, ses)
		else:
			ses.data['SpiritGenTick'] = MSTaskManager.TaskManager.addDelayTask(300 - (curTime - result['LastSpGenTime']), self.delayGenSpirit, ses)
		
		self.transferCallback(ses, MSModule.MSPLAYER_STAGE_GAME_ENTRANCE)


	def delayGenSpirit(self, ses):
		self.onGenSpirit(ses)
		ses.data['SpiritGenTick'] = MSTaskManager.TaskManager.addSustainTask(300, self.onGenSpirit, ses)


	def onGenSpirit(self, ses):
		try:
			pid = ses.data['_id']
			data = self.database.fetchPlayerProperty(pid)
			if data['Spirit'] < 100 :
				data['Spirit'] += 1
				curTime = time.time()
				self.database.updatePlayerProperty(pid, data)
				self.database.updateSpiritGenTime(pid, curTime)
				chance = self.database.getPlayerPurchaseSpiritChance(pid)
				data['chance'] = chance
				data['LastSpGenTime'] = curTime
				self.network.send(ses.getNetHandle(), MSMessage.packMessage(MSMessage.MSG_SC_RESTORE_SPIRIT, {'Spirit':1, 'LastSpGenTime':curTime, 'chance':data['chance']}))
		except:
			print 'ses failed gen spirit %s'%(ses.data['Nick'])	





	def handlePlayerDisconnected(self, session):
		_id = session.data.get('_id', None)
		if _id != None:
			self.loginPlayer.remove(_id)
			MSTaskManager.TaskManager.cancel(session.data['SpiritGenTick'])

