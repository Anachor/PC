from __future__ import annotations
import os
from typing import Tuple, List, Dict

from circuits.circuit import Circuit
from circuits.elements import Terminal
from garbled_circuits.garbled_gate import GarbledGate


class GarbledCircuit:
    """
        Represents a garbled circuit.

        Suppose we have a circuit with n+m [a1, ..., an, b1, ..., bm].
        We also a truth value assignment for the terminals: assignment[a1, ..., an].
        And we have two passwords for each of the terminals: password[b1, ..., bm] where password[bi][0]
        is the password for bi = 0 and password[bi][1] is the password for bi = 1.

        We can construct a garbled circuit with the following property:
            Given the truth value assignment t = [t1, ..., tm] for [b1, ..., bm] (ti = 0 or 1), we can evaluate
            the circuit for the assignment if and only if we have [password[b1][t1], ..., password[bm][tm]].

        GarbledCircuit.garble(circuit, assignment, input_passwords) constructs the garbled circuit.
        garbled_circuit.evaluate(passwords) evaluates the garbled circuit with the given passwords.

        passwords for the terminals should be generated using the GarbledCircuit.random_password() function.
    """
    def __init__(self, terminals: List[Terminal], output: GarbledGate):
        self.terminals = terminals
        self.output = output

    @staticmethod
    def garble(circuit: Circuit,
            assignments: Dict[Terminal, bool],
            input_passwords: Dict[Terminal, List[bytes]]
        ) -> GarbledCircuit:
        """
        Contruct the garbled circuit with a circuit object and partial assignments.
        assignments is a dictionary of terminal -> boolean value.
        input_passwords is a dictionary of terminal -> list of two passwords.
        """

        terminals = list(set(circuit.terminals) - set(assignments.keys()))
        output = GarbledCircuit._dfs_construct(circuit.output, input_passwords, assignments, is_root=True)[0]
        return GarbledCircuit(terminals, output)

    @staticmethod
    def random_password() -> bytes:
        """
        Generate a random password. This function should be used to generate the passwords for the terminals.
        """
        return os.urandom(32)

    @staticmethod
    def _dfs_construct(node, input_passwords, assignments, is_root=False) -> Tuple[GarbledGate | Terminal, List[bytes] | None] :
        """
        Helper function to recursively construct the garbled circuit.
        Returns a garbled gate or terminal and the passwords for the outputs.
        No passwords are returned for the root node as we directly output the value
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
                garbled_gate, password = GarbledCircuit._dfs_construct(input, input_passwords, assignments)
                inputs.append(garbled_gate)
                passwords.append(password)

            output_passwords = [GarbledCircuit.random_password(), GarbledCircuit.random_password()] if not is_root else None
            garbled_gate = GarbledGate.garble(node, inputs, passwords, output_passwords)
            return garbled_gate, output_passwords


    def evaluate(self, passwords) -> bool:
        """
        Evaluate the garbled circuit with the given passwords.
        assignments is a dictionary of terminal -> password.
        """

        return self._dfs_evaluate(self.output, passwords)

    def _dfs_evaluate(self, node: GarbledGate | Terminal, passwords) -> bytes | bool:
        """
        Helper to recursively evaluate the garbled circuit.
        Returns a password or boolean value.
        """
        if type(node) == Terminal:
            if node not in passwords:
                raise ValueError(f"Terminal {node} not found in passwords")
            return passwords[node]
        else:
            input_passwords = [self._dfs_evaluate(input, passwords) for input in node.inputs]
            return node.evaluate(input_passwords)
