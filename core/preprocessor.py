import cv2
import numpy as np


class Preprocessor:
    def __init__(self):
        pass
            
    def process(self, frame: np.ndarray) -> np.ndarray:
        if frame is None:
            return frame
         
        img = cv2.medianBlur(frame, 15)
        return img