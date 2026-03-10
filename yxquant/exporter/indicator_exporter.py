import math
import json
from typing import List, Dict
from .base import BaseExporter


class IndicatorDataExporter(BaseExporter):
    indicators_data: Dict[str, Dict[str, List[float]]] = {}

    def replace_nan(self, arr):
        first_valid = next(x for x in arr if not math.isnan(x))
        for i, v in enumerate(arr):
            if math.isnan(v):
                arr[i] = first_valid
        return arr

    def extract_indicator_lines(self, indicator_obj):
        lines_data = {}
        for line_name in indicator_obj.lines.getlinealiases():
            line_obj = getattr(indicator_obj.lines, line_name)
            line_data = self.replace_nan(line_obj.array.tolist())
            lines_data[line_name] = line_data
        return lines_data

    def export(self, engine, back_result):
        for strat in engine.cerebro.runningstrats:
            exported_indicators = strat.params.exported_indicators
            for idc_alias in exported_indicators:
                idc_obj = getattr(engine.cerebro.runningstrats[0], idc_alias)
                idc_name = idc_obj.__class__.__name__
                lines_data = self.extract_indicator_lines(idc_obj)
                self.indicators_data[idc_name] = lines_data

        with open(f"{self.output_path}/dist/indicator_data.json", "w") as outfile:
            json.dump(self.indicators_data, outfile)






