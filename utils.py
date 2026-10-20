import csv
from collections.abc import Sequence
from typing import Protocol

from numpy import isclose, log2, ndarray, sum


# Any Symbol is one that has a string representation; this is a wrapper for type hints
class Symbol(Protocol):
    def __str__(self) -> str: ...


# [f]loating [p]oint [g]reater [t]han; ensures that a >> b from an fp perspective
def fp_gt(a: float, b: float):
    return (a > b) and not isclose(a, b)


# The usual Shannon entropy
def entropy(pmf: ndarray) -> float:
    return sum(-pmf * log2(pmf))


def export_tuples_to_csv(
    data: Sequence[Sequence[object]], fname: str, header: Sequence[str]
):
    # Keep it to first row; doing all rows would require more compute
    if len(data[0]) != len(header):
        raise ValueError(
            f"Length mismatch between provided headers and first row of data"
        )

    with open(fname, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)  # Write header first
        writer.writerows(data)  # Write the rest of the data
