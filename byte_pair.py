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


s = "Ｕｎｉｃｏｄｅ! 🅤🅝🅘🅒🅞🅓🅔‽ 🇺‌🇳‌🇮‌🇨‌🇴‌🇩‌🇪! 😄 The very name strikes fear and awe into the hearts of programmers worldwide. We all know we ought to “support Unicode” in our software (whatever that means—like using wchar_t for all the strings, right?). But Unicode can be abstruse, and diving into the thousand-page Unicode Standard plus its dozens of supplementary annexes, reports, and notes can be more than a little intimidating. I don’t blame programmers for still finding the whole thing mysterious, even 30 years after Unicode’s inception."


byte_list = list(s.encode("utf-8"))
print(f"initial size of byte_list={len(byte_list)}")  # show byte pt num

new_encodings = {}
unused_code = 256

# Byte pair loop
while True:
    # Gather most frequent pairs
    pairs = defaultdict(int) 
    for i in range(1, len(byte_list)):
        b1, b2 = byte_list[i - 1], byte_list[i]
        pairs[(b1, b2)] += 1

    max_freq = max(pairs.values()) 
    max_pair = max(pairs, key=pairs.get)
    print(f"max_pair={max_pair}")

    if max_freq == 1:
        break

    new_encodings[unused_code] = max_pair 
    unused_code += 1

    # Replace
    for i in range(1, len(byte_list)):
        pair = (byte_list[i - 1], byte_list[i])
        if pair == max_pair:
            byte_list[i - 1] = unused_code
            byte_list[i] = -1

    # Remove -1s
    byte_list = [byte for byte in byte_list if byte != -1]

    print(f"size of byte_list {len(byte_list)}")

