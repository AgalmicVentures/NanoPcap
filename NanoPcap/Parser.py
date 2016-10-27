
import gzip

from NanoPcap import Format

class PcapParser(object):

	def __init__(self, pcapFile, strict=False):
		"""
		Instantiates a parser for the given file-like object (file, socket, etc.)

		:param pcapFile: file-like object to parse from
		:param strict: bool Indicating strict validation
		"""
		self._pcapFile = pcapFile
		self._strict = strict

		#Read the header first
		headerBytes = pcapFile.read(Format.PCAP_HEADER_STRUCT.size)
		if len(headerBytes) != Format.PCAP_HEADER_STRUCT.size:
			raise ValueError('Could not read comple PCAP header (got only %d bytes)' % len(headerBytes))

		#Unpack the header and check for inverted byte order
		headerValues = Format.PCAP_HEADER_STRUCT.unpack(headerBytes)
		if headerValues[0] in [Format.PCAP_MAGIC_NUMBER_INVERTED, Format.PCAP_NS_MAGIC_NUMBER_INVERTED]:
			headerValues = Format.PCAP_HEADER_STRUCT_INVERTED.unpack(headerBytes)
			self._recordHeaderStruct = Format.PCAP_RECORD_HEADER_STRUCT_INVERTED
		else:
			self._recordHeaderStruct = Format.PCAP_RECORD_HEADER_STRUCT

		self._header = Format.PcapHeader(*headerValues)

	def header(self):
		"""
		Returns the PCAP file header.

		:return: PcapHeader
		"""
		return self._header

	def parse(self):
		"""
		Parses the PCAP file.

		:return: iterable of (PcapRecordHeader, data)
		"""
		#And now, walk 1 record at a time
		while True:
			recordHeaderBytes = self._pcapFile.read(self._recordHeaderStruct.size)
			if len(recordHeaderBytes) == 0:
				break #EOF
			elif len(recordHeaderBytes) != self._recordHeaderStruct.size:
				raise ValueError('Could not read comple PCAP record header (got only %d bytes)' % len(recordHeaderBytes))

			recordHeader = Format.PcapRecordHeader(
				*self._recordHeaderStruct.unpack(recordHeaderBytes),
				fileHeader=self._header, strict=self._strict)

			data = self._pcapFile.read(recordHeader.includedLength())
			if len(data) != recordHeader.includedLength():
				raise ValueError('Could not read PCAP record data (expected %d bytes; got %d)' % (
					recordHeader.includedLength(), len(data)))

			yield (recordHeader, data)

def parseFile(filename, listener, strict=False):
	"""
	Parse a PCAP with the given filename.

	:param filename: str The file to parse
	:param listener: PcapListener
	:param strict: bool Indicating strict validation
	"""
	with gzip.open(filename, 'rb') if filename.endswith('.gz') else open(filename, 'rb') as pcapFile:
		parse(pcapFile, listener, strict=strict)

def parse(pcapFile, listener, strict=False):
	"""
	Parse a PCAP from the given file-like object (file, socket, etc.)

	:param pcapFile: file-like object to parse from
	:param listener: PcapListener
	:param strict: bool Indicating strict validation
	"""
	parser = PcapParser(pcapFile, strict=strict)
	listener.onPcapHeader(parser.header())

	for recordHeader, data in parser.parse():
		listener.onPcapRecord(recordHeader, data)
