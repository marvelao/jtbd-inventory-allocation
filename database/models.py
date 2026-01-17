"""
数据模型定义
"""
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class InventoryItem:
    """库存物料"""
    matnr: str  # 物料编码
    clabs: float  # 库存数量


@dataclass
class BOMItem:
    """BOM子项"""
    parent_item_number: str  # 父项编码（机型）
    component_item_number: str  # 子项编码（物料编码）
    component_description: str  # 子项描述
    component_num: float  # 子项数量


@dataclass
class ModelConfig:
    """机型配置"""
    model_code: str  # 机型编码
    model_name: str  # 机型名称
    plan_quantity: int  # 计划制造数量
    priority: int  # 优先级（1=最高，2=次之，以此类推）
    bom_items: List[BOMItem]  # BOM子项列表


@dataclass
class AllocationResult:
    """分配结果"""
    model_code: str  # 机型编码
    model_name: str  # 机型名称
    plan_quantity: int  # 计划制造数量
    allocated_quantity: int  # 实际可制造数量
    satisfaction_rate: float  # 满足率（百分比）
    allocated_materials: Dict[str, float]  # 分配到的物料清单 {物料编码: 数量}
    shortage_materials: Dict[str, float]  # 短缺物料清单 {物料编码: 短缺数量}
    bom_items: List[BOMItem]  # BOM子项列表（用于计算物料平均满足率）


@dataclass
class MaterialAllocation:
    """物料分配详情"""
    material_code: str  # 物料编码
    total_inventory: float  # 总库存
    shared_by_models: List[str]  # 共用该物料的机型列表
    allocation_details: Dict[str, float]  # 分配详情 {机型编码: 分配数量}
