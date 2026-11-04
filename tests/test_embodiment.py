import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
import memory_store
from animated_avatar import moving_face_markup
from camera_preview import CAMERA_HTML


class EmbodimentTests(unittest.TestCase):
    def test_model_text_is_never_inserted_as_html(self):
        markup=moving_face_markup('</script><img src=x onerror=alert(1)>')
        self.assertNotIn('</script><img',markup)
        self.assertIn('\\u003c/script\\u003e',markup)
        self.assertIn('voice.localService',markup)

    def test_mouth_is_driven_by_speech_events_and_respects_reduced_motion(self):
        markup=moving_face_markup('Hello',reduced_motion=True)
        self.assertIn('const reduced=true',markup)
        self.assertIn("phase==='speaking'&&time<mouthUntil",markup)
        self.assertIn("window.addEventListener('jarvis-boundary'",markup)
        self.assertIn('utterance.onboundary',markup)
        self.assertIn('cancelAnimationFrame',markup)
        self.assertNotIn('getUserMedia',markup)

    def test_camera_has_no_frame_capture_or_upload_path(self):
        for forbidden in ('MediaRecorder','toDataURL','fetch(', 'XMLHttpRequest','WebSocket','localStorage','sessionStorage'):
            self.assertNotIn(forbidden,CAMERA_HTML)
        self.assertIn('audio:false',CAMERA_HTML)
        self.assertIn('start.onclick=async',CAMERA_HTML)
        self.assertIn('incoming.getTracks().forEach(track=>track.stop())',CAMERA_HTML)
        self.assertIn('track.stop()',CAMERA_HTML)
        self.assertIn('visibilitychange',CAMERA_HTML)
        self.assertIn('if(pending)return',CAMERA_HTML)
        self.assertIn('20000',CAMERA_HTML)

    def test_camera_not_mounted_until_opt_in(self):
        with tempfile.TemporaryDirectory() as folder,patch.object(memory_store,'DB_PATH',Path(folder)/'test.db'),patch('camera_preview.render_camera_preview') as camera:
            app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=15).run()
            self.assertFalse(app.exception)
            camera.assert_not_called()
            app.toggle(key='show_local_camera').set_value(True).run()
            self.assertFalse(app.exception)
            camera.assert_called_once()
            app.toggle(key='show_local_camera').set_value(False).run()
            self.assertFalse(app.exception)
            self.assertEqual(camera.call_count,1)

    def test_original_scene_is_preserved_even_with_stale_avatar_choice(self):
        with tempfile.TemporaryDirectory() as folder,patch.object(memory_store,'DB_PATH',Path(folder)/'test.db'):
            app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=15).run()
            app.session_state['avatar_style']='Animated wireframe face'
            app.run()
            self.assertFalse(app.exception)
            self.assertTrue(any('Photorealistic holographic' in item.value for item in app.markdown))
