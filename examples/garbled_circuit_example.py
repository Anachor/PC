from itertools import product
from circuits.circuit import Circuit
from circuits.elements import Terminal, NotGate, OrGate, AndGate
from garbled_circuits.garbled_circuit import GarbledCircuit

### a < b  ---->     (~a1 & b1) | (  ((a1 & b1) | (~a1 & ~b1)) & (~a0 & b0) )

a0 = Terminal("a0")
a1 = Terminal("a1")
b0 = Terminal("b0")
b1 = Terminal("b1")

na0 = NotGate(a0)
na1 = NotGate(a1)
nb1 = NotGate(b1)
nb0 = NotGate(b0)

l1 = AndGate(na1, b1)
l0 = OrGate(na0, b0)

eq1 = OrGate(AndGate(a1, b1), AndGate(na1, nb1))
eq = OrGate(l1, AndGate(eq1, l0))

circuit = Circuit([a0, a1, b0, b1], eq)

alice_assignment = {
    a1: False,
    a0: True
}

alice_passwords = {
    b0: [GarbledCircuit.random_password(), GarbledCircuit.random_password()],
    b1: [GarbledCircuit.random_password(), GarbledCircuit.random_password()],
}


garbled_circuit = GarbledCircuit.garble(circuit, alice_assignment, alice_passwords)
remaining_terminals = garbled_circuit.terminals

vals = [False, True]
for values in product(vals, repeat=len(remaining_terminals)):
    bob_assignment = {t: v for t, v in zip(remaining_terminals, values)}
    all_assignment = {**alice_assignment, **bob_assignment}
    simplified = circuit.simplify(all_assignment)

    assigment_str = ", ".join(f"{t}={v}" for t, v in bob_assignment.items())
    print(f"Assignment: {assigment_str} => {simplified}")

    # Evaluate the garbled circuit
    bob_passwords = {t: alice_passwords[t][bob_assignment[t]] for t in remaining_terminals}
    val = garbled_circuit.evaluate(bob_passwords)
    print(f"Garbled circuit evaluation: {val}\n")
    
    if simplified != val:
        print(f"Error: Simplified circuit {simplified} does not match garbled circuit evaluation {val}")