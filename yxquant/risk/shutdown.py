"""
风险引擎 - 处理程序异常并执行紧急关闭
"""
import sys
import traceback
import threading
from typing import Optional, Callable
import backtrader as bt
from yxquant.utils.logger import get_logger

logger = get_logger('live')


def emergency_shutdown(cerebro: bt.Cerebro, error_msg: str,
                      exception: Optional[Exception] = None,
                      alert = None):
    """
    紧急关闭程序

    Args:
        cerebro: Backtrader Cerebro实例
        error_msg: 错误消息
        exception: 异常对象（可选）
        alert: （可选）
    """
    logger.critical(f"🚨 紧急关闭程序 - {error_msg}")

    try:
        # 1. 平仓所有仓位和取消所有挂单
        if hasattr(cerebro.broker, 'close_all'):
            logger.critical("正在关闭所有仓位和取消所有挂单...")
            cerebro.broker.close_all()
        else:
            logger.critical("Broker没有close_all方法，跳过平仓操作")
    except Exception as e:
        logger.critical(f"关闭仓位时出错: {e}", exc_info=True)

    try:
        # 2. 停止cerebro运行
        logger.critical("正在停止cerebro运行...")
        if hasattr(cerebro, 'runstop'):
            cerebro.runstop()
        else:
            logger.critical("Cerebro没有runstop方法")
    except Exception as e:
        logger.critical(f"停止cerebro时出错: {e}", exc_info=True)

    try:
        # 3. 发送Alert通知
        if alert:
            logger.critical("正在发送Alert通知...")
            error_details = error_msg
            if exception:
                error_details += f"\n\n异常类型: {type(exception).__name__}"
                error_details += f"\n异常详情: {str(exception)}"
                error_details += f"\n\n堆栈跟踪:\n```\n{traceback.format_exc()}\n```"

            alert.notify_error(
                error_details,
                strategy="系统紧急关闭",
                exception=exception
            )
        else:
            logger.critical("未配置Alert webhook URL，跳过通知")
    except Exception as e:
        logger.critical(f"发送Alert通知时出错: {e}", exc_info=True)

    # 4. 退出程序
    logger.critical("程序即将退出...")


def setup_exception_handler(cerebro: bt.Cerebro, alert = None):
    """
    设置全局异常处理器（包括主线程、子线程）
    """
    original_excepthook = sys.excepthook

    def exception_handler(exc_type, exc_value, exc_traceback):
        """全局异常处理器（主线程）"""
        if exc_type == KeyboardInterrupt:
            original_excepthook(exc_type, exc_value, exc_traceback)
            return
        error_msg = f"程序遇到未捕获的异常: {exc_type.__name__}: {str(exc_value)}"
        logger.critical(error_msg, exc_info=(exc_type, exc_value, exc_traceback))
        emergency_shutdown(cerebro, error_msg, exc_value, alert)

    def thread_exception_handler(args):
        """线程异常处理器"""
        exc_type, exc_value, exc_traceback = args.exc_type, args.exc_value, args.exc_traceback
        error_msg = f"线程中发生未捕获的异常: {exc_type.__name__}: {str(exc_value)}"
        logger.critical(error_msg, exc_info=(exc_type, exc_value, exc_traceback))
        emergency_shutdown(cerebro, error_msg, exc_value, alert)


    # 设置主线程异常处理器
    sys.excepthook = exception_handler
    # 设置线程异常处理器
    threading.excepthook = thread_exception_handler

