
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

import math

class OrderStatistics(object):
	"""
	Represents naive order statistics on a set of data (useful to avoid
	pulling in dependencies for simple projects).
	"""

	__slots__ = ['_samples', '_dirty']

	def __init__(self):
		self.reset()

	def reset(self):
		"""
		Resets the summary statistics.
		"""
		self._samples = []
		self._dirty = False

	def _update(self):
		self._samples.sort()
		self._dirty = False

	def sample(self, x):
		"""
		Adds a single sample.

		:param x: float
		"""
		if math.isnan(x):
			return

		self._samples.append(x)
		self._dirty = True

	def n(self):
		"""
		Returns the number of samples so far.

		:return: int
		"""
		return len(self._samples)

	def fractile(self, f):
		"""
		Returns the f-th fractile of samples so far.

		:param f: float in [0, 1]
		:return: float
		"""
		if self._dirty:
			self._update()

		n = len(self._samples)
		k = int(n * f)
		return self._samples[k] if n > 0 else None

	def median(self):
		"""
		Returns the median of samples so far.

		:return: float
		"""
		return self.fractile(0.5)

	def q1(self):
		"""
		Returns the 1st quartile of samples so far.

		:return: float
		"""
		return self.fractile(0.25)

	def q3(self):
		"""
		Returns the 3rd quartile of samples so far.

		:return: float
		"""
		return self.fractile(0.75)

	def min(self):
		"""
		Returns the min of samples so far.

		:return: float
		"""
		if self._dirty:
			self._update()
		return self._samples[0] if len(self._samples) > 0 else None

	def max(self):
		"""
		Returns the max of samples so far.

		:return: float
		"""
		if self._dirty:
			self._update()
		return self._samples[-1] if len(self._samples) > 0 else None

class SummaryStatistics(object):
	"""
	Represents simple summary statistics on a set of data (useful to avoid
	pulling in dependencies for simple projects).
	"""

	__slots__ = ['_n', '_sum', '_average', '_m2']

	def __init__(self):
		self.reset()

	def reset(self):
		"""
		Resets the summary statistics.
		"""
		self._n = 0
		self._sum = 0
		self._average = 0.0
		self._m2 = 0.0

	def sample(self, x):
		"""
		Adds a single sample.

		:param x: float
		"""
		self._n += 1
		self._sum += x

		delta = x - self._average
		self._average += delta / self._n
		self._m2 += delta * (x - self._average)

	def n(self):
		"""
		Returns the number of the samples.

		:return: int
		"""
		return self._n

	def sum(self):
		"""
		Returns the sum of the samples.

		:return: float
		"""
		return self._sum

	def average(self):
		"""
		Returns the average of the samples.

		:return: float
		"""
		return self._average

	def populationVariance(self):
		"""
		Returns the variance of the samples.

		:return: float
		"""
		if self.n() < 2:
			return 0.0

		return self._m2 / (self._n)

	def populationStddev(self):
		"""
		Returns the stddev of samples so far.

		:return: float
		"""
		if self.n() < 2:
			return 0.0

		return math.sqrt(self.populationVariance())

	def sampleVariance(self):
		"""
		Returns the variance of samples so far.

		:return: float
		"""
		if self.n() < 2:
			return 0.0

		return self._m2 / (self._n - 1)

	def sampleStddev(self):
		"""
		Returns the standard deviation.

		:return: float
		"""
		if self.n() < 2:
			return 0.0

		return math.sqrt(self.sampleVariance())
