from dataclasses import dataclass


@dataclass
class Metrics:
    iou: float
    fps: float