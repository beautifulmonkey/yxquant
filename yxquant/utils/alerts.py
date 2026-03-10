import requests
from typing import Optional, Dict, Any
from datetime import datetime
from yxquant.utils.logger import get_logger
from concurrent.futures import ThreadPoolExecutor

logger = get_logger('live')
_alert_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="alert")


class DiscordAlert:
    """Discord webhook通知"""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url
    
    def _send(self, content: str, embed: Optional[Dict[str, Any]] = None):
        if not self.webhook_url:
            return
        def _send_request():
            try:
                payload = {"content": content}
                if embed:
                    payload["embeds"] = [embed]
                
                requests.post(self.webhook_url, json=payload, timeout=5)
            except Exception as e:
                logger.error(f"Discord通知发送失败: {e}")
        
        _alert_executor.submit(_send_request)

    def notify_order(self, strategy: str, symbol: str, action: str, size: int, 
                     price: Optional[float] = None, status: str = "", order_ref: str = ""):
        """订单通知"""
        title = f"📋 订单通知 - {strategy}"
        fields = [
            {"name": "策略", "value": strategy, "inline": True},
            {"name": "品种", "value": symbol, "inline": True},
            {"name": "操作", "value": action, "inline": True},
            {"name": "数量", "value": str(size), "inline": True},
            {"name": "价格", "value": str(price) if price else "市价", "inline": True},
            {"name": "状态", "value": status, "inline": True},
        ]
        
        embed = {
            "title": title,
            "color": 0x3498db,
            "fields": fields,
            "timestamp": datetime.utcnow().isoformat()
        }
        self._send(f"订单通知 - {strategy}", embed)
    
    def notify_trade(self, strategy: str, symbol: str, action: str, size: int, 
                     price: float, pnl: Optional[float] = None):
        """成交通知"""
        title = f"💰 成交通知 - {strategy}"
        fields = [
            {"name": "策略", "value": strategy, "inline": False},
            {"name": "品种", "value": symbol, "inline": False},
            {"name": "操作", "value": action, "inline": False},
            {"name": "数量", "value": str(size), "inline": False},
            {"name": "价格", "value": str(price), "inline": False},
            {"name": "滑点", "value": "null", "inline": False},
        ]
        if pnl is not None:
            fields.append({"name": "盈亏", "value": f"{pnl:.2f}", "inline": True})
        
        color = 0x2ecc71 if (pnl is None or pnl >= 0) else 0xe74c3c
        embed = {
            "title": title,
            "color": color,
            "fields": fields,
            "timestamp": datetime.utcnow().isoformat()
        }
        self._send(f"成交通知 - {strategy}", embed)
    
    def notify_position(self, strategy: str, symbol: str, size: int, 
                        price: float, value: float, pnl: Optional[float] = None):
        """持仓通知"""
        title = f"📊 持仓更新 - {strategy}"
        fields = [
            {"name": "策略", "value": strategy, "inline": True},
            {"name": "品种", "value": symbol, "inline": True},
            {"name": "数量", "value": str(size), "inline": True},
            {"name": "均价", "value": str(price), "inline": True},
            {"name": "价值", "value": f"{value:.2f}", "inline": True},
        ]
        if pnl is not None:
            fields.append({"name": "浮动盈亏", "value": f"{pnl:.2f}", "inline": True})
        
        embed = {
            "title": title,
            "color": 0x9b59b6,
            "fields": fields,
            "timestamp": datetime.utcnow().isoformat()
        }
        self._send(f"持仓更新 - {strategy}", embed)
    
    def notify_error(self, error_msg: str, strategy: Optional[str] = None, exception: Optional[Exception] = None):
        """错误通知"""
        strategy_str = f" - {strategy}" if strategy else ""
        embed = {
            "title": f"❌ 系统错误{strategy_str}",
            "description": error_msg,
            "color": 0xe74c3c,
            "timestamp": datetime.utcnow().isoformat()
        }
        if exception:
            embed["fields"] = [{"name": "异常详情", "value": str(exception)}]
        self._send(f"系统错误{strategy_str}: {error_msg}", embed)
    
    def notify_warning(self, warning_msg: str, strategy: Optional[str] = None):
        """警告通知"""
        strategy_str = f" - {strategy}" if strategy else ""
        embed = {
            "title": f"⚠️ 系统警告{strategy_str}",
            "description": warning_msg,
            "color": 0xf39c12,
            "timestamp": datetime.utcnow().isoformat()
        }
        self._send(f"系统警告{strategy_str}: {warning_msg}", embed)
    
    def notify_critical(self, critical_msg: str, strategy: Optional[str] = None):
        """严重错误通知"""
        strategy_str = f" - {strategy}" if strategy else ""
        embed = {
            "title": f"🚨 严重错误{strategy_str}",
            "description": critical_msg,
            "color": 0xc0392b,
            "timestamp": datetime.utcnow().isoformat()
        }
        self._send(f"🚨 严重错误{strategy_str}: {critical_msg}", embed)
    
    def notify_info(self, info_msg: str, strategy: Optional[str] = None):
        """信息通知"""
        strategy_str = f" - {strategy}" if strategy else ""
        embed = {
            "title": f"ℹ️ 系统信息{strategy_str}",
            "description": info_msg,
            "color": 0x3498db,
            "timestamp": datetime.utcnow().isoformat()
        }
        self._send(f"系统信息{strategy_str}: {info_msg}", embed)


