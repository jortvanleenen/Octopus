class BitVector:
    def __init__(self, bits: str):
        if not all(c in "01" for c in bits):
            raise ValueError("BitVector must contain only '0' and '1'")
        self._bits: str = bits

    def __str__(self):
        return self._bits

    def __repr__(self):
        return f"BitVector('{self._bits}')"

    def __len__(self):
        return len(self._bits)

    def __getitem__(self, index):
        return self._bits[index]

    def __eq__(self, other):
        if isinstance(other, BitVector):
            return self._bits == other._bits
        return False

    def __add__(self, other):
        if isinstance(other, BitVector):
            return BitVector(self._bits + other._bits)
        raise TypeError("Can only concatenate BitVector to BitVector")

    def __hash__(self):
        return hash(self._bits)

    def __contains__(self, item):
        return item in self._bits

    def __iter__(self):
        return iter(self._bits)

    def __reversed__(self):
        return reversed(self._bits)

    @property
    def bits(self):
        return self._bits

    @property
    def int_value(self):
        return int(self._bits, 2)
