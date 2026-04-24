import json
from pathlib import Path
from typing import List, Dict
import chromadb
from chromadb.config import Settings

"""
Wolof Local RAG System
Creates a permanent vector database of all Wolof linguistic resources
"""

# Configuration
SEGMENTED_DIR = "Wolof_Segmented"
RAG_DB_PATH = "wolof_rag_db"
COLLECTION_NAME = "wolof_linguistics"


class WolofRAG:
    """Build and query local RAG system for Wolof linguistics."""

    def __init__(self, db_path: str = RAG_DB_PATH):
        """Initialize ChromaDB client."""
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = None

    def create_collection(self):
        """Create or get collection."""
        print("Creating/loading vector database...")

        # Delete existing collection if it exists
        try:
            self.client.delete_collection(COLLECTION_NAME)
            print("  Deleted existing collection")
        except:
            pass

        # Create new collection
        self.collection = self.client.create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "Wolof linguistic resources"}
        )
        print(f"  ✓ Collection '{COLLECTION_NAME}' ready")

    def load_segments(self) -> List[Dict]:
        """Load all segmented data."""
        print("\nLoading segments...")

        segments = []
        json_file = Path(SEGMENTED_DIR) / "wolof_training_dataset.json"

        if not json_file.exists():
            print(f"  ✗ Error: {json_file} not found!")
            return []

        with open(json_file, 'r', encoding='utf-8') as f:
            segments = json.load(f)

        print(f"  ✓ Loaded {len(segments)} segments")
        return segments

    def add_segments_to_db(self, segments: List[Dict]):
        """Add segments to vector database."""
        print("\nAdding segments to vector database...")

        batch_size = 100
        total = len(segments)

        for i in range(0, total, batch_size):
            batch = segments[i:i + batch_size]

            # Prepare data for ChromaDB
            documents = []
            metadatas = []
            ids = []

            for j, seg in enumerate(batch):
                doc_id = f"seg_{i + j}"

                documents.append(seg["text"])
                metadatas.append({
                    "type": seg["type"],
                    "category": seg["category"],
                    "source": seg["source_file"],
                    "length": seg["length"],
                    "word_count": seg["word_count"]
                })
                ids.append(doc_id)

            # Add to collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )

            print(f"  Progress: {min(i + batch_size, total)}/{total}")

        print(f"  ✓ All segments added to database")

    def query(self, query_text: str, n_results: int = 5,
              filter_type: str = None) -> List[Dict]:
        """Query the database."""

        where_filter = None
        if filter_type:
            where_filter = {"type": filter_type}

        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            where=where_filter
        )

        # Format results
        formatted = []
        for i in range(len(results['documents'][0])):
            formatted.append({
                "text": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i]
            })

        return formatted

    def get_stats(self) -> Dict:
        """Get database statistics."""
        count = self.collection.count()
        return {"total_segments": count}


def build_rag_system():
    """Build the complete RAG system."""
    print("=" * 60)
    print("BUILDING WOLOF LOCAL RAG SYSTEM")
    print("=" * 60)

    # Initialize RAG
    rag = WolofRAG()

    # Create collection
    rag.create_collection()

    # Load segments
    segments = rag.load_segments()

    if not segments:
        print("\n✗ No segments found. Run segment_texts.py first.")
        return None

    # Add to database
    rag.add_segments_to_db(segments)

    # Get stats
    stats = rag.get_stats()

    print("\n" + "=" * 60)
    print("RAG SYSTEM BUILT SUCCESSFULLY")
    print("=" * 60)
    print(f"Total segments in database: {stats['total_segments']}")
    print(f"Database location: {Path(RAG_DB_PATH).absolute()}")

    return rag


def demo_queries(rag: WolofRAG):
    """Test the RAG system with sample queries."""
    print("\n" + "=" * 60)
    print("TESTING RAG SYSTEM")
    print("=" * 60)

    test_queries = [
        "verb conjugation",
        "noun classes",
        "phonology vowel harmony",
        "clitic pronouns"
    ]

    for query in test_queries:
        print(f"\nQuery: '{query}'")
        results = rag.query(query, n_results=3)

        for i, result in enumerate(results, 1):
            print(f"\n  Result {i}:")
            print(f"    Type: {result['metadata']['type']}")
            print(f"    Source: {result['metadata']['source']}")
            print(f"    Category: {result['metadata']['category']}")
            print(f"    Preview: {result['text'][:150]}...")


def main():
    """Main function."""

    # Check if segmented data exists
    if not Path(SEGMENTED_DIR).exists():
        print(f"✗ Error: {SEGMENTED_DIR} not found!")
        print("  Run segment_texts.py first to create segmented data.")
        return

    # Build RAG system
    rag = build_rag_system()

    if rag:
        # Test with sample queries
        demo_queries(rag)

        print("\n" + "=" * 60)
        print("RAG SYSTEM READY FOR USE")
        print("=" * 60)
        print("\nYou can now:")
        print("  1. Query the system with any linguistic question")
        print("  2. Use it to build NLP tools")
        print("  3. Extract rules for tokenization, morphology, etc.")
        print(f"\nDatabase saved permanently at: {Path(RAG_DB_PATH).absolute()}")


if __name__ == "__main__":
    main()