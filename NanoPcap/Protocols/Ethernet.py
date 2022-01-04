
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

from . import IPv4

#TODO: parse MAC address
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

########## Types ##########

class Ethertype(object):
	"""
	Represents an Ethertype.
	"""

	def __init__(self, id, protocol, packetType=None):
		self._id = id
		self._protocol = protocol
		self._packetType = packetType

	def id(self):
		"""
		Returns the numeric value of the Ethertype.

		:return: int
		"""
		return self._id

	def protocol(self):
		"""
		Returns the name of the protocol of the Ethertype.

		:return: str
		"""
		return self._protocol

	def packetType(self):
		"""
		Returns the class of the Packet of this Ethertype.

		:return: Packet or None
		"""
		return self._packetType

ETHERTYPES = [
	Ethertype(0x0800, 'IPv4', packetType=IPv4.IPv4Packet),
	Ethertype(0x0806, 'ARP'),
	Ethertype(0x0842, 'Wake-on-LAN'),
	Ethertype(0x22F3, 'IETF TRILL Protocol'),
	Ethertype(0x6003, 'DECnet Phase IV'),
	Ethertype(0x8035, 'Reverse ARP'),
	Ethertype(0x809B, 'Apple Talk'),
	Ethertype(0x80F3, 'Apple Talk ARP'),
	Ethertype(0x8100, 'VLAN-tagged Frame'),
	Ethertype(0x8137, 'IPX'),
	Ethertype(0x8204, 'QNX Qnet'),
	Ethertype(0x86DD, 'IPv6'),
	Ethertype(0x8808, 'Ethernet Flow Control'),
	Ethertype(0x8819, 'CobraNet'),
	Ethertype(0x8847, 'MPLS Unicast'),
	Ethertype(0x8848, 'MPLS Multicast'),
	Ethertype(0x8863, 'PPPoE Discovery'),
	Ethertype(0x8864, 'PPPoE Session'),
	Ethertype(0x88A4, 'EtherCAT'),
	Ethertype(0x88CC, 'LLDP'),
	Ethertype(0x88F7, 'PTP'),
	Ethertype(0x88FB, 'PRP'),
	Ethertype(0x8906, 'Fiber Channel over Ethernet'),
	Ethertype(0x9000, 'Ethernet Configuration Testing Protocol'),
]

ETHERTYPE_ID_TO_ETHERTYPE = {}
ETHERTYPE_PROTOCOL_TO_ETHERTYPE = {}
for ethertype in ETHERTYPES:
	assert(ethertype.id() not in ETHERTYPE_ID_TO_ETHERTYPE)
	ETHERTYPE_ID_TO_ETHERTYPE[ethertype.id()] = ethertype

	assert(ethertype.protocol() not in ETHERTYPE_PROTOCOL_TO_ETHERTYPE)
	ETHERTYPE_PROTOCOL_TO_ETHERTYPE[ethertype.protocol()] = ethertype

########## Packet ##########

class EthernetPacket(object):
	"""
	Represents an Ethernet packet and allows extracting its information.

	https://en.wikipedia.org/wiki/Ethernet_frame
	"""

	LINKTYPE = 1

	def __init__(self, data):
		self._data = data
		self._key = None
		self._ethertype = None

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

	def ethertypeId(self):
		"""
		Returns the ethertype as a numeric value.

		:return: int
		"""
		return self._data[12] * 256 + self._data[13]

	def ethertype(self):
		"""
		Returns the ethertype as an object with useful helpers.

		:return: Ethertype
		"""
		if self._ethertype is None:
			self._ethertype = ETHERTYPE_ID_TO_ETHERTYPE.get(self.ethertypeId())

		return self._ethertype

	def payload(self):
		"""
		Extracts the payload from the data.

		:return: bytes
		"""
		return self._data[14:-4]

	def crcBytes(self):
		"""
		Extracts the source MAC address from the data.

		:return: bytes
		"""
		return self._data[-4:]
