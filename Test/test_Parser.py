
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

import os
import unittest

from NanoPcap import Listener, Parser

#TODO: all of the relative pathing in this file is fragile and should be fixed
testDataPath = 'TestData'

class ParserTest(unittest.TestCase):

    def test_parse(self):
        listener = Listener.PcapRecordingListener()
        Parser.parseFile(os.path.join(testDataPath, 'Empty.pcap'), listener)

        self.assertTrue(listener.header() is not None)
        self.assertTrue(listener.header().isMagicValid())
        self.assertEqual(listener.header().timeResolution(), 1000 * 1000)
        self.assertEqual(listener.header().versionMajor(), 2)
        self.assertEqual(listener.header().versionMinor(), 4)
        self.assertEqual(listener.header().tzOffset(), 0)
        self.assertEqual(listener.header().sigfigs(), 0)
        self.assertEqual(listener.header().snaplen(), 0xFFFF)
        self.assertEqual(listener.header().network(), 1)

        self.assertEqual(listener.recordHeaders(), [])

    def test_parse_ns(self):
        listener = Listener.PcapRecordingListener()
        Parser.parseFile(os.path.join(testDataPath, 'EmptyNs.pcap'), listener)

        self.assertTrue(listener.header() is not None)
        self.assertTrue(listener.header().isMagicValid())
        self.assertEqual(listener.header().timeResolution(), 1000 * 1000 * 1000)
        self.assertEqual(listener.header().versionMajor(), 2)
        self.assertEqual(listener.header().versionMinor(), 4)
        self.assertEqual(listener.header().tzOffset(), 0)
        self.assertEqual(listener.header().sigfigs(), 0)
        self.assertEqual(listener.header().snaplen(), 0xFFFF)
        self.assertEqual(listener.header().network(), 1)

        self.assertEqual(listener.recordHeaders(), [])

    def test_parse_inverted(self):
        listener = Listener.PcapRecordingListener()
        Parser.parseFile(os.path.join(testDataPath, 'EmptyInverted.pcap'), listener)

        self.assertTrue(listener.header() is not None)
        self.assertTrue(listener.header().isMagicValid())
        self.assertEqual(listener.header().timeResolution(), 1000 * 1000)
        self.assertEqual(listener.header().versionMajor(), 2)
        self.assertEqual(listener.header().versionMinor(), 4)
        self.assertEqual(listener.header().tzOffset(), 0)
        self.assertEqual(listener.header().sigfigs(), 0)
        self.assertEqual(listener.header().snaplen(), 0xFFFF)
        self.assertEqual(listener.header().network(), 1)

        self.assertEqual(listener.recordHeaders(), [])

    def test_parse_ns_inverted(self):
        listener = Listener.PcapRecordingListener()
        Parser.parseFile(os.path.join(testDataPath, 'EmptyNsInverted.pcap'), listener)

        self.assertTrue(listener.header() is not None)
        self.assertTrue(listener.header().isMagicValid())
        self.assertEqual(listener.header().timeResolution(), 1000 * 1000 * 1000)
        self.assertEqual(listener.header().versionMajor(), 2)
        self.assertEqual(listener.header().versionMinor(), 4)
        self.assertEqual(listener.header().tzOffset(), 0)
        self.assertEqual(listener.header().sigfigs(), 0)
        self.assertEqual(listener.header().snaplen(), 0xFFFF)
        self.assertEqual(listener.header().network(), 1)

        self.assertEqual(listener.recordHeaders(), [])

    def test_parse_invalid_magic(self):
        listener = Listener.PcapRecordingListener()
        Parser.parseFile(os.path.join(testDataPath, 'InvalidMagic.pcap'), listener)

        self.assertTrue(listener.header() is not None)
        self.assertFalse(listener.header().isMagicValid())
        self.assertEqual(listener.header().timeResolution(), 1000 * 1000)
        self.assertEqual(listener.header().versionMajor(), 2)
        self.assertEqual(listener.header().versionMinor(), 4)
        self.assertEqual(listener.header().tzOffset(), 0)
        self.assertEqual(listener.header().sigfigs(), 0)
        self.assertEqual(listener.header().snaplen(), 0xFFFF)
        self.assertEqual(listener.header().network(), 1)

        self.assertEqual(listener.recordHeaders(), [])

    def test_parse_data(self):
        listener = Listener.PcapRecordingListener()
        Parser.parseFile(os.path.join(testDataPath, 'SSH_L3.pcap'), listener)

        self.assertTrue(listener.header() is not None)
        self.assertTrue(listener.header().isMagicValid())
        self.assertEqual(listener.header().timeResolution(), 1000 * 1000)
        self.assertEqual(listener.header().versionMajor(), 2)
        self.assertEqual(listener.header().versionMinor(), 4)
        self.assertEqual(listener.header().tzOffset(), 0)
        self.assertEqual(listener.header().sigfigs(), 0)
        self.assertEqual(listener.header().snaplen(), 0xFFFF)
        self.assertEqual(listener.header().network(), 228)

        self.assertEqual(len(listener.recordHeaders()), 21)
