"""Remove UTF-8 BOM from all .py files in the project."""
import os
import sys

BOM = b"\xef\xbb\xbf"
count = 0

for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in ("__pycache__", ".venv", ".git", "node_modules")]
    for fn in files:
        if not fn.endswith(".py"):
            continue
        path = os.path.join(root, fn)
        with open(path, "rb") as f:
            raw = f.read()
        if raw.startswith(BOM):
            with open(path, "wb") as f:
                f.write(raw[3:])
            print(f"FIXED {path}")
            count += 1

print(f"\nDone. Stripped BOM from {count} files.")
