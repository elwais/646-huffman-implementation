from scipy.io import wavfile
from huffman import binary_huffman
from utils import entropy
import numpy as np

# uint8, so 0-255
rate, data = wavfile.read("music3b.wav")

# Get unique values *and* # of occurences to get empirical probabilities
values, counts = np.unique(data, return_counts=True)
probabilities = counts / np.sum(counts)

# binary_huffman maps symbols to codewords
huffman_encoder = binary_huffman(list(values), probabilities)

# codewords are unique, so swapping keys for vals and vice versa creates a decoder
huffman_decoder = {codeword: symbol for symbol, codeword in huffman_encoder.items()}

# # Prints huffman encoder table
# for symbol, codeword in huffman_encoder.items():
#     print(f"{symbol:03d}: {codeword}")
