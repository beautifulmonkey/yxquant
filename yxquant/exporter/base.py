from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional


class BaseExporter(ABC):
    """导出器基类"""
    
    def __init__(self, output_path: str, name: Optional[str] = None, **kwargs):
        self.output_path = Path(output_path)
        self.name = name or self.__class__.__name__
        self.kwargs = kwargs
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def export(self, engine, result) -> Any:
        """
        导出回测结果
        
        Args:
            engine: 回测引擎
            result: 回测结果
        """
        pass
