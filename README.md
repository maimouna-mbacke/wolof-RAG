# wolof-RAG

**Local Retrieval-Augmented Generation system for Wolof linguistics research**

> A semantic search engine over a curated corpus of Wolof linguistic resources — grammar books, academic papers, and dissertations — powered by ChromaDB and a custom NLP pipeline, with an optional LLM generation layer via the Anthropic API.

---

## Overview

`wolof-RAG` is a fully local RAG system built for **Wolof**, a Niger-Congo language spoken by approximately 10 million people in Senegal and The Gambia, and severely under-resourced in NLP.

The system enables semantic search over linguistically segmented chunks extracted from primary Wolof research sources, covering phonology, morphology, syntax, semantics, pragmatics, and more.

This project is a companion to [`wolof-nlp`](https://github.com/maimouna-mbacke/wolof-nlp), providing the retrieval backbone for knowledge-grounded Wolof NLP applications.

---

## Architecture

The system is built as a sequential pipeline of five stages:

```
Wolof_Resources/          ← Primary source PDFs (grammar books, papers, dissertations)
        │
        ▼
extract_text.py           ← PDF text extraction (PyPDF2), page-by-page
        │
        ▼
Wolof_Resources_Text/     ← Raw .txt files, one per source
        │
        ▼
segment_texts.py          ← Chunking pipeline: clean → detect type → split
        │
        ▼
Wolof_Segmented/          ← Typed, categorized JSON segments
   wolof_training_dataset.json   (master flat dataset — input to ChromaDB)
   wolof_examples_dataset.json   (Wolof sentence examples only)
        │
        ▼
extract_knowledge.py      ← Keyword-based extraction into 13 linguistic categories
        │
        ▼
Wolof_Knowledge_Base/     ← Structured JSON files per linguistic category
        │
        ▼
build_rag.py              ← ChromaDB vector indexing (batched, 100 docs/batch)
        │
        ▼
wolof_rag_db/             ← Persistent ChromaDB vector store
        │
        ▼
wolof_query.py            ← Semantic search interface (CLI + importable class)
        │
        ▼
wolof_assistant.py        ← RAG retrieval + Anthropic LLM generation + memory
        │
        ▼
chat_app.py               ← Streamlit conversational interface
```

Additionally, `Wolof_Morphology_Patterns.py` extracts morphological patterns (suffixes, verb paradigms, clitics, reduplication) from the examples dataset independently of the main RAG pipeline.

---

## Segment Types

The segmentation pipeline (`segment_texts.py`) classifies each chunk into one of five types:

| Type | Description |
|---|---|
| `grammar_rule` | Paragraphs containing explicit linguistic terminology |
| `example` | Sentences containing Wolof grammatical markers |
| `vocabulary` | Entries matching `word - definition` or `word: definition` patterns |
| `section_header` | Short headings (< 100 chars, all-caps, or numbered) |
| `paragraph` | General text not matching other types |

---

## Linguistic Categories (Knowledge Base)

`extract_knowledge.py` organizes segments into 13 structured JSON files:

| File | Content |
|---|---|
| `verbs.json` | Copula, conjugation paradigms, tense, aspect, mood |
| `nouns.json` | Noun classes, pluralization, derivation |
| `pronouns.json` | Subject clitics, object pronouns, possessives, demonstratives |
| `adjectives.json` | Agreement, position |
| `morphology.json` | Affixes, derivation, compounding, reduplication |
| `syntax.json` | Word order, questions, negation, focus, relative clauses |
| `phonology.json` | Vowels, consonants, vowel harmony, syllable structure |
| `clitics.json` | Subject and object clitics, positional patterns |
| `particles.json` | Tense, aspect, and focus particles |
| `vocabulary.json` | Core vocabulary entries |
| `orthography.json` | CLAD standard spelling rules |
| `semantics.json` | Lexical meanings, idioms |
| `pragmatics.json` | Politeness, discourse structure |

> **Note on categorization:** Detection is keyword-based and therefore approximate. Some segments may be miscategorized, particularly for short Wolof particles that overlap with common English strings (e.g. `di`, `mu`, `bu`). This is a known limitation and an area for future improvement.

---

## Primary Sources

The following published works were used to build the knowledge base. They are **not distributed** in this repository due to copyright. Most are accessible through university libraries or institutional open-access repositories.

| Source | Category |
|---|---|
| Robert, S. (2021). *Wolof Grammatical Sketch* | Grammar Books |
| Stewart, J. *Notes on Wolof Grammar* | Grammar Books |
| Peace Corps (1980). *Wolof Practical Course* | Grammar Books |
| Diouf, J.-L. *Grammaire du Wolof contemporain* | Grammar Books |
| Dye, C. (2015). *Vowel Harmony and Coarticulation in Wolof*. Dissertation | Dissertations |
| Torrence, H. *Chapter 1: Introduction to Wolof Syntax*. Dissertation | Dissertations |
| Torrence, H. *Chapter 3: Relative Clauses in Wolof*. Dissertation | Dissertations |
| Martinovic, M. *Locatives and Progressives in Wolof* | Academic Papers |
| *Noun Classes and Grammatical Gender in Wolof* | Academic Papers |
| *Head Splitting at the Clausal Periphery* | Academic Papers |
| *Second Occurrence Focus in Wolof* | Academic Papers |
| *Topic, Comment and Copular Sentences in Wolof* | Academic Papers |
| *Exploring Wolofal NLP* | Academic Papers |
| *SENCORPUS Paper* | Corpora |

---

## Installation

```bash
git clone https://github.com/maimouna-mbacke/wolof-RAG
cd wolof-RAG
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## How to Rebuild the Database

Since the data files are not distributed, you need to run the pipeline from your own copies of the source PDFs.

**Step 1 — Organize your source PDFs:**
```
Wolof_Resources/
├── Grammar_Books/
├── Academic_Papers/
├── Dissertations/
├── Corpora/
└── Progressives_Locatives/
```

**Step 2 — Extract text from PDFs:**
```bash
python3 extract_text.py
# Output: Wolof_Resources_Text/
```

**Step 3 — Segment the extracted text:**
```bash
python3 segment_texts.py
# Output: Wolof_Segmented/wolof_training_dataset.json
```

**Step 4 — (Optional) Build structured knowledge base:**
```bash
python3 extract_knowledge.py
# Output: Wolof_Knowledge_Base/
```

**Step 5 — Build the ChromaDB vector index:**
```bash
python3 build_rag.py
# Output: wolof_rag_db/  (persistent vector store)
```

**Step 6 — (Optional) Extract morphological patterns:**
```bash
python3 Wolof_Morphology_Patterns.py
# Requires: Wolof_Segmented/wolof_examples_dataset.json
# Output: Wolof_Morphology_Patterns/
```

---

## Usage

### Query via CLI (retrieval only — no API key needed)

```bash
python3 wolof_query.py
```

```
WOLOF RAG QUERY INTERFACE
Database loaded: 5585 segments

Query: verb conjugation
Query: grammar: negation
Query: examples: noun classes
Query: vocab: buur
```

### Query with LLM generation (requires Anthropic API key)

```bash
export ANTHROPIC_API_KEY="your-key-here"
python3 wolof_assistant.py
```

The assistant retrieves 5 relevant chunks from ChromaDB, passes them to Claude as context, and returns a structured answer in the language of the question (French or English). Conversation history is maintained across turns (last 6 exchanges).

### Streamlit chat interface

```bash
export ANTHROPIC_API_KEY="your-key-here"
streamlit run chat_app.py
```

---

## Query Types

```bash
# General semantic search (all segment types)
Query: how does vowel harmony work in Wolof?

# Grammar rules only
Query: grammar: TAM system

# Annotated sentence examples only
Query: examples: clitic pronouns

# Vocabulary lookup
Query: vocab: dafa
```

---

## Project Status

| Component | Status |
|---|---|
| PDF extraction pipeline |  Complete |
| Text segmentation pipeline |  Complete |
| ChromaDB vector store |  Complete |
| Structured knowledge base (13 categories) |  Complete |
| Morphological pattern extraction |  Complete |
| CLI query interface |  Complete |
| Streamlit chat interface |  Complete |
| LLM generation layer (Anthropic API) |  Complete |
| Open-source LLM alternative (Groq) |  Planned |
| Public dataset release |  Pending rights clearance |

---

## Relation to wolof-nlp

This project provides the **retrieval layer** that complements [`wolof-nlp`](https://github.com/maimouna-mbacke/wolof-nlp):

```
wolof-nlp    →  process and analyze Wolof text programmatically
                (tokenization, POS tagging, NER, sentiment, glossing)

wolof-RAG    →  retrieve and ground Wolof linguistic knowledge
                (semantic search over primary research sources)
```

Together they form a research infrastructure for low-resource Wolof NLP.

---

## Author

**Maimouna MBACKE**
[github.com/maimouna-mbacke](https://github.com/maimouna-mbacke)

---

## License

MIT License — see [LICENSE](LICENSE)

---

## Citation

If you use this pipeline in your research, please consider citing the primary sources listed above.
