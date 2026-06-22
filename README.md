# Object Detection Tracker

Standalone object detection and tracking project.

## Features

- Centroid tracker that keeps stable IDs across frames
- Optional YOLO detection through Ultralytics
- OpenCV motion-detection fallback when YOLO is not installed
- Bounding box and tracking ID drawing helper
- Unit tests for ID stability and missed-frame cleanup

## Run Tests

```powershell
python -m unittest discover -s tests -v
```

## Run Demo

```powershell
python run_demo.py
```

Demo output is written to `outputs/tracking_demo.txt`.

## Run Video Tracking

```powershell
python -m pip install -r requirements.txt
python apps/object_detection_tracking_app.py --source 0
```

Press `q` to close the OpenCV window.

To use YOLO:

```powershell
python apps/object_detection_tracking_app.py --source sample_video.mp4 --model yolov8n.pt
```

## Files

- `object_tracker/tracking.py` - centroid tracker and drawing helper
- `apps/object_detection_tracking_app.py` - OpenCV/YOLO video runner
- `tests/test_tracking.py` - automated tests
