from collections import defaultdict
import time

CODE_POINT_START = 256  # Start value for custom code point assignment

def timed(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f} seconds")
        return result
    return wrapper


class Tokenizer():
    def __init__(self):
        self.data = ""
        self.vocab = {} 
 
    @timed
    def train(self, training_data):
        # Build initial vocabulary
        self.data = training_data
        self.vocab = {
            b: b
            for b in set(self.data.encode("utf-8"))
        } 

        # Convert chars to bytes
        byte_list = list(self.data.encode("utf-8"))

        unused_code_pt = CODE_POINT_START 

        # Byte pair loop
        while True:
            # Gather most frequent pairs
            pairs = defaultdict(int) 
            for b1, b2 in zip(byte_list, byte_list[1:]):
                pairs[(b1, b2)] += 1

            if not pairs:
                break

            max_freq = max(pairs.values()) 
            max_pair = max(pairs, key=pairs.get)

            if max_freq == 1:
                break

            new_byte_list = []
            for b1, b2 in zip(byte_list, byte_list[1:]):
                if (b1, b2) == max_pair:
                    new_byte_list.append(unused_code_pt)
                else:
                    new_byte_list.append(b1)

            byte_list = new_byte_list
            self.vocab[unused_code_pt] = max_pair 
            unused_code_pt += 1

    @timed
    def encode(self, s: str) -> list[int]: 
        """ Convert string to tokens """
        byte_list = list(s.encode("utf-8"))
        pair_found = True

        while pair_found:
            pair_found = False
            for i, s_pair in enumerate(zip(byte_list, byte_list[1:])):
                for code_pt, vocab_pair in self.vocab.items():
                    if s_pair == vocab_pair:
                        byte_list[i] = -1
                        byte_list[i + 1] = code_pt
                        pair_found = True
                    
            byte_list = [b for b in byte_list if b != -1]

        return byte_list
    
    @timed
    def decode(self, tokens) -> str:
        """ Convert tokens to string """
        pair_inserted = True
        final_code_points = []

        while pair_inserted:
            final_code_points = []
            pair_inserted = False

            for pt in tokens:
                if pt <= CODE_POINT_START - 1 or pt not in self.vocab:
                    # Only values above 255 are assigned pairs
                    final_code_points.append(pt)
                    continue

                b1, b2 = self.vocab[pt]
                final_code_points.extend([b1, b2])
               
                # Reset list - keep the loop going
                tokens = final_code_points
                pair_inserted = True

        # Convert code points to byte ints
        return self.byte_list_to_str(final_code_points)

    def byte_list_to_str(self, byte_list: list[int]) -> str:
        output_str = ""

        # Loop needed to handle multi-byte chars
        i = 0
        while i < len(byte_list):
            # Convert byte to binary string
            b_bin = f"{byte_list[i]:08b}"
            if b_bin[0] == "0":
                # Single byte sequence
                output_str += chr(byte_list[i])
                i += 1
                continue

            bytez = []
            offset = 0
            if all(b == '1' for b in b_bin[:4]):
                offset = 4  # 4 byte sequence
            elif all(b == '1' for b in b_bin[:3]):
                offset = 3  # 3 byte sequence
            else:
                offset = 2  # 2 byte sequence

            bytez = byte_list[i:i+offset]
            i += offset
            
            c = bytes(bytez).decode("utf-8")
            output_str += c

        return output_str 


print("\n" + "=" * 70)
print("TOKENIZER MAIN EXECUTION")
print("=" * 70)

data = ""
with open("training_text.txt", "r", encoding="utf-8") as f:
    data = f.read()

print(f"INPUT: Loaded from training_text.txt")
print(f"       Length: {len(data)} characters, {len(data.encode('utf-8'))} bytes")

print("\n--- TRAINING ---")
t = Tokenizer()
t.train(training_data=data)
print(f"Vocabulary size: {len(t.vocab)} tokens")
print(f"Learned merges: {len([k for k in t.vocab.keys() if k >= 256])}")

print("\n--- ENCODING ---")
encoded_data = t.encode(data)
print(f"Token count: {len(encoded_data)}")
compression_ratio = (1 - len(encoded_data) / len(data.encode('utf-8'))) * 100
print(f"Compression: {compression_ratio:.1f}% ({len(data.encode('utf-8'))} bytes → {len(encoded_data)} tokens)")

print("\n--- DECODING ---")
decoded_data = t.decode(encoded_data)
print(f"Output length: {len(decoded_data)} characters")

print("\n--- RESULT ---")
if data == decoded_data:
    print("✓ SUCCESS: Input matches output")
else:
    print("✗ FAILED: Input does not match output")
    print(f"  Expected length: {len(data)}")
    print(f"  Got length: {len(decoded_data)}")

print("=" * 70 + "\n")

