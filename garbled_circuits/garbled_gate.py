from __future__ import annotations

import secrets
import string
from typing import Self, List, Dict, Tuple
from Crypto.Hash import SHA256
from circuits.elements import Gate, Terminal
from Crypto.Cipher import Salsa20

class GarbledGate:
    """
    Represents a garbled gate in a garbled circuit. Has multiple inputs and one output.
    inputs is a list of input garbled gates/terminals
    truth_table is a dictionary mapping the input passwords to the output passwords.
    """

    def __init__(self, inputs: List[Self | Terminal], truth_table: Dict[bytes, Tuple[bytes, bytes]]):
        self.inputs = inputs
        self.truth_table = truth_table
        self.identifier = ''.join(secrets.choice(string.ascii_lowercase) for _ in range(8))

    @staticmethod
    def garble(gate: Gate, inputs: List[GarbledGate | Terminal | bool],
               pin: List[List[bytes]], pout: List[bytes] | None) -> GarbledGate:
        """
        Construct a garbled gate given the input and output passwords and the underlying gate + inputs.

        - gate is the underlying gate
        - inputs is a list of garbled gates/terminals/bool
        - Each element in pin is a list of two passwords
            - pin[i] is a list of two passwords for the ith input, one for 0 and one for 1
            - If the ith input is a boolean, we do not need the passwords for it., pin[i] is ignored (should be None)
        - pout is a list of two passwords for the output, one for 0 and one for 1
            -if pout is None, then True/False is used as the output
        """


        truth_table = gate.truth_table()
        assignments = [ inputs[i] if type(inputs[i]) == bool else None for i in range(len(inputs))]
        reduced_truth_table = GarbledGate.reduce_truth_table(truth_table, assignments)

        reduced_inputs = [inputs[i] for i in range(len(inputs)) if type(inputs[i]) != bool]
        reduces_idxs = [ i for i in range(len(inputs)) if type(inputs[i]) != bool]
        garbled_truth_table = {}

        k = len(reduced_inputs)
        for mask in range(1 << k):
            key = b''.join(pin[reduces_idxs[i]][mask >> i & 1] for i in range(k))
            hashed_key = SHA256.new(data=key).digest()

            val = reduced_truth_table[mask] if pout is None else pout[reduced_truth_table[mask]]
            val = GarbledGate._to_bytes(val)

            encryption_key = GarbledGate._wrap(hashed_key, 32)
            cipher = Salsa20.new(encryption_key)
            ct = cipher.encrypt(val)
            nonce = cipher.nonce
            garbled_truth_table[hashed_key] = (ct, nonce)

        garbled_gate = GarbledGate(reduced_inputs, garbled_truth_table)
        return garbled_gate



    def evaluate(self, pin:List[bytes]) -> bytes|bool:
        """
        Evaluate the garbled gate given the passwords for each input.
        pin is a list of passwords for each input.
        """

        key = b''.join(pin[i] for i in range(len(pin)))
        key = SHA256.new(data=key).digest()

        if key not in self.truth_table:
            raise ValueError("Invalid passwords")

        ct, nonce = self.truth_table[key]
        encryption_key = self._wrap(key, 32)
        cipher = Salsa20.new(encryption_key, nonce=nonce)
        val = cipher.decrypt(ct)
        return self.from_bytes(val)


    @staticmethod
    def _wrap(b: bytes, n: int) -> bytes:
        """
        Shorten a byte array to n bytes
        """
        ans = bytearray(n)
        for i in range(n):
            ans[i] ^= b[i]
        return ans

    @staticmethod
    def _to_bytes(val: bool | bytes) -> bytes:
        """
        Gate output is either a boolean value or a byte array.
        If it is a boolean value, convert it to a byte array of length `.
        Otherwise, return the byte array.
        """
        return val if type(val) == bytes else bytes([val])

    @staticmethod
    def from_bytes(val: bytes) -> bool | bytes:
        """
        Convert byte array to boolean value or bytes
        if the byte array is of length 1, convert it to a boolean value.
        Otherwise, return the byte array.
        """
        return bool(val[0]) if len(val) == 1 else val

    @staticmethod
    def reduce_truth_table(truth_table: List[bool], assignments: List[bool | None]) -> List[bool]:
        """
        Reduce the truth table given the assignments.
        assignments is a list of boolean values or None.
        If an assignment is None, it is not assigned a value.

        Example: Consider the Or gate truth table:
        [0, 1, 1, 1]

        If the assignments are [True, None], then the truth table is reduced to [1, 1].
        If the assignments are [None, False], then the truth table is  reduced to [0, 1].
        """

        n = len(assignments)
        if len(truth_table) != 1 << n:
            raise ValueError("Invalid truth table length")

        free_vars = [i for i in range(n) if assignments[i] is None]
        set_bits = sum(1 << i for i in range(n) if assignments[i] is True)

        k = len(free_vars)
        reduced_truth_table = [False] * (1 << k)

        for mask in range(1 << k):
            full_mask = sum(1<<free_vars[i] for i in range(k) if mask & (1 << i)) | set_bits
            reduced_truth_table[mask] = truth_table[full_mask]

        return reduced_truth_table



