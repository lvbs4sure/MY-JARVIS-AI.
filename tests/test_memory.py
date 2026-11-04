import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import memory_store


class MemoryTests(unittest.TestCase):
    def test_total_count_is_not_limited_to_the_visible_page(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(memory_store, "DB_PATH", Path(folder) / "notes.db"):
                with memory_store.connect() as db:
                    db.executemany("INSERT INTO memories(note) VALUES (?)", [(f"Test {index}",) for index in range(101)])
                self.assertEqual(len(memory_store.list_memories()), 100)
                self.assertEqual(memory_store.count_memories(), 101)

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

    def test_invalid_memory_ids_do_not_modify_notes(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(memory_store, "DB_PATH", Path(folder) / "ids.db"):
                memory_store.add_memory("keep this")
                for invalid in (None, True, False, 0, -1, 1.0, "1", b"1"):
                    with self.subTest(invalid=repr(invalid)):
                        with self.assertRaises(ValueError):
                            memory_store.update_memory(invalid, "overwrite")
                        with self.assertRaises(ValueError):
                            memory_store.delete_memory(invalid)
                self.assertEqual(memory_store.list_memories()[0][1], "keep this")

    def test_search_rejects_invalid_limits_even_when_query_is_blank(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(memory_store, "DB_PATH", Path(folder) / "search_limits.db"):
                memory_store.add_memory("unchanged")
                for query in ("", "   ", "unchanged"):
                    for limit in (0, -1, 101, True, 1.5, "5", None):
                        with self.subTest(query=query, limit=repr(limit)):
                            with self.assertRaises(ValueError):
                                memory_store.search_memories(query, limit)
                self.assertEqual(memory_store.list_memories()[0][1], "unchanged")

    def test_get_memory_is_scoped_to_installation_and_validates_ids(self):
        with tempfile.TemporaryDirectory() as folder:
            first = Path(folder) / "first.db"
            second = Path(folder) / "second.db"
            with patch.object(memory_store, "DB_PATH", first):
                memory_store.add_memory("private first installation")
                first_id = memory_store.list_memories()[0][0]
                self.assertEqual(memory_store.get_memory(first_id)[1], "private first installation")
                self.assertIsNone(memory_store.get_memory(first_id + 1))
                for invalid in (None, True, False, 0, -1, "1", 1.0):
                    with self.subTest(invalid=repr(invalid)):
                        with self.assertRaises(ValueError):
                            memory_store.get_memory(invalid)
            with patch.object(memory_store, "DB_PATH", second):
                self.assertIsNone(memory_store.get_memory(first_id))
                memory_store.add_memory("private second installation")
                self.assertEqual(memory_store.get_memory(first_id)[1], "private second installation")
            with patch.object(memory_store, "DB_PATH", first):
                self.assertEqual(memory_store.get_memory(first_id)[1], "private first installation")

    def test_search_treats_backslashes_and_sql_as_literal_text(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(memory_store, "DB_PATH", Path(folder) / "literal_search.db"):
                memory_store.add_memory(r"Windows path C:\\Users\\owner")
                memory_store.add_memory("A note with a single quote: owner's")
                memory_store.add_memory("Ordinary note")
                self.assertEqual(
                    [row[1] for row in memory_store.search_memories(r"C:\\Users")],
                    [r"Windows path C:\\Users\\owner"],
                )
                self.assertEqual(
                    [row[1] for row in memory_store.search_memories("owner's")],
                    ["A note with a single quote: owner's"],
                )
                self.assertEqual(memory_store.search_memories("' OR 1=1 --"), [])
                self.assertEqual(memory_store.count_memories(), 3)

    @unittest.skipUnless(os.name == "posix", "POSIX file permissions only")
    def test_new_private_database_is_owner_only(self):
        with tempfile.TemporaryDirectory() as folder:
            database = Path(folder) / "private.db"
            with patch.object(memory_store, "DB_PATH", database):
                memory_store.add_memory("private note")
                self.assertEqual(database.stat().st_mode & 0o777, 0o600)
                self.assertEqual(memory_store.list_memories()[0][1], "private note")

    @unittest.skipUnless(os.name == "posix", "POSIX file permissions only")
    def test_existing_database_permissions_are_not_changed(self):
        with tempfile.TemporaryDirectory() as folder:
            database = Path(folder) / "existing.db"
            database.touch(mode=0o640)
            database.chmod(0o640)
            with patch.object(memory_store, "DB_PATH", database):
                memory_store.add_memory("existing note")
            self.assertEqual(database.stat().st_mode & 0o777, 0o640)

    def test_symlinked_database_is_rejected_without_changing_target(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "owner.db"
            link = Path(folder) / "friend.db"
            with patch.object(memory_store, "DB_PATH", target):
                memory_store.add_memory("owner private note")
            try:
                link.symlink_to(target)
            except (OSError, NotImplementedError):
                self.skipTest("Creating symbolic links is unavailable")
            with patch.object(memory_store, "DB_PATH", link):
                with self.assertRaises(ValueError):
                    memory_store.list_memories()
                with self.assertRaises(ValueError):
                    memory_store.add_memory("friend note")
            with patch.object(memory_store, "DB_PATH", target):
                self.assertEqual([row[1] for row in memory_store.list_memories()], ["owner private note"])

    def test_reject_blank_memory(self):
        with self.assertRaises(ValueError):
            memory_store.add_memory("   ")


if __name__ == "__main__":
    unittest.main()
