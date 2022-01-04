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

from NanoPcap import Parser

def main():
	parser = argparse.ArgumentParser(description='PCAP Filter Tool')
	parser.add_argument('input1', help='PCAP file to use as input.')
	parser.add_argument('input2', help='PCAP file to use as other input.')
	parser.add_argument('output', help='Output file')

	#Validation
	parser.add_argument('--strict', action='store_true',
		help='Enables strict validation rules.')
	parser.add_argument('-R', '--require-same-linktype', action='store_true',
		help='Require the two PCAPs being merged to have the same link type.')

	arguments = parser.parse_args(sys.argv[1:])

	with gzip.open(arguments.input1, 'rb') if arguments.input1.endswith('.gz') else open(arguments.input1, 'rb') as inputFile1, \
			gzip.open(arguments.input2, 'rb') if arguments.input2.endswith('.gz') else open(arguments.input2, 'rb') as inputFile2:
		parser1 = Parser.PcapParser(inputFile1, strict=arguments.strict)
		iterator1 = parser1.parse()

		parser2 = Parser.PcapParser(inputFile2, strict=arguments.strict)
		iterator2 = parser2.parse()

		if arguments.require_same_linktype and parser1.header().network() != parser2.header().network():
			print('ERROR: Mismatched link types - %s vs %s' % (parser1.header().network(), parser2.header().network()))
			return 1

		with gzip.open(arguments.output, 'wb') if arguments.output.endswith('.gz') else open(arguments.output, 'wb') as outputFile:
			#Output the header
			parser1.header().writeToFile(outputFile)

			#Merge and output the records
			next1 = None
			nextData1 = None
			next2 = None
			nextData2 = None
			while True:
				try:
					if next1 is None:
						next1, nextData1 = iterator1.send(None)
					if next2 is None:
						next2, nextData2 = iterator2.send(None)
				except StopIteration:
					break

				if next1.epochNanos() < next2.epochNanos():
					next1.writeToFile(outputFile)
					outputFile.write(nextData1)
					next1 = None
				else:
					next2.writeToFile(outputFile)
					outputFile.write(nextData2)
					next2 = None

			if next1 is not None:
				next1.writeToFile(outputFile)
				outputFile.write(nextData1)
			if next2 is not None:
				next2.writeToFile(outputFile)
				outputFile.write(nextData2)

			#Dump any remaining (only one of these loops will do anything)
			for next, nextData in iterator1:
				next.writeToFile(outputFile)
				outputFile.write(nextData)
			for next, nextData in iterator2:
				next.writeToFile(outputFile)
				outputFile.write(nextData)

	return 0

if __name__ == '__main__':
	sys.exit(main())
