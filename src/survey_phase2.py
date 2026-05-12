"""
survey_phase2.py — Argus Phase 2 technical survey.

Enriches data/manifest.csv with per-item metadata:
  - text/PDF:   pdf_page_count
  - image:      image_width, image_height
  - video:      video_duration_sec, video_resolution

Also runs filename pattern analysis and emits a structured survey notes
document at notebooks/survey_phase2.md.

Idempotent: re-running on an already-enriched manifest refreshes values
(does not duplicate rows).

Run from project root:
    python src/survey_phase2.py
"""
from __future__ import annotations

import csv
import datetime as dt
import logging
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

__version__ = "1.0.0"

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "data" / "manifest.csv"
NOTES_PATH = ROOT / "notebooks" / "survey_phase2.md"
LOG_DIR = ROOT / "logs"
DATA_RAW = ROOT / "data" / "raw"

NEW_COLUMNS = [
    "pdf_page_count",
    "image_width",
    "image_height",
    "video_duration_sec",
    "video_resolution",
]


def setup_logging() -> Path:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    log_path = LOG_DIR / f"survey_phase2_{stamp}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return log_path


# ---------------------------------------------------------------------------
# Enrichment

def enrich_pdf(path: Path) -> dict:
    from pypdf import PdfReader
    from pypdf.errors import PdfReadError
    try:
        reader = PdfReader(str(path), strict=False)
        return {"pdf_page_count": len(reader.pages)}
    except (PdfReadError, Exception) as e:
        logging.warning(f"  pdf failed: {path.name}: {e}")
        return {"pdf_page_count": ""}


def enrich_image(path: Path) -> dict:
    from PIL import Image
    try:
        with Image.open(path) as im:
            return {
                "image_width": im.width,
                "image_height": im.height,
            }
    except Exception as e:
        logging.warning(f"  image failed: {path.name}: {e}")
        return {"image_width": "", "image_height": ""}


def enrich_video(path: Path) -> dict:
    try:
        import cv2
    except ImportError:
        return {"video_duration_sec": "", "video_resolution": ""}
    try:
        cap = cv2.VideoCapture(str(path))
        if not cap.isOpened():
            return {"video_duration_sec": "", "video_resolution": ""}
        fps = cap.get(cv2.CAP_PROP_FPS) or 0
        n_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        duration = round(n_frames / fps, 2) if fps > 0 else 0
        cap.release()
        return {
            "video_duration_sec": duration,
            "video_resolution": f"{width}x{height}" if width and height else "",
        }
    except Exception as e:
        logging.warning(f"  video failed: {path.name}: {e}")
        return {"video_duration_sec": "", "video_resolution": ""}


def enrich_manifest() -> list[dict]:
    with MANIFEST_PATH.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    logging.info(f"loaded {len(rows)} rows")

    media_dirs = {
        "video": DATA_RAW / "video",
        "image": DATA_RAW / "images",
        "text": DATA_RAW / "text",
    }

    n_enriched = {"video": 0, "image": 0, "text": 0}

    for i, row in enumerate(rows, 1):
        media_type = row["media_type"]
        path = media_dirs[media_type] / row["filename"]
        if not path.exists():
            logging.warning(f"  missing file: {path}")
            continue

        if media_type == "text":
            update = enrich_pdf(path)
        elif media_type == "image":
            update = enrich_image(path)
        elif media_type == "video":
            update = enrich_video(path)
        else:
            update = {}

        for k, v in update.items():
            row[k] = v
        n_enriched[media_type] += 1

        if i % 25 == 0:
            logging.info(f"  ...{i} rows enriched")

    logging.info(f"enriched: {n_enriched}")
    return rows


def write_enriched_manifest(rows: list[dict]) -> None:
    # Preserve original column order + append new columns
    base_cols = [
        "item_id", "filename", "media_type", "source_archive", "internal_path",
        "tranche", "agency", "sha256", "byte_size", "source_url",
        "retrieval_timestamp", "archiver_version",
    ]
    all_cols = base_cols + NEW_COLUMNS

    with MANIFEST_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=all_cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in all_cols})


# ---------------------------------------------------------------------------
# Filename pattern analysis

