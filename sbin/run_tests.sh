#!/usr/bin/env bash

total_tests=0
passed_tests=0

RED='\033[0;31m'
GREEN='\033[0;32m'
CLEAR='\033[0m' # No Color

for test_dir in $(ls -d test/T23-*)
do
    total_tests=$(echo "${total_tests} + 1" | bc)
    echo -n "Running $(basename "${test_dir}")... "
    python3 src/main.py "${test_dir}/input.json" "${test_dir}/patterns.json"
    if python3 src/cmp_output.py "${test_dir}/output.json" "${test_dir}/input.output.json" >/dev/null 2>/dev/null
    then
        passed_tests=$(echo "${passed_tests} + 1" | bc)
        echo -e "${GREEN}OK${CLEAR}"
    else
        echo -e "${RED}NOK${CLEAR}"
    fi
done

echo -e "\nFinal results: ${passed_tests}/${total_tests} ($( echo " (100. * ${passed_tests}) / ${total_tests}" | bc) %)"
