"""知识库配置缺省应是空字符串。没配环境变量、也没有 .env 时，导入不能因为 None 失败。"""
import os
import subprocess
import sys
import unittest
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[1]


class KnowledgeSettingsDefaultTest(unittest.TestCase):
    def test_unset_env_defaults_to_empty_string(self):
        env = os.environ.copy()
        for key in ("API_KEY", "BASE_URL", "MODEL", "EMBEDDING_MODEL", "KNOWLEDGE_BASE_URL"):
            env.pop(key, None)
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "from config.settings import Settings\n"
                    "fresh = Settings(_env_file=None)\n"
                    "assert fresh.API_KEY == ''\n"
                    "assert fresh.BASE_URL == ''\n"
                    "assert fresh.MODEL == ''\n"
                    "assert fresh.EMBEDDING_MODEL == ''\n"
                    "assert fresh.KNOWLEDGE_BASE_URL == ''\n"
                    "print('EMPTY_DEFAULT_OK')\n"
                ),
            ],
            cwd=KNOWLEDGE_DIR,
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("EMPTY_DEFAULT_OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
