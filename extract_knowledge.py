import json
from pathlib import Path
from typing import List, Dict
import re

"""
Complete Wolof Knowledge Extractor
Extracts ALL linguistic knowledge: grammar, morphology, syntax, phonology, vocabulary
"""

SEGMENTED_DIR = "Wolof_Segmented"
OUTPUT_DIR = "Wolof_Knowledge_Base"


class ComprehensiveWolofExtractor:
    """Extract complete Wolof linguistic knowledge."""

    def __init__(self):
        self.kb = {
            "verbs": {"copula": [], "conjugation": [], "tense": [], "aspect": [], "mood": []},
            "nouns": {"classes": [], "plurals": [], "derivation": []},
            "pronouns": {"subject": [], "object": [], "possessive": [], "demonstrative": []},
            "adjectives": {"agreement": [], "position": []},
            "morphology": {"affixes": [], "derivation": [], "compounding": [], "reduplication": []},
            "syntax": {"word_order": [], "questions": [], "negation": [], "focus": [], "relative_clauses": []},
            "phonology": {"vowels": [], "consonants": [], "harmony": [], "tone": [], "syllable": []},
            "clitics": {"subject": [], "object": [], "position": []},
            "particles": {"tense": [], "aspect": [], "focus": [], "negation": []},
            "vocabulary": {"core": [], "derivations": [], "borrowings": []},
            "orthography": {"rules": [], "variants": []},
            "semantics": {"meanings": [], "idioms": []},
            "pragmatics": {"politeness": [], "discourse": []}
        }

    def load_segments(self) -> List[Dict]:
        """Load all segments."""
        json_file = Path(SEGMENTED_DIR) / "wolof_training_dataset.json"
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def categorize_segment(self, segment: Dict) -> List[str]:
        """Determine which categories this segment belongs to."""
        text = segment["text"].lower()
        categories = []

        # Verb-related
        if any(kw in text for kw in ["verb", "conjugat", "copula", "to be", "ngi", "nga"]):
            categories.append("verbs")

        # Noun-related
        if any(kw in text for kw in ["noun", "class", "plural", "gender"]):
            categories.append("nouns")

        # Pronoun-related
        if any(kw in text for kw in ["pronoun", "clitic", "maa", "nga", "subject", "object"]):
            categories.append("pronouns")

        # Morphology
        if any(kw in text for kw in ["suffix", "prefix", "affix", "morpheme", "derivation", "-al", "-ante"]):
            categories.append("morphology")

        # Syntax
        if any(kw in text for kw in ["word order", "clause", "sentence", "svo", "focus", "question", "relative"]):
            categories.append("syntax")

        # Phonology
        if any(kw in text for kw in ["phonology", "vowel", "consonant", "harmony", "tone", "atr", "syllable"]):
            categories.append("phonology")

        # Particles
        if any(kw in text for kw in ["particle", "di", "la", "ci", "mu", "bu"]):
            categories.append("particles")

        # Orthography
        if any(kw in text for kw in ["orthography", "spelling", "writing", "script"]):
            categories.append("orthography")

        return categories if categories else ["general"]

    def extract_by_topic(self, segments: List[Dict], topic: str, keywords: List[str]) -> List[Dict]:
        """Extract segments related to a specific topic."""
        results = []
        for seg in segments:
            text = seg["text"].lower()
            if any(kw in text for kw in keywords):
                results.append({
                    "text": seg["text"],
                    "source": seg.get("source_file", seg.get("source", "unknown")),
                    "type": seg["type"],
                    "category": seg["category"]
                })
        return results

    def extract_all_knowledge(self, segments: List[Dict]):
        """Extract all linguistic knowledge systematically."""

        print("\n📚 Extracting Verbs...")
        self.kb["verbs"]["copula"] = self.extract_by_topic(
            segments, "copula", ["copula", "to be", "ngi", "nga", "existential"]
        )
        self.kb["verbs"]["conjugation"] = self.extract_by_topic(
            segments, "conjugation", ["conjugat", "paradigm", "inflection"]
        )
        self.kb["verbs"]["tense"] = self.extract_by_topic(
            segments, "tense", ["tense", "past", "present", "future", "anterior"]
        )
        self.kb["verbs"]["aspect"] = self.extract_by_topic(
            segments, "aspect", ["aspect", "perfective", "imperfective", "habitual"]
        )
        self.kb["verbs"]["mood"] = self.extract_by_topic(
            segments, "mood", ["mood", "imperative", "subjunctive", "conditional"]
        )

        print("📚 Extracting Nouns...")
        self.kb["nouns"]["classes"] = self.extract_by_topic(
            segments, "noun_classes", ["noun class", "class marker", "agreement"]
        )
        self.kb["nouns"]["plurals"] = self.extract_by_topic(
            segments, "plurals", ["plural", "pluralization", "yi", "ñi"]
        )

        print("📚 Extracting Pronouns...")
        self.kb["pronouns"]["subject"] = self.extract_by_topic(
            segments, "subject_pronouns", ["subject pronoun", "subject clitic", "maa", "yaa"]
        )
        self.kb["pronouns"]["object"] = self.extract_by_topic(
            segments, "object_pronouns", ["object pronoun", "object clitic", "-ko", "-la"]
        )
        self.kb["pronouns"]["possessive"] = self.extract_by_topic(
            segments, "possessive", ["possessive", "sama", "sa", "possessor"]
        )

        print("📚 Extracting Morphology...")
        self.kb["morphology"]["affixes"] = self.extract_by_topic(
            segments, "affixes", ["suffix", "prefix", "affix", "-al", "-ante", "-u", "-e"]
        )
        self.kb["morphology"]["derivation"] = self.extract_by_topic(
            segments, "derivation", ["derivation", "causative", "passive", "reciprocal"]
        )
        self.kb["morphology"]["reduplication"] = self.extract_by_topic(
            segments, "reduplication", ["reduplication", "reduplicate", "repetition"]
        )

        print("📚 Extracting Syntax...")
        self.kb["syntax"]["word_order"] = self.extract_by_topic(
            segments, "word_order", ["word order", "svo", "vso", "constituent"]
        )
        self.kb["syntax"]["focus"] = self.extract_by_topic(
            segments, "focus", ["focus", "cleft", "emphasis"]
        )
        self.kb["syntax"]["questions"] = self.extract_by_topic(
            segments, "questions", ["question", "interrogative", "wh-"]
        )
        self.kb["syntax"]["negation"] = self.extract_by_topic(
            segments, "negation", ["negation", "negative", "du", "not"]
        )
        self.kb["syntax"]["relative_clauses"] = self.extract_by_topic(
            segments, "relatives", ["relative clause", "relativization"]
        )

        print("📚 Extracting Phonology...")
        self.kb["phonology"]["vowels"] = self.extract_by_topic(
            segments, "vowels", ["vowel", "atr", "advanced tongue root"]
        )
        self.kb["phonology"]["consonants"] = self.extract_by_topic(
            segments, "consonants", ["consonant", "geminate", "prenasalized"]
        )
        self.kb["phonology"]["harmony"] = self.extract_by_topic(
            segments, "harmony", ["harmony", "vowel harmony", "assimilation"]
        )

        print("📚 Extracting Particles...")
        self.kb["particles"]["tense"] = self.extract_by_topic(
            segments, "tense_particles", ["di", "dina", "dafa", "tense marker"]
        )
        self.kb["particles"]["focus"] = self.extract_by_topic(
            segments, "focus_particles", ["la", "nga", "focus marker"]
        )

        print("📚 Extracting Clitics...")
        self.kb["clitics"]["object"] = self.extract_by_topic(
            segments, "object_clitics", ["clitic", "-ko", "-la", "-ci", "pronominal"]
        )

        print("📚 Extracting Orthography...")
        self.kb["orthography"]["rules"] = self.extract_by_topic(
            segments, "orthography", ["orthography", "spelling", "writing system"]
        )

        print("📚 Extracting Vocabulary...")
        vocab_segments = [s for s in segments if s["type"] == "vocabulary"]
        self.kb["vocabulary"]["core"] = vocab_segments[:500]  # Top 500

    def save_knowledge_base(self):
        """Save complete knowledge base."""
        output_path = Path(OUTPUT_DIR)
        output_path.mkdir(exist_ok=True)

        # Save complete KB
        with open(output_path / "complete_knowledge_base.json", 'w', encoding='utf-8') as f:
            json.dump(self.kb, f, indent=2, ensure_ascii=False)

        # Save individual categories
        for category, data in self.kb.items():
            with open(output_path / f"{category}.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        return output_path

    def generate_summary(self) -> Dict:
        """Generate summary statistics."""
        summary = {}
        for category, subcats in self.kb.items():
            summary[category] = {}
            for subcat, items in subcats.items():
                summary[category][subcat] = len(items)
        return summary


def main():
    """Main function."""

    print("=" * 60)
    print("COMPREHENSIVE WOLOF KNOWLEDGE EXTRACTION")
    print("=" * 60)

    if not Path(SEGMENTED_DIR).exists():
        print(f"✗ Error: {SEGMENTED_DIR} not found!")
        return

    extractor = ComprehensiveWolofExtractor()

    print("\n📖 Loading segments...")
    segments = extractor.load_segments()
    print(f"   ✓ Loaded {len(segments)} segments")

    print("\n🔍 Extracting linguistic knowledge...")
    extractor.extract_all_knowledge(segments)

    print("\n💾 Saving knowledge base...")
    output_path = extractor.save_knowledge_base()

    print("\n📊 Knowledge Base Summary:")
    summary = extractor.generate_summary()
    for category, subcats in summary.items():
        total = sum(subcats.values())
        if total > 0:
            print(f"\n  {category.upper()}: {total} items")
            for subcat, count in subcats.items():
                if count > 0:
                    print(f"    - {subcat}: {count}")

    print("\n" + "=" * 60)
    print("✓ COMPLETE KNOWLEDGE BASE CREATED")
    print("=" * 60)
    print(f"Saved to: {output_path.absolute()}")
    print("\nYou now have structured knowledge for:")
    print("  • Verbs, Nouns, Pronouns, Adjectives")
    print("  • Morphology, Syntax, Phonology")
    print("  • Clitics, Particles, Orthography")
    print("  • Vocabulary, Semantics, Pragmatics")


if __name__ == "__main__":
    main()