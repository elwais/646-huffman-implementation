# Huffman Coding of 8-Bit Sampled Music

This repository holds the code used for Problem 5.X1, which tasks us with implementing
the binary Huffman encoder on an audio file.

## Where to find work for each problem/task assigned

| Task | What it asks for | Where it's implemented (entry point) |
| --- | --- | --- |
| 1 · program step | Read the music file `music3b.wav` into memory | `preprocess.py` — module top level: `wavfile.read("music3b.wav")`                    |
| 2 · program step | Calculate the empirical distribution | `preprocess.py` — module top level: `np.unique(data, return_counts=True)` → `empirical_distribution` |
| 3 · program step | Calculate the entropy of the file (iid assumption) | `__init__.py` — calls `utils.entropy(probabilities)` (defined in `utils.py`)            |
| 4 · program step | Calculate the (binary) Huffman codewords and put them in a table | `huffman.py` — `binary_huffman(...)`, core loop `_HuffmanLayer.step()`; invoked from `preprocess.py` → `huffman_encoder` / `huffman_decoder` |
| 5 · program step | Encode the data with the table; size vs. the entropy bound | `__init__.py` — bit-packing encode (`chain`/`join` over codewords) + `ceil(len(encoded_bits) / 8)`, compared with `entropy()` bound |
| 6 · program step | Decode the data with the table; verify it matches the original | `__init__.py` — greedy decode loop over `huffman_decoder`; `np.all(data == decoded_data)` raises on mismatch |
| H1 · hand-in | A description of the algorithm you use | README — “The algorithm” section (data structures + procedure) |
| H2 · hand-in | Program code clear enough to see how the algorithm is implemented | All source files — commented `huffman.py`, `utils.py`, `preprocess.py`, `__init__.py` |
| H3(a) · hand-in | Test-run print-out verifying: how much the data was compressed | `__init__.py` — “Length of compressed data” / “Compression ratio” prints; see “Output” below |
| H3(b) · hand-in | Test-run print-out verifying: data unchanged after encoding/decoding | `__init__.py` — lossless checks (no `RuntimeError` ⇒ unchanged); see “Output” below |

## Files

The table below lists the Python files used in this project.

| File           | Role                                                                         |
| -------------- | ---------------------------------------------------------------------------  |
| `huffman.py`   | Implementation of the binary Huffman code (`binary_huffman`)                 |
| `utils.py`     | Assorted utility functions with bits, entropy, and the like                  |
| `preprocess.py`| Reads `music3b.wav` and builds the empirical distribution and the code tables|
| `__init__.py`  | The primary file that handles tasks 3 and later                              |
| `music3b.wav`  | The 8-bit sampled music file                                                 |

## The algorithm

### Background and data structures used

I will deliberately leave out micro-optimizations and edge-case handling for
brevity's sake; you're more than welcome to examine `huffman.py` for the
nitty-gritty details if you are curious. Note that I use "symbol" to refer to
an element in the support set. This term might be nonstandard; you've been
warned.

My implementation of the Huffman coder closely mirrors the by-hand way of doing it
through the use of custom data structures, defined below. (The actual code prefixes
their names with an underscore to mark as "private." I will be dropping those for 
convenience's sake.)
- `Entry`: the underlying element of the empirical distribution, holding
    - an element of the support,
    - that element's empirical probability, and
    - a (mutable) list of bits that will get updated in Huffman steps.
- `Aggregator`: an abstraction of grouping multiple `Entry`s when combining the
least probable.
- `HuffmanLayer`: a specific layout of `Aggregators` and their associated `Entry`
assignments. When initializing the algorithm, each `Aggregator` holds exactly
one `Entry`. When taking a Huffman step, the least-probable combine into a single
aggregator with its probability being given a sum.

### The algorithm

#### Givens

Assume we're given two
equal-length `Sequence`s (Python classes that have notions of length and
indexing), with one sequence containing the support and the other containing
the probability. The $i^\text{th}$ element of the support corresponds to the
$i^\text{th}$ probability. (In essence, we have the empirical distribution expressed
slightly differently.) The process is thus as follows.

#### Procedure

1. Begin by assigning each element-probability pair into its own `Entry`, which is
then put into its own `Aggregator` which then forms the inital `HuffmanLayer`.
2. Perform the Huffman step (`HuffmanLayer`s have a `.step()` method that represents this).
    1. Remove the two least probable `Aggregator`s.
    2. Prepend a `0` to the `Entry`s in one of the `Aggregator`s and a `1` to
       the `Entry`s in the other.
    3. Merge the `Aggregator`s into a single `Aggregator`.
    5. Put the merged `Aggregator` back into the `HuffmanLayer`.
3. Attempt to take another Huffman step.
    - If the step **does not raise** a `StopIteration` error, repeat step 2.
    - Else, there is one `Aggregator` left, and there are no more steps to take.
4. At this point, each `Entry` in the lone `Aggregator` has codewords that correspond
to the Huffman code. For each `Entry`, pull out the symbol and associate with it
the completed codeword to get a map (in Python, a `dict`) from symbols to codewords.
5. Return that map.

The above yields the Huffman encoder. As the codewords are unique, one can simply
swap the keys and values of the `dict` to produce a decoder:
```py
huffman_decoder = {
    codeword: symbol for symbol, codeword in huffman_encoder.items()
}
```

## How to run the code

Requires Python ≥ 3.10 with `numpy` and `scipy`:

```bash
pip install -r requirements.txt
python __init__.py
```

The script must be run in this directory (next to `music3b.wav`). It will compute and print
- the Shannon entropy of `music3b.wav`,
- the expected Huffman code length of `music3b.wav`,
- the length of the music data after Huffman coding,
- the length of the original music data, and
- the ratio of the former and the latter ("compression ratio").

## Output

```
Shannon entropy of empirical distribution: 4.72
Expected length after applying Huffman code: 4.75
Length of compressed data: 78366
Actual length: 132000
Compression ratio: 0.59
```
