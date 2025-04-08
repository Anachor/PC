import pickle
import sys
from typing import List
import datetime

from circuits.circuit import Circuit
from circuits.elements import Terminal

def log(message):
    script = sys.argv[0]
    """Timestamp with microseconds"""
    timestamp = datetime.datetime.now().timestamp()
    print(f"{timestamp:.6f} {script} | \t{message}")


def next_line(file):
    """
    Reads the next line from the file, skipping empty lines and comments.
    """
    while True:
        line = file.readline()
        if not line:
            break
        line = line.strip()
        if line and not line.startswith('#'):
            return line

def read_circuit_description(file):
    description = []
    while True:
        line = file.readline()
        if not line:
            raise EOFError("End of file reached while reading circuit description")
        description.append(line)

        if line.startswith('output'):
            break
    return '\n'.join(description)

def load_circuit_from_file(file_path):
    """
    Expects a file with the following format:
        - The file starts with the circuit description.
            - Each line represents a gate or terminal.
              - A terminal is represented in the following format: term identifier
              - A gate is represented in the following format: (gate_type input1 input2 ... inputN identifier)
        - The circuit representation ends with a line in the format: output identifier
              - identifier is the identifier of the output terminal or gate.
        - Then alices terminals are listed in the format: a1, a2, ..., an
        - Then bobs terminals are listed in the format: b1, b2, ..., bm
        - All subsequent lines are ignored.
        - Empty lines or lines starting with '#' are ignored.

        Example:
            term a0
            term a1
            term b0
            term b1
            and a0 a1 g1
            and b0 b1 g2
            or g1 g2 g3
            output g3
            a0, a1
            b0, b1
    """
    with open(file_path, 'r') as f:
        description = read_circuit_description(f)
        circuit = Circuit.deserialize(description)
        terminals = circuit.terminals

        name2terminal = {t.name: t for t in terminals}
        alice_terminals = [name2terminal[name] for name in next_line(f).split(' ')]
        bob_terminals = [name2terminal[name] for name in next_line(f).split(' ')]

        all_terminals = set(alice_terminals + bob_terminals)
        if len(all_terminals) != len(terminals):
            raise ValueError("Each terminal should be assigned to either Alice or Bob")
    return circuit, alice_terminals, bob_terminals

def load_assignment_from_file(file_path, terminals: List[Terminal]):
    """
    Expects a file with the following format:
        - Each line represents a terminal assignment in the format: terminal_name assignment
        - The assignment is either True or False.
        - Empty lines or lines starting with '#' are ignored.
        - only terminals from the list of terminals are allowed.
        Example:
            a0 1
            a1 0
    """
    name2terminal = {t.name: t for t in terminals}
    assignments = {}
    with open(file_path, 'r') as f:
        while line := next_line(f):
            tokens = line.split()
            if len(tokens) != 2:
                raise ValueError("Invalid format for assignment")
            terminal_name, assignment = tokens
            if terminal_name not in name2terminal:
                raise ValueError(f"Terminal {terminal_name} not found in circuit")
            if assignment not in ['0', '1']:
                raise ValueError(f"Invalid assignment: {assignment}")
            if terminal_name in assignments:
                raise ValueError(f"Terminal {terminal_name} already assigned")
            assignments[name2terminal[terminal_name]] = bool(int(assignment))
    return assignments

def read_object(sock, buffer_size=65000, verbose=False):
    data = sock.recv(buffer_size)
    obj = pickle.loads(data)

    if verbose:
        script = sys.argv[0]
        log(f"Received object: {obj}")
    return obj

def send_object(sock, obj, verbose=False):
    if verbose:
        script = sys.argv[0]
        log(f"Sending object: {obj}")
    data = pickle.dumps(obj)
    sock.sendall(data)