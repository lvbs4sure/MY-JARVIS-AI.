"""Pure tests: facial signals must not masquerade as a rendered avatar."""
import unittest

from face_motion import FaceMotionController
from lip_sync import LipTimeline, VisemeCue


class FaceMotionTests(unittest.TestCase):
    def setUp(self):
        self.motion = FaceMotionController()
        self.timeline = LipTimeline([VisemeCue(100, 200, 4)], 500, transition_ms=0)

    def test_blink_closes_and_opens_without_frame_history(self):
        self.assertEqual(self.motion.sample(0).blink, 0)
        self.assertEqual(self.motion.sample(90).blink, 1)
        self.assertEqual(self.motion.sample(180).blink, 0)
        self.assertEqual(self.motion.sample(4490).blink, 1)

    def test_no_fake_mouth_without_audio_and_timeline(self):
        self.assertEqual(self.motion.sample(150, state="speaking").mouth_open, 0)
        self.assertEqual(self.motion.sample(150, state="speaking", audio_playing=True).mouth_open, 0)
        self.assertEqual(self.motion.sample(150, state="ready", timeline=self.timeline,
                                            audio_playing=True, audio_position_ms=150).mouth_open, 0)

    def test_audio_clock_controls_mouth_and_seeks(self):
        def sample(position, **kwargs):
            return self.motion.sample(500, state="speaking", timeline=self.timeline,
                                      audio_playing=True, audio_position_ms=position, **kwargs).mouth_open
        self.assertEqual(sample(150), 1)
        self.assertEqual(sample(350), 0)
        self.assertEqual(sample(150), 1)
        self.assertEqual(sample(150, interrupted=True), 0)

    def test_pause_and_reduced_motion_close_mouth(self):
        pose = self.motion.sample(90, state="paused", timeline=self.timeline,
                                  audio_playing=False, audio_position_ms=150)
        self.assertEqual(pose.mouth_open, 0)
        pose = self.motion.sample(90, state="speaking", timeline=self.timeline,
                                  audio_playing=True, audio_position_ms=150,
                                  reduced_motion=True)
        self.assertEqual((pose.blink, pose.gaze_x, pose.gaze_y, pose.mouth_open),
                         (0, 0, 0, 0))

    def test_rejects_bad_clock_states_and_flags(self):
        with self.assertRaises(ValueError):
            self.motion.sample(float("nan"))
        with self.assertRaises(ValueError):
            self.motion.sample(-1)
        with self.assertRaises(ValueError):
            self.motion.sample(0, state="imaginary")
        with self.assertRaises(ValueError):
            self.motion.sample(0, audio_playing=1)
        with self.assertRaises(ValueError):
            FaceMotionController(blink_interval_ms=10)


if __name__ == "__main__":
    unittest.main()
