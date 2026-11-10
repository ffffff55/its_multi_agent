"""python api/main.py 必须能导入知识库应用。"""
import os
import subprocess
import sys
import unittest
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]


class KnowledgeEntrypointTest(unittest.TestCase):
    def test_script_entrypoint_can_import(self):
        env = os.environ.copy()
        env.update(
            {
                "API_KEY": "kb-test",
                "BASE_URL": "https://example.invalid/v1",
                "MODEL": "demo-model",
                "EMBEDDING_MODEL": "demo-embed",
            }
        )
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import runpy\n"
                    "runpy.run_path('api/main.py', run_name='not_main')\n"
                    "print('SCRIPT_IMPORT_OK')\n"
                ),
            ],
            cwd=KNOWLEDGE_DIR,
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("SCRIPT_IMPORT_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
