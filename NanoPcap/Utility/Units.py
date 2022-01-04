
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

def formatUnits(value, units, precision=1, useUnits=True):
	"""
	Formats the value with appropriate units to the given number of digits of precision.
	The use_units parameter exists as a convenience, to make this easier to use with
	argparse boolean flags for friendly formatting.

	:param value: int or float value to format
	:param units: list of tuples of unit names with their multipliers
	:param precision: number of digits of precision to use after the decimal
	:param useUnits: bool indicating if this function should display units
	"""
	if value is None:
		return None

	#No need to attach units to infinities
	elif math.isinf(value):
		return str(value)

	scaledValue = value
	unit = ''
	if useUnits:
		for name, multiplier in units:
			if value < multiplier:
				break

			scaledValue = float(value) / multiplier
			unit = name

	formatString = '%%.%df%%s' % precision
	return formatString % (float(scaledValue), unit)

def parseUnits(value, units):
	"""
	Parses a value with a unit and returns it in the base unit.

	:param value: str The value to parse
	:param units: list of tuples of unit names and multipliers
	:return: int
	"""
	n = len(value)
	for i, c in enumerate(value):
		if c.isalpha():
			n = i
			break

	numberStr = value[:n]
	number = float(numberStr)

	unitStr = value[n:]
	for unit, multiplier in units:
		if unitStr == unit:
			return int(multiplier * number)

	raise ValueError('Unknown unit "%s"' % unitStr)

#### Standard Units #####

UNITS_1000 = [
	('', 1),
	('K', 1000),
	('M', 1000 * 1000),
	('G', 1000 * 1000 * 1000),
	('T', 1000 * 1000 * 1000 * 1000),
	('P', 1000 * 1000 * 1000 * 1000 * 1000),
]

UNITS_1024 = [
	('', 1),
	('K', 1024),
	('M', 1024 * 1024),
	('G', 1024 * 1024 * 1024),
	('T', 1024 * 1024 * 1024 * 1024),
	('P', 1024 * 1024 * 1024 * 1024 * 1024),
]

UNITS_TIME = [
	('', 1),
	('ns', 1),
	('us', 1000),
	('ms', 1000 * 1000),
	('s',  1000 * 1000 * 1000),
	('m',  1000 * 1000 * 1000 * 60),
	('h',  1000 * 1000 * 1000 * 60 * 60),
	('d',  1000 * 1000 * 1000 * 60 * 60 * 24),
	('w',  1000 * 1000 * 1000 * 60 * 60 * 24 * 7),
	('fn',  1000 * 1000 * 1000 * 60 * 60 * 24 * 14),
]
