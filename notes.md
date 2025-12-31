## Qs
### What is tokenization?
Tokenization is the process of converting text into tokens. 

A token is a number (an id) that represents a piece of text. It's the "atom" of an LLM.

token = 3/4 word on average

### Why is tokenization required?
LLMs have an inherent constraint in their design. They are limited by their context window - the maximum number of tokens it can process for a given request.

Converting all of the raw characters into tokens produces a very large vocabulary size that takes up token space in the context window.

#### Example
The dog ate the bone
|-||--||--||--||---|
 1  2   3   4    5

This sentence is 5 tokens with the GPT4 tokenizer - one for each word, some with leading spaces - but 20 characters total.

A token is a way to compact meaning.

### Why can't tokens be full words?
There is nuance.


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