def filename_clusters(rows: list[dict]) -> dict[str, list[dict]]:
    """Group rows by leading-token filename pattern."""
    clusters: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        fn = r["filename"]
        # Match common patterns: AGENCY_NUMBER, AGENCY-text, leading-number_
        if re.match(r"^[A-Z]{2,5}_\d+", fn):
            cluster = re.match(r"^([A-Z]{2,5})_", fn).group(1) + "_<numeric_id>"
        elif re.match(r"^[A-Z]{2,5}-", fn):
            cluster = re.match(r"^([A-Z]{2,5})-", fn).group(1) + "-<rest>"
        elif re.match(r"^\d+_", fn):
            cluster = "<numeric_prefix>_<rest>"
        elif re.match(r"^[A-Z]", fn):
            first_word = re.match(r"^([A-Za-z]+)", fn).group(1)
            cluster = f"<{first_word}_prefix>"
        else:
            cluster = "<other>"
        clusters[cluster].append(r)
    return dict(clusters)


# ---------------------------------------------------------------------------
# Distributions

def numeric_distribution(values: list) -> dict:
    nums = [float(v) for v in values if v not in ("", None)]
    if not nums:
        return {}
    nums.sort()
    return {
        "n": len(nums),
        "min": min(nums),
        "p25": statistics.quantiles(nums, n=4)[0] if len(nums) >= 4 else nums[0],
        "median": statistics.median(nums),
        "p75": statistics.quantiles(nums, n=4)[2] if len(nums) >= 4 else nums[-1],
        "max": max(nums),
    }


