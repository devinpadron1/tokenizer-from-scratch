from collections import defaultdict
import time


def timed(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f} seconds")
        return result
    return wrapper


class Tokenizer():
    def __init__(self, training_data):
        self.data = training_data
        self.vocab = {
            b: b
            for b in set(self.data.encode("utf-8"))
        } 
 
    # @timed
    def train(self):
        byte_list = list(self.data.encode("utf-8"))
        # print(byte_list)

        unused_code_pt = 256

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

    def encode(self, s: str) -> str: 
        """ Converts string to compressed version """
        
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

        return self.byte_list_to_str(byte_list)

    def decode(self, s) -> str:
        """ Convert compressed string to original """
        # Convert chars to code points
        # Recall our vocab maps code points to byte pairs
        code_points = [ord(c) for c in s] 

        pair_inserted = True

        while pair_inserted:
            pairs_to_insert = []

            # Gather pairs
            for i, pt in enumerate(code_points):
                if pt <= 255 or pt not in self.vocab:
                    # Only values above 255 are assigned pairs
                    continue

                pair = self.vocab[pt]
                pairs_to_insert.append((i, pair))
                code_points[i] = -1

            # Insert pairs
            offset = 0
            for i, p in pairs_to_insert:
                idx = i + offset
                code_points[idx:idx] = p 
                offset += 2  # Since we're adding 2 items to the list

            # Clean up prior encodings
            code_points = [pt for pt in code_points if pt != -1]

            pair_inserted = True if pairs_to_insert else False

        return self.byte_list_to_str(code_points)

    def byte_list_to_str(self, byte_list) -> str:
        char_list = [chr(b) for b in byte_list]
        return "".join(char_list)


data = ""
with open("training_text.txt", "r", encoding="utf-8") as f:
    data = f.read()

data = "café naïve résumé"

print()
print(f"  input data => {data}")
# print(list(data.encode("utf-8")))

t = Tokenizer(training_data=data)
t.train()

encoded_data = t.encode(data)
print(f"encoded data => {encoded_data}")
# print([ord(d) for d in encoded_data])

decoded_data = t.decode(encoded_data)
print(f"decoded data => {decoded_data}")

print()
print("success! :-)") if data == decoded_data else print("tokenizer failed :-(")
print()

