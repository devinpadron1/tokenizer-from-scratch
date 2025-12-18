# Makefile for tokenizer implementations

CC = gcc
CFLAGS = -O3 -Wall -Wextra
RUSTC = rustc
RUSTFLAGS = -O

.PHONY: all clean benchmark c rust python test

all: tokenizer_c tokenizer_rust

# Compile C version
tokenizer_c: tokenizer.c
	$(CC) $(CFLAGS) -o tokenizer_c tokenizer.c -lm

# Compile Rust version
tokenizer_rust: tokenizer.rs
	$(RUSTC) $(RUSTFLAGS) tokenizer.rs -o tokenizer_rust

# Build both C and Rust
c: tokenizer_c

rust: tokenizer_rust

# Run Python version
python:
	python tokenizer.py

# Run benchmark
benchmark: all
	bash benchmark.sh

# Run tests
test: all
	@echo "Running Python tests..."
	python test_tokenizer.py
	@echo ""
	@echo "All tests passed!"

# Clean build artifacts
clean:
	rm -f tokenizer_c tokenizer_rust
	rm -rf __pycache__
	rm -f /tmp/python_output.txt /tmp/c_output.txt /tmp/rust_output.txt

help:
	@echo "Tokenizer Benchmark Makefile"
	@echo ""
	@echo "Targets:"
	@echo "  all        - Build C and Rust versions (default)"
	@echo "  c          - Build only C version"
	@echo "  rust       - Build only Rust version"
	@echo "  python     - Run Python version"
	@echo "  benchmark  - Run full benchmark comparing all three"
	@echo "  test       - Run test suite (Python)"
	@echo "  clean      - Remove build artifacts"
	@echo "  help       - Show this help message"
