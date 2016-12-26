
import random
import sys

if sys.version_info >= (3, ):
	xrange = range

def randomizeBytes(data, fraction):
	"""
	Randomizes a fraction of the bytes in data.

	:param data: bytes
	:param fraction: float
	:return: bytearray
	"""
	output = bytearray(data)
	for i in xrange(len(data)):
		if random.random() < fraction:
			output[i] = random.randrange(0, 256)
	return output
