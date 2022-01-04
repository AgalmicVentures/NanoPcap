
# Copyright (c) 2015-2022 Agalmic Ventures LLC (www.agalmicventures.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

def ipAddressToString(ip, separator='.'):
	"""
	Converts an IPv4 address from bytes into a string.

	:param ip: bytes
	:param separator: str
	:return: str
	"""
	return separator.join('%d' % b for b in ip)

def ipPairToKey(ip1, ip2, separator='_'):
	"""
	Converts a pair of IPv4 addresses from bytes into a key.

	:param ip1: bytes
	:param ip2: bytes
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

	LINKTYPE = 228

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
