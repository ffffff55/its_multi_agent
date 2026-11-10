"""创建 repair_shops 表并插入样例数据。

坐标是 BD09LL 近似值，只供演示。数据库连接从环境变量或 backend/app/.env 读取，
与主服务使用同一套 MYSQL_* 配置。
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

TABLE_SQL = """
CREATE TABLE IF NOT EXISTS repair_shops (
    id INT PRIMARY KEY AUTO_INCREMENT,
    service_station_name VARCHAR(255),
    province VARCHAR(100),
    city VARCHAR(100),
    district VARCHAR(100),
    address VARCHAR(500),
    phone VARCHAR(50),
    manager VARCHAR(100),
    manager_phone VARCHAR(50),
    opening_hours VARCHAR(100),
    repair_types VARCHAR(255),
    repair_specialties VARCHAR(500),
    repair_services VARCHAR(500),
    supported_brands VARCHAR(255),
    rating DECIMAL(2,1),
    established_year INT,
    employee_count INT,
    service_station_description TEXT,
    latitude DECIMAL(10,6),
    longitude DECIMAL(10,6)
);
"""

ROWS = [
    ("联想官方客户服务中心(北京中关村店)", "北京市", "北京市", "海淀区", "北京市海淀区中关村大街1号",
     "010-88888801", "张伟", "13800000001", "09:00-18:00", "笔记本,台式机,平板",
     "主板维修,屏幕更换,系统重装", "硬件检测,数据恢复,清灰保养", "Lenovo,ThinkPad",
     4.8, 2008, 25, "联想官方授权服务中心，提供全系列设备维修。", 39.9841, 116.3184),
    ("小米之家授权维修中心(北京五道口)", "北京市", "北京市", "海淀区", "北京市海淀区成府路28号",
     "010-88888802", "李娜", "13800000002", "10:00-22:00", "手机,笔记本,智能家居",
     "屏幕更换,电池更换,进水维修", "快修服务,以旧换新", "Xiaomi,Redmi",
     4.7, 2015, 18, "小米官方授权服务网点，支持手机与生态产品维修。", 39.9925, 116.3370),
    ("Apple Store 零售店(北京三里屯)", "北京市", "北京市", "朝阳区", "北京市朝阳区三里屯太古里",
     "010-88888803", "王芳", "13800000003", "10:00-22:00", "Mac,iPhone,iPad",
     "电池更换,屏幕维修,主板维修", "天才吧预约维修,系统支持", "Apple",
     4.9, 2012, 40, "Apple 官方零售店，提供全产品线维修与支持。", 39.9367, 116.4551),
    ("华为客户服务中心(广州天河城)", "广东省", "广州市", "天河区", "广州市天河区天河路208号",
     "020-88888804", "陈强", "13800000004", "09:30-21:30", "手机,平板,笔记本",
     "屏幕更换,电池更换,主板维修", "快修,数据备份", "Huawei,Honor",
     4.8, 2010, 30, "华为官方客户服务中心，华南旗舰网点。", 23.1351, 113.3245),
    ("联想服务中心(广州岗顶店)", "广东省", "广州市", "天河区", "广州市天河区天河路598号",
     "020-88888805", "刘洋", "13800000005", "09:00-18:30", "笔记本,台式机",
     "主板维修,屏幕更换,系统重装", "硬件检测,清灰保养", "Lenovo",
     4.6, 2013, 20, "联想授权服务站，专注笔记本维修。", 23.1411, 113.3305),
    ("OPPO 客服中心(深圳华强北)", "广东省", "深圳市", "福田区", "深圳市福田区华强北路1019号",
     "0755-88888806", "赵敏", "13800000006", "09:30-21:00", "手机,平板",
     "屏幕更换,电池更换,进水维修", "快修,以旧换新", "OPPO,OnePlus,realme",
     4.7, 2014, 22, "OPPO 官方客服中心，华强北旗舰店。", 22.5446, 114.0850),
]

INSERT_SQL = """
INSERT INTO repair_shops (
    service_station_name, province, city, district, address, phone, manager, manager_phone,
    opening_hours, repair_types, repair_specialties, repair_services, supported_brands,
    rating, established_year, employee_count, service_station_description, latitude, longitude
) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
"""


def mysql_conn_kwargs() -> dict:
    """与主服务 settings 相同的 MYSQL_* 环境变量。"""
    return {
        "host": os.environ.get("MYSQL_HOST", "localhost"),
        "port": int(os.environ.get("MYSQL_PORT", "3306")),
        "user": os.environ.get("MYSQL_USER", "root"),
        "password": os.environ.get("MYSQL_PASSWORD", ""),
        "database": os.environ.get("MYSQL_DATABASE", "its_db"),
        "charset": "utf8mb4",
    }


def main():
    import pymysql

    conn = pymysql.connect(**mysql_conn_kwargs())
    try:
        with conn.cursor() as cur:
            cur.execute(TABLE_SQL)
            conn.commit()
            print("表 repair_shops 已就绪")
            cur.execute("SELECT COUNT(*) FROM repair_shops")
            cnt = cur.fetchone()[0]
            if cnt == 0:
                cur.executemany(INSERT_SQL, ROWS)
                conn.commit()
                print(f"已插入 {len(ROWS)} 条样例服务站数据")
            else:
                print(f"表已有 {cnt} 条数据，跳过插入")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
