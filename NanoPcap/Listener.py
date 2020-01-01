
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
			raise RuntimeError('Tried to call PcapRecordingListener.onPcapHeader twice')

		self._header = header

	def onPcapRecord(self, recordHeader, data):
		self._recordHeaders.append(recordHeader)
