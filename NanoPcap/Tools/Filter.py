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
import datetime
import gzip
import os
import random
import sys

import inspect
_currentFile = os.path.abspath(inspect.getfile(inspect.currentframe()))
_currentDir = os.path.dirname(_currentFile)
_parentDir = os.path.dirname(os.path.dirname(_currentDir))
sys.path.insert(0, _parentDir)

from NanoPcap import Listener, Parser
from NanoPcap.Utility import Data

class PcapFilterListener(Listener.PcapListener):

	def __init__(self, arguments):
		self._arguments = arguments

		self._lastPacketDatas = []
		self._outputFileName = None
		self._outputFile = None
		self._header = None

	def onPcapHeader(self, header):
		self._header = header

		#Warn on a larger snap len than before
		if self._arguments.snaplen > header.snaplen():
			print('WARNING: New snaplen is greater than original: %d > %d' % (self._arguments.snaplen, header.snaplen()))

		#Check if the link type is correct
		if self._arguments.required_link_type is not None and self._arguments.required_link_type != header.network():
			print('ERROR: Link type is %d instead of %d' % (header.network(), self._arguments.required_link_type))
			sys.exit(1)

		#Update with new snaplen
		snaplen = min(self._arguments.snaplen, header.snaplen())
		self._header.setSnaplen(snaplen)

		#Update with the new link link
		if self._arguments.link_type is not None:
			self._header.setNetwork(self._arguments.link_type)

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

		#Drop?
		if self._arguments.drop_fraction > 0 and random.random() < self._arguments.drop_fraction:
			return

		#De-duplicate
		if self._arguments.deduplication_window > 0:
			found = False
			for packetData in self._lastPacketDatas:
				if packetData == data:
					found = True
					break

			self._lastPacketDatas.append(data)
			if len(self._lastPacketDatas) > self._arguments.deduplication_window:
				self._lastPacketDatas.pop(0)
			if found:
				return

		#Roll the file if necessary
		newOutputFileName = recordHeader.timestampDatetime().strftime(self._arguments.output)
		if newOutputFileName != self._outputFileName:
			if self._outputFile is not None:
				self._outputFile.close()

			#Write to the output file
			self._outputFileName = newOutputFileName
			directory, fileName = os.path.split(self._outputFileName)
			if directory != '' and not os.path.exists(directory):
				os.makedirs(directory)

			mode = 'ab' if self._arguments.append else 'wb'
			self._outputFile = gzip.open(self._outputFileName, mode) if self._outputFileName.endswith('.gz') else open(self._outputFileName, mode)
			#Write the header at the beginning, unless instructed otherwise
			#This neatly handles append mode
			if not self._arguments.no_header and self._outputFile.tell() == 0:
				self._header.writeToFile(self._outputFile)

		#Update with new snaplen
		start = self._arguments.data_offset
		end = min(start + self._arguments.snaplen, len(data) - start - self._arguments.data_end_offset)
		truncatedData = data[start:end]
		recordHeader.setIncludedLength(len(truncatedData))
		if self._arguments.link_type is not None:
			recordHeader.setOriginalLength(len(truncatedData))

		#Update with the new timestamp if necessary
		if self._arguments.time_shift_seconds is not None:
			recordHeader.setTsSec(recordHeader.tsSec() + self._arguments.time_shift_seconds)

		#Write the header
		recordHeader.writeToFile(self._outputFile)

		#Write the data, randomizing if necessary
		if self._arguments.data_randomization_fraction > 0:
			newTruncatedData = Data.randomizeBytes(truncatedData, self._arguments.data_randomization_fraction)
			self._outputFile.write(newTruncatedData)
		else:
			self._outputFile.write(truncatedData)

		#Duplicate?
		if self._arguments.duplicate_fraction > 0 and random.random() < self._arguments.duplicate_fraction:
			recordHeader.writeToFile(self._outputFile)
			self._outputFile.write(truncatedData)

def datetimeToEpochNanos(dt):
	seconds = (dt - datetime.datetime(1970, 1, 1)).total_seconds()
	return seconds * 1000 * 1000 * 1000

def main():
	parser = argparse.ArgumentParser(description='PCAP Filter Tool')
	parser.add_argument('input', help='PCAP file to use as input.')
	parser.add_argument('output', help='Output file. May include time format strings to roll the file based on packet time stamps, e.g. %%Y/%%m/%%d/%%H.pcap for hourly output files in daily folders.')

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
	parser.add_argument('--data-randomization-fraction', type=float, default=0.0, action='store',
		help='Fraction of the data bytes to randomize (from 0 to 1 inclusive).')

	#Header edits
	parser.add_argument('--required-link-type', type=int, default=None, action='store',
		help='The required link type of the file being edited (e.g. 1 for Ethernet, 228 for IPv4, 229 for IPv6).')
	parser.add_argument('--link-type', type=int, default=None, action='store',
		help='A value to set the link type in the header to (e.g. 1 for Ethernet, 228 for IPv4, 229 for IPv6).')

	parser.add_argument('--time-shift-seconds', type=int, default=None, action='store',
		help='The amount of time in seconds to shift timestamps in the output PCAP.')

	#Filtering
	parser.add_argument('-s', '--start', default=None, action='store',
		help='Start time as either epoch nanoseconds or a datetime (with only microsecond resolution).')
	parser.add_argument('-e', '--end', default=None, action='store',
		help='End time as either epoch nanoseconds or a relative offset in nanoseconds to the start (e.g. +100 would yield a 100ns PCAP).')

	parser.add_argument('-D', '--drop-fraction', type=float, default=0.0, action='store',
		help='Fraction of the time to drop packagets (from 0 to 1 inclusive).')
	parser.add_argument('--duplicate-fraction', type=float, default=0.0, action='store',
		help='Fraction of the time to duplicate packagets (from 0 to 1 inclusive).')
	parser.add_argument('--deduplication-window', type=int, default=0, action='store',
		help='Sets the number of the packets in the deduplication window (based on contents).')

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
