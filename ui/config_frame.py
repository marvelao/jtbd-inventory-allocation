"""
配置界面 - 机型信息管理和参数设置
"""
import tkinter as tk
from tkinter import ttk
from database.connection import db_manager
from database.models import ModelConfig, BOMItem


class ConfigFrame(ttk.Frame):
    """配置框架"""
    
    def __init__(self, parent, main_window):
        super().__init__(parent)
        self.main_window = main_window
        self.create_widgets()
        self.load_available_models()
    
    def create_widgets(self):
        """创建配置界面组件"""
        # 标题
        title_label = ttk.Label(
            self,
            text="机型配置与参数设置",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=10)
        
        # 创建Notebook用于切换A/B机型配置
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 机型A配置页
        self.model_a_frame = ModelConfigFrame(self.notebook, "机型 A")
        self.notebook.add(self.model_a_frame, text="机型 A")
        
        # 机型B配置页
        self.model_b_frame = ModelConfigFrame(self.notebook, "机型 B")
        self.notebook.add(self.model_b_frame, text="机型 B")
    
    def load_available_models(self):
        """加载可用机型列表"""
        try:
            parent_items = db_manager.get_all_parent_items()
            if parent_items:
                models = [item[0] for item in parent_items]
                self.model_a_frame.set_available_models(models, other_frame=self.model_b_frame)
                self.model_b_frame.set_available_models(models, other_frame=self.model_a_frame)
        except Exception as e:
            print(f"加载机型列表失败: {e}")
    
    def get_model_a_config(self):
        """获取机型A配置"""
        return self.model_a_frame.get_config()
    
    def get_model_b_config(self):
        """获取机型B配置"""
        return self.model_b_frame.get_config()
    
    def clear_all(self):
        """清空所有配置"""
        self.model_a_frame.clear()
        self.model_b_frame.clear()


