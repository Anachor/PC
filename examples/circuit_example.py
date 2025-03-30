from itertools import product

from circuits.circuit import Circuit
from circuits.elements import Terminal, NotGate, AndGate, OrGate


### Define circuits programmatically
a = Terminal("a")
b = Terminal("b")
c = Terminal("c")
g1 = AndGate(a, b)
g2 = NotGate(c)
g3 = OrGate(g1, g2)

c1 = Circuit([a, b, c], g3)
print(f"circuit: {c1}")

simplified = c1.simplify({a: True, b: False})
print(f"Assignment: a=True, b=False => Simplified = {simplified}")
simplified = c1.simplify({c: False})
print(f"Assignment: c=False => Simplified = {simplified}")

simplified = c1.simplify({a: True, c: True})
print(f"Assignment: a=True, c=True => Simplified = {simplified}")
print()



### Read a circuit from a file
with open("equality_circuit.txt", "r") as f:
    description = f.read()
    eq_circuit = Circuit.deserialize(description)
    terminals = eq_circuit.terminals

    print(f"Circuit: {eq_circuit}")

    vals = [None, True, False]
    assigments = {}
    for values in product(vals, repeat=len(terminals)):
        assigment = {t: v for t, v in zip(terminals, values) if v is not None}
        simplified = eq_circuit.simplify(assigment)

        assigment_str = ", ".join(f"{t}={v}" for t, v in assigment.items())
        print(f"Assignment: {assigment_str} =>  Simplified = {simplified}")

