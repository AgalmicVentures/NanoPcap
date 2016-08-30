#!/usr/bin/env python3

import argparse
import datetime
import os
import random
import sys

import inspect
_currentFile = os.path.abspath(inspect.getfile(inspect.currentframe()))
_currentDir = os.path.dirname(_currentFile)
_parentDir = os.path.dirname(os.path.dirname(_currentDir))
sys.path.insert(0, _parentDir)

from NanoPcap import Listener, Parser

def main():
	parser = argparse.ArgumentParser(description='PCAP Filter Tool')
	parser.add_argument('input1', help='PCAP file to use as input.')
	parser.add_argument('input2', help='PCAP file to use as other input.')
	parser.add_argument('output', help='Output file')

	#Validation
	parser.add_argument('--strict', action='store_true',
		help='Enables strict validation rules.')
	#TODO: flag to require same link type?

	arguments = parser.parse_args(sys.argv[1:])

	with open(arguments.input1, 'rb') as inputFile1, open(arguments.input2, 'rb') as inputFile2:
		parser1 = Parser.PcapParser(inputFile1, strict=arguments.strict)
		iterator1 = parser1.parse()

		parser2 = Parser.PcapParser(inputFile2, strict=arguments.strict)
		iterator2 = parser2.parse()

		#TODO: validate link types, snap lengths, etc.

		with open(arguments.output, 'wb') as outputFile:
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
