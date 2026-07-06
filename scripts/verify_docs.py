import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
required_files = [
    root / "README.md",
    root / "SPEC.md",
    root / "main.py",
    root / "cli" / "main.py",
    root / "server" / "app.py",
    root / "streamlit_app" / "app.py",
]

missing = [str(path.relative_to(root)) for path in required_files if not path.exists()]
if missing:
    print("Missing required documentation-related files:")
    for item in missing:
        print(f"- {item}")
    sys.exit(1)

readme = (root / "README.md").read_text(encoding="utf-8")
spec = (root / "SPEC.md").read_text(encoding="utf-8")

checks = [
    ("README mentions root CLI entrypoint", "python main.py" in readme),
    ("README mentions module CLI entrypoint", "python cli/main.py" in readme),
    ("SPEC mentions root CLI entrypoint", "main.py" in spec and "root CLI driver" in spec),
    ("SPEC mentions documentation maintenance", "Documentation Maintenance" in spec),
]

failed = [name for name, passed in checks if not passed]
if failed:
    print("Documentation verification failed:")
    for item in failed:
        print(f"- {item}")
    sys.exit(1)

print("Documentation verification passed.")
