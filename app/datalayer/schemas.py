"""schemas"""
from dataclasses import dataclass
import numpy as np


@dataclass
class Eyes:
    """eyes or eggs in the picture"""
    left: np.array
    right: np.array


class NotEyesException(Exception):
    """Exception"""