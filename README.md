
# NanoPcap
NanoPcap is a Python library and set of tools for working with nanosecond
resolution PCAP data. It is designed to be minimal and require no dependencies.

## Tools

### `PcapDump`
Dumps a PCAP in either short form (1 line per packet) or long form (1 line per
value).

	> NanoPcap/Tools/PcapDump.py -h
	usage: PcapDump.py [-h] [-d DATA_BYTES] [-l] [-o DATA_OFFSET] [-H] [-R] [-s]
	                   pcap

	PCAP Dump Diagnostic

	positional arguments:
	  pcap                  PCAP file to dump.

	optional arguments:
	  -h, --help            show this help message and exit
	  -d DATA_BYTES, --data-bytes DATA_BYTES
	                        Show a certain number of bytes as hex for each packet
	                        record.
	  -l, --long            Enable long form which generally puts one value per
	                        line for easy diffing.
	  -o DATA_OFFSET, --data-offset DATA_OFFSET
	                        Offset of the data to show.
	  -H, --no-header       Do not show the header.
	  -R, --no-records      Do not show records.
	  -s, --strict          Enables strict validation rules.

### `PcapFilter`
Filters a PCAP based on set criteria and optionally does other edits like snapshot
length truncation.

	> NanoPcap/Tools/PcapFilter.py -h
	usage: PcapFilter.py [-h] [--strict] [-l SNAPLEN] [-o DATA_OFFSET]
	                     [-x DATA_END_OFFSET] [-H] [-R] [-a]
	                     [--link-type LINK_TYPE] [-s START] [-e END]
	                     [-D DROP_FRACTION]
	                     input output

	PCAP Filter Tool

	positional arguments:
	  input                 PCAP file to use as input.
	  output                Output file

	optional arguments:
	  -h, --help            show this help message and exit
	  --strict              Enables strict validation rules.
	  -l SNAPLEN, --snaplen SNAPLEN
	                        Add a certain number of bytes for each packet record.
	  -o DATA_OFFSET, --data-offset DATA_OFFSET
	                        Offset of the data to include.
	  -x DATA_END_OFFSET, --data-end-offset DATA_END_OFFSET
	                        Offset from the end of the data to include.
	  -H, --no-header       Do not output the header.
	  -R, --no-records      Do not output records.
	  -a, --append          Append to the file (implies no header).
	  --link-type LINK_TYPE
	                        A value to set the link type in the header to (e.g. 1
	                        for Ethernet, 228 for IPv4, 229 for IPv6).
	  -s START, --start START
	                        Start time as either epoch nanoseconds or a datetime
	                        (with only microsecond resolution).
	  -e END, --end END     End time as either epoch nanoseconds or a relative
	                        offset in nanoseconds to the start (e.g. +100 would
	                        yield a 100ns PCAP).
	  -D DROP_FRACTION, --drop-fraction DROP_FRACTION
	                        Fraction of the time to drop packagets (from 0 to 1
	                        inclusive).

For example, here is how Ethernet headers (L2) were removed to generate the files in TestData:

	> NanoPcap/Tools/PcapFilter.py SSH.pcap TestData/SSH_L3.pcap -o 14 -x 4 --link-type 228
	> NanoPcap/Tools/PcapFilter.py SSH2.pcap TestData/SSH2_L3.pcap -o 14 -x 4 --link-type 228

### `PcapSummary`
Summarizes a PCAP. For example:

	> NanoPcap/Tools/PcapSummary.py TestData/SSH_L3.pcap
	Epoch times: 1472402096321502000 - 1472402096321652000 (150000ns) (2016-08-28 16:34:56.321501 - 2016-08-28 16:34:56.321651)

	Name                          Count            Total        Average        Std Dev            Min         25th %         50th %         75th %         95th %         99th %       99.9th %            Max
	Included Length                  21           8850.0         421.43         502.94             34             34            102            582           1482           1482           1482           1482
	Original Length                  21           8850.0         421.43         502.94             34             34            102            582           1482           1482           1482           1482
	Interpacket Time (ns)            20         150000.0         7500.0        20884.2            0.0            0.0         1000.0         1000.0        74000.0        74000.0        74000.0        74000.0
	Packet Rate (pps)                20                        133333.3                       13513.5      1000000.0            inf            inf            inf            inf            inf            inf
	Data Rate (Bps)                  20                                                      459459.5    566000000.0            inf            inf            inf            inf            inf            inf

Or with units:

	Epoch times: 1472402228930675000 - 1472402228930905000 (230000ns) (2016-08-28 16:37:08.930675 - 2016-08-28 16:37:08.930905)

	Name                          Count            Total        Average        Std Dev            Min         25th %         50th %         75th %         95th %         99th %       99.9th %            Max
	Included Length                  20             6.8K         348.80         491.01             34             34            118            550           1482           1482           1482           1482
	Original Length                  20             6.8K         348.80         491.01             34             34            118            550           1482           1482           1482           1482
	Interpacket Time (ns)            19          230.0us         12.1us         20.4us            0.0            0.0          1.0us         21.0us         68.0us         68.0us         68.0us         68.0us
	Packet Rate (pps)                19                           82.6K                         14.7K          47.6K           1.0M            inf            inf            inf            inf            inf
	Data Rate (Bps)                  19                                                        488.3K          13.2M         506.4M            inf            inf            inf            inf            inf
