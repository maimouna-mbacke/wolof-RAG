import chromadb
from chromadb.config import Settings
from pathlib import Path
from typing import List, Dict, Optional

"""
Wolof RAG Query Interface
Query your Wolof linguistics database
"""

RAG_DB_PATH = "wolof_rag_db"
COLLECTION_NAME = "wolof_linguistics"


class WolofQuery:
    """Query interface for Wolof RAG system."""

    def __init__(self, db_path: str = RAG_DB_PATH):
        """Initialize connection to database."""
        if not Path(db_path).exists():
            raise FileNotFoundError(
                f"Database not found at {db_path}. Run build_rag.py first."
            )

        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.client.get_collection(COLLECTION_NAME)

    def search(self, query: str, n_results: int = 10,
               segment_type: Optional[str] = None,
               category: Optional[str] = None) -> List[Dict]:
        """
        Search the database.

        Args:
            query: Search query
            n_results: Number of results to return
            segment_type: Filter by type (grammar_rule, example, vocabulary, etc.)
            category: Filter by category (Grammar_Books, Academic_Papers, etc.)
        """
        where_filter = {}
        if segment_type:
            where_filter["type"] = segment_type
        if category:
            where_filter["category"] = category

        where = where_filter if where_filter else None

        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )

        formatted = []
        for i in range(len(results['documents'][0])):
            formatted.append({
                "text": results['documents'][0][i],
                "type": results['metadatas'][0][i]['type'],
                "category": results['metadatas'][0][i]['category'],
                "source": results['metadatas'][0][i]['source'],
                "relevance": 1 - results['distances'][0][i]  # Convert distance to relevance
            })

        return formatted

    def get_grammar_rules(self, topic: str, n_results: int = 5) -> List[Dict]:
        """Get grammar rules about a specific topic."""
        return self.search(topic, n_results, segment_type="grammar_rule")

    def get_examples(self, topic: str, n_results: int = 10) -> List[Dict]:
        """Get examples related to a topic."""
        return self.search(topic, n_results, segment_type="example")

    def get_vocabulary(self, topic: str, n_results: int = 10) -> List[Dict]:
        """Get vocabulary entries."""
        return self.search(topic, n_results, segment_type="vocabulary")

    def stats(self) -> Dict:
        """Get database statistics."""
        return {
            "total_segments": self.collection.count()
        }


def interactive_query():
    """Interactive query interface."""
    print("=" * 60)
    print("WOLOF RAG QUERY INTERFACE")
    print("=" * 60)

    try:
        query_engine = WolofQuery()
        stats = query_engine.stats()
        print(f"Database loaded: {stats['total_segments']} segments")
        print("\nCommands:")
        print("  - Type your question")
        print("  - 'grammar: <topic>' - Get grammar rules")
        print("  - 'examples: <topic>' - Get examples")
        print("  - 'vocab: <word>' - Get vocabulary")
        print("  - 'quit' - Exit")
        print("=" * 60)

        while True:
            query = input("\nQuery: ").strip()

            if query.lower() in ['quit', 'exit', 'q']:
                break

            if not query:
                continue

            # Parse command
            if query.startswith("grammar:"):
                topic = query.replace("grammar:", "").strip()
                results = query_engine.get_grammar_rules(topic)
            elif query.startswith("examples:"):
                topic = query.replace("examples:", "").strip()
                results = query_engine.get_examples(topic)
            elif query.startswith("vocab:"):
                word = query.replace("vocab:", "").strip()
                results = query_engine.get_vocabulary(word)
            else:
                results = query_engine.search(query)

            # Display results
            print(f"\nFound {len(results)} results:")
            print("-" * 60)

            for i, result in enumerate(results, 1):
                print(f"\n[{i}] Relevance: {result['relevance']:.2f}")
                print(f"Type: {result['type']} | Source: {result['source']}")
                print(f"Text: {result['text'][:300]}...")

                if i >= 3:  # Show top 3 by default
                    if i < len(results):
                        show_more = input("\nShow more? (y/n): ").strip().lower()
                        if show_more != 'y':
                            break

    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("Run build_rag.py first to create the database.")
    except KeyboardInterrupt:
        print("\n\nExiting...")


def main():
    """Main function."""
    interactive_query()


if __name__ == "__main__":
    main()