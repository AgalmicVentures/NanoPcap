#!/usr/bin/env python3

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
from NanoPcap.Protocols import Ethernet

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

		#Update with new snaplen
		snaplen = min(self._arguments.snaplen, header.snaplen())
		self._header.setSnaplen(snaplen)

	def onPcapRecord(self, recordHeader, data):
		ethernetPacket = Ethernet.EthernetPacket(data)
		key = ethernetPacket.key()
		fileName = os.path.join(self._arguments.output, key + '.pcap')

		outputFile = self._outputFiles.get(fileName)
		if outputFile is None:
			mode = 'ab' if self._arguments.append else 'wb'
			outputFile = gzip.open(fileName, mode) if fileName.endswith('.gz') else open(fileName, mode)

			#TODO: should this write the header in append mode if there is nothing yet in the file?
			if not (self._arguments.no_header or self._arguments.append):
				self._header.writeToFile(outputFile)

			self._outputFiles[fileName] = outputFile

		#Update with new snaplen
		start = self._arguments.data_offset
		end = min(start + self._arguments.snaplen, len(data) - start - self._arguments.data_end_offset)
		truncatedData = data[start:end]
		recordHeader.setIncludedLength(len(truncatedData))
		if self._arguments.link_type is not None:
			recordHeader.setOriginalLength(len(truncatedData))

		#Write the header and data
		recordHeader.writeToFile(outputFile)
		outputFile.write(truncatedData)

def main():
	parser = argparse.ArgumentParser(description='PCAP Filter Tool')
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

	parser.add_argument('--link-type', type=int, default=None, action='store',
		help='A value to set the link type in the header to (e.g. 1 for Ethernet, 228 for IPv4, 229 for IPv6).')

	arguments = parser.parse_args(sys.argv[1:])

	listener = PcapSplitFlowsListener(arguments)
	Parser.parseFile(arguments.input, listener, strict=arguments.strict)

	return 0

if __name__ == '__main__':
	sys.exit(main())
