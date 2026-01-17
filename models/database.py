# -*- coding: utf-8 -*-
"""
数据库连接配置
"""
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import urllib

# 数据库连接配置
SERVER = '172.16.31.42'
DATABASE = 'BI_TEMP'
USERNAME = 'dw'
PASSWORD = 'dw'
DRIVER = 'ODBC Driver 17 for SQL Server'

# 构建连接字符串
params = urllib.parse.quote_plus(f'DRIVER={DRIVER};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}')
DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={params}"

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """测试数据库连接"""
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            print("✅ 数据库连接成功")
            return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def check_tables_exist():
    """检查必要的表是否存在"""
    try:
        with engine.connect() as connection:
            # 检查XZB_InvNum表
            result = connection.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'XZB_InvNum'")
            if result.scalar() == 0:
                raise Exception("表 XZB_InvNum 不存在")

            # 检查XZB_Forcast_BOM表
            result = connection.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'XZB_Forcast_BOM'")
            if result.scalar() == 0:
                raise Exception("表 XZB_Forcast_BOM 不存在")

            print("✅ 数据表检查通过")
            return True

    except Exception as e:
        print(f"❌ 数据表检查失败: {e}")
        return False
