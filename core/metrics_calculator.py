from pathlib import Path
import cv2
import numpy as np
import torch
from torchmetrics.detection import MeanAveragePrecision
from core.domain.metrics import Metrics



class MetricsCalculator:
    def __init__(self, iou_thresholds=None, class_metrics=None):
        self.labels_dir = None
        
        if iou_thresholds is None:
            self.iou_thresholds = torch.arange(0.5, 0.96, 0.05).tolist()
        else:
            self.iou_thresholds = list(iou_thresholds)
            
        self.metric = MeanAveragePrecision(
            box_format='xyxy',
            iou_type='segm',
            iou_thresholds=self.iou_thresholds,
            class_metrics=class_metrics,
            extended_summary=False
        )
    
    
    def switch_source(self, new_base_path: str | Path):
        self.labels_dir = Path(new_base_path, "labels_swapped") 
        self.metric.reset()
    
    
    def _gt_to_torchmetrics_format(self, label_name: str, img_h: int, img_w: int):
        gt_lines = Path(self.labels_dir, label_name + ".txt").read_text().strip().split("\n")
        boxes, labels, masks = [], [], []
        
        for line in gt_lines:
            coords = list(map(float, line.strip().split()))
            cls_id = int(coords[0])
            labels.append(torch.tensor(cls_id, dtype=torch.int64))
            
            pts = np.array(coords[1:], dtype=np.float32).reshape(-1, 2)
            pts[:, 0] *= img_w
            pts[:, 1] *= img_h
            pts = np.round(pts).astype(np.int32)
            
            mask = np.zeros((img_h, img_w), dtype=np.uint8)
            cv2.fillPoly(mask, [pts], 1)
            masks.append(torch.from_numpy(mask).bool())
            
            x, y, bw, bh = cv2.boundingRect(pts)
            boxes.append(torch.tensor([x, y, x + bw, y + bh], dtype=torch.float32))
            
        return [{
            'boxes': torch.stack(boxes) if boxes else torch.empty(0, 4, dtype=torch.float32),
            'labels': torch.stack(labels) if labels else torch.empty(0, dtype=torch.int64),
            'masks': torch.stack(masks) if masks else torch.empty(0, img_h, img_w, dtype=torch.bool),
        }]
        
        
    @staticmethod 
    def _preds_to_torchmetrics_format(preds: list[dict], img_h: int, img_w: int):
        if not preds:
            return [{
                "boxes": torch.empty(0, 4, dtype=torch.float32),
                "scores": torch.empty(0, dtype=torch.float32),
                "labels": torch.empty(0, dtype=torch.int64),
                "masks": torch.empty(0, img_h, img_w, dtype=torch.bool)
            }]
            
        boxes = np.stack([p['bbox'] for p in preds])
        scores = np.array([p['confidence'] for p in preds])
        labels = np.array([p['class_id'] for p in preds])        
        masks = np.stack([
            cv2.resize(p['mask'], (img_w, img_h), interpolation=cv2.INTER_NEAREST)
            for p in preds
        ])
        
        return [{
            "boxes": torch.from_numpy(boxes).float(),
            "scores": torch.from_numpy(scores).float(),
            "labels": torch.from_numpy(labels).long(),
            "masks": torch.from_numpy(masks).bool()
        }]
        
    
    def update(self, predictions: list[dict], label_name: str, frame_shape: tuple):
        h, w = frame_shape[:2]
        preds = self._preds_to_torchmetrics_format(predictions, img_h=h, img_w=w)
        target = self._gt_to_torchmetrics_format(label_name, img_h=h, img_w=w)
        
        self.metric.update(preds=preds, target=target)  
    
    
    def compute(self):
        metrics = self.metric.compute()
        return Metrics(
            mAP50=metrics['map_50'].item(), 
            mAP50_95=metrics['map'].item()
        )