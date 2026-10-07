"""
smoke_test_guide.py – Manual end-to-end smoke test for GoGuide RAG + LLM.

Usage:
  # Retrieval only (no model required):
  python -m backend.scripts.smoke_test_guide --retrieval-only

  # Full smoke test with Qwen (requires LLM_MODEL set):
  LLM_MODEL=Qwen/Qwen3-4B-Instruct-2507 python -m backend.scripts.smoke_test_guide
"""

import sys
import os
import argparse
import json

# Ensure backend/ is on path when invoked as a module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.app.rag.index import RAGIndex
from backend.app.schemas.llm import LLMContext, Evidence


TEST_QUERIES = [
    "What skills are needed for software development?",
    "What education paths lead to technology careers?",
    "Which careers are related to data and analytics?",
    "I like computers and mathematics. What careers could fit me?",
]


def run_retrieval_smoke(index: RAGIndex):
    print("\n" + "="*60)
    print("RETRIEVAL SMOKE TEST")
    print("="*60)

    for query in TEST_QUERIES:
        print(f"\nQuery: {query!r}")
        results = index.retrieve(query, top_k=3)

        if not results:
            print("  ⚠  No results returned (index may be empty or not built).")
            continue

        for i, r in enumerate(results, 1):
            print(f"  [{i}] id={r['document_id'][:8]}…  type={r['document_type']}")
            print(f"       title : {r['title'][:70]}")
            print(f"       score : {r['score']:.4f}")
            print(f"       source: {r['metadata'].get('source', 'unknown')}")
            synthetic = r['metadata'].get('status', '')
            if synthetic:
                print(f"       ⚠ SYNTHETIC_PROTOTYPE")
            assert r["document_id"], "document_id must not be empty"
            assert r["text"],        "text must not be empty"
            assert r["document_type"], "document_type must not be empty"
            assert "source" in r["metadata"], "metadata.source missing"

    print("\n✓ Retrieval smoke test passed.\n")


def run_full_smoke(index: RAGIndex):
    from backend.app.schemas.llm import LLMRequest
    from backend.app.services.llm_service import process_chat_request

    query = "I like computers and mathematics. What careers could fit me?"
    retrieved = index.retrieve(query, top_k=5)

    context = LLMContext(
        user_profile={"interests": ["computers", "mathematics"], "grade": 12},
        user_message=query,
        deterministic_results={
            "financial": {
                "total_cost": {"value": 400000, "source": "financial_solver", "authoritative": True},
                "is_feasible": {"value": True,  "source": "financial_solver", "authoritative": True},
            }
        },
        retrieved_documents=retrieved,
        constraints={},
        provenance=[Evidence(source="smoke_test", value="manual test context")],
    )

    print("\n" + "="*60)
    print("FULL LLM SMOKE TEST")
    print("="*60)
    print(f"Query : {query}")
    print(f"Docs  : {len(retrieved)} retrieved")
    print("Calling LLM ...\n")

    llm_req = LLMRequest(prompt=query, context=context)
    resp = process_chat_request(llm_req)

    print("─"*60)
    print("LLM Response:")
    print(resp.response_text)
    print("─"*60)
    print(f"Model : {resp.model}")
    print(f"At    : {resp.generated_at}")
    print("\n✓ Full smoke test complete.\n")


def main():
    parser = argparse.ArgumentParser(description="GoGuide RAG + LLM smoke test")
    parser.add_argument("--retrieval-only", action="store_true",
                        help="Run retrieval smoke test only (no model needed)")
    args = parser.parse_args()

    index = RAGIndex.get_instance()
    index.initialize()

    if not index._initialized:
        print("ERROR: RAG index not initialised. Run build_rag_index first:")
        print("  python -m backend.scripts.build_rag_index")
        sys.exit(1)

    print(f"Index loaded. Documents: {len(index.documents)}")

    run_retrieval_smoke(index)

    if not args.retrieval_only:
        run_full_smoke(index)
    else:
        print("Skipping LLM call (--retrieval-only flag set).")


if __name__ == "__main__":
    main()
