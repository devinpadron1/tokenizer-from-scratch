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

for i, test in enumerate(tests, 1):
    print("\n" + "=" * 70)
    print(f"TEST {i}/{len(tests)}")
    print("=" * 70)
    print(f"INPUT: '{test}'")
    print(f"       Length: {len(test)} characters, {len(test.encode('utf-8'))} bytes")

    print("\n--- TRAINING ---")
    t = Tokenizer()
    t.train(training_data=test)
    print(f"Vocabulary size: {len(t.vocab)} tokens")
    print(f"Learned merges: {len([k for k in t.vocab.keys() if k >= 256])}")

    print("\n--- ENCODING ---")
    encoded_data = t.encode(test)
    print(f"Tokens: {encoded_data}")
    print(f"Token count: {len(encoded_data)}")
    compression_ratio = (1 - len(encoded_data) / len(test.encode('utf-8'))) * 100 if len(test.encode('utf-8')) > 0 else 0
    print(f"Compression: {compression_ratio:.1f}% ({len(test.encode('utf-8'))} bytes → {len(encoded_data)} tokens)")

    print("\n--- DECODING ---")
    decoded_data = t.decode(encoded_data)
    print(f"Output: '{decoded_data}'")

    print("\n--- RESULT ---")
    if test == decoded_data:
        print("✓ SUCCESS: Input matches output")
    else:
        print("✗ FAILED: Input does not match output")
        print(f"  Expected: '{test}'")
        print(f"  Got:      '{decoded_data}'")

