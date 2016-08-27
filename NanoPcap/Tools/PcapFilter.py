#!/usr/bin/env python3

import argparse
import json
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

        self._outputFile = open(arguments.output, 'wb')

    def onPcapHeader(self, header):
        if self._arguments.no_header:
            return

        #Warn on a larger snap len than before
        if self._arguments.snaplen > header.snaplen():
            print('WARNING: New snaplen is greater than original: %d > %d' % (args.snaplen, header.snaplen()))

        #Update with new snaplen
        snaplen = min(self._arguments.snaplen, header.snaplen())
        header.setSnaplen(snaplen)

        header.writeToFile(self._outputFile)

    def onPcapRecord(self, recordHeader, data):
        if self._arguments.no_records:
            return

        #Filter
        if random.random() < self._arguments.drop_fraction:
            return

        #Update with new snaplen
        snaplen = min(self._arguments.snaplen, recordHeader.includedLength())
        recordHeader.setIncludedLength(snaplen)

        #Write the header
        recordHeader.writeToFile(self._outputFile)

        #Write the data
        truncatedData = data[self._arguments.data_offset:self._arguments.data_offset+self._arguments.snaplen]
        self._outputFile.write(truncatedData)

def main():
    parser = argparse.ArgumentParser(description='PCAP Filter Tool')
    parser.add_argument('input', help='PCAP file to use as input.')
    parser.add_argument('output', help='Output file')

    #Validation
    parser.add_argument('-s', '--strict', action='store_true',
        help='Enables strict validation rules.')

    #"Where to cut"
    parser.add_argument('-l', '--snaplen', type=int, default=65535, action='store',
        help='Add a certain number of bytes for each packet record.')
    parser.add_argument('-o', '--data-offset', type=int, default=0, action='store',
        help='Offset of the data to include.')
    parser.add_argument('-H', '--no-header', action='store_true',
        help='Do not output the header.')
    parser.add_argument('-R', '--no-records', action='store_true',
        help='Do not output records.')

    #Filtering
    parser.add_argument('-D', '--drop-fraction', type=float, default=0.0, action='store',
        help='Fraction of the time to drop packagets (from 0 to 1 inclusive).')

    arguments = parser.parse_args(sys.argv[1:])

    listener = PcapFilterListener(arguments)
    Parser.parseFile(arguments.input, listener, strict=arguments.strict)

    return 0

if __name__ == '__main__':
    sys.exit(main())
