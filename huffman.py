from dataclasses import dataclass, field
from numpy import ndarray, isclose, uint8
from collections.abc import Sequence
from utils import fp_gt, int2bytearray
from functools import reduce

# @dataclass is just syntax sugar that avoids manual __init__ definitions
# @property is useful for getters and avoids the whole `class.prop()` business with trailing parens


@dataclass
class _Entry:
    _symbol: uint8
    _probability: float

    @property
    def symbol(self) -> uint8:
        return self._symbol

    @property
    def probability(self) -> float:
        return self._probability

    # bit-stack assigned to x; to have symbols pushed on top before reading it out upon giving the code
    # Put in __post_init__ to avoid having it as dataclass constructor argument
    def __post_init__(self):
        self._reverse_order_codeword_symbols: bytearray = bytearray()

    # Used when moving forward in Huffman; add a bit
    # NOTE: add_bit should be called something else if not binary
    def add_bit(self, addl_bit: int):
        assert addl_bit < 2, f"Attempted to add {addl_bit} >= 2 as a bit"
        self._reverse_order_codeword_symbols.append(addl_bit)

    # When done, go backwards and read bits to produce Huffman code
    @property
    def codeword(self) -> int:
        assert len(self._reverse_order_codeword_symbols) > 0
        # `a << 1 | b` shifts a left and puts b in; requires a=1 initially to avoid collapse
        return reduce(
            lambda a, b: (a << 1) | b,
            reversed(self._reverse_order_codeword_symbols + bytearray([1])),
        )
        # Will be addressed in `.get_final_code()` in HuffmanLayer


@dataclass
class _Aggregator:
    _entries: list[_Entry] = field(default_factory=list)
    # _probability: float = 0

    @property
    def entries(self):
        return self._entries

    @property
    def probability(self):
        return sum(entry.probability for entry in self._entries)

    # Summing two aggregators groups their entries together and sums probabilities
    def __add__(self, other: object):
        if isinstance(other, _Aggregator):
            return _Aggregator(self._entries + other._entries)
        raise NotImplementedError("Cannot add Aggregators to non-Aggregator objects")

    # For validation logic after class construction
    def __post_init__(self):
        # If greater than 1 *and* "far" from 1
        if fp_gt(self.probability, 1):
            raise RuntimeError(
                f"Aggregator probability of {self.probability:.2f} greater than 1"
            )

    # NOTE: add_bit should be called something else if not binary
    def add_bit(self, bit: int):
        for entry in self._entries:
            entry.add_bit(bit)


@dataclass
class _HuffmanLayer:
    # NOTE: Initialization of Huffman Layer would just put each Entry in its own
    # Aggregator; for D>2 case, may need dummy variables

    # The `field()` business makes mutable defaults ok
    _aggregators: list[_Aggregator] = field(default_factory=list)

    # We sort after initializing
    def __post_init__(self):
        self._sort()

    # reverse=True uses descending probability order; .pop() then removes the least probable aggregators
    def _sort(self):
        self._aggregators.sort(key=lambda x: x.probability, reverse=True)

    def step(self):
        if len(self._aggregators) == 1:
            raise StopIteration("Only one Aggregator in layer; no steps left")

        # Set to hold the combined Aggregators
        least_probable_aggregators = _Aggregator([])

        # NOTE: here, D=2, so we get bit = 0,1. In general would change the range int
        for bit in range(2):
            # Remove the least_probable
            least_probable_aggregator = self._aggregators.pop()

            # Add the bit
            least_probable_aggregator.add_bit(int(bit))

            # Put it into the container above
            least_probable_aggregators += least_probable_aggregator

        # Now feed the merged Aggregator back into the collection to get the new layer
        self._aggregators.append(least_probable_aggregators)

        # Sort it again before the next step
        self._sort()

    # Print the Huffman code as dict and remove 1 as MSB; raises error if HuffmanLayer is not singleton
    def get_final_code(self) -> dict[uint8, bytes]:
        if len(self._aggregators) > 1:
            raise RuntimeError(
                f"{len(self._aggregators)} > 1 aggregators left; need {len(self._aggregators) - 1} more `.step()`s"
            )

        # We sort by shortest lengths to longest lengths
        final_entries = sorted(
            self._aggregators[0].entries,
            key=lambda entry: entry.codeword,
        )

        def sentinel_to_bytes(n: int):
            # Remove the sentinel MSB after coercing into bytearray form
            return bytes(int2bytearray(n)[1:])

        final_code = {
            entry.symbol: sentinel_to_bytes(entry.codeword) for entry in final_entries
        }
        return final_code


def binary_huffman(symbols: Sequence[uint8], probabilities: ndarray):
    # Probabilities must be a PMF
    if not isclose(s := probabilities.sum(), 1):
        raise ValueError(f"Probabilities have sum {s} != 1")

    # Lengths must match
    if (len(symbols)) != (probabilities.size):
        raise ValueError(
            f"{len(symbols)} number of symbols neq to {probabilities.size} number of probabilities"
        )

    # Quickly return trivial codes
    if len(symbols) == 1:
        return {symbols[0]: b"0"}
    if len(symbols) == 2:
        return {symbols[0]: b"0", symbols[1]: b"1"}

    # Now the fun part!

    # Initialize the HuffmanLayer with singleton Aggregators
    huffman_instance = _HuffmanLayer(
        [_Aggregator([_Entry(x, p)]) for x, p in list(zip(symbols, probabilities))]
    )

    # Keep on taking Huffman `.step()`s until we hit the StopIteration
    while True:
        try:
            huffman_instance.step()
        except StopIteration:
            break

    return huffman_instance.get_final_code()
