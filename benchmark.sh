#!/bin/bash

echo "========================================================================"
echo "TOKENIZER BENCHMARK - Python vs C vs Rust"
echo "========================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if training file exists
if [ ! -f "training_text.txt" ]; then
    echo "Error: training_text.txt not found!"
    exit 1
fi

FILE_SIZE=$(wc -c < training_text.txt)
echo "Training file size: $FILE_SIZE bytes"
echo ""

# ============================================================
# Compile C version
# ============================================================
echo -e "${BLUE}[1/6] Compiling C version...${NC}"
gcc -O3 -o tokenizer_c tokenizer.c -lm
if [ $? -ne 0 ]; then
    echo "Error compiling C version"
    exit 1
fi
echo "✓ C compilation successful"
echo ""

# ============================================================
# Compile Rust version
# ============================================================
echo -e "${BLUE}[2/6] Compiling Rust version...${NC}"
rustc -O tokenizer.rs -o tokenizer_rust
if [ $? -ne 0 ]; then
    echo "Error compiling Rust version"
    exit 1
fi
echo "✓ Rust compilation successful"
echo ""

# ============================================================
# Run Python version
# ============================================================
echo -e "${YELLOW}======================================================================${NC}"
echo -e "${YELLOW}Running Python version...${NC}"
echo -e "${YELLOW}======================================================================${NC}"
PYTHON_START=$(date +%s.%N)
python tokenizer.py > /tmp/python_output.txt
PYTHON_END=$(date +%s.%N)
PYTHON_TIME=$(echo "$PYTHON_END - $PYTHON_START" | bc)
echo ""
echo -e "${GREEN}Python total runtime: ${PYTHON_TIME}s${NC}"
echo ""

# ============================================================
# Run C version
# ============================================================
echo -e "${YELLOW}======================================================================${NC}"
echo -e "${YELLOW}Running C version...${NC}"
echo -e "${YELLOW}======================================================================${NC}"
C_START=$(date +%s.%N)
./tokenizer_c > /tmp/c_output.txt
C_END=$(date +%s.%N)
C_TIME=$(echo "$C_END - $C_START" | bc)
echo ""
echo -e "${GREEN}C total runtime: ${C_TIME}s${NC}"
echo ""

# ============================================================
# Run Rust version
# ============================================================
echo -e "${YELLOW}======================================================================${NC}"
echo -e "${YELLOW}Running Rust version...${NC}"
echo -e "${YELLOW}======================================================================${NC}"
RUST_START=$(date +%s.%N)
./tokenizer_rust > /tmp/rust_output.txt
RUST_END=$(date +%s.%N)
RUST_TIME=$(echo "$RUST_END - $RUST_START" | bc)
echo ""
echo -e "${GREEN}Rust total runtime: ${RUST_TIME}s${NC}"
echo ""

# ============================================================
# Summary
# ============================================================
echo "========================================================================"
echo "BENCHMARK SUMMARY"
echo "========================================================================"
printf "%-15s %15s %15s\n" "Language" "Total Time" "Speedup vs Python"
echo "------------------------------------------------------------------------"
printf "%-15s %15ss %15s\n" "Python" "$PYTHON_TIME" "1.00x"

if command -v bc &> /dev/null; then
    C_SPEEDUP=$(echo "scale=2; $PYTHON_TIME / $C_TIME" | bc)
    RUST_SPEEDUP=$(echo "scale=2; $PYTHON_TIME / $RUST_TIME" | bc)
    printf "%-15s %15ss %15sx\n" "C" "$C_TIME" "$C_SPEEDUP"
    printf "%-15s %15ss %15sx\n" "Rust" "$RUST_TIME" "$RUST_SPEEDUP"
else
    printf "%-15s %15ss %15s\n" "C" "$C_TIME" "N/A"
    printf "%-15s %15ss %15s\n" "Rust" "$RUST_TIME" "N/A"
fi
echo "========================================================================"
echo ""

# Verify all outputs are identical
echo "Verifying outputs match..."
if diff /tmp/python_output.txt /tmp/c_output.txt > /dev/null && \
   diff /tmp/python_output.txt /tmp/rust_output.txt > /dev/null; then
    echo -e "${GREEN}✓ All outputs match!${NC}"
else
    echo -e "\033[0;31m✗ Warning: Outputs differ!${NC}"
    echo "This might indicate implementation differences."
fi
echo ""

# Cleanup
rm -f tokenizer_c tokenizer_rust
echo "Cleaned up executables"
