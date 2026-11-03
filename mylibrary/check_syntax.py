import ast
import os
import sys

bad = []
for root, dirs, files in os.walk("app"):
    dirs[:] = [d for d in dirs if d not in ("__pycache__", ".venv")]
    for fn in files:
        if not fn.endswith(".py"):
            continue
        path = os.path.join(root, fn)
        try:
            with open(path, encoding="utf-8") as f:
                ast.parse(f.read())
        except SyntaxError as e:
            bad.append((path, e.lineno, e.msg))

if not bad:
    print("OK: all python files are syntactically valid")
else:
    print(f"FOUND {len(bad)} files with syntax errors:")
    for path, lineno, msg in bad:
        print(f"  {path}:{lineno}: {msg}")
