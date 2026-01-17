"""
数据库模块
"""
from .connection import db_manager, DatabaseManager
from .models import (
    InventoryItem,
    BOMItem,
    ModelConfig,
    AllocationResult,
    MaterialAllocation
)
from .config import CONNECTION_STRING, TABLE_INVENTORY, TABLE_BOM

__all__ = [
    'db_manager',
    'DatabaseManager',
    'InventoryItem',
    'BOMItem',
    'ModelConfig',
    'AllocationResult',
    'MaterialAllocation',
    'CONNECTION_STRING',
    'TABLE_INVENTORY',
    'TABLE_BOM'
]
