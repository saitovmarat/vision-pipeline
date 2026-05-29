from core.segmentation.yolo_segmenter import YOLOSegmenter
from core.segmentation.gsam_segmenter import GSAMSegmenter


class SegmenterManager:
    def __init__(self, model: str, weights: dict):
        if model == "yolo":
            self.segmenter = YOLOSegmenter(weights['yolo_weights'])
        else:
            self.segmenter = GSAMSegmenter()
        
        
    def predict(self, frame):
        return self.segmenter.predict(frame)