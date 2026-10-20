from itertools import chain
from math import ceil

import numpy as np
from numpy import uint8

from preprocess import data, empirical_distribution, huffman_encoder, probabilities
from utils import bytes2str, entropy

print(f"Shannon entropy of empirical distribution: {entropy(probabilities):.2f}")

expected_length = 0
for sym, codeword in huffman_encoder.items():
    expected_length += len(bytes2str(codeword)) * empirical_distribution[sym]

print(f"Expected length after applying Huffman code: {expected_length:.2f}")


# We do bit-packing for encoding
# map does int2bytearray for each element of data
# chain connects the int2bytearrays with a single iterator
# b"".join() combines the single iterator
encoded_bits = bytearray(
    b"".join(chain(map(lambda datum: huffman_encoder[datum], data)))
)

# Each element of a bytearray is, well, a byte---but we only use a bit. Thus we
# divide by 8.
# Huffman compression is variable across symbols, so we do not get an integer.
# We thus follow-up with ceil to give the number of bits we need

compressed_length = ceil(len(encoded_bits) / 8)
print(f"Length of compressed data: {compressed_length}")
print(f"Actual length: {len(data)}")
print(f"Compression ratio: {compressed_length / len(data):.2f}")

# Now for decoding
# 1. Have a buffer represent to-be-decoded bits
# 2. For each append, check if to-be-decoded bits matches any entry in the decoder
#   If match, decode and push to data list
#   Else, add another bit and repeat
#   Can optimize by pre-partitioning symbols under equiv. relation of sharing codeword lengths
#   ...but will skip because lazy
# Also doing .pop(0) not as efficient compared to just .pop(), but will skip also

huffman_decoder = {codeword: symbol for symbol, codeword in huffman_encoder.items()}
to_be_decoded = bytearray()
decoded_data: list[uint8] = []

for bit in encoded_bits:
    to_be_decoded.append(bit)
    decoded_value = huffman_decoder.get(bytes(to_be_decoded), None)

    # No match, so skip
    if decoded_value is None:
        continue

    decoded_data.append(decoded_value)
    to_be_decoded = bytearray()

if len(data) != len(decoded_data):
    raise RuntimeError("Length mismatch between original and decoded data")
if not np.all(data == decoded_data):
    raise RuntimeError("Data and decoded_data are not equal everywhere")
