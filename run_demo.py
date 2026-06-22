from pathlib import Path

from codealpha_ai.tracking import CentroidTracker, Detection


def main() -> None:
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    tracker = CentroidTracker(max_distance=30)
    first = tracker.update([Detection((10, 10, 30, 30), "person", 0.9)])
    second = tracker.update([Detection((14, 12, 34, 32), "person", 0.91)])
    output_path = output_dir / "tracking_demo.txt"
    output_path.write_text(
        f"Frame 1 track id: {first[0].track_id}\nFrame 2 track id: {second[0].track_id}\n",
        encoding="utf-8",
    )
    print(f"Tracking demo written to {output_path}")


if __name__ == "__main__":
    main()
