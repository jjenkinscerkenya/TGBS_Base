"""
Metrics module for temporal analysis and metric calculations.

Provides time-series compositing, disturbance detection, landscape metrics,
and vegetation/productivity/moisture indices.
"""

from .temporal import (
    _validate_composite_stat,
    _apply_stat,
    _time_windows,
)

__all__ = [
    "_validate_composite_stat",
    "_apply_stat",
    "_time_windows",
]
