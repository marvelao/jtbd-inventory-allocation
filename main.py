"""
JTBD库存分配系统 - 主程序入口

功能：
- 支持A、B两款机型的库存分配
- 根据优先级规则分配共用物料
- 计算并展示各机型的满足率
"""
import tkinter as tk
from ui.main_window import MainWindow
import sys


def main():
    """主函数"""
    # 创建主窗口
    root = tk.Tk()
    
    # 创建主窗口实例
    app = MainWindow(root)
    
    # 设置窗口关闭事件
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # 启动主循环
    root.mainloop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"程序运行出错: {e}")
        sys.exit(1)
