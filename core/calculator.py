"""
满足率计算器 - 计算各机型的满足率
"""
from typing import Dict
from database.models import ModelConfig, AllocationResult


class SatisfactionCalculator:
    """满足率计算器"""
    
    def calculate_satisfaction(
        self,
        config_a: ModelConfig,
        config_b: ModelConfig,
        allocation_results: Dict
    ) -> Dict[str, AllocationResult]:
        """
        计算满足率
        
        Args:
            config_a: 机型A配置
            config_b: 机型B配置
            allocation_results: 分配结果字典
            
        Returns:
            包含满足率的结果字典
        """
        # 提取分配结果
        allocation_a = allocation_results.get('model_a', {})
        allocation_b = allocation_results.get('model_b', {})
        
        # 计算机型A的满足率
        result_a = self._calculate_model_satisfaction(config_a, allocation_a)
        
        # 计算机型B的满足率
        result_b = self._calculate_model_satisfaction(config_b, allocation_b)
        
        return {
            'model_a': result_a,
            'model_b': result_b,
            'materials': allocation_results.get('materials', {})
        }
    
    def _calculate_model_satisfaction(
        self,
        config: ModelConfig,
        allocated_materials: Dict[str, float]
    ) -> AllocationResult:
        """
        计算单个机型的满足率
        
        Args:
            config: 机型配置
            allocated_materials: 分配到的物料清单
            
        Returns:
            分配结果对象
        """
        # 计算每个物料的短缺情况
        shortage_materials = {}
        for item in config.bom_items:
            material_code = item.component_item_number
            required_per_unit = item.component_num
            total_required = required_per_unit * config.plan_quantity
            allocated_qty = allocated_materials.get(material_code, 0)
            
            shortage = total_required - allocated_qty
            if shortage > 0:
                shortage_materials[material_code] = shortage
        
        # 计算可制造数量（基于最紧缺的物料）
        allocated_quantity = config.plan_quantity
        
        if shortage_materials:
            # 找出限制性物料（短缺比例最大的）
            min_ratio = float('inf')
            limiting_material = None
            
            for item in config.bom_items:
                material_code = item.component_item_number
                required_per_unit = item.component_num
                total_required = required_per_unit * config.plan_quantity
                allocated_qty = allocated_materials.get(material_code, 0)
                
                if allocated_qty < total_required:
                    ratio = allocated_qty / total_required if total_required > 0 else 0
                    if ratio < min_ratio:
                        min_ratio = ratio
                        limiting_material = material_code
            
            if limiting_material and min_ratio < float('inf'):
                # 重新计算可制造数量
                limiting_item = None
                for item in config.bom_items:
                    if item.component_item_number == limiting_material:
                        limiting_item = item
                        break
                
                if limiting_item and limiting_item.component_num > 0:
                    allocated_qty_for_limiting = allocated_materials.get(limiting_material, 0)
                    allocated_quantity = int(allocated_qty_for_limiting / limiting_item.component_num)
        
        # 计算满足率
        satisfaction_rate = 0.0
        if config.plan_quantity > 0:
            satisfaction_rate = (allocated_quantity / config.plan_quantity) * 100
        
        # 创建分配结果对象
        return AllocationResult(
            model_code=config.model_code,
            model_name=config.model_name,
            plan_quantity=config.plan_quantity,
            allocated_quantity=allocated_quantity,
            satisfaction_rate=satisfaction_rate,
            allocated_materials=allocated_materials,
            shortage_materials=shortage_materials,
            bom_items=config.bom_items
        )
