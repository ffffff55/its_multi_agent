"""主进程导入时，只配一套模型密钥也必须能起来；缺项时要逐项指出缺的是哪个字段。"""
import os
import subprocess
import sys
import unittest
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]

# 这些变量必须先清掉，否则本机环境变量或 .env 会把「缺配置」的场景藏起来。
CONFIG_ENV_KEYS = (
    "SF_API_KEY",
    "SF_BASE_URL",
    "AL_BAILIAN_API_KEY",
    "AL_BAILIAN_BASE_URL",
    "MAIN_MODEL_NAME",
    "SUB_MODEL_NAME",
    "OPENAI_API_KEY",
    "OPENAI_ADMIN_KEY",
)


class OpenAIClientStartupTest(unittest.TestCase):
    def _run(self, extra: dict[str, str], code: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        for key in CONFIG_ENV_KEYS:
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

    def test_missing_both_providers_names_every_missing_field(self):
        """没配任何一套时，报错要按服务逐项列出缺的字段名。"""
        result = self._run(
            {
                "SF_API_KEY": "",
                "SF_BASE_URL": "",
                "AL_BAILIAN_API_KEY": "",
                "AL_BAILIAN_BASE_URL": "",
            },
            "import config.settings",
        )
        self.assertNotEqual(result.returncode, 0, result.stderr)
        self.assertIn("启动前配置检查未通过", result.stderr)
        for field in (
            "SF_API_KEY",
            "SF_BASE_URL",
            "AL_BAILIAN_API_KEY",
            "AL_BAILIAN_BASE_URL",
        ):
            self.assertIn(field, result.stderr)

    def test_half_configured_provider_names_only_the_missing_field(self):
        """只填了 API Key、漏了 Base URL 时，报错要指出漏的是 Base URL。"""
        result = self._run(
            {
                "SF_API_KEY": "sf-test",
                "SF_BASE_URL": "",
                "AL_BAILIAN_API_KEY": "",
                "AL_BAILIAN_BASE_URL": "",
            },
            "import config.settings",
        )
        self.assertNotEqual(result.returncode, 0, result.stderr)
        self.assertIn("缺少 SF_BASE_URL", result.stderr)
        # 半配的硅基流动已经指出缺 Base URL，就不该再说它缺 API Key。
        self.assertNotIn("缺少 SF_API_KEY", result.stderr)

    def test_bailian_without_model_name_names_sub_model_name(self):
        """配了阿里百炼但没填子模型名称时，要直接指出缺 SUB_MODEL_NAME。"""
        result = self._run(
            {
                "SF_API_KEY": "",
                "SF_BASE_URL": "",
                "AL_BAILIAN_API_KEY": "bailian-test",
                "AL_BAILIAN_BASE_URL": "https://example.invalid/v1",
                "SUB_MODEL_NAME": "",
            },
            "import config.settings",
        )
        self.assertNotEqual(result.returncode, 0, result.stderr)
        self.assertIn("缺少模型名称", result.stderr)
        self.assertIn("SUB_MODEL_NAME", result.stderr)
        # 阿里百炼那一套是完整的，不该再说它缺 API Key。
        self.assertNotIn("AL_BAILIAN_API_KEY", result.stderr)

    def test_siliconflow_without_main_model_name_names_main_model_name(self):
        result = self._run(
            {
                "SF_API_KEY": "sf-test",
                "SF_BASE_URL": "https://example.invalid/sf/v1",
                "MAIN_MODEL_NAME": "",
                "AL_BAILIAN_API_KEY": "",
                "AL_BAILIAN_BASE_URL": "",
            },
            "import config.settings",
        )
        self.assertNotEqual(result.returncode, 0, result.stderr)
        self.assertIn("缺少模型名称", result.stderr)
        self.assertIn("MAIN_MODEL_NAME", result.stderr)

    def test_error_message_never_prints_the_api_key(self):
        """报错和标准输出里都不能出现密钥值。"""
        secret = "sk-startup-secret-should-not-be-printed-9f8e7d"
        result = self._run(
            {
                "SF_API_KEY": secret,
                "SF_BASE_URL": "",
                "AL_BAILIAN_API_KEY": "",
                "AL_BAILIAN_BASE_URL": "",
            },
            "import config.settings",
        )
        self.assertNotEqual(result.returncode, 0, result.stderr)
        self.assertIn("SF_BASE_URL", result.stderr)
        combined = result.stdout + result.stderr
        self.assertNotIn(secret, combined)
        # 只报字段名，所以字段名本身必须出现。
        self.assertIn("SF_API_KEY", combined)

    def test_script_entrypoint_can_import(self):
        result = self._run(
            {
                "SF_API_KEY": "",
                "SF_BASE_URL": "",
                "AL_BAILIAN_API_KEY": "bailian-test",
                "AL_BAILIAN_BASE_URL": "https://example.invalid/v1",
                "SUB_MODEL_NAME": "qwen3-max",
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
        """只配硅基流动时进程仍能起来，这与 README 的说明一致。"""
        result = self._run(
            {
                "SF_API_KEY": "sf-test",
                "SF_BASE_URL": "https://example.invalid/sf/v1",
                "AL_BAILIAN_API_KEY": "",
                "AL_BAILIAN_BASE_URL": "",
                "SUB_MODEL_NAME": "",
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
                "SUB_MODEL_NAME": "qwen3-max",
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
