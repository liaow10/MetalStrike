# simple s^0x55


def Encrypt(s):
	res = []
	for c in s:
		res.append(chr(ord(c)^0x55))
	return ''.join(res)

def Decrypt(s):
	return Encrypt(s)