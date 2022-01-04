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

class PcapSplitListener(Listener.PcapListener):

	def __init__(self, arguments):
		self._arguments = arguments

		self._outputFileNumber = 0
		self._outputFile = None
		self._header = None

		self._resetSlice()

	def _resetSlice(self):
		if self._outputFile is not None:
			self._outputFile.close()
			self._outputFile = None
			self._outputFileNumber += 1
		self._slicePackets = 0
		self._sliceBytes = 0

	def onPcapHeader(self, header):
		self._header = header
		if self._arguments.no_header:
			return

		#Warn on a larger snap len than before
		if self._arguments.snaplen > header.snaplen():
			print('WARNING: New snaplen is greater than original: %d > %d' % (self._arguments.snaplen, header.snaplen()))

		#Update with new snaplen
		snaplen = min(self._arguments.snaplen, header.snaplen())
		self._header.setSnaplen(snaplen)

	def onPcapRecord(self, recordHeader, data):
		#Check if it's time for a new file
		newBytes = self._sliceBytes + recordHeader.includedLength()
		outOfBytes = self._arguments.max_bytes is not None and self._arguments.max_bytes < newBytes
		outOfPackets = self._arguments.max_packets is not None and self._arguments.max_packets < self._slicePackets + 1
		if outOfBytes or outOfPackets:
			self._resetSlice()

		self._sliceBytes += recordHeader.includedLength()
		self._slicePackets += 1

		#Open a file if necessary
		if self._outputFile is None:
			fileNameFormat = '%s.pcap.gz' if self._arguments.gzip_output else '%s.pcap'
			fileName = os.path.join(self._arguments.output, fileNameFormat % self._outputFileNumber)
			mode = 'ab' if self._arguments.append else 'wb'
			self._outputFile = gzip.open(fileName, mode) if fileName.endswith('.gz') else open(fileName, mode)

			#Write the header at the beginning, unless instructed otherwise
			#This neatly handles append mode
			if not self._arguments.no_header and self._outputFile.tell() == 0:
				self._header.writeToFile(self._outputFile)

		#Update with new snaplen
		#NOTE: since the link type doesn't change, the original length shouldn't either
		start = self._arguments.data_offset
		end = min(start + self._arguments.snaplen, len(data) - start - self._arguments.data_end_offset)
		truncatedData = data[start:end]
		recordHeader.setIncludedLength(len(truncatedData))

		#Write the header and data
		recordHeader.writeToFile(self._outputFile)
		self._outputFile.write(truncatedData)

def main():
	parser = argparse.ArgumentParser(description='PCAP Splitting Tool')
	parser.add_argument('input', help='PCAP file to use as input.')
	parser.add_argument('output', help='Output path -- output files will be named based on the identifying attributes.')
	parser.add_argument('--gzip-output', action='store_true',
		help='Enables gzip for the output files.')

	#Validation
	parser.add_argument('--strict', action='store_true',
		help='Enables strict validation rules.')

	#Where to split
	parser.add_argument('-b', '--max-bytes', type=int, default=None, action='store',
		help='The maximum number of bytes in a slice.')
	parser.add_argument('-p', '--max-packets', type=int, default=None, action='store',
		help='The maximum number of packets in a slice.')

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

	if arguments.max_bytes is not None and arguments.max_bytes < 1:
		print('Maximum bytes per slice must be a positive integer.')
		sys.exit(1)
	if arguments.max_packets is not None and arguments.max_packets < 1:
		print('Maximum packets per slice must be a positive integer.')
		sys.exit(1)

	listener = PcapSplitListener(arguments)
	Parser.parseFile(arguments.input, listener, strict=arguments.strict)

	return 0

if __name__ == '__main__':
	sys.exit(main())
