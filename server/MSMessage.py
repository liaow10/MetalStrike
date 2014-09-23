
import struct
import socket
import json
import MSEncryption
import MSNetwork
import MSService


# Message header definitions.
MSG_CS_CONNECT                      = 0x0000
MSG_SC_WELCOME                      = 0x0001
MSG_CS_BEAT                         = 0x0002
MSG_CS_DISCONNECT                   = 0xff7f

MSG_CS_REGISTER                     = 0x0010
MSG_SC_REGISTER_CONFIRM             = 0x0011
MSG_SC_REGISTER_DENIED              = 0x0012

MSG_CS_LOGIN                        = 0x0020
MSG_CS_COOKIE_LOGIN                 = 0x0021
MSG_SC_LOGIN_CONFIRM                = 0x0022
MSG_SC_LOGIN_DENIED                 = 0x0023

MSG_CS_FETCH_PLAYER_DATA            = 0x0030
MSG_SC_FETCH_DENY                   = 0x0031
MSG_SC_PLAYER_DATA                  = 0x0032
MSG_SC_RESTORE_SPIRIT               = 0x0033

MSG_CS_UPGRADE_ACTOR                = 0x0035
MSG_CS_PURCHASE_ACTOR               = 0x0036
MSG_CS_SYNC_ACTOR                   = 0x0037
MSG_SC_SYNC_ACTOR_CONFIRM           = 0x0038
MSG_SC_SYNC_ACTOR_DENY              = 0x0039

MSG_CS_EQUIP                        = 0x0040
MSG_CS_UNEQUIP                      = 0x0041
MSG_CS_UPGRADE_EQUIP                = 0x0042
MSG_CS_EVOLUTE_EQUIP                = 0x0043
MSG_CS_SELL_EQUIP                   = 0x0044
MSG_CS_SELL_MATERIAL                = 0x0045
MSG_CS_SELL_ITEM                    = 0x0046

MSG_CS_FETCH_WEEKLY_RANK            = 0x0048
MSG_CS_FETCH_FRIEND_RANK            = 0x0049
MSG_SC_WEEKLY_RANK                  = 0x0050
MSG_SC_FRIEND_RANK                  = 0x0051


MSG_CS_SYNC_ASSET                   = 0x005f
MSG_SC_SYNC_ASSET_CONFIRM           = 0x0060
MSG_SC_SYNC_ASSET_DENY              = 0x0061

MSG_CS_ENTER_TREASURE_MODE          = 0x0140
MSG_SC_ENTER_TREASURE_MODE_CONFIRM  = 0x0141
MSG_CS_FETCH_TREASURE_MODE_DATA     = 0x0142
MSG_SC_TREASURE_MODE_DATA           = 0x0143
MSG_SC_TREASURE_MODE_DATA_DENY      = 0x0144

MSG_CS_TREASURE_GAME_OVER           = 0x0145
MSG_SC_TREASURE_CASH_UP             = 0x0146
MSG_CS_START_TREASURE               = 0x0147

MSG_CS_LEAVE_TREASURE_MODE          = 0x014d
MSG_SC_LEAVE_TREASURE_MODE_DENY     = 0x014e
MSG_SC_LEAVE_TREASURE_MODE_CONFIRM  = 0x014f

MSG_CS_ENTER_ADVENTURE_MODE         = 0x0150
MSG_SC_ENTER_ADVENTURE_MODE_CONFIRM = 0x0151
MSG_CS_FETCH_ADVENTURE_MODE_DATA    = 0x0152
MSG_SC_ADVENTURE_MODE_DATA          = 0x0153
MSG_SC_ADVENTURE_MODE_DATA_DENY     = 0x0154

MSG_CS_ADVENTURE_GAME_OVER          = 0x0155
MSG_SC_ADVENTURE_CASH_UP            = 0x0156
MSG_CS_START_ADVENTURE              = 0x0157

MSG_CS_LEAVE_ADVENTURE_MODE         = 0x015d
MSG_SC_LEAVE_ADVENTURE_MODE_DENY    = 0x015e
MSG_SC_LEAVE_ADVENTURE_MODE_CONFIRM = 0x015f


MSG_CS_ENTER_STORE                  = 0x0200
MSG_CS_LEAVE_STORE                  = 0x0201
MSG_SC_SYNC_STORE_CONFIRM           = 0x0202
MSG_SC_SYNC_STORE_DENY              = 0x0203

MSG_CS_PURCHASE_SPIRIT              = 0x0209
MSG_CS_PURCHASE_COIN                = 0x020a
MSG_CS_PURCHASE_GEM                 = 0x020b
MSG_CS_PURCHASE_ITEM                = 0x020c
MSG_SC_PURCHASE_ITEM_RESULT         = 0x020d

"""
A requrest contains a sid and aid to indicate its action, and a data field to contain
its message.
"""
class Request(object):
	def __init__(self, time, netEvent, sid, aid, data):
		self.time = time
		self.event = netEvent
		self.sid = sid
		self.aid = aid
		self.data = data


class RequestManager(object):
	requests = {}

	@staticmethod
	def defineRequest(msgID, service, action):
		RequestManager.requests[msgID] = (service, action)

	@staticmethod
	def getRequest(time, event, msg):
		if event == MSNetwork.NET_NEW :
			return Request(time, event, MSService.SERVICE_PLAYER_CONNECTION, MSService.ACTION_PLAYER_CONNECT, msg)
		if event == MSNetwork.NET_LEAVE :
			return Request(time, event, MSService.SERVICE_PLAYER_CONNECTION, MSService.ACTION_PLAYER_DISCONNECT, msg)
		if len(msg) < 2:
			return None

		# out game requrests
		_hmsg = struct.unpack('<H', msg[0:2])[0]
		_peeledmsg = msg[2:]
		_peeledmsg = MSEncryption.Decrypt(_peeledmsg)
		req = RequestManager.requests.get(_hmsg, None)
		if req != None:
			data = None
			try:
				data = json.loads(_peeledmsg)
			except:
				return None
			return Request(time, event, req[0], req[1], data)

# pack a dict into a json string and encrypt it.
def packMessage(header, data):
	_hmsg = struct.pack('<H', header)
	_msg = json.dumps(data)
	_msg = MSEncryption.Encrypt(_msg)
	return _hmsg + _msg