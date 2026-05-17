from pathlib import Path
import cv2

from core.data_source.base import IDataSource
from core.domain.frame_packet import FramePacket

IMAGE_EXTS = {'.jpg', '.jpeg', '.png'}


class DiskSource(IDataSource):
    def __init__(self, data_path: str | Path):
        self.data_path = data_path
        self.cap = None
        
        self.images = []
        self.idx = 0
        
        
    def switch_source(self, new_path: str | Path):
        self.stop()
        self.data_path = Path(new_path)
        self.start()
                
    
    def start(self):
        images_dir = Path(self.data_path, "images")
        if not images_dir.is_dir():
            raise NotADirectoryError("Not a directory")
                    
        self.images = sorted(
            [f for f in images_dir.iterdir() if f.suffix.lower() in IMAGE_EXTS],
            key=lambda p: p.name
        )
        if not self.images:
            raise ValueError(f"No Images in {images_dir}")
        self.idx = 0

    
    def get_frame_data(self) -> FramePacket | None:
        if self.idx >= len(self.images):
            return None
        
        img_path = self.images[self.idx]
        self.idx += 1
        
        frame = cv2.imread(str(img_path))
        if frame is None:
            return None

        return FramePacket(frame=frame, frame_id=img_path.stem)
    
    
    def stop(self):
        self.images.clear()
        self.idx = 0