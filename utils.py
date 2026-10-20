import csv
from collections.abc import Sequence
from typing import Protocol, Iterable

from numpy import isclose, log2, ndarray, sum, uint8


# Any Symbol is one that has a string representation; this is a wrapper for type hints
class Symbol(Protocol):
    def __str__(self) -> str: ...


# [f]loating [p]oint [g]reater [t]han; ensures that a > b and not close to b
def fp_gt(a: float, b: float):
    return (a > b) and not isclose(a, b)


# The usual Shannon entropy
def entropy(pmf: ndarray) -> float:
    return sum(-pmf * log2(pmf))


def bytes2str(byte_vals: bytes):
    return "".join([str(i) for i in byte_vals])


def int2bytearray(n: int | uint8):
    return bytearray((n >> i) & 1 for i in range(int(n).bit_length() - 1, -1, -1))


def export_tuples_to_csv(
    data: Iterable[Sequence[object]], fname: str, header: Sequence[str]
):
    # Keep it to first row; doing all rows would require more iterations
    first_row = next(iter(data))
    if len(first_row) != len(header):
        raise ValueError(
            f"Length mismatch between provided headers and first row of data"
        )

    with open(fname, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)  # Write header first
        writer.writerow(first_row)  # Write first row
        writer.writerows(
            data
        )  # Write the rest of the data that does not include first row
