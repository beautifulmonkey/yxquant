import shutil
import json
from datetime import datetime
from pathlib import Path
from .base import BaseExporter


class DistExporter(BaseExporter):

    def export(self, engine, back_result):
        """复制dist目录到输出路径"""
        current_dir = Path(__file__).parent.parent
        dist_source = current_dir / "dist"
        dist_target = self.output_path / "dist"
        assert dist_source.exists()
        if not dist_target.exists():
            shutil.copytree(dist_source, dist_target)
            print(f"已复制dist目录到: {dist_target}")

        _config = {
            "running_mode": engine.cerebro.p.running_mode.value,
            "backtest_mode": engine.ctx.profile.mode.value,
            "datetime": str(datetime.now()),
        }
        with open(f"{dist_target}/config.json", "w") as outfile:
            json.dump(_config, outfile)







