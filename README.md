# 📸 FaceSorter

**AI-powered event photo organizer for photographers.**
Drop in a shoot, get back one folder per person — ready to upload as Pixieset Sets.

Built with [InsightFace](https://github.com/deepinsight/insightface) · Python · Streamlit

---

## What it does

FaceSorter scans a folder of event photos, detects every face, filters out background
and blurry people, and clusters the remaining faces by identity. Each unique person
gets their own output subfolder — no names needed, just clean groupings ready for
client delivery.

```
input/
    IMG_001.jpg
    IMG_002.jpg
    ...

output/
    person-001/   ← 54 photos  (most-photographed person first)
    person-002/   ← 41 photos
    person-003/   ← 38 photos
    ...
    unmatched/    ← worth a quick look
```

Each `person-XXX` folder maps directly to a **Set** inside a Pixieset Collection.

---

## Setup (one time, ~5 minutes)

### 1. Python

Make sure you have Python 3.9 or higher:
```bash
python3 --version
```
Download from [python.org](https://www.python.org/downloads/) if needed.

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Folder structure

Create a working directory with this layout:
```
FaceSorter/
    app.py
    face_sorter.py
    requirements.txt
    input/        ← drop your event photos here
    output/       ← sorted folders appear here (auto-created)
```

---

## Running the dashboard

```bash
streamlit run app.py
```

Your browser opens automatically to the FaceSorter dashboard. From there:

1. Set the input/output folder paths in the sidebar
2. Adjust any filters if needed (defaults work well for most events)
3. Click **Sort Photos** and wait — large events take 5–20 min on Mac
4. Review the results, then upload each `person-XXX` folder to Pixieset

> **First run:** InsightFace will download the `buffalo_l` model (~200MB).
> Make sure you're on WiFi. This only happens once.

---

## Running from terminal (no dashboard)

```bash
python3 face_sorter.py
```

Uses the default settings in `face_sorter.py`. Edit the `DEFAULT_CONFIG` dict
at the top of the file to change paths or thresholds.

---

## Settings reference

All settings are available as sliders in the dashboard sidebar.
For CLI use, edit `DEFAULT_CONFIG` in `face_sorter.py`.

| Setting | Default | What it does |
|---|---|---|
| `min_face_size_ratio` | `0.04` | Face must be ≥ this fraction of image width. Raise to exclude background people. |
| `min_confidence` | `0.55` | InsightFace detection confidence. Lower catches more faces. |
| `min_sharpness` | `45` | Laplacian sharpness score. Lower = blur-tolerant (candid-friendly). |
| `max_yaw_angle` | `60°` | Max left/right head turn. 60°+ is generous for candids. |
| `max_pitch_angle` | `45°` | Max up/down tilt. |
| `dbscan_eps` | `0.45` | Matching strictness. Lower = fewer mis-groupings. Raise if same person splits into two folders. |
| `dbscan_min_samples` | `2` | Minimum photos a person must appear in to get their own folder. |

### Tuning tips

- **Too many background strangers?** Raise `min_face_size_ratio` to `0.06`
- **Missing candid shots?** Lower `min_sharpness` to `25–30` and raise `max_yaw_angle` to `75`
- **Same person split across two folders?** Raise `dbscan_eps` to `0.50–0.55`
- **Too many tiny folders?** Raise `dbscan_min_samples` to `3` or `4`

---

## Supported formats

JPG · JPEG · TIFF · TIF

---

## After sorting

1. Open your `output/` folder
2. Spot-check a few person folders — merge any that look like the same person
3. In Pixieset, create a new **Collection** for the event
4. Upload each `person-XXX` folder as a separate **Set** within that collection
5. Clients can browse to their own Set and download their photos

---

## Notes

- Photos of the same person may occasionally split across two folders if lighting or
  angle varies significantly. A quick merge before uploading fixes this.
- The `unmatched/` folder contains faces that didn't cluster confidently — worth a
  look before delivery.
- FaceSorter runs entirely on your machine. No photos leave your computer.

---

## License

MIT
