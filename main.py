import yaml
import sys
from PySide6.QtWidgets import QApplication
from core.factory import build_models
from core.core_manager import CoreManager
from core.debug_visualizer import DebugVisualizer


def load_config(config_path: str) -> dict:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


if __name__ == "__main__":
    config = load_config("./settings/main.yaml")
    data_source, segmenter, metrics_calculator, postprocessor = build_models(config)
    
    app = None
    visualizer = None
    if config['mode'] == "debug":
        app = QApplication(sys.argv)
        visualizer = DebugVisualizer()
        
    manager = CoreManager(
        config, 
        data_source=data_source, 
        segmenter=segmenter, 
        metrics_calculator=metrics_calculator,
        postprocessor=postprocessor,
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