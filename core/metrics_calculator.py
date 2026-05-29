from pathlib import Path
import cv2
import numpy as np

from core.domain.metrics import Metrics


class MetricsCalculator:
    def __init__(self):
        self.labels_dir = None
        self.num_images = 0
        
    
    def set_base_path(self, new_base_path: str | Path):
        self.labels_dir = Path(new_base_path, "labels") 
    
    
    def update(self, results: list[dict],  frame_id: str) -> Metrics | None:
        if not results:
            return None
        
        fps = results[0].get("fps", 0.0) if results else 0.0
        image_shape = results[0].get("shape")
        if image_shape is None:
            return None

        gt_path = Path(self.labels_dir, f"{frame_id}.txt")
        if not gt_path.exists():
            return None
        
        gt_mask = self._load_yolo_mask(gt_path, image_shape)
        if gt_mask is None:
            return None
        
        pred_combined = np.zeros(image_shape, dtype=np.uint8)
        
        for pred in results:
            mask = pred.get("mask")
            if mask is None:
                continue
            
            if mask.shape != image_shape:
                mask = cv2.resize(
                    mask, (image_shape[1], image_shape[0]), 
                    interpolation=cv2.INTER_NEAREST
                )
            pred_combined = np.maximum(pred_combined, (mask > 0).astype(np.uint8))

        intersection = np.logical_and(pred_combined, gt_mask).sum()
        union = np.logical_or(pred_combined, gt_mask).sum()
        iou = float(intersection / union) if union > 0 else 0.0
        
        return Metrics(fps=fps, iou=iou)
                  
        
    def _load_yolo_mask(self, path: Path, image_shape: tuple[int, int]) -> np.ndarray | None:
        h, w = image_shape
        mask = np.zeros((h, w), dtype=np.uint8)
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) < 5:
                        continue
                    
                    coords = list(map(float, parts[1:]))
                    
                    if len(coords) == 4:
                        x_c, y_c, bw, bh = coords
                        x1 = int((x_c - bw/2) * w)
                        y1 = int((y_c - bh/2) * h)
                        x2 = int((x_c + bw/2) * w)
                        y2 = int((y_c + bh/2) * h)
                        
                        x1, x2 = max(0, x1), min(w, x2)
                        y1, y2 = max(0, y1), min(h, y2)
                        mask[y1:y2, x1:x2] = 1
                        
                    elif len(coords) >= 6 and len(coords) % 2 == 0:
                        pts = np.array([
                            [int(coords[i] * w), int(coords[i+1] * h)] 
                            for i in range(0, len(coords), 2)
                        ], dtype=np.int32)
                        pts = pts.reshape((-1, 1, 2))
                        cv2.fillPoly(mask, [pts], 1)
                        
        except Exception as e:
            print(f"Error {path}: {e}")
            return None
            
        return mask