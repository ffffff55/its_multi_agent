"""向量库入库必须把每一批都写完，不能在第一批之后返回。"""
import ast
import sys
import unittest
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
if str(KNOWLEDGE_DIR) not in sys.path:
    sys.path.insert(0, str(KNOWLEDGE_DIR))

from utils.batches import iter_batches


def _returns_inside_for(function: ast.AST) -> bool:
    for node in ast.walk(function):
        if isinstance(node, ast.For):
            for child in ast.walk(node):
                if isinstance(child, ast.Return):
                    return True
    return False


class BatchWriteTest(unittest.TestCase):
    def test_iter_batches_keeps_every_item(self):
        items = [f"chunk-{index}" for index in range(20)]
        batches = list(iter_batches(items, 16))
        self.assertEqual(batches, [items[:16], items[16:]])
        self.assertEqual([item for batch in batches for item in batch], items)

    def test_add_documents_does_not_return_inside_the_loop(self):
        source = KNOWLEDGE_DIR.joinpath("repositories", "vector_store_repository.py").read_text(encoding="utf-8")
        self.assertIn("iter_batches", source)
        tree = ast.parse(source)
        functions = [
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "add_documents"
        ]
        self.assertEqual(functions, [], "add_documents 应是类方法，不应是模块函数")
        methods = [
            node
            for cls in tree.body
            if isinstance(cls, ast.ClassDef) and cls.name == "VectorStoreRepository"
            for node in cls.body
            if isinstance(node, ast.FunctionDef) and node.name == "add_documents"
        ]
        self.assertEqual(len(methods), 1)
        self.assertFalse(
            _returns_inside_for(methods[0]),
            "add_documents 不能在 for 循环里 return，否则 16 条之后的切片不会入库",
        )


if __name__ == "__main__":
    unittest.main()
