
class PcapListener(object):
	"""
	Represents a generic PCAP event listener.
	"""

	def onPcapHeader(self, header):
		"""
		Called once per file before any other callbacks.

		:param header: PcapHeader
		"""
		raise NotImplementedError('PcapListener.onPcapHeader is pure virtual!')

	def onPcapRecord(self, recordHeader, data):
		"""
		Called once per record in the file.

		:param record_header: PcapRecordHeader
		:param data: bytes
		"""
		raise NotImplementedError('PcapListener.onPcapRecord is pure virtual!')

class PcapDoNothingListener(object):
	"""
	Implementation of PcapListener which discards events.
	"""

	def onPcapHeader(self, header):
		pass #Do nothing

	def onPcapRecord(self, recordHeader, data):
		pass #Do nothing

class PcapRecordingListener(object):
	"""
	Implementation of PcapListener which records headers for later use.
	"""

	def __init__(self):
		self._header = None
		self._recordHeaders = []

	def header(self):
		"""
		Returns the header, or None if no header has been processed yet.

		:return: PcapHeader or None
		"""
		return self._header

	def recordHeaders(self):
		"""
		Returns the header, or None if no header has been processed yet.

		:return: list of PcapRecordHeader
		"""
		return self._recordHeaders

	def onPcapHeader(self, header):
		if self._header is not None:
			raise RuntimeError('Tried to call PcapRecordingListener.on_pcap_header twice')

		self._header = header

	def onPcapRecord(self, recordHeader, data):
		self._recordHeaders.append(recordHeader)
