"""Root CLI entrypoint for ExamDigest.

Usage:
    python main.py --exam psc
    python main.py --exam ssc
    python main.py --exam railway
    python main.py --exam psc --data-mode live
    python main.py --reset-memory
    python main.py --exam psc --reset-memory
"""

import sys
import os

# Ensure the project root is on sys.path regardless of where this is called from
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cli.main import run_pipeline, reset_memory
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="ExamDigest — Current Affairs Digest Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --exam psc
  python main.py --exam ssc
  python main.py --exam railway
  python main.py --exam psc --data-mode live
  python main.py --reset-memory
  python main.py --exam psc --reset-memory
        """,
    )
    parser.add_argument(
        "--exam",
        choices=["psc", "ssc", "railway"],
        help="Target exam type (psc, ssc, railway)",
    )
    parser.add_argument(
        "--reset-memory",
        action="store_true",
        help="Clear the seen_topics.json deduplication memory",
    )
    parser.add_argument(
        "--data-mode",
        choices=["mock", "live"],
        default=os.getenv("DATA_MODE", "mock"),
        help="Use deterministic mock data or best-effort free live sources",
    )
    args = parser.parse_args()

    if args.reset_memory:
        path = reset_memory()
        print(f"✅  Memory cleared: {path}")

    if args.exam:
        run_pipeline(args.exam, data_mode=args.data_mode)
        print("✅  Workflow completed successfully!")
    elif not args.reset_memory:
        parser.print_help()


if __name__ == "__main__":
    main()
