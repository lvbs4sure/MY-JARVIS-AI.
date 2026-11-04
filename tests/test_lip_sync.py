import unittest
from lip_sync import VisemeCue,LipTimeline,from_sapi_events


class LipSyncTests(unittest.TestCase):
    def timeline(self):
        return LipTimeline([VisemeCue(100,100,2),VisemeCue(200,100,21)],400,20)

    def test_silence_pause_interrupt_and_clip_end_close_mouth(self):
        timeline=self.timeline()
        for position in (0,99,300,400,900):
            self.assertEqual(timeline.sample(position,playing=True),{0:1.0})
        self.assertEqual(timeline.sample(150,playing=False),{0:1.0})
        self.assertEqual(timeline.sample(150,playing=True,interrupted=True),{0:1.0})

    def test_real_audio_position_supports_seek_and_frame_skip(self):
        timeline=self.timeline()
        self.assertEqual(timeline.sample(250,playing=True),{21:1.0})
        self.assertEqual(timeline.sample(150,playing=True),{2:1.0})
        self.assertEqual(timeline.sample(250,playing=True),{21:1.0})
        self.assertEqual(timeline.sample(110,playing=True),{0:0.5,2:0.5})
        self.assertEqual(timeline.sample(210,playing=True),{2:0.5,21:0.5})

    def test_invalid_and_unordered_data_rejected(self):
        for offset in (-1,float('nan'),float('inf'),True,'10'):
            with self.assertRaises(ValueError):VisemeCue(offset,100,2)
        for viseme in (-1,22,True,1.5,'1'):
            with self.assertRaises(ValueError):VisemeCue(0,100,viseme)
        for cues in ([VisemeCue(200,100,1),VisemeCue(100,100,2)],[VisemeCue(350,100,1)]):
            with self.assertRaises(ValueError):LipTimeline(cues,400)
        with self.assertRaises(ValueError):from_sapi_events([{'text':'not timing data'}],400)

    def test_short_cues_weights_remain_bounded_and_normalized(self):
        timeline=LipTimeline([VisemeCue(10,2,2),VisemeCue(30,20,18)],100)
        for position in range(101):
            weights=timeline.sample(position,playing=True)
            self.assertAlmostEqual(sum(weights.values()),1)
            self.assertTrue(all(0<=value<=1 for value in weights.values()))
        self.assertEqual(timeline.sample(31,playing=True),{0:0.9,18:0.1})

    def test_no_cues_never_fabricates_speech(self):
        timeline=from_sapi_events([],1000)
        self.assertEqual(timeline.sample(300,playing=True),{0:1.0})
