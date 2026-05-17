from abc import ABC, abstractmethod 


class ISegmenter(ABC):
    @abstractmethod
    def predict(self, frame):
        raise NotImplementedError