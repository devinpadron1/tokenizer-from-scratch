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

s = ""
with open("training_text.txt", "r", encoding="utf-8") as f:
    s = f.read()

byte_list = list(s.encode("utf-8"))
# print(byte_list)

new_encodings = {}
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

    new_encodings[unused_code] = max_pair 
    unused_code += 1

    # Remove -1s
    byte_list = [byte for byte in byte_list if byte != -1]
    print(byte_list)


