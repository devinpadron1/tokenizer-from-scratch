#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdint.h>
#include <stdbool.h>
#include "uthash.h"

#define CODE_POINT_START 256
#define MAX_VOCAB_SIZE 50000

// Pair structure to represent byte pairs
typedef struct {
    int b1;
    int b2;
} Pair;

// Hash table entry for pair counting
typedef struct {
    Pair key;           // Key (the pair)
    int count;          // Value (frequency)
    UT_hash_handle hh;  // Makes this structure hashable
} PairHashEntry;

// Vocabulary entry
typedef struct {
    bool is_pair;
    int byte_value;  // For single bytes
    Pair pair_value; // For merged pairs
} VocabEntry;

// Dynamic array for bytes
typedef struct {
    int *data;
    size_t size;
    size_t capacity;
} ByteList;

// Tokenizer structure
typedef struct {
    VocabEntry vocab[MAX_VOCAB_SIZE];
    size_t vocab_size;
} Tokenizer;

// Initialize byte list
ByteList* bytelist_create(size_t initial_capacity) {
    ByteList *list = malloc(sizeof(ByteList));
    list->data = malloc(initial_capacity * sizeof(int));
    list->size = 0;
    list->capacity = initial_capacity;
    return list;
}

void bytelist_append(ByteList *list, int value) {
    if (list->size >= list->capacity) {
        list->capacity *= 2;
        list->data = realloc(list->data, list->capacity * sizeof(int));
    }
    list->data[list->size++] = value;
}

void bytelist_free(ByteList *list) {
    free(list->data);
    free(list);
}

// Convert string to byte list
ByteList* string_to_bytes(const char *str) {
    size_t len = strlen(str);
    ByteList *list = bytelist_create(len);
    for (size_t i = 0; i < len; i++) {
        bytelist_append(list, (unsigned char)str[i]);
    }
    return list;
}

// Find unique bytes in data
void get_unique_bytes(const char *data, bool *present) {
    memset(present, 0, 256 * sizeof(bool));
    size_t len = strlen(data);
    for (size_t i = 0; i < len; i++) {
        present[(unsigned char)data[i]] = true;
    }
}

// Count pairs using hash table (now O(n) instead of O(n²))
PairHashEntry* count_pairs_hash(ByteList *list) {
    if (list->size < 2) {
        return NULL;
    }

    PairHashEntry *pairs_hash = NULL;

    for (size_t i = 0; i < list->size - 1; i++) {
        Pair p = {list->data[i], list->data[i + 1]};

        PairHashEntry *entry;
        HASH_FIND(hh, pairs_hash, &p, sizeof(Pair), entry);

        if (entry) {
            // Pair already exists, increment count
            entry->count++;
        } else {
            // New pair, add to hash table
            entry = malloc(sizeof(PairHashEntry));
            entry->key = p;
            entry->count = 1;
            HASH_ADD(hh, pairs_hash, key, sizeof(Pair), entry);
        }
    }

    return pairs_hash;
}

// Find max frequency pair from hash table
bool find_max_pair(PairHashEntry *pairs_hash, Pair *max_pair, int *max_freq) {
    if (pairs_hash == NULL) {
        return false;
    }

    *max_freq = 0;
    PairHashEntry *entry, *tmp;

    HASH_ITER(hh, pairs_hash, entry, tmp) {
        if (entry->count > *max_freq) {
            *max_freq = entry->count;
            *max_pair = entry->key;
        }
    }

    return true;
}

// Free hash table
void free_pairs_hash(PairHashEntry *pairs_hash) {
    PairHashEntry *entry, *tmp;
    HASH_ITER(hh, pairs_hash, entry, tmp) {
        HASH_DEL(pairs_hash, entry);
        free(entry);
    }
}

// Train the tokenizer
void tokenizer_train(Tokenizer *tok, const char *training_data) {
    clock_t start = clock();

    // Build initial vocabulary
    bool present[256];
    get_unique_bytes(training_data, present);

    tok->vocab_size = 0;
    for (int i = 0; i < 256; i++) {
        if (present[i]) {
            tok->vocab[i].is_pair = false;
            tok->vocab[i].byte_value = i;
            tok->vocab_size++;
        }
    }

    // Convert to byte list
    ByteList *byte_list = string_to_bytes(training_data);

    int unused_code_pt = CODE_POINT_START;

    // Byte pair loop
    while (true) {
        PairHashEntry *pairs_hash = count_pairs_hash(byte_list);

        if (pairs_hash == NULL) {
            break;
        }

        // Find max frequency pair
        Pair max_pair;
        int max_freq;
        if (!find_max_pair(pairs_hash, &max_pair, &max_freq)) {
            free_pairs_hash(pairs_hash);
            break;
        }

        free_pairs_hash(pairs_hash);

        if (max_freq == 1) {
            break;
        }

        // Build new byte list (THIS HAS THE BUG - matches Python)
        ByteList *new_list = bytelist_create(byte_list->size);
        for (size_t i = 0; i < byte_list->size - 1; i++) {
            if (byte_list->data[i] == max_pair.b1 &&
                byte_list->data[i + 1] == max_pair.b2) {
                bytelist_append(new_list, unused_code_pt);
            } else {
                bytelist_append(new_list, byte_list->data[i]);
            }
        }

        bytelist_free(byte_list);
        byte_list = new_list;

        // Add to vocabulary
        tok->vocab[unused_code_pt].is_pair = true;
        tok->vocab[unused_code_pt].pair_value = max_pair;
        tok->vocab_size++;
        unused_code_pt++;

        if (unused_code_pt >= MAX_VOCAB_SIZE) {
            break;
        }
    }

    bytelist_free(byte_list);

    clock_t end = clock();
    double elapsed = (double)(end - start) / CLOCKS_PER_SEC;
    printf("train took %.4f seconds\n", elapsed);
}

