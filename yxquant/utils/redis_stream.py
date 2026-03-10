"""
Redis Stream 工具类，用于推送消息到 Redis Stream
"""
import json
import redis
from typing import Optional, Dict, Any


class RedisStreamPublisher:
    """Redis Stream 消息发布器"""
    
    def __init__(self, 
                 stream_name: str,
                 redis_host: str = "127.0.0.1",
                 redis_port: int = 6379,
                 redis_password: Optional[str] = None,
                 redis_db: int = 0,
                 maxlen: Optional[int] = None):
        self.stream_name = stream_name
        self.maxlen = maxlen
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
        self.redis_db = redis_db
        
        # 初始化 Redis 连接
        self._redis_client = None
        self._connect()
    
    def _connect(self):
        """建立 Redis 连接"""
        try:
            redis_kwargs = {
                'host': self.redis_host,
                'port': self.redis_port,
                'db': self.redis_db,
                'decode_responses': True,
            }
            if self.redis_password:
                redis_kwargs['password'] = self.redis_password
            
            self._redis_client = redis.StrictRedis(**redis_kwargs)
            # 测试连接
            self._redis_client.ping()
        except Exception as e:
            print(f"Redis 连接失败: {e}")
            self._redis_client = None
    
    def add(self, data: Dict[str, Any]) -> Optional[str]:
        if self._redis_client is None:
            print("Redis 客户端未初始化，无法发布消息")
            return None
        
        try:
            stream_fields = {}
            for key, value in data.items():
                if value is None:
                    stream_fields[key] = ""
                elif isinstance(value, bool):
                    stream_fields[key] = 1 if value else 0
                elif isinstance(value, (str, int, float)):
                    stream_fields[key] = value
                else:
                    stream_fields[key] = json.dumps(value)
            
            # 发布到 Redis Stream
            xadd_kwargs = {
                'name': self.stream_name,
                'fields': stream_fields,
            }
            if self.maxlen is not None:
                xadd_kwargs['maxlen'] = self.maxlen
            
            message_id = self._redis_client.xadd(**xadd_kwargs)
            
            return message_id
        except Exception as e:
            print(f"发布消息到 Redis Stream 失败: {e}")
            return None
    
    def close(self):
        """关闭 Redis 连接"""
        if self._redis_client:
            try:
                self._redis_client.close()
            except Exception:
                pass
            self._redis_client = None


class RedisStreamSubscriber:
    """
    轻量订阅器，使用 xread 读取最新消息（非消费者组）。
    """
    def __init__(self,
                 stream_name: str,
                 redis_host: str = "127.0.0.1",
                 redis_port: int = 6379,
                 redis_password: Optional[str] = None,
                 redis_db: int = 0):
        self.stream_name = stream_name
        self.redis_client = redis.StrictRedis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            db=redis_db,
            decode_responses=True,
        )
        self.redis_client.ping()

    def read_latest(self, block_ms: int = 100, count: int = 10, last_id: str = "$"):
        return self.redis_client.xread(
            streams={self.stream_name: last_id},
            count=count,
            block=block_ms,
        )

