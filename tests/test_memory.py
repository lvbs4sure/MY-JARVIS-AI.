import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import memory_store


class MemoryTests(unittest.TestCase):
    def test_create_update_delete_and_isolation(self):
        with tempfile.TemporaryDirectory() as folder:
            original = memory_store.DB_PATH
            try:
                memory_store.DB_PATH = Path(folder) / "person_a.db"
                memory_store.add_memory("My favourite colour is green")
                rows = memory_store.list_memories()
                self.assertEqual(rows[0][1], "My favourite colour is green")
                identity = rows[0][0]
                self.assertTrue(memory_store.update_memory(identity, "My favourite colour is blue"))
                self.assertEqual(memory_store.list_memories()[0][1], "My favourite colour is blue")
                memory_store.DB_PATH = Path(folder) / "person_b.db"
                self.assertEqual(memory_store.list_memories(), [])
                memory_store.DB_PATH = Path(folder) / "person_a.db"
                self.assertTrue(memory_store.delete_memory(identity))
                self.assertEqual(memory_store.list_memories(), [])
            finally:
                memory_store.DB_PATH = original

    def test_reject_oversized_memory(self):
        with self.assertRaises(ValueError):
            memory_store.add_memory("x" * 2001)

    def test_reject_blank_update_without_modifying_data(self):
        with tempfile.TemporaryDirectory() as folder:
            original = memory_store.DB_PATH
            try:
                memory_store.DB_PATH = Path(folder) / "notes.db"
                memory_store.add_memory("keep me")
                memory_id = memory_store.list_memories()[0][0]
                with self.assertRaises(ValueError):
                    memory_store.update_memory(memory_id, "  ")
                self.assertEqual(memory_store.list_memories()[0][1], "keep me")
            finally:
                memory_store.DB_PATH = original

    def test_search_memories_matches_text_and_literal_wildcards(self):
        with tempfile.TemporaryDirectory() as folder:
            original = memory_store.DB_PATH
            try:
                memory_store.DB_PATH = Path(folder) / "search.db"
                memory_store.add_memory("Project alpha")
                memory_store.add_memory("Budget 50%")
                memory_store.add_memory("File a_b")
                self.assertEqual([r[1] for r in memory_store.search_memories("alpha")], ["Project alpha"])
                self.assertEqual([r[1] for r in memory_store.search_memories("%")], ["Budget 50%"])
                self.assertEqual([r[1] for r in memory_store.search_memories("_")], ["File a_b"])
                self.assertEqual(memory_store.search_memories("   "), [])
                with self.assertRaises(ValueError):
                    memory_store.search_memories("x" * 201)
            finally:
                memory_store.DB_PATH = original

    def test_reject_non_text_notes_and_invalid_list_limits(self):
        with tempfile.TemporaryDirectory() as folder:
            original = memory_store.DB_PATH
            try:
                memory_store.DB_PATH = Path(folder) / "validation.db"
                memory_store.add_memory("preserve this")
                memory_id = memory_store.list_memories()[0][0]
                for invalid in (None, 42, b"bytes", ["not", "text"]):
                    with self.subTest(invalid=repr(invalid)):
                        with self.assertRaises(ValueError):
                            memory_store.add_memory(invalid)
                        with self.assertRaises(ValueError):
                            memory_store.update_memory(memory_id, invalid)
                for limit in (0, -1, 1001, True, 1.5, "10"):
                    with self.subTest(limit=repr(limit)):
                        with self.assertRaises(ValueError):
                            memory_store.list_memories(limit)
                self.assertEqual(memory_store.list_memories()[0][1], "preserve this")
            finally:
                memory_store.DB_PATH = original

    def test_reject_blank_memory(self):
        with self.assertRaises(ValueError):
            memory_store.add_memory("   ")


if __name__ == "__main__":
    unittest.main()
