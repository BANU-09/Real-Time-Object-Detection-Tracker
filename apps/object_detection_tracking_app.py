from argparse import ArgumentParser
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from codealpha_ai.tracking import CentroidTracker, Detection, draw_tracks


def detections_from_yolo(result) -> list[Detection]:
    detections: list[Detection] = []
    names = getattr(result, "names", {})
    boxes = getattr(result, "boxes", None)
    if boxes is None:
        return detections

    for box in boxes:
        xyxy = [int(value) for value in box.xyxy[0].tolist()]
        class_id = int(box.cls[0].item()) if box.cls is not None else -1
        label = names.get(class_id, "object")
        score = float(box.conf[0].item()) if box.conf is not None else 1.0
        detections.append(Detection(tuple(xyxy), label, score))
    return detections


def detections_from_motion(frame, subtractor) -> list[Detection]:
    import cv2

    mask = subtractor.apply(frame)
    _, mask = cv2.threshold(mask, 200, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    detections: list[Detection] = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < 900:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        detections.append(Detection((x, y, x + w, y + h), "moving_object", min(1.0, area / 5000)))
    return detections


def run(source: str, model_path: str | None) -> None:
    import cv2

    yolo_model = None
    if model_path:
        try:
            from ultralytics import YOLO

            yolo_model = YOLO(model_path)
            print(f"Loaded YOLO model: {model_path}")
        except ImportError:
            print("ultralytics is not installed. Falling back to OpenCV motion detection.")

    source_value = int(source) if source.isdigit() else source
    capture = cv2.VideoCapture(source_value)
    if not capture.isOpened():
        raise RuntimeError(f"Could not open video source: {source}")

    tracker = CentroidTracker(max_distance=70, max_missed=8)
    subtractor = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=25, detectShadows=True)

    while True:
        ok, frame = capture.read()
        if not ok:
            break

        if yolo_model is not None:
            result = yolo_model(frame, verbose=False)[0]
            detections = detections_from_yolo(result)
        else:
            detections = detections_from_motion(frame, subtractor)

        tracks = tracker.update(detections)
        output = draw_tracks(frame, tracks)
        cv2.imshow("CodeAlpha Object Detection and Tracking", output)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    capture.release()
    cv2.destroyAllWindows()


def main() -> None:
    parser = ArgumentParser(description="Object detection and tracking demo.")
    parser.add_argument("--source", default="0", help="Webcam index or video file path.")
    parser.add_argument("--model", default=None, help="Optional YOLO model path, for example yolov8n.pt.")
    args = parser.parse_args()
    run(args.source, args.model)


if __name__ == "__main__":
    main()
