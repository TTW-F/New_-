"""
新日志系统使用示例

展示如何使用 Loguru + Rich 实现优雅的日志输出
"""

from api.core.logger import logger, console
from rich.panel import Panel
from rich.table import Table
from rich.progress import track
import time

# ============================================
# 1. 基础日志使用 (替代原来的 logging)
# ============================================

def basic_logging_example():
    """基础日志示例"""
    console.print("\n[bold cyan]1. 基础日志示例[/bold cyan]")
    
    # 不同级别的日志
    logger.debug("这是调试信息")
    logger.info("这是普通信息")
    logger.success("这是成功信息")  # Loguru 特有
    logger.warning("这是警告信息")
    logger.error("这是错误信息")
    
    # 带变量的日志
    user_id = 12345
    username = "张三"
    logger.info(f"用户登录: ID={user_id}, 用户名={username}")
    
    # 结构化日志
    logger.bind(user_id=user_id, username=username).info("用户操作")


# ============================================
# 2. 异常追踪 (自动美化异常信息)
# ============================================

def exception_tracking_example():
    """异常追踪示例"""
    console.print("\n[bold cyan]2. 异常追踪示例[/bold cyan]")
    
    try:
        result = 1 / 0
    except Exception as e:
        # Loguru 会自动美化异常堆栈
        logger.exception("发生了一个错误")


# ============================================
# 3. 上下文日志 (绑定上下文信息)
# ============================================

def context_logging_example():
    """上下文日志示例"""
    console.print("\n[bold cyan]3. 上下文日志示例[/bold cyan]")
    
    # 绑定请求上下文
    request_logger = logger.bind(
        request_id="req-123456",
        user_id=12345,
        ip="192.168.1.100"
    )
    
    request_logger.info("开始处理请求")
    request_logger.info("查询数据库")
    request_logger.success("请求处理完成")


# ============================================
# 4. Rich 美化输出 (表格、面板、进度条)
# ============================================

def rich_output_example():
    """Rich 美化输出示例"""
    console.print("\n[bold cyan]4. Rich 美化输出示例[/bold cyan]")
    
    # 面板输出
    console.print(Panel(
        "[green]系统启动成功![/green]\n"
        "API 地址: http://localhost:8000\n"
        "文档地址: http://localhost:8000/docs",
        title="🚀 启动信息",
        border_style="green"
    ))
    
    # 表格输出
    table = Table(title="用户列表")
    table.add_column("ID", style="cyan")
    table.add_column("用户名", style="magenta")
    table.add_column("状态", style="green")
    
    table.add_row("1", "张三", "在线")
    table.add_row("2", "李四", "离线")
    table.add_row("3", "王五", "在线")
    
    console.print(table)
    
    # 进度条
    console.print("\n处理数据中...")
    for i in track(range(20), description="加载中..."):
        time.sleep(0.05)


# ============================================
# 5. 性能日志 (记录执行时间)
# ============================================

def performance_logging_example():
    """性能日志示例"""
    console.print("\n[bold cyan]5. 性能日志示例[/bold cyan]")
    
    import time
    
    # 使用装饰器记录执行时间
    @logger.catch  # 自动捕获异常
    def slow_function():
        logger.info("开始执行耗时操作...")
        start = time.time()
        time.sleep(1)
        elapsed = time.time() - start
        logger.info(f"操作完成,耗时: {elapsed:.2f}秒")
    
    slow_function()


# ============================================
# 6. 实际应用场景
# ============================================

def real_world_example():
    """实际应用场景示例"""
    console.print("\n[bold cyan]6. 实际应用场景示例[/bold cyan]")
    
    # 模拟 API 请求处理
    request_id = "req-789012"
    user_id = 12345
    
    req_logger = logger.bind(request_id=request_id, user_id=user_id)
    
    req_logger.info("收到问答请求")
    req_logger.debug("查询知识图谱...")
    
    # 模拟查询结果
    entities = ["感冒", "发烧", "咳嗽"]
    req_logger.info(f"找到实体: {entities}")
    
    req_logger.debug("调用 LLM 生成回答...")
    req_logger.success("回答生成成功")
    
    # 使用 Rich 展示结果
    console.print(Panel(
        f"[green]✓[/green] 请求处理完成\n"
        f"请求ID: {request_id}\n"
        f"用户ID: {user_id}\n"
        f"实体数: {len(entities)}",
        title="处理结果",
        border_style="green"
    ))


# ============================================
# 运行所有示例
# ============================================

if __name__ == "__main__":
    console.print(Panel(
        "[bold cyan]优雅的日志系统使用示例[/bold cyan]\n"
        "Loguru + Rich",
        title="🎨 日志系统",
        border_style="cyan"
    ))
    
    basic_logging_example()
    exception_tracking_example()
    context_logging_example()
    rich_output_example()
    performance_logging_example()
    real_world_example()
    
    console.print("\n[bold green]✓ 所有示例运行完成![/bold green]")
    console.print("\n查看日志文件:")
    console.print("  - logs/app.log (所有日志)")
    console.print("  - logs/error.log (仅错误)")
