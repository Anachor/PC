from circuits.elements import Terminal, NotGate, AndGate, OrGate

class Circuit:
    """
    Represents a boolean circuit. A circuit can have multiple inputs but exactly one output.
    We only keep the output gate/terminal in the circuit. The entire circuit is then recursively defined.

    Example:
    a = Terminal('a')
    b = Terminal('b')
    c = Terminal('c')

    g1 = AndGate(a, b)
    g2 = NotGate(c)
    g3 = OrGate(g1, g2)
    circuit = Circuit([a, b, c], g3)

    This represents ((a & b) | ~c)
    """

    def __init__(self, terminals, output):
        self.terminals = terminals
        self.output = output

    def __str__(self):
        """
        Returns a string representation of the circuit. Example: ((a & ~b) | ~c)
        """
        return str(self.output)
    
    def simplify(self, assignments):
        """
        Simplifies the circuit when some or all of the terminals are assigned boolean values.
        The output is a boolean value or a gate or terminal representing simplified circuit.

        assignments: dict[Terminal -> bool]
        A dictionary where the keys are terminals and the values are boolean values.
        If a terminal is not present in the dictionary, it is not assigned a value.

        Example:
        Suppose we have a circuit with terminals a, b, c and the output is ((a & b) | ~c)

        circuit.simplify({a: True, b: False}) will simplify ((True & False) | c) = (False | ~c) = ~c.
        The output will be a Gate whose output is ~c.

        circuit.simplify({c: False}) will simplify ((a & b) | ~False) = ((a & b) | True) = True.
        The output will be True.

        circuit.simplify({a:True, c:True}) will simplify ((True & b) | ~True) = (b | False) = b.
        The output will be the Terminal b.
        """

        return self.__dfs_simplify(self.output, assignments)

        
    def __dfs_simplify(self, node, assignments):
        """
        Helper function to recursively simplify the circuit.
        """
        if type(node) == Terminal:
            return assignments.get(node, node)
        else:
            simplified_inputs = [self.__dfs_simplify(input, assignments) for input in node.inputs]
            return node.simplify(*simplified_inputs)

    @staticmethod
    def deserialize(description: str):
        """
          Deserializes string to a Circuit object.

          Format:
          - Each line represents a gate or terminal.
              - A terminal is represented in the following format: term identifier
              - A gate is represented in the following format: (gate_type input1 input2 ... inputN identifier)
          - The representation ends with a line in the format: output identifier
              - identifier is the identifier of the output terminal or gate.
              - All subsequent lines are ignored.
          - Empty lines or lines starting with '#' are ignored.

          Example:
              term a
              term b
              and a b g1
              term c
              not c g2
              or g1 g2 g3
              output g3
          """

        mapper = {}
        terminals = []
        output = None

        for line in description.split('\n'):
            if line.startswith('#') or not line:
                continue

            tokens = line.split()
            line_type = tokens[0]

            if line_type == 'term':
                terminal, identifier = Circuit._handle_terminal_line(tokens, mapper)
                terminals.append(terminal)
                mapper[identifier] = terminal
            elif line_type == 'output':
                identifier = Circuit._handle_output_line(tokens, mapper)
                output = mapper[identifier]
                break
            else:
                gate, identifier = Circuit._handle_gate_line(tokens, mapper)
                mapper[identifier] = gate

        if output is None:
            raise ValueError("Output identifier not found")

        return Circuit(terminals, output)

    @staticmethod
    def _handle_output_line(tokens, mapper):
        if len(tokens) != 2:
            raise ValueError("Invalid format for output")
        identifier = tokens[1]
        if identifier not in mapper:
            raise ValueError(f"Output identifier not found: {identifier}")
        return identifier

    @staticmethod
    def _handle_terminal_line(tokens, mapper):
        if len(tokens) != 2:
            raise ValueError("Invalid format for terminal")
        if mapper.get(tokens[1]) is not None:
            raise ValueError(f"Duplicate identifier: {tokens[1]}")
        name = tokens[1]
        terminal = Terminal(name)
        return terminal, name

    @staticmethod
    def _handle_gate_line(tokens, mapper):
        if len(tokens) < 3:
            raise ValueError("Invalid format for gate")

        gate_type = tokens[0]
        inputs = tokens[1:-1]
        identifier = tokens[-1]

        if identifier in mapper:
            raise ValueError(f"Duplicate identifier: {identifier}")

        for input in inputs:
            if input not in mapper:
                raise ValueError(f"Input identifier not found: {input}")

        if gate_type.lower() == 'and':
            if len(inputs) != 2:
                raise ValueError("AND gate requires exactly 2 inputs")
            gate = AndGate(mapper[inputs[0]], mapper[inputs[1]])
        elif gate_type.lower() == 'or':
            if len(inputs) != 2:
                raise ValueError("OR gate requires exactly 2 inputs")
            gate = OrGate(mapper[inputs[0]], mapper[inputs[1]])
        elif gate_type.lower() == 'not':
            if len(inputs) != 1:
                raise ValueError("NOT gate requires exactly 1 input")
            gate = NotGate(mapper[inputs[0]])
        else:
            raise ValueError(f"Unsupported gate type: {gate_type}")

        return gate, identifier

