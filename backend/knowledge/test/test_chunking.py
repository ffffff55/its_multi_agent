"""长文档只切当前这一篇，分隔符不能因为漏逗号粘成一条。"""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
if str(KNOWLEDGE_DIR) not in sys.path:
    sys.path.insert(0, str(KNOWLEDGE_DIR))

from services.ingestion.chunking import MD_SEPARATORS, chunk_documents


def _doc(text: str, source: str):
    return SimpleNamespace(page_content=text, metadata={"source": source, "title": source})


class ChunkingTest(unittest.TestCase):
    def test_separators_keep_bold_marker_and_blank_line_apart(self):
        self.assertIn("\n**", MD_SEPARATORS)
        self.assertIn("\n\n", MD_SEPARATORS)
        self.assertNotIn("\n**\n\n", MD_SEPARATORS)

    def test_long_documents_are_split_one_at_a_time(self):
        short = _doc("短文", "short.md")
        long_a = _doc("甲" * 3000, "a.md")
        long_b = _doc("乙" * 3000, "b.md")
        seen = []

        def split_documents(docs):
            seen.append([doc.metadata["source"] for doc in docs])
            return [
                SimpleNamespace(page_content=doc.page_content[:4], metadata=dict(doc.metadata))
                for doc in docs
            ]

        chunks = chunk_documents([short, long_a, long_b], split_documents, threshold=3000)
        self.assertEqual(seen, [["a.md"], ["b.md"]])
        self.assertEqual(chunks[0].page_content, "短文")
        self.assertEqual(
            [chunk.page_content for chunk in chunks[1:]],
            ["文档来源:a.md\n甲甲甲甲", "文档来源:b.md\n乙乙乙乙"],
        )
        self.assertEqual(len(chunks), 3)

    def test_one_long_document_does_not_duplicate_a_short_sibling(self):
        short = _doc("只有一句", "short.md")
        long_doc = _doc("长" * 3000, "long.md")

        def split_documents(docs):
            self.assertEqual(len(docs), 1)
            return [SimpleNamespace(page_content="片段", metadata=dict(docs[0].metadata))]

        chunks = chunk_documents([short, long_doc], split_documents, threshold=3000)
        contents = [chunk.page_content for chunk in chunks]
        self.assertEqual(contents, ["只有一句", "文档来源:long.md\n片段"])

    def test_ingestion_uses_the_shared_chunking(self):
        source = KNOWLEDGE_DIR.joinpath("services", "ingestion", "ingestion_processor.py").read_text(encoding="utf-8")
        self.assertIn("chunk_documents(", source)
        self.assertIn("MD_SEPARATORS", source)


if __name__ == "__main__":
    unittest.main()
