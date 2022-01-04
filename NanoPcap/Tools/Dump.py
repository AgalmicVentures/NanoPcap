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
import json
import os
import sys

import inspect
_currentFile = os.path.abspath(inspect.getfile(inspect.currentframe()))
_currentDir = os.path.dirname(_currentFile)
_parentDir = os.path.dirname(os.path.dirname(_currentDir))
sys.path.insert(0, _parentDir)

from NanoPcap import Listener, Parser

class PcapDumpListener(Listener.PcapListener):

	def __init__(self, arguments):
		self._arguments = arguments

	def onPcapHeader(self, header):
		if self._arguments.no_header:
			return

		if self._arguments.json:
			print(json.dumps({
				'Magic': header.magicNumber(),
				'Valid': header.isMagicValid() ,
				'Resolution': header.timeResolution(),
				'MajorVersion': header.versionMajor(),
				'MinorVersion': header.versionMinor(),
				'TzOffset': header.tzOffset(),
				'Sigfigs': header.sigfigs(),
				'Snaplen': header.snaplen(),
				'Network': header.network(),
			}, indent=2 if self._arguments.long else None, sort_keys=True))
			if self._arguments.long:
				print()
		elif self._arguments.long:
			print('  Magic:         %X' % header.magicNumber())
			print('  Valid:         %s' % ("Valid" if header.isMagicValid() else "Invalid"))
			print('  Resolution:    %s' % ("Micros" if header.timeResolution() == 1000 * 1000 else "Nanos"))
			print('  Major Version: %d' % header.versionMajor())
			print('  Minor Version: %d' % header.versionMinor())
			print('  TZ Offset:     %d' % header.tzOffset())
			print('  Sigfigs:       %d' % header.sigfigs())
			print('  Snaplen:       %d' % header.snaplen())
			print('  Network:       %d' % header.network())
		else:
			print('Header | Magic: %X %s %s | Version %d . %d | TZ Offset: %d | Sigfigs: %d | Snaplen: %d | Network: %d' % (
				header.magicNumber(),
				"Valid" if header.isMagicValid() else "Invalid",
				"Micros" if header.timeResolution() == 1000 * 1000 else "Nanos",
				header.versionMajor(),
				header.versionMinor(),
				header.tzOffset(),
				header.sigfigs(),
				header.snaplen(),
				header.network(),
			))
		if self._arguments.no_records:
			#No need to continue processing the rest of the file, and no simpler way to exit
			sys.exit(0)

	def onPcapRecord(self, recordHeader, data):
		if self._arguments.data_bytes > 0:
			truncatedData = data[self._arguments.data_offset:self._arguments.data_offset+self._arguments.data_bytes]
			dataOutput = '%s' % ' '.join('%.2X' % b for b in truncatedData)
		else:
			dataOutput = ''

		if self._arguments.json:
			print(json.dumps({
				'Seconds': recordHeader.tsSec(),
				'Fraction': recordHeader.tsFrac(),
				'IncludedLength': recordHeader.includedLength(),
				'OriginalLength': recordHeader.originalLength(),
			}, indent=2 if self._arguments.long else None, sort_keys=True))
			if self._arguments.long:
				print()
		elif self._arguments.long:
			print('Record')
			print('  Seconds:  %d' % recordHeader.tsSec())
			print('  Fraction: %d' % recordHeader.tsFrac())
			print('  Length:   %d' % recordHeader.includedLength())
			print('  Original: %d' % recordHeader.originalLength())
			if dataOutput != '':
				print ('  Data:	 %s' % dataOutput)
		else:
			print('Record | %d.%d | Length %5d | Original: %5d | %s' % (
				recordHeader.tsSec(),
				recordHeader.tsFrac(),
				recordHeader.includedLength(),
				recordHeader.originalLength(),
				dataOutput,
			))

def main():
	parser = argparse.ArgumentParser(description='PCAP Dump Diagnostic')
	parser.add_argument('pcap', help='PCAP file to dump.')
	parser.add_argument('-d', '--data-bytes', type=int, default=0, action='store',
		help='Show a certain number of bytes as hex for each packet record.')
	parser.add_argument('-l', '--long', action='store_true',
		help='Enable long form which generally puts one value per line for easy diffing.')
	parser.add_argument('-j', '--json', action='store_true',
		help='Enable JSON output with either one object per line (short mode) or one value per line (long mode).')
	parser.add_argument('-o', '--data-offset', type=int, default=0, action='store',
		help='Offset of the data to show.')
	parser.add_argument('-H', '--no-header', action='store_true',
		help='Do not show the header.')
	parser.add_argument('-R', '--no-records', action='store_true',
		help='Do not show records.')
	parser.add_argument('-s', '--strict', action='store_true',
		help='Enables strict validation rules.')
	arguments = parser.parse_args(sys.argv[1:])

	listener = PcapDumpListener(arguments)
	Parser.parseFile(arguments.pcap, listener, strict=arguments.strict)

	return 0

if __name__ == '__main__':
	sys.exit(main())
