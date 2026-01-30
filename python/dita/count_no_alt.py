#!/usr/bin/env python3
"""
Count <image> elements and how many still lack <alt> in DITA files.
"""

from pathlib import Path
from lxml import etree
import sys

SKIP_PARTS = {
    'out', 'temp', '.git', '.svn', 'node_modules', '__pycache__',
    'dist', 'build', 'target', 'bin', 'vendor', 'images', 'media'
}

def count_in_file(filepath: Path):
    try:
        tree = etree.parse(str(filepath))
        # All images
        all_images = len(tree.xpath("//*[local-name()='image']"))
        # Images without alt
        no_alt = len(tree.xpath("//*[local-name()='image'][not(*[local-name()='alt'])]"))
        return all_images, no_alt
    except Exception as e:
        print(f"Error in {filepath}: {e}")
        return 0, 0

def main():
    if len(sys.argv) == 1:
        folders = [Path.cwd()]
    else:
        folders = [Path(p) for p in sys.argv[1:]]

    total_images = 0
    total_no_alt = 0
    files_scanned = 0
    skipped = 0

    for folder in folders:
        print(f"\nScanning: {folder.resolve()}")
        dita_files = list(folder.rglob("*.dita")) + list(folder.rglob("*.xml"))

        for f in dita_files:
            if any(part in SKIP_PARTS for part in f.parts):
                skipped += 1
                continue

            files_scanned += 1
            img_count, no_alt_count = count_in_file(f)
            total_images += img_count
            total_no_alt += no_alt_count

    percent = round((total_no_alt / total_images * 100), 1) if total_images > 0 else 0

    print("\n" + "="*60)
    print("Summary:")
    print(f"  Files scanned     : {files_scanned}")
    print(f"  Files skipped     : {skipped}")
    print(f"  Total <image>     : {total_images}")
    print(f"  Still without <alt>: {total_no_alt} ({percent}%)")

if __name__ == "__main__":
    main()