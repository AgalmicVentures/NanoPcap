
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

    def test_parse(self):
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
