import cv2
import numpy as np


class Preprocessor:
    def __init__(self):
        pass
         
    def process(self, frame: np.ndarray) -> np.ndarray:
        if frame is None:
            return frame
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

        kernel = np.ones((3,3), np.uint8)
        dilated_mask = cv2.dilate(mask, kernel, iterations=2)

        img = cv2.inpaint(frame, dilated_mask, 3, cv2.INPAINT_TELEA)  
        return img