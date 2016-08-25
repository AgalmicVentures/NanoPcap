
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

### `PcapSummary`
Summarizes a PCAP.

	> NanoPcap/Tools/PcapSummary.py -h
	usage: PcapSummary.py [-h] [-H] [-s] [-u] pcap

	PCAP Summary Diagnostic

	positional arguments:
	  pcap             PCAP file to summarize.

	optional arguments:
	  -h, --help       show this help message and exit
	  -H, --no-header  Do not show header.
	  -s, --strict     Enables strict validation rules.
	  -u, --use-units  Use units to make the display friendlier.
