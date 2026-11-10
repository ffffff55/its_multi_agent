"""手工试 MCP 的函数必须引用文件里真正创建的客户端。"""
import unittest
from pathlib import Path

MCP_SERVERS = Path(__file__).resolve().parents[1].joinpath("infrastructure", "tools", "mcp", "mcp_servers.py")


class McpClientNameTest(unittest.TestCase):
    def test_manual_calls_use_the_defined_clients(self):
        source = MCP_SERVERS.read_text(encoding="utf-8")
        self.assertNotIn("search_mac_client", source)
        self.assertNotIn("baidu_map_mcp", source)
        self.assertIn("search_mcp_client", source)
        self.assertIn("baidu_mcp_client", source)


if __name__ == "__main__":
    unittest.main()
