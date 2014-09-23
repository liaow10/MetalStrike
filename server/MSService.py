
# Services & Actions definitions.
SERVICE_PLAYER_CONNECTION 	= 0x0000
ACTION_PLAYER_CONNECT 		= 0x0000
ACTION_PLAYER_BEAT			= 0x0001
ACTION_PLAYER_DISCONNECT 	= 0xffff

ACTION_PLAYER_ENTER_STORE	= 0x0002

SERVICE_PLAYER_ACCOUNT			= 0x0001
ACTION_PLAYER_REGISTER 			= 0x01ff
ACTION_PLAYER_LOGIN				= 0x0100
ACTION_PLAYER_COOKIE_LOGIN		= 0x0101


#------------------------------------------
SERVICE_GAME_ENTRANCE			= 0x0002
ACTION_FETCH_ENTRANCE_DATA		= 0x0100

ACTION_PURCHASE_ACTOR			= 0x0110
ACTION_UPGRADE_ACTOR			= 0x0111
ACTION_SYNC_ACTOR				= 0x0112

ACTION_EQUIP 					= 0x0200
ACTION_UNEQUIP					= 0x0201

ACTION_UPGRADE_EQUIP			= 0x0202
ACTION_EVOLUTE_EQUIP			= 0x0203

ACTION_SELL_EQUIP				= 0x0204 
ACTION_SELL_MATERIAL			= 0x0205 
ACTION_SELL_ITEM				= 0x0206

ACTION_FETCH_WEEKLY_RANK		= 0x0207
ACTION_FETCH_FRIEND_RANK		= 0x0208

ACTION_SYNC_ASSET				= 0x02ff



ACTION_ENTER_TREASURE_MODE			= 0x0103
ACTION_ENTER_ADVENTURE_MODE			= 0x0104


#------------------------------------------
SERVICE_PLAYER_TREASURE_MODE			= 0x0005
ACTION_PLAYER_FETCH_TREASURE_DATA		= 0x0101
ACTION_PLAYER_START_TREASURE			= 0x0102

ACTION_PLAYER_TREASURE_GAME_OVER		= 0x011a	

ACTION_PLAYER_LEAVE_TREASURE_MODE		= 0x011f


#------------------------------------------
SERVICE_PLAYER_ADVENTURE_MODE			= 0x0006
ACTION_PLAYER_FETCH_ADVENTURE_DATA		= 0x0101
ACTION_PLAYER_START_ADVENTURE			= 0x0102


ACTION_PLAYER_ADVENTURE_GAME_OVER		= 0x011a
ACTION_PLAYER_LEAVE_ADVENTURE_MODE		= 0x011f

#------------------------------------------
SERVICE_STORE							= 0x0007
ACTION_PLAYER_PURCHASE_SPIRIT			= 0x000f
ACTION_PLAYER_PURCHASE_COIN				= 0x0010
ACTION_PLAYER_PURCHASE_GEM				= 0x0011
ACTION_PLAYER_PURCHASE_ITEM				= 0x0012
ACTION_PLAYER_LEAVE_STORE				= 0x0013

"""
Service is a manager class that handle actual requesting message, it will find 
a registered handler (using aid) to do specified work
"""
class Service(object):
	def __init__(self, sid = 0):
		self.serviceID = sid
		self._commandMap = {}

	"""
	The rqst should contain a aid to indicate its action id(aid)
	"""
	def execute(self, rqst, owner):
		_aid = rqst.aid
		if not _aid in self._commandMap:
			raise Exception("Bad commmand %s" %_aid)
		_func = self._commandMap[_aid]
		return _func(rqst, owner)

	def registerHandler(self, aid, func):
		self._commandMap[aid] = func

	def registerHandlerMap(self, cmdDict):
		self._commandMap = {}
		for aid, func in cmdDict.items():
			self._commandMap[aid] = func
		return 0

"""
Dispatch service according to the request's service id(sid).
"""
class Dispatcher(object):
	def __init__(self):
		self._serviceMap = {}

	def dispatch(self, rqst, owner):
		_sid = rqst.sid
		if not _sid in self._serviceMap:
			raise Exception("Bad request %s" %_sid)
		_svc = self._serviceMap[_sid]
		_svc.execute(rqst, owner)

	def register(self, sid, svc):
		self._serviceMap[sid] = svc
