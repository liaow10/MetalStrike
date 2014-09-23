

import sys
import time
import socket

import MSNetwork
import MSTaskManager
import MSService
import MSMessage
import MSDatabaseManager
import MSServerLogic

import random
1

class IOService(object):
	def process(self):
		#process network
		raise NotImplementedError

	def run(self):
		while 1:
			#self.process()
			MSTaskManager.TaskManager.scheduler()
		return

class GameServer(IOService):
	def __init__(self, tickTime = 0.1):
		super(GameServer, self).__init__()
		self._timeout = tickTime
		self._tickTimer = MSTaskManager.TaskManager.addSustainTask(tickTime, self.tick)
		return

	def tick(self):
		raise NotImplementedError

	def run(self):
		super(GameServer, self).run()

 

"""
Main server body
"""
SERVER_PORT  = 10305


class MSServer(GameServer):
	"""
	Initialize.
	"""
	def __init__(self):
		super(MSServer, self).__init__(0.1)
		self._tickStartTime = time.time()
		# Database 
		self._dbMgr = MSDatabaseManager.MSDatabaseManager()
		self._dbMgr.openDatabase("127.0.0.1", 27017)
		# Network 
		self._network = MSNetwork.NetHost()
		self._network.startup(SERVER_PORT)
		self._network.setTimer(1000)
		# Game logic
		self._clientMsgList = []
		self._serviceDispatcher = MSService.Dispatcher()
		self._gameLogic = MSServerLogic.MSServerLogic(self._network, self._dbMgr, self._serviceDispatcher)

		
	"""
	Network handling
	"""
	def process(self):
		# receive msgs from clients, then push them to the _clientMsgList
		self._network.process()
		_event, _clientHid, _clientTag, _data = self._network.read()
		_time = time.time()
		if _event != -1:
			if _event != MSNetwork.NET_TIMER:
				self._clientMsgList.append((_time, _event, _clientHid, _clientTag, _data))

	"""
	Start logic loop
	"""
	def tick(self):
		self.process()
		for n in self._clientMsgList:
			_rqst = MSMessage.RequestManager.getRequest(n[0], n[1], n[4])
			if _rqst != None:
				try:
					self._serviceDispatcher.dispatch(_rqst, n[2])
				except Exception as e:
					print e
		self._clientMsgList = []
		self._gameLogic.updateGame()


if __name__ == '__main__':
	random.seed()
	svr = MSServer()
	svr.run()
	# try:
	# 	svr.run()
	# except Exception as e:
	# 	raise
	# 	print e

	

	