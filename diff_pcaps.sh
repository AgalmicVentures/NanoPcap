#!/bin/bash

if [[ $# -lt 2 ]]
then
	echo 'Usage: ./diff_pcaps.sh <INPUT1> <INPUT2>'
	exit 2
fi

set -e
set -x

diff <(NanoPcap/Tools/Dump.py $1) <(NanoPcap/Tools/Dump.py $2)
