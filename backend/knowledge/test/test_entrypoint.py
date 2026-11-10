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
        for key in (
            "API_KEY",
            "BASE_URL",
            "MODEL",
            "EMBEDDING_MODEL",
            "KNOWLEDGE_BASE_URL",
        ):
            env.pop(key, None)
        # 显式写入测试用配置，避免本机 .env 混进启动测试。
        # 五个键都不配时的空字符串缺省，由 test_settings_defaults.py 锁住。
        env.update(
            {
                "API_KEY": "kb-test",
                "BASE_URL": "https://example.invalid/v1",
                "MODEL": "demo-model",
                "EMBEDDING_MODEL": "demo-embed",
                "KNOWLEDGE_BASE_URL": "",
            }
        )
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import sys\n"
                    "from pathlib import Path\n"
                    "script = Path('api/main.py').resolve()\n"
                    "service_root = script.parent.parent\n"
                    "sys.path = [str(script.parent)] + [\n"
                    "    item for item in sys.path\n"
                    "    if item not in ('', str(service_root), str(script.parent))\n"
                    "]\n"
                    "import runpy\n"
                    "runpy.run_path(str(script), run_name='not_main')\n"
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
