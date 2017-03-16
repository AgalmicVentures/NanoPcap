#!/bin/bash

set -u

if [[ $# -lt 2 ]]
then
	echo 'Usage: ./strip_ethernet_header.sh <INPUT> <OUTPUT>'
	exit 2
fi

set -e
set -x

#Strip an Ethernet header
NanoPcap/Tools/Filter.py --required-link-type 1 --link-type 228 -o 14 -x 4 $1 $2
