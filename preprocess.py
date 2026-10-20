import numpy as np
from scipy.io import wavfile

from huffman import binary_huffman

# This module contains "prep"
# Importing the wavfile, computing the empirical, obtaining the encoders/decoders, etc.

# uint8, so 0-255
rate, data = wavfile.read("music3b.wav")

# Get unique values *and* number of occurences to get empirical probabilities
_symbols, _counts = np.unique(data, return_counts=True)
probabilities = _counts / np.sum(_counts)

# Just a dict
empirical_distribution: dict[np.uint8, float] = {
    symbol: prob for symbol, prob in zip(_symbols, probabilities)
}

# binary_huffman maps symbols to codewords
huffman_encoder = binary_huffman(list(_symbols), probabilities)
huffman_decoder = {codeword: symbol for symbol, codeword in huffman_encoder.items()}
