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

class PcapFilterListener(Listener.PcapListener):

	def __init__(self, arguments):
		self._arguments = arguments

	def onPcapHeader(self, header):
		if self._arguments.no_header or self._arguments.append:
			return

		#Warn on a larger snap len than before
		if self._arguments.snaplen > header.snaplen():
			print('WARNING: New snaplen is greater than original: %d > %d' % (self._arguments.snaplen, header.snaplen()))

		#Check if the link type is correct
		if self._arguments.required_link_type is not None and self._arguments.required_link_type != header.network():
			print('ERROR: Link type is %d instead of %d' % (header.network(), self._arguments.required_link_type))
			sys.exit(1)

		#Update with new snaplen
		snaplen = min(self._arguments.snaplen, header.snaplen())
		header.setSnaplen(snaplen)

		#Update with the new link link
		if self._arguments.link_type is not None:
			header.setNetwork(self._arguments.link_type)

		#Write to the output file
		self._outputFile = open(arguments.output, 'ab' if arguments.append else 'wb')
		header.writeToFile(self._outputFile)

	def onPcapRecord(self, recordHeader, data):
		if self._arguments.no_records:
			return

		#Filter

		#Check the time
		epochTime = recordHeader.epochNanos()
		if self._arguments.start is not None and epochTime < self._arguments.start:
			return
		if self._arguments.end is not None and epochTime > self._arguments.end:
			return

		#Drop
		if self._arguments.drop_fraction > 0 and random.random() < self._arguments.drop_fraction:
			return

		#Update with new snaplen
		start = self._arguments.data_offset
		end = min(start + self._arguments.snaplen, len(data) - start - self._arguments.data_end_offset)
		truncatedData = data[start:end]
		recordHeader.setIncludedLength(len(truncatedData))
		if self._arguments.link_type is not None:
			recordHeader.setOriginalLength(len(truncatedData))

		#Write the header and data
		recordHeader.writeToFile(self._outputFile)
		self._outputFile.write(truncatedData)

def datetimeToEpochNanos(dt):
	seconds = (dt - datetime.datetime(1970, 1, 1)).total_seconds()
	return seconds * 1000 * 1000 * 1000

def main():
	parser = argparse.ArgumentParser(description='PCAP Filter Tool')
	parser.add_argument('input', help='PCAP file to use as input.')
	parser.add_argument('output', help='Output file')

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
	parser.add_argument('-R', '--no-records', action='store_true',
		help='Do not output records.')
	parser.add_argument('-a', '--append', action='store_true',
		help='Append to the file (implies no header).')

	#Header edits
	parser.add_argument('--required-link-type', type=int, default=None, action='store',
		help='The required link type of the file being edited (e.g. 1 for Ethernet, 228 for IPv4, 229 for IPv6).')
	parser.add_argument('--link-type', type=int, default=None, action='store',
		help='A value to set the link type in the header to (e.g. 1 for Ethernet, 228 for IPv4, 229 for IPv6).')

	#Filtering
	parser.add_argument('-s', '--start', default=None, action='store',
		help='Start time as either epoch nanoseconds or a datetime (with only microsecond resolution).')
	parser.add_argument('-e', '--end', default=None, action='store',
		help='End time as either epoch nanoseconds or a relative offset in nanoseconds to the start (e.g. +100 would yield a 100ns PCAP).')

	parser.add_argument('-D', '--drop-fraction', type=float, default=0.0, action='store',
		help='Fraction of the time to drop packagets (from 0 to 1 inclusive).')

	arguments = parser.parse_args(sys.argv[1:])

	#Parse the start time
	if arguments.start is not None:
		try:
			arguments.start = int(arguments.start)
		except ValueError:
			arguments.start = datetimeToEpochNanos(datetime.datetime.strptime(arguments.start, '%Y-%m-%d %H:%M:%S.%f'))

	#Parse the end time
	if arguments.end is not None:
		try:
			relativeEnd = arguments.end[0] == '+' and arguments.start is not None
			arguments.end = int(arguments.end)
			if relativeEnd:
				arguments.end += arguments.start
		except ValueError:
			arguments.end = datetimeToEpochNanos(datetime.datetime.strptime(arguments.end, '%Y-%m-%d %H:%M:%S.%f'))

	listener = PcapFilterListener(arguments)
	Parser.parseFile(arguments.input, listener, strict=arguments.strict)

	return 0

if __name__ == '__main__':
	sys.exit(main())
