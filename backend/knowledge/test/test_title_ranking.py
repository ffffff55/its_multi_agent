"""标题粗排遇到空标题时要跳过，不能在排序时 KeyError。"""
import sys
import unittest
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]
if str(KNOWLEDGE_DIR) not in sys.path:
    sys.path.insert(0, str(KNOWLEDGE_DIR))

from services.title_ranking import rough_rank_metadata


class TitleRankingTest(unittest.TestCase):
    def test_empty_title_does_not_crash_and_is_dropped(self):
        rows = [
            {"path": "a.md", "title": ""},
            {"path": "b.md", "title": "   "},
            {"path": "c.md", "title": None},
            {"path": "d.md"},
            {"path": "e.md", "title": "开机黑屏"},
        ]
        ranked = rough_rank_metadata("开机黑屏", rows, cut_words=lambda text: [text])
        self.assertEqual([item["path"] for item in ranked], ["e.md"])
        self.assertIn("roughing_score", ranked[0])

    def test_higher_overlap_ranks_first(self):
        rows = [
            {"path": "low.md", "title": "打印机墨盒"},
            {"path": "high.md", "title": "开机黑屏"},
        ]
        ranked = rough_rank_metadata("开机黑屏怎么办", rows, cut_words=lambda text: [text])
        self.assertEqual(ranked[0]["path"], "high.md")


if __name__ == "__main__":
    unittest.main()
