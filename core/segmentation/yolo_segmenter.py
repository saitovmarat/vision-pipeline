from core.segmentation.base import ISegmenter
from ultralytics import YOLO


class YOLOSegmenter(ISegmenter):
    def __init__(self, weights_path):
        self.weights_path = weights_path
        self.model = YOLO(weights_path)
        
        
    def predict(self, frame):
        results = self.model.predict(frame, verbose=False)[0]

        total_time_ms = sum(results.speed.values())
        fps = 1000.0 / total_time_ms if total_time_ms > 0 else 0.0
        image_shape = tuple(results.orig_shape)

        predictions = []
        
        if results.boxes is not None and results.masks is not None:
            for box, mask, cls_id, conf in zip(
                results.boxes.xyxy, 
                results.masks.data, 
                results.boxes.cls, 
                results.boxes.conf
            ):
                predictions.append({
                    'bbox': box.cpu().numpy(),
                    'mask': mask.cpu().numpy(),
                    'class_id': int(cls_id),
                    'confidence': float(conf),
                    'fps': round(fps, 2),
                    'shape': image_shape
                })
                
        return predictions     
            