class ModelConfigFrame(ttk.Frame):
    """单机型配置框架"""
    
    def __init__(self, parent, model_label):
        super().__init__(parent)
        self.model_label = model_label
        self.available_models = []
        self.other_frame = None  # 另一个机型的引用
        self.bom_items = []
        self.create_widgets()
    
    def create_widgets(self):
        """创建配置组件"""
        # 机型选择区域
        selection_frame = ttk.LabelFrame(self, text=f"{self.model_label} 选择", padding="10")
        selection_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 机型编码选择
        ttk.Label(selection_frame, text="机型编码:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.model_code_var = tk.StringVar()
        self.model_code_combo = ttk.Combobox(
            selection_frame,
            textvariable=self.model_code_var,
            state="readonly"
        )
        self.model_code_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        self.model_code_combo.bind("<<ComboboxSelected>>", self.on_model_selected)
        
        # 机型名称
        ttk.Label(selection_frame, text="机型名称:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.model_name_var = tk.StringVar()
        self.model_name_entry = ttk.Entry(
            selection_frame,
            textvariable=self.model_name_var
        )
        self.model_name_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 刷新按钮
        refresh_btn = ttk.Button(
            selection_frame,
            text="刷新机型列表",
            command=self.refresh_models
        )
        refresh_btn.grid(row=0, column=2, padx=5, pady=5)
        
        selection_frame.columnconfigure(1, weight=1)
        
        # 参数设置区域
        params_frame = ttk.LabelFrame(self, text="生产参数设置", padding="10")
        params_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 计划制造数量
        ttk.Label(params_frame, text="计划制造数量:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.plan_quantity_var = tk.IntVar(value=0)
        plan_quantity_spin = ttk.Spinbox(
            params_frame,
            from_=0,
            to=100000,
            textvariable=self.plan_quantity_var
        )
        plan_quantity_spin.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # 优先级
        ttk.Label(params_frame, text="分配优先级:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        self.priority_var = tk.IntVar(value=1)
        priority_frame = ttk.Frame(params_frame)
        priority_frame.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Radiobutton(
            priority_frame,
            text="高优先级",
            variable=self.priority_var,
            value=1
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            priority_frame,
            text="低优先级",
            variable=self.priority_var,
            value=2
        ).pack(side=tk.LEFT, padx=5)
        
        # 加载BOM按钮
        load_bom_btn = ttk.Button(
            params_frame,
            text="加载BOM数据",
            command=self.load_bom_data
        )
        load_bom_btn.grid(row=2, column=0, columnspan=2, pady=10)
        
        params_frame.columnconfigure(1, weight=1)
        
        # BOM信息展示区域
        bom_frame = ttk.LabelFrame(self, text="BOM物料清单", padding="10")
        bom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建Treeview显示BOM数据
        columns = ("物料编码", "物料描述", "数量")
        self.bom_tree = ttk.Treeview(bom_frame, columns=columns, show="headings")
        
        for col in columns:
            self.bom_tree.heading(col, text=col)
            self.bom_tree.column(col, width=100)
        
        # 添加滚动条
        bom_scrollbar = ttk.Scrollbar(bom_frame, orient=tk.VERTICAL, command=self.bom_tree.yview)
        self.bom_tree.configure(yscrollcommand=bom_scrollbar.set)
        
        self.bom_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        bom_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # BOM统计信息
        self.bom_stats_var = tk.StringVar()
        bom_stats_label = ttk.Label(bom_frame, textvariable=self.bom_stats_var)
        bom_stats_label.pack(fill=tk.X, pady=5)
    
    def set_available_models(self, models, other_frame=None):
        """
        设置可用机型列表

        Args:
            models: 可用机型列表
            other_frame: 另一个机型的引用，用于互斥选择
        """
        self.other_frame = other_frame
        self.available_models = models
        self.model_code_combo['values'] = models
    
    def refresh_models(self):
        """刷新机型列表"""
        self.load_available_models()
    
    def load_available_models(self):
        """从数据库加载可用机型"""
        try:
            parent_items = db_manager.get_all_parent_items()
            if parent_items:
                models = [item[0] for item in parent_items]
                self.set_available_models(models, self.other_frame)
        except Exception as e:
            print(f"加载机型列表失败: {e}")
    
    def on_model_selected(self, event):
        """机型选择事件"""
        model_code = self.model_code_var.get()
        if model_code:
            # 自动填充机型名称（使用机型编码）
            self.model_name_var.set(model_code)

            # 更新另一个机型的可用列表（排除已选择的机型）
            if self.other_frame:
                available_for_other = [
                    model for model in self.available_models if model != model_code
                ]
                self.other_frame.set_available_models(available_for_other, self)
    
    def load_bom_data(self):
        """加载BOM数据"""
        model_code = self.model_code_var.get()
        if not model_code:
            return
        
        try:
            bom_data = db_manager.get_bom_data(model_code)
            if bom_data:
                self.bom_items = []
                self.bom_tree.delete(*self.bom_tree.get_children())
                
                for row in bom_data:
                    bom_item = BOMItem(
                        parent_item_number=row[0],
                        component_item_number=row[1],
                        component_description=row[2] if row[2] else "",
                        component_num=row[3] if row[3] else 0
                    )
                    self.bom_items.append(bom_item)
                    
                    self.bom_tree.insert(
                        "",
                        tk.END,
                        values=(row[1], row[2] if row[2] else "", row[3] if row[3] else 0)
                    )
                
                # 更新统计信息
                self.bom_stats_var.set(f"共 {len(self.bom_items)} 个物料")
            else:
                self.bom_tree.delete(*self.bom_tree.get_children())
                self.bom_items = []
                self.bom_stats_var.set("未找到BOM数据")
        
        except Exception as e:
            print(f"加载BOM数据失败: {e}")
            self.bom_stats_var.set(f"加载失败: {str(e)}")
    
    def get_config(self):
        """获取配置"""
        model_code = self.model_code_var.get()
        model_name = self.model_name_var.get()
        plan_quantity = self.plan_quantity_var.get()
        priority = self.priority_var.get()
        
        if not model_code or plan_quantity <= 0 or not self.bom_items:
            return None
        
        return ModelConfig(
            model_code=model_code,
            model_name=model_name,
            plan_quantity=plan_quantity,
            priority=priority,
            bom_items=self.bom_items
        )
    
    def clear(self):
        """清空配置"""
        self.model_code_var.set("")
        self.model_name_var.set("")
        self.plan_quantity_var.set(0)
        self.priority_var.set(1)
        self.bom_tree.delete(*self.bom_tree.get_children())
        self.bom_items = []
        self.bom_stats_var.set("")

        # 恢复另一个机型的可用列表
        if self.other_frame:
            self.other_frame.set_available_models(self.available_models, self)
