
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
        if value[i].isalpha():
            n = i
            break

    numberStr = value[:n]
    number = float(numberStr)

    unitStr = value[n:]
    for unit, multiplier in units:
        if unitStr == unit:
            return int(multiplier * number)

    raise ValueError('Uknknown unit "%s"' % unitStr)

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
