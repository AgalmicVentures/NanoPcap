
from NanoPcap import Format

def parseFile(filename, listener, strict=False):
    """
    Parse a PCAP with the given filename.

    :param filename: str The file to parse
    """
    with open(filename, 'rb') as pcapFile:
        parse(pcapFile, listener, strict=strict)

def parse(pcapFile, listener, strict=False):
    """
    Parse a PCAP from the given file-like object (file, socket, etc.)

    :param pcapFile: file-like object to parse from
    """
    #Read the header first
    headerBytes = pcapFile.read(Format.PCAP_HEADER_STRUCT.size)
    if len(headerBytes) != Format.PCAP_HEADER_STRUCT.size:
        raise ValueError('Could not read comple PCAP header (got only %d bytes)' % len(headerBytes))

    #Unpack the header and check for inverted byte order
    headerValues = Format.PCAP_HEADER_STRUCT.unpack(headerBytes)
    if headerValues[0] in [Format.PCAP_MAGIC_NUMBER_INVERTED, Format.PCAP_NS_MAGIC_NUMBER_INVERTED]:
        headerValues = Format.PCAP_HEADER_STRUCT_INVERTED.unpack(headerBytes)
        recordHeaderStruct = Format.PCAP_RECORD_HEADER_STRUCT_INVERTED
    else:
        recordHeaderStruct = Format.PCAP_RECORD_HEADER_STRUCT

    header = Format.PcapHeader(*headerValues)
    listener.onPcapHeader(header)

    #And now, walk 1 record at a time
    while True:
        recordHeaderBytes = pcapFile.read(recordHeaderStruct.size)
        if len(recordHeaderBytes) == 0:
            break #EOF
        elif len(recordHeaderBytes) != recordHeaderStruct.size:
            raise ValueError('Could not read comple PCAP record header (got only %d bytes)' % len(recordHeaderBytes))

        recordHeader = Format.PcapRecordHeader(
            *recordHeaderStruct.unpack(recordHeaderBytes),
            fileHeader=header, strict=strict)

        data = pcapFile.read(recordHeader.includedLength())
        if len(data) != recordHeader.includedLength():
            raise ValueError('Could not read PCAP record data (expected %d bytes; got %d)' % (
                recordHeader.includedLength(), len(data)))

        listener.onPcapRecord(recordHeader, data)
