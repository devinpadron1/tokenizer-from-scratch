""" 
Implement Byte Pair encoding
1. Continuously iterate over your text
2. Find the most frequent adjacent pairs of bytes
    - how to store? dict with key being encoding as str, value being count?
    - do we replace all in each pass or one per pass?
    - could use a heap
        - why?
            - I wouldn't need to sort or iterate over
3. Replace it with a new character
    - which character?
        - initially we'll have 
4. Continue until all are unique(?)
    - unsure about the stop condition (when no tokens with freq > 1?)

Data Structures
{} to count pairs    
    - dict: pair (str) -> count (int)
    - a max heap which contains highest count pair on top
{} to store your vocabulary
    - dict with mapping between abbreviated char and string
    - ex Z -> aa
"""


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

        unused_code = 256

        # Byte pair loop
        while True:
            # Gather most frequent pairs
            pairs = defaultdict(int) 
            for b1, b2 in zip(byte_list, byte_list[1:]):
                pairs[(b1, b2)] += 1

            max_freq = max(pairs.values()) 
            max_pair = max(pairs, key=pairs.get)

            if max_freq == 1:
                break

            # Replace
            for i, (b1, b2) in enumerate(zip(byte_list, byte_list[1:])):
                if (b1, b2) == max_pair:
                    byte_list[i] = unused_code
                    byte_list[i + 1] = -1

            self.vocab[unused_code] = max_pair 
            unused_code += 1

            # Filter out -1s
            byte_list = [byte for byte in byte_list if byte != -1]

        # print(byte_list)

    def encode(self, s: str) -> str: 
        """ 
        string -> tokens 

        We want to convert the string into the tokens.

        This will involve multiple passes on s
        my vocab dictionary contains byte -> pair pairing
        we need to start iterating over the pairs on strings 
        and compare to the list of values in the dict
        I think the way we encode is similar to how we train it
        
        for every pair, iterate over the vocabulary values
        if you find a match, replace
        """
        
        byte_list = list(s.encode("utf-8"))
        pair_found = True
        
        while pair_found:
            for i, s_pair in enumerate(zip(byte_list, byte_list[1:])):
                pair_found = False
                for pt_num, vocab_pair in self.vocab.items():
                    if s_pair == vocab_pair:
                        byte_list[i] = -1
                        byte_list[i + 1] = pt_num
                        pair_found = True
                    
            byte_list = [b for b in byte_list if b != -1]

        char_list = [chr(b) for b in byte_list]
        new_str = "".join(char_list)

        return new_str 

    def decode(self, s) -> str:
        """ 
        tokens -> string 
        """

        byte_list = list(s.encode("utf-8"))
        pair_inserted = True

        while pair_inserted:
            pair_inserted = False 
            for i, b in enumerate(byte_list):
                if b in self.vocab:
                    pair = self.vocab[b]
                    # TODO: Insert vocab pair
                    pair_inserted = True

data = ""
with open("training_text.txt", "r", encoding="utf-8") as f:
    data = f.read()

# data = "aabcdeaaghi"

print(f"data before={data}")

t = Tokenizer(training_data=data)
t.train()

print(f"data after={t.encode(data)}")