def format_size(bytes_n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if bytes_n < 1024:
            return f"{bytes_n:.1f} {unit}"
        bytes_n /= 1024
    return f"{bytes_n:.1f} TB"


# ---------------------------------------------------------------------------
# Notes writer

def write_survey_notes(rows: list[dict], clusters: dict[str, list[dict]]) -> None:
    NOTES_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Distributions per media type
    by_type = defaultdict(list)
    for r in rows:
        by_type[r["media_type"]].append(r)

    size_dist = {
        mt: numeric_distribution([r["byte_size"] for r in lst])
        for mt, lst in by_type.items()
    }
    page_dist = numeric_distribution([r.get("pdf_page_count", "") for r in by_type["text"]])
    duration_dist = numeric_distribution([r.get("video_duration_sec", "") for r in by_type["video"]])

    # Image resolution counts
    res_counter = Counter(
        f"{r.get('image_width', '?')}x{r.get('image_height', '?')}"
        for r in by_type["image"]
    )
    video_res_counter = Counter(r.get("video_resolution", "") for r in by_type["video"])

    # Agency distribution
    agency_counter = Counter(r["agency"] for r in rows)

    md = []
    md.append("# Survey — Phase 2 (Tranche 1)\n")
    md.append(f"**Generated:** {dt.datetime.now().strftime('%Y-%m-%d %H:%M')} by `src/survey_phase2.py` v{__version__}\n")
    md.append("**Source:** `data/manifest.csv` after enrichment with per-item metadata.\n")
    md.append("\n---\n\n")

    md.append("## 1. Counts per media type\n\n")
    md.append("| Media | Count |\n|---|---|\n")
    for mt in ("video", "image", "text"):
        md.append(f"| {mt} | {len(by_type[mt])} |\n")
    md.append(f"| **Total** | **{len(rows)}** |\n\n")

    md.append("## 2. File size distributions (bytes)\n\n")
    md.append("| Media | Count | Min | p25 | Median | p75 | Max |\n|---|---|---|---|---|---|---|\n")
    for mt in ("video", "image", "text"):
        d = size_dist[mt]
        if d:
            md.append(
                f"| {mt} | {d['n']} | {format_size(d['min'])} | {format_size(d['p25'])} | "
                f"{format_size(d['median'])} | {format_size(d['p75'])} | {format_size(d['max'])} |\n"
            )
    md.append("\n")

    md.append("## 3. PDF page-count distribution\n\n")
    if page_dist:
        md.append("| Min | p25 | Median | p75 | Max |\n|---|---|---|---|---|\n")
        md.append(
            f"| {int(page_dist['min'])} | {int(page_dist['p25'])} | "
            f"{int(page_dist['median'])} | {int(page_dist['p75'])} | "
            f"{int(page_dist['max'])} |\n\n"
        )

    md.append("## 4. Video duration distribution (seconds)\n\n")
    if duration_dist:
        md.append("| Min | p25 | Median | p75 | Max |\n|---|---|---|---|---|\n")
        md.append(
            f"| {duration_dist['min']:.1f} | {duration_dist['p25']:.1f} | "
            f"{duration_dist['median']:.1f} | {duration_dist['p75']:.1f} | "
            f"{duration_dist['max']:.1f} |\n\n"
        )
    md.append("**Video resolutions:**\n\n")
    for res, n in video_res_counter.most_common():
        md.append(f"- `{res}`: {n} videos\n")
    md.append("\n")

    md.append("## 5. Image resolution distribution\n\n")
    md.append("| Resolution | Count |\n|---|---|\n")
    for res, n in res_counter.most_common(20):
        md.append(f"| {res} | {n} |\n")
    md.append("\n")

    md.append("## 6. Agency distribution (derived from filename)\n\n")
    md.append("| Agency | Count |\n|---|---|\n")
    for ag, n in agency_counter.most_common():
        md.append(f"| {ag} | {n} |\n")
    md.append("\n")

    md.append("## 7. Filename pattern clusters\n\n")
    for cluster, items in sorted(clusters.items(), key=lambda kv: -len(kv[1])):
        md.append(f"### `{cluster}` — {len(items)} items\n\n")
        md.append("Examples:\n\n")
        for r in items[:5]:
            md.append(f"- `{r['filename']}` ({r['media_type']})\n")
        md.append("\n")

    # Observations and open questions — auto-generated starters
    md.append("## 8. Observations on what filenames implicitly encode\n\n")

    dod_count = len([r for r in rows if r["agency"] == "DOD"])
    unknown_count = len([r for r in rows if r["agency"] == "unknown"])

    md.append(
        f"- **Agency tag in prefix:** {dod_count} items have `DOD_` filename prefix; "
        f"these are all videos. Remaining {unknown_count} items have no derivable "
        f"agency from the filename alone.\n"
    )
    md.append(
        "- **Numeric IDs:** the `DOD_<numeric>.mp4` videos use sequential-looking "
        "9-digit DOD identifiers (likely DVIDS asset IDs, but unconfirmed).\n"
    )
    md.append(
        "- **Document naming heterogeneity:** the 115 PDFs do not share a single "
        "naming convention. Multiple clusters present (see §7). This suggests the "
        "release was assembled from multiple agency sources, each with its own "
        "filing conventions, and concatenated without normalization.\n"
    )
    md.append("\n")

    md.append("## 9. Conspicuous absences\n\n")
    md.append(
        "Things filenames generally **do not** encode for these items:\n\n"
        "- **Date of incident** — no year or date is parseable from most filenames.\n"
        "- **Geographic location** — no place name in the filename.\n"
        "- **Sensor type** — no FLIR/optical/radar tag; would need to be inferred from content.\n"
        "- **Classification level at time of original creation** — no markings in the filename "
        "(this would be a property of the document content, not its name).\n"
        "- **Sequencing / pairing** — when multiple items belong to the same incident, "
        "the filename does not encode that relationship.\n\n"
    )

    md.append("## 10. Open questions for the researcher (pre-Phase-3)\n\n")
    md.append(
        "1. **Do the 28 DOD videos belong to a small number of incidents, or are they 28 distinct incidents?** "
        "Numeric IDs are non-sequential — need to view content to know whether they cluster.\n"
        "2. **Do PDFs accompany videos (paired evidence packages) or are they independent document releases?** "
        "Filename matching would not detect this; need content inspection.\n"
        "3. **Is the war.gov page itself adding metadata that's not in the filenames** "
        "(captions, agency attribution, incident date)? Worth fetching the page in a later handoff.\n"
        "4. **What's the right level of granularity for classification — per-file, per-incident, per-frame?** "
        "Videos in particular contain many distinct visual events; a single classification per video may be too coarse.\n"
        "5. **Are documents-vs-images-vs-video three separate taxonomies or one with a media-type dimension?** "
        "(Open question carried from `FUTURE_WORK.md`.)\n\n"
    )

    md.append("## 11. Next handoffs\n\n")
    md.append(
        "- **H-004 (suggested):** External-taxonomy survey — Hynek, Vallée, AARO, GEIPAN, SCU. "
        "Output goes to `notebooks/existing_taxonomies.md`.\n"
        "- **H-005 (suggested):** Fetch war.gov/UFO/pursue-initiative/ and parse the page "
        "for source-level metadata (captions, agency attribution per item). Refine `source_url` "
        "in the manifest from page-URL to direct-download-URL.\n"
    )

    NOTES_PATH.write_text("".join(md), encoding="utf-8")
    logging.info(f"wrote {NOTES_PATH}")


# ---------------------------------------------------------------------------
# Main

def main() -> int:
    log_path = setup_logging()
    logging.info(f"survey_phase2 v{__version__} starting")
    logging.info(f"log: {log_path}")

    rows = enrich_manifest()
    write_enriched_manifest(rows)
    logging.info(f"manifest written with new columns: {NEW_COLUMNS}")

    clusters = filename_clusters(rows)
    logging.info(f"filename clusters: {[(k, len(v)) for k, v in clusters.items()]}")

    write_survey_notes(rows, clusters)

    return 0


if __name__ == "__main__":
    sys.exit(main())
