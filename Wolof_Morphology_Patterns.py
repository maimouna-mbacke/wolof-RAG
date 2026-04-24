import json
import re
from pathlib import Path
from collections import defaultdict

"""
Extract actual morphological patterns from Wolof examples
"""

INPUT_FILE = "Wolof_Segmented/wolof_examples_dataset.json"
OUTPUT_DIR = "Wolof_Morphology_Patterns"


class MorphologyExtractor:

    def __init__(self):
        self.suffixes = defaultdict(list)
        self.prefixes = defaultdict(list)
        self.stems = defaultdict(int)
        self.patterns = []

    def load_examples(self):
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    def extract_common_suffixes(self, examples):
        """Find recurring word endings (potential suffixes)."""
        # Common Wolof verb suffixes from literature
        known_suffixes = [
            'al', 'ante', 'loo', 'lu', 'e', 'i', 'u',
            'aat', 'ati', 'waat', 'si', 'naa', 'na',
            'oon', 'ee', 'ko', 'la', 'ci', 'di'
        ]

        for example in examples:
            text = example.get('text', '')
            words = text.split()

            for word in words:
                word = word.lower().strip('.,!?;:')
                if len(word) < 3:
                    continue

                # Check for known suffixes
                for suffix in known_suffixes:
                    if word.endswith(suffix) and len(word) > len(suffix) + 2:
                        stem = word[:-len(suffix)]
                        self.suffixes[suffix].append({
                            'word': word,
                            'stem': stem,
                            'source': example.get('source', 'unknown')
                        })

    def extract_verb_patterns(self, examples):
        """Extract verb conjugation patterns."""
        # Wolof verb patterns: root + extensions + TAM + clitics
        verb_markers = ['na', 'nga', 'naa', 'dafa', 'danga', 'dinaa']

        for example in examples:
            text = example.get('text', '').lower()

            for marker in verb_markers:
                if marker in text:
                    # Extract context around marker
                    pattern = re.findall(rf'\w+\s+{marker}', text)
                    if pattern:
                        self.patterns.append({
                            'pattern': pattern[0],
                            'marker': marker,
                            'example': text,
                            'source': example.get('source', 'unknown')
                        })

    def find_reduplication(self, examples):
        """Find reduplicated forms."""
        reduplicated = []

        for example in examples:
            text = example.get('text', '')
            words = text.split()

            for word in words:
                word = word.lower().strip('.,!?;:')
                if len(word) < 6:
                    continue

                # Check for full reduplication (word-word)
                mid = len(word) // 2
                if word[:mid] == word[mid:]:
                    reduplicated.append({
                        'word': word,
                        'base': word[:mid],
                        'example': text,
                        'source': example.get('source', 'unknown')
                    })

        return reduplicated

    def extract_clitics(self, examples):
        """Extract clitic patterns."""
        # Object clitics: -ko, -la, -ci, -leen, etc.
        clitic_patterns = [
            'ko', 'la', 'ci', 'leen', 'leen', 'ma', 'nga'
        ]

        clitics = defaultdict(list)

        for example in examples:
            text = example.get('text', '')
            # Look for verb-clitic combinations
            for clitic in clitic_patterns:
                pattern = re.findall(rf'\w+{clitic}\b', text.lower())
                for match in pattern:
                    clitics[clitic].append({
                        'form': match,
                        'example': text,
                        'source': example.get('source', 'unknown')
                    })

        return clitics

    def save_patterns(self, output_path):
        """Save extracted patterns."""
        output_path.mkdir(exist_ok=True)

        # Save suffixes
        with open(output_path / 'suffixes.json', 'w', encoding='utf-8') as f:
            json.dump(dict(self.suffixes), f, indent=2, ensure_ascii=False)

        # Save verb patterns
        with open(output_path / 'verb_patterns.json', 'w', encoding='utf-8') as f:
            json.dump(self.patterns, f, indent=2, ensure_ascii=False)

        print(f"✓ Saved patterns to {output_path}")


def main():
    print("=" * 60)
    print("WOLOF MORPHOLOGY PATTERN EXTRACTION")
    print("=" * 60)

    extractor = MorphologyExtractor()

    print("\nLoading examples...")
    examples = extractor.load_examples()
    print(f"  ✓ Loaded {len(examples)} examples")

    print("\nExtracting suffixes...")
    extractor.extract_common_suffixes(examples)
    print(f"  ✓ Found {len(extractor.suffixes)} suffix types")

    print("\nExtracting verb patterns...")
    extractor.extract_verb_patterns(examples)
    print(f"  ✓ Found {len(extractor.patterns)} verb patterns")

    print("\nFinding reduplication...")
    reduplicated = extractor.find_reduplication(examples)
    print(f"  ✓ Found {len(reduplicated)} reduplicated forms")

    print("\nExtracting clitics...")
    clitics = extractor.extract_clitics(examples)
    print(f"  ✓ Found {len(clitics)} clitic types")

    print("\nSaving patterns...")
    output_path = Path(OUTPUT_DIR)
    extractor.save_patterns(output_path)

    # Summary
    print("\n" + "=" * 60)
    print("EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"Output: {output_path.absolute()}")
    print("\nNext: Build morphological analyzer from these patterns")


if __name__ == "__main__":
    main()