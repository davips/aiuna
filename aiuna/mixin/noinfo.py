from functools import lru_cache
from typing import Dict, Any

from pjdata.types import Data


class NoInfo:
    @lru_cache()
    def _enhancer_info(self, data: Data) -> Dict[str, Any]:
        return {}

    @lru_cache()
    def _model_info(self, data: Data) -> Dict[str, Any]:
        return {}
