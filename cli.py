import os
import argparse
import sys
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()


def _get_pinecone():
    return Pinecone(api_key=os.getenv("PINECONE_API_KEY"))


def _index_name():
    return os.getenv("PINECONE_INDEX_NAME", "aristo-docs")


def cmd_research(args):
    from graph.research_graph import build_research_graph

    graph = build_research_graph(debug=args.verbose)
    config = {"configurable": {"thread_id": args.thread_id}}

    result = graph.invoke(
        {"query": args.query, "max_iterations": args.max_iterations},
        config,
    )

    print(result.get("final_answer", "No answer produced"))


def cmd_ingest(args):
    from ingestion.pipeline import ingest

    result = ingest(args.pdf)
    print(f"\nIngested: {result['document_title']}")
    print(f"Sections: {result['sections']}")
    print(f"Chunks: {result['chunks']}")


def cmd_status(args):
    pc = _get_pinecone()
    name = _index_name()

    indexes = [idx.name for idx in pc.list_indexes()]
    print(f"Available indexes: {', '.join(indexes)}")

    if name not in indexes:
        print(f"\nIndex '{name}' does not exist. Run 'aristo ingest <pdf>' first.")
        return

    index = pc.Index(name)
    stats = index.describe_index_stats()

    print(f"\nIndex: {name}")
    print(f"Dimension: {stats.dimension}")
    print(f"Metric: {stats.metric}")
    print(f"Total vectors: {stats.total_vector_count}")

    for ns, ns_stats in stats.namespaces.items():
        label = ns if ns else "(default)"
        print(f"  Namespace '{label}': {ns_stats.vector_count} vectors")


def cmd_list(args):
    pc = _get_pinecone()
    name = _index_name()
    index = pc.Index(name)

    docs = {}
    for match in index.query(vector=[0.0] * 384, top_k=10000, include_metadata=True).matches:
        meta = match.metadata
        title = meta.get("document_title", "Unknown")
        if title not in docs:
            docs[title] = {"chunks": 0, "sections": set(), "pages": set()}
        docs[title]["chunks"] += 1
        if meta.get("section"):
            docs[title]["sections"].add(meta["section"])
        if meta.get("pages"):
            for p in meta["pages"]:
                docs[title]["pages"].add(p)

    if not docs:
        print("No documents indexed.")
        return

    print(f"Indexed documents ({len(docs)} total):\n")
    for title, info in docs.items():
        print(f"  {title}")
        print(f"    Chunks: {info['chunks']}")
        print(f"    Sections: {len(info['sections'])}")
        pages = sorted(info["pages"], key=lambda x: int(x)) if info["pages"] else []
        print(f"    Pages: {', '.join(pages) if pages else 'N/A'}")
        print()


def build_parser():
    parser = argparse.ArgumentParser(
        prog="aristo",
        description="Autonomous research agent with document ingestion and retrieval.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    research_parser = subparsers.add_parser("research", help="Run research on a query")
    research_parser.add_argument("query", help="Research query")
    research_parser.add_argument("-n", "--max-iterations", type=int, default=3, help="Max research iterations (default: 3)")
    research_parser.add_argument("-t", "--thread-id", default="cli-run", help="Thread ID for state persistence (default: cli-run)")
    research_parser.add_argument("-v", "--verbose", action="store_true", help="Show state monitoring during research")

    subparsers.add_parser("ingest", help="Ingest a PDF into the knowledge base").add_argument("pdf", help="Path to PDF file")
    subparsers.add_parser("status", help="Show vector store index stats")
    subparsers.add_parser("list", help="List indexed documents")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "research": cmd_research,
        "ingest": cmd_ingest,
        "status": cmd_status,
        "list": cmd_list,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
