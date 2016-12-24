
# NanoPcap
NanoPcap is a Python library and set of tools for working with nanosecond
resolution PCAP data. It is designed to be minimal and require no dependencies.

## Tools

### `Dump`
Dumps a PCAP in either short form (1 line per packet) or long form (1 line per
value).

	> NanoPcap/Tools/Dump.py -h
	usage: Dump.py [-h] [-d DATA_BYTES] [-l] [-j] [-o DATA_OFFSET] [-H] [-R] [-s]
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
	  -j, --json            Enable JSON output with either one object per line
	                        (short mode) or one value per line (long mode).
	  -o DATA_OFFSET, --data-offset DATA_OFFSET
	                        Offset of the data to show.
	  -H, --no-header       Do not show the header.
	  -R, --no-records      Do not show records.
	  -s, --strict          Enables strict validation rules.

### `Filter`
Filters a PCAP based on set criteria and optionally does other edits like snapshot
length truncation, packet deduplication, or even fuzzing like random drops and duplication.

	> NanoPcap/Tools/Filter.py -h
	usage: Filter.py [-h] [--strict] [-l SNAPLEN] [-o DATA_OFFSET]
	                 [-x DATA_END_OFFSET] [-H] [-R] [-a]
	                 [--required-link-type REQUIRED_LINK_TYPE]
	                 [--link-type LINK_TYPE]
	                 [--time-shift-seconds TIME_SHIFT_SECONDS] [-s START] [-e END]
	                 [-D DROP_FRACTION] [--duplicate-fraction DUPLICATE_FRACTION]
	                 [--deduplication-window DEDUPLICATION_WINDOW]
	                 input output

	PCAP Filter Tool

	positional arguments:
	  input                 PCAP file to use as input.
	  output                Output file. May include time format strings to roll
	                        the file based on packet time stamps, e.g.
	                        %Y/%m/%d/%H.pcap for hourly output files in daily
	                        folders.

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
	  --required-link-type REQUIRED_LINK_TYPE
	                        The required link type of the file being edited (e.g.
	                        1 for Ethernet, 228 for IPv4, 229 for IPv6).
	  --link-type LINK_TYPE
	                        A value to set the link type in the header to (e.g. 1
	                        for Ethernet, 228 for IPv4, 229 for IPv6).
	  --time-shift-seconds TIME_SHIFT_SECONDS
	                        The amount of time in seconds to shift timestamps in
	                        the output PCAP.
	  -s START, --start START
	                        Start time as either epoch nanoseconds or a datetime
	                        (with only microsecond resolution).
	  -e END, --end END     End time as either epoch nanoseconds or a relative
	                        offset in nanoseconds to the start (e.g. +100 would
	                        yield a 100ns PCAP).
	  -D DROP_FRACTION, --drop-fraction DROP_FRACTION
	                        Fraction of the time to drop packagets (from 0 to 1
	                        inclusive).
	  --duplicate-fraction DUPLICATE_FRACTION
	                        Fraction of the time to duplicate packagets (from 0 to
	                        1 inclusive).
	  --deduplication-window DEDUPLICATION_WINDOW
	                        Sets the number of the packets in the deduplication
	                        window (based on contents).

For example, here is how Ethernet headers (L2) were removed to generate the files in TestData:

	> NanoPcap/Tools/Filter.py --required-link-type 1 --link-type 228 -o 14 -x 4 SSH.pcap TestData/SSH_L3.pcap
	> NanoPcap/Tools/Filter.py --required-link-type 1 --link-type 228 -o 14 -x 4 SSH2.pcap TestData/SSH2_L3.pcap

There is also a convenience script for that transformation:

	> ./strip_ethernet_header.sh SSH.pcap TestData/SSH_L3.pcap

### `Merge`
Merges two PCAP files with potentially interleaved timestamps.

	> NanoPcap/Tools/Merge.py -h
	usage: Merge.py [-h] [--strict] input1 input2 output

	PCAP Filter Tool

	positional arguments:
	  input1      PCAP file to use as input.
	  input2      PCAP file to use as other input.
	  output      Output file

	optional arguments:
	  -h, --help  show this help message and exit
	  --strict    Enables strict validation rules.

