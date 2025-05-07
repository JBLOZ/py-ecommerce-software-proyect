"""
State memory for the app.
WARNING: If the app is restarted, the state will be lost.
"""

from typing import Dict, List
from app.api.webhook import Prediction

result_store: Dict[str, List[Prediction]] = {}