// Encode string to tokens
ByteList* tokenizer_encode(Tokenizer *tok, const char *str) {
    clock_t start = clock();

    ByteList *byte_list = string_to_bytes(str);
    bool pair_found = true;

    while (pair_found) {
        pair_found = false;

        for (size_t i = 0; i < byte_list->size - 1; i++) {
            Pair s_pair = {byte_list->data[i], byte_list->data[i + 1]};

            for (int code_pt = 0; code_pt < MAX_VOCAB_SIZE; code_pt++) {
                if (tok->vocab[code_pt].is_pair) {
                    Pair vocab_pair = tok->vocab[code_pt].pair_value;
                    if (s_pair.b1 == vocab_pair.b1 && s_pair.b2 == vocab_pair.b2) {
                        byte_list->data[i] = -1;
                        byte_list->data[i + 1] = code_pt;
                        pair_found = true;
                        break;
                    }
                }
            }
        }

        // Remove -1 entries
        ByteList *new_list = bytelist_create(byte_list->size);
        for (size_t i = 0; i < byte_list->size; i++) {
            if (byte_list->data[i] != -1) {
                bytelist_append(new_list, byte_list->data[i]);
            }
        }
        bytelist_free(byte_list);
        byte_list = new_list;
    }

    clock_t end = clock();
    double elapsed = (double)(end - start) / CLOCKS_PER_SEC;
    printf("encode took %.4f seconds\n", elapsed);

    return byte_list;
}

// Decode tokens to string
char* tokenizer_decode(Tokenizer *tok, ByteList *tokens) {
    clock_t start = clock();

    ByteList *final_list = bytelist_create(tokens->size * 2);

    // Copy initial tokens
    for (size_t i = 0; i < tokens->size; i++) {
        bytelist_append(final_list, tokens->data[i]);
    }

    bool pair_inserted = true;
    while (pair_inserted) {
        pair_inserted = false;
        ByteList *new_list = bytelist_create(final_list->size * 2);

        for (size_t i = 0; i < final_list->size; i++) {
            int pt = final_list->data[i];

            if (pt <= CODE_POINT_START - 1 || !tok->vocab[pt].is_pair) {
                bytelist_append(new_list, pt);
            } else {
                Pair p = tok->vocab[pt].pair_value;
                bytelist_append(new_list, p.b1);
                bytelist_append(new_list, p.b2);
                pair_inserted = true;
            }
        }

        bytelist_free(final_list);
        final_list = new_list;
    }

    // Convert bytes to string
    char *result = malloc(final_list->size + 1);
    for (size_t i = 0; i < final_list->size; i++) {
        result[i] = (char)final_list->data[i];
    }
    result[final_list->size] = '\0';

    bytelist_free(final_list);

    clock_t end = clock();
    double elapsed = (double)(end - start) / CLOCKS_PER_SEC;
    printf("decode took %.4f seconds\n", elapsed);

    return result;
}

int main() {
    printf("\n======================================================================\n");
    printf("TOKENIZER MAIN EXECUTION (C)\n");
    printf("======================================================================\n");

    // Read file
    FILE *f = fopen("training_text.txt", "r");
    if (!f) {
        fprintf(stderr, "Error: Could not open training_text.txt\n");
        return 1;
    }

    fseek(f, 0, SEEK_END);
    long fsize = ftell(f);
    fseek(f, 0, SEEK_SET);

    char *data = malloc(fsize + 1);
    size_t bytes_read = fread(data, 1, fsize, f);
    data[bytes_read] = '\0';
    fclose(f);

    printf("INPUT: Loaded from training_text.txt\n");
    printf("       Length: %ld bytes\n", fsize);

    printf("\n--- TRAINING ---\n");
    Tokenizer tok = {0};
    tokenizer_train(&tok, data);
    printf("Vocabulary size: %zu tokens\n", tok.vocab_size);

    printf("\n--- ENCODING ---\n");
    ByteList *encoded = tokenizer_encode(&tok, data);
    printf("Token count: %zu\n", encoded->size);
    double compression = (1.0 - (double)encoded->size / fsize) * 100;
    printf("Compression: %.1f%% (%ld bytes → %zu tokens)\n", compression, fsize, encoded->size);

    printf("\n--- DECODING ---\n");
    char *decoded = tokenizer_decode(&tok, encoded);
    size_t decoded_len = strlen(decoded);
    printf("Output length: %zu characters\n", decoded_len);

    printf("\n--- RESULT ---\n");
    if (strcmp(data, decoded) == 0) {
        printf("✓ SUCCESS: Input matches output\n");
    } else {
        printf("✗ FAILED: Input does not match output\n");
    }

    printf("======================================================================\n\n");

    free(data);
    free(decoded);
    bytelist_free(encoded);

    return 0;
}
