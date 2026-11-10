"""锁住检索里已经犯过的两处笔误，避免再把问答接口打崩。"""
import ast
import unittest
from pathlib import Path

RETRIEVAL = Path(__file__).resolve().parents[1].joinpath("services", "retrieval_service.py")


def _function(tree: ast.AST, class_name: str, name: str) -> ast.AST:
    for cls in tree.body:
        if isinstance(cls, ast.ClassDef) and cls.name == class_name:
            for node in cls.body:
                if isinstance(node, ast.FunctionDef) and node.name == name:
                    return node
    raise AssertionError(f"找不到 {class_name}.{name}")


class RetrievalGuardTest(unittest.TestCase):
    def test_long_chunk_metadata_key_has_no_trailing_colon(self):
        source = RETRIEVAL.read_text(encoding="utf-8")
        self.assertNotIn("chunk_index:", source)
        self.assertIn('CHUNK_INDEX_KEY = "chunk_index"', source)
        self.assertIn("SIMILARITY_KEY", source)
        self.assertIn("rough_rank_metadata", source)

    def test_unreadable_title_file_does_not_drop_the_rest(self):
        tree = ast.parse(RETRIEVAL.read_text(encoding="utf-8"))
        function = _function(tree, "RetrievalService", "_search_based_title")
        for node in ast.walk(function):
            if isinstance(node, ast.ExceptHandler):
                for child in ast.walk(node):
                    self.assertNotIsInstance(child, ast.Return)


if __name__ == "__main__":
    unittest.main()
