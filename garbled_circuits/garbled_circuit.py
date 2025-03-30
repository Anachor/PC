import os
from typing import Tuple, List

from circuits.elements import Terminal
from garbled_circuits.garbled_gate import GarbledGate


class GarbledCircuit:
    def __init__(self, circuit, assignments, input_passwords):
        """
        Contruct the garbled circuit with a circuit object and partial assignments.
        assignments is a dictionary of terminal -> boolean value.
        input_passwords is a dictionary of terminal -> list of two passwords.
        """

        reduced_circuit = circuit.simplify(assignments)
        self.terminals = list(set(circuit.terminals) - set(assignments.keys()))
        self.output = self._dfs_construct(reduced_circuit, input_passwords, assignments)[0]

    @staticmethod
    def _random_password() -> bytes:
        """
        Generate a random password.
        """
        return os.urandom(8)

    def _dfs_construct(self, node, input_passwords, assignments) -> Tuple[GarbledGate | Terminal | bool, List[bytes] | None] :
        """
        Helper function to recursively construct the garbled circuit.
        Returns a garbled gate or terminal and the passwords for the outputs.
        """
        if type(node) == Terminal:
            if node in input_passwords:
                return node, input_passwords[node]
            elif node in assignments:
                val = assignments[node]
                return val, None
            else:
                raise ValueError(f"Terminal {node} not found in input_passwords or assignments")
        else:
            passwords = []
            inputs = []
            for input in node.inputs:
                garbled_gate, password = self._dfs_construct(input, input_passwords)
                inputs.append(garbled_gate)
                passwords.append(password)

            output_passwords = [self._random_password(), self._random_password()]
            garbled_gate = GarbledGate.construct_from_gate(node, inputs, passwords, output_passwords)
            return garbled_gate, output_passwords


    def evaluate(self, assignments) -> bool:
        """
        Evaluate the garbled circuit with the given passwords.
        assignments is a dictionary of terminal -> password.
        """

        return self._dfs_evaluate(self.output, assignments)

    def _dfs_evaluate(self, node: GarbledGate | Terminal, assignments) -> List[bytes] | bool:
        """
        Helper to recursively evaluate the garbled circuit.
        Returns a password or boolean value.
        """
        if type(node) == Terminal:
            if node not in assignments:
                raise ValueError(f"Missing password for terminal {node}")
            return assignments[node]
        else:
            input_passwords = [self._dfs_evaluate(input, assignments) for input in node.inputs]
            return node.evaluate(*input_passwords)
