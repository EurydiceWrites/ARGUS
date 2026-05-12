"""
phase1_archive.py — Argus Phase 1 archiver.

Extracts the Tranche 1 PURSUE release ZIPs from data/raw/, routes contents to
the three media buckets (video/, images/, text/), computes SHA-256 per file,
and writes a tracked manifest at data/manifest.csv.

Idempotent: re-running skips items already in manifest whose destination
file exists.

Run from the project root:
    python src/phase1_archive.py
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import logging
import sys
import zipfile
from pathlib import Path

__version__ = "1.0.0"

# ---------------------------------------------------------------------------
# Paths

ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data" / "raw"
VIDEO_DIR = DATA_RAW / "video"
IMAGES_DIR = DATA_RAW / "images"
TEXT_DIR = DATA_RAW / "text"
MANIFEST_PATH = ROOT / "data" / "manifest.csv"
LOG_DIR = ROOT / "logs"

# Source archives
SOURCE_ARCHIVES = {
    "Release_1.zip": DATA_RAW / "Release_1.zip",
    "uapvideos.zip": DATA_RAW / "uapvideos.zip",
}

SOURCE_URL_DEFAULT = "https://www.war.gov/ufo/pursue-initiative/"
TRANCHE_DEFAULT = "Tranche_1"
TRANCHE_MANUAL = "Tranche_0_manual"

# ---------------------------------------------------------------------------
# Routing

EXT_TO_MEDIA_TYPE = {
    # video
    ".mp4": "video",
    ".mov": "video",
    ".avi": "video",
    ".mkv": "video",
    ".wmv": "video",
    # images
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".gif": "image",
    ".tiff": "image",
    ".tif": "image",
    ".webp": "image",
    ".bmp": "image",
    # text / documents
    ".pdf": "text",
    ".txt": "text",
    ".docx": "text",
    ".doc": "text",
    ".rtf": "text",
    ".md": "text",
}

MEDIA_TYPE_TO_DIR = {
    "video": VIDEO_DIR,
    "image": IMAGES_DIR,
    "text": TEXT_DIR,
}

SKIP_PATTERNS = ("__MACOSX/", "__MACOSX\\", ".DS_Store")

MANIFEST_COLUMNS = [
    "item_id",
    "filename",
    "media_type",
    "source_archive",
    "internal_path",
    "tranche",
    "agency",
    "sha256",
    "byte_size",
    "source_url",
    "retrieval_timestamp",
    "archiver_version",
]

# ---------------------------------------------------------------------------
# Helpers

def setup_logging() -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    log_path = LOG_DIR / f"phase1_archive_{stamp}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return log_path


def should_skip(internal_path: str) -> bool:
    """Skip Mac metadata cruft and directory entries."""
    if internal_path.endswith("/") or internal_path.endswith("\\"):
        return True
    if any(pat in internal_path for pat in SKIP_PATTERNS):
        return True
    name = Path(internal_path).name
    if name.startswith("._"):  # AppleDouble resource forks
        return True
    return False


def sniff_media_type(data_head: bytes) -> tuple[str, str]:
    """Identify media type from the first few bytes of a file.

    Returns (media_type, inferred_extension). If unknown, returns ('text', '.bin')
    as a conservative default (everything text-like or unidentified gets
    archived in text/ with a .bin extension flag).
    """
    if len(data_head) < 4:
        return ("text", ".bin")

    sig4 = data_head[:4]
    sig8 = data_head[:8]

    if sig4 == b"%PDF":
        return ("text", ".pdf")
    if sig8 == b"\x89PNG\r\n\x1a\n":
        return ("image", ".png")
    if sig4[:3] == b"\xff\xd8\xff":
        return ("image", ".jpg")
    if sig4 == b"GIF8":
        return ("image", ".gif")
    if sig4 in (b"II*\x00", b"MM\x00*"):
        return ("image", ".tiff")
    if len(data_head) >= 12 and data_head[4:8] == b"ftyp":
        return ("video", ".mp4")
    if sig4 == b"RIFF" and len(data_head) >= 12 and data_head[8:12] == b"WEBP":
        return ("image", ".webp")
    if sig4 == b"PK\x03\x04":
        return ("text", ".zip")
    if sig4 == b"\xd0\xcf\x11\xe0":
        return ("text", ".doc")  # MS Office legacy compound
    return ("text", ".bin")


def route_internal_path(internal_path: str, zf: zipfile.ZipFile) -> tuple[str | None, str]:
    """Decide (media_type, final_extension) for an item in a ZIP.

    For known extensions, use the map. For unknown, peek at first bytes.
    """
    suffix = Path(internal_path).suffix.lower()
    if suffix in EXT_TO_MEDIA_TYPE:
        return (EXT_TO_MEDIA_TYPE[suffix], suffix)

    # Unknown extension — sniff first 16 bytes
    try:
        with zf.open(internal_path) as f:
            head = f.read(16)
        media_type, inferred_ext = sniff_media_type(head)
        return (media_type, inferred_ext)
    except Exception as e:
        logging.warning(f"  sniff failed for {internal_path}: {e}")
        return (None, "")


def derive_agency(filename: str) -> str:
    """Derive originating agency from filename conventions."""
    if filename.startswith("DOD_") or filename.startswith("DoD_"):
        return "DOD"
    if filename.startswith("NASA_"):
        return "NASA"
    if filename.startswith("FBI_"):
        return "FBI"
    return "unknown"


def sha256_of_file(path: Path, chunk_size: int = 1 << 20) -> tuple[str, int]:
    """Compute SHA-256 of a file. Returns (hex_digest, byte_size)."""
    h = hashlib.sha256()
    size = 0
    with path.open("rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
            size += len(chunk)
    return (h.hexdigest(), size)


def resolve_destination(
    dest_dir: Path, base_name: str, internal_path: str
) -> Path:
    """Return a non-colliding destination path. If base_name exists,
    prefix with parent directory name from internal_path."""
    candidate = dest_dir / base_name
    if not candidate.exists():
        return candidate

    # Collision — prefix with parent dir
    parts = Path(internal_path).parts
    if len(parts) >= 2:
        parent = parts[-2]
        candidate = dest_dir / f"{parent}__{base_name}"
        if not candidate.exists():
            return candidate

    # Still colliding (unlikely) — numeric suffix
    stem = Path(base_name).stem
    suffix = Path(base_name).suffix
    for i in range(2, 1000):
        candidate = dest_dir / f"{stem}__{i}{suffix}"
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"could not resolve collision for {base_name}")


def load_existing_manifest() -> tuple[list[dict], set[tuple[str, str]]]:
    """Return (existing_rows, skip_set keyed by (source_archive, internal_path))."""
    if not MANIFEST_PATH.exists():
        return ([], set())
    with MANIFEST_PATH.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    skip_set = {(r["source_archive"], r["internal_path"]) for r in rows}
    return (rows, skip_set)


def write_manifest(rows: list[dict]) -> None:
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MANIFEST_COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in MANIFEST_COLUMNS})


# ---------------------------------------------------------------------------
# Main extraction

def extract_archive(
    archive_name: str,
    archive_path: Path,
    existing_skip: set[tuple[str, str]],
    next_item_id: int,
) -> tuple[list[dict], int]:
    """Extract one ZIP. Returns (new_rows, next_item_id_after)."""
    if not archive_path.exists():
        logging.error(f"archive missing: {archive_path}")
        return ([], next_item_id)

    new_rows: list[dict] = []
    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    with zipfile.ZipFile(archive_path) as zf:
        infos = zf.infolist()
        logging.info(f"  {archive_name}: {len(infos)} entries")

        for info in infos:
            internal_path = info.filename
            if should_skip(internal_path):
                continue

            key = (archive_name, internal_path)
            if key in existing_skip:
                logging.info(f"  skip (already in manifest): {internal_path}")
                continue

            media_type, ext = route_internal_path(internal_path, zf)
            if media_type is None:
                logging.warning(f"  could not route: {internal_path}")
                continue

            dest_dir = MEDIA_TYPE_TO_DIR[media_type]
            dest_dir.mkdir(parents=True, exist_ok=True)

            base_name = Path(internal_path).name
            # If we sniffed a different extension than the file's own, append it.
            current_suffix = Path(base_name).suffix.lower()
            if not current_suffix and ext:
                base_name = base_name + ext

            dest_path = resolve_destination(dest_dir, base_name, internal_path)

            # Extract bytes
            with zf.open(info) as src, dest_path.open("wb") as dst:
                while True:
                    chunk = src.read(1 << 20)
                    if not chunk:
                        break
                    dst.write(chunk)

            sha256, byte_size = sha256_of_file(dest_path)
            agency = derive_agency(dest_path.name)

            new_rows.append({
                "item_id": next_item_id,
                "filename": dest_path.name,
                "media_type": media_type,
                "source_archive": archive_name,
                "internal_path": internal_path,
                "tranche": TRANCHE_DEFAULT,
                "agency": agency,
                "sha256": sha256,
                "byte_size": byte_size,
                "source_url": SOURCE_URL_DEFAULT,
                "retrieval_timestamp": timestamp,
                "archiver_version": __version__,
            })
            next_item_id += 1

            if next_item_id % 50 == 0:
                logging.info(f"  ...{next_item_id - 1} items processed")

    return (new_rows, next_item_id)


def catalog_manual_items(
    existing_skip: set[tuple[str, str]],
    existing_hashes: set[str],
    next_item_id: int,
) -> tuple[list[dict], int]:
    """Catalog any items already sitting in data/raw/{video,images,text} that
    aren't in the manifest by hash. Used for genuinely manually-added files."""
    new_rows: list[dict] = []

    for media_type, dest_dir in MEDIA_TYPE_TO_DIR.items():
        if not dest_dir.exists():
            continue
        for path in sorted(dest_dir.iterdir()):
            if not path.is_file():
                continue

            sha256, byte_size = sha256_of_file(path)

            # Skip if already in manifest by hash (covers both prior manual
            # entries and ZIP-extracted entries from previous runs)
            if sha256 in existing_hashes:
                continue

            internal_path = f"manual/{path.name}"
            key = ("manual", internal_path)
            if key in existing_skip:
                continue

            ts = dt.datetime.fromtimestamp(
                path.stat().st_mtime, tz=dt.timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%SZ")

            new_rows.append({
                "item_id": next_item_id,
                "filename": path.name,
                "media_type": media_type,
                "source_archive": "manual",
                "internal_path": internal_path,
                "tranche": TRANCHE_MANUAL,
                "agency": derive_agency(path.name),
                "sha256": sha256,
                "byte_size": byte_size,
                "source_url": "unknown",
                "retrieval_timestamp": ts,
                "archiver_version": __version__,
            })
            next_item_id += 1

    return (new_rows, next_item_id)


def main() -> int:
    log_path = setup_logging()
    logging.info(f"phase1_archive v{__version__} starting")
    logging.info(f"log file: {log_path}")
    logging.info(f"manifest: {MANIFEST_PATH}")

    # Ensure media bucket dirs exist
    for d in MEDIA_TYPE_TO_DIR.values():
        d.mkdir(parents=True, exist_ok=True)

    existing_rows, skip_set = load_existing_manifest()
    logging.info(f"existing manifest rows: {len(existing_rows)}")
    next_item_id = max((int(r["item_id"]) for r in existing_rows), default=0) + 1

    all_new_rows: list[dict] = []

    # Process ZIPs first (so any ZIP-extracted file pre-empts the manual catalog)
    for archive_name, archive_path in SOURCE_ARCHIVES.items():
        logging.info(f"--- processing {archive_name}")
        rows, next_item_id = extract_archive(
            archive_name, archive_path, skip_set, next_item_id
        )
        all_new_rows.extend(rows)
        # Update skip set so the manual catalog pass sees these as covered
        for r in rows:
            skip_set.add((r["source_archive"], r["internal_path"]))

    # Catalog any unmanaged manual files. Skip by hash against everything
    # already in manifest OR newly extracted in this run.
    logging.info("--- cataloging manual items")
    existing_hashes = {r["sha256"] for r in existing_rows}
    existing_hashes.update(r["sha256"] for r in all_new_rows)
    manual_rows, next_item_id = catalog_manual_items(
        skip_set, existing_hashes, next_item_id
    )
    all_new_rows.extend(manual_rows)

    # Write manifest (existing + new)
    combined = existing_rows + all_new_rows
    write_manifest(combined)

    # Summary
    logging.info("--- summary")
    logging.info(f"new rows this run: {len(all_new_rows)}")
    logging.info(f"total rows in manifest: {len(combined)}")

    from collections import Counter
    media_counter = Counter(r["media_type"] for r in combined)
    archive_counter = Counter(r["source_archive"] for r in combined)
    tranche_counter = Counter(r["tranche"] for r in combined)
    logging.info(f"by media_type: {dict(media_counter)}")
    logging.info(f"by source_archive: {dict(archive_counter)}")
    logging.info(f"by tranche: {dict(tranche_counter)}")

    # File-on-disk counts
    for mt, d in MEDIA_TYPE_TO_DIR.items():
        n = sum(1 for p in d.iterdir() if p.is_file())
        logging.info(f"  files on disk in {d.name}/: {n}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
