from pathlib import Path

from core.data_source.disk_source import DiskSource
from core.data_source.rtsp_source import RTSPSource
from core.domain.frame_packet import FramePacket


class DataManager:
    def __init__(self, mode: str, source_url: str):
        if mode == "debug":
            self.data_source = DiskSource()
        else:
            self.data_source = RTSPSource(source_url)
        
        
    def switch_source(self, new_source: str | Path):
        self.data_source.switch_source(new_source)
        
    def start(self):
        self.data_source.start()

    
    def get_frame_data(self) -> FramePacket | None:
        return self.data_source.get_frame_data()
    
    def stop(self):
        self.data_source.stop()