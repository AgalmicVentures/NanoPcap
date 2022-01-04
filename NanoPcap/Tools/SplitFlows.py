#!/usr/bin/env python3

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

import argparse
import gzip
import os
import sys

import inspect
_currentFile = os.path.abspath(inspect.getfile(inspect.currentframe()))
_currentDir = os.path.dirname(_currentFile)
_parentDir = os.path.dirname(os.path.dirname(_currentDir))
sys.path.insert(0, _parentDir)

from NanoPcap import Listener, Parser
from NanoPcap.Protocols import Ethernet, IPv4

class PcapSplitFlowsListener(Listener.PcapListener):

	def __init__(self, arguments):
		self._arguments = arguments

		self._outputFiles = {}
		self._header = None

	def onPcapHeader(self, header):
		self._header = header
		if self._arguments.no_header:
			return

		#Warn on a larger snap len than before
		if self._arguments.snaplen > header.snaplen():
			print('WARNING: New snaplen is greater than original: %d > %d' % (self._arguments.snaplen, header.snaplen()))

		#Check the link type
		if header.network() == Ethernet.EthernetPacket.LINKTYPE:
			self._packetType = Ethernet.EthernetPacket
		elif header.network() == IPv4.IPv4Packet.LINKTYPE:
			self._packetType = IPv4.IPv4Packet
		else:
			print('ERROR: Link type is %d instead of %d' % (header.network(), 1))
			sys.exit(1)

		#Update with new snaplen
		snaplen = min(self._arguments.snaplen, header.snaplen())
		self._header.setSnaplen(snaplen)

	def onPcapRecord(self, recordHeader, data):
		packet = self._packetType(data)
		key = packet.key()

		fileName = os.path.join(self._arguments.output, key + '.pcap')
		outputFile = self._outputFiles.get(fileName)
		if outputFile is None:
			mode = 'ab' if self._arguments.append else 'wb'
			outputFile = gzip.open(fileName, mode) if fileName.endswith('.gz') else open(fileName, mode)

			#Write the header at the beginning, unless instructed otherwise
			#This neatly handles append mode
			if not self._arguments.no_header and outputFile.tell() == 0:
				self._header.writeToFile(outputFile)

			self._outputFiles[fileName] = outputFile

		#Update with new snaplen
		#NOTE: since the link type doesn't change, the original length shouldn't either
		start = self._arguments.data_offset
		end = min(start + self._arguments.snaplen, len(data) - start - self._arguments.data_end_offset)
		truncatedData = data[start:end]
		recordHeader.setIncludedLength(len(truncatedData))

		#Write the header and data
		recordHeader.writeToFile(outputFile)
		outputFile.write(truncatedData)

def main():
	parser = argparse.ArgumentParser(description='PCAP Flow Splitting Tool')
	parser.add_argument('input', help='PCAP file to use as input.')
	parser.add_argument('output', help='Output path -- output files will be named based on the identifying attributes.')

	#Validation
	parser.add_argument('--strict', action='store_true',
		help='Enables strict validation rules.')

	#"Where to cut" in bytes
	parser.add_argument('-l', '--snaplen', type=int, default=65535, action='store',
		help='Add a certain number of bytes for each packet record.')
	parser.add_argument('-o', '--data-offset', type=int, default=0, action='store',
		help='Offset of the data to include.')
	parser.add_argument('-x', '--data-end-offset', type=int, default=0, action='store',
		help='Offset from the end of the data to include.')
	parser.add_argument('-H', '--no-header', action='store_true',
		help='Do not output the header.')
	parser.add_argument('-a', '--append', action='store_true',
		help='Append to the file (implies no header).')

	arguments = parser.parse_args(sys.argv[1:])

	listener = PcapSplitFlowsListener(arguments)
	Parser.parseFile(arguments.input, listener, strict=arguments.strict)

	return 0

if __name__ == '__main__':
	sys.exit(main())
