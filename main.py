import yaml
import sys
from PySide6.QtWidgets import QApplication
from core.core_manager import CoreManager
from core.debug_visualizer import DebugVisualizer
import os

os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"


def load_config(config_path: str) -> dict:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    config = load_config("./settings/main.yaml")
    
    app = None
    visualizer = None
    if config['mode'] == "debug":
        app = QApplication(sys.argv)
        visualizer = DebugVisualizer()
        
    manager = CoreManager(
        config, 
        visualizer=visualizer
    )
    
    if visualizer:
        visualizer.show()
        try:
            exit_code = app.exec()
        finally:
            manager.stop_processing()
        sys.exit(exit_code)

    else:        
        manager.start_processing()
        try:
            while manager.thread.is_alive():
                manager.thread.join(timeout=1.0)
        finally:
            manager.stop_processing()