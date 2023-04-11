#!/usr/bin/env bash

# Force test to have a given output

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CLEAR='\033[0m' # No Color

if [[ $# -ne 1 ]]
then
    echo "usage: set_test.sh [test#]"
    exit 1
fi

test_dir=$(printf "test/T23-%02d" "$1")
echo -n "Running $(basename "${test_dir}")... "
python3 src/main.py "${test_dir}/input.json" "${test_dir}/patterns.json"

test_output="${test_dir}/output.json"
echo -e "${YELLOW}--------- old value ---------------${RED}"
cat "$test_output" 1>&2
echo -e "\n${YELLOW}-----------------------------------"
echo -e "--------- new value ---------------${GREEN}"
mv "${test_dir}/input.output.json" "$test_output"
cat "$test_output" 1>&2
echo -e "\n${YELLOW}-----------------------------------${CLEAR}"

