import os
from itertools import product

from circuits.circuit import Circuit
from circuits.elements import Terminal, NotGate, AndGate, OrGate
from garbled_circuits.garbled_circuit import GarbledCircuit

a = Terminal("a")
b = Terminal("b")

na = NotGate(a)
nb = NotGate(b)
ab = AndGate(a, b)
nab = AndGate(na, nb)
g1 =  OrGate(ab, nab)

eq = Circuit([a, b], g1)

assignment = {
    a: True,
}

passwords = {
    b: [os.urandom(32), os.urandom(32)],
}

simplified = eq.simplify(assignment)
print(f"Assignment: {assignment} => Simplified = {simplified}")

garbled_circuit = GarbledCircuit(eq, assignment, passwords)
print(f"Garbled circuit: {garbled_circuit}")

remaining_terminals = garbled_circuit.terminals

vals = [True, False]
assigments = {}
for values in product(vals, repeat=len(remaining_terminals)):
    assigment = {t: v for t, v in zip(remaining_terminals, values)}
    simplified = eq.simplify(assigment)

    assigment_str = ", ".join(f"{t}={v}" for t, v in assigment.items())
    print(f"Assignment: {assigment_str} =>  Simplified = {simplified}")




