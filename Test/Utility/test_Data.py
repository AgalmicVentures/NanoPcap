
import unittest

from NanoPcap.Utility import Data

class DataTest(unittest.TestCase):

    def test_randomizeBytes_empty(self):
        self.assertEqual(Data.randomizeBytes(b'', 0.5), b'')

    def test_randomizeBytes_trivial(self):
        self.assertNotEqual(Data.randomizeBytes(b'1234567890', 0.0), b'')
        self.assertNotEqual(Data.randomizeBytes(b'1234567890', 1.0), b'1234567890')
