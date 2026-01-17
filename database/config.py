"""
数据库连接配置
"""

# 数据库连接字符串
CONNECTION_STRING = 'mssql+pyodbc://dw:dw@172.16.31.42:1433/BI_TEMP?driver=ODBC+Driver+17+for+SQL+Server'

# 表名
TABLE_INVENTORY = 'XZB_InvNum'
TABLE_BOM = 'XZB_Forcast_BOM'
