"""
数据库连接管理
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database.config import CONNECTION_STRING


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.engine = None
        self.Session = None
        self.session = None
    
    def connect(self):
        """建立数据库连接"""
        try:
            self.engine = create_engine(CONNECTION_STRING)
            self.Session = sessionmaker(bind=self.engine)
            self.session = self.Session()
            print("数据库连接成功")
            return True
        except Exception as e:
            print(f"数据库连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        if self.session:
            self.session.close()
        if self.engine:
            self.engine.dispose()
    
    def execute_query(self, query):
        """执行查询"""
        if not self.session:
            print("数据库未连接")
            return None
        try:
            result = self.session.execute(text(query))
            return result.fetchall()
        except Exception as e:
            print(f"查询执行失败: {e}")
            return None
    
    def get_inventory_data(self):
        """获取库存数据"""
        from database.config import TABLE_INVENTORY
        query = f"SELECT MATNR, CLABS FROM {TABLE_INVENTORY}"
        return self.execute_query(query)
    
    def get_bom_data(self, parent_item_number):
        """获取指定机型的BOM数据"""
        from database.config import TABLE_BOM
        query = f"""
        SELECT Parent_ItemNumber, Component_ItemNumber, 
               [Component_ItemNumber Description], [Component_ItemNumber Num]
        FROM {TABLE_BOM}
        WHERE Parent_ItemNumber = '{parent_item_number}'
        """
        return self.execute_query(query)
    
    def get_all_parent_items(self):
        """获取所有父项编码（机型）"""
        from database.config import TABLE_BOM
        query = f"SELECT DISTINCT Parent_ItemNumber FROM {TABLE_BOM}"
        return self.execute_query(query)


# 全局数据库管理器实例
db_manager = DatabaseManager()
