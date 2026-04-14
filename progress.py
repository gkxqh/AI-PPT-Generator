"""
进度条模块 - 显示PPT生成过程的可视化进度
"""
import sys
import time


class ProgressBar:
    """
    进度条类 - 显示任务进度
    """
    
    def __init__(self, total_steps=5, desc="生成PPT"):
        """
        初始化进度条
        
        Args:
            total_steps: 总步骤数
            desc: 任务描述
        """
        self.total_steps = total_steps
        self.current_step = 0
        self.desc = desc
        self.step_names = [
            "生成PPT大纲",
            "信息检索",
            "生成PPT内容",
            "内容校验",
            "生成PPT文件"
        ]
        self.step_status = ["pending"] * total_steps  # pending, running, done, error
        self.start_time = None
        self.step_start_time = None
    
    def start(self):
        """
        开始进度条
        """
        self.start_time = time.time()
        self._print_header()
    
    def _print_header(self):
        """
        打印进度条头部
        """
        print()
        print("=" * 60)
        print(f"  {self.desc}")
        print("=" * 60)
        print()
    
    def update(self, step, status="running", message=None):
        """
        更新进度
        
        Args:
            step: 当前步骤（1-based）
            status: 状态 (running/done/error)
            message: 附加消息
        """
        self.current_step = step - 1
        
        # 更新步骤状态
        if status == "done":
            self.step_status[self.current_step] = "done"
        elif status == "error":
            self.step_status[self.current_step] = "error"
        else:
            # 标记当前步骤为running
            self.step_status[self.current_step] = "running"
            # 标记之前的步骤为done
            for i in range(self.current_step):
                if self.step_status[i] != "error":
                    self.step_status[i] = "done"
        
        self._render(message)
    
    def _render(self, message=None):
        """
        渲染进度条
        """
        # 打印进度概览
        progress_percent = (self.current_step + 1) / self.total_steps * 100
        
        # 进度条可视化 - 使用ASCII兼容字符
        bar_length = 30
        filled_length = int(bar_length * (self.current_step + 1) / self.total_steps)
        bar = "=" * filled_length + "-" * (bar_length - filled_length)
        
        # 计算耗时
        elapsed_str = ""
        if self.start_time:
            elapsed = time.time() - self.start_time
            elapsed_str = f" | {elapsed:.1f}s"
        
        # 清除当前行并打印进度
        print(f"\r  [{bar}] {progress_percent:5.1f}% ({self.current_step + 1}/{self.total_steps}){elapsed_str}    ")
        
        # 打印各步骤状态
        for i in range(self.total_steps):
            status = self.step_status[i]
            name = self.step_names[i]
            status_icon = self._get_status_icon(status)
            
            if status == "running":
                print(f"  > {status_icon} Step {i+1}: {name}")
            elif status == "done":
                print(f"    {status_icon} Step {i+1}: {name}")
            elif status == "error":
                print(f"    {status_icon} Step {i+1}: {name} [ERROR]")
            else:
                print(f"    {status_icon} Step {i+1}: {name}")
        
        # 打印附加消息
        if message:
            print(f"       -> {message}")
        
        # 打印分隔线
        print("  " + "-" * 50)
    
    def _get_status_icon(self, status):
        """
        获取状态图标 - 使用ASCII兼容字符
        """
        icons = {
            "pending": "[ ]",
            "running": "[>]",
            "done": "[OK]",
            "error": "[X]"
        }
        return icons.get(status, "[ ]")
    
    def complete(self, message="完成!"):
        """
        完成进度条
        """
        # 标记所有步骤为完成
        self.step_status = ["done"] * self.total_steps
        
        # 渲染最终状态
        self._render(message)
        
        # 打印完成信息
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        print()
        print("=" * 60)
        print(f"  [SUCCESS] {message}")
        print(f"  Total time: {elapsed:.1f} seconds")
        print("=" * 60 + "\n")
    
    def error(self, step, message="发生错误"):
        """
        显示错误
        """
        self.update(step, "error", message)
        
        print()
        print("=" * 60)
        print(f"  [ERROR] {message}")
        print("=" * 60 + "\n")


class SimpleProgress:
    """
    简单进度条 - 单行显示
    """
    
    def __init__(self, total=100, desc="进度", width=50):
        """
        初始化简单进度条
        
        Args:
            total: 总数
            desc: 描述
            width: 进度条宽度
        """
        self.total = total
        self.desc = desc
        self.width = width
        self.current = 0
        self.start_time = None
    
    def update(self, n=1):
        """
        更新进度
        """
        if self.start_time is None:
            self.start_time = time.time()
        
        self.current += n
        self._render()
    
    def _render(self):
        """
        渲染进度条
        """
        percent = self.current / self.total * 100
        filled = int(self.width * self.current / self.total)
        bar = "=" * filled + "-" * (self.width - filled)
        
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        # 使用 \r 回到行首覆盖之前的内容
        sys.stdout.write(f"\r  {self.desc}: [{bar}] {percent:.1f}% | {self.current}/{self.total} | {elapsed:.1f}s   ")
        sys.stdout.flush()
    
    def close(self):
        """
        关闭进度条
        """
        print()  # 换行


def create_progress_bar(total_steps=5, desc="生成PPT"):
    """
    创建进度条实例
    
    Args:
        total_steps: 总步骤数
        desc: 任务描述
    
    Returns:
        ProgressBar: 进度条实例
    """
    return ProgressBar(total_steps=total_steps, desc=desc)


# 测试代码
if __name__ == "__main__":
    import time
    
    print("测试进度条...")
    
    # 测试完整进度条
    progress = ProgressBar(total_steps=5, desc="PPT生成测试")
    progress.start()
    
    for i in range(1, 6):
        time.sleep(0.5)
        if i == 5:
            progress.complete("PPT生成成功!")
        else:
            progress.update(i, "done", f"步骤 {i} 完成")
    
    print("\n测试完成!")
