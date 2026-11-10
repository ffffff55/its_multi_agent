"""主进程导入时，只配一套模型密钥也必须能起来。"""
import os
import subprocess
import sys
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]


class OpenAIClientStartupTest(unittest.TestCase):
    def _run(self, extra: dict[str, str], code: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        for key in (
            "SF_API_KEY",
            "SF_BASE_URL",
            "AL_BAILIAN_API_KEY",
            "AL_BAILIAN_BASE_URL",
            "OPENAI_API_KEY",
            "OPENAI_ADMIN_KEY",
        ):
            env.pop(key, None)
        env.update(extra)
        return subprocess.run(
            [sys.executable, "-c", code],
            cwd=APP_DIR,
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )

    def test_missing_both_providers_fails_startup_check(self):
        result = self._run(
            {
                "SF_API_KEY": "",
                "SF_BASE_URL": "",
                "AL_BAILIAN_API_KEY": "",
                "AL_BAILIAN_BASE_URL": "",
            },
            "import api.main",
        )
        self.assertNotEqual(result.returncode, 0, result.stderr)
        self.assertIn("必须配置至少一个 AI 服务", result.stderr)

    def test_script_entrypoint_can_import(self):
        result = self._run(
            {
                "SF_API_KEY": "",
                "SF_BASE_URL": "",
                "AL_BAILIAN_API_KEY": "bailian-test",
                "AL_BAILIAN_BASE_URL": "https://example.invalid/v1",
            },
            (
                # python -c 会把 cwd 放在 sys.path[0]，runpy 执行 .py 文件时也不会改成脚本目录。
                # 这里改成和 `python api/main.py` 一样：只把 api/ 放在最前，服务根目录不在搜索路径里。
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
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("SCRIPT_IMPORT_OK", result.stdout)

    def test_only_siliconflow_can_import_app(self):
        result = self._run(
            {
                "SF_API_KEY": "sf-test",
                "SF_BASE_URL": "https://example.invalid/sf/v1",
                "AL_BAILIAN_API_KEY": "",
                "AL_BAILIAN_BASE_URL": "",
            },
            "import api.main\nprint('IMPORT_OK')",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("IMPORT_OK", result.stdout)

    def test_only_bailian_keeps_sub_client_and_stubs_main_client(self):
        result = self._run(
            {
                "SF_API_KEY": "",
                "SF_BASE_URL": "",
                "AL_BAILIAN_API_KEY": "bailian-test",
                "AL_BAILIAN_BASE_URL": "https://example.invalid/bailian/v1",
            },
            (
                "from infrastructure.ai.openai_client import main_model_client, sub_model_client\n"
                "print(str(main_model_client.base_url))\n"
                "print(str(sub_model_client.base_url))\n"
            ),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        self.assertEqual(lines[0], "http://127.0.0.1:9/v1/")
        self.assertEqual(lines[1], "https://example.invalid/bailian/v1/")


if __name__ == "__main__":
    unittest.main()
