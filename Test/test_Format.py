
# Copyright (c) 2015-2020 Agalmic Ventures LLC (www.agalmicventures.com)
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

import unittest

from NanoPcap import Format

class FormatTest(unittest.TestCase):

    def setUp(self):
        self._initialHeader = (1234, 5678, 9102, -1, 3456, 7890, 4321)
        self._initialRecordHeader = (1463179445, 10 * 1000 * 1000, 9102, 3456)

    def test_header(self):
        self.assertEqual(Format.PCAP_HEADER_STRUCT.size, 24)

        initial = self._initialHeader
        packed = Format.PCAP_HEADER_STRUCT.pack(*initial)
        unpacked = Format.PCAP_HEADER_STRUCT.unpack(packed)
        self.assertEqual(unpacked, initial)

        header = Format.PcapHeader(*initial)
        self.assertEqual(header.magicNumber(), initial[0])
        self.assertEqual(header.timeResolution(), 1000 * 1000)
        self.assertEqual(header.versionMajor(), initial[1])
        self.assertEqual(header.versionMinor(), initial[2])
        self.assertEqual(header.tzOffset(), initial[3])
        self.assertEqual(header.sigfigs(), initial[4])
        self.assertEqual(header.snaplen(), initial[5])
        self.assertEqual(header.network(), initial[6])
        self.assertFalse(header.isMagicValid())

        byteValue = header.asBytes()
        self.assertEqual(byteValue, packed)

    def test_headerMagic(self):
        correctMagicInitial = list(self._initialHeader)
        correctMagicInitial[0] = Format.PCAP_MAGIC_NUMBER
        correctHeader = Format.PcapHeader(*correctMagicInitial)
        self.assertEqual(correctHeader.magicNumber(), Format.PCAP_MAGIC_NUMBER)
        self.assertEqual(correctHeader.timeResolution(), 1000 * 1000)
        self.assertTrue(correctHeader.isMagicValid())

    def test_headerMagicNs(self):
        correctMagicInitial = list(self._initialHeader)
        correctMagicInitial[0] = Format.PCAP_NS_MAGIC_NUMBER
        correctHeaderNs = Format.PcapHeader(*correctMagicInitial)
        self.assertEqual(correctHeaderNs.magicNumber(), Format.PCAP_NS_MAGIC_NUMBER)
        self.assertEqual(correctHeaderNs.timeResolution(), 1000 * 1000 * 1000)
        self.assertTrue(correctHeaderNs.isMagicValid())

    def testRecord(self):
        self.assertEqual(Format.PCAP_RECORD_HEADER_STRUCT.size, 16)

        initial = self._initialRecordHeader
        packed = Format.PCAP_RECORD_HEADER_STRUCT.pack(*initial)
        unpacked = Format.PCAP_RECORD_HEADER_STRUCT.unpack(packed)
        self.assertEqual(unpacked, initial)

        recordHeader = Format.PcapRecordHeader(*initial)
        self.assertEqual(recordHeader.tsSec(), initial[0])
        self.assertEqual(recordHeader.tsFrac(), initial[1])
        self.assertEqual(recordHeader.epochNanos(), initial[0] * 1000 * 1000 * 1000 + initial[1])
        self.assertEqual(recordHeader.epochSecondsFloat(), 1463179445.010)

        byteValue = recordHeader.asBytes()
        self.assertEqual(byteValue, packed)

        d = recordHeader.timestampDatetime()
        self.assertEqual(d.year, 2016)
        self.assertEqual(d.month, 5)
        self.assertEqual(d.day, 13)
        #TODO: make this time-zone agnostic self.assertEqual(d.hour, 17)
        self.assertEqual(d.minute, 44)
        self.assertEqual(d.second, 5)
        self.assertEqual(d.microsecond, 10 * 1000)

        self.assertEqual(recordHeader.includedLength(), initial[2])
        self.assertEqual(recordHeader.originalLength(), initial[3])
