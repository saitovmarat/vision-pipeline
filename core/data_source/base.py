from abc import ABC, abstractmethod
from pathlib import Path


class IDataSource(ABC):
    @abstractmethod
    def start(self):
        raise NotImplementedError
        
    @abstractmethod
    def get_frame_data(self):
        raise NotImplementedError
        
    @abstractmethod
    def stop(self):
        raise NotImplementedError
    
    def switch_source(self, new_path: str | Path):
        pass