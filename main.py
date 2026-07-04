# Copyright (c) 2026 MyCompany LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Root CLI entrypoint for ExamDigest.

Usage:
    python main.py --exam psc
    python main.py --exam ssc
    python main.py --exam railway
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
    args = parser.parse_args()

    if args.reset_memory:
        path = reset_memory()
        print(f"✅  Memory cleared: {path}")

    if args.exam:
        run_pipeline(args.exam)
        print("✅  Workflow completed successfully!")
    elif not args.reset_memory:
        parser.print_help()


if __name__ == "__main__":
    main()
