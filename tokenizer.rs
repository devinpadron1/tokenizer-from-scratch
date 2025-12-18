use std::collections::HashMap;
use std::fs;
use std::time::Instant;

const CODE_POINT_START: i32 = 256;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
struct Pair {
    b1: i32,
    b2: i32,
}

#[derive(Debug, Clone)]
enum VocabEntry {
    Byte(i32),
    Pair(Pair),
}

struct Tokenizer {
    vocab: HashMap<i32, VocabEntry>,
}

impl Tokenizer {
    fn new() -> Self {
        Tokenizer {
            vocab: HashMap::new(),
        }
    }

    fn train(&mut self, training_data: &str) {
        let start = Instant::now();

        // Build initial vocabulary
        let bytes: Vec<u8> = training_data.bytes().collect();
        let unique_bytes: std::collections::HashSet<u8> = bytes.iter().cloned().collect();

        for &b in &unique_bytes {
            self.vocab.insert(b as i32, VocabEntry::Byte(b as i32));
        }

        // Convert to byte list
        let mut byte_list: Vec<i32> = bytes.iter().map(|&b| b as i32).collect();
        let mut unused_code_pt = CODE_POINT_START;

        // Byte pair loop
        loop {
            // Count pairs
            let mut pairs: HashMap<Pair, i32> = HashMap::new();
            for i in 0..byte_list.len().saturating_sub(1) {
                let pair = Pair {
                    b1: byte_list[i],
                    b2: byte_list[i + 1],
                };
                *pairs.entry(pair).or_insert(0) += 1;
            }

            if pairs.is_empty() {
                break;
            }

            // Find max frequency pair
            let max_pair = pairs
                .iter()
                .max_by_key(|(_, &count)| count)
                .map(|(pair, _)| *pair)
                .unwrap();

            let max_freq = pairs[&max_pair];

            if max_freq == 1 {
                break;
            }

            // Build new byte list (THIS HAS THE BUG - matches Python exactly)
            // Iterates through pairs, only appends first element or merged token
            // Last element is never appended!
            let mut new_byte_list = Vec::new();
            for i in 0..byte_list.len().saturating_sub(1) {
                if byte_list[i] == max_pair.b1 && byte_list[i + 1] == max_pair.b2 {
                    new_byte_list.push(unused_code_pt);
                } else {
                    new_byte_list.push(byte_list[i]);
                }
            }

            byte_list = new_byte_list;

            // Add to vocabulary
            self.vocab.insert(unused_code_pt, VocabEntry::Pair(max_pair));
            unused_code_pt += 1;
        }

        let elapsed = start.elapsed();
        println!("train took {:.4} seconds", elapsed.as_secs_f64());
    }

    fn encode(&self, s: &str) -> Vec<i32> {
        let start = Instant::now();

        let mut byte_list: Vec<i32> = s.bytes().map(|b| b as i32).collect();
        let mut pair_found = true;

        while pair_found {
            pair_found = false;

            for i in 0..byte_list.len().saturating_sub(1) {
                let s_pair = Pair {
                    b1: byte_list[i],
                    b2: byte_list[i + 1],
                };

                for (&code_pt, vocab_entry) in &self.vocab {
                    if let VocabEntry::Pair(vocab_pair) = vocab_entry {
                        if s_pair == *vocab_pair {
                            byte_list[i] = -1;
                            byte_list[i + 1] = code_pt;
                            pair_found = true;
                            break;
                        }
                    }
                }
            }

            byte_list.retain(|&b| b != -1);
        }

        let elapsed = start.elapsed();
        println!("encode took {:.4} seconds", elapsed.as_secs_f64());

        byte_list
    }

    fn decode(&self, tokens: &[i32]) -> String {
        let start = Instant::now();

        let mut final_code_points: Vec<i32> = tokens.to_vec();
        let mut pair_inserted = true;

        while pair_inserted {
            pair_inserted = false;
            let mut new_list = Vec::new();

            for &pt in &final_code_points {
                if pt <= CODE_POINT_START - 1 {
                    new_list.push(pt);
                } else if let Some(VocabEntry::Pair(pair)) = self.vocab.get(&pt) {
                    new_list.push(pair.b1);
                    new_list.push(pair.b2);
                    pair_inserted = true;
                } else {
                    new_list.push(pt);
                }
            }

            final_code_points = new_list;
        }

        let elapsed = start.elapsed();
        println!("decode took {:.4} seconds", elapsed.as_secs_f64());

        // Convert to bytes then string
        let bytes: Vec<u8> = final_code_points.iter().map(|&b| b as u8).collect();
        String::from_utf8(bytes).unwrap_or_else(|_| String::from("ERROR: Invalid UTF-8"))
    }
}

fn main() {
    println!("\n======================================================================");
    println!("TOKENIZER MAIN EXECUTION (Rust)");
    println!("======================================================================");

    // Read file
    let data = fs::read_to_string("training_text.txt")
        .expect("Error: Could not read training_text.txt");

    let byte_count = data.as_bytes().len();
    println!("INPUT: Loaded from training_text.txt");
    println!("       Length: {} characters, {} bytes", data.len(), byte_count);

    println!("\n--- TRAINING ---");
    let mut tokenizer = Tokenizer::new();
    tokenizer.train(&data);
    println!("Vocabulary size: {} tokens", tokenizer.vocab.len());
    let learned_merges = tokenizer
        .vocab
        .iter()
        .filter(|(&k, _)| k >= CODE_POINT_START)
        .count();
    println!("Learned merges: {}", learned_merges);

    println!("\n--- ENCODING ---");
    let encoded_data = tokenizer.encode(&data);
    println!("Token count: {}", encoded_data.len());
    let compression = (1.0 - encoded_data.len() as f64 / byte_count as f64) * 100.0;
    println!(
        "Compression: {:.1}% ({} bytes → {} tokens)",
        compression,
        byte_count,
        encoded_data.len()
    );

    println!("\n--- DECODING ---");
    let decoded_data = tokenizer.decode(&encoded_data);
    println!("Output length: {} characters", decoded_data.len());

    println!("\n--- RESULT ---");
    if data == decoded_data {
        println!("✓ SUCCESS: Input matches output");
    } else {
        println!("✗ FAILED: Input does not match output");
        println!("  Expected length: {}", data.len());
        println!("  Got length: {}", decoded_data.len());
    }

    println!("======================================================================\n");
}
