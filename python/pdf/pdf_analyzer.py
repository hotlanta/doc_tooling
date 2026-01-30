"""
PDF Analyzer

Detects:
- Page overruns
- Table boundary overflows
- Table cell overflows
- Broken internal PDF links
- Broken external hyperlinks

Run contexts:
- hook   : fast, safe, non-blocking
- manual : developer fix loop
- ci     : strict, fail on errors
"""

import sys
import json
from pathlib import Path
from urllib.parse import urlparse

try:
    import pypdf
    import pdfplumber
    import requests
except ImportError:
    print("ERROR: Required libraries not installed.")
    print("pip install pypdf pdfplumber requests")
    sys.exit(1)


# --------------------------------------------------
# Analyzer
# --------------------------------------------------

class PDFAnalyzer:
    def __init__(
        self,
        pdf_path,
        run_context="hook",
        check_cells=True,
        cell_tolerance=3.0,
        check_links=False,
        check_external_links=False,
        link_timeout=5
    ):
        self.pdf_path = Path(pdf_path)
        self.run_context = run_context
        self.check_cells = check_cells
        self.cell_tolerance = cell_tolerance
        self.check_links = check_links
        self.check_external_links = check_external_links
        self.link_timeout = link_timeout

        self.issues = []
        self.named_destinations = {}

    # --------------------------------------------------
    # Main
    # --------------------------------------------------

    def analyze(self):
        if not self.pdf_path.exists():
            print(f"PDF not found – skipping analysis: {self.pdf_path}")
            return True

        with pypdf.PdfReader(self.pdf_path) as reader:
            self.named_destinations = reader.named_destinations or {}

        with pdfplumber.open(self.pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                self._check_page_overflow(page, page_num)
                self._check_table_overflow(page, page_num)

                if self.check_cells:
                    self._check_table_cell_overflow(page, page_num)

                if self.check_links:
                    self._check_links(page, page_num)

        return True

    # --------------------------------------------------
    # Issue handling
    # --------------------------------------------------

    def _add_issue(self, **issue):
        self.issues.append(issue)

    # --------------------------------------------------
    # Overflow checks (simplified but safe)
    # --------------------------------------------------

    def _check_page_overflow(self, page, page_num):
        for char in page.chars or []:
            if char["x1"] > page.width:
                self._add_issue(
                    page=page_num,
                    type="Page Overflow",
                    severity="warning",
                    text=char.get("text", ""),
                    details="Content exceeds page width"
                )

    def _check_table_overflow(self, page, page_num):
        for table in page.find_tables() or []:
            if table.bbox and table.bbox[2] > page.width:
                self._add_issue(
                    page=page_num,
                    type="Table Boundary Overflow",
                    severity="warning",
                    text=self._table_sample(table),
                    details="Table exceeds page width"
                )

    def _check_table_cell_overflow(self, page, page_num):
        for table in page.find_tables() or []:
            for cell in table.cells or []:
                x0, y0, x1, y1 = cell
                for char in page.chars or []:
                    if char["x1"] > x1 + self.cell_tolerance:
                        self._add_issue(
                            page=page_num,
                            type="Table Cell Overflow",
                            severity="warning",
                            text=char.get("text", ""),
                            details="Text exceeds cell boundary"
                        )

    # --------------------------------------------------
    # Link checks
    # --------------------------------------------------

    def _check_links(self, page, page_num):
        if not page.annots:
            return

        for annot in page.annots:
            if annot.get("Subtype") != "/Link":
                continue

            # External links
            if "/A" in annot and "/URI" in annot["/A"]:
                if self.check_external_links:
                    self._check_external_link(
                        annot["/A"]["/URI"], page_num
                    )

            # Internal links
            elif "/Dest" in annot:
                self._check_internal_link(
                    annot["/Dest"], page_num
                )

    def _check_internal_link(self, dest, page_num):
        # Named destination
        if isinstance(dest, str):
            if dest not in self.named_destinations:
                self._add_issue(
                    page=page_num,
                    type="Broken Internal Link",
                    severity="error",
                    text=dest,
                    details="Named destination not found"
                )

        # Page-based destination (valid)
        elif isinstance(dest, list):
            return

    def _check_external_link(self, uri, page_num):
        parsed = urlparse(uri)
        if parsed.scheme not in ("http", "https"):
            return

        try:
            r = requests.head(
                uri,
                timeout=self.link_timeout,
                allow_redirects=True
            )
            if r.status_code >= 400:
                raise Exception(f"HTTP {r.status_code}")
        except Exception as e:
            self._add_issue(
                page=page_num,
                type="Broken External Link",
                severity="warning",
                text=uri,
                details=str(e)
            )

    # --------------------------------------------------
    # Output
    # --------------------------------------------------

    def to_json(self):
        return {
            "file": self.pdf_path.name,
            "summary": {
                "errors": sum(1 for i in self.issues if i["severity"] == "error"),
                "warnings": sum(1 for i in self.issues if i["severity"] == "warning"),
            },
            "issues": self.issues,
        }

    def has_errors(self):
        return any(i["severity"] == "error" for i in self.issues)

    def _table_sample(self, table):
        data = table.extract()
        if not data:
            return "[Empty table]"
        return " | ".join(
            str(cell)[:30]
            for row in data[:1]
            for cell in row[:3]
            if cell
        )


# --------------------------------------------------
# CLI
# --------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: pdf_analyzer.py <pdf> [options]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    args = sys.argv[2:]

    run_context = "hook"
    if "--run-context" in args:
        run_context = args[args.index("--run-context") + 1]

    check_links = "--check-links" in args
    check_external_links = "--no-external-links" not in args

    json_out = None
    if "--json" in args:
        json_out = args[args.index("--json") + 1]

    analyzer = PDFAnalyzer(
        pdf_path,
        run_context=run_context,
        check_links=check_links,
        check_external_links=check_external_links,
    )

    analyzer.analyze()

    if json_out:
        Path(json_out).parent.mkdir(parents=True, exist_ok=True)
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(analyzer.to_json(), f, indent=2)

    if run_context == "ci" and analyzer.has_errors():
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
