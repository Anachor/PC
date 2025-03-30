#!/bin/bash

if [ "$#" -l 2 ]; then
    echo "Usage: $0 <port> <testcase_folder> [--verbose]"
    exit 1
fi

if [[ "$*" == *"--verbose"* ]] then
    verbose='--verbose'
else
    verbose=''
fi

PORT=$1
TESTCASE_FOLDER=$2


CIRCUIT_FILE="${TESTCASE_FOLDER}/circuit.txt"
ALICE_FILE="${TESTCASE_FOLDER}/alice.txt"
BOB_FILE="${TESTCASE_FOLDER}/bob.txt"

python bob.py "$PORT" "$CIRCUIT_FILE" "$BOB_FILE" "$verbose" &
python alice.py localhost "$PORT" "$CIRCUIT_FILE" "$ALICE_FILE" "$verbose" &

exit
