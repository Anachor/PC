"""
Stresstesting script for the garbled circuit protocol.
For each possible assignment of the inputs, the script will calculate the output of the circuit using two methods:
   1. Direct evaluation of the circuit
   2. Garbled circuit protocol using alice.py and bob.py
If the outputs differ, it will print the assignment and the outputs and exit.

Usage:
    python stresstester.py <testcase_folder> <port> [iterations]

<testcase_folder> contains the circuit file as circuit.txt.
<port> is the port number to use for the garbled circuit protocol.
if iterations is provided, it will only generate that many random assignments and check them.
Otherwise, it will check all possible assignments.
"""

import os, tqdm
import shutil
import sys
from itertools import product
import random
from timeit import default_timer as timer
from common import load_circuit_from_file

def handle_args():
    if len(sys.argv) < 3:
        print("Usage: python stresstester.py <testcase_folder> <port> [iterations]")
        exit(1)

    testcase_folder = sys.argv[1]
    port = int(sys.argv[2])
    iterations = int(sys.argv[3]) if len(sys.argv) > 3 else None

    return testcase_folder, port, iterations

def setup_temp_folder(testcase_folder):
    temp_folder = "./temp/"
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    circuit_file = os.path.join(testcase_folder, "circuit.txt")
    new_destination = os.path.join(temp_folder, "circuit.txt")
    shutil.copyfile(circuit_file, new_destination)

    return temp_folder


testcase_folder, port, iterations = handle_args()
temp_folder = setup_temp_folder(testcase_folder)
circuit_file = os.path.join(temp_folder, "circuit.txt")
alice_file = os.path.join(temp_folder, "alice.txt")
bob_file = os.path.join(temp_folder, "bob.txt")
circuit, alice_terminals, bob_terminals = load_circuit_from_file(circuit_file)


def brute(assignment):
    simplified = circuit.simplify(assignment)
    if not simplified in [True, False]:
        raise ValueError(f"Simplified circuit {simplified} is not a boolean value")
    return simplified

def setup_files(assignment):
    with open(alice_file, 'w') as alice, open(bob_file, 'w') as bob:
        for terminal, value in assignment.items():
            if terminal in alice_terminals:
                alice.write(f"{terminal.name} {int(value)}\n")
            elif terminal in bob_terminals:
                bob.write(f"{terminal.name} {int(value)}\n")
            else:
                raise ValueError(f"Terminal {terminal} not found in circuit")

def protocol(assignment):
    setup_files(assignment)
    os.system(f"python alice.py localhost {port} {circuit_file} {alice_file} > alice.temp &")
    os.system(f"python bob.py {port} {circuit_file} {bob_file} > bob.temp")

    with open("bob.temp", 'r') as f:
        lines = f.readlines()
        all_tokens = [token for line in lines for token in line.split()]
        last_token = all_tokens[-1]

        if last_token.lower() not in ['true', 'false']:
            raise ValueError(f"Invalid output from Bob: {last_token}")
    return last_token.lower() == 'true'


def check(actual, calculated):
    if actual != calculated:
        print("Found a mismatch!")
        print(f"Actual: {actual}")
        print(f"Calculated: {calculated}")

        print("Alice assignment")
        with open("alice.py", 'r') as f:
            print(f.read())

        print("Bob assignment")
        with open("bob.py", 'r') as f:
            print(f.read())
        exit(0)



all_terminals = set(alice_terminals + bob_terminals)
values = [False, True]

start = timer()

assignments = list(product(values, repeat=len(all_terminals)))
if iterations is not None:
    random.shuffle(assignments)
    assignments = assignments[:iterations]

for assignments in tqdm.tqdm(assignments):
    assignments = {t: v for t, v in zip(all_terminals, assignments)}
    actual = brute(assignments)
    calculated = protocol(assignments)
    check(actual, calculated)

end = timer()
elapsed_time = end - start
average_time = elapsed_time / len(assignments)

print(f"All assignments passed in {elapsed_time:.2f} seconds")
print(f"Average time per assignment: {average_time:.2f} seconds")


