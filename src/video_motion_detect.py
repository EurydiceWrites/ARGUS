"""H-005.5 detour — motion-isolated object detection on three PURSUE Tranche 1 videos.

Pipeline per video:
  1. Extract every frame at native fps via ffmpeg.
  2. Pass 1 — register each frame to frame-0 with ORB+RANSAC homography
     (mask out near-black redaction rectangles so they don't dominate
     features). Store stabilized grayscale stack in memory.
  3. Compute per-pixel temporal median across the stabilized stack — the
     static background. A moving dot is at any one pixel only briefly,
     so the median is effectively dot-free.
  4. Pass 2 — for each stabilized frame, subtract the median (signed
     positive part = brighter-than-background), threshold, morphology,
     contour extraction, filtered by area + circularity.
  5. Greedy nearest-neighbor link contour centroids into tracks.
  6. Pick the dominant track and emit overlay, motion accumulator,
     best-frame crop, annotated sequence, detections.csv, summary.

This is exploratory (low ceremony). Not part of build-order.
"""

from __future__ import annotations

import csv
import json
import math
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np

VIDEO_DIR = Path("data/raw/video")
FRAME_DIR = Path("frames")
OUT_DIR = Path("outputs/video_analysis")

VIDEOS = [
    ("DOD_111688809", 30.0),
    ("DOD_111689022", 10.0),
    ("DOD_111689759", 30000.0 / 1001.0),
]

FG_THRESHOLD = 35       # frame vs locally-dilated median; brighter than local-max background
DARK_FG_THRESHOLD = 35  # also catch darker-than-background blobs
LOCAL_BG_RADIUS = 3     # +/-N px tolerance for sub-pixel misregistration
MEDIAN_SAMPLE_STRIDE = 4  # use every Nth frame for median (memory + speed)
MIN_AREA = 3
MAX_AREA = 250          # the dot is small; anything bigger is probably a vehicle
MIN_CIRCULARITY = 0.45  # 4πA / P²; drops linear edge artifacts
LINK_MAX_DIST = 80      # pixels between consecutive frame detections to link
MIN_TRACK_LEN = 4       # minimum frames in a kept track
MIN_TRACK_DISPLACEMENT = 30  # a real moving object travels at least this many pixels
EDGE_GUARD_PX = 15      # ignore detections within this many px of warp border


@dataclass
class Detection:
    frame: int
    x: float
    y: float
    area: float
    bbox: tuple  # (x, y, w, h)


@dataclass
class Track:
    detections: list = field(default_factory=list)

    @property
    def frames(self):
        return [d.frame for d in self.detections]

    @property
    def length(self):
        if not self.detections:
            return 0
        return self.detections[-1].frame - self.detections[0].frame + 1

    def append(self, d: Detection):
        self.detections.append(d)

    def last(self):
        return self.detections[-1] if self.detections else None


def extract_frames(video_id: str) -> list[Path]:
    src = VIDEO_DIR / f"{video_id}.mp4"
    dst = FRAME_DIR / video_id
    dst.mkdir(parents=True, exist_ok=True)
    existing = sorted(dst.glob("frame_*.jpg"))
    if existing:
        return existing
    cmd = [
        "ffmpeg", "-loglevel", "error", "-y",
        "-i", str(src),
        "-q:v", "1",
        "-start_number", "0",
        str(dst / "frame_%05d.jpg"),
    ]
    subprocess.run(cmd, check=True)
    return sorted(dst.glob("frame_*.jpg"))


