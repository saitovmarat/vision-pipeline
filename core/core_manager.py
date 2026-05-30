from pathlib import Path
import time
import threading
from core.data_source.data_manager import DataManager
from core.segmentation.segmenter_manager import SegmenterManager
from core.metrics_calculator import MetricsCalculator
from core.postprocessor import Postprocessor
from core.network.udp_sender import UDPSender
from core.debug_visualizer import DebugVisualizer
from core.preprocessor import Preprocessor


class CoreManager():
    def __init__(self,
        config: dict,
        visualizer: DebugVisualizer
    ):
        self.data_source = DataManager(
            mode=config['mode'],
            source_url=config['source']
        )
        self.segmenter = SegmenterManager(
            model=config['model'],
            weights=config['weights']
        )
        self.metrics_calculator = MetricsCalculator(class_metrics=True)
        self.postprocessor = Postprocessor()
        self.network_sender = UDPSender(
            ip=config['network']['udp_ip'],
            port=config['network']['udp_port']
        )
        self.visualizer = visualizer
        
        self.preprocessor = Preprocessor()
        self.frame_interval = 1.0 / config['fps'] 
        
        self.thread = None
        self.stop_event = threading.Event()
        
        if self.visualizer:
            self.visualizer.source_selected.connect(self.on_new_source_selected)
        
        
    def on_new_source_selected(self, new_path: str | Path):
        self.stop_processing()
        self.data_source.switch_source(new_path)
        self.metrics_calculator.switch_source(new_path)
        self.start_processing()
        
        
    def start_processing(self):
        self.stop_event.clear()
        self.data_source.start()
        self.thread = threading.Thread(target=self.worker_loop)
        self.thread.start()
        
        
    def run_once(self):
        frame_data = self.data_source.get_frame_data()
        if frame_data is None:
            return False
        
        frame, frame_id = frame_data.frame, frame_data.frame_id 
        
        start_time = time.time()
        filtered_frame = self.preprocessor.process(frame)
        filter_time = time.time() - start_time
        
        start_time = time.time()
        preds = self.segmenter.predict(filtered_frame)
        pred_time = time.time() - start_time
        if preds is None:
            return True
        
        if self.visualizer:
            self.metrics_calculator.update(preds, frame_id, frame.shape)
            metrics = self.metrics_calculator.compute()
            frame = self.postprocessor.apply_mask_overlay(frame, preds) 
            self.visualizer.update_ready.emit(frame, metrics, filter_time, pred_time)
            
        packet = {
            "objects": [
                {
                    "bbox": pred["bbox"].tolist(),
                    "class_id": int(pred["class_id"]),
                    "confidence": float(pred["confidence"]),}
                for pred in preds
            ]
        }
        self.network_sender.send_dict(packet)
        return True        
        
    
    def worker_loop(self):
        while not self.stop_event.is_set():
            loop_start = time.perf_counter()
            if not self.run_once():
                break
                
            elapsed = time.perf_counter() - loop_start
            sleep_time = self.frame_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
            
            
    def stop_processing(self):
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=2.0)