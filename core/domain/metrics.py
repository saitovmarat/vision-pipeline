from dataclasses import dataclass


@dataclass
class Metrics:
    mAP50: float
    mAP50_95: float