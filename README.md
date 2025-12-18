An educational exercise to build a tokenizer from scratch.

Part of a higher level effort to learn about LLM's from end-to-end.

Reference
- [Let's build a GPT Tokenizer](https://www.youtube.com/watch?v=zduSFxRajkE)

## Multi-Language Implementations

This project includes identical implementations of the BPE (Byte Pair Encoding) tokenizer in three languages for performance comparison:

- **Python** (`tokenizer.py`) - Original implementation
- **C** (`tokenizer.c`) - Low-level compiled version
- **Rust** (`tokenizer.rs`) - Memory-safe compiled version

All three implementations use the exact same algorithm to enable apples-to-apples performance comparison.

## Prerequisites

- **Python 3.x**
- **GCC** (for C compilation)
- **Rust** compiler (`rustc`)
- **Make** (optional, for using Makefile)
- **Bash** (for benchmark script)

## Quick Start

### Build All Versions

```bash
make all
```

Or compile individually:

```bash
# C version
gcc -O3 -o tokenizer_c tokenizer.c -lm

# Rust version
rustc -O tokenizer.rs -o tokenizer_rust
```

### Run Benchmark

Compare performance across all three implementations:

```bash
make benchmark
# OR
bash benchmark.sh
```

This will:
1. Compile C and Rust versions with optimizations
2. Run all three implementations on `training_text.txt`
3. Display detailed timing for train/encode/decode phases
4. Show overall speedup comparison
5. Verify all outputs match

### Run Individual Versions

```bash
# Python
python tokenizer.py

# C (after building)
./tokenizer_c

# Rust (after building)
./tokenizer_rust
```

### Run Tests

```bash
python test_tokenizer.py
# OR
make test
```

## Project Structure

```
.
├── tokenizer.py          # Python implementation
├── tokenizer.c           # C implementation
├── tokenizer.rs          # Rust implementation
├── test_tokenizer.py     # Test suite
├── training_text.txt     # Sample training data
├── benchmark.sh          # Benchmark runner script
├── Makefile             # Build automation
└── README.md            # This file
```

## Performance Notes

The implementations are deliberately identical in algorithm (including any inefficiencies) to provide a fair language comparison. The benchmark measures:

- **Training time** - Building the BPE vocabulary
- **Encoding time** - Converting text to tokens
- **Decoding time** - Converting tokens back to text
- **Total runtime** - End-to-end execution

Expect to see significant speedups with C and Rust compared to Python, with the exact ratio depending on your system and training data size.

## Cleaning Up

```bash
make clean
```

This removes compiled executables and temporary files.