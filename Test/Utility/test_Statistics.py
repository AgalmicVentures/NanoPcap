
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

	def test_nsn(self):
		s = Statistics.OrderStatistics()
		s.sample(3.0)
		s.sample(float('nan'))

		self.assertEqual(s.n(), 1)
		self.assertEqual(s.min(), 3.0)
		self.assertEqual(s.q1(), 3.0)
		self.assertEqual(s.median(), 3.0)
		self.assertEqual(s.q3(), 3.0)
		self.assertEqual(s.max(), 3.0)

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
