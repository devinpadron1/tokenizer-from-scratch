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

            # Replace most freq pair with unused code point
            new_byte_list = []
            i = 0
            while i < len(byte_list):
                b1 = byte_list[i]
                b2 = byte_list[i + 1] if i + 1 < len(byte_list) else None

                if b2 is not None and (b1, b2) == max_pair:
                    new_byte_list.append(unused_code_pt)
                    i += 2
                else:
                    new_byte_list.append(b1)
                    i += 1

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
                        break
                    
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

        return bytes(final_code_points).decode("utf-8")


with open("training_text.txt", "r", encoding="utf-8") as f:
    data = f.read()

t = Tokenizer()
t.train(training_data=data)

encoded_data = t.encode(data)
decoded_data = t.decode(encoded_data)

print("success! :-)") if data == decoded_data else print("tokenizer failed :-(")

