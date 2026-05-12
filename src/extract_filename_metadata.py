"""
extract_filename_metadata.py — Argus filename metadata extractor.

Parses DOW, DOS, and NASA filename conventions surfaced in H-003 into
structured columns on data/manifest.csv. Enriches ~55 PDFs + ~12 NASA
images deterministically without opening any file.

What this script does:
  - Reads data/manifest.csv
  - Tries three deterministic regex parsers (DOW, DOS, NASA) per filename
  - Updates `agency` in place (preserve where it agrees; surface disagreements)
  - Appends four new columns: country, date, date_precision, item_type

What this script does NOT do:
  - No file opening (filenames only)
  - No LLM invocation
  - No taxonomy assignment
  - No FBI / DOD-video / USPER parsing — their filenames carry no incident
    metadata per H-003 and require content-extraction passes deferred to
    a later sub-phase

Idempotent: re-running on an already-enriched manifest produces byte-identical
output. Verified by an internal second-run hash comparison.

Authorized by: H-004 (handoffs/H-004_filename_extractor.md)

Run from project root:
    python src/extract_filename_metadata.py
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import logging
import re
import sys
from pathlib import Path

__version__ = "1.0.0"

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "data" / "manifest.csv"
LOG_DIR = ROOT / "logs"

NEW_COLUMNS = ["country", "date", "date_precision", "item_type"]

MONTHS = {
    "JANUARY": "01", "FEBRUARY": "02", "MARCH": "03", "APRIL": "04",
    "MAY": "05", "JUNE": "06", "JULY": "07", "AUGUST": "08",
    "SEPTEMBER": "09", "OCTOBER": "10", "NOVEMBER": "11", "DECEMBER": "12",
}
_MONTH_RE = "|".join(MONTHS.keys())

# Known DOW item_types, longest-first so prefix-collision picks the most
# specific match (e.g. "Range-Fouler-Debrief" before "Range-Fouler").
# New types observed in future tranches go here; unknown types fall through
# to the unparsed-candidates list for researcher review.
DOW_ITEM_TYPES = (
    "Range-Fouler-Debrief",
    "Range-Fouler",
    "Email-Correspondence",
    "Email-Correspondance",  # observed spelling variant in D52
    "Mission-Report",
    "Launch-Summary",
    "Report",
)

DOW_PREFIX_RE = re.compile(
    r"^DOW-UAP-D(?P<doc_num>\d+)-(?P<rest>.+)\.pdf$", re.IGNORECASE
)

# DOW date suffixes, tried longest-first (most specific) on the trailing
# portion of `rest` after `.pdf` is stripped:
_DATE_DAY_RE = re.compile(
    rf"-(?P<month>{_MONTH_RE})-(?P<day>\d{{1,2}})-(?P<year>\d{{4}})$",
    re.IGNORECASE,
)
_DATE_MONTH_RE = re.compile(
    rf"-(?P<month>{_MONTH_RE})-(?P<year>\d{{4}})$", re.IGNORECASE
)
_DATE_YEAR_RE = re.compile(r"-(?P<year>\d{4})$")
_DATE_NA_RE = re.compile(r"-NA$", re.IGNORECASE)

DOS_PATTERN = re.compile(
    rf"^DOS-UAP-D(?P<doc_num>\d+)"
    rf"-Cable-(?P<cable_num>\d+)"
    rf"-(?P<country>.+?)"
    rf"-(?P<month>{_MONTH_RE})"
    rf"-(?P<year>\d{{4}})"
    rf"\.pdf$",
    re.IGNORECASE,
)

NASA_PATTERN = re.compile(
    r"^NASA-UAP-(?P<item_subtype>[A-Z]+\d+)"
    r"-(?P<mission>.+)"
    r"-(?P<year>\d{4})"
    r"\.(?:jpg|jpeg|png|pdf)$",
    re.IGNORECASE,
)


def _strip_dow_date(rest: str) -> tuple[str, str, str]:
    """Strip a trailing date pattern off the DOW middle portion.

    Returns (remainder_without_date, iso_date_or_empty, precision_or_empty).
    Precision is "day", "month", "year", or "" if the date token is literal NA
    or absent.
    """
    m = _DATE_DAY_RE.search(rest)
    if m:
        month = MONTHS[m.group("month").upper()]
        day = m.group("day").zfill(2)
        year = m.group("year")
        return rest[: m.start()], f"{year}-{month}-{day}", "day"

    m = _DATE_MONTH_RE.search(rest)
    if m:
        month = MONTHS[m.group("month").upper()]
        year = m.group("year")
        return rest[: m.start()], f"{year}-{month}-01", "month"

    m = _DATE_YEAR_RE.search(rest)
    if m:
        year = m.group("year")
        return rest[: m.start()], f"{year}-01-01", "year"

    m = _DATE_NA_RE.search(rest)
    if m:
        # Date deliberately marked unknown in the filename
        return rest[: m.start()], "", ""

    return rest, "", ""


def _strip_dow_item_type(rest: str) -> tuple[str, str] | None:
    """Strip a known DOW item_type prefix off the left of `rest`.

    Returns (item_type, remainder) or None if no known prefix matches.
    Per H-004a: an exact match (remainder == item_type, no separator)
    returns an empty location; the caller treats that as "filename
    omits location" rather than as a parse failure.
    """
    upper = rest.upper()
    for item_type in DOW_ITEM_TYPES:
        item_upper = item_type.upper()
        if upper == item_upper:
            return item_type, ""
        # D32 has "Mission-Report,-Syria-..." — tolerate the comma artifact
        # observed in the source release. The canonical separator is "-".
        for sep in ("-", ",-"):
            token = item_upper + sep
            if upper.startswith(token):
                return item_type, rest[len(token):]
    return None


def parse_dow(filename: str) -> dict | None:
    m = DOW_PREFIX_RE.match(filename)
    if not m:
        return None
    rest = m.group("rest")

    remainder, iso_date, precision = _strip_dow_date(rest)

    extracted = _strip_dow_item_type(remainder)
    if extracted is None:
        return None
    item_type, location = extracted

    # H-004a: blank location is allowed (e.g. D48 "Report-September-1996",
    # D49 "Launch-Summary-February-2000"). Source filename simply omits a
    # location token; do not fabricate one.
    return {
        "agency": "DOW",
        "country": location,
        "date": iso_date,
        "date_precision": precision,
        "item_type": item_type,
    }


def parse_dos(filename: str) -> dict | None:
    m = DOS_PATTERN.match(filename)
    if not m:
        return None
    month = MONTHS[m.group("month").upper()]
    return {
        "agency": "DOS",
        "country": m.group("country"),
        "date": f"{m.group('year')}-{month}-01",
        "date_precision": "month",
        "item_type": "Cable",
    }


def parse_nasa(filename: str) -> dict | None:
    m = NASA_PATTERN.match(filename)
    if not m:
        return None
    year = m.group("year")
    return {
        "agency": "NASA",
        "country": "",  # NASA filenames don't encode country
        "date": f"{year}-01-01",
        "date_precision": "year",
        "item_type": m.group("item_subtype"),
    }


def parse_filename(filename: str) -> dict | None:
    """Dispatch: try DOW, DOS, NASA in order. Return first match or None."""
    for parser in (parse_dow, parse_dos, parse_nasa):
        result = parser(filename)
        if result is not None:
            return result
    return None


def enrich_manifest(manifest_path: Path) -> dict:
    """Read manifest, enrich rows, write back. Return stats dict."""
    with manifest_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    if "agency" not in fieldnames:
        fieldnames.append("agency")
    for col in NEW_COLUMNS:
        if col not in fieldnames:
            fieldnames.append(col)

    stats: dict = {
        "rows_total": len(rows),
        "parsed_per_agency": {"DOW": 0, "DOS": 0, "NASA": 0},
        "unparsed_candidates": [],
        "agency_disagreements": [],
    }

    for row in rows:
        for col in NEW_COLUMNS:
            row.setdefault(col, "")

        filename = row.get("filename", "")
        parsed = parse_filename(filename)

        if parsed is None:
            # Looks like a DOW/DOS/NASA filename but failed all parsers?
            if re.match(r"^(DOW|DOS|NASA)-", filename, re.IGNORECASE):
                stats["unparsed_candidates"].append(filename)
            continue

        stats["parsed_per_agency"][parsed["agency"]] += 1

        existing_agency = (row.get("agency") or "").strip()
        new_agency = parsed["agency"]
        # Per Step 5: preserve where it agrees; flag real disagreements.
        # "unknown" / "" are treated as blank, not as a real prior tag.
        if (
            existing_agency
            and existing_agency.lower() != "unknown"
            and existing_agency != new_agency
        ):
            stats["agency_disagreements"].append(
                {
                    "filename": filename,
                    "existing": existing_agency,
                    "parsed": new_agency,
                }
            )

        row["agency"] = new_agency
        row["country"] = parsed["country"]
        row["date"] = parsed["date"]
        row["date_precision"] = parsed["date_precision"]
        row["item_type"] = parsed["item_type"]

    with manifest_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    return stats


def _file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def setup_logging() -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = LOG_DIR / f"extract_filename_metadata_{stamp}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )
    return log_path


def main() -> int:
    log_path = setup_logging()
    logging.info("extract_filename_metadata.py v%s starting", __version__)
    logging.info("Manifest: %s", MANIFEST_PATH)
    logging.info("Log: %s", log_path)

    # First pass
    stats = enrich_manifest(MANIFEST_PATH)
    hash1 = _file_sha256(MANIFEST_PATH)

    # Idempotency: second pass on the now-enriched manifest
    enrich_manifest(MANIFEST_PATH)
    hash2 = _file_sha256(MANIFEST_PATH)
    idempotent = hash1 == hash2

    logging.info("=== Results ===")
    logging.info("Rows processed: %d", stats["rows_total"])
    for agency in ("DOW", "DOS", "NASA"):
        logging.info("  %s parsed: %d", agency, stats["parsed_per_agency"][agency])

    logging.info(
        "Unparsed DOW/DOS/NASA-like filenames: %d",
        len(stats["unparsed_candidates"]),
    )
    for fn in stats["unparsed_candidates"]:
        logging.info("  - %s", fn)

    logging.info(
        "Agency disagreements (filename parser vs. existing column): %d",
        len(stats["agency_disagreements"]),
    )
    for d in stats["agency_disagreements"]:
        logging.info(
            "  - %s: existing=%s parsed=%s",
            d["filename"],
            d["existing"],
            d["parsed"],
        )

    logging.info(
        "Idempotency: %s (run1=%s run2=%s)",
        "PASS" if idempotent else "FAIL",
        hash1,
        hash2,
    )

    return 0 if idempotent else 1


if __name__ == "__main__":
    sys.exit(main())
