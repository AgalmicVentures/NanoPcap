#!/usr/bin/env python3

import argparse
import os
import sys

import inspect
_current_file = os.path.abspath(inspect.getfile(inspect.currentframe()))
_current_dir = os.path.dirname(_current_file)
_parent_dir = os.path.dirname(os.path.dirname(_current_dir))
sys.path.insert(0, _parent_dir)

from NanoPcap import Listener, Parser

class PcapDumpListener(Listener.PcapListener):

    def __init__(self, arguments):
        self._arguments = arguments

    def onPcapHeader(self, header):
        if self._arguments.no_header:
            return

        if self._arguments.long:
            print('  Magic:         %X' % header.magic_number())
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

    def onPcapRecord(self, recordHeader, data):
        if self._arguments.no_records:
            return

        if self._arguments.data_bytes > 0:
            truncatedData = data[self._arguments.data_offset:self._arguments.data_offset+self._arguments.data_bytes]
            dataOutput = '%s' % ' '.join('%.2X' % b for b in truncatedData)
        else:
            dataOutput = ''

        if self._arguments.long:
            print('Record')
            print('  Seconds:  %d' % recordHeader.tsSec())
            print('  Fraction: %d' % recordHeader.tsFrac())
            print('  Length:   %d' % recordHeader.includedLength())
            print('  Original: %d' % recordHeader.originalLength())
            if dataOutput != '':
                print ('  Data:     %s' % dataOutput)
        else:
            print('Record | %d.%d | Length %5d | Original: %5d | %s' % (
                recordHeader.tsSec(),
                recordHeader.tsFrac(),
                recordHeader.includedLength(),
                recordHeader.originalLength(),
                dataOutput,
            ))

def main():
    parser = argparse.ArgumentParser(description='PCAP dump diagnostic')
    parser.add_argument('pcap', help='PCAP file to dump.')
    parser.add_argument('-d', '--data-bytes', type=int, default=0, action='store',
        help='Show a certain number of bytes as hex for each packet record.')
    parser.add_argument('-l', '--long', action='store_true',
        help='Enable long form which generally puts one value per line for easy diffing.')
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