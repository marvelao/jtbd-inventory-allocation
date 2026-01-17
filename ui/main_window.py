"""
主窗口界面
"""
import tkinter as tk
from tkinter import ttk, messagebox
from ui.config_frame import ConfigFrame
from ui.result_frame import ResultFrame
from database.connection import db_manager


class MainWindow:
    """主窗口类"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("JTBD库存分配系统")
        self.root.geometry("1200x800")
        
        # 初始化数据库连接
        self.db_connected = db_manager.connect()
        
        # 创建界面
        self.create_widgets()
        
        # 机型配置数据
        self.model_a = None
        self.model_b = None
    
    def create_widgets(self):
        """创建界面组件"""
        # 顶部标题
        title_frame = ttk.Frame(self.root, padding="10")
        title_frame.pack(fill=tk.X)
        
        title_label = ttk.Label(
            title_frame,
            text="JTBD库存分配系统 - A/B机型库存竞争解决方案",
            font=("Arial", 16, "bold")
        )
        title_label.pack()
        
        # 主内容区域
        main_content = ttk.Frame(self.root)
        main_content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 左侧：配置区域
        left_frame = ttk.Frame(main_content)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # 配置框架
        self.config_frame = ConfigFrame(left_frame, self)
        self.config_frame.pack(fill=tk.BOTH, expand=True)
        
        # 右侧：结果展示区域
        right_frame = ttk.Frame(main_content)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # 结果框架
        self.result_frame = ResultFrame(right_frame)
        self.result_frame.pack(fill=tk.BOTH, expand=True)
        
        # 底部按钮区域
        button_frame = ttk.Frame(self.root, padding="10")
        button_frame.pack(fill=tk.X)
        
        # 执行分配按钮
        allocate_btn = ttk.Button(
            button_frame,
            text="执行库存分配",
            command=self.execute_allocation
        )
        allocate_btn.pack(side=tk.LEFT, padx=5)
        
        # 清空按钮
        clear_btn = ttk.Button(
            button_frame,
            text="清空所有数据",
            command=self.clear_all
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        # 退出按钮
        exit_btn = ttk.Button(
            button_frame,
            text="退出系统",
            command=self.on_closing
        )
        exit_btn.pack(side=tk.RIGHT, padx=5)
        
        # 状态栏
        self.status_var = tk.StringVar()
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        if self.db_connected:
            self.status_var.set("数据库连接成功，系统就绪")
        else:
            self.status_var.set("数据库连接失败，请检查连接配置")
    
    def execute_allocation(self):
        """执行库存分配"""
        try:
            # 获取配置数据
            config_a = self.config_frame.get_model_a_config()
            config_b = self.config_frame.get_model_b_config()
            
            if not config_a or not config_b:
                messagebox.showerror("错误", "请先完善A、B机型的配置信息")
                return
            
            # 导入分配算法
            from core.allocation import InventoryAllocator
            from core.calculator import SatisfactionCalculator
            
            # 创建分配器
            allocator = InventoryAllocator(db_manager)
            
            # 执行分配
            allocation_results = allocator.allocate(config_a, config_b)
            
            # 计算满足率
            calculator = SatisfactionCalculator()
            results = calculator.calculate_satisfaction(config_a, config_b, allocation_results)
            
            # 展示结果
            self.result_frame.display_results(results)
            
            self.status_var.set("库存分配完成")
            messagebox.showinfo("成功", "库存分配完成！")
            
        except Exception as e:
            messagebox.showerror("错误", f"分配失败：{str(e)}")
            self.status_var.set(f"分配失败: {str(e)}")
    
    def clear_all(self):
        """清空所有数据"""
        self.config_frame.clear_all()
        self.result_frame.clear_all()
        self.status_var.set("数据已清空")
    
    def on_closing(self):
        """关闭窗口"""
        if messagebox.askokcancel("退出", "确定要退出系统吗？"):
            db_manager.disconnect()
            self.root.destroy()
