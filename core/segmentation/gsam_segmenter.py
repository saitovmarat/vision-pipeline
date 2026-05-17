from core.segmentation.base import ISegmenter


class GSAMSegmenter(ISegmenter):
    def __init__(self):
        ...
        
    def predict(self, frame):
        ...