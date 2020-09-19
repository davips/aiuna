from typing import Dict, Any

from aiuna.types import Data


class NoInfo:
    def _enhancer_info(self, data: Data) -> Dict[str, Any]:
        return {}

    def _model_info(self, data: Data) -> Dict[str, Any]:
        return {}
