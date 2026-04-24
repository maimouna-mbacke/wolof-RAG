# wolof_assistant.py

import os
from wolof_query import WolofQuery

SYSTEM_PROMPT = """You are an expert linguist specializing in Wolof, a Niger-Congo language spoken in Senegal and The Gambia.

You have access to a curated knowledge base of Wolof linguistic resources including grammar books, academic papers, and dissertations.

Your role:
- Answer questions about Wolof grammar, phonology, morphology, syntax, vocabulary, and usage
- Base your answers strictly on the retrieved context provided
- Give clear, structured, pedagogically useful answers
- Include Wolof examples with French/English glosses when relevant
- If the context is insufficient, say so honestly rather than hallucinating

Always respond in the same language as the user's question (French or English).
"""


class WolofAssistant:
    """
    Wolof Assistant — RAG retrieval with optional LLM generation.

    Modes:
      - With ANTHROPIC_API_KEY set: retrieval + Claude generation + memory
      - Without API key: retrieval only, returns formatted chunks
    """

    def __init__(self):
        self.rag = WolofQuery()
        self.memory = []
        self.llm_enabled = False

        api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
        if api_key:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=api_key)
                self.llm_enabled = True
                print("✓ LLM mode enabled (Anthropic API)")
            except ImportError:
                print("⚠ anthropic package not installed — running in retrieval-only mode")
        else:
            print("ℹ No ANTHROPIC_API_KEY found — running in retrieval-only mode")

    def _format_retrieval_only(self, results: list, question: str) -> str:
        """Format raw retrieval results cleanly when no LLM is available."""
        lines = [f"**Retrieval results for:** _{question}_\n"]
        for i, res in enumerate(results, 1):
            lines.append(f"**[{i}] {res['source']}** — {res['type']} | relevance: {res['relevance']:.2f}")
            lines.append(res['text'][:400])
            lines.append("")
        lines.append("---")
        lines.append("*LLM generation not enabled. Set ANTHROPIC_API_KEY to get synthesized answers.*")
        return "\n".join(lines)

    def answer(self, question: str) -> str:
        """Answer using RAG retrieval, with LLM generation if API key is set."""

        # Step 1 — Retrieve relevant chunks
        results = self.rag.search(question, n_results=5)

        if not results:
            return "No relevant information found in the knowledge base for this query."

        # Step 2 — Retrieval-only mode
        if not self.llm_enabled:
            return self._format_retrieval_only(results, question)

        # Step 3 — LLM mode: build context
        context_parts = []
        for i, res in enumerate(results, 1):
            context_parts.append(
                f"[Source {i} — {res['type']} | {res['source']} | {res['category']}]\n{res['text']}"
            )
        context = "\n\n---\n\n".join(context_parts)

        # Step 4 — Build messages with memory
        messages = list(self.memory[-6:])
        messages.append({
            "role": "user",
            "content": (
                f"Retrieved context from the Wolof linguistics knowledge base:\n\n"
                f"{context}\n\n---\n\n"
                f"Based on the context above, please answer this question:\n{question}"
            )
        })

        # Step 5 — Call Claude
        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                system=SYSTEM_PROMPT,
                messages=messages
            )
            answer_text = response.content[0].text
        except Exception as e:
            return f"LLM error: {e}\n\n" + self._format_retrieval_only(results, question)

        # Step 6 — Store in memory
        self.memory.append({"role": "user", "content": question})
        self.memory.append({"role": "assistant", "content": answer_text})

        return answer_text


def interactive_cli():
    """CLI interface for testing without Streamlit."""
    print("=" * 60)
    print("WOLOF AI ASSISTANT")
    print("=" * 60)
    print("Type 'quit' to exit\n")

    try:
        assistant = WolofAssistant()
        mode = "RAG + LLM" if assistant.llm_enabled else "Retrieval only"
        print(f"✓ System ready — mode: {mode}\n")
    except Exception as e:
        print(f"✗ Initialization error: {e}")
        return

    while True:
        question = input("You: ").strip()
        if not question:
            continue
        if question.lower() in ["quit", "exit", "q"]:
            break
        print("\nAssistant:", assistant.answer(question), "\n")


if __name__ == "__main__":
    interactive_cli()
