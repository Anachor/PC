import functools


@functools.total_ordering
class Terminal:
    """
    Represents an input terminal in a circuit.
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Terminal({self.name})"

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        if isinstance(other, Terminal):
            return self.name == other.name
        return False

    def __lt__(self, other):
        if isinstance(other, Terminal):
            return self.name < other.name
        return NotImplemented

class Gate:
    """
    Represents a gate in a circuit. A gate can have multiple inputs. Each input can be a terminal or another gate.
    """

    def __init__(self, *inputs):
        self.inputs = inputs

    def __str__(self):
        """
        Returns a string representation of the output of the gate. Example: ((a & ~b) | ~c)
        """
        class_name = self.__class__.__name__
        inputs = ', '.join([str(x) for x in self.inputs])

        return f"{class_name}({inputs})"

    def simplify(self, *inputs):
        """
        Simplifies the circuit by recursively evaluating the inputs.
        The output is a boolean value or a gate whose output is the representation of the simplified circuit.
        """

        raise NotImplemented("Subclasses should implement")

    @staticmethod
    def truth_table():
        """
        Returns the truth table of the gate as a list.
        For example, the truth table of an AND gate is [0, 0, 0, 1].
        """
        raise NotImplemented("Subclasses should implement")


class NotGate(Gate):
    def __init__(self, input):
        super().__init__(input)

    def __str__(self):
        return f"~{self.inputs[0]}"

    def simplify(self, input):
        if type(input) == bool:
            return not input
        else:
            return NotGate(input)

    @staticmethod
    def truth_table():
        return [1, 0]


class BufferGate(Gate):
    def __init__(self, input):
        super().__init__(input)

    def __str__(self):
        return f"{self.inputs[0]}"

    def simplify(self, input):
        if type(input) == bool:
            return input
        else:
            return BufferGate(input)

    @staticmethod
    def truth_table():
        return [0, 1]


class AndGate(Gate):
    def __init__(self, input1, input2):
        super().__init__(input1, input2)

    def __str__(self):
        return f"({self.inputs[0]} & {self.inputs[1]})"

    def simplify(self, input1, input2):
        if type(input1) == bool and type(input2) == bool:
            return input1 and input2
        elif type(input1) == bool:
            if not input1:
                return False
            else:
                return input2
        elif type(input2) == bool:
            if not input2:
                return False
            else:
                return input1
        else:
            return AndGate(input1, input2)

    @staticmethod
    def truth_table():
        return [0, 0, 0, 1]


class OrGate(Gate):
    def __init__(self, input1, input2):
        super().__init__(input1, input2)

    def __str__(self):
        return f"({self.inputs[0]} | {self.inputs[1]})"

    def simplify(self, input1, input2):
        if type(input1) == bool and type(input2) == bool:
            return input1 or input2
        elif type(input1) == bool:
            if input1:
                return True
            else:
                return input2
        elif type(input2) == bool:
            if input2:
                return True
            else:
                return input1
        else:
            return OrGate(input1, input2)

    @staticmethod
    def truth_table():
        return [0, 1, 1, 1]