# -*- coding: utf-8 -*-
# Text Analyzer: Word frequency analysis

def analyze_text(text):
    """Analyze word frequency in text."""
    # Convert to lowercase
    let text_lower = text.lower()

    # Remove punctuation and split
    let words = text_lower.split()

    # Count word frequencies
    let word_count = {}
    for word in words:
        if word in word_count:
            word_count[word] = word_count[word] + 1
        else:
            word_count[word] = 1

    # Sort by frequency (descending)
    let sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)

    return sorted_words

# Test text
let text = "the quick brown fox jumps over the lazy dog"

# Analyze
let frequency = analyze_text(text)

# Print results
for word, count in frequency:
    print(word + ": " + str(count))
