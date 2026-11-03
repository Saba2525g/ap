"""Align existing templates with the new theme."""
import os
import re

# Simple textual replacements
REPLACEMENTS = {
    "background:#e2e8f0; color:var(--navy-900);": "background:var(--gray-100); color:var(--navy-900);",
    'class="btn" style="background:#fee2e2; color:#7f1d1d;"': 'class="btn btn-ghost" style="background:#fee2e2; color:#7f1d1d;"',
}

# Remove old book-card <style> from catalog
CATALOG_STYLE = """
<style>
  .book-card:hover { transform: translateY(-4px) !important; box-shadow: 0 8px 24px rgba(15,23,42,.12) !important; }
</style>
"""

files = [
    "app/templates/books/catalog.html",
    "app/templates/books/detail.html",
    "app/templates/books/form.html",
    "app/templates/books/manage.html",
    "app/templates/borrowings/my.html",
    "app/templates/borrowings/requests.html",
    "app/templates/borrowings/all.html",
    "app/templates/notifications/list.html",
    "app/templates/admin/audit.html",
]

for path in files:
    if not os.path.exists(path):
        continue
    with open(path, encoding="utf-8") as f:
        content = f.read()
    original = content
    for old, new in REPLACEMENTS.items():
        content = content.replace(old, new)
    if path.endswith("catalog.html"):
        content = content.replace(CATALOG_STYLE, "")
    if content != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"UPDATED {path}")

print("\nDONE: theme alignment applied.")
