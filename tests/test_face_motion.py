"""Pure tests: facial signals must not masquerade as a rendered avatar."""
import unittest

from face_motion import FaceMotionController, FacePose, rig_controls, viseme_rig_controls
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

    def test_rig_controls_are_named_and_normalized(self):
        pose = self.motion.sample(90)
        controls = rig_controls(pose)
        self.assertEqual(controls["blink_left"], 1)
        self.assertEqual(controls["blink_right"], 1)
        self.assertEqual(controls["mouth_open"], 0)
        self.assertTrue(-1 <= controls["gaze_horizontal"] <= 1)

    def test_rig_controls_reject_invalid_values(self):
        with self.assertRaises(TypeError):
            rig_controls({})
        with self.assertRaises(ValueError):
            rig_controls(FacePose(2, 0, 0, 0, "ready"))
        with self.assertRaises(ValueError):
            rig_controls(FacePose(0, float("nan"), 0, 0, "ready"))

    def test_viseme_shapes_follow_actual_audio_clock(self):
        weights = viseme_rig_controls(self.timeline, 150, playing=True)
        self.assertEqual(len(weights), 22)
        self.assertEqual(weights["viseme_04"], 1)
        self.assertEqual(weights["viseme_00"], 0)
        self.assertEqual(sum(weights.values()), 1)
        self.assertEqual(viseme_rig_controls(self.timeline, 350, playing=True)["viseme_00"], 1)

    def test_visemes_close_on_pause_and_interruption(self):
        for kwargs in ({"playing": False}, {"playing": True, "interrupted": True}):
            weights = viseme_rig_controls(self.timeline, 150, **kwargs)
            self.assertEqual(weights["viseme_00"], 1)
            self.assertEqual(weights["viseme_04"], 0)

    def test_viseme_adapter_rejects_untrusted_inputs(self):
        with self.assertRaises(TypeError):
            viseme_rig_controls({}, 150, playing=True)
        with self.assertRaises(ValueError):
            viseme_rig_controls(self.timeline, 150, playing=1)
        with self.assertRaises(ValueError):
            viseme_rig_controls(self.timeline, float("nan"), playing=True)

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
