"""
face_sorter.py
Core face detection, filtering, clustering, and thumbnail generation pipeline.
Can be imported by app.py (dashboard) or run directly from the terminal.
"""

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

THUMBNAIL_SIZE = 500


def load_image(path):
    try:
        pil_img = PILImage.open(path).convert('RGB')
        return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    except Exception:
        return None


def get_face_sharpness(image, bbox):
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


def face_quality_score(face_entry):
    """
    Score a face for thumbnail selection.
    Rewards: large face in frame, sharp image, high detection confidence, straight-on angle.
    Penalises: small face, blur, turned head.
    """
    x1, y1, x2, y2 = face_entry['bbox']
    face_width = x2 - x1

    score  = face_width * 1.2
    score += face_entry['sharpness'] * 0.3
    score += face_entry['det_score'] * 100
    score -= abs(face_entry.get('yaw',   0)) * 0.5
    score -= abs(face_entry.get('pitch', 0)) * 0.5
    return score


def generate_thumbnail(img_path, bbox, output_path):
    """
    Crop the face with padding, fill to a square using a blurred
    version of the edges (no white corners), resize and save.
    """
    img = load_image(Path(img_path))
    if img is None:
        return False

    h, w = img.shape[:2]
    x1, y1, x2, y2 = [int(v) for v in bbox]

    pad_x = int((x2 - x1) * 0.50)
    pad_y = int((y2 - y1) * 0.60)
    x1 = max(0, x1 - pad_x)
    y1 = max(0, y1 - pad_y)
    x2 = min(w, x2 + pad_x)
    y2 = min(h, y2 + pad_y)

    crop = img[y1:y2, x1:x2]
    if crop.size == 0:
        return False

    ch, cw = crop.shape[:2]
    dim = max(ch, cw)

    if ch != cw:
        blurred_bg = cv2.resize(crop, (dim, dim), interpolation=cv2.INTER_LINEAR)
        blurred_bg = cv2.GaussianBlur(blurred_bg, (0, 0), sigmaX=dim * 0.08)
        y_off = (dim - ch) // 2
        x_off = (dim - cw) // 2
        blurred_bg[y_off:y_off + ch, x_off:x_off + cw] = crop
        square = blurred_bg
    else:
        square = crop

    thumb = cv2.resize(square, (THUMBNAIL_SIZE, THUMBNAIL_SIZE), interpolation=cv2.INTER_LANCZOS4)
    pil_thumb = PILImage.fromarray(cv2.cvtColor(thumb, cv2.COLOR_BGR2RGB))
    pil_thumb.save(str(output_path), 'JPEG', quality=99)
    return True


def collect_image_paths(folder):
    paths = []
    for ext in SUPPORTED_EXTENSIONS:
        paths.extend(folder.rglob('*' + ext))
        paths.extend(folder.rglob('*' + ext.upper()))
    return sorted(set(paths))


