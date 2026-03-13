"""
数据库连接管理, 基于DatabaseProxy
"""

from typing import Union
from peewee import PostgresqlDatabase, SqliteDatabase, MySQLDatabase
from .models import database_proxy, Trade


def init_db(db: Union[MySQLDatabase, PostgresqlDatabase, SqliteDatabase]) -> Union[SqliteDatabase, PostgresqlDatabase]:
    """
    初始化数据库连接
    """
    database_proxy.initialize(db)
    db.connect()
    db.create_tables([Trade])
    return db


def init_sqlite(database: str = 'quant.db') -> SqliteDatabase:
    """
    初始化SQLite数据库

    Args:
        database: 数据库文件路径

    Returns:
        SQLite数据库连接
    """

    db = SqliteDatabase(database)
    return init_db(db)


def init_postgresql(database: str, user: str, password: str, 
                   host: str = 'localhost', port: int = 5432, **kwargs) -> PostgresqlDatabase:
    """
    初始化PostgreSQL数据库
    
    Args:
        database: 数据库名称
        user: 用户名
        password: 密码
        host: 主机地址
        port: 端口
        **kwargs: 其他连接参数
        
    Returns:
        PostgreSQL数据库连接
    """

    db = PostgresqlDatabase(database=database, user=user, password=password,
                            host=host, port=port, **kwargs)
    return init_db(db)

