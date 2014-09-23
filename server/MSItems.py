
MSWEAPON_TYPE_MACHINEGUN	= 0x0001
MSWEAPON_TYPE_SHOTGUN		= 0x0002
MSWEAPON_TYPE_LASERGUN		= 0x0003

MSARMOR_TYPE_STRIKE			= 0x0101
MSARMOR_TYPE_THUNDER		= 0x0102
MSARMOR_TYPE_GUARDIAN		= 0x0103

MSWEAPON_TYPE_DESERT_FOX	= 0x1001
MSWEAPON_TYPE_DEATH_PULSE	= 0x1002
MSWEAPON_TYPE_MISSILE		= 0x1003

MSITEM_TYPE_MGALALLOY		= 0x0121
MSITEM_TYPE_TUNGSTENSTEEL	= 0x0122
MSITEM_TYPE_TICRALLOY		= 0x0123

MSITEM_TYPE_SC				= 0x0331
MSITEM_TYPE_TI				= 0x0332
MSITEM_TYPE_V				= 0x0333
MSITEM_TYPE_CR				= 0x0334
MSITEM_TYPE_MN				= 0x0335
MSITEM_TYPE_FE				= 0x0336
MSITEM_TYPE_CO				= 0x0337
MSITEM_TYPE_NI				= 0x0338
MSITEM_TYPE_CU				= 0x0339
MSITEM_TYPE_ZN				= 0x033a
MSITEM_TYPE_Y				= 0x033b
MSITEM_TYPE_ZR				= 0x033c
MSITEM_TYPE_NB				= 0x033d
MSITEM_TYPE_MO				= 0x033e
MSITEM_TYPE_TC				= 0x033f
MSITEM_TYPE_RU				= 0x0340
MSITEM_TYPE_RH				= 0x0341
MSITEM_TYPE_PD				= 0x0342
MSITEM_TYPE_AG				= 0x0343
MSITEM_TYPE_CD				= 0x0344

from bson.objectid import ObjectId

def generateEquipment(typ, iid, level, star, exp):
	ret = {}
	ret['_id'] = iid
	ret['type'] = typ
	ret['level'] = level
	ret['exp'] = exp
	ret['star'] = star
	return ret

def isExpMaterial(typ):
	return typ == MSITEM_TYPE_MGALALLOY or typ == MSITEM_TYPE_TUNGSTENSTEEL or typ == MSITEM_TYPE_TICRALLOY

def getEvoElement(star):
	ret = []
	base = 0
	if star == '2':
		base = MSITEM_TYPE_SC
	elif star == '3':
		base = MSITEM_TYPE_FE
	elif star == '4+++':
		base = MSITEM_TYPE_Y
	elif star == '5+++':
		base = MSITEM_TYPE_RU
	else:
		raise Exception()

	for i in range(5):
		ret.append(base + i)
	return ret

