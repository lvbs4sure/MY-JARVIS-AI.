import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
import chat_history
import memory_store


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        db=patch.object(chat_history,"DB_PATH",Path(self.folder.name)/"history.db")
        db.start();self.addCleanup(db.stop)

    def test_default_off_creates_no_database(self):
        chat_history.sync_history({"chat":[{"role":"user","content":"Private fixture"}]})
        self.assertEqual(chat_history.list_conversations(),[])
        self.assertFalse(chat_history.DB_PATH.exists())

    def test_persistence_update_and_installation_isolation(self):
        messages=[{"role":"user","content":"Unicode café and SQL ' quote"},{"role":"assistant","content":"Remembered response"}]
        identity=chat_history.save_conversation(messages)
        self.assertEqual(chat_history.load_conversation(identity),messages)
        chat_history.save_conversation(messages+[{"role":"user","content":"Next turn"}],identity)
        self.assertEqual(len(chat_history.list_conversations()),1)
        self.assertEqual(len(chat_history.load_conversation(identity)),3)
        with patch.object(chat_history,"DB_PATH",Path(self.folder.name)/"other.db"):
            self.assertIsNone(chat_history.load_conversation(identity))
            self.assertFalse(chat_history.DB_PATH.exists())

    def test_validation_and_size_failure_leave_existing_history(self):
        original=[{"role":"user","content":"Keep me"}]
        identity=chat_history.save_conversation(original)
        for invalid in ("../memory.db","' OR 1=1 --",None,1):
            with self.assertRaises(ValueError):chat_history.load_conversation(invalid)
        with self.assertRaises(ValueError):chat_history.save_conversation([{"role":"user","content":"x"*2_000_001}],identity)
        self.assertEqual(chat_history.load_conversation(identity),original)

    def test_no_credentials_failed_answers_or_interrupted_turns_saved(self):
        with patch.dict(os.environ,{"GEMINI_API_KEY":"private-key-marker"}):
            identity=chat_history.save_conversation([
                {"role":"user","content":"private-key-marker"},
                {"role":"assistant","content":"Provider failure","ok":False},
                {"role":"user","content":"Interrupted prompt","cancelled":True}])
            self.assertEqual(chat_history.load_conversation(identity),[{"role":"user","content":"[redacted API key]"}])
            self.assertNotIn(b"private-key-marker",chat_history.DB_PATH.read_bytes())

    def test_dashboard_save_reopen_without_model_call(self):
        with patch.object(memory_store,"DB_PATH",Path(self.folder.name)/"memories.db"),patch("jarvis_ai.generate_reply_result") as model:
            app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/"app.py"),default_timeout=15)
            app.session_state["chat"]=[{"role":"user","content":"History fixture"},{"role":"assistant","content":"Local reply fixture"}]
            app.run()
            self.assertFalse(chat_history.DB_PATH.exists())
            app.toggle(key="save_chat_history").set_value(True).run()
            self.assertFalse(app.exception)
            self.assertEqual(len(chat_history.list_conversations()),1)
            app.button(key="new_conversation").click().run()
            self.assertEqual(app.session_state["chat"],[])
            app.button(key="open_history").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state["chat"][-1]["content"],"Local reply fixture")
            model.assert_not_called()
            # A fresh app session reads the same persisted chat, without using private memories.
            restarted=AppTest.from_file(str(Path(__file__).resolve().parents[1]/"app.py"),default_timeout=15).run()
            restarted.button(key="open_history").click().run()
            self.assertEqual(restarted.session_state["chat"][-1]["content"],"Local reply fixture")
            self.assertEqual(memory_store.list_memories(),[])

    def test_clear_session_never_overwrites_saved_conversation(self):
        original=[{"role":"user","content":"Keep the saved original"},{"role":"assistant","content":"Original answer"}]
        identity=chat_history.save_conversation(original)
        with patch.object(memory_store,"DB_PATH",Path(self.folder.name)/"memories.db"):
            app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/"app.py"),default_timeout=15)
            app.session_state["chat"]=original.copy()
            app.session_state["history_id"]=identity
            app.session_state["save_chat_history"]=True
            app.run()
            next(button for button in app.button if button.label=="Confirm clear conversation").click().run()
            self.assertFalse(app.exception)
            app.session_state["chat"]=[{"role":"user","content":"A separate new conversation"}]
            app.run()
            self.assertEqual(len(chat_history.list_conversations()),2)
            self.assertEqual(chat_history.load_conversation(identity),original)
