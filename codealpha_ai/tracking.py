"""Object tracking utilities with a centroid tracker core."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Dict, Iterable, List, Sequence, Tuple


BBox = Tuple[int, int, int, int]


@dataclass(frozen=True)
class Detection:
    bbox: BBox
    label: str = "object"
    score: float = 1.0

    @property
    def centroid(self) -> Tuple[float, float]:
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)


@dataclass
class Track:
    track_id: int
    bbox: BBox
    label: str
    score: float
    missed: int = 0

    @property
    def centroid(self) -> Tuple[float, float]:
        x1, y1, x2, y2 = self.bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)


class CentroidTracker:
    """Assigns stable IDs to detections by nearest-centroid matching."""

    def __init__(self, *, max_distance: float = 50.0, max_missed: int = 5) -> None:
        if max_distance <= 0:
            raise ValueError("max_distance must be positive.")
        if max_missed < 0:
            raise ValueError("max_missed cannot be negative.")

        self.max_distance = max_distance
        self.max_missed = max_missed
        self._next_id = 1
        self._tracks: Dict[int, Track] = {}

    def update(self, detections: Sequence[Detection]) -> List[Track]:
        unmatched_tracks = set(self._tracks)
        updated_tracks: Dict[int, Track] = {}

        for detection in detections:
            track_id = self._find_nearest_track(detection, unmatched_tracks)
            if track_id is None:
                track_id = self._next_id
                self._next_id += 1
            else:
                unmatched_tracks.remove(track_id)

            updated_tracks[track_id] = Track(
                track_id=track_id,
                bbox=detection.bbox,
                label=detection.label,
                score=detection.score,
                missed=0,
            )

        for track_id in unmatched_tracks:
            previous = self._tracks[track_id]
            previous.missed += 1
            if previous.missed <= self.max_missed:
                updated_tracks[track_id] = previous

        self._tracks = updated_tracks
        return sorted(self._tracks.values(), key=lambda track: track.track_id)

    def _find_nearest_track(self, detection: Detection, candidates: Iterable[int]) -> int | None:
        best_id = None
        best_distance = self.max_distance

        for track_id in candidates:
            track = self._tracks[track_id]
            distance = _distance(detection.centroid, track.centroid)
            if distance <= best_distance:
                best_distance = distance
                best_id = track_id

        return best_id


def _distance(left: Tuple[float, float], right: Tuple[float, float]) -> float:
    return math.sqrt((left[0] - right[0]) ** 2 + (left[1] - right[1]) ** 2)


def draw_tracks(frame, tracks: Sequence[Track]):
    """Draw track boxes on an OpenCV frame.

    This function imports OpenCV lazily so the core tracker remains testable
    without optional video dependencies installed.
    """

    try:
        import cv2
    except ImportError as exc:
        raise RuntimeError("Install opencv-python to draw tracks on video frames.") from exc

    for track in tracks:
        x1, y1, x2, y2 = track.bbox
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 180, 90), 2)
        cv2.putText(
            frame,
            f"{track.label} #{track.track_id}",
            (x1, max(15, y1 - 8)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 180, 90),
            2,
        )
    return frame
