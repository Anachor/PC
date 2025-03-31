import sys
import socket

from common import read_object, send_object, load_circuit_from_file, load_assignment_from_file
from oblivious_transfer.oblivious_transfer import ObliviousTransfer

script_name = sys.argv[0]

def get_connection(self_port):
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    params = ("localhost", self_port)
    server.bind(params)
    server.listen(1)
    print(f"{script_name} | Listening on port {self_port}")
    client, addr = server.accept()
    print(f"{script_name} | Connection from {addr}")
    return client

def handle_args():
    if len(sys.argv) < 4:
        print("Usage: python bob.py <bob_port> <circuit_file> <bob_assignment_file> [--verbose]")
        sys.exit(1)

    bob_port = int(sys.argv[1])
    circuit_file = sys.argv[2]
    bobs_assignment_file = sys.argv[3]
    verbose = '--verbose' in sys.argv
    return bob_port, circuit_file, bobs_assignment_file, verbose


def bob2alice(circuit, bob_assignment):
    ot = ObliviousTransfer(2)
    k = len(bob_assignment)

    keys = []
    sks = []
    for t, v in sorted(bob_assignment.items()):
        b, sk = ot.bob_ot1(v)
        keys.append(b)
        sks.append(sk)

    return keys, sks

def recover_passwords(ciphertexts, sks, bob_assignment, verbose=False):
    if len(keys) != len(bob_assignment) or len(ciphertexts) != len(bob_assignment):
        raise ValueError("Incorrect number of passwords")

    ot = ObliviousTransfer(2)
    input_passwords = {}
    for i, (terminal, assignment) in enumerate(sorted(bob_assignment.items())):
        c = int(assignment)
        passwords = ciphertexts[i]
        sk = sks[i]
        password = ot.bob_ot2(c, sk, passwords)
        input_passwords[terminal] = password

    if verbose:
        print(f"{script_name} | Recovered passwords: {input_passwords}")

    return input_passwords


if __name__ == '__main__':
    bob_port, circuit_file, bob_assignment_file, verbose = handle_args()
    connection = get_connection(bob_port)

    circuit, alice_terminals, bob_terminals = load_circuit_from_file(circuit_file)
    bob_assignment = load_assignment_from_file(bob_assignment_file, bob_terminals)


    # Round 1: Bob -> Alice
    keys, sks = bob2alice(circuit, bob_assignment)
    send_object(connection, keys, verbose=verbose)

    #Round 2: Alice -> Bob
    ciphertexts, garbled_circuit = read_object(connection, verbose=verbose)
    bob_passwords = recover_passwords(ciphertexts, sks, bob_assignment, verbose=verbose)
    value = garbled_circuit.evaluate(bob_passwords)

    print(f"{script_name} | Output: {value}")






