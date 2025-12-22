## Qs
### What is tokenization? Why is it used?
Tokenization is the process of converting text into tokens. A token is the "atom" of an LLM. 

Tokens are generally more dense than a string.
"Daughter" -> string -> 8 bytes
"Dau" "gh" "ter" -> tokens -> 3 tokens

### 
Why pair bytes and not characters?
- think vocabulary size, lookup tables

Why not compress the training data until no consecutive pairs found?
- probably due to desire to keep limited vocab size

How to determine vocab size?
- experimentation 

Does a larger vocabulary size make a model better? What are the pros / cons of a large vocabulary size? What are lookup tables?

I don't understand how lookup tables work. We'll get there...


## Know your terminology
utf-8 and ascii
an encoding is a way to represent something with something else

Unicode is the standard that assigns code points (numbers) to characters
UTF is a way to encode these code points into bytes
A byte is a group of 8 bits that can store up to 256 distinct values

char -> unicode -> code_pt -> utf-# -> bytes
char -> ASCII -> number

