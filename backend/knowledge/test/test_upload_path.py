"""上传文件名只能落在临时目录里，不能跟着 ../ 或绝对路径跑出去。"""
import sys
import tempfile
import unittest
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
if str(KNOWLEDGE_DIR) not in sys.path:
    sys.path.insert(0, str(KNOWLEDGE_DIR))

from repositories.file_repository import resolve_upload_path


class UploadPathTest(unittest.TestCase):
    def test_keeps_a_normal_name_inside_the_temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(resolve_upload_path(temp_dir, "0430-联想手机常见问题.md"))
            self.assertEqual(destination.parent, Path(temp_dir).resolve())
            self.assertEqual(destination.name, "0430-联想手机常见问题.md")

    def test_rejects_paths_that_leave_the_temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            for name in ("../.env", "..", "/etc/passwd", "foo/../../outside.md", "a\\..\\secret.md", "bad\x00.md", "", None):
                with self.subTest(name=name):
                    with self.assertRaises(ValueError):
                        resolve_upload_path(temp_dir, name)

    def test_uses_only_the_last_path_segment(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(resolve_upload_path(temp_dir, "nested/dir/note.md"))
            self.assertEqual(destination.parent, Path(temp_dir).resolve())
            self.assertEqual(destination.name, "note.md")

    def test_upload_route_calls_the_guard(self):
        source = KNOWLEDGE_DIR.joinpath("api", "routers.py").read_text(encoding="utf-8")
        self.assertIn("resolve_upload_path", source)
        self.assertIn("temp_file_path = None", source)


if __name__ == "__main__":
    unittest.main()
