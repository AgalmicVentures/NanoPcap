#!/bin/bash

set -u

MODULE_PATH=`pwd` #Often this is the correct path

rm -r docs/
mkdir -p docs

cp sphinx/* docs/

sphinx-apidoc -o docs/ $MODULE_PATH

cd docs/
make html
