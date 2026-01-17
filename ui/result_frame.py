"""
结果展示界面 - 显示分配结果和满足率
"""
import tkinter as tk
from tkinter import ttk, filedialog
from typing import List
import pandas as pd
from datetime import datetime
from database.models import AllocationResult


class ResultFrame(ttk.Frame):
    """结果展示框架"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
    
    def create_widgets(self):
        """创建结果展示组件"""
        # 标题
        title_label = ttk.Label(
            self,
            text="库存分配结果",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # 创建Notebook用于切换不同结果的展示
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 总览页
        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="总览")
        
        # 机型A详细页
        self.model_a_frame = ModelResultFrame(self.notebook, "机型 A")
        self.notebook.add(self.model_a_frame, text="机型 A 详情")
        
        # 机型B详细页
        self.model_b_frame = ModelResultFrame(self.notebook, "机型 B")
        self.notebook.add(self.model_b_frame, text="机型 B 详情")
        
        # 初始化总览界面
        self.create_summary_view()
    
    def create_summary_view(self):
        """创建总览视图"""
        # 统计信息区域
        stats_frame = ttk.LabelFrame(self.summary_frame, text="分配统计", padding="10")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 机型A统计
        self.model_a_stats_var = tk.StringVar()
        model_a_label = ttk.Label(
            stats_frame,
            textvariable=self.model_a_stats_var,
            font=("Arial", 11)
        )
        model_a_label.pack(fill=tk.X, pady=2)
        
        # 机型B统计
        self.model_b_stats_var = tk.StringVar()
        model_b_label = ttk.Label(
            stats_frame,
            textvariable=self.model_b_stats_var,
            font=("Arial", 11)
        )
        model_b_label.pack(fill=tk.X, pady=2)
        
        # 物料分配总览
        materials_frame = ttk.LabelFrame(self.summary_frame, text="物料分配总览", padding="10")
        materials_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建Treeview
        columns = ("物料编码", "总库存", "机型A分配", "机型B分配", "剩余库存")
        self.materials_tree = ttk.Treeview(materials_frame, columns=columns, show="headings")

        for col in columns:
            self.materials_tree.heading(col, text=col)
            self.materials_tree.column(col, width=100)

        # 添加滚动条
        materials_scrollbar = ttk.Scrollbar(
            materials_frame,
            orient=tk.VERTICAL,
            command=self.materials_tree.yview
        )
        self.materials_tree.configure(yscrollcommand=materials_scrollbar.set)

        self.materials_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        materials_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 导出按钮区域
        button_frame = ttk.Frame(self.summary_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        export_btn = ttk.Button(
            button_frame,
            text="导出物料分配详情",
            command=self.export_to_excel
        )
        export_btn.pack(side=tk.LEFT)

        # 存储当前结果用于导出
        self.current_results = None
    
    def display_results(self, results: dict):
        """展示分配结果"""
        # 存储当前结果用于导出
        self.current_results = results

        result_a = results.get('model_a')
        result_b = results.get('model_b')
        materials = results.get('materials', {})

        # 更新统计信息
        if result_a:
            # 计算子项物料平均满足率
            avg_material_satisfaction_a = self._calculate_avg_material_satisfaction(result_a)
            stats_a = (
                f"机型 A ({result_a.model_name}): "
                f"计划 {result_a.plan_quantity} 台, "
                f"可生产 {result_a.allocated_quantity} 台, "
                f"满足率 {result_a.satisfaction_rate:.2f}%, "
                f"子项物料平均满足率 {avg_material_satisfaction_a:.2f}%"
            )
            self.model_a_stats_var.set(stats_a)

        if result_b:
            # 计算子项物料平均满足率
            avg_material_satisfaction_b = self._calculate_avg_material_satisfaction(result_b)
            stats_b = (
                f"机型 B ({result_b.model_name}): "
                f"计划 {result_b.plan_quantity} 台, "
                f"可生产 {result_b.allocated_quantity} 台, "
                f"满足率 {result_b.satisfaction_rate:.2f}%, "
                f"子项物料平均满足率 {avg_material_satisfaction_b:.2f}%"
            )
            self.model_b_stats_var.set(stats_b)
        
        # 更新物料分配总览
        self.update_materials_overview(materials)
        
        # 更新机型详情
        if result_a:
            self.model_a_frame.display_result(result_a)
        
        if result_b:
            self.model_b_frame.display_result(result_b)
    
    def update_materials_overview(self, materials: dict):
        """更新物料分配总览"""
        self.materials_tree.delete(*self.materials_tree.get_children())
        
        for material_code, material_data in materials.items():
            total_inv = material_data.get('total_inventory', 0)
            allocated_a = material_data.get('allocated_a', 0)
            allocated_b = material_data.get('allocated_b', 0)
            remaining = total_inv - allocated_a - allocated_b
            
            self.materials_tree.insert(
                "",
                tk.END,
                values=(
                    material_code,
                    f"{total_inv:.2f}",
                    f"{allocated_a:.2f}",
                    f"{allocated_b:.2f}",
                    f"{remaining:.2f}"
                )
            )
    
    def clear_all(self):
        """清空所有结果"""
        self.model_a_stats_var.set("")
        self.model_b_stats_var.set("")
        self.materials_tree.delete(*self.materials_tree.get_children())
        self.model_a_frame.clear()
        self.model_b_frame.clear()
        self.current_results = None

    def _calculate_avg_material_satisfaction(self, result: AllocationResult) -> float:
        """
        计算子项物料平均满足率

        Args:
            result: 机型分配结果

        Returns:
            物料平均满足率（百分比）
        """
        if not result.allocated_materials or not result.bom_items:
            return 0.0

        total_satisfaction = 0.0
        material_count = 0

        # 遍历所有BOM物料
        for bom_item in result.bom_items:
            material_code = bom_item.component_item_number
            required_qty = bom_item.component_num * result.plan_quantity
            allocated_qty = result.allocated_materials.get(material_code, 0)

            # 计算单个物料的满足率
            if required_qty > 0:
                satisfaction = min(allocated_qty / required_qty, 1.0) * 100
                total_satisfaction += satisfaction
                material_count += 1

        # 计算平均满足率
        if material_count > 0:
            return total_satisfaction / material_count
        else:
            return 0.0

    def export_to_excel(self):
        """导出物料分配详情到Excel"""
        if not self.current_results:
            from tkinter import messagebox
            messagebox.showwarning("警告", "没有可导出的数据，请先执行库存分配")
            return

        try:
            # 获取文件保存路径
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")],
                initialfile=f"库存分配详情_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                title="保存导出文件"
            )

            if not filename:
                return

            # 创建Excel writer
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # 写入总览数据
                result_a = self.current_results.get('model_a')
                result_b = self.current_results.get('model_b')
                materials = self.current_results.get('materials', {})

                # 1. 写入分配统计
                summary_data = []
                if result_a:
                    summary_data.append({
                        '机型': '机型 A',
                        '机型编码': result_a.model_code,
                        '机型名称': result_a.model_name,
                        '计划制造数量': result_a.plan_quantity,
                        '实际可生产': result_a.allocated_quantity,
                        '满足率(%)': f"{result_a.satisfaction_rate:.2f}"
                    })
                if result_b:
                    summary_data.append({
                        '机型': '机型 B',
                        '机型编码': result_b.model_code,
                        '机型名称': result_b.model_name,
                        '计划制造数量': result_b.plan_quantity,
                        '实际可生产': result_b.allocated_quantity,
                        '满足率(%)': f"{result_b.satisfaction_rate:.2f}"
                    })

                pd.DataFrame(summary_data).to_excel(
                    writer, sheet_name='分配统计', index=False
                )

                # 2. 写入物料分配总览
                materials_data = []
                for material_code, material_data in materials.items():
                    total_inv = material_data.get('total_inventory', 0)
                    allocated_a = material_data.get('allocated_a', 0)
                    allocated_b = material_data.get('allocated_b', 0)
                    remaining = total_inv - allocated_a - allocated_b

                    materials_data.append({
                        '物料编码': material_code,
                        '总库存': total_inv,
                        '机型A分配': allocated_a,
                        '机型B分配': allocated_b,
                        '剩余库存': remaining
                    })

                pd.DataFrame(materials_data).to_excel(
                    writer, sheet_name='物料分配总览', index=False
                )

                # 3. 写入机型A详情
                if result_a:
                    model_a_data = []
                    for material_code, allocated_qty in result_a.allocated_materials.items():
                        required_qty = allocated_qty + result_a.shortage_materials.get(material_code, 0)
                        shortage_qty = result_a.shortage_materials.get(material_code, 0)

                        model_a_data.append({
                            '物料编码': material_code,
                            '需求数量': required_qty,
                            '分配数量': allocated_qty,
                            '短缺数量': shortage_qty
                        })

                    if model_a_data:
                        pd.DataFrame(model_a_data).to_excel(
                            writer, sheet_name='机型A详情', index=False
                        )

                # 4. 写入机型B详情
                if result_b:
                    model_b_data = []
                    for material_code, allocated_qty in result_b.allocated_materials.items():
                        required_qty = allocated_qty + result_b.shortage_materials.get(material_code, 0)
                        shortage_qty = result_b.shortage_materials.get(material_code, 0)

                        model_b_data.append({
                            '物料编码': material_code,
                            '需求数量': required_qty,
                            '分配数量': allocated_qty,
                            '短缺数量': shortage_qty
                        })

                    if model_b_data:
                        pd.DataFrame(model_b_data).to_excel(
                            writer, sheet_name='机型B详情', index=False
                        )

            from tkinter import messagebox
            messagebox.showinfo("成功", f"导出成功！\n文件已保存到:\n{filename}")

        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("错误", f"导出失败：{str(e)}")


class ModelResultFrame(ttk.Frame):
    """单机型结果展示框架"""
    
    def __init__(self, parent, model_label):
        super().__init__(parent)
        self.model_label = model_label
        self.create_widgets()
    
    def create_widgets(self):
        """创建展示组件"""
        # 统计信息
        stats_frame = ttk.LabelFrame(self, text=f"{self.model_label} 分配统计", padding="10")
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stats_var = tk.StringVar()
        stats_label = ttk.Label(
            stats_frame,
            textvariable=self.stats_var,
            font=("Arial", 11)
        )
        stats_label.pack(fill=tk.X, pady=2)
        
        # 满足率进度条
        satisfaction_frame = ttk.Frame(stats_frame)
        satisfaction_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(satisfaction_frame, text="满足率:").pack(side=tk.LEFT)
        
        self.satisfaction_progress = ttk.Progressbar(
            satisfaction_frame,
            length=300,
            mode='determinate'
        )
        self.satisfaction_progress.pack(side=tk.LEFT, padx=5)
        
        self.satisfaction_label = ttk.Label(satisfaction_frame, text="0%")
        self.satisfaction_label.pack(side=tk.LEFT)
        
        # 物料分配详情
        materials_frame = ttk.LabelFrame(self, text="物料分配详情", padding="10")
        materials_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建Treeview
        columns = ("物料编码", "需求数量", "分配数量", "短缺数量")
        self.materials_tree = ttk.Treeview(materials_frame, columns=columns, show="headings")
        
        for col in columns:
            self.materials_tree.heading(col, text=col)
            self.materials_tree.column(col, width=100)
        
        # 添加滚动条
        materials_scrollbar = ttk.Scrollbar(
            materials_frame,
            orient=tk.VERTICAL,
            command=self.materials_tree.yview
        )
        self.materials_tree.configure(yscrollcommand=materials_scrollbar.set)
        
        self.materials_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        materials_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def display_result(self, result: AllocationResult):
        """展示机型分配结果"""
        # 计算子项物料平均满足率
        avg_material_satisfaction = self._calculate_avg_material_satisfaction(result)

        # 更新统计信息
        stats = (
            f"机型: {result.model_name} ({result.model_code})\n"
            f"计划制造数量: {result.plan_quantity} 台\n"
            f"实际可生产: {result.allocated_quantity} 台\n"
            f"满足率: {result.satisfaction_rate:.2f}%\n"
            f"子项物料平均满足率: {avg_material_satisfaction:.2f}%"
        )
        self.stats_var.set(stats)

        # 更新满足率进度条
        self.satisfaction_progress['value'] = result.satisfaction_rate
        self.satisfaction_label.config(text=f"{result.satisfaction_rate:.2f}%")

        # 更新物料分配详情
        self.materials_tree.delete(*self.materials_tree.get_children())

        for material_code, allocated_qty in result.allocated_materials.items():
            required_qty = result.allocated_materials.get(material_code, 0) + result.shortage_materials.get(material_code, 0)
            shortage_qty = result.shortage_materials.get(material_code, 0)

            self.materials_tree.insert(
                "",
                tk.END,
                values=(
                    material_code,
                    f"{required_qty:.2f}",
                    f"{allocated_qty:.2f}",
                    f"{shortage_qty:.2f}"
                )
            )

    def _calculate_avg_material_satisfaction(self, result: AllocationResult) -> float:
        """
        计算子项物料平均满足率

        Args:
            result: 机型分配结果

        Returns:
            物料平均满足率（百分比）
        """
        if not result.allocated_materials or not result.bom_items:
            return 0.0

        total_satisfaction = 0.0
        material_count = 0

        # 遍历所有BOM物料
        for bom_item in result.bom_items:
            material_code = bom_item.component_item_number
            required_qty = bom_item.component_num * result.plan_quantity
            allocated_qty = result.allocated_materials.get(material_code, 0)

            # 计算单个物料的满足率
            if required_qty > 0:
                satisfaction = min(allocated_qty / required_qty, 1.0) * 100
                total_satisfaction += satisfaction
                material_count += 1

        # 计算平均满足率
        if material_count > 0:
            return total_satisfaction / material_count
        else:
            return 0.0
    
    def clear(self):
        """清空结果"""
        self.stats_var.set("")
        self.satisfaction_progress['value'] = 0
        self.satisfaction_label.config(text="0%")
        self.materials_tree.delete(*self.materials_tree.get_children())
