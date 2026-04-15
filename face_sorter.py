"""
face_sorter.py
Core face detection, filtering, and clustering pipeline.
Can be imported by app.py (dashboard) or run directly from the terminal.
"""

import os
import sys
import shutil
import cv2
import numpy as np
from pathlib import Path
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import normalize
from PIL import Image as PILImage

SUPPORTED_EXTENSIONS = {'.jpg', '.jpeg', '.tiff', '.tif'}

DEFAULT_CONFIG = {
    'input_folder':         './input',
    'output_folder':        './output',
    'min_face_size_ratio':  0.04,
    'min_confidence':       0.55,
    'min_sharpness':        45.0,
    'max_yaw_angle':        60.0,
    'max_pitch_angle':      45.0,
    'dbscan_eps':           0.45,
    'dbscan_min_samples':   2,
}


def load_image(path: Path):
    try:
        pil_img = PILImage.open(path).convert('RGB')
        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    except Exception:
        return None


def get_face_sharpness(image, bbox) -> float:
    x1, y1, x2, y2 = [int(v) for v in bbox]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(image.shape[1], x2), min(image.shape[0], y2)
    region = image[y1:y2, x1:x2]
    if region.size == 0:
        return 0.0
    return float(cv2.Laplacian(cv2.cvtColor(region, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var())


def should_keep_face(face, image_width, image_height, sharpness, cfg):
    x1, y1, x2, y2 = face.bbox
    if (x2 - x1) / image_width < cfg['min_face_size_ratio']:
        return False, 'size'
    if face.det_score < cfg['min_confidence']:
        return False, 'confidence'
    if sharpness < cfg['min_sharpness']:
        return False, 'blur'
    if hasattr(face, 'pose') and face.pose is not None:
        yaw, pitch, _ = face.pose
        if abs(yaw) > cfg['max_yaw_angle'] or abs(pitch) > cfg['max_pitch_angle']:
            return False, 'angle'
    return True, 'ok'


def collect_image_paths(folder: Path):
    paths = []
    for ext in SUPPORTED_EXTENSIONS:
        paths.extend(folder.rglob(f'*{ext}'))
        paths.extend(folder.rglob(f'*{ext.upper()}'))
    return sorted(set(paths))


def run_sort(config: dict, step_cb=None) -> dict:
    """
    Run the full face sorting pipeline.

    step_cb(phase, current, total, message) is called throughout.
    Phases: 'init' | 'scan' | 'cluster' | 'write' | 'done'

    Returns a results dict on success, raises Exception on failure.
    """
    cfg = {**DEFAULT_CONFIG, **config}

    def cb(phase, current, total, msg):
        if step_cb:
            step_cb(phase, current, total, msg)

    input_path  = Path(cfg['input_folder'])
    output_path = Path(cfg['output_folder'])

    if not input_path.exists():
        raise FileNotFoundError(f"Input folder not found: {input_path}")

    image_paths = collect_image_paths(input_path)
    if not image_paths:
        raise ValueError(f"No supported images found in: {input_path}")

    cb('init', 0, 1, f'Found {len(image_paths)} photos — loading AI model...')

    try:
        from insightface.app import FaceAnalysis
    except ImportError:
        raise ImportError("InsightFace not installed. Run: pip install insightface onnxruntime")

    app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
    app.prepare(ctx_id=0, det_size=(640, 640))

    cb('scan', 0, len(image_paths), 'Starting face detection...')

    face_data   = []
    skip_counts = {'size': 0, 'confidence': 0, 'blur': 0, 'angle': 0}
    total_detected = 0

    for i, img_path in enumerate(image_paths):
        cb('scan', i + 1, len(image_paths), f'Scanning {img_path.name}')
        img = load_image(img_path)
        if img is None:
            continue
        h, w = img.shape[:2]
        try:
            faces = app.get(img)
        except Exception:
            continue
        total_detected += len(faces)
        for face in faces:
            sharpness = get_face_sharpness(img, face.bbox)
            keep, reason = should_keep_face(face, w, h, sharpness, cfg)
            if not keep:
                skip_counts[reason] = skip_counts.get(reason, 0) + 1
                continue
            if face.embedding is None:
                continue
            face_data.append({'embedding': face.embedding, 'image_path': str(img_path)})

    if not face_data:
        raise ValueError(
            "No faces passed the filters. Try lowering Min Face Size or Min Sharpness."
        )

    cb('cluster', 0, 1, f'Clustering {len(face_data)} faces into people...')

    embeddings = normalize(np.array([d['embedding'] for d in face_data]))
    labels = DBSCAN(
        eps=cfg['dbscan_eps'],
        min_samples=cfg['dbscan_min_samples'],
        metric='cosine',
        n_jobs=-1
    ).fit_predict(embeddings)

    unique_people = set(l for l in labels if l != -1)
    noise_count   = int((labels == -1).sum())

    cb('cluster', 1, 1, f'Found {len(unique_people)} unique people')

    output_path.mkdir(parents=True, exist_ok=True)
    unmatched_path = output_path / 'unmatched'
    unmatched_path.mkdir(exist_ok=True)

    person_photos: dict[int, set] = {}
    for i, label in enumerate(labels):
        img_path = face_data[i]['image_path']
        if label == -1:
            dest = unmatched_path / Path(img_path).name
            if not dest.exists():
                shutil.copy2(img_path, dest)
        else:
            person_photos.setdefault(label, set()).add(img_path)

    sorted_people = sorted(person_photos.items(), key=lambda x: len(x[1]), reverse=True)
    total_to_write = sum(len(p) for _, p in sorted_people)
    written = 0
    person_folders = []

    for rank, (label, photos) in enumerate(sorted_people, start=1):
        folder_name   = f'person-{rank:03d}'
        person_folder = output_path / folder_name
        person_folder.mkdir(exist_ok=True)
        for img_path in photos:
            dest = person_folder / Path(img_path).name
            if not dest.exists():
                shutil.copy2(img_path, dest)
            written += 1
            cb('write', written, total_to_write, f'Writing {folder_name}...')
        person_folders.append({'name': folder_name, 'count': len(photos)})

    results = {
        'success':        True,
        'total_photos':   len(image_paths),
        'total_detected': total_detected,
        'faces_kept':     len(face_data),
        'people_found':   len(unique_people),
        'photos_sorted':  sum(len(p) for p in person_photos.values()),
        'unmatched':      noise_count,
        'skip_counts':    skip_counts,
        'person_folders': person_folders,
        'output_folder':  str(output_path.resolve()),
    }

    cb('done', 1, 1, 'Complete!')
    return results


if __name__ == '__main__':
    from tqdm import tqdm

    print('\n📸  FaceSorter — CLI Mode')
    print('─' * 40)

    _last_progress = [0]

    def cli_cb(phase, current, total, msg):
        print(f'  [{phase.upper():7s}] {msg}')

    try:
        results = run_sort(DEFAULT_CONFIG, step_cb=cli_cb)
        r = results
        print(f'\n{"═"*40}')
        print(f'✅  Done!')
        print(f'  Photos scanned:  {r["total_photos"]}')
        print(f'  People found:    {r["people_found"]}')
        print(f'  Photos sorted:   {r["photos_sorted"]}')
        print(f'  Unmatched:       {r["unmatched"]}')
        print(f'  Output:          {r["output_folder"]}')
    except Exception as e:
        print(f'\n❌  Error: {e}')
        sys.exit(1)
