
# Copyright (c) 2015-2020 Agalmic Ventures LLC (www.agalmicventures.com)
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

# https://wiki.wireshark.org/Development/LibpcapFileFormat

#TODO: support inverted byte order

import datetime
import struct
import sys

########## Constants ##########

PCAP_MAGIC_NUMBER = 0xa1b2c3d4
PCAP_NS_MAGIC_NUMBER = 0xa1b23c4d

#Some special stuff for handling inverted byte order (not necessarily big endian -- these will be
#used for little endian caps on a big endian system
PCAP_MAGIC_NUMBER_INVERTED = 0xd4c3b2a1
PCAP_NS_MAGIC_NUMBER_INVERTED = 0x4d3cb2a1

MICROS_PER_SECOND = 1000 * 1000
NANOS_PER_SECOND = MICROS_PER_SECOND * 1000

PCAP_DEFAULT_TIME_RESOLUTION = NANOS_PER_SECOND

########## Structs ##########

#Unfortunately there is no direct way to tell the struct library to swap bytes, so we have to choose
#Based on the magic value, the parser automatically switches between structs with or without this
_structInvert = '>' if sys.byteorder == 'little' else '<'

PCAP_HEADER_STRUCT_PATTERN = 'IHHiIII'
PCAP_HEADER_STRUCT = struct.Struct(PCAP_HEADER_STRUCT_PATTERN)
PCAP_HEADER_STRUCT_INVERTED = struct.Struct(_structInvert + PCAP_HEADER_STRUCT_PATTERN)

PCAP_RECORD_HEADER_STRUCT_PATTERN = 'IIII'
PCAP_RECORD_HEADER_STRUCT = struct.Struct(PCAP_RECORD_HEADER_STRUCT_PATTERN)
PCAP_RECORD_HEADER_STRUCT_INVERTED = struct.Struct(_structInvert + PCAP_RECORD_HEADER_STRUCT_PATTERN)

########## Types ##########

class PcapHeader(object):
	"""
	Represents a PCAP file header.

	:param magicNumber: int The magic number.
	:param versionMajor: int The major version number.
	:param versionMinor: int The minor version number.
	:param tzOffset: int The time zone offset from UTC.
	:param sigfigs: int The precision of the time tamps.
	:param snaplen: int The snapshot length.
	:param network: int The network type ID.
	"""

	__slots__ = ['_magicNumber', '_timeResolution', '_versionMajor', '_versionMinor', '_tzOffset', '_sigfigs', '_snaplen', '_network']

	def __init__(self, magicNumber, versionMajor, versionMinor, tzOffset, sigfigs, snaplen, network):
		if magicNumber < 0:
			raise ValueError('magicNumber must not be negative')
		if versionMajor < 0:
			raise ValueError('versionMajor must not be negative')
		if versionMinor < 0:
			raise ValueError('versionMinor must not be negative')
		if sigfigs < 0:
			raise ValueError('sigfigs must not be negative')
		if snaplen < 0:
			raise ValueError('snaplen must not be negative')
		if network < 0:
			raise ValueError('network must not be negative')

		self._magicNumber = magicNumber
		self._timeResolution = 1000 * 1000 * 1000 if magicNumber == PCAP_NS_MAGIC_NUMBER else 1000 * 1000
		self._versionMajor = versionMajor
		self._versionMinor = versionMinor
		self._tzOffset = tzOffset
		self._sigfigs = sigfigs
		self._snaplen = snaplen
		self._network = network

	def magicNumber(self):
		"""
		Returns the magic number.

		:return: int
		"""
		return self._magicNumber

	def isMagicValid(self):
		"""
		Returns a bool indicating if the magic value is correct.

		:return: bool
		"""
		return self._magicNumber in [PCAP_MAGIC_NUMBER, PCAP_NS_MAGIC_NUMBER]

	def timeResolution(self):
		"""
		Returns the denominator of the fraction for which ts_frac is the numerator.
		For files with microsecond resolution, this will be 1e6, and for those with
		nanosecond resolution, it will be 1e9.

		:return: int
		"""
		return self._timeResolution

	def versionMajor(self):
		"""
		Returns the major version number.

		:return: int
		"""
		return self._versionMajor

	def versionMinor(self):
		"""
		Returns the minor version number.

		:return: int
		"""
		return self._versionMinor

	def tzOffset(self):
		"""
		Returns the timezone offset from GMT.

		:return: int
		"""
		return self._tzOffset

	def sigfigs(self):
		"""
		Returns the precision of the timestamps.

		:return: int
		"""
		return self._sigfigs

	def snaplen(self):
		"""
		Returns the snapshot length.

		:return: int
		"""
		return self._snaplen

	#TODO: Not thrilled about making these not immutable -- figure out how to make that efficient
	def setSnaplen(self, snaplen):
		"""
		Sets the snapshot length.

		:param snaplen: int
		"""
		self._snaplen = snaplen

	def network(self):
		"""
		Returns the data link type.

		:return: int
		"""
		return self._network

	#TODO: Not thrilled about making these not immutable -- figure out how to make that efficient
	def setNetwork(self, network):
		"""
		Sets the network (link type).

		:param network: int
		"""
		self._network = network

	def asBytes(self):
		"""
		Returns the data as bytes.

		:return: bytes or str depending on Python version
		"""
		return PCAP_HEADER_STRUCT.pack(
			self.magicNumber(),
			self.versionMajor(),
			self.versionMinor(),
			self.tzOffset(),
			self.sigfigs(),
			self.snaplen(),
			self.network(),
		)

	def writeToFile(self, output):
		"""
		Writes this as bytes to a file.

		:param output: file like object
		"""
		output.write(self.asBytes())

