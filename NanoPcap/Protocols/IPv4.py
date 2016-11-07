
def ipAddressToString(mac, separator='.'):
	"""
	Converts a MAC address from bytes into a string.

	:param mac: bytes
	:param separator: str
	:return: str
	"""
	return separator.join('%d' % b for b in mac)

def ipPairToKey(ip1, ip2, separator='_'):
	"""
	Converts a pair of MAC addresses from bytes into a key.

	:param mac1: bytes
	:param mac2: bytes
	:param separator: str
	:return: str
	"""
	if ip1 < ip2:
		lower = ip1
		upper = ip2
	else:
		lower = ip2
		upper = ip1

	return ''.join([ipAddressToString(lower), separator, ipAddressToString(upper)])

########## Packet ##########

class IPv4Packet(object):
	"""
	Represents an IPv4 packet and allows extracting its information.

	https://en.wikipedia.org/wiki/IPv4#Packet_structure
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
			self._key = ipPairToKey(self.sourceIp(), self.destinationIp())

		return self._key

	def version(self):
		"""
		Extracts the version.

		:return: int
		"""
		return self._data[0] & 0x0F

	def ihl(self):
		"""
		Extracts the IHL.

		:return: int
		"""
		return self._data[0] >> 4

	def headerLength(self):
		"""
		Computes the header length from the IHL.

		:return: int
		"""
		return self.ihl() * 4

	def ttl(self):
		"""
		Extracts the TTL.

		:return: int
		"""
		return self._data[8]

	def protocol(self):
		"""
		Extracts the IP protocol (TCP, UDP, etc.).

		:return: int
		"""
		return self._data[9]

	#TODO: others

	def sourceIp(self):
		"""
		Extracts the source IP.

		:return: bytes
		"""
		return self._data[12:16]

	def destinationIp(self):
		"""
		Extracts the destination IP.

		:return: bytes
		"""
		return self._data[16:20]

	#TODO: options (even though they are little used)

	def payload(self):
		"""
		Extracts the payload from the data.

		:return: bytes
		"""
		return self._data[self.headerLength():]
