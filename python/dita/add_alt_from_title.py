#!/usr/bin/env python3
"""
Batch add <alt> to <image> in DITA topics:
- Priority 1: copy from <fig><title>
- Fallback A: cleaned filename from @href
- Fallback B: preceding <p> text (max 110 chars, min 15 chars)
"""

import sys
import re
from pathlib import Path
from lxml import etree

# === Configuration ===
DRY_RUN = False              # ← Start with True to preview!
CREATE_BACKUP = True
OVERWRITE_ORIGINAL = True
MAX_ALT_LENGTH = 110
MIN_FALLBACK_LENGTH = 15    # Ignore very short preceding text

SKIP_PARTS = {
    'out', 'temp', '.git', '.svn', 'node_modules', '__pycache__',
    'dist', 'build', 'target', 'bin', 'vendor', 'images', 'media'
}

def clean_filename(href: str) -> str:
    """ 'images/architecture-2026.svg' → 'Architecture 2026' """
    if not href:
        return "Image"
    name = Path(href).stem.replace("-", " ").replace("_", " ")
    name = re.sub(r'\s+', ' ', name).strip()
    return ' '.join(word.capitalize() for word in name.split()) or "Image"

def get_preceding_p_text(image):
    """Get text from immediately preceding <p>, if meaningful"""
    prev = image.getprevious()
    if prev is None:
        return None

    # Only consider direct preceding <p>
    if not (prev.tag.endswith('}p') or prev.tag == 'p'):
        return None

    text = ''.join(prev.itertext()).strip()
    if len(text) < MIN_FALLBACK_LENGTH:
        return None

    return text[:MAX_ALT_LENGTH] + ("..." if len(text) > MAX_ALT_LENGTH else "")

def process_file(filepath: Path):
    try:
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(str(filepath), parser)
        root = tree.getroot()

        modified = False

        for image in root.xpath("//*[local-name()='image'][not(*[local-name()='alt'])]"):
            alt = etree.Element("alt")
            alt_text = None
            source = "unknown"
            href = image.get('href', 'no-href')

            # 1. Highest priority: fig/title
            fig = image
            while fig is not None and not (fig.tag.endswith('}fig') or fig.tag == 'fig'):
                fig = fig.getparent()
            if fig is not None:
                title = fig.find(".//title")
                if title is not None:
                    title_text = ''.join(title.itertext()).strip()
                    if title_text:
                        alt_text = title_text[:MAX_ALT_LENGTH]
                        source = "title"

            # 2. If no title: try meaningful preceding <p> first
            if not alt_text:
                p_text = get_preceding_p_text(image)
                if p_text and len(p_text.strip()) >= MIN_FALLBACK_LENGTH:
                    alt_text = p_text
                    source = "preceding p"

            # 3. Always fall back to filename if nothing better
            if not alt_text:
                alt_text = clean_filename(href)
                source = "filename"

            # Final safety: at least something
            if not alt_text or alt_text.strip() == "":
                alt_text = "Icon"
                source = "default"

            # Add and log
            alt.text = alt_text
            image.insert(0, alt)
            modified = True
            print(f"  Added <alt> from {source}: '{alt_text[:60]}...' in {filepath.name} (href: {href})")

        if modified:
            if DRY_RUN:
                print(f"[DRY RUN] Would save changes to: {filepath}")
                return True  # count as "would modify"

            if CREATE_BACKUP:
                backup = filepath.with_suffix(filepath.suffix + ".bak")
                
                # If .bak already exists → delete or rename it to avoid WinError 183
                if backup.exists():
                    old_backup = backup.with_suffix(backup.suffix + ".old")
                    if old_backup.exists():
                        old_backup.unlink()  # delete very old one
                    backup.rename(old_backup)
                    print(f"  Existing backup renamed to: {old_backup.name}")
                else:
                    print(f"  Creating new backup")

                # Now safe to rename original to .bak
                filepath.rename(backup)
                print(f"  Backup created: {backup.name}")

            out_path = filepath if OVERWRITE_ORIGINAL else filepath.with_stem(filepath.stem + "_with_alt")

            tree.write(
                str(out_path),
                pretty_print=True,
                xml_declaration=True,
                encoding="utf-8",
                with_tail=True
            )
            print(f"  Saved: {out_path.name}")
            return True
        else:
            print(f"  No changes: {filepath.name}")
            return False

    except Exception as e:
        print(f"Error in {filepath}: {e}")
        return False

def main():
    if len(sys.argv) == 1:
        folders = [Path.cwd()]
    else:
        folders = [Path(p) for p in sys.argv[1:]]

    total_files = 0
    modified_files = 0
    skipped_files = 0

    for folder in folders:
        print(f"\nProcessing: {folder.resolve()}")

        dita_files = sorted(folder.rglob("*.dita")) + sorted(folder.rglob("*.xml"))

        for f in dita_files:
            if any(part in SKIP_PARTS for part in f.parts):
                print(f"  Skipped: {f}")
                skipped_files += 1
                continue

            total_files += 1
            if process_file(f):
                modified_files += 1

    print("\n" + "="*70)
    print(f"Finished.")
    print(f"  Scanned files   : {total_files}")
    print(f"  Modified files  : {modified_files}")
    print(f"  Skipped files   : {skipped_files}")

if __name__ == "__main__":
    main()