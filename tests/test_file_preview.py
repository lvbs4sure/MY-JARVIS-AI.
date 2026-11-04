import io
import unittest
from file_preview import preview_upload


class PreviewTests(unittest.TestCase):
    def upload(self, data, name="sample.txt", size=None):
        stream=io.BytesIO(data)
        stream.name=name
        stream.size=len(data) if size is None else size
        return stream

    def test_unicode_bom_truncation_and_inert_content(self):
        raw="<script>never execute</script>"+"x"*5000
        name,text,size,truncated=preview_upload(self.upload(b"\xef\xbb\xbf"+raw.encode(),r"C:\fakepath\sample.md"))
        self.assertEqual(name,"sample.md")
        self.assertTrue(text.startswith("<script>"))
        self.assertEqual(len(text),4000)
        self.assertTrue(truncated)

    def test_rejects_oversize_even_if_size_metadata_is_wrong(self):
        for reported in (1,1_000_001):
            with self.assertRaises(ValueError):
                preview_upload(self.upload(b"x"*1_000_001,size=reported))

    def test_binary_wrong_extension_invalid_encoding_rejected(self):
        for data,name in [(b"\x00","a.txt"),(b"\xff","a.csv"),(b"x",".env"),(b"x","code.py")]:
            with self.subTest(name=name,data=data),self.assertRaises(ValueError):
                preview_upload(self.upload(data,name))

    def test_reader_position_is_preserved(self):
        upload=self.upload(b"hello")
        upload.seek(2)
        self.assertEqual(preview_upload(upload)[1],"hello")
        self.assertEqual(upload.tell(),2)
