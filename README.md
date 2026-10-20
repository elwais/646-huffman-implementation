# Huffman Coding of 8-Bit Sampled Music

ECE 646 — Homework 5, Problem 5.X1. An implementation, written from scratch,
of the (binary) Huffman coding algorithm, used to losslessly compress the
8-bit sampled music file `music3b.wav`.

## What the assignment asked for

1. Read the music file.
2. Calculate the empirical distribution of the samples.
3. Calculate the entropy of the file (iid assumption).
4. Build the (binary) Huffman codewords and put them in a table.
5. Encode the data with the table; compare the compressed size with the
   entropy bound.
6. Decode the data with the table and verify that it matches the original.

Hand-in: a description of the algorithm, the program code, and the print-out
from a test run verifying compression and losslessness. All three live in
this repository (see below).

## Files

| File           | Role                                                                        |
| -------------- | --------------------------------------------------------------------------- |
| `huffman.py`   | The from-scratch Huffman implementation (`binary_huffman`)                  |
| `utils.py`     | Helpers: Shannon entropy, bit-stack utilities, CSV export                   |
| `preprocess.py`| Reads `music3b.wav`, builds the empirical distribution and the code tables  |
| `__init__.py`  | End-to-end test run: encodes, packs, decodes, verifies, prints results      |
| `music3b.wav`  | The 8-bit sampled music file (12 kHz, 132,000 samples)                      |

## The algorithm

Each distinct sample value starts as its own node (`_Entry`: symbol +
probability). Entries are wrapped in `_Aggregator` groups, and all groups live
in a `_HuffmanLayer` sorted by decreasing probability. The core loop:

1. Pop the two least-probable groups.
2. Push bit `0` onto the bit-stack of every entry in one, and bit `1` onto
   every entry in the other.
3. Merge the two groups, push the merged group back, and re-sort.

Repeat until a single group remains. Because each entry keeps its bits in a
stack in *reverse* order (the bit assigned at the last merge is the most
significant), a merge only touches the entries of the two groups being
merged. When reading out a codeword, the stack is reversed and joined; a
sentinel `1` is prepended as the most significant bit so that leading zeros
survive integer conversion, and the sentinel is stripped afterwards. The
result is a prefix-free table mapping each symbol to a codeword.

Encoding replaces each sample by its codeword and packs the resulting bit
stream into bytes. Decoding is the greedy left-to-right inverse: accumulate
bits until the buffer matches a codeword, emit the symbol, reset the buffer
(prefix-freeness guarantees this is unambiguous).

## Running it

Requires Python ≥ 3.10 with `numpy` and `scipy`:

```bash
pip install -r requirements.txt
python __init__.py
```

The script must be run from this directory (next to `music3b.wav`). It
verifies that encoding followed by decoding reproduces the original samples
and raises an error if it does not.

### Sample test-run print-out

```
Shannon entropy of empirical distribution: 4.72
Expected length after applying Huffman code: 4.75
Length of compressed data: 78366
Actual length: 132000
Compression ratio: 0.59
```

- Entropy bound under the iid assumption: `132000 × 4.72 ≈ 623,000 bits ≈
  77,900 bytes`; the packed Huffman stream is `78,366` bytes — within
  0.6% of the bound, the gap being the (small) coding redundancy plus the
  sub-byte packing slack.
- The decode/verify step ends without error, i.e. the decoded data is
  identical to the original.

## Interactive notebook

`huffman-coding-music.ipynb` is a Google Colab notebook that walks through
all six steps with the exact same code and produces the print-outs above.
To run it: upload `huffman-coding-music.ipynb` to Colab, run all cells, and
select `music3b.wav` when the upload widget appears.