class DingTalkAlert:
    """钉钉 webhook通知"""
    
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url
    
    def _send(self, title: str, markdown_text: str):
        if not self.webhook_url:
            return

        def _send_request():
            keyword = "yxquant"
            try:
                payload = {
                    "msgtype": "markdown",
                    "markdown": {
                        "title": f"{keyword}{title}",
                        "text": markdown_text
                    }
                }
                res = requests.post(self.webhook_url, json=payload, timeout=5)
                if res.status_code == 200:
                    result = res.json()
                    if result.get("errcode") != 0:
                        logger.warning(f"钉钉通知返回错误: {result}")
            except Exception as e:
                logger.error(f"钉钉通知发送失败: {e}")
        
        _alert_executor.submit(_send_request)
    

    def notify_order(self, strategy: str, symbol: str, action: str, size: int, 
                     price: Optional[float] = None, status: str = "", order_ref: str = ""):
        """订单通知"""
        title = f"📋 订单通知 - {strategy}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        markdown_text = f"""## {title}

**策略**: {strategy}  
**品种**: {symbol}  
**操作**: {action}  
**数量**: {size}  
**价格**: {str(price) if price else '市价'}  
**状态**: {status}  
**时间**: {timestamp}
"""
        self._send(title, markdown_text)
    
    def notify_trade(self, strategy: str, symbol: str, action: str, size: int, 
                     price: float, pnl: Optional[float] = None):
        """成交通知"""
        title = f"💰 成交通知 - {strategy}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pnl_text = f"{pnl:.2f}" if pnl is not None else "未计算"
        pnl_emoji = ("📈" if pnl > 0 else "📉") if pnl is not None else ""
        
        markdown_text = f"""## {title}

**时间**: {timestamp}  
**策略**: {strategy}  
**品种**: {symbol}  
**操作**: {action}  
**数量**: {size}  
**价格**: {price}  
**滑点**: null  
**盈亏**: {pnl_emoji} {pnl_text}  
"""
        self._send(title, markdown_text)
    
    def notify_position(self, strategy: str, symbol: str, size: int, 
                        price: float, value: float, pnl: Optional[float] = None):
        """持仓通知"""
        title = f"📊 持仓更新 - {strategy}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pnl_text = f"{pnl:.2f}" if pnl is not None else "未计算"
        pnl_emoji = "📈" if (pnl is None or pnl >= 0) else "📉"
        
        markdown_text = f"""## {title}

**策略**: {strategy}  
**品种**: {symbol}  
**数量**: {size}  
**均价**: {price}  
**价值**: {value:.2f}  
**浮动盈亏**: {pnl_emoji} {pnl_text}  
**时间**: {timestamp}
"""
        self._send(title, markdown_text)
    

    def notify_error(self, error_msg: str, strategy: Optional[str] = None, exception: Optional[Exception] = None):
        """错误通知"""
        strategy_str = f" - {strategy}" if strategy else ""
        title = f"❌ 系统错误{strategy_str}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        markdown_text = f"""## {title}

**错误信息**: {error_msg}  
"""
        if exception:
            markdown_text += f"**异常详情**: {str(exception)}  \n"
        markdown_text += f"**时间**: {timestamp}"
        
        self._send(title, markdown_text)
    
    def notify_warning(self, warning_msg: str, strategy: Optional[str] = None):
        """警告通知"""
        strategy_str = f" - {strategy}" if strategy else ""
        title = f"⚠️ 系统警告{strategy_str}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        markdown_text = f"""## {title}

**警告信息**: {warning_msg}  
**时间**: {timestamp}
"""
        self._send(title, markdown_text)
    
    def notify_critical(self, critical_msg: str, strategy: Optional[str] = None):
        """严重错误通知"""
        strategy_str = f" - {strategy}" if strategy else ""
        title = f"🚨 严重错误{strategy_str}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        markdown_text = f"""## {title}

**严重错误**: {critical_msg}  
**时间**: {timestamp}
"""
        self._send(title, markdown_text)
    
    def notify_info(self, info_msg: str, strategy: Optional[str] = None):
        """信息通知"""
        strategy_str = f" - {strategy}" if strategy else ""
        title = f"ℹ️ 系统信息{strategy_str}"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        markdown_text = f"""## {title}

**信息**: {info_msg}  
**时间**: {timestamp}
"""
        self._send(title, markdown_text)
