#!/usr/bin/env bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CLEAR='\033[0m' # No Color

if [[ $# -ne 1 ]]
then
    echo "usage: run_test.sh [test#]"
    exit 1
fi

test_dir=$(printf "test/T23-%02d" "$1")
echo -n "Running $(basename "${test_dir}")... "
python3 src/main.py "${test_dir}/input.json" "${test_dir}/patterns.json"

if python3 src/cmp_output.py "${test_dir}/output.json" "${test_dir}/input.output.json" >/dev/null 2>/dev/null
then
    echo -e "${GREEN}OK${CLEAR}"
else
    echo -e "${RED}NOK"
    echo -e "${YELLOW}-----------------------------------"
    python3 src/cmp_output.py "${test_dir}/output.json" "${test_dir}/input.output.json" 1>&2
    echo -e "-----------------------------------${CLEAR}"
    echo -e "${YELLOW}-----------------------------------"
    echo -e "generated output\n"
    cat "${test_dir}/input.output.json" 1>&2
    echo -e "\n-----------------------------------${CLEAR}"
fi