### `Split`
Splits a PCAP into slices with a maximum number of packets, bytes, etc.

	> NanoPcap/Tools/Split.py -h
	usage: Split.py [-h] [--gzip-output] [--strict] [-b MAX_BYTES]
	                [-p MAX_PACKETS] [-l SNAPLEN] [-o DATA_OFFSET]
	                [-x DATA_END_OFFSET] [-H] [-a]
	                input output

	PCAP Splitting Tool

	positional arguments:
	  input                 PCAP file to use as input.
	  output                Output path -- output files will be named based on the
	                        identifying attributes.

	optional arguments:
	  -h, --help            show this help message and exit
	  --gzip-output         Enables gzip for the output files.
	  --strict              Enables strict validation rules.
	  -b MAX_BYTES, --max-bytes MAX_BYTES
	                        The maximum number of bytes in a slice.
	  -p MAX_PACKETS, --max-packets MAX_PACKETS
	                        The maximum number of packets in a slice.
	  -l SNAPLEN, --snaplen SNAPLEN
	                        Add a certain number of bytes for each packet record.
	  -o DATA_OFFSET, --data-offset DATA_OFFSET
	                        Offset of the data to include.
	  -x DATA_END_OFFSET, --data-end-offset DATA_END_OFFSET
	                        Offset from the end of the data to include.
	  -H, --no-header       Do not output the header.
	  -a, --append          Append to the file (implies no header).

### `SplitFlows`
Splits a PCAP into multiple PCAP's, one per flow at the top layer protocol.

	> mkdir -p SplitData && NanoPcap/Tools/SplitEthernetFlows.py TestData/SSH_L3.pcap SplitData/ && ls SplitData/
	192.168.1.192_192.168.1.241.pcap

	> NanoPcap/Tools/SplitFlows.py -h
	usage: SplitFlows.py [-h] [--strict] [-l SNAPLEN] [-o DATA_OFFSET]
	                     [-x DATA_END_OFFSET] [-H] [-a] [--link-type LINK_TYPE]
	                     input output

	PCAP Filter Tool

	positional arguments:
	  input                 PCAP file to use as input.
	  output                Output path -- output files will be named based on the
	                        identifying attributes.

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
	  -a, --append          Append to the file (implies no header).
	  --link-type LINK_TYPE
	                        A value to set the link type in the header to (e.g. 1
	                        for Ethernet, 228 for IPv4, 229 for IPv6).

### `Summary`
Summarizes a PCAP. For example:

	> NanoPcap/Tools/Summary.py TestData/SSH_L3.pcap -u
	Epoch times: 1472402096321502000 - 1472402096321652000 (150000ns) (2016-08-28 16:34:56.321501 - 2016-08-28 16:34:56.321651)

	Name                      Count    Total  Average  Std Dev      Min   25th %   50th %   75th %   95th %   99th % 99.9th %      Max
	Included Length              21     8.6K   421.43   502.94       34       34      102      582     1482     1482     1482     1482
	Original Length              21     8.6K   421.43   502.94       34       34      102      582     1482     1482     1482     1482
	Interpacket Time (ns)        20  150.0us    7.5us   20.9us      0.0      0.0    1.0us    1.0us   74.0us   74.0us   74.0us   74.0us
	Packet Rate (pps)            20            133.3K             13.5K     1.0M      inf      inf      inf      inf      inf      inf
	Data Rate (Bps)              20                              448.7K   539.8M      inf      inf      inf      inf      inf      inf

Or without units:

	> NanoPcap/Tools/Summary.py TestData/SSH_L3.pcap
	Epoch times: 1472402096321502000 - 1472402096321652000 (150000ns) (2016-08-28 16:34:56.321501 - 2016-08-28 16:34:56.321651)

	Name                          Count            Total        Average        Std Dev            Min         25th %         50th %         75th %         95th %         99th %       99.9th %            Max
	Included Length                  21           8850.0         421.43         502.94             34             34            102            582           1482           1482           1482           1482
	Original Length                  21           8850.0         421.43         502.94             34             34            102            582           1482           1482           1482           1482
	Interpacket Time (ns)            20         150000.0         7500.0        20884.2            0.0            0.0         1000.0         1000.0        74000.0        74000.0        74000.0        74000.0
	Packet Rate (pps)                20                        133333.3                       13513.5      1000000.0            inf            inf            inf            inf            inf            inf
	Data Rate (Bps)                  20                                                      459459.5    566000000.0            inf            inf            inf            inf            inf            inf
