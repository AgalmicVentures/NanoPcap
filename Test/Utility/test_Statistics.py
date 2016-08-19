
import unittest

from NanoPcap.Utility import Statistics

class OrderStatisticsTest(unittest.TestCase):

    def test_empty(self):
        s = Statistics.OrderStatistics()
        self.assertEqual(s.n(), 0)
        self.assertEqual(s.min(), None)
        self.assertEqual(s.q1(), None)
        self.assertEqual(s.median(), None)
        self.assertEqual(s.q3(), None)
        self.assertEqual(s.max(), None)

    def test_single(self):
        s = Statistics.OrderStatistics()
        s.sample(3.0)

        self.assertEqual(s.n(), 1)
        self.assertEqual(s.min(), 3.0)
        self.assertEqual(s.q1(), 3.0)
        self.assertEqual(s.median(), 3.0)
        self.assertEqual(s.q3(), 3.0)
        self.assertEqual(s.max(), 3.0)

    def test_double(self):
        s = Statistics.OrderStatistics()
        s.sample(7.0)
        s.sample(1.0)

        self.assertEqual(s.n(), 2)
        self.assertEqual(s.min(), 1.0)
        self.assertEqual(s.q1(), 1.0)
        self.assertEqual(s.median(), 7.0)
        self.assertEqual(s.q3(), 7.0)
        self.assertEqual(s.max(), 7.0)

    def test_many(self):
        s = Statistics.OrderStatistics()
        s.sample(5.0)
        s.sample(3.0)
        s.sample(2.0)
        s.sample(4.0)
        s.sample(1.0)

        self.assertEqual(s.n(), 5)
        self.assertEqual(s.min(), 1.0)
        self.assertEqual(s.q1(), 2.0)
        self.assertEqual(s.median(), 3.0)
        self.assertEqual(s.q3(), 4.0)
        self.assertEqual(s.max(), 5.0)

class SummaryStatisticsTest(unittest.TestCase):

    def test_empty(self):
        s = Statistics.SummaryStatistics()
        self.assertEqual(s.n(), 0)
        self.assertEqual(s.sum(), 0.0)
        self.assertEqual(s.average(), 0.0)
        self.assertEqual(s.populationVariance(), 0.0)
        self.assertEqual(s.populationStddev(), 0.0)

    def test_single(self):
        s = Statistics.SummaryStatistics()
        s.sample(2.0)

        self.assertEqual(s.n(), 1)
        self.assertEqual(s.sum(), 2.0)
        self.assertEqual(s.average(), 2.0)
        self.assertEqual(s.populationVariance(), 0.0)
        self.assertEqual(s.populationStddev(), 0.0)

    def test_double(self):
        s = Statistics.SummaryStatistics()
        s.sample(5.0)
        s.sample(1.0)

        self.assertEqual(s.n(), 2)
        self.assertEqual(s.sum(), 6.0)
        self.assertEqual(s.average(), 3.0)
        self.assertEqual(s.populationVariance(), 4.0)
        self.assertEqual(s.populationStddev(), 2.0)
        self.assertEqual(s.sampleVariance(), 8.0)
