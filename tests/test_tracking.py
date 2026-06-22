import unittest

from codealpha_ai.tracking import CentroidTracker, Detection


class TrackingTests(unittest.TestCase):
    def test_keeps_same_id_for_nearby_detection_across_frames(self):
        tracker = CentroidTracker(max_distance=30)

        first_frame = tracker.update([Detection((10, 10, 30, 30), "person", 0.9)])
        second_frame = tracker.update([Detection((14, 12, 34, 32), "person", 0.91)])

        self.assertEqual(len(first_frame), 1)
        self.assertEqual(len(second_frame), 1)
        self.assertEqual(first_frame[0].track_id, second_frame[0].track_id)

    def test_removes_track_after_too_many_missed_frames(self):
        tracker = CentroidTracker(max_distance=30, max_missed=1)

        tracker.update([Detection((10, 10, 30, 30), "person", 0.9)])
        tracker.update([])
        tracks = tracker.update([])

        self.assertEqual(tracks, [])


if __name__ == "__main__":
    unittest.main()
