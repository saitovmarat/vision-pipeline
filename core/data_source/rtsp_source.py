from pathlib import Path

import cv2

from core.data_source.base import IDataSource
from core.domain.frame_packet import FramePacket


class RTSPSource(IDataSource):
    def __init__(self, url: str):
        self.url = url
        self.cap = None
        
        self._frame_idx = 0
    
    
    def switch_source(self, new_source: str | Path):
        self.stop()
        self.url = new_source
        self.start()
        
    
    def start(self): 
        if not self.url:
            raise ValueError("RTSP url is not set")
        
        self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
        if not self.cap.isOpened():
            raise RuntimeError(f"Not able to open RTSP thread: {self.url}")
            
        self._frame_idx = 0
    
    
    def get_frame_data(self) -> FramePacket | None: 
        if not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        self._frame_idx += 1
        return FramePacket(frame=frame, frame_id=self._frame_idx)
    
    
    def stop(self): 
        if self.cap:
            self.cap.release()
            self.cap = None