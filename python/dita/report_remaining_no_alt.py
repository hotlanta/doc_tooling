#!/usr/bin/env python3
"""
Generate simple report of images still without alt.
Outputs to console and report_no_alt.txt
"""

from pathlib import Path
from lxml import etree
import sys

SKIP_PARTS = {'out', 'temp', '.git', '.svn', 'node_modules', '__pycache__', 'dist', 'build'}

def report_no_alt(filepath: Path, output_file):
    try:
        tree = etree.parse(str(filepath))
        images = tree.xpath("//*[local-name()='image'][not(*[local-name()='alt'])]")
        if not images:
            return 0

        output_file.write(f"\nFile: {filepath.relative_to(Path.cwd())}\n")
        count = 0
        for img in images:
            href = img.get('href', 'no href')
            context = ""
            prev = img.getprevious()
            if prev is not None and (prev.tag.endswith('}p') or prev.tag == 'p'):
                context = ''.join(prev.itertext()).strip()[:80] + "..."
            output_file.write(f"  - href: {href}\n    Preceding p: {context}\n")
            count += 1
        return count
    except Exception as e:
        print(f"Error in {filepath}: {e}")
        return 0

def main():
    folder = Path.cwd()
    output_path = folder / "report_no_alt.txt"
    total_no_alt = 0

    with open(output_path, "w", encoding="utf-8") as out:
        out.write("Remaining images without <alt>\n")
        out.write("="*50 + "\n")

        dita_files = list(folder.rglob("*.dita")) + list(folder.rglob("*.xml"))
        for f in dita_files:
            if any(part in SKIP_PARTS for part in f.parts):
                continue
            count = report_no_alt(f, out)
            total_no_alt += count

    print(f"\nReport saved to: {output_path}")
    print(f"Total remaining images without alt: {total_no_alt}")

if __name__ == "__main__":
    main()