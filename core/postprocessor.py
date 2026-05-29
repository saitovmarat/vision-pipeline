# postprocessor.py
import numpy as np
import cv2
from typing import List, Dict


class Postprocessor:
    def __init__(self, mask_alpha: float = 0.4):
        self.mask_alpha = mask_alpha
        self.palette = np.random.RandomState(42).randint(0, 255, size=(256, 3), dtype=np.uint8)


    def apply_mask_overlay(self, frame: np.ndarray, predictions: List[Dict]) -> np.ndarray:
        if not predictions:
            return frame.copy()

        overlay = frame.copy()

        for pred in predictions:
            mask = pred.get('mask')
            cls_id = pred.get('class_id', 0)

            if mask is None:
                continue

            if not isinstance(mask, np.ndarray):
                mask = np.array(mask)

            if mask.shape[:2] != frame.shape[:2]:
                mask = cv2.resize(mask, (frame.shape[1], frame.shape[0]), interpolation=cv2.INTER_NEAREST)

            mask_bool = mask > 0.5
            if not np.any(mask_bool):
                continue

            color = self.palette[int(cls_id) % len(self.palette)]
            overlay[mask_bool] = color

        return cv2.addWeighted(overlay, self.mask_alpha, frame, 1 - self.mask_alpha, 0)