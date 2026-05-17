from dataclasses import dataclass
import numpy as np


@dataclass
class FramePacket:
    frame: np.ndarray
    frame_id: str | int 