#!/usr/bin/env bash

RED='\033[0;31m'
GREEN='\033[0;32m'
CLEAR='\033[0m' # No Color

if [[ $# -ne 1 ]]
then
    echo "usage: run_test.sh [test#]"
    exit 1
fi

test_dir="test/T23-*$1"
echo -n "Running $(basename ${test_dir})... "
python3 src/main.py ${test_dir}/input.json ${test_dir}/patterns.json
diff -i -E -Z -b -w -B ${test_dir}/output.json ${test_dir}/input.output.json >/dev/null 2>/dev/null
if [[ "$?" -eq "0" ]]
then
    echo -e "${GREEN}OK${CLEAR}"
else
    echo -e "${RED}NOK${CLEAR}"
fi