def run_sort(config, step_cb=None):
    cfg = {**DEFAULT_CONFIG, **config}

    def cb(phase, current, total, msg):
        if step_cb:
            step_cb(phase, current, total, msg)

    input_path  = Path(cfg['input_folder'])
    output_path = Path(cfg['output_folder'])

    if not input_path.exists():
        raise FileNotFoundError('Input folder not found: ' + str(input_path))

    image_paths = collect_image_paths(input_path)
    if not image_paths:
        raise ValueError('No supported images found in: ' + str(input_path))

    cb('init', 0, 1, 'Found ' + str(len(image_paths)) + ' photos - loading AI model...')

    try:
        from insightface.app import FaceAnalysis
    except ImportError:
        raise ImportError('InsightFace not installed. Run: pip install insightface onnxruntime')

    app = FaceAnalysis(name='buffalo_l', providers=['CPUExecutionProvider'])
    app.prepare(ctx_id=0, det_size=(640, 640))

    cb('scan', 0, len(image_paths), 'Starting face detection...')

    face_data = []
    skip_counts = {'size': 0, 'confidence': 0, 'blur': 0, 'angle': 0}
    total_detected = 0

    for i, img_path in enumerate(image_paths):
        cb('scan', i + 1, len(image_paths), 'Scanning ' + img_path.name)
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
            yaw, pitch = 0.0, 0.0
            if hasattr(face, 'pose') and face.pose is not None:
                yaw, pitch = float(face.pose[0]), float(face.pose[1])
            face_data.append({
                'embedding':  face.embedding,
                'image_path': str(img_path),
                'bbox':       [float(v) for v in face.bbox],
                'det_score':  float(face.det_score),
                'sharpness':  sharpness,
                'yaw':        yaw,
                'pitch':      pitch,
            })

    if not face_data:
        raise ValueError('No faces passed the filters. Try lowering Min Face Size or Min Sharpness.')

    cb('cluster', 0, 1, 'Clustering ' + str(len(face_data)) + ' faces into people...')

    embeddings = normalize(np.array([d['embedding'] for d in face_data]))
    labels = DBSCAN(
        eps=cfg['dbscan_eps'],
        min_samples=cfg['dbscan_min_samples'],
        metric='cosine',
        n_jobs=-1
    ).fit_predict(embeddings)

    unique_people = set(l for l in labels if l != -1)
    noise_count = int((labels == -1).sum())

    cb('cluster', 1, 1, 'Found ' + str(len(unique_people)) + ' unique people')

    output_path.mkdir(parents=True, exist_ok=True)
    unmatched_path = output_path / 'unmatched'
    unmatched_path.mkdir(exist_ok=True)

    person_photos = {}
    person_faces = {}

    for i, label in enumerate(labels):
        img_path = face_data[i]['image_path']
        if label == -1:
            dest = unmatched_path / Path(img_path).name
            if not dest.exists():
                shutil.copy2(img_path, dest)
        else:
            person_photos.setdefault(label, set()).add(img_path)
            person_faces.setdefault(label, []).append(face_data[i])

    sorted_people = sorted(person_photos.items(), key=lambda x: len(x[1]), reverse=True)
    total_to_write = sum(len(p) for _, p in sorted_people)
    written = 0
    person_folders = []

    for rank, (label, photos) in enumerate(sorted_people, start=1):
        folder_name = 'person-' + str(rank).zfill(3)
        person_folder = output_path / folder_name
        person_folder.mkdir(exist_ok=True)

        for img_path in photos:
            dest = person_folder / Path(img_path).name
            if not dest.exists():
                shutil.copy2(img_path, dest)
            written += 1
            cb('write', written, total_to_write, 'Writing ' + folder_name + '...')

        thumb_path = person_folder / 'thumbnail.jpg'
        thumb_generated = False
        if label in person_faces:
            best_face = max(person_faces[label], key=face_quality_score)
            thumb_generated = generate_thumbnail(
                best_face['image_path'],
                best_face['bbox'],
                thumb_path
            )

        person_folders.append({
            'name':      folder_name,
            'count':     len(photos),
            'thumbnail': str(thumb_path) if thumb_generated else None,
        })

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
    print('\n📸  FaceSorter - CLI Mode')
    print('-' * 40)

    def cli_cb(phase, current, total, msg):
        print('  [' + phase.upper() + '] ' + msg)

    try:
        results = run_sort(DEFAULT_CONFIG, step_cb=cli_cb)
        r = results
        print('\n' + '=' * 40)
        print('Done!')
        print('  Photos scanned:  ' + str(r['total_photos']))
        print('  People found:    ' + str(r['people_found']))
        print('  Photos sorted:   ' + str(r['photos_sorted']))
        print('  Unmatched:       ' + str(r['unmatched']))
        print('  Output:          ' + r['output_folder'])
    except Exception as e:
        print('\nError: ' + str(e))
        sys.exit(1)
