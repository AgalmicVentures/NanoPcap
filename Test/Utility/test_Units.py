
import unittest

from NanoPcap.Utility import Units

class UnitsTest(unittest.TestCase):

    def test_units_1000(self):
        self.assertEqual(Units.formatUnits(342, Units.UNITS_1000), '342.0')
        self.assertEqual(Units.formatUnits(1342, Units.UNITS_1000), '1.3K')
        self.assertEqual(Units.formatUnits(671342, Units.UNITS_1000), '671.3K')
        self.assertEqual(Units.formatUnits(8671342, Units.UNITS_1000), '8.7M')
        self.assertEqual(Units.formatUnits(772671342, Units.UNITS_1000), '772.7M')
        self.assertEqual(Units.formatUnits(3471984097, Units.UNITS_1000), '3.5G')

        self.assertEqual(Units.parseUnits('342.0', Units.UNITS_1000), 342)
        self.assertEqual(Units.parseUnits('1.3K', Units.UNITS_1000), 1300)
        self.assertEqual(Units.parseUnits('671.3K', Units.UNITS_1000), 671300)
        self.assertEqual(Units.parseUnits('8.7M', Units.UNITS_1000), 8700000)
        self.assertEqual(Units.parseUnits('772.7M', Units.UNITS_1000), 772700000)
        self.assertEqual(Units.parseUnits('3.5G', Units.UNITS_1000), 3500000000)

    def test_units_1024(self):
        self.assertEqual(Units.formatUnits(342, Units.UNITS_1024), '342.0')
        self.assertEqual(Units.formatUnits(1342, Units.UNITS_1024), '1.3K')
        self.assertEqual(Units.formatUnits(671342, Units.UNITS_1024), '655.6K')
        self.assertEqual(Units.formatUnits(8671342, Units.UNITS_1024), '8.3M')
        self.assertEqual(Units.formatUnits(772671342, Units.UNITS_1024), '736.9M')
        self.assertEqual(Units.formatUnits(3471984097, Units.UNITS_1024), '3.2G')

    def test_units_time(self):
        self.assertEqual(Units.formatUnits(342, Units.UNITS_TIME), '342.0ns')
        self.assertEqual(Units.formatUnits(1342, Units.UNITS_TIME), '1.3us')
        self.assertEqual(Units.formatUnits(671342, Units.UNITS_TIME), '671.3us')
        self.assertEqual(Units.formatUnits(8671342, Units.UNITS_TIME), '8.7ms')
        self.assertEqual(Units.formatUnits(772671342, Units.UNITS_TIME), '772.7ms')
        self.assertEqual(Units.formatUnits(3471984097, Units.UNITS_TIME), '3.5s')