class PcapRecordHeader(object):
	"""
	Represents a PCAP record header.

	:param tsSec: int The timestamp seconds.
	:param tsFrac: int The timestamp fraction.
	:param includedLength: int The included length.
	:param originalLength: int The original length.
	:param fileHeader: PcapHeader The file's header (optional).
	:param strict: bool Flag indicating whether to validate strictly (default False).
	"""

	__slots__ = ['_fileHeader', '_tsSec', '_tsFrac', '_includedLength', '_originalLength']

	def __init__(self, tsSec, tsFrac, includedLength, originalLength, fileHeader=None, strict=False):
		#Basic validation for types
		if tsSec < 0:
			raise ValueError('tsSec must not be negative (%s)' % tsSec)
		if tsFrac < 0:
			raise ValueError('tsFrac must not be negative (%s)' % tsFrac)
		if tsFrac >= (fileHeader.timeResolution() if fileHeader is not None else PCAP_DEFAULT_TIME_RESOLUTION):
			raise ValueError('tsFrac is too large (%s)' % tsFrac)
		if includedLength < 0:
			raise ValueError('included_length must not be negative (%d)' % includedLength)
		if originalLength < 0:
			raise ValueError('original_length must not be negative (%d)' % originalLength)

		#Strict validation checks semantics
		if strict:
			#NOTE: Some files actually do this on purpose, for example to include additional metadata after the packet
			#Hence, this being an optional check
			if originalLength < includedLength:
				raise ValueError('original_length < included_length (%d < %d)' % (originalLength, includedLength))
			if fileHeader is not None and fileHeader.snaplen() < includedLength:
				raise ValueError('file snaplen < included_length (%d < %d)' % (fileHeader.snaplen(), includedLength))

		self._fileHeader = fileHeader
		self._tsSec = tsSec
		self._tsFrac = tsFrac
		self._includedLength = includedLength
		self._originalLength = originalLength

	def fileHeader(self):
		"""
		Returns the file header that this record came from (used for time resolution).

		:return: PcapHeader
		"""
		return self._fileHeader

	def timeResolution(self):
		"""
		Returns the denominator of the fraction for which the timestamp fraction is the numerator.

		For files with microsecond resolution, this will be 1e6, and for those with nanosecond resolution, it will be 1e9.

		:return: int
		"""
		return self._fileHeader.timeResolution() if self._fileHeader is not None else PCAP_DEFAULT_TIME_RESOLUTION

	def tsSec(self):
		"""
		Returns the seconds portion of the timestamp.

		:return: int
		"""
		return self._tsSec

	#TODO: Not thrilled about making these not immutable -- figure out how to make that efficient
	def setTsSec(self, tsSec):
		"""
		Sets the time stamp seconds.

		:param tsSec: int
		"""
		self._tsSec = tsSec

	def tsFrac(self):
		"""
		Returns the fraction portion of the timestamp.

		:return: int
		"""
		return self._tsFrac

	def epochNanos(self):
		"""
		Returns the timestamp as nanoseconds since epoch.

		:return: int
		"""
		return self._tsSec * NANOS_PER_SECOND + self._tsFrac * int(NANOS_PER_SECOND / self.timeResolution())

	def epochSecondsFloat(self):
		"""
		Returns the timestamp as a floating point number of seconds (like time.time might return,
		suitable for passing to datetime.fromtimestamp).

		:return: float
		"""
		return self._tsSec + float(self._tsFrac) / self.timeResolution()

	def timestampDatetime(self):
		"""
		Returns the timestamp a datetime.datetime. Note that this will only have microsecond resolution,
		regardless of the resolution of the file.

		:return: datetime.datetime
		"""
		#You might want to be clever and just call self.ts_float(), but don't do it! It's not accurate enough.
		microseconds = int(self._tsFrac / int(self.timeResolution() / MICROS_PER_SECOND))
		return datetime.datetime.fromtimestamp(self._tsSec) + datetime.timedelta(microseconds=microseconds)

	def includedLength(self):
		"""
		Returns the number of bytes included in the file for this packet.

		:return: int
		"""
		return self._includedLength

	#TODO: Not thrilled about making these not immutable -- figure out how to make that efficient
	def setIncludedLength(self, includedLength):
		"""
		Sets the snapshot length.

		:param snaplen: int
		"""
		self._includedLength = includedLength

	def originalLength(self):
		"""
		Returns the original number of bytes in the packet.

		:return: int
		"""
		return self._originalLength

	#TODO: Not thrilled about making these not immutable -- figure out how to make that efficient
	def setOriginalLength(self, originalLength):
		"""
		Sets the snapshot length.

		:param snaplen: int
		"""
		self._originalLength = originalLength

	def asBytes(self):
		"""
		Returns the data as bytes.

		:return: bytes or str depending on Python version
		"""
		return PCAP_RECORD_HEADER_STRUCT.pack(
			self.tsSec(),
			self.tsFrac(),
			self.includedLength(),
			self.originalLength(),
		)

	def writeToFile(self, output):
		"""
		Writes this as bytes to a file.

		:param output: file like object
		"""
		output.write(self.asBytes())
