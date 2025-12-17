from tokenizer import Tokenizer

tests = [
   "aaaabcdeaaaaghi", 
   "aa",
   "aaa",
   "aaaa",
   "aabaab",
   "unfortunately the understanding was misunderstood",
   "café naïve résumé",
   "x",
   "",
   "the theater thermal theme"
]

for test in tests:
    print()
    print(f"  input data => {test}")

    t = Tokenizer()
    t.train(training_data=test)

    encoded_data = t.encode(test)
    print(f"encoded data => {encoded_data}")

    decoded_data = t.decode(encoded_data)
    print(f"decoded data => {decoded_data}")

    print()
    print("success! :-)") if test == decoded_data else print("tokenizer failed :-(")
    print()

