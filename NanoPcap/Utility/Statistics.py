
import math

class OrderStatistics:
    """
    Represents naive order statistics on a set of data (useful to avoid
    pulling in dependencies for simple projects).
    """

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
        Returns the median of samples so far.

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

class SummaryStatistics:
    """
    Represents simple summary statistics on a set of data (useful to avoid
    pulling in dependencies for simple projects).
    """

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