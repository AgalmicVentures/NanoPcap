
#TODO: parse MAC address
#TODO: logisitical support for Ethertypes
#TODO: support https://en.wikipedia.org/wiki/IEEE_802.1Q

def macAddressToString(mac, separator=':'):
	"""
	Converts a MAC address from bytes into a string.

	:param mac: bytes
	:param separator: str
	:return: str
	"""
	return separator.join('%02X' % b for b in mac)

def macPairToKey(mac1, mac2, separator='_'):
	"""
	Converts a pair of MAC addresses from bytes into a key.

	:param mac1: bytes
	:param mac2: bytes
	:param separator: str
	:return: str
	"""
	if mac1 < mac2:
		lower = mac1
		upper = mac2
	else:
		lower = mac2
		upper = mac1

	return ''.join([macAddressToString(lower), separator, macAddressToString(upper)])

class EthernetPacket(object):
	"""
	Represents an Ethernet packet and allows extracting its information.

	https://en.wikipedia.org/wiki/Ethernet_frame
	"""

	def __init__(self, data):
		self._data = data
		self._key = None

	def key(self):
		"""
		Returns this packet's MAC addresses as a key that can be used.

		:return: str
		"""
		if self._key is None:
			self._key = macPairToKey(self.destinationMac(), self.sourceMac())

		return self._key

	def destinationMac(self):
		"""
		Extracts the destination MAC address from the data.

		:return: bytes
		"""
		return self._data[0:6]

	def sourceMac(self):
		"""
		Extracts the source MAC address from the data.

		:return: bytes
		"""
		return self._data[6:12]

	def ethertypeBytes(self):
		"""
		Extracts the source MAC address from the data.

		:return: bytes
		"""
		return self._data[12:14]

	def payload(self):
		"""
		Extracts the source MAC address from the data.

		:return: bytes
		"""
		return self._data[14:-4]

	def crcBytes(self):
		"""
		Extracts the source MAC address from the data.

		:return: bytes
		"""
		return self._data[-4:]