def detect_hud_mask(bgr: np.ndarray) -> np.ndarray:
    """Return uint8 mask (255 = HUD or redaction) for cyan/green HUD overlay
    (reticle, brackets, 'N') AND pure-black redaction rectangles. Both are
    pixel-fixed in the original frame and get falsely warped by stabilization."""
    b, g, r = cv2.split(bgr)
    bi = b.astype(np.int16); gi = g.astype(np.int16); ri = r.astype(np.int16)
    cyan = (gi > 110) & (bi > 80) & (ri < gi - 25)
    pure_green = (gi > 130) & (gi - ri > 30) & (gi - bi > 20)
    color_mask = (cyan | pure_green).astype(np.uint8) * 255

    # near-black redaction rectangles (pure black, large connected components)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    redaction = (gray <= 5).astype(np.uint8) * 255
    n_labels, labels, stats, _ = cv2.connectedComponentsWithStats(redaction, connectivity=8)
    redaction_clean = np.zeros_like(redaction)
    for i in range(1, n_labels):
        if stats[i, cv2.CC_STAT_AREA] >= 200:
            redaction_clean[labels == i] = 255

    mask = cv2.bitwise_or(color_mask, redaction_clean)
    mask = cv2.dilate(mask, np.ones((9, 9), np.uint8))
    return mask


