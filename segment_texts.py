import os
import re
import json
from pathlib import Path
from typing import List, Dict

# Configuration
INPUT_DIR = "Wolof_Resources_Text"
OUTPUT_DIR = "Wolof_Segmented"


class WolofTextSegmenter:
    """Segments Wolof linguistic texts into structured, learnable chunks."""

    def __init__(self):
        self.segments = []

    def clean_text(self, text: str) -> str:
        """Clean text of artifacts from PDF extraction."""
        # Remove page markers
        text = re.sub(r'={40,}', '\n', text)
        text = re.sub(r'PAGE \d+', '', text)

        # Remove excessive whitespace but preserve paragraph breaks
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def detect_segment_type(self, text: str) -> str:
        """Detect what type of segment this is."""
        text_lower = text.lower()

        # Section headers (short, might end with colon or be all caps)
        if len(text) < 100 and (text.isupper() or text.endswith(':') or re.match(r'^\d+\.?\d*\s+[A-Z]', text)):
            return "section_header"

        # Grammar rule indicators
        grammar_indicators = [
            'verb', 'noun', 'adjective', 'tense', 'aspect', 'conjugation',
            'morpheme', 'suffix', 'prefix', 'inflection', 'declension',
            'phoneme', 'phonology', 'syntax', 'morphology', 'clause',
            'particle', 'marker', 'agreement', 'gender', 'plural'
        ]

        if any(indicator in text_lower for indicator in grammar_indicators):
            return "grammar_rule"

        # Vocabulary (word - definition or word: definition)
        if re.match(r'^[a-zàáâãäåçèéêëìíîïñòóôõöùúûüý]+\s*[-:–]\s*', text_lower):
            return "vocabulary"

        # Examples with Wolof text patterns
        wolof_patterns = [
            r'\b(dafa|danga|dangay|dinaa|nga|naa|la|ci|di|mu|bu|ku|su)\b',
            r'\b(am|jàng|dëkk|dem|gis|wax|jox|dox)\b'
        ]

        if any(re.search(pattern, text_lower) for pattern in wolof_patterns):
            return "example"

        return "paragraph"

    def split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences while preserving linguistic examples."""
        # Split on sentence boundaries but be careful with abbreviations
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
        return [s.strip() for s in sentences if len(s.strip()) > 20]

    def split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs more aggressively."""
        paragraphs = []

        lines = text.split('\n')
        current_para = []

        for line in lines:
            line = line.strip()

            if not line:
                if current_para:
                    paragraphs.append(' '.join(current_para))
                    current_para = []
                continue

            # If line looks like a header, save current para and start new
            if (len(line) < 100 and (line.isupper() or line.endswith(':') or
                                     re.match(r'^\d+\.?\d*\s+[A-Z]', line))):
                if current_para:
                    paragraphs.append(' '.join(current_para))
                    current_para = []
                paragraphs.append(line)
                continue

            current_para.append(line)

            # If paragraph is getting long, split it
            if len(' '.join(current_para)) > 1000:
                paragraphs.append(' '.join(current_para))
                current_para = []

        if current_para:
            paragraphs.append(' '.join(current_para))

        # Filter out very short segments
        paragraphs = [p for p in paragraphs if len(p) > 30]

        return paragraphs

    def extract_wolof_examples(self, text: str) -> List[Dict]:
        """Extract Wolof sentences (might have translations)."""
        examples = []

        # Look for sentences with Wolof particles
        sentences = self.split_into_sentences(text)

        for i, sentence in enumerate(sentences):
            # Check if this looks like Wolof
            wolof_markers = ['dafa', 'danga', 'nga', 'naa', 'la', 'mu', 'bu', 'di']
            if any(marker in sentence.lower() for marker in wolof_markers):
                example = {
                    "text": sentence,
                    "type": "wolof_sentence"
                }

                # Check if next sentence might be translation
                if i + 1 < len(sentences) and len(sentences[i + 1]) > 10:
                    if not any(marker in sentences[i + 1].lower() for marker in wolof_markers):
                        example["possible_translation"] = sentences[i + 1]

                examples.append(example)

        return examples

    def process_file(self, filepath: Path, category: str) -> Dict:
        """Process a single text file."""
        print(f"\n  📄 Processing: {filepath.name}")

        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        # Clean the text
        text = self.clean_text(text)

        # Split into paragraphs
        paragraphs = self.split_into_paragraphs(text)

        print(f"    Found {len(paragraphs)} raw segments")

        # Extract Wolof examples
        examples = self.extract_wolof_examples(text)

        # Classify each paragraph
        classified_segments = []

        for para in paragraphs:
            segment_type = self.detect_segment_type(para)

            classified_segments.append({
                "text": para,
                "type": segment_type,
                "category": category,
                "source_file": filepath.stem,
                "length": len(para),
                "word_count": len(para.split())
            })

        # Count by type
        type_counts = {}
        for seg in classified_segments:
            seg_type = seg["type"]
            type_counts[seg_type] = type_counts.get(seg_type, 0) + 1

        result = {
            "source_file": filepath.stem,
            "category": category,
            "total_segments": len(classified_segments),
            "segments": classified_segments,
            "wolof_examples": examples,
            "stats": type_counts
        }

        print(f"    ✓ Extracted {len(classified_segments)} segments:")
        for seg_type, count in sorted(type_counts.items()):
            print(f"      - {seg_type}: {count}")
        print(f"      - Wolof examples extracted: {len(examples)}")

        return result

    def save_segments(self, data: Dict, output_path: Path):
        """Save segmented data to JSON."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def create_training_dataset(self, all_results: List[Dict], output_path: Path):
        """Create a flat training dataset from all segments."""
        training_data = []

        for result in all_results:
            for segment in result["segments"]:
                training_data.append(segment)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, indent=2, ensure_ascii=False)

        return training_data

    def create_examples_dataset(self, all_results: List[Dict], output_path: Path):
        """Create a dataset of just Wolof examples."""
        all_examples = []

        for result in all_results:
            for example in result["wolof_examples"]:
                example["source"] = result["source_file"]
                example["category"] = result["category"]
                all_examples.append(example)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_examples, f, indent=2, ensure_ascii=False)

        return all_examples


def process_all_texts():
    """Process all text files and create segmented datasets."""

    # Create output directory
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)

    segmenter = WolofTextSegmenter()
    all_results = []

    input_path = Path(INPUT_DIR)

    print("=" * 60)
    print("WOLOF TEXT SEGMENTATION FOR AI TRAINING")
    print("=" * 60)

    # Process each category
    for category_dir in sorted(input_path.iterdir()):
        if not category_dir.is_dir():
            continue

        print(f"\n{'=' * 60}")
        print(f"Category: {category_dir.name}")
        print(f"{'=' * 60}")

        # Create category output directory
        category_output = output_path / category_dir.name
        category_output.mkdir(exist_ok=True)

        txt_files = list(category_dir.glob("*.txt"))

        if not txt_files:
            print("  No text files found.")
            continue

        for txt_file in sorted(txt_files):
            result = segmenter.process_file(txt_file, category_dir.name)
            all_results.append(result)

            # Save individual file segments
            output_file = category_output / f"{txt_file.stem}_segments.json"
            segmenter.save_segments(result, output_file)

    # Create master datasets
    print(f"\n{'=' * 60}")
    print("Creating Master Datasets")
    print(f"{'=' * 60}")

    training_data = segmenter.create_training_dataset(
        all_results,
        output_path / "wolof_training_dataset.json"
    )

    examples_data = segmenter.create_examples_dataset(
        all_results,
        output_path / "wolof_examples_dataset.json"
    )

    # Calculate statistics
    total_segments = sum(r["total_segments"] for r in all_results)
    total_examples = sum(len(r["wolof_examples"]) for r in all_results)

    # Aggregate type counts
    all_type_counts = {}
    for result in all_results:
        for seg_type, count in result["stats"].items():
            all_type_counts[seg_type] = all_type_counts.get(seg_type, 0) + count

    print(f"\n{'=' * 60}")
    print("SEGMENTATION SUMMARY")
    print(f"{'=' * 60}")
    print(f"Files processed: {len(all_results)}")
    print(f"Total segments: {total_segments}")
    print(f"\nSegment types:")
    for seg_type, count in sorted(all_type_counts.items()):
        print(f"  - {seg_type}: {count}")
    print(f"\nWolof examples extracted: {total_examples}")
    print(f"\nOutput saved to: {output_path.absolute()}")
    print(f"  - wolof_training_dataset.json (all segments)")
    print(f"  - wolof_examples_dataset.json (Wolof sentences only)")


def main():
    """Main function."""

    # Check if input directory exists
    if not Path(INPUT_DIR).exists():
        print(f"✗ Error: Directory '{INPUT_DIR}' not found!")
        print(f"  Make sure you've run the text extraction script first.")
        return

    try:
        process_all_texts()
        print("\n✓ Text segmentation completed!")

    except KeyboardInterrupt:
        print("\n\n⚠ Segmentation interrupted by user")
    except Exception as e:
        print(f"\n✗ An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()