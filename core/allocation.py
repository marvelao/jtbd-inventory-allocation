"""
库存分配算法 - 核心业务逻辑
"""
from typing import Dict, List
from database.models import ModelConfig, BOMItem, AllocationResult, MaterialAllocation


class InventoryAllocator:
    """库存分配器"""
    
    def __init__(self, db_manager):
        """
        初始化分配器
        
        Args:
            db_manager: 数据库管理器实例
        """
        self.db_manager = db_manager
        self.inventory_data = {}
        self.load_inventory_data()
    
    def load_inventory_data(self):
        """加载库存数据"""
        try:
            inventory_rows = self.db_manager.get_inventory_data()
            if inventory_rows:
                self.inventory_data = {
                    row[0]: row[1] if row[1] else 0.0
                    for row in inventory_rows
                }
        except Exception as e:
            print(f"加载库存数据失败: {e}")
            self.inventory_data = {}
    
    def allocate(self, config_a: ModelConfig, config_b: ModelConfig) -> Dict:
        """
        执行库存分配
        
        Args:
            config_a: 机型A配置
            config_b: 机型B配置
            
        Returns:
            分配结果字典，包含两个机型的分配结果和物料分配详情
        """
        # 1. 识别共用物料和专属物料
        materials_a = self._extract_materials(config_a.bom_items)
        materials_b = self._extract_materials(config_b.bom_items)
        
        shared_materials = self._find_shared_materials(materials_a, materials_b)
        exclusive_materials_a = self._find_exclusive_materials(materials_a, materials_b)
        exclusive_materials_b = self._find_exclusive_materials(materials_b, materials_a)
        
        # 2. 计算各机型的物料需求
        requirements_a = self._calculate_requirements(config_a)
        requirements_b = self._calculate_requirements(config_b)
        
        # 3. 分配库存
        # 先分配专属物料
        allocated_exclusive_a = self._allocate_exclusive(
            exclusive_materials_a, requirements_a
        )
        allocated_exclusive_b = self._allocate_exclusive(
            exclusive_materials_b, requirements_b
        )
        
        # 再按优先级分配共用物料
        allocated_shared = self._allocate_shared_materials(
            shared_materials,
            requirements_a,
            requirements_b,
            config_a.priority,
            config_b.priority
        )
        
        # 4. 合并分配结果
        final_allocation_a = self._merge_allocation(
            allocated_exclusive_a,
            allocated_shared.get('model_a', {})
        )
        final_allocation_b = self._merge_allocation(
            allocated_exclusive_b,
            allocated_shared.get('model_b', {})
        )
        
        # 5. 计算物料分配详情（用于展示）
        materials_detail = self._calculate_materials_detail(
            shared_materials,
            allocated_shared,
            requirements_a,
            requirements_b
        )
        
        # 6. 返回分配结果
        return {
            'model_a': final_allocation_a,
            'model_b': final_allocation_b,
            'materials': materials_detail
        }
    
    def _extract_materials(self, bom_items: List[BOMItem]) -> Dict[str, float]:
        """从BOM项目中提取物料清单"""
        return {
            item.component_item_number: item.component_num
            for item in bom_items
        }
    
    def _find_shared_materials(self, materials_a: Dict, materials_b: Dict) -> set:
        """找出共用物料"""
        return set(materials_a.keys()) & set(materials_b.keys())
    
    def _find_exclusive_materials(self, materials_a: Dict, materials_b: Dict) -> set:
        """找出专属物料"""
        return set(materials_a.keys()) - set(materials_b.keys())
    
    def _calculate_requirements(self, config: ModelConfig) -> Dict[str, float]:
        """计算机型物料需求（考虑制造数量）"""
        requirements = {}
        for item in config.bom_items:
            material_code = item.component_item_number
            quantity_per_unit = item.component_num
            total_required = quantity_per_unit * config.plan_quantity
            requirements[material_code] = total_required
        return requirements
    
    def _allocate_exclusive(self, exclusive_materials: set, requirements: Dict) -> Dict[str, float]:
        """分配专属物料"""
        allocation = {}
        for material_code in exclusive_materials:
            required_qty = requirements.get(material_code, 0)
            available_qty = self.inventory_data.get(material_code, 0)
            
            # 分配可用库存，最多分配到需求量
            allocated_qty = min(required_qty, available_qty)
            allocation[material_code] = allocated_qty
        
        return allocation
    
    def _allocate_shared_materials(
        self,
        shared_materials: set,
        requirements_a: Dict,
        requirements_b: Dict,
        priority_a: int,
        priority_b: int
    ) -> Dict:
        """
        按优先级分配共用物料
        
        Args:
            shared_materials: 共用物料集合
            requirements_a: 机型A的需求
            requirements_b: 机型B的需求
            priority_a: 机型A的优先级（数字越小优先级越高）
            priority_b: 机型B的优先级
            
        Returns:
            分配结果 {'model_a': {...}, 'model_b': {...}, 'material_detail': {...}}
        """
        allocation_a = {}
        allocation_b = {}
        
        # 按优先级排序机型
        models = [
            ('A', requirements_a, priority_a, allocation_a),
            ('B', requirements_b, priority_b, allocation_b)
        ]
        models.sort(key=lambda x: x[2])  # 按优先级排序（数字越小优先级越高）
        
        # 逐个分配共用物料
        for material_code in shared_materials:
            total_inventory = self.inventory_data.get(material_code, 0)
            remaining_inventory = total_inventory
            
            # 按优先级依次分配
            for model_name, requirements, priority, allocation in models:
                if remaining_inventory <= 0:
                    break
                
                required_qty = requirements.get(material_code, 0)
                if required_qty > 0:
                    # 分配可用库存，最多分配到需求量
                    allocated_qty = min(required_qty, remaining_inventory)
                    allocation[material_code] = allocated_qty
                    remaining_inventory -= allocated_qty
        
        return {
            'model_a': allocation_a,
            'model_b': allocation_b
        }
    
    def _merge_allocation(self, base: Dict, additional: Dict) -> Dict:
        """合并两次分配的结果"""
        merged = base.copy()
        for material_code, qty in additional.items():
            if material_code in merged:
                merged[material_code] += qty
            else:
                merged[material_code] = qty
        return merged
    
    def _calculate_materials_detail(
        self,
        shared_materials: set,
        allocated_shared: Dict,
        requirements_a: Dict,
        requirements_b: Dict
    ) -> Dict:
        """计算物料分配详情（用于展示）"""
        materials_detail = {}
        
        # 添加专属物料信息
        for material_code, inventory_qty in self.inventory_data.items():
            if material_code not in shared_materials:
                materials_detail[material_code] = {
                    'total_inventory': inventory_qty,
                    'allocated_a': 0,
                    'allocated_b': 0
                }
        
        # 添加共用物料分配信息
        for material_code in shared_materials:
            allocated_a = allocated_shared.get('model_a', {}).get(material_code, 0)
            allocated_b = allocated_shared.get('model_b', {}).get(material_code, 0)
            total_inventory = self.inventory_data.get(material_code, 0)
            
            materials_detail[material_code] = {
                'total_inventory': total_inventory,
                'allocated_a': allocated_a,
                'allocated_b': allocated_b
            }
        
        return materials_detail