def _compute_homography(orb, bf, ref_gray, kp_ref, des_ref, cur_gray, extra_mask=None):
    cur_mask = (cur_gray > 10).astype(np.uint8) * 255
    if extra_mask is not None:
        cur_mask = cv2.bitwise_and(cur_mask, cv2.bitwise_not(extra_mask))
    kp_cur, des_cur = orb.detectAndCompute(cur_gray, cur_mask)
    if des_cur is None or des_ref is None or len(kp_cur) < 12:
        return None
    matches = bf.match(des_ref, des_cur)
    if len(matches) < 12:
        return None
    matches = sorted(matches, key=lambda m: m.distance)[:300]
    src_pts = np.float32([kp_ref[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp_cur[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
    H, _ = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 3.0)
    return H


def stabilize_and_diff(video_id: str):
    frame_paths = extract_frames(video_id)
    n = len(frame_paths)
    print(f"  [{video_id}] {n} frames extracted", flush=True)

    ref = cv2.imread(str(frame_paths[0]))
    ref_gray = cv2.cvtColor(ref, cv2.COLOR_BGR2GRAY)
    h, w = ref_gray.shape

    ref_hud = detect_hud_mask(ref)

    orb = cv2.ORB_create(nfeatures=3000)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    ref_mask = (ref_gray > 10).astype(np.uint8) * 255
    ref_mask = cv2.bitwise_and(ref_mask, cv2.bitwise_not(ref_hud))
    kp_ref, des_ref = orb.detectAndCompute(ref_gray, ref_mask)

    # ---- Pass 1: stabilize all frames into an in-memory stack ----
    stab_stack = np.zeros((n, h, w), dtype=np.uint8)
    valid_stack = np.zeros((n, h, w), dtype=bool)
    hud_stack = np.zeros((n, h, w), dtype=bool)  # warped HUD mask per frame
    stab_stack[0] = ref_gray
    valid_stack[0] = ref_gray > 0
    hud_stack[0] = ref_hud > 0
    homography_failures = 0

    for i in range(1, n):
        cur = cv2.imread(str(frame_paths[i]))
        cur_gray = cv2.cvtColor(cur, cv2.COLOR_BGR2GRAY)
        cur_hud = detect_hud_mask(cur)
        H = _compute_homography(orb, bf, ref_gray, kp_ref, des_ref, cur_gray,
                                extra_mask=cur_hud)
        if H is None:
            homography_failures += 1
            H = np.eye(3, dtype=np.float64)
        stab = cv2.warpPerspective(cur_gray, H, (w, h),
                                   borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        # warp the HUD mask alongside so we know where HUD landed in stabilized frame
        hud_warped = cv2.warpPerspective(cur_hud, H, (w, h),
                                         flags=cv2.INTER_NEAREST,
                                         borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        stab_stack[i] = stab
        valid_stack[i] = stab > 0
        hud_stack[i] = hud_warped > 0
    print(f"  pass 1 done — stack {stab_stack.nbytes/1e6:.0f} MB, "
          f"H failures: {homography_failures}", flush=True)

    # ---- Median background from sampled subset ----
    # Mask out HUD pixels (their value is HUD overlay color, not scene) by
    # setting them to median of non-HUD samples. Simpler: just use samples as-is
    # and accept that the HUD trail biases median in the swept region; we'll
    # mask HUD-touched regions out of detection separately.
    sample = stab_stack[::MEDIAN_SAMPLE_STRIDE]
    median_bg = np.median(sample, axis=0).astype(np.uint8)
    print(f"  median background computed from {len(sample)} sampled frames", flush=True)

    # locally-dilated and -eroded median: tolerates +/- LOCAL_BG_RADIUS
    # px misregistration on bright/dark scene edges.
    local_kernel = np.ones((LOCAL_BG_RADIUS * 2 + 1, LOCAL_BG_RADIUS * 2 + 1), np.uint8)
    local_max_bg = cv2.dilate(median_bg, local_kernel)
    local_min_bg = cv2.erode(median_bg, local_kernel)

    # union of HUD positions across all frames — exclude these regions from detection
    hud_union = np.any(hud_stack, axis=0)
    hud_union_mask = (hud_union.astype(np.uint8) * 255)
    hud_union_mask = cv2.dilate(hud_union_mask, np.ones((7, 7), np.uint8))

    # erode valid mask once: ignore detections near warp borders
    border_kernel = np.ones((EDGE_GUARD_PX * 2 + 1, EDGE_GUARD_PX * 2 + 1), np.uint8)

    # ---- Pass 2: per-frame foreground detection ----
    detections: list[Detection] = []
    motion_accum = np.zeros_like(ref_gray, dtype=np.uint32)
    fg_accum = np.zeros_like(ref_gray, dtype=np.uint32)

    for i in range(n):
        stab = stab_stack[i]
        valid = valid_stack[i].astype(np.uint8) * 255
        valid_eroded = cv2.erode(valid, border_kernel)
        valid_eroded = cv2.bitwise_and(valid_eroded, cv2.bitwise_not(hud_union_mask))

        # local-max / local-min comparison: tolerates sub-pixel misregistration
        bright = np.clip(stab.astype(np.int16) - local_max_bg.astype(np.int16), 0, 255).astype(np.uint8)
        dark = np.clip(local_min_bg.astype(np.int16) - stab.astype(np.int16), 0, 255).astype(np.uint8)

        _, bright_bin = cv2.threshold(bright, FG_THRESHOLD, 255, cv2.THRESH_BINARY)
        _, dark_bin = cv2.threshold(dark, DARK_FG_THRESHOLD, 255, cv2.THRESH_BINARY)
        fg = cv2.bitwise_or(bright_bin, dark_bin)
        fg = cv2.bitwise_and(fg, valid_eroded)

        kernel = np.ones((3, 3), np.uint8)
        opened = cv2.morphologyEx(fg, cv2.MORPH_OPEN, kernel)

        motion_accum += (opened > 0).astype(np.uint32)
        fg_accum += np.maximum(bright, dark).astype(np.uint32)

        contours, _ = cv2.findContours(opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            area = cv2.contourArea(c)
            if not (MIN_AREA <= area <= MAX_AREA):
                continue
            perim = cv2.arcLength(c, True)
            if perim <= 0:
                continue
            circularity = 4 * math.pi * area / (perim * perim)
            if circularity < MIN_CIRCULARITY:
                continue
            M = cv2.moments(c)
            if M["m00"] <= 0:
                continue
            cx = M["m10"] / M["m00"]
            cy = M["m01"] / M["m00"]
            x, y, bw, bh = cv2.boundingRect(c)
            detections.append(Detection(frame=i, x=cx, y=cy, area=float(area),
                                        bbox=(int(x), int(y), int(bw), int(bh))))

    return {
        "n_frames": n,
        "ref_frame": ref,
        "shape": (h, w),
        "detections": detections,
        "motion_accum": motion_accum,
        "fg_accum": fg_accum,
        "median_bg": median_bg,
        "hud_union_mask": hud_union_mask,
        "homography_failures": homography_failures,
        "frame_paths": frame_paths,
        "stab_stack": stab_stack,
    }


def link_tracks(detections: list[Detection]) -> list[Track]:
    """Greedy nearest-neighbor linking across consecutive frames."""
    if not detections:
        return []
    by_frame: dict[int, list[Detection]] = {}
    for d in detections:
        by_frame.setdefault(d.frame, []).append(d)

    tracks: list[Track] = []
    active: list[Track] = []
    frames_sorted = sorted(by_frame.keys())

    for f_idx, frame in enumerate(frames_sorted):
        dets = by_frame[frame]
        used_dets = set()
        # try to extend each active track
        next_active: list[Track] = []
        for tr in active:
            last = tr.last()
            if frame - last.frame > 2:
                tracks.append(tr)
                continue
            best = None
            best_dist = LINK_MAX_DIST + 1
            for j, d in enumerate(dets):
                if j in used_dets:
                    continue
                dist = math.hypot(d.x - last.x, d.y - last.y)
                if dist < best_dist:
                    best_dist = dist
                    best = j
            if best is not None:
                tr.append(dets[best])
                used_dets.add(best)
                next_active.append(tr)
            else:
                if frame - last.frame >= 2:
                    tracks.append(tr)
                else:
                    next_active.append(tr)
        # spawn new tracks for unused detections
        for j, d in enumerate(dets):
            if j in used_dets:
                continue
            new_tr = Track()
            new_tr.append(d)
            next_active.append(new_tr)
        active = next_active

    tracks.extend(active)
    return tracks


def trajectory_metrics(track: Track, fps: float) -> dict:
    if len(track.detections) < 2:
        return {}
    xs = [d.x for d in track.detections]
    ys = [d.y for d in track.detections]
    frames = [d.frame for d in track.detections]
    seg_dists = [math.hypot(xs[i] - xs[i-1], ys[i] - ys[i-1])
                 for i in range(1, len(xs))]
    seg_frames = [frames[i] - frames[i-1] for i in range(1, len(frames))]
    px_per_frame = [d / max(1, df) for d, df in zip(seg_dists, seg_frames)]
    total_path = sum(seg_dists)
    displacement = math.hypot(xs[-1] - xs[0], ys[-1] - ys[0])
    duration_s = (frames[-1] - frames[0]) / fps
    mean_pps = (sum(px_per_frame) / len(px_per_frame)) if px_per_frame else 0.0
    angle_deg = math.degrees(math.atan2(ys[-1] - ys[0], xs[-1] - xs[0]))
    sizes = [d.area for d in track.detections]
    return {
        "n_detections": len(track.detections),
        "first_frame": frames[0],
        "last_frame": frames[-1],
        "duration_s": round(duration_s, 3),
        "start_xy": (round(xs[0], 1), round(ys[0], 1)),
        "end_xy": (round(xs[-1], 1), round(ys[-1], 1)),
        "displacement_px": round(displacement, 1),
        "total_path_px": round(total_path, 1),
        "mean_speed_px_per_frame": round(mean_pps, 2),
        "mean_speed_px_per_sec": round(mean_pps * fps, 2),
        "direction_deg_image_xy": round(angle_deg, 1),
        "mean_area_px": round(sum(sizes) / len(sizes), 1),
        "max_area_px": round(max(sizes), 1),
    }


def overlay_trajectory(ref: np.ndarray, track: Track, out_path: Path):
    img = ref.copy()
    pts = [(int(d.x), int(d.y)) for d in track.detections]
    for i in range(1, len(pts)):
        cv2.line(img, pts[i-1], pts[i], (0, 255, 255), 2)
    for d in track.detections:
        cv2.circle(img, (int(d.x), int(d.y)), 4, (0, 0, 255), -1)
    if pts:
        cv2.circle(img, pts[0], 8, (0, 255, 0), 2)
        cv2.circle(img, pts[-1], 8, (0, 0, 255), 2)
        cv2.putText(img, "START", (pts[0][0]+10, pts[0][1]-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.putText(img, "END", (pts[-1][0]+10, pts[-1][1]+15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    cv2.imwrite(str(out_path), img)


def overlay_all_detections(ref: np.ndarray, detections: list[Detection], out_path: Path):
    """Diagnostic: every raw detection regardless of track membership, color-coded by frame."""
    img = ref.copy()
    if not detections:
        cv2.imwrite(str(out_path), img)
        return
    fmin = min(d.frame for d in detections)
    fmax = max(d.frame for d in detections)
    span = max(1, fmax - fmin)
    for d in detections:
        t = (d.frame - fmin) / span
        # color ramp: blue (early) -> red (late)
        color = (int(255 * (1 - t)), 0, int(255 * t))
        cv2.circle(img, (int(d.x), int(d.y)), 3, color, -1)
    cv2.imwrite(str(out_path), img)


def best_frame_crop(track: Track, frame_paths: list[Path], out_path: Path):
    if not track.detections:
        return None
    best = max(track.detections, key=lambda d: d.area)
    img = cv2.imread(str(frame_paths[best.frame]))
    h, w = img.shape[:2]
    pad = 80
    x, y, bw, bh = best.bbox
    x0 = max(0, x - pad); y0 = max(0, y - pad)
    x1 = min(w, x + bw + pad); y1 = min(h, y + bh + pad)
    crop = img[y0:y1, x0:x1].copy()
    # draw a circle on the cropped object
    cv2.circle(crop, (x - x0 + bw // 2, y - y0 + bh // 2),
               max(bw, bh) // 2 + 6, (0, 255, 255), 2)
    # 4x upscale for readability
    crop_big = cv2.resize(crop, (crop.shape[1] * 4, crop.shape[0] * 4),
                          interpolation=cv2.INTER_NEAREST)
    cv2.imwrite(str(out_path), crop_big)
    return best.frame


def motion_accumulator_image(accum: np.ndarray, ref: np.ndarray, out_path: Path):
    if accum.max() == 0:
        cv2.imwrite(str(out_path), ref)
        return
    norm = (accum.astype(np.float32) / accum.max() * 255.0).astype(np.uint8)
    heat = cv2.applyColorMap(norm, cv2.COLORMAP_HOT)
    blend = cv2.addWeighted(ref, 0.5, heat, 0.5, 0)
    cv2.imwrite(str(out_path), blend)


def annotated_sequence(track: Track, frame_paths: list[Path],
                       out_dir: Path, every: int = 10):
    out_dir.mkdir(parents=True, exist_ok=True)
    track_by_frame = {d.frame: d for d in track.detections}
    n = len(frame_paths)
    for i in range(0, n, every):
        img = cv2.imread(str(frame_paths[i]))
        if i in track_by_frame:
            d = track_by_frame[i]
            cv2.circle(img, (int(d.x), int(d.y)), 18, (0, 255, 255), 2)
            cv2.putText(img, f"f{i} obj", (int(d.x)+22, int(d.y)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.putText(img, f"frame {i}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imwrite(str(out_dir / f"frame_{i:05d}.jpg"), img)


def save_detections_csv(detections: list[Detection], out_path: Path):
    with out_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["frame", "x", "y", "area", "bbox_x", "bbox_y", "bbox_w", "bbox_h"])
        for d in detections:
            writer.writerow([d.frame, f"{d.x:.2f}", f"{d.y:.2f}", f"{d.area:.1f}",
                             d.bbox[0], d.bbox[1], d.bbox[2], d.bbox[3]])


def write_summary(out_dir: Path, video_id: str, fps: float, result: dict,
                  tracks: list[Track], dominant: Track | None,
                  metrics: dict):
    summary = {
        "video_id": video_id,
        "fps_native": round(fps, 4),
        "n_frames": result["n_frames"],
        "shape_hw": list(result["shape"]),
        "homography_failures": result["homography_failures"],
        "n_raw_detections": len(result["detections"]),
        "n_tracks": len(tracks),
        "tracks_min_len_kept": MIN_TRACK_LEN,
        "kept_tracks": [
            {
                "len_frames": t.length,
                "n_detections": len(t.detections),
                "first_frame": t.detections[0].frame,
                "last_frame": t.detections[-1].frame,
            }
            for t in tracks if t.length >= MIN_TRACK_LEN
        ],
        "dominant_track_metrics": metrics,
    }
    (out_dir / "motion_summary.json").write_text(json.dumps(summary, indent=2))
    lines = [
        f"# {video_id} — motion summary",
        "",
        f"Native fps: {summary['fps_native']}",
        f"Frames: {summary['n_frames']}  Shape (HxW): {summary['shape_hw']}",
        f"Homography RANSAC failures: {summary['homography_failures']}",
        f"Raw detections (all contours, all frames): {summary['n_raw_detections']}",
        f"Tracks linked: {summary['n_tracks']}  Kept (>= {MIN_TRACK_LEN} frames): {len(summary['kept_tracks'])}",
        "",
    ]
    if metrics:
        lines.append("## Dominant track")
        for k, v in metrics.items():
            lines.append(f"- {k}: {v}")
    else:
        lines.append("## Dominant track\n- none — no track met the minimum-length threshold.")
    lines.append("")
    lines.append("## Per kept-track summary")
    for t in [t for t in tracks if t.length >= MIN_TRACK_LEN]:
        lines.append(f"- frames {t.detections[0].frame}-{t.detections[-1].frame}  "
                     f"n_dets={len(t.detections)}  len={t.length}f")
    (out_dir / "motion_summary.txt").write_text("\n".join(lines))


def process_video(video_id: str, fps: float):
    print(f"\n=== {video_id} (fps={fps:.3f}) ===", flush=True)
    out_dir = OUT_DIR / video_id
    out_dir.mkdir(parents=True, exist_ok=True)

    result = stabilize_and_diff(video_id)
    print(f"  raw detections: {len(result['detections'])}", flush=True)

    tracks = link_tracks(result["detections"])

    def displacement(t):
        if not t.detections:
            return 0.0
        xs = [d.x for d in t.detections]; ys = [d.y for d in t.detections]
        return math.hypot(xs[-1] - xs[0], ys[-1] - ys[0])

    kept = [t for t in tracks
            if t.length >= MIN_TRACK_LEN
            and displacement(t) >= MIN_TRACK_DISPLACEMENT]
    print(f"  tracks: total {len(tracks)} | kept (>= {MIN_TRACK_LEN}f, "
          f">= {MIN_TRACK_DISPLACEMENT}px disp) {len(kept)}", flush=True)

    # rank kept tracks: prefer longer + more detections + larger displacement
    dominant = max(kept,
                   key=lambda t: (t.length, len(t.detections), displacement(t)),
                   default=None)
    metrics = trajectory_metrics(dominant, fps) if dominant else {}

    overlay_all_detections(result["ref_frame"], result["detections"],
                           out_dir / "all_detections_overlay.png")
    motion_accumulator_image(result["motion_accum"], result["ref_frame"],
                             out_dir / "motion_accumulator.png")
    motion_accumulator_image(result["fg_accum"], result["ref_frame"],
                             out_dir / "foreground_accumulator.png")
    cv2.imwrite(str(out_dir / "median_background.png"), result["median_bg"])
    cv2.imwrite(str(out_dir / "hud_mask_union.png"), result["hud_union_mask"])
    save_detections_csv(result["detections"], out_dir / "detections.csv")

    if dominant:
        overlay_trajectory(result["ref_frame"], dominant, out_dir / "trajectory_overlay.png")
        best_frame_crop(dominant, result["frame_paths"], out_dir / "best_frame_crop.png")
        annotated_sequence(dominant, result["frame_paths"], out_dir / "annotated", every=10)
        print(f"  dominant track: frames {dominant.detections[0].frame}-{dominant.detections[-1].frame} "
              f"({len(dominant.detections)} dets, len={dominant.length}f)", flush=True)
    else:
        # still emit annotated sequence with no overlay
        annotated_sequence(Track(), result["frame_paths"], out_dir / "annotated", every=10)

    write_summary(out_dir, video_id, fps, result, tracks, dominant, metrics)
    print(f"  outputs -> {out_dir}", flush=True)


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for vid, fps in VIDEOS:
        if only and vid != only:
            continue
        process_video(vid, fps)


if __name__ == "__main__":
    main()
