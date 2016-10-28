#!/usr/bin/env python3

import argparse
import datetime
import json
import math
import os
import sys

import inspect
_currentFile = os.path.abspath(inspect.getfile(inspect.currentframe()))
_currentDir = os.path.dirname(_currentFile)
_parentDir = os.path.dirname(os.path.dirname(_currentDir))
sys.path.insert(0, _parentDir)

from NanoPcap.Listener import PcapListener
from NanoPcap.Parser import parseFile
from NanoPcap.Utility import Statistics, Units

class PcapSummaryListener(PcapListener):

	def __init__(self, arguments):
		self._arguments = arguments

		self._includedLengths = Statistics.SummaryStatistics()
		self._includedLengthsOrder = Statistics.OrderStatistics()
		self._originalLengths = Statistics.SummaryStatistics()
		self._originalLengthsOrder = Statistics.OrderStatistics()

		self._lastNs = None
		self._interpacketNs = Statistics.SummaryStatistics()
		self._interpacketNsOrder = Statistics.OrderStatistics()
		self._epochNs = Statistics.SummaryStatistics()
		self._epochNsOrder = Statistics.OrderStatistics()
		self._packetRatesOrder = Statistics.OrderStatistics()
		self._dataRatesOrder = Statistics.OrderStatistics()

	def _formatRate1000(self, value):
		return Units.formatUnits(value, Units.UNITS_1000, useUnits=self._arguments.use_units)

	def _formatRate1024(self, value):
		return Units.formatUnits(value, Units.UNITS_1024, useUnits=self._arguments.use_units)

	def _formatTime(self, value):
		return Units.formatUnits(value, Units.UNITS_TIME, useUnits=self._arguments.use_units)

	def printReport(self):
		formatString = '%-22s %10s %16s %14s %14s %14s %14s %14s %14s %14s %14s %14s %14s' if not self._arguments.use_units else '%-22s %8s %8s %8s %8s %8s %8s %8s %8s %8s %8s %8s %8s'
		if not self._arguments.no_header:
			if self._epochNsOrder.n() > 0:
				print('Epoch times: %d - %d (%dns) (%s - %s)' % (
					self._epochNsOrder.min(), self._epochNsOrder.max(),
					self._epochNsOrder.max() - self._epochNsOrder.min(),
					datetime.datetime.utcfromtimestamp(self._epochNsOrder.min() / (1000 * 1000 * 1000)),
					datetime.datetime.utcfromtimestamp(self._epochNsOrder.max() / (1000 * 1000 * 1000)),
				))
				print()
			print(formatString % ('Name', 'Count', 'Total', 'Average', 'Std Dev', 'Min', '25th %', '50th %', '75th %', '95th %', '99th %', '99.9th %', 'Max'))

		print(formatString % ('Included Length',
			self._includedLengths.n(),
			self._formatRate1024(self._includedLengths.sum()),
			'%.2f' % self._includedLengths.average(),
			'%.2f' % self._includedLengths.populationStddev(),
			self._includedLengthsOrder.min(),
			self._includedLengthsOrder.q1(),
			self._includedLengthsOrder.median(),
			self._includedLengthsOrder.q3(),
			self._includedLengthsOrder.fractile(0.95),
			self._includedLengthsOrder.fractile(0.99),
			self._includedLengthsOrder.fractile(0.999),
			self._includedLengthsOrder.max(),
		))
		print(formatString % ('Original Length',
			self._originalLengths.n(),
			self._formatRate1024(self._originalLengths.sum()),
			'%.2f' % self._originalLengths.average(),
			'%.2f' % self._originalLengths.populationStddev(),
			self._originalLengthsOrder.min(),
			self._originalLengthsOrder.q1(),
			self._originalLengthsOrder.median(),
			self._originalLengthsOrder.q3(),
			self._originalLengthsOrder.fractile(0.95),
			self._originalLengthsOrder.fractile(0.99),
			self._originalLengthsOrder.fractile(0.999),
			self._originalLengthsOrder.max(),
		))
		print(formatString % ('Interpacket Time (ns)',
			self._interpacketNs.n(),
			self._formatTime(self._interpacketNs.sum()),
			self._formatTime(self._interpacketNs.average()),
			self._formatTime(self._interpacketNs.populationStddev()),
			self._formatTime(self._interpacketNsOrder.min()),
			self._formatTime(self._interpacketNsOrder.q1()),
			self._formatTime(self._interpacketNsOrder.median()),
			self._formatTime(self._interpacketNsOrder.q3()),
			self._formatTime(self._interpacketNsOrder.fractile(0.95)),
			self._formatTime(self._interpacketNsOrder.fractile(0.99)),
			self._formatTime(self._interpacketNsOrder.fractile(0.999)),
			self._formatTime(self._interpacketNsOrder.max()),
		))
		print(formatString % ('Packet Rate (pps)',
			self._interpacketNs.n(),
			'',
			self._formatRate1000(1.0e9 / self._interpacketNs.average() if self._interpacketNs.n() > 0 else float('inf')),
			'',
			self._formatRate1000(self._packetRatesOrder.min()),
			self._formatRate1000(self._packetRatesOrder.q1()),
			self._formatRate1000(self._packetRatesOrder.median()),
			self._formatRate1000(self._packetRatesOrder.q3()),
			self._formatRate1000(self._packetRatesOrder.fractile(0.95)),
			self._formatRate1000(self._packetRatesOrder.fractile(0.99)),
			self._formatRate1000(self._packetRatesOrder.fractile(0.999)),
			self._formatRate1000(self._packetRatesOrder.max()),
		))
		print(formatString % ('Data Rate (Bps)',
			self._dataRatesOrder.n(),
			'',
			'',
			'',
			self._formatRate1024(self._dataRatesOrder.min()),
			self._formatRate1024(self._dataRatesOrder.q1()),
			self._formatRate1024(self._dataRatesOrder.median()),
			self._formatRate1024(self._dataRatesOrder.q3()),
			self._formatRate1024(self._dataRatesOrder.fractile(0.95)),
			self._formatRate1024(self._dataRatesOrder.fractile(0.99)),
			self._formatRate1024(self._dataRatesOrder.fractile(0.999)),
			self._formatRate1024(self._dataRatesOrder.max()),
		))
		print()

		#Compute the minimum line rate that would accomodate this data rate
		#NOTE: line rates are in bits per second, hence the multiplication
		maxDataRate = self._dataRatesOrder.max() * 8
		nextPowerOf10DataRate = 10 ** math.ceil(math.log10(maxDataRate))
		maxDataRateFraction = maxDataRate / nextPowerOf10DataRate
		print('Based on the maximum data rate, the line rate must be at least: %s with peak utilization of %.1f%%' % (
			self._formatRate1000(nextPowerOf10DataRate), 100.0 * maxDataRateFraction))
		if maxDataRateFraction > 0.8:
			print('WARNING: Peak data rates are approaching the limit of your line')

	def printJsonReport(self):
		output = {
			'includedLength': {
				'n': self._includedLengths.n(),
				'sum': self._includedLengths.sum(),
				'average': self._includedLengths.average(),
				'stddev': self._includedLengths.populationStddev(),
				'min': self._includedLengthsOrder.min(),
				'q1': self._includedLengthsOrder.q1(),
				'median': self._includedLengthsOrder.median(),
				'q3': self._includedLengthsOrder.q3(),
				'p95': self._includedLengthsOrder.fractile(0.95),
				'p99': self._includedLengthsOrder.fractile(0.99),
				'p999': self._includedLengthsOrder.fractile(0.999),
				'max': self._includedLengthsOrder.max(),
			},
			'originalLength': {
				'n': self._originalLengths.n(),
				'sum': self._originalLengths.sum(),
				'average': self._originalLengths.average(),
				'stddev': self._originalLengths.populationStddev(),
				'min': self._originalLengthsOrder.min(),
				'q1': self._originalLengthsOrder.q1(),
				'median': self._originalLengthsOrder.median(),
				'q3': self._originalLengthsOrder.q3(),
				'p95': self._originalLengthsOrder.fractile(0.95),
				'p99': self._originalLengthsOrder.fractile(0.99),
				'p999': self._originalLengthsOrder.fractile(0.999),
				'max': self._originalLengthsOrder.max(),
			},
			'interpacketTime': {
				'n': self._interpacketNs.n(),
				'sum': self._interpacketNs.sum(),
				'average': self._interpacketNs.average(),
				'stddev': self._interpacketNs.populationStddev(),
				'min': self._interpacketNsOrder.min(),
				'q1': self._interpacketNsOrder.q1(),
				'median': self._interpacketNsOrder.median(),
				'q3': self._interpacketNsOrder.q3(),
				'p95': self._interpacketNsOrder.fractile(0.95),
				'p99': self._interpacketNsOrder.fractile(0.99),
				'p999': self._interpacketNsOrder.fractile(0.999),
				'max': self._interpacketNsOrder.max(),
			},
			'packetRate': {
				'n': self._interpacketNs.n(),
				'average': 1.0e9 / self._interpacketNs.average() if self._interpacketNs.n() > 0 else 999999999.0, #Rather than infinity, because JSON doesn't support it
				'min': self._packetRatesOrder.min(),
				'q1': self._packetRatesOrder.q1(),
				'median': self._packetRatesOrder.median(),
				'q3': self._packetRatesOrder.q3(),
				'p95': self._packetRatesOrder.fractile(0.95),
				'p99': self._packetRatesOrder.fractile(0.99),
				'p999': self._packetRatesOrder.fractile(0.999),
				'max': self._packetRatesOrder.max(),
			},
			'dataRate': {
				'n': self._dataRatesOrder.n(),
				'min': self._dataRatesOrder.min(),
				'q1': self._dataRatesOrder.q1(),
				'median': self._dataRatesOrder.median(),
				'q3': self._dataRatesOrder.q3(),
				'p95': self._dataRatesOrder.fractile(0.95),
				'p99': self._dataRatesOrder.fractile(0.99),
				'p999': self._dataRatesOrder.fractile(0.999),
				'max': self._dataRatesOrder.max(),
			},
		}

		print(json.dumps(output, indent=2, separators=(',', ': '), sort_keys=True))

	def onPcapHeader(self, header):
		pass #Nothing to do

	def onPcapRecord(self, recordHeader, data):
		self._includedLengths.sample(recordHeader.includedLength())
		self._includedLengthsOrder.sample(recordHeader.includedLength())
		self._originalLengths.sample(recordHeader.originalLength())
		self._originalLengthsOrder.sample(recordHeader.originalLength())

		ns = recordHeader.epochNanos()
		self._epochNs.sample(ns)
		self._epochNsOrder.sample(ns)
		if self._lastNs is not None:
			dtNs = ns - self._lastNs
			self._interpacketNs.sample(dtNs)
			self._interpacketNsOrder.sample(dtNs)

			packetRate = 1.0e9 / dtNs if dtNs > 0 else float('inf')
			self._packetRatesOrder.sample(packetRate)

			data_rate = 1.0e9 * self._lastPacketLength / dtNs if dtNs > 0 else float('inf')
			self._dataRatesOrder.sample(data_rate)

		self._lastNs = ns
		self._lastPacketLength = recordHeader.originalLength()

def main():
	parser = argparse.ArgumentParser(description='PCAP Summary Diagnostic')
	parser.add_argument('pcap', help='PCAP file to summarize.')
	parser.add_argument('-H', '--no-header', action='store_true',
		help='Do not show header.')
	parser.add_argument('-j', '--json', action='store_true',
		help='Enable JSON output with one object per line.')
	parser.add_argument('-s', '--strict', action='store_true',
		help='Enables strict validation rules.')
	parser.add_argument('-u', '--use-units', action='store_true',
		help='Use units to make the display friendlier.')
	arguments = parser.parse_args(sys.argv[1:])

	listener = PcapSummaryListener(arguments)
	parseFile(arguments.pcap, listener, strict=arguments.strict)

	if arguments.json:
		listener.printJsonReport()
	else:
		listener.printReport()

	return 0

if __name__ == '__main__':
	sys.exit(main())
