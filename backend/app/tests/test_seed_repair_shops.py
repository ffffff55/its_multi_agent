"""样例服务站脚本必须从环境变量读取数据库连接，不能写死。"""
import os
import unittest
from pathlib import Path

from seed_repair_shops import mysql_conn_kwargs


class SeedRepairShopsConfigTest(unittest.TestCase):
    def test_reads_mysql_settings_from_environment(self):
        keys = (
            "MYSQL_HOST",
            "MYSQL_PORT",
            "MYSQL_USER",
            "MYSQL_PASSWORD",
            "MYSQL_DATABASE",
        )
        previous = {key: os.environ.get(key) for key in keys}
        os.environ["MYSQL_HOST"] = "db.example"
        os.environ["MYSQL_PORT"] = "3307"
        os.environ["MYSQL_USER"] = "its_user"
        os.environ["MYSQL_PASSWORD"] = "from-env"
        os.environ["MYSQL_DATABASE"] = "its_demo"
        try:
            self.assertEqual(
                mysql_conn_kwargs(),
                {
                    "host": "db.example",
                    "port": 3307,
                    "user": "its_user",
                    "password": "from-env",
                    "database": "its_demo",
                    "charset": "utf8mb4",
                },
            )
        finally:
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_source_has_no_inline_connection_dict(self):
        source = Path(__file__).resolve().parents[1].joinpath("seed_repair_shops.py").read_text(encoding="utf-8")
        self.assertNotIn("pymysql.connect(", source.split("def main")[0])
        self.assertIn("os.environ.get(\"MYSQL_PASSWORD\"", source)
        self.assertIn("its_db", source)


if __name__ == "__main__":
    unittest.main()
