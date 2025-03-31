import sys
import time
from socket import socket

from common import load_circuit_from_file, send_object, read_object, load_assignment_from_file
from garbled_circuits.garbled_circuit import GarbledCircuit
from oblivious_transfer.oblivious_transfer import ObliviousTransfer

script_name = sys.argv[0]

def get_connection(host, port, max_retries=20, retry_delay=5):
    client = socket()
    for _ in range(max_retries):
        try:
            client.connect((host, port))
            print(f"{script_name} | Connected to {host}:{port}")
            return client
        except ConnectionRefusedError:
            print(f"{script_name} | Connection refused. Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)

    raise ConnectionError(f"Failed to connect to {host}:{port}")

def handle_args():
    if len(sys.argv) < 5:
        print("Usage: python alice.py <bob_host> <bob_port> <circuit_file> <assignment_file> [--verbose]")

    bob_host = sys.argv[1]
    bob_port = int(sys.argv[2])
    circuit_file = sys.argv[3]
    assignment_file = sys.argv[4]
    verbose = '--verbose' in sys.argv

    return bob_host, bob_port, circuit_file, assignment_file, verbose

def generate_passwords(terminals):
    passwords = {
        t: [GarbledCircuit.random_password(), GarbledCircuit.random_password()]
        for t in terminals
    }

    return passwords

def alice2bob(circuit, alice_assignment, keys, bob_terminals, verbose=False):
    if len(keys) != len(bob_terminals):
        raise ValueError("Bob asked for incorrect number of passwords")

    passwords = generate_passwords(bob_terminals)
    garbled_circuit = GarbledCircuit.garble(circuit, alice_assignment, passwords)

    if verbose:
        print(f"{script_name} | Passwords: {passwords}")

    ot = ObliviousTransfer(2)
    ciphertexts = [ot.alice_ot1(passwords[t], keys[i]) for i, t in enumerate(sorted(bob_terminals))]
    message = (ciphertexts, garbled_circuit)
    return message




if __name__ == '__main__':
    bob_host, bob_port, circuit_file, alice_assignment_file, verbose = handle_args()
    connection = get_connection(bob_host, bob_port)

    circuit, alice_terminals, bob_terminals = load_circuit_from_file(circuit_file)
    alice_assignment = load_assignment_from_file(alice_assignment_file, alice_terminals)


    # Round 1: Bob -> Alice
    keys = read_object(connection, verbose=verbose)

    # Round 2: Alice -> Bob
    message = alice2bob(circuit, alice_assignment, keys, bob_terminals, verbose=verbose)
    send_object(connection, message, verbose=verbose